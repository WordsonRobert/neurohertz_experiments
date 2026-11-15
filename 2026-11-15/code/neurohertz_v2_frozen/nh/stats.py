"""Inferential statistics (subject-level). Every function takes one row per subject.

Conventions
  * effect sizes always come with 95% CIs; p-values are permutation-based where feasible
  * covariate-adjusted permutation uses Freedman-Lane (permute residuals of the reduced model)
  * multiple channels: max-|t| permutation (family-wise error control across the scalp)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats


# ------------------------------------------------------------------ helpers
def assert_one_row_per_subject(df: pd.DataFrame, col: str = "subject") -> None:
    dup = df[col][df[col].duplicated()].unique()
    if len(dup):
        raise ValueError(f"duplicate subjects (would leak across folds/tests): {list(dup)[:5]}")


def design(df: pd.DataFrame, covars: list[str]) -> pd.DataFrame:
    parts = []
    for c in covars:
        if c not in df or df[c].isna().all():
            continue
        if not pd.api.types.is_numeric_dtype(df[c]):
            parts.append(pd.get_dummies(df[c].astype(str), prefix=c, drop_first=True, dtype=float))
        else:
            parts.append(df[[c]].astype(float))
    X = pd.concat(parts, axis=1) if parts else pd.DataFrame(index=df.index)
    return sm.add_constant(X, has_constant="add")


def hedges_g(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2))
    d = (np.mean(a) - np.mean(b)) / sp
    return float(d * (1 - 3 / (4 * (na + nb) - 9)))


def holm(pvals: dict[str, float]) -> dict[str, float]:
    keys = sorted(pvals, key=lambda k: pvals[k])
    m, out, run = len(keys), {}, 0.0
    for i, k in enumerate(keys):
        run = max(run, min(1.0, (m - i) * pvals[k]))
        out[k] = run
    return out


def fdr_bh(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, float); n = len(p)
    o = np.argsort(p); q = p[o] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n); out[o] = np.minimum(q, 1)
    return out


# ------------------------------------------------------------------ group effects
def hedges_g_bca(a, b, n_boot: int, rng: np.random.Generator, level: float = 0.95) -> list[float]:
    """Bias-corrected and accelerated bootstrap CI for Hedges' g (Efron 1987), resampling within
    each group. Better coverage than the percentile interval at n ~ 30 per group."""
    from scipy.stats import norm
    a, b = np.asarray(a, float), np.asarray(b, float)
    g0 = hedges_g(a, b)
    gb = np.array([hedges_g(rng.choice(a, len(a)), rng.choice(b, len(b))) for _ in range(n_boot)])
    gb = gb[np.isfinite(gb)]
    z0 = norm.ppf(np.clip((np.sum(gb < g0) + 0.5 * np.sum(gb == g0)) / len(gb), 1e-6, 1 - 1e-6))
    jack = np.array([hedges_g(np.delete(a, i), b) for i in range(len(a))] +
                    [hedges_g(a, np.delete(b, j)) for j in range(len(b))])
    dj = jack.mean() - jack
    acc = np.sum(dj ** 3) / (6 * np.sum(dj ** 2) ** 1.5 + 1e-30)
    out = []
    for q in ((1 - level) / 2, (1 + level) / 2):
        zq = norm.ppf(q)
        out.append(float(np.percentile(gb, 100 * norm.cdf(z0 + (z0 + zq) / (1 - acc * (z0 + zq))))))
    return out


def group_effect(df: pd.DataFrame, y: str, group_col: str, target: str, ref: str,
                 covars: list[str], n_perm: int, n_boot: int, seed: int) -> dict:
    d = df[df[group_col].isin([target, ref])].dropna(subset=[y] + [c for c in covars if c in df]).copy()
    assert_one_row_per_subject(d)
    if min((d[group_col] == target).sum(), (d[group_col] == ref).sum()) < 3:
        raise ValueError(f"{y}: fewer than 3 subjects with data in a group")
    d["_grp"] = (d[group_col] == target).astype(float)
    Xr = design(d, covars)
    Xf = Xr.copy(); Xf["_grp"] = d["_grp"].values
    yv = d[y].astype(float).values
    if d[y].nunique() < 3:
        raise ValueError(f"{y}: fewer than 3 distinct values")
    if len(d) < Xf.shape[1] + 3:
        raise ValueError(f"{y}: only {len(d)} subjects for {Xf.shape[1]} model terms")
    fit = sm.OLS(yv, Xf).fit(cov_type="HC3")
    beta, se = fit.params["_grp"], fit.bse["_grp"]
    t_obs = beta / se
    if not np.isfinite(t_obs):     # a NaN statistic would give the smallest possible permutation p
        raise ValueError(f"{y}: group effect undefined (constant values or collinear design)")
    ci = fit.conf_int().loc["_grp"].tolist()

    # Freedman-Lane
    rng = np.random.default_rng(seed)
    red = sm.OLS(yv, Xr.values).fit()
    fitted, resid = np.asarray(red.fittedvalues), np.asarray(red.resid)
    Xf_np = Xf.values
    gi = list(Xf.columns).index("_grp")
    cnt = 0
    for _ in range(n_perm):
        ys = fitted + rng.permutation(resid)
        f2 = sm.OLS(np.asarray(ys), Xf_np).fit(cov_type="HC3")
        cnt += abs(np.asarray(f2.params)[gi] / np.asarray(f2.bse)[gi]) >= abs(t_obs)
    p_perm = (cnt + 1) / (n_perm + 1)

    a, b = yv[d["_grp"] == 1], yv[d["_grp"] == 0]
    g = hedges_g(a, b)
    g_ci = hedges_g_bca(a, b, n_boot, rng)
    return {"feature": y, "contrast": f"{target}-{ref}", "n_target": int(len(a)), "n_ref": int(len(b)),
            "mean_target": float(a.mean()), "mean_ref": float(b.mean()),
            "beta_adj": float(beta), "beta_ci95": [float(ci[0]), float(ci[1])], "t_HC3": float(t_obs),
            "p_param": float(fit.pvalues["_grp"]), "p_perm_freedman_lane": float(p_perm),
            "hedges_g_unadj": g, "hedges_g_ci95": g_ci, "hedges_g_ci_method": "BCa",
            "covariates": [c for c in covars if c in d]}


def partial_spearman(df: pd.DataFrame, x: str, y: str, covars: list[str], n_perm: int, n_boot: int,
                     seed: int) -> dict:
    d = df.dropna(subset=[x, y] + [c for c in covars if c in df]).copy()
    assert_one_row_per_subject(d)
    k = design(d, covars).shape[1] if len(d) else 1
    if len(d) < k + 4:      # never return a permutation p for (almost) no data: NaN r made p = 1/(n_perm+1)
        raise ValueError(f"{x} vs {y}: only {len(d)} subjects with data (need >= {k + 4})")
    if d[x].nunique() < 3 or d[y].nunique() < 3:
        raise ValueError(f"{x} vs {y}: fewer than 3 distinct values")

    def _r(dd):
        rx, ry = stats.rankdata(dd[x]), stats.rankdata(dd[y])
        Z = design(dd.assign(**{c: stats.rankdata(dd[c]) for c in covars
                                 if c in dd and pd.api.types.is_numeric_dtype(dd[c])}), covars).values
        ex = rx - Z @ np.linalg.lstsq(Z, rx, rcond=None)[0]
        ey = ry - Z @ np.linalg.lstsq(Z, ry, rcond=None)[0]
        return float(np.corrcoef(ex, ey)[0, 1]), ex, ey

    r, ex, ey = _r(d)
    if not np.isfinite(r):
        raise ValueError(f"{x} vs {y}: correlation undefined (constant values)")
    rng = np.random.default_rng(seed)
    cnt = sum(abs(np.corrcoef(rng.permutation(ex), ey)[0, 1]) >= abs(r) for _ in range(n_perm))
    boots = []
    for _ in range(n_boot):
        bd = d.iloc[rng.integers(0, len(d), len(d))]
        try:
            boots.append(_r(bd)[0])
        except Exception:
            pass
    return {"x": x, "y": y, "n": int(len(d)), "rho_partial": r,
            "ci95": [float(np.nanpercentile(boots, 2.5)), float(np.nanpercentile(boots, 97.5))],
            "ci90": [float(np.nanpercentile(boots, 5)), float(np.nanpercentile(boots, 95))],
            "p_perm": float((cnt + 1) / (n_perm + 1)), "covariates": covars}


def maxT_channels(wide: pd.DataFrame, channels: list[str], group_col: str, target: str, ref: str,
                  covars: list[str], n_perm: int, seed: int) -> pd.DataFrame:
    """wide: one row per subject, one column per channel (feature value). FWER via max-|t|."""
    d = wide[wide[group_col].isin([target, ref])].dropna(subset=channels).copy()
    assert_one_row_per_subject(d)
    Xr = design(d, covars).values
    g = (d[group_col] == target).astype(float).values[:, None]
    Xf = np.hstack([Xr, g])
    Y = d[channels].astype(float).values

    def _t(Yv):
        beta, *_ = np.linalg.lstsq(Xf, Yv, rcond=None)
        res = Yv - Xf @ beta
        dof = len(Yv) - Xf.shape[1]
        s2 = (res ** 2).sum(0) / dof
        cov = np.linalg.inv(Xf.T @ Xf)[-1, -1]
        return beta[-1] / np.sqrt(s2 * cov)

    t_obs = _t(Y)
    br, *_ = np.linalg.lstsq(Xr, Y, rcond=None)
    fit_r, res_r = Xr @ br, Y - Xr @ br
    rng = np.random.default_rng(seed)
    maxes = np.empty(n_perm)
    for i in range(n_perm):
        maxes[i] = np.abs(_t(fit_r + res_r[rng.permutation(len(Y))])).max()
    p_fwer = [(np.sum(maxes >= abs(t)) + 1) / (n_perm + 1) for t in t_obs]
    return pd.DataFrame({"channel": channels, "t": t_obs, "p_fwer_maxT": p_fwer})


# ------------------------------------------------------------------ reliability
def icc_2_1(M: np.ndarray) -> float:
    """ICC(2,1): two-way random, absolute agreement, single measure. M: subjects x sessions."""
    M = np.asarray(M, float); n, k = M.shape
    gm = M.mean()
    msr = k * ((M.mean(1) - gm) ** 2).sum() / (n - 1)
    msc = n * ((M.mean(0) - gm) ** 2).sum() / (k - 1)
    sse = ((M - M.mean(1, keepdims=True) - M.mean(0, keepdims=True) + gm) ** 2).sum()
    mse = sse / ((n - 1) * (k - 1))
    return float((msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n))


# ------------------------------------------------------------------ ROC
def delong_auc(y: np.ndarray, s: np.ndarray) -> dict:
    """AUC with DeLong standard error and 95% CI (Sun & Xu 2014 fast algorithm)."""
    y = np.asarray(y).astype(int); s = np.asarray(s, float)
    pos, neg = s[y == 1], s[y == 0]
    m, n = len(pos), len(neg)

    def _mid(x):
        return stats.rankdata(x)
    tx, ty, tz = _mid(pos), _mid(neg), _mid(np.concatenate([pos, neg]))
    auc = (tz[:m].sum() - m * (m + 1) / 2) / (m * n)
    v01 = (tz[:m] - tx) / n
    v10 = 1 - (tz[m:] - ty) / m
    se = np.sqrt(np.var(v01, ddof=1) / m + np.var(v10, ddof=1) / n)
    return {"auc": float(auc), "se": float(se),
            "ci95": [float(max(0, auc - 1.96 * se)), float(min(1, auc + 1.96 * se))], "n_pos": m, "n_neg": n}
