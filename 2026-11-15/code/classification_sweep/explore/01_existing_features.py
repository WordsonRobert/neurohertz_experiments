"""EXPLORATORY step 1: what in the already-extracted features separates AD from CN around 30-45 Hz, and does it
survive the obvious non-neural explanations?  Uses only results/features (no raw data).

Outputs results/explore01/*.csv and report.md.  Every p-value here is exploratory (ds004504 is unblinded).
"""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import RepeatedStratifiedKFold, LeaveOneOut
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load, hedges_g, ROOT  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results" / "explore01"
OUT.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(20261115)
N_PERM = 2000

d = load()
ad_cn = d[d.group.isin(["AD", "CN"])].copy()
ad_cn["y"] = (ad_cn.group == "AD").astype(int)


def fl_perm(df, y, covars, target="AD", ref="CN", n_perm=N_PERM):
    """OLS group effect (HC3) with Freedman-Lane permutation p."""
    x = df[df.group.isin([target, ref])].dropna(subset=[y] + covars)
    g = (x.group == target).astype(float).values
    Z = sm.add_constant(x[covars].astype(float).values) if covars else np.ones((len(x), 1))
    yv = x[y].astype(float).values
    Xf = np.column_stack([Z, g])
    fit = sm.OLS(yv, Xf).fit(cov_type="HC3")
    t0 = fit.params[-1] / fit.bse[-1]
    if not np.isfinite(t0) or np.nanstd(yv) == 0:
        raise ValueError(f"{y}: group effect undefined (constant or collinear)")
    red = sm.OLS(yv, Z).fit(); fv, rs = red.fittedvalues, red.resid
    cnt = 0
    for _ in range(n_perm):
        yp = fv + RNG.permutation(rs)
        f2 = sm.OLS(yp, Xf).fit(cov_type="HC3")
        cnt += abs(f2.params[-1] / f2.bse[-1]) >= abs(t0)
    sd = np.std(yv, ddof=1)
    return dict(n=len(x), beta_sd=fit.params[-1] / sd, t=t0, p_perm=(cnt + 1) / (n_perm + 1))


def cv_auc(X, y, n_rep=20, resid_cols=None, seed=0):
    """Leakage-safe repeated 5-fold AUC (logistic, C chosen as 1.0 on standardized features).
    resid_cols: columns of X to regress OUT of the first column inside each training fold."""
    X = np.asarray(X, float); y = np.asarray(y)
    rs = RepeatedStratifiedKFold(n_splits=5, n_repeats=n_rep, random_state=seed)
    scores = np.zeros((n_rep, len(y)))
    for k, (tr, te) in enumerate(rs.split(X, y)):
        Xtr, Xte = X[tr].copy(), X[te].copy()
        if resid_cols is not None:
            lr = LinearRegression().fit(Xtr[:, resid_cols], Xtr[:, 0])
            Xtr[:, 0] -= lr.predict(Xtr[:, resid_cols]); Xte[:, 0] -= lr.predict(Xte[:, resid_cols])
            keep = [0]
            Xtr, Xte = Xtr[:, keep], Xte[:, keep]
        sc = StandardScaler().fit(Xtr)
        m = LogisticRegression(C=1.0, max_iter=2000).fit(sc.transform(Xtr), y[tr])
        scores[k // 5, te] = m.decision_function(sc.transform(Xte))
    aucs = [roc_auc_score(y, s) for s in scores]
    acc = [np.mean((s > 0) == y) for s in scores]
    return dict(auc=float(np.mean(aucs)), auc_lo=float(np.percentile(aucs, 2.5)), auc_hi=float(np.percentile(aucs, 97.5)),
                acc=float(np.mean(acc)))


def loso_acc(X, y):
    X = np.asarray(X, float); y = np.asarray(y); s = np.zeros(len(y))
    for tr, te in LeaveOneOut().split(X):
        sc = StandardScaler().fit(X[tr])
        m = LogisticRegression(C=1.0, max_iter=2000).fit(sc.transform(X[tr]), y[tr])
        s[te] = m.decision_function(sc.transform(X[te]))
    return dict(loso_auc=float(roc_auc_score(y, s)), loso_acc=float(np.mean((s > 0) == y)))


report = ["# Exploratory step 1: existing features (ds004504, post-freeze, EXPLORATORY)\n"]

# ---------------------------------------------------------------- A. what drove the old 73%?
A = ad_cn.dropna(subset=["roi__legacy_std", "roi__aperiodic_exponent", "roi__theta_alpha_ratio"])
yA = A.y.values
rowsA = []
for name, cols, rc in [
    ("legacy_std (old NeuroHertz metric) alone", ["roi__legacy_std"], None),
    ("legacy_std with 1/f exponent regressed out (inside folds)", ["roi__legacy_std", "roi__aperiodic_exponent"], [1]),
    ("legacy_std with exponent + theta/alpha regressed out", ["roi__legacy_std", "roi__aperiodic_exponent", "roi__theta_alpha_ratio"], [1, 2]),
    ("1/f exponent alone", ["roi__aperiodic_exponent"], None),
    ("theta/alpha ratio alone", ["roi__theta_alpha_ratio"], None),
    ("gamma envelope amplitude (env_mean) alone", ["roi__env_mean"], None),
    ("burst_freq_sd (new primary) alone", ["roi__burst_freq_sd"], None),
]:
    r = cv_auc(A[cols].values, yA, resid_cols=rc); r["model"] = name
    if rc is None:
        r.update(loso_acc(A[cols].values, yA))
    rowsA.append(r)
tA = pd.DataFrame(rowsA)[["model", "auc", "auc_lo", "auc_hi", "acc", "loso_auc", "loso_acc"]]
tA.to_csv(OUT / "A_old_metric.csv", index=False)
corrA = {c: spearmanr(A["roi__legacy_std"], A[c], nan_policy="omit")[0] for c in
         ["roi__aperiodic_exponent", "roi__theta_alpha_ratio", "roi__alpha_peak_freq", "roi__env_mean",
          "roi__gamma_abs_logpow", "roi__emg_logpow", "roi__relpow_gamma", "roi__burst_freq_sd"]}
report += ["## A. What drove the old 73% (old metric = SD of instantaneous frequency in 25-80 Hz)\n",
           tA.round(3).to_markdown(index=False), "\n\nSpearman correlation of legacy_std with:\n",
           pd.Series(corrA).round(2).to_markdown(), "\n"]

# ---------------------------------------------------------------- B. the 30-45 Hz power lead + eliminations
# roi__gamma_peak_height is excluded: it is identically 0 (specparam range is 3-30 Hz, so no 30-45 Hz peaks)
GAMMA = ["roi__gamma_abs_logpow", "roi__relpow_gamma", "roi__gamma_osc_logpow", "roi__gamma_above_floor",
         "roi__env_mean", "roi__burst_rate", "roi__hf_slope_30_90", "roi__emg_logpow",
         "emg_sentinel__emg_logpow", "roi__floor_log10", "roi__aperiodic_exponent", "roi__legacy_std"]
COV = {
    "none": [],
    "age_sex": ["age", "sex_m"],
    "+exponent": ["age", "sex_m", "roi__aperiodic_exponent"],
    "+EMG(sentinel 55-90Hz)": ["age", "sex_m", "emg_sentinel__emg_logpow"],
    "+slowing(theta/alpha)": ["age", "sex_m", "roi__theta_alpha_ratio"],
    "+all three": ["age", "sex_m", "roi__aperiodic_exponent", "emg_sentinel__emg_logpow", "roi__theta_alpha_ratio"],
}
rowsB = []
for feat in GAMMA:
    for contrast in [("AD", "CN"), ("FTD", "CN")]:
        row = dict(feature=feat, contrast="-".join(contrast),
                   g=hedges_g(d.loc[d.group == contrast[0], feat], d.loc[d.group == contrast[1], feat]))
        for k, cv in COV.items():
            cv = [c for c in cv if c != feat]
            try:
                r = fl_perm(d, feat, cv, *contrast)
                row[f"t[{k}]"], row[f"p[{k}]"] = r["t"], r["p_perm"]
            except Exception as e:  # noqa: BLE001
                row[f"t[{k}]"], row[f"p[{k}]"] = np.nan, np.nan
        rowsB.append(row)
tB = pd.DataFrame(rowsB)
tB.to_csv(OUT / "B_gamma_eliminations.csv", index=False)
show = tB[tB.contrast == "AD-CN"][["feature", "g"] + [f"p[{k}]" for k in COV]]
report += ["## B. 30-45 Hz measures, AD vs CN: does the difference survive each alternative explanation?\n",
           "p = Freedman-Lane permutation p (2000 perms) for the group term after the listed covariates.\n\n",
           show.round(3).to_markdown(index=False), "\n\nSame for FTD vs CN (is it AD-specific or any dementia?):\n\n",
           tB[tB.contrast == "FTD-CN"][["feature", "g", "p[age_sex]", "p[+all three]"]].round(3).to_markdown(index=False), "\n"]

# ---------------------------------------------------------------- C. topography: EMG-like (temporal/frontal) or not?
REG = ["frontal", "central", "temporal", "parietal", "occipital", "csd_roi"]
rowsC = []
for m in ["gamma_abs_logpow", "relpow_gamma", "gamma_above_floor", "emg_logpow", "aperiodic_exponent", "theta_alpha_ratio", "env_mean"]:
    row = {"metric": m}
    for r in REG:
        c = f"{r}__{m}"
        if c in d:
            row[r] = hedges_g(d.loc[d.group == "AD", c], d.loc[d.group == "CN", c])
    rowsC.append(row)
tC = pd.DataFrame(rowsC); tC.to_csv(OUT / "C_topography_g.csv", index=False)
report += ["## C. Where on the scalp (Hedges g AD-CN per region; muscle is largest at temporal/frontal edges)\n",
           tC.round(2).to_markdown(index=False), "\n"]

# ---------------------------------------------------------------- D. coupling with muscle, within group
rowsD = []
for grp in ["CN", "AD", "FTD"]:
    x = d[d.group == grp]
    for feat in ["roi__gamma_abs_logpow", "roi__gamma_above_floor", "roi__relpow_gamma", "roi__legacy_std", "roi__burst_freq_sd"]:
        rowsD.append(dict(group=grp, feature=feat,
                          rho_emg=spearmanr(x[feat], x["emg_sentinel__emg_logpow"], nan_policy="omit")[0],
                          rho_hfslope=spearmanr(x[feat], x["roi__hf_slope_30_90"], nan_policy="omit")[0],
                          rho_exponent=spearmanr(x[feat], x["roi__aperiodic_exponent"], nan_policy="omit")[0]))
tD = pd.DataFrame(rowsD); tD.to_csv(OUT / "D_within_group_coupling.csv", index=False)
report += ["## D. Within-group coupling of 30-45 Hz measures with muscle (55-90 Hz) and 1/f\n",
           tD.round(2).to_markdown(index=False), "\n"]

# ---------------------------------------------------------------- E. harmonic test + presence + MMSE
E = d.dropna(subset=["roi__osc_f0", "roi__alpha_peak_freq"])
ratio = E["roi__osc_f0"] / E["roi__alpha_peak_freq"]
harm = dict(n_with_peak=len(E), rho_f0_alpha=spearmanr(E["roi__osc_f0"], E["roi__alpha_peak_freq"])[0],
            median_ratio=float(ratio.median()), frac_within_0p15_of_integer=float((np.abs(ratio - ratio.round()) < 0.15).mean()))
pres = d.groupby("group")["roi__osc_present"].agg(["sum", "count"]).assign(frac=lambda t: t["sum"] / t["count"])
ad = d[d.group == "AD"]
mm = {f: spearmanr(ad[f], ad["mmse"], nan_policy="omit")[0] for f in
      ["roi__gamma_above_floor", "roi__gamma_abs_logpow", "roi__relpow_gamma", "roi__legacy_std", "roi__theta_alpha_ratio", "roi__aperiodic_exponent"]}
report += ["## E. Is a 30-45 Hz peak a harmonic of alpha?  Presence by group.  Severity (MMSE within AD)\n",
           f"Subjects with a fitted 30-45 Hz peak: {harm['n_with_peak']}; rho(peak f, alpha f) = {harm['rho_f0_alpha']:.2f}; "
           f"median f_gamma/f_alpha = {harm['median_ratio']:.2f}; fraction within 0.15 of an integer ratio = {harm['frac_within_0p15_of_integer']:.2f} "
           "(about 0.30 expected by chance).\n\n", pres.to_markdown(), "\n\nSpearman rho with MMSE within AD (n=36):\n\n",
           pd.Series(mm).round(2).to_markdown(), "\n"]

(OUT / "report.md").write_text("\n".join(report))
json.dump(dict(harmonic=harm), open(OUT / "E_harmonic.json", "w"), indent=1)
print("\n".join(report))
