"""Ground-truth validation of every candidate instability metric + pre-specified metric selection.

Uses ONLY simulated data. No dataset, no label is touched. The selection rule is fixed here
in code before any real-data result is examined:

  For metric m and factor F (one-at-a-time sweeps around a base signal, several seeds):
      E_F(m) = (max_level_mean - min_level_mean) / pooled within-level SD   (seed-to-seed noise)
  eligible(m)  : Spearman(level means, jitter levels) >= 0.9   (tracks true jitter, positively)
  score(m)     = E_jitter(m) / max_F!=jitter E_F(m)              (specificity to jitter)
  PRIMARY      = argmax score among eligible metrics

Outputs: results/simulation/sim_long.csv, sim_summary.csv, metric_selection.json, sim_sweeps.png
Run:  python scripts/02_simulation_validation.py --seeds 8 --n-surr 10 --jobs 2
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import ROOT, analysis_hash, apply_overrides, load_config  # noqa: E402
from nh.gamma import SURR_METRICS, gii_subject  # noqa: E402
from nh.simulate import BASE, SWEEPS, simulate  # noqa: E402

CANDIDATES = (["if_sd", "if_mad", "if_iqr", "if_awsd", "cycle_cv", "burst_if_sd", "burst_freq_sd",
               "xjit_var", "legacy_std"]
              + [f"{m}_z" for m in SURR_METRICS] + [f"{m}_excess" for m in SURR_METRICS])


def _one(factor, level, seed, n_surr, cfg_feat, base_over=None):
    x, sf = simulate(seed=seed, **{**(base_over or {}), factor: level})
    rng = np.random.default_rng([seed, 7])
    r = gii_subject(x[None], [(0, len(x))], sf, ["sim"], cfg_feat["gamma_band"], cfg_feat, rng,
                    n_surr=n_surr)["sim"]
    return {"factor": factor, "level": level, "seed": seed, **r}


def summarise(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    rows = []
    for m in CANDIDATES:
        if m not in df:
            continue
        rec = {"metric": m}
        for F in SWEEPS:
            d = df[df.factor == F][["level", m]].dropna()
            if d.level.nunique() < 2:
                rec[f"E_{F}"] = np.nan; continue
            means = d.groupby("level")[m].mean()
            sd = np.sqrt(d.groupby("level")[m].var(ddof=1).mean())
            rec[f"E_{F}"] = float((means.max() - means.min()) / sd) if sd > 0 else np.nan
            if F == "jitter_hz":
                rec["rho_jitter"] = float(spearmanr(means.index, means.values)[0])
        nuis = [rec[f"E_{F}"] for F in SWEEPS if F != "jitter_hz" and np.isfinite(rec.get(f"E_{F}", np.nan))]
        rec["max_nuisance_E"] = float(max(nuis)) if nuis else np.nan
        rec["score"] = rec["E_jitter_hz"] / rec["max_nuisance_E"] if nuis else np.nan
        # rounded: with 5 jitter levels Spearman = 0.9 is stored as 0.8999999999999998 and failed ">= 0.9"
        rec["eligible"] = bool(round(rec.get("rho_jitter", 0), 9) >= 0.9)
        rows.append(rec)
    summ = pd.DataFrame(rows).sort_values("score", ascending=False)
    elig = summ[summ.eligible & np.isfinite(summ.score)]
    sel = {"primary_metric": None if elig.empty else elig.iloc[0]["metric"],
           "rule": "argmax E_jitter / max nuisance E among metrics with Spearman(jitter) >= 0.9",
           "ranking": summ[["metric", "score", "rho_jitter", "eligible"]].to_dict("records"),
           "base_signal": BASE, "sweeps": SWEEPS}
    return summ, sel


def plot(df, out):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    show = ["legacy_std", "if_sd", "if_sd_z", "burst_freq_sd", "burst_freq_sd_z", "burst_if_sd", "xjit_var"]
    show = [m for m in show if m in df]
    fig, axes = plt.subplots(len(show), len(SWEEPS), figsize=(3 * len(SWEEPS), 2.2 * len(show)),
                             sharey="row")
    for i, m in enumerate(show):
        for j, F in enumerate(SWEEPS):
            d = df[df.factor == F].groupby("level")[m].agg(["mean", "std"])
            ax = axes[i, j]
            ax.errorbar(d.index, d["mean"], yerr=d["std"], marker="o", lw=1.5,
                        color="#1f6f8b" if F == "jitter_hz" else "#9a9a9a")
            if i == 0: ax.set_title(F, fontsize=9)
            if j == 0: ax.set_ylabel(m, fontsize=9)
            ax.tick_params(labelsize=7)
    fig.suptitle("Metric response to true jitter (blue) vs nuisance factors (grey); mean +/- SD over seeds",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(out, dpi=130)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--n-surr", type=int, default=10)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--out", default=str(ROOT / "results" / "simulation"))
    ap.add_argument("--set", nargs="*", default=None, metavar="KEY=VALUE",
                    help="estimator ablation, e.g. features.if_estimator=sst")
    ap.add_argument("--tag", default=None, help="sub-folder name for this variant's results")
    a = ap.parse_args()
    cfg = apply_overrides(load_config(), a.set)
    base_out = Path(a.out)
    out = base_out / a.tag if a.tag else base_out
    out.mkdir(parents=True, exist_ok=True)
    cal_p = base_out / "calibration.json"      # label-free calibration (02b), if available
    base_over = json.loads(cal_p.read_text())["base_overrides"] if cal_p.exists() else {}
    print("base signal overrides:", base_over or "none (uncalibrated default)")
    tasks = [(F, lv, s) for F, lvls in SWEEPS.items() for lv in lvls for s in range(a.seeds)]
    recs = Parallel(n_jobs=a.jobs, verbose=5)(
        delayed(_one)(F, lv, s, a.n_surr, cfg["features"], base_over) for F, lv, s in tasks)
    df = pd.DataFrame(recs)
    df.to_csv(out / "sim_long.csv", index=False)
    summ, sel = summarise(df)
    summ.to_csv(out / "sim_summary.csv", index=False)
    sel["analysis_hash"] = analysis_hash()
    sel["base_overrides_from_calibration"] = base_over
    sel["variant_overrides"] = a.set or []
    (out / "metric_selection.json").write_text(json.dumps(sel, indent=2, default=float))
    plot(df, out / "sim_sweeps.png")
    print(summ.to_string(index=False))
    print("\nPRIMARY METRIC (simulation-selected):", sel["primary_metric"])


if __name__ == "__main__":
    main()
