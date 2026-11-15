"""Stage 55: characterize frequency instability in every band, then ask whether it separates AD (EXPLORATORY).

Label-free first (nothing below A-C sees a diagnosis):
  A reliability   split-half ICC(2,1) with Spearman-Brown, coverage. ELIGIBLE = SB-ICC >= 0.6 and >= 80% of
                  subjects measurable. Only eligible measures go on.
  B spectrum      how much of each raw measure is its spectrum: R^2 of raw on its own surrogate mean; and its
                  correlation with rhythm presence (frac_snr3) in the same band.
  C structure     PCA of eligible measures: one global "instability trait", or band-specific dimensions?
With labels:
  D group tests   Freedman-Lane, joint maxT across all eligible measures of a family (raw / excess / presence),
                  for AD-CN, FTD-CN, AD-FTD, under a covariate ladder: L0 age+sex, L1 +slowing (theta/alpha),
                  L2 +1/f (fractal slope), L3 +the band's own rhythm presence.
  E time-on-task  second-half minus first-half value, AD vs CN (fatigue / drowsiness drift).
  F severity      within AD, partial Spearman with MMSE (age, sex, slowing), BH-FDR.
  G prediction    nested CV; inside each training fold the single best eligible measure is picked by its
                  training-fold AUC, added to the slowing + 1/f baseline; AUC, balanced accuracy, gain over the
                  baseline, permutation p of the WHOLE pipeline (selection included), selection frequencies.
Outputs: results/<ds>/<variant>/bandinst/*.csv and REPORT_INSTABILITY.md
"""
from __future__ import annotations
import argparse, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr, rankdata
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from common import variant_dir, participants, OUT, ROI

SEED = 20261115
BASE = ["theta_alpha", "iaf", "fractal_slope", "fractal_offset"]
PRESENCE = ("frac_snr3", "snr_median")


def load_wide(dataset, variant):
    fs = sorted((variant_dir(dataset, variant) / "bandinst").glob("sub-*.csv.gz"))
    L = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    L["region"] = np.where(L.ch.isin(ROI), "roi", "other")
    out = {}
    for reg, need in (("roi", 3), ("global", 10)):
        sub = L if reg == "global" else L[L.region == "roi"]
        g = sub.groupby(["subject", "part", "band", "metric"]).value
        agg = g.mean().where(g.count() >= need)
        out[reg] = agg
    W = {}
    for reg, s in out.items():
        u = s.unstack(["band", "metric"])
        u.columns = [f"{b}|{m}|{reg}" for b, m in u.columns]
        W[reg] = u
    W = pd.concat(W.values(), axis=1)
    return {p: W.xs(p, level="part") for p in ("all", "h1", "h2")}


def icc21(a, b):
    M = np.column_stack([a, b]); M = M[np.isfinite(M).all(1)]
    n, k = M.shape
    if n < 10:
        return np.nan
    gm = M.mean(); msr = k * ((M.mean(1) - gm) ** 2).sum() / (n - 1); msc = n * ((M.mean(0) - gm) ** 2).sum() / (k - 1)
    sse = ((M - M.mean(1, keepdims=True) - M.mean(0, keepdims=True) + gm) ** 2).sum(); mse = sse / ((n - 1) * (k - 1))
    return float((msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n))


def family(col):
    m = col.split("|")[1]
    return "presence" if m in PRESENCE else ("excess" if m.endswith("__excess") else ("surr" if m.endswith("__surr") else "raw"))


def t_cols(Y, X, j):
    XtXi = np.linalg.pinv(X.T @ X); B = XtXi @ X.T @ Y; R = Y - X @ B
    h = (XtXi @ X.T)[j]; return B[j] / np.maximum(np.sqrt((h[:, None] ** 2 * R ** 2).sum(0)), 1e-300)


def maxT_test(D, feats, covs_for, tgt, ref, n_perm, rng):
    """Freedman-Lane per feature (own design allowed), ONE permutation of subjects shared by all features ->
    the max |t| over features gives family-wise p-values (strong FWER control). Missing values: a feature is
    tested on its complete cases (designs grouped by identical covariate set and missingness pattern)."""
    x = D[D.group.isin([tgt, ref])]
    g = (x.group == tgt).astype(float).values
    n = len(x); perms = [rng.permutation(n) for _ in range(n_perm)]
    t_obs, null = {}, np.zeros((n_perm, len(feats)))
    for j, f in enumerate(feats):
        covs = covs_for(f)
        ok = x[[f] + covs].notna().all(1).values
        if ok.sum() < 12 or min(g[ok].sum(), (1 - g[ok]).sum()) < 5:
            t_obs[f] = np.nan; null[:, j] = 0; continue
        C = x.loc[ok, covs].astype(float).values; C = C - C.mean(0) if covs else np.empty((ok.sum(), 0))
        X = np.column_stack([np.ones(ok.sum()), C, g[ok]]); Xr = X[:, :-1]
        y = x.loc[ok, f].astype(float).values[:, None]
        br = np.linalg.pinv(Xr) @ y; F, R = Xr @ br, y - Xr @ br
        t_obs[f] = float(t_cols(y, X, X.shape[1] - 1)[0])
        idx = np.flatnonzero(ok)
        for b, pm in enumerate(perms):
            # the shared permutation, restricted to this feature's complete cases (order preserved)
            pr = np.argsort(np.argsort(pm[np.isin(pm, idx)]))
            null[b, j] = abs(t_cols(F + R[pr], X, X.shape[1] - 1)[0])
    mx = null.max(1)
    return {f: (t_obs[f], float((np.sum(mx >= abs(t_obs[f])) + 1) / (n_perm + 1)) if np.isfinite(t_obs[f]) else np.nan)
            for f in feats}


def rank_auc(X, y):
    """Training-fold AUC of every column at once (Mann-Whitney), missing values set to the column median;
    returned as max(AUC, 1 - AUC) because the selected measure may separate in either direction."""
    med = np.nanmedian(X, 0)
    Xf = np.where(np.isfinite(X), X, med)
    R = rankdata(Xf, axis=0)
    n1 = y.sum(); n0 = len(y) - n1
    a = (R[y == 1].sum(0) - n1 * (n1 + 1) / 2) / (n1 * n0)
    a = np.where(np.isfinite(med), a, 0.5)
    return np.maximum(a, 1 - a)


def cv_select(B, F, y, rep, perm=None, base_only=False):
    yv = y if perm is None else perm
    skf = StratifiedKFold(5, shuffle=True, random_state=SEED + rep)
    s = np.zeros(len(yv)); picks = []
    for tr, te in skf.split(B, yv):
        if base_only:
            Xtr, Xte = B[tr], B[te]
        else:
            Ftr = F[tr]; med = np.nanmedian(Ftr, 0)
            j = int(np.argmax(rank_auc(Ftr, yv[tr]))); picks.append(j)
            col_tr = np.where(np.isfinite(Ftr[:, j]), Ftr[:, j], med[j])
            col_te = np.where(np.isfinite(F[te, j]), F[te, j], med[j])     # training-fold median imputation
            Xtr = np.column_stack([B[tr], col_tr]) if B.size else col_tr[:, None]
            Xte = np.column_stack([B[te], col_te]) if B.size else col_te[:, None]
        sc = StandardScaler().fit(Xtr)
        m = LogisticRegression(C=1.0, class_weight="balanced", max_iter=5000).fit(sc.transform(Xtr), yv[tr])
        s[te] = m.decision_function(sc.transform(Xte))
    return roc_auc_score(yv, s), balanced_accuracy_score(yv, s > 0), picks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="main")
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--n-perm-cv", type=int, default=200)
    ap.add_argument("--n-rep", type=int, default=20)
    a = ap.parse_args()
    rng = np.random.default_rng(SEED)
    out = OUT / a.dataset / a.variant / "bandinst"; out.mkdir(parents=True, exist_ok=True)
    W = load_wide(a.dataset, a.variant)
    A_, H1, H2 = W["all"], W["h1"], W["h2"]
    feats = [c for c in A_.columns if family(c) in ("raw", "excess", "presence")]
    # ---------------- A. reliability (label-free)
    rel = pd.DataFrame({"feature": feats, "family": [family(c) for c in feats],
                        "coverage": [float(A_[c].notna().mean()) for c in feats],
                        "icc_half": [icc21(H1.reindex(A_.index)[c].values, H2.reindex(A_.index)[c].values)
                                     if c in H1 and c in H2 else np.nan for c in feats]})
    rel["icc_sb"] = 2 * rel.icc_half / (1 + rel.icc_half)
    rel["eligible"] = (rel.icc_sb >= 0.6) & (rel.coverage >= 0.8)
    rel.to_csv(out / "A_reliability.csv", index=False)
    elig = rel.feature[rel.eligible].tolist()
    # ---------------- B. how much is spectrum (label-free)
    rowsB = []
    for c in [f for f in elig if family(f) == "raw"]:
        sc_ = c.replace("|" + c.split("|")[1] + "|", "|" + c.split("|")[1] + "__surr|")
        pres = "|".join([c.split("|")[0], "frac_snr3", c.split("|")[2]])
        r2 = np.nan
        if sc_ in A_:
            ok = A_[[c, sc_]].notna().all(1)
            r2 = float(np.corrcoef(A_.loc[ok, c], A_.loc[ok, sc_])[0, 1] ** 2) if ok.sum() > 10 else np.nan
        rowsB.append(dict(feature=c, r2_raw_on_surrogate=r2,
                          rho_with_presence=spearmanr(A_[c], A_[pres], nan_policy="omit")[0] if pres in A_ else np.nan))
    pd.DataFrame(rowsB).to_csv(out / "B_spectral_share.csv", index=False)
    # ---------------- C. structure (label-free)
    pca_info = {}
    for fam in ("raw", "excess"):
        cols = [c for c in elig if family(c) == fam]
        if len(cols) >= 3:
            Z = A_[cols].apply(lambda v: (v - v.mean()) / v.std()); Z = Z.fillna(0.0)
            u, s_, vt = np.linalg.svd(Z.values - Z.values.mean(0), full_matrices=False)
            ev = s_ ** 2 / np.sum(s_ ** 2)
            load = pd.Series(vt[0], index=cols).sort_values(key=np.abs, ascending=False)
            pca_info[fam] = {"n": len(cols), "var_explained_pc1_3": ev[:3].round(3).tolist(),
                             "pc1_top_loadings": load.head(8).round(2).to_dict()}
    json.dump(pca_info, open(out / "C_structure.json", "w"), indent=1)
    # ---------------- labels
    P = participants(a.dataset)
    st = pd.read_csv(OUT / a.dataset / a.variant / "subject_table.csv", index_col=0)
    D = P[["group", "age", "sex_m", "mmse"]].join(st[BASE], how="inner").join(A_, how="inner")
    ladders = {"L0": lambda f: ["age", "sex_m"],
               "L1": lambda f: ["age", "sex_m", "theta_alpha"],
               "L2": lambda f: ["age", "sex_m", "theta_alpha", "fractal_slope"],
               "L3": lambda f: ["age", "sex_m", "theta_alpha", "fractal_slope",
                                "|".join([f.split("|")[0], "frac_snr3", f.split("|")[2]])]}
    rowsD = []
    for fam in ("raw", "excess", "presence"):
        cols = [c for c in elig if family(c) == fam]
        if not cols:
            continue
        for tgt, ref in [("AD", "CN"), ("FTD", "CN"), ("AD", "FTD")]:
            for lad, cf in ladders.items():
                if lad == "L3" and fam == "presence":
                    continue
                res = maxT_test(D, cols, cf, tgt, ref, a.n_perm, rng)
                rowsD += [dict(family=fam, contrast=f"{tgt}-{ref}", ladder=lad, feature=f, t=t, p_maxT=p)
                          for f, (t, p) in res.items()]
    Dt = pd.DataFrame(rowsD); Dt.to_csv(out / "D_group_tests.csv", index=False)
    # ---------------- E. time-on-task drift (h2 - h1)
    drift = (H2.reindex(D.index)[elig] - H1.reindex(D.index)[elig]).add_suffix("|drift")
    DD = D[["group", "age", "sex_m"]].join(drift)
    resE = maxT_test(DD, list(drift.columns), ladders["L0"], "AD", "CN", a.n_perm, rng)
    pd.DataFrame([dict(feature=f, t=t, p_maxT=p) for f, (t, p) in resE.items()]).to_csv(out / "E_drift.csv", index=False)
    # ---------------- F. severity within AD
    ad = D[D.group == "AD"]; rowsF = []
    for c in elig:
        x = ad[[c, "mmse", "age", "sex_m", "theta_alpha"]].dropna()
        if len(x) < 15:
            continue
        rz = x.rank()
        Zc = np.column_stack([np.ones(len(x)), rz[["age", "sex_m", "theta_alpha"]].values])
        e1 = rz[c] - Zc @ np.linalg.lstsq(Zc, rz[c], rcond=None)[0]; e2 = rz.mmse - Zc @ np.linalg.lstsq(Zc, rz.mmse, rcond=None)[0]
        rho = float(np.corrcoef(e1, e2)[0, 1])
        null = np.array([np.corrcoef(e1, rng.permutation(e2.values))[0, 1] for _ in range(2000)])
        rowsF.append(dict(feature=c, n=len(x), rho_partial=rho, p_perm=(np.sum(np.abs(null) >= abs(rho)) + 1) / 2001))
    Ft = pd.DataFrame(rowsF)
    if len(Ft):
        o = np.argsort(Ft.p_perm.values); m = len(o); q = np.empty(m)
        q[o] = np.minimum.accumulate((Ft.p_perm.values[o] * m / np.arange(1, m + 1))[::-1])[::-1]
        Ft["q_bh"] = np.minimum(q, 1)
    Ft.to_csv(out / "F_severity_within_AD.csv", index=False)
    # ---------------- G. prediction with in-fold selection
    rowsG = []
    for tgt, ref in [("AD", "CN"), ("FTD", "CN"), ("AD", "FTD")]:
        x = D[D.group.isin([tgt, ref])].dropna(subset=BASE)
        y = (x.group == tgt).astype(int).values
        Bm = x[BASE].values
        for pool_name, pool in (("all eligible", elig), ("excess only", [c for c in elig if family(c) == "excess"]),
                                ("raw only", [c for c in elig if family(c) == "raw"])):
            if not pool:
                continue
            Fm = x[pool].values
            base = np.array([cv_select(Bm, Fm, y, r, base_only=True)[0] for r in range(a.n_rep)])
            full = [cv_select(Bm, Fm, y, r) for r in range(a.n_rep)]
            alone = [cv_select(np.empty((len(y), 0)), Fm, y, r) for r in range(a.n_rep)]
            fa = np.array([f_[0] for f_ in full]); al = np.array([f_[0] for f_ in alone])
            picks = pd.Series([pool[j] for f_ in full for j in f_[2]]).value_counts(normalize=True).head(5)
            pr = np.random.default_rng(SEED)
            null_full = np.array([cv_select(Bm, Fm, y, i, pr.permutation(y))[0] for i in range(a.n_perm_cv)])
            null_alone = np.array([cv_select(np.empty((len(y), 0)), Fm, y, i, pr.permutation(y))[0] for i in range(a.n_perm_cv)])
            d = fa - base
            rowsG.append(dict(contrast=f"{tgt}-{ref}", pool=pool_name, n=len(y), auc_baseline=base.mean(),
                              auc_instability_alone=al.mean(), p_alone=(np.sum(null_alone >= al.mean()) + 1) / (a.n_perm_cv + 1),
                              auc_baseline_plus=fa.mean(), p_plus=(np.sum(null_full >= fa.mean()) + 1) / (a.n_perm_cv + 1),
                              bal_acc_plus=np.mean([f_[1] for f_ in full]), gain=d.mean(),
                              gain_lo=np.percentile(d, 2.5), gain_hi=np.percentile(d, 97.5),
                              top_picks="; ".join(f"{k} ({v:.0%})" for k, v in picks.items())))
            print(f"[55] {tgt}-{ref} {pool_name}: alone {al.mean():.3f}  base {base.mean():.3f}  base+ {fa.mean():.3f}", flush=True)
    Gt = pd.DataFrame(rowsG); Gt.to_csv(out / "G_prediction.csv", index=False)
    # ---------------- report
    sig = Dt[Dt.p_maxT < 0.05]
    rep = ["# Frequency instability across bands: characterization (EXPLORATORY)\n",
           f"Eligible measures (split-half SB-ICC >= 0.6, coverage >= 80%): {len(elig)} of {len(feats)} "
           f"({rel[rel.eligible].groupby('family').size().to_dict()}).\n",
           "## A. Most reliable measures\n", rel.sort_values("icc_sb", ascending=False).head(25).round(3).to_markdown(index=False),
           "\n## B. How much of each reliable raw measure is spectrum\n",
           pd.DataFrame(rowsB).sort_values("r2_raw_on_surrogate", ascending=False).round(3).to_markdown(index=False) if rowsB else "none",
           "\n## C. Structure\n```\n" + json.dumps(pca_info, indent=1) + "\n```",
           "\n## D. Family-wise significant group differences (maxT p < 0.05)\n",
           sig.round(4).to_markdown(index=False) if len(sig) else "none",
           "\n## E. Time-on-task drift, AD vs CN (maxT p < 0.1)\n",
           pd.read_csv(out / "E_drift.csv").query("p_maxT < 0.1").round(4).to_markdown(index=False) or "none",
           "\n## F. Severity within AD (q < 0.1)\n", Ft[Ft.get("q_bh", pd.Series(dtype=float)) < 0.1].round(4).to_markdown(index=False) if len(Ft) else "none",
           "\n## G. Prediction with in-fold selection\n", Gt.round(3).to_markdown(index=False)]
    (out / "REPORT_INSTABILITY.md").write_text("\n".join(rep))
    print("[55] done ->", out)


if __name__ == "__main__":
    main()
