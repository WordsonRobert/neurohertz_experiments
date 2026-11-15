"""Stage 40 (labels for norms only, EXPLORATORY): stratify the patients by WHICH mechanism deviates.

1. Normative model from the controls: for each axis, x ~ age within CN; a patient's z = (x - prediction) / SD of
   the CN residuals. CN subjects get leave-one-out z (they never enter their own norm).
2. Per axis: fraction of AD and FTD outside |z| > 1.96 (5% expected by chance) with a binomial p.
3. Patients (AD + FTD pooled, diagnosis hidden) are clustered on their z-profiles (k-means, K = 2..5 by
   silhouette, bootstrap stability). Only afterwards: cluster x diagnosis (Fisher/chi2) and MMSE by cluster.
Outputs: results/<ds>/<variant>/stratify/*
"""
from __future__ import annotations
import argparse, json
import numpy as np, pandas as pd
from scipy.stats import binomtest, chi2_contingency, kruskal
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from common import participants, OUT

AXES = {   # axis: (column, sign so that + means "in the direction of a deficit / abnormality")
    "slowing_theta_alpha": ("theta_alpha", 1), "slowing_iaf": ("iaf", -1),
    "aperiodic_slope": ("fractal_slope", 1), "aperiodic_offset": ("fractal_offset", 1),
    "gamma_periodic_35_45": ("periodic_35_45", 1), "gamma_lowemg_35_45": ("logpow_35_45_lowemg", 1),
    "gamma_burst_excess": ("burst_excess_roi", 1), "muscle": ("emg_mean", 1),
    "transients": ("transient_rate", 1), "pac_theta_gamma": ("pac_theta_z", 1), "alpha_harmonic": ("alpha_1to4_z", 1),
}
SEED = 20261115


def normative_z(D, cols):
    Z = pd.DataFrame(index=D.index, columns=cols, dtype=float)
    cn = D.index[D.group == "CN"]
    for c in cols:
        for s in D.index:
            ref = cn.drop(s) if s in cn else cn
            r = D.loc[ref, [c, "age"]].dropna()
            if len(r) < 10 or not np.isfinite(D.loc[s, c]):
                continue
            b = np.polyfit(r.age, r[c], 1); res = r[c] - np.polyval(b, r.age)
            Z.loc[s, c] = (D.loc[s, c] - np.polyval(b, D.loc[s, "age"])) / res.std(ddof=2)
    return Z


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="main")
    ap.add_argument("--burst-threshold", default="p95")
    a = ap.parse_args()
    base = OUT / a.dataset / a.variant
    out = base / "stratify"; out.mkdir(parents=True, exist_ok=True)
    st = pd.read_csv(base / "subject_table.csv", index_col=0)
    bt_path = base / f"bursts_{a.burst_threshold}" / "subject_burst_types.csv"
    if bt_path.exists():
        bt = pd.read_csv(bt_path, index_col=0)
        st = st.join(bt[[c for c in bt if c.startswith("share_type")]], how="left")
    P = participants(a.dataset)
    D = P[["group", "age", "mmse"]].join(st, how="inner")
    axes = {k: v for k, v in AXES.items() if v[0] in D}
    for c in [c for c in D if c.startswith("share_type")]:
        axes[f"bursts_{c}"] = (c, 1)
    cols = [v[0] for v in axes.values()]
    Z = normative_z(D, cols)
    for name, (c, sgn) in axes.items():
        Z[c] = Z[c] * sgn
    Z.columns = list(axes)
    Z.to_csv(out / "normative_z.csv")
    # 2. per-axis abnormality rates
    rows = []
    for grp in ["CN", "AD", "FTD"]:
        g = Z[D.group == grp]
        for ax in Z.columns:
            v = g[ax].dropna(); k = int((v.abs() > 1.96).sum())
            rows.append(dict(group=grp, axis=ax, n=len(v), n_abnormal=k, frac=k / max(len(v), 1),
                             mean_z=float(v.mean()), p_binom_vs_5pct=binomtest(k, len(v), 0.05, "greater").pvalue if len(v) else np.nan))
    pd.DataFrame(rows).to_csv(out / "axis_abnormality.csv", index=False)
    # 3. label-blind clustering of the patients
    pat = Z[D.group.isin(["AD", "FTD"])].dropna(axis=1, thresh=int(0.9 * (D.group != "CN").sum()))
    pat = pat.fillna(0.0).clip(-5, 5)
    sil = {}
    labs = {}
    for k in range(2, 6):
        km = KMeans(k, n_init=50, random_state=SEED).fit(pat.values)
        sil[k] = float(silhouette_score(pat.values, km.labels_)); labs[k] = km.labels_
    K = max(sil, key=sil.get)
    rng = np.random.default_rng(SEED); aris = []
    for b in range(50):
        ib = rng.choice(len(pat), len(pat), replace=True)
        kb = KMeans(K, n_init=10, random_state=b).fit(pat.values[ib])
        aris.append(adjusted_rand_score(labs[K], kb.predict(pat.values)))
    cl = pd.Series(labs[K], index=pat.index, name="cluster")
    prof = pat.groupby(cl).mean().T
    ct = pd.crosstab(cl, D.loc[pat.index, "group"])
    chi = chi2_contingency(ct.values) if ct.shape[1] > 1 else (np.nan, np.nan)
    mm = D.loc[pat.index, "mmse"].groupby(cl)
    kw = kruskal(*[g.dropna().values for _, g in mm]) if K > 1 else None
    prof.to_csv(out / "cluster_profiles.csv"); ct.to_csv(out / "cluster_by_diagnosis.csv")
    cl.to_csv(out / "patient_clusters.csv")
    meta = {"K": K, "silhouette": sil, "stability_ari_mean": float(np.mean(aris)), "stability_ari_sd": float(np.std(aris)),
            "chi2_cluster_vs_diagnosis_p": float(chi[1]) if np.isfinite(chi[1]) else None,
            "mmse_by_cluster_median": mm.median().to_dict(), "kruskal_mmse_p": float(kw.pvalue) if kw else None,
            "axes_used": list(pat.columns)}
    json.dump(meta, open(out / "stratify_meta.json", "w"), indent=1, default=float)
    print(f"[40] K={K} silhouette={sil[K]:.2f} stability ARI={np.mean(aris):.2f}")
    print(ct.to_string()); print(prof.round(2).to_string())


if __name__ == "__main__":
    main()
