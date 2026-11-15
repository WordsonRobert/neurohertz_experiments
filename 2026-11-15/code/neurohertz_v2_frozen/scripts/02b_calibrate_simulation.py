"""Calibrate the simulator's base signal to the real data WITHOUT labels.

Reads one cohort's features_subject.csv (Stage A output; contains no labels), takes POOLED medians
over all subjects of label-free descriptors, simulates a grid of base signals, and picks the grid
point whose descriptors are closest (standardised distance). The result is written to
results/simulation/calibration.json, which 02_simulation_validation.py uses as its base signal.

Descriptors: posterior-ROI aperiodic exponent, gamma power above 1/f, gamma burst rate,
burst duration, envelope CV.

Usage: python scripts/02b_calibrate_simulation.py --dataset ds004504
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import ROOT, load_config  # noqa: E402
from nh.gamma import if_metrics_channel  # noqa: E402
from nh.simulate import simulate  # noqa: E402
from nh.spectral import channel_spectral_features, welch_psd  # noqa: E402

DESC = ["aperiodic_exponent", "gamma_above_floor", "burst_rate", "burst_dur", "env_cv"]
GRID = {"chi": [1.0, 1.5, 2.0, 2.5], "gamma_amp": [0.05, 0.1, 0.2, 0.4, 0.6, 0.9],
        "burst_dur_s": [0.1, 0.25, 0.5]}


def sim_desc(cfg, **kw):
    x, sf = simulate(seed=11, dur_s=120, **kw)
    psd, fr = welch_psd(x[None], sf, cfg["features"]["spectral"]["welch_s"], fmax=min(100, sf / 2 - 1))
    s = channel_spectral_features(psd[0], fr, cfg, None)
    g = if_metrics_channel(x, [(0, len(x))], sf, cfg["features"]["gamma_band"], cfg["features"])
    return {**{k: s[k] for k in DESC if k in s}, **{k: g[k] for k in DESC if k in g}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--variant", default="primary")
    a = ap.parse_args()
    cfg = load_config()
    f = pd.read_csv(ROOT / "results" / "features" / a.dataset / a.variant / "features_subject.csv")
    assert not {"group", "mmse", "diagnosis"} & set(map(str.lower, f.columns)), "feature table must be label-free"
    real = {d: float(f[f"roi__{d}"].median()) for d in DESC}
    spread = {d: float(f[f"roi__{d}"].quantile(.75) - f[f"roi__{d}"].quantile(.25)) or 1.0 for d in DESC}
    rows = []
    for chi, amp, bd in itertools.product(*GRID.values()):
        d = sim_desc(cfg, chi=chi, gamma_amp=amp, burst_dur_s=bd)
        dist = np.sqrt(sum(((d[k] - real[k]) / spread[k]) ** 2 for k in DESC))
        rows.append({"chi": chi, "gamma_amp": amp, "burst_dur_s": bd, **d, "distance": dist})
    grid = pd.DataFrame(rows).sort_values("distance")
    best = grid.iloc[0]
    out = {"dataset": a.dataset, "pooled_real_medians_label_free": real,
           "base_overrides": {"chi": float(best.chi), "gamma_amp": float(best.gamma_amp),
                              "burst_dur_s": float(best.burst_dur_s)},
           "best_distance": float(best.distance)}
    od = ROOT / "results" / "simulation"; od.mkdir(parents=True, exist_ok=True)
    grid.to_csv(od / "calibration_grid.csv", index=False)
    (od / "calibration.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
