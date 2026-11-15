"""Stage 57: frequency x electrode screen of instability (stage 13 output), EXPLORATORY.

Two questions, answered from the same run:
  SEPARATING  which frequency x electrode cells' instability differs between groups (AD-CN, FTD-CN, AD-FTD)?
  REFERENCE   which cells are reliable AND show no group difference (candidate reference / negative-control
              measures for later analyses)?

Label-free first:
  A reliability   per cell (metric, window, electrode): coverage, split-half ICC(2,1), Spearman-Brown.
                  RELIABLE = SB-ICC >= 0.6 and >= 80% of subjects measurable.
With labels:
  B cluster tests Freedman-Lane cluster permutation over window x electrode (adjacent windows; neighbouring
                  electrodes), separately for grid A (2-46 Hz) and grid B (54-90 Hz), per metric (raw and
                  __excess), contrast and covariate ladder: L0 age+sex, L1 +slowing (theta/alpha), L2 +1/f.
                  Cells with < 80% coverage are held at t = 0 (cannot join a cluster); other missing values are
                  set to the cell median, blind to group (pulls toward no difference).
                  Each cluster test controls the family-wise error over its own window x electrode map only.
                  Every grid x ladder holds 30 such maps (10 instability metrics x 3 contrasts), so a cluster is
                  called significant only if p_family = min(1, 30 x p_fwer) < 0.05 (Bonferroni over the maps; the
                  presence measure snr_median is its own family of 3). Added 2026-11-16 after the first full-size
                  synthetic control: under the uncorrected rule one null cluster is expected per ~30 maps (one
                  appeared in grid B, where nothing was injected). No real-data result existed at that point.
  C reference     reliable cells whose standardized group difference (L0) is EQUIVALENT to zero in every contrast:
                  90% CI of d inside +/- 0.5 (two one-sided tests). A looser tier lists reliable cells with
                  |t| < 1 in every contrast.
  D prediction    nested CV; in each training fold the single best reliable cell (training-fold AUC) is chosen and
                  added to the slowing + 1/f baseline; whole-pipeline permutation p (selection included).
Outputs: results/<ds>/<variant>/freqinst/*.csv, t-map PNGs, REPORT_FREQ_INSTABILITY.md
"""
from __future__ import annotations
import argparse, importlib.util, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm
from common import variant_dir, participants, OUT

HERE = Path(__file__).resolve().parent
def _load(name, fn):
    s = importlib.util.spec_from_file_location(name, HERE / fn); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m
s20 = _load("s20", "20_frequency_resolved.py")
s55 = _load("s55", "55_band_instability_analysis.py")

SEED = 20261116
METRICS = ["if_sd", "slip_frac", "period_cv", "pf_sd_epochs", "burst_f_sd"]       # SNR-matched (sub-bin mean)
KINDS = ["", "__excess"]                                                             # raw, beyond the spectrum
PRESENCE = ["snr_median"]
BASE = s55.BASE
CONTRASTS = [("AD", "CN"), ("FTD", "CN"), ("AD", "FTD")]
LADDERS = {"L0": ["age", "sex_m"], "L1": ["age", "sex_m", "theta_alpha"],
           "L2": ["age", "sex_m", "theta_alpha", "fractal_slope"]}
EQ_BOUND = 0.5
N_MAPS_INST = len(METRICS) * len(KINDS) * len(CONTRASTS)   # 30 maps per grid x ladder
N_MAPS_PRES = len(PRESENCE) * len(CONTRASTS)
warnings.filterwarnings("ignore", category=RuntimeWarning)       # all-NaN cells (low coverage) are expected
warnings.filterwarnings("ignore", category=FutureWarning)


def load(dataset, variant):
    fs = sorted((variant_dir(dataset, variant) / "freqinst").glob("sub-*.csv.gz"))
    keep = set(m + k for m in METRICS for k in KINDS) | set(PRESENCE)
    L = pd.concat([pd.read_csv(f).query("metric in @keep") for f in fs], ignore_index=True)
    return L


def cube(L, part, metric, grid, subjects, chs):
    """subjects x (window-major, electrode-minor) matrix for one metric, part and grid."""
    x = L[(L.part == part) & (L.metric == metric) & (L.grid == grid)]
    wins = sorted(x.win_lo.unique())
    idx = pd.MultiIndex.from_product([wins, chs], names=["win_lo", "ch"])
    M = x.pivot_table(index="subject", columns=["win_lo", "ch"], values="value", aggfunc="first")
    M = M.reindex(index=subjects, columns=idx)
    return M, wins


def plot_map(t, wins, width, chs, sig, title, path):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    T = t.reshape(len(wins), len(chs))
    fig, ax = plt.subplots(figsize=(9, 4))
    v = max(3.0, np.nanmax(np.abs(T)))
    im = ax.imshow(T.T, aspect="auto", cmap="RdBu_r", vmin=-v, vmax=v, origin="lower",
                   extent=[wins[0], wins[-1] + 2, -0.5, len(chs) - 0.5])
    if sig is not None and sig.any():
        S = sig.reshape(len(wins), len(chs))
        yy, xx = np.nonzero(S.T)
        ax.scatter(np.asarray(wins)[xx] + 1, yy, s=6, c="k")
    ax.set_yticks(range(len(chs))); ax.set_yticklabels(chs, fontsize=6)
    ax.set_xlabel(f"window start (Hz), window width {width:g} Hz"); ax.set_title(title, fontsize=9)
    fig.colorbar(im, ax=ax, label="t"); fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="main")
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--n-perm-cv", type=int, default=200)
    ap.add_argument("--n-rep", type=int, default=20)
    a = ap.parse_args()
    rng = np.random.default_rng(SEED)
    out = OUT / a.dataset / a.variant / "freqinst"; (out / "maps").mkdir(parents=True, exist_ok=True)
    L = load(a.dataset, a.variant)
    subjects = sorted(L.subject.unique())
    chs = [c for c in ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "T3", "C3", "Cz", "C4", "T4", "T5", "P3",
                       "Pz", "P4", "T6", "O1", "O2"] if c in set(L.ch)]
    grids = [g for g in ("A", "B") if g in set(L.grid)]
    width = float((L.win_hi - L.win_lo).iloc[0])
    feats = [m + k for m in METRICS for k in KINDS] + PRESENCE

    # ---------------- A. reliability per cell (label-free)
    cubes, rel_rows = {}, []
    for g in grids:
        for f in feats:
            Ma, wins = cube(L, "all", f, g, subjects, chs)
            M1, _ = cube(L, "h1", f, g, subjects, chs); M2, _ = cube(L, "h2", f, g, subjects, chs)
            cubes[(g, f)] = (Ma, wins)
            for j, (w, ch) in enumerate(Ma.columns):
                icc = s55.icc21(M1.iloc[:, j].values, M2.iloc[:, j].values)
                rel_rows.append(dict(grid=g, feature=f, win_lo=w, win_hi=w + width, ch=ch,
                                     coverage=float(Ma.iloc[:, j].notna().mean()), icc_half=icc))
    rel = pd.DataFrame(rel_rows)
    rel["icc_sb"] = 2 * rel.icc_half / (1 + rel.icc_half)
    rel["reliable"] = (rel.icc_sb >= 0.6) & (rel.coverage >= 0.8)
    rel.to_csv(out / "A_reliability_cells.csv", index=False)
    rel_sum = rel.groupby(["grid", "feature"]).agg(cells=("reliable", "size"), reliable=("reliable", "sum"),
                                                   median_icc_sb=("icc_sb", "median")).reset_index()
    rel_sum.to_csv(out / "A_reliability_summary.csv", index=False)
    print("[57] reliability\n", rel_sum.to_string(index=False), flush=True)

    # ---------------- labels
    P = participants(a.dataset)
    st = pd.read_csv(OUT / a.dataset / a.variant / "subject_table.csv", index_col=0)
    D = P[["group", "age", "sex_m", "mmse"]].join(st[BASE], how="inner")
    D = D.loc[[s for s in subjects if s in D.index]]
    ch_adj = s20.ch_adjacency(chs)

    # ---------------- B. cluster tests + per-cell t
    cl_rows, cell_rows = [], []
    for g in grids:
        for f in feats:
            Ma, wins = cubes[(g, f)]
            adj = s20.grid_adjacency(len(wins), ch_adj)
            cov_ok = Ma.notna().mean().values >= 0.8
            for tgt, ref in CONTRASTS:
                for lad, covs in LADDERS.items():
                    x = D[D.group.isin([tgt, ref])].dropna(subset=covs)
                    Y = Ma.loc[x.index].values.astype(float)
                    med = np.nanmedian(np.where(cov_ok, Y, np.nan), 0) if Y.size else None
                    Y = np.where(np.isfinite(Y), Y, med)
                    Y[:, ~cov_ok] = 0.0
                    Y = np.nan_to_num(Y)
                    gvec = (x.group == tgt).astype(float).values
                    C = x[covs].astype(float).values; C = C - C.mean(0)
                    X = np.column_stack([np.ones(len(x)), C, gvec]); j = X.shape[1] - 1
                    t_obs, res, thr = s20.fl_cluster_test(Y, X, j, adj, a.n_perm, rng)
                    t_obs = np.where(cov_ok, t_obs, np.nan)
                    sig = np.zeros(len(t_obs), bool)
                    for sign, idx, mass, p in res:
                        if p * (N_MAPS_PRES if f in PRESENCE else N_MAPS_INST) < 0.05:
                            sig[idx] = True
                        wi, ci = idx // len(chs), idx % len(chs)
                        pk = idx[np.nanargmax(np.abs(t_obs[idx]))]
                        cl_rows.append(dict(grid=g, feature=f, contrast=f"{tgt}-{ref}", ladder=lad, sign=sign,
                                            mass=mass, p_fwer=p, f_lo=wins[wi.min()], f_hi=wins[wi.max()] + width,
                                            peak_win=f"{wins[pk // len(chs)]:g}-{wins[pk // len(chs)] + width:g}",
                                            ch_peak=chs[pk % len(chs)], t_peak=float(t_obs[pk]), n_cells=len(idx),
                                            channels=" ".join(sorted({chs[c] for c in ci}))))
                    n1, n0 = int(gvec.sum()), int(len(gvec) - gvec.sum())
                    for k, (w, ch) in enumerate(Ma.columns):
                        cell_rows.append(dict(grid=g, feature=f, win_lo=w, ch=ch, contrast=f"{tgt}-{ref}",
                                              ladder=lad, t=t_obs[k], n1=n1, n0=n0, in_sig_cluster=bool(sig[k])))
                    if lad in ("L0", "L1") and not f.startswith("snr"):
                        plot_map(np.nan_to_num(t_obs), wins, width, chs, sig,
                                 f"{f} grid {g} {tgt}-{ref} {lad}", out / "maps" / f"t_{g}_{f}_{tgt}-{ref}_{lad}.png")
            print(f"[57] grid {g} {f}: cluster tests done", flush=True)
    CL = pd.DataFrame(cl_rows)
    if len(CL):
        CL["family"] = np.where(CL.feature.str.startswith("snr"), "presence", "instability")
        CL["n_maps"] = np.where(CL.family == "presence", N_MAPS_PRES, N_MAPS_INST)
        CL["p_family"] = np.minimum(1.0, CL.p_fwer * CL.n_maps)
    CL.to_csv(out / "B_clusters.csv", index=False)
    CE = pd.DataFrame(cell_rows)
    # standardized difference and its 90% CI (L0)
    CE["d"] = CE.t * np.sqrt(1 / CE.n1 + 1 / CE.n0)
    se = np.sqrt(1 / CE.n1 + 1 / CE.n0 + CE.d ** 2 / (2 * (CE.n1 + CE.n0)))
    z90 = norm.ppf(0.95)
    CE["d_lo90"], CE["d_hi90"] = CE.d - z90 * se, CE.d + z90 * se
    CE.to_csv(out / "B_cells.csv", index=False)

    # ---------------- C. reference cells (reliable, no group difference)
    l0 = CE[CE.ladder == "L0"].merge(rel[["grid", "feature", "win_lo", "ch", "reliable", "icc_sb", "coverage"]],
                                     on=["grid", "feature", "win_lo", "ch"])
    l0 = l0[l0.reliable]
    agg = l0.groupby(["grid", "feature", "win_lo", "ch"]).agg(
        icc_sb=("icc_sb", "first"), coverage=("coverage", "first"), n_contrasts=("contrast", "nunique"),
        max_abs_t=("t", lambda v: np.nanmax(np.abs(v))),
        max_abs_d_bound=("d", lambda v: np.nan)).reset_index()
    bounds = l0.assign(b=np.maximum(np.abs(l0.d_lo90), np.abs(l0.d_hi90))).groupby(
        ["grid", "feature", "win_lo", "ch"]).b.max().rename("max_ci90_bound").reset_index()
    agg = agg.drop(columns="max_abs_d_bound").merge(bounds, on=["grid", "feature", "win_lo", "ch"])
    agg["equivalent"] = (agg.n_contrasts == 3) & (agg.max_ci90_bound < EQ_BOUND)
    agg["no_detectable_difference"] = (agg.n_contrasts == 3) & (agg.max_abs_t < 1.0)
    agg["win_hi"] = agg.win_lo + width
    agg.sort_values(["equivalent", "max_ci90_bound"], ascending=[False, True]).to_csv(out / "C_reference_cells.csv", index=False)

    # ---------------- D. prediction with in-fold selection of one reliable cell
    W = {}
    for g in grids:
        for f in feats:
            Ma, _ = cubes[(g, f)]
            for (w, ch) in Ma.columns:
                W[f"{g}|{f}|{w:g}-{w + width:g}|{ch}"] = Ma[(w, ch)]
    W = pd.DataFrame(W)
    relk = {f"{r.grid}|{r.feature}|{r.win_lo:g}-{r.win_hi:g}|{r.ch}" for r in rel[rel.reliable].itertuples()}
    rowsD = []
    for tgt, ref in CONTRASTS:
        x = D[D.group.isin([tgt, ref])].dropna(subset=BASE)
        y = (x.group == tgt).astype(int).values
        Bm = x[BASE].values
        Wx = W.reindex(x.index)
        pools = {"grid A, beyond spectrum": [c for c in relk if c.startswith("A|") and "__excess" in c],
                 "grid A, raw": [c for c in relk if c.startswith("A|") and "__excess" not in c and "|snr" not in c],
                 "grid B, all instability": [c for c in relk if c.startswith("B|") and "|snr" not in c]}
        for name, pool in pools.items():
            pool = sorted(pool)
            if not pool:
                rowsD.append(dict(contrast=f"{tgt}-{ref}", pool=name, n_cells=0)); continue
            Fm = Wx[pool].values
            base = np.array([s55.cv_select(Bm, Fm, y, r, base_only=True)[0] for r in range(a.n_rep)])
            full = [s55.cv_select(Bm, Fm, y, r) for r in range(a.n_rep)]
            alone = [s55.cv_select(np.empty((len(y), 0)), Fm, y, r) for r in range(a.n_rep)]
            fa = np.array([f_[0] for f_ in full]); al = np.array([f_[0] for f_ in alone])
            picks = pd.Series([pool[j] for f_ in alone for j in f_[2]]).value_counts(normalize=True).head(5)
            pr = np.random.default_rng(SEED)
            null_alone = np.array([s55.cv_select(np.empty((len(y), 0)), Fm, y, i, pr.permutation(y))[0]
                                   for i in range(a.n_perm_cv)])
            null_full = np.array([s55.cv_select(Bm, Fm, y, i, pr.permutation(y))[0] for i in range(a.n_perm_cv)])
            d = fa - base
            rowsD.append(dict(contrast=f"{tgt}-{ref}", pool=name, n_cells=len(pool), n=len(y),
                              auc_baseline=base.mean(), auc_cell_alone=al.mean(),
                              p_alone=(np.sum(null_alone >= al.mean()) + 1) / (a.n_perm_cv + 1),
                              auc_baseline_plus=fa.mean(), p_plus=(np.sum(null_full >= fa.mean()) + 1) / (a.n_perm_cv + 1),
                              gain=d.mean(), gain_lo=np.percentile(d, 2.5), gain_hi=np.percentile(d, 97.5),
                              top_picks_alone="; ".join(f"{k} ({v:.0%})" for k, v in picks.items())))
            print(f"[57] {tgt}-{ref} {name}: alone {al.mean():.3f} base {base.mean():.3f} base+ {fa.mean():.3f}", flush=True)
    DP = pd.DataFrame(rowsD); DP.to_csv(out / "D_prediction.csv", index=False)

    # ---------------- report
    sigc = CL[CL.p_family < 0.05].sort_values(["grid", "feature", "contrast", "ladder", "p_fwer"])
    nomc = CL[(CL.p_fwer < 0.05) & (CL.p_family >= 0.05)].sort_values(["grid", "feature", "contrast", "ladder", "p_fwer"])
    ref_eq = agg[agg.equivalent]; ref_nd = agg[agg.no_detectable_difference]
    cnt = lambda d_: d_.groupby(["grid", "feature"]).size().rename("cells").reset_index() if len(d_) else pd.DataFrame()
    rep = ["# Frequency x electrode instability screen (EXPLORATORY)\n",
           f"Dataset {a.dataset}; n = {len(D)} ({D.group.value_counts().to_dict()}). Windows {width:g} Hz wide in 2 Hz "
           f"steps; grid A 2-46 Hz, grid B 54-90 Hz (above ~45 Hz mostly muscle; ds004504 has a 70 Hz amplifier "
           f"filter). {len(chs)} electrodes (CSD). Metrics: {', '.join(METRICS)} (SNR-matched), each raw and beyond "
           f"the spectrum (__excess); presence: snr_median.\n",
           "## A. Reliability (cells with SB-ICC >= 0.6 and coverage >= 80%)\n", rel_sum.round(3).to_markdown(index=False),
           "\n## B. Significant clusters (Freedman-Lane; p_family = 30 x p_FWER < 0.05)\n",
           "Single-cell clusters (n_cells = 1) rest on one window at one electrode; read them with care.\n",
           sigc.drop(columns=["mass"]).round(4).to_markdown(index=False) if len(sigc) else "none",
           "\nClusters with p_FWER < 0.05 within their own map that do not survive the correction over maps:\n",
           nomc.drop(columns=["mass"]).round(4).to_markdown(index=False) if len(nomc) else "none",
           "\n## C. Reference cells: reliable, and equivalent to no group difference in all three contrasts "
           f"(90% CI of d within +/- {EQ_BOUND})\n",
           cnt(ref_eq).to_markdown(index=False) if len(ref_eq) else "none",
           "\nTop 30 by tightest bound:\n",
           ref_eq.sort_values("max_ci90_bound").head(30).round(3).to_markdown(index=False) if len(ref_eq) else "none",
           "\nLooser tier (reliable, |t| < 1 in all three contrasts), counts:\n",
           cnt(ref_nd).to_markdown(index=False) if len(ref_nd) else "none",
           "\n## D. Prediction with in-fold selection of one reliable cell (baseline: slowing + 1/f)\n",
           DP.round(3).to_markdown(index=False)]
    (out / "REPORT_FREQ_INSTABILITY.md").write_text("\n".join(rep))
    print("[57] done ->", out)


if __name__ == "__main__":
    main()
