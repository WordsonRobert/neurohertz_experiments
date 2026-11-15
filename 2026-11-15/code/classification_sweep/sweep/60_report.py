"""Stage 60: collect everything into one report with PRE-DECLARED verdict rules (written 2026-11-15, before any
real-data result of this sweep existed). Rules are mechanical so the verdicts cannot drift toward the hoped-for one.

Verdict rules
  Effect present (E0): a FWER-significant cluster (p < 0.05) overlapping 35-45 Hz in AD-CN for logpsd_csd or
      periodic_csd (age + sex). If none, every explanation below is reported as "nothing to explain at 35-45 Hz",
      and the tests stay descriptive.
  E1 muscle: NOT eliminated if the ROI 35-45 Hz t (AD-CN) loses more than half its size or flips sign when
      (a) only the lowest-EMG 25% of epochs are used, (b) BSS-CCA muscle removal is switched off (nomuscle), or
      (c) per-subject EMG is a covariate.
  E2 ocular/frontal: NOT eliminated if frontal-polar burst excess differs AD-CN (p < 0.05) in the same direction.
  E3 aperiodic: EXPLAINS the effect if logpsd has a 35-45 Hz cluster but periodic_csd does not, while fractal_csd
      has a significant cluster.
  E4 vigilance: NOT eliminated unless the stratified ROI 30-45 Hz effect has the overall sign with |t| > 1 in at
      least 3 of 4 vigilance strata.
  E5 harmonics: NOT eliminated if alpha 1:4 locking differs AD-CN (p < 0.05) AND |rho(alpha_1to4_z,
      periodic_35_45)| > 0.3.
  E6 transients: NOT eliminated if transient rate or gamma_no_transient_delta differs AD-CN (p < 0.05).
  E7 notch/filter: SUSPECT if every 35-45 Hz cluster lies entirely above 42 Hz.
  E8 medication: cannot be tested (no medication list). Reported: whether a frontocentral 15-30 Hz excess exists.
"""
from __future__ import annotations
import argparse, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from common import participants, OUT


def fl(D, y, tgt, ref, rng, covs=("age", "sex_m"), n_perm=5000):
    x = D[D.group.isin([tgt, ref])].dropna(subset=[y, *covs])
    if min((x.group == tgt).sum(), (x.group == ref).sum()) < 4:
        return np.nan, np.nan
    X = np.column_stack([np.ones(len(x)), (x[list(covs)] - x[list(covs)].mean()).values, (x.group == tgt).astype(float)])
    Y = x[y].astype(float).values

    def t_of(v):
        b, *_ = np.linalg.lstsq(X, v, rcond=None); r = v - X @ b
        h = (np.linalg.pinv(X.T @ X) @ X.T)[-1]
        return b[-1] / max(np.sqrt(np.sum(h ** 2 * r ** 2)), 1e-300)
    t0 = t_of(Y); Xr = X[:, :-1]; br, *_ = np.linalg.lstsq(Xr, Y, rcond=None)
    F, R = Xr @ br, Y - Xr @ br
    null = np.array([t_of(F + R[rng.permutation(len(R))]) for _ in range(n_perm)])
    return float(t0), float((np.sum(np.abs(null) >= abs(t0)) + 1) / (n_perm + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    a = ap.parse_args()
    rng = np.random.default_rng(20261115)
    base = OUT / a.dataset
    m = base / "main"; nm = base / "nomuscle"
    P = participants(a.dataset)
    st = pd.read_csv(m / "subject_table.csv", index_col=0)
    D = P[["group", "age", "sex_m", "mmse"]].join(st, how="inner")
    # subject-level group tests
    rows = []
    for c in st.columns:
        for tgt, ref in [("AD", "CN"), ("FTD", "CN"), ("AD", "FTD")]:
            t, p = fl(D, c, tgt, ref, rng)
            rows.append(dict(measure=c, contrast=f"{tgt}-{ref}", t=t, p_perm=p))
    G = pd.DataFrame(rows); G.to_csv(m / "subject_group_tests.csv", index=False)
    g = lambda c, con="AD-CN": G[(G.measure == c) & (G.contrast == con)].iloc[0]  # noqa: E731

    W = pd.read_csv(m / "freq" / "window_35_45.csv"); CL = pd.read_csv(m / "freq" / "clusters.csv")
    w = lambda fam, cov="age_sex", W=W: W[(W.family == fam) & (W.contrast == "AD-CN") & (W.covariates == cov)].iloc[0]  # noqa: E731
    sig = CL[(CL.p_fwer < 0.05) & (CL.contrast == "AD-CN") & (CL.covariates == "age_sex")]
    in_win = lambda fam: sig[(sig.family == fam) & (sig.f_hi >= 35) & (sig.f_lo <= 45)]  # noqa: E731
    v = {}
    e0 = len(in_win("logpsd_csd")) + len(in_win("periodic_csd")) > 0
    v["E0 effect at 35-45 Hz"] = ("PRESENT" if e0 else "ABSENT",
                                  f"clusters overlapping 35-45 Hz: logpsd_csd {len(in_win('logpsd_csd'))}, periodic_csd {len(in_win('periodic_csd'))}")
    t_all = w("logpsd_csd").roi_mean_t_35_45
    t_low = w("logpsd_csd_lowemg25").roi_mean_t_35_45
    t_emg = w("logpsd_csd", "age_sex_emg").roi_mean_t_35_45
    t_nom = np.nan
    if (nm / "freq" / "window_35_45.csv").exists():
        Wn = pd.read_csv(nm / "freq" / "window_35_45.csv")
        t_nom = w("logpsd_csd", W=Wn).roi_mean_t_35_45
    keep = lambda t2: np.isfinite(t2) and np.sign(t2) == np.sign(t_all) and abs(t2) >= 0.5 * abs(t_all)  # noqa: E731
    e1_ok = keep(t_low) and keep(t_emg) and (keep(t_nom) or not np.isfinite(t_nom))
    v["E1 muscle"] = ("eliminated" if e1_ok else "NOT eliminated",
                      f"ROI 35-45 Hz t: all epochs {t_all:.2f}, lowest-EMG 25% {t_low:.2f}, +EMG covariate {t_emg:.2f}, no BSS-CCA {t_nom:.2f}")
    r = g("burst_excess_fp")
    v["E2 ocular/frontal-polar"] = ("NOT eliminated" if (r.p_perm < 0.05 and np.sign(r.t) == np.sign(t_all)) else "eliminated",
                                    f"frontal-polar burst excess AD-CN t = {r.t:.2f}, p = {r.p_perm:.3f}")
    fr_sig = len(sig[sig.family == "fractal_csd"]) > 0
    e3 = len(in_win("logpsd_csd")) > 0 and len(in_win("periodic_csd")) == 0 and fr_sig
    v["E3 aperiodic"] = ("EXPLAINS the 35-45 Hz difference" if e3 else ("fractal part differs" if fr_sig else "no fractal cluster"),
                         f"significant AD-CN clusters: fractal {int(fr_sig)} (any frequency); periodic in 35-45 Hz {len(in_win('periodic_csd'))}; "
                         f"periodic ROI 35-45 t = {w('periodic_csd').roi_mean_t_35_45:.2f}")
    VS = pd.read_csv(m / "freq" / "vigilance_strata.csv"); vs = VS[VS.contrast == "AD-CN"]
    n_cons = int(((np.sign(vs.t) == np.sign(t_all)) & (vs.t.abs() > 1)).sum())
    v["E4 vigilance"] = ("eliminated" if n_cons >= 3 else "NOT eliminated",
                         "per-stratum t (low->high alpha/theta): " + ", ".join(f"{x:.2f}" for x in vs.t))
    r5 = g("alpha_1to4_z"); rho = spearmanr(D.alpha_1to4_z, D.periodic_35_45, nan_policy="omit")[0]
    v["E5 alpha harmonics"] = ("NOT eliminated" if (r5.p_perm < 0.05 and abs(rho) > 0.3) else "eliminated",
                               f"1:4 locking AD-CN t = {r5.t:.2f}, p = {r5.p_perm:.3f}; rho with periodic 35-45 = {rho:.2f}")
    r6a, r6b = g("transient_rate"), g("gamma_no_transient_delta")
    v["E6 sharp transients"] = ("NOT eliminated" if min(r6a.p_perm, r6b.p_perm) < 0.05 else "eliminated",
                                f"transient rate AD-CN t = {r6a.t:.2f}, p = {r6a.p_perm:.3f}; gamma change without transients t = {r6b.t:.2f}, p = {r6b.p_perm:.3f}")
    wins = pd.concat([in_win("logpsd_csd"), in_win("periodic_csd")])
    v["E7 notch/filter edge"] = ("SUSPECT" if len(wins) and (wins.f_lo >= 42).all() else "not suspected",
                                 "; ".join(f"{r.family} {r.f_lo:.1f}-{r.f_hi:.1f} Hz" for r in wins.itertuples()) or "no 35-45 Hz cluster")
    beta = sig[(sig.family == "logpsd_csd") & (sig.f_lo <= 30) & (sig.f_hi >= 15)]
    v["E8 medication (signature only)"] = ("untestable", f"beta-range (15-30 Hz) AD-CN clusters: "
                                           + ("; ".join(f"{r.f_lo:.1f}-{r.f_hi:.1f} Hz sign {r.sign:+d} [{r.channels}]" for r in beta.itertuples()) or "none"))
    rep = ["# Classification sweep: elimination report (EXPLORATORY)\n",
           f"Dataset {a.dataset}; n = {len(D)} ({D.group.value_counts().to_dict()}). Verdict rules are in the header "
           "of sweep/60_report.py and were fixed before any real-data result existed.\n",
           "| Explanation | Verdict | Evidence |", "|---|---|---|"]
    rep += [f"| {k} | {vv[0]} | {vv[1]} |" for k, vv in v.items()]
    rep += ["\n## All significant spectral clusters (p_FWER < 0.05)\n",
            CL[CL.p_fwer < 0.05].round(3).to_markdown(index=False) if (CL.p_fwer < 0.05).any() else "none",
            "\n## Subject-level measures, group tests (Freedman-Lane, age + sex, 5000 perms)\n",
            G.pivot(index="measure", columns="contrast", values="p_perm").round(4).to_markdown()]
    for sub in ["bursts_p95", "bursts_p99"]:
        if (m / sub / "group_tests.csv").exists():
            bt = pd.read_csv(m / sub / "group_tests.csv"); ty = pd.read_csv(m / sub / "burst_types.csv")
            meta = json.load(open(m / sub / "typing_meta.json"))
            rep += [f"\n## Burst types ({sub}): K = {meta['K']}, stability ARI {meta['stability_ari_mean']:.2f}\n",
                    ty[["type", "share", "auto_name", "frac_roi", "mean_f_mean", "mean_nb_index", "mean_emg_coact"]].round(3).to_markdown(index=False),
                    "\n", bt[(bt.covariates == "age_sex") & (bt.p_perm < 0.1)].round(4).to_markdown(index=False) or "no type differs (p < 0.1)"]
    for f in ["stratify/stratify_meta.json"]:
        if (m / f).exists():
            rep += ["\n## Stratification\n", "```", (m / f).read_text(), "```"]
    if (m / "predict" / "prediction.csv").exists():
        pr = pd.read_csv(m / "predict" / "prediction.csv")
        rep += ["\n## Prediction (nested CV, 20 repeats)\n", pr.round(3).to_markdown(index=False)]
    (m / "REPORT.md").write_text("\n".join(rep))
    json.dump({k: list(vv) for k, vv in v.items()}, open(m / "verdicts.json", "w"), indent=1)
    print("\n".join(rep[:14]))


if __name__ == "__main__":
    main()
