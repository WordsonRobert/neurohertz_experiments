"""Stage 30: classify the 30-48 Hz instabilities (bursts) into types WITHOUT labels, then compare groups.

1. Label-free typing: subject-balanced sample (<= 200 bursts per subject), standardized descriptors, Gaussian
   mixture with K = 2..7 chosen by BIC; stability = mean adjusted Rand index over subject bootstraps.
2. Every burst gets a type; per subject: rate of each type (per minute per channel) and the within-burst
   frequency instability (f_mad) of each type.
3. Labels (EXPLORATORY): group differences in type rates and in within-burst instability, Freedman-Lane
   permutation with age + sex (and + fractal slope), Holm across types; mixed model on burst-level f_mad.
Outputs: results/<ds>/<variant>/bursts/*
"""
from __future__ import annotations
import argparse, json, warnings
import numpy as np, pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import adjusted_rand_score
from common import variant_dir, participants, OUT, ROI

# 10-20 coordinates: anteriority (+1 frontal-polar ... -1 occipital) and laterality (0 midline ... 1 temporal)
POS = {"Fp1": (1, .5), "Fp2": (1, .5), "F7": (.6, 1), "F3": (.6, .5), "Fz": (.6, 0), "F4": (.6, .5), "F8": (.6, 1),
       "T3": (0, 1), "C3": (0, .5), "Cz": (0, 0), "C4": (0, .5), "T4": (0, 1), "T5": (-.6, 1), "P3": (-.6, .5),
       "Pz": (-.6, 0), "P4": (-.6, .5), "T6": (-.6, 1), "O1": (-1, .5), "O2": (-1, .5)}
DESC = ["log_dur_cycles", "f_mean", "log_f_mad", "abs_chirp", "log_amp", "nb_index", "emg_coact", "sharp",
        "spread", "anteriority", "laterality"]
SEED = 20261115


def load_bursts(dataset, variant):
    d = variant_dir(dataset, variant) / "bursts"
    fs = [f for f in sorted(d.glob("sub-*.csv.gz")) if "transients" not in f.name]
    B = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    B["log_dur_cycles"] = np.log(B.dur_cycles)
    B["log_f_mad"] = np.log(B.f_mad + 1e-3)
    B["abs_chirp"] = np.log1p(B.chirp_hz_s.abs())
    B["log_amp"] = np.log(B.amp_rel95)
    B["anteriority"] = B.ch.map(lambda c: POS.get(c, (np.nan, np.nan))[0])
    B["laterality"] = B.ch.map(lambda c: POS.get(c, (np.nan, np.nan))[1])
    return B.dropna(subset=DESC).reset_index(drop=True)


def balanced_sample(B, per_sub, rng):
    idx = []
    for _, g in B.groupby("subject"):
        idx += list(rng.choice(g.index.to_numpy(), min(per_sub, len(g)), replace=False))
    return np.sort(np.asarray(idx))


def fit_types(B, k_range=range(2, 8), per_sub=200, seed=SEED, n_boot=10):
    rng = np.random.default_rng(seed)
    idx = balanced_sample(B, per_sub, rng)
    sc = StandardScaler().fit(B.loc[idx, DESC])
    Z = sc.transform(B.loc[idx, DESC])
    bic = {}
    models = {}
    for k in k_range:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m = GaussianMixture(k, covariance_type="full", n_init=3, random_state=seed, reg_covar=1e-4).fit(Z)
        bic[k], models[k] = m.bic(Z), m
    K = min(bic, key=bic.get)
    base = models[K]
    lab0 = base.predict(Z)
    subs = B.subject.unique()
    aris = []
    for b in range(n_boot):
        bs = rng.choice(subs, len(subs), replace=True)
        Bb = pd.concat([B[B.subject == s] for s in bs], ignore_index=True)
        ib = balanced_sample(Bb, per_sub, rng)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mb = GaussianMixture(K, covariance_type="full", n_init=2, random_state=seed + b + 1,
                                 reg_covar=1e-4).fit(sc.transform(Bb.loc[ib, DESC]))
        aris.append(adjusted_rand_score(lab0, mb.predict(Z)))
    return sc, base, K, bic, float(np.mean(aris)), float(np.std(aris))


def describe_types(B, labels, K):
    """Centroids in original units + an automatic, purely descriptive name from the most distinctive features."""
    rows = []
    zall = (B[DESC] - B[DESC].mean()) / B[DESC].std()
    for k in range(K):
        m = labels == k
        cz = zall[m].mean()
        top = cz.abs().sort_values(ascending=False).index[:3]
        name = ", ".join(f"{'high' if cz[c] > 0 else 'low'} {c}" for c in top)
        rows.append({"type": k, "share": float(m.mean()), "auto_name": name,
                     **{f"mean_{c}": float(B.loc[m, c].mean()) for c in DESC},
                     "frac_roi": float(B.loc[m, "ch"].isin(ROI).mean())})
    return pd.DataFrame(rows)


def fl_test(df, y, covs, tgt, ref, rng, n_perm=2000):
    x = df[df.group.isin([tgt, ref])].dropna(subset=[y] + covs)
    if min((x.group == tgt).sum(), (x.group == ref).sum()) < 4 or x[y].nunique() < 3:
        return np.nan, np.nan, len(x)
    C = (x[covs] - x[covs].mean()).values if covs else np.empty((len(x), 0))
    g = (x.group == tgt).astype(float).values
    X = np.column_stack([np.ones(len(x)), C, g]); Xr = X[:, :-1]
    Y = x[y].astype(float).values

    def tstat(yv):
        b, *_ = np.linalg.lstsq(X, yv, rcond=None); r = yv - X @ b
        XtXi = np.linalg.pinv(X.T @ X); h = (XtXi @ X.T)[-1]
        return b[-1] / max(np.sqrt(np.sum(h ** 2 * r ** 2)), 1e-300)
    t0 = tstat(Y)
    br, *_ = np.linalg.lstsq(Xr, Y, rcond=None); Fr, Rr = Xr @ br, Y - Xr @ br
    null = np.array([tstat(Fr + Rr[rng.permutation(len(Rr))]) for _ in range(n_perm)])
    return float(t0), float((np.sum(np.abs(null) >= abs(t0)) + 1) / (n_perm + 1)), len(x)


def holm(p):
    p = np.asarray(p, float); o = np.argsort(np.where(np.isfinite(p), p, 2)); m = np.isfinite(p).sum()
    adj = np.full(len(p), np.nan); run = 0.0
    for r, i in enumerate(o):
        if not np.isfinite(p[i]):
            continue
        run = max(run, min(1.0, (m - r) * p[i])); adj[i] = run
    return adj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="main")
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--threshold", choices=["p95", "p99"], default="p95",
                    help="p99 keeps only bursts whose peak exceeds the surrogate 99th percentile")
    a = ap.parse_args()
    rng = np.random.default_rng(SEED)
    out = OUT / a.dataset / a.variant / f"bursts_{a.threshold}"; out.mkdir(parents=True, exist_ok=True)
    B = load_bursts(a.dataset, a.variant)
    if a.threshold == "p99":
        B = B[B.above99].reset_index(drop=True)
    # ---------- 1. label-free typing
    sc, gmm, K, bic, ari_m, ari_s = fit_types(B)
    B["type"] = gmm.predict(sc.transform(B[DESC]))
    T = describe_types(B, B["type"].to_numpy(), K)
    T.to_csv(out / "burst_types.csv", index=False)
    json.dump({"K": K, "bic": bic, "stability_ari_mean": ari_m, "stability_ari_sd": ari_s,
               "n_bursts": int(len(B)), "n_subjects": int(B.subject.nunique())},
              open(out / "typing_meta.json", "w"), indent=1)
    import joblib
    joblib.dump({"scaler": sc, "gmm": gmm, "desc": DESC, "K": K}, out / "typing_model.joblib")
    # ---------- 2. per-subject descriptors
    nch = B.groupby("subject").ch.nunique().clip(lower=1)
    cm = B.groupby("subject").clean_min.first()
    S = pd.DataFrame(index=sorted(B.subject.unique()))
    for k in range(K):
        Bk = B[B.type == k]
        S[f"rate_type{k}"] = (Bk.groupby("subject").size().reindex(S.index).fillna(0) / cm / 19.0)
        S[f"fmad_type{k}"] = Bk.groupby("subject").log_f_mad.mean().reindex(S.index)
        S[f"share_type{k}"] = S[f"rate_type{k}"] / (B.groupby("subject").size().reindex(S.index) / cm / 19.0)
    S["rate_all"] = B.groupby("subject").size().reindex(S.index) / cm / 19.0
    S["fmad_all"] = B.groupby("subject").log_f_mad.mean().reindex(S.index)
    S.index.name = "subject"
    S.to_csv(out / "subject_burst_types.csv")
    # ---------- 3. labels (EXPLORATORY)
    P = participants(a.dataset)
    st_path = OUT / a.dataset / a.variant / "subject_table.csv"
    st = pd.read_csv(st_path, index_col=0) if st_path.exists() else pd.DataFrame(index=S.index)
    D = P.join(S, how="inner").join(st[["fractal_slope"]] if "fractal_slope" in st else pd.DataFrame(), how="left")
    rows = []
    for tgt, ref in [("AD", "CN"), ("FTD", "CN"), ("AD", "FTD")]:
        for covname, covs in (("age_sex", ["age", "sex_m"]), ("age_sex_slope", ["age", "sex_m", "fractal_slope"])):
            if "fractal_slope" in covs and "fractal_slope" not in D:
                continue
            block = []
            for y in [c for c in S.columns if c.startswith(("rate_", "fmad_", "share_"))]:
                t, p, n = fl_test(D, y, covs, tgt, ref, rng, a.n_perm)
                block.append(dict(contrast=f"{tgt}-{ref}", covariates=covname, measure=y, n=n, t=t, p_perm=p))
            ph = holm([b["p_perm"] for b in block])
            for b, h in zip(block, ph):
                b["p_holm"] = h
            rows += block
    R = pd.DataFrame(rows); R.to_csv(out / "group_tests.csv", index=False)
    # mixed model on burst-level instability, AD vs CN, per type
    import statsmodels.formula.api as smf
    mm = []
    for k in list(range(K)) + ["all"]:
        Bk = B if k == "all" else B[B.type == k]
        Bk = Bk.merge(P[["group", "age", "sex_m"]], left_on="subject", right_index=True)
        Bk = Bk[Bk.group.isin(["AD", "CN"])]
        Bk = Bk.sample(frac=1.0, random_state=SEED).groupby("subject").head(300)   # <= 300 random bursts each
        if Bk.subject.nunique() < 8 or Bk.group.nunique() < 2:
            continue
        Bk = Bk.assign(ad=(Bk.group == "AD").astype(float), age_c=Bk.age - Bk.age.mean())
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                f = smf.mixedlm("log_f_mad ~ ad + age_c + sex_m + f_mean + log_dur_cycles", Bk,
                                groups=Bk["subject"]).fit(reml=True)
                mm.append(dict(type=k, n_bursts=len(Bk), n_subj=Bk.subject.nunique(), beta_ad=f.params["ad"],
                               se=f.bse["ad"], p_wald=f.pvalues["ad"]))
            except Exception as e:  # noqa: BLE001
                mm.append(dict(type=k, error=str(e)))
    pd.DataFrame(mm).to_csv(out / "mixed_within_burst_instability.csv", index=False)
    print(f"[30] K={K} (stability ARI {ari_m:.2f}±{ari_s:.2f}), {len(B)} bursts ->", out)
    print(T[["type", "share", "auto_name", "frac_roi"]].to_string(index=False))
    print(R[R.covariates == "age_sex"].sort_values("p_perm").head(8).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
