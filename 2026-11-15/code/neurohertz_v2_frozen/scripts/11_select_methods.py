"""Choose each Stage-A method LABEL-FREE (no diagnosis, no MMSE is read).

Per dimension in ablations.stage_a:
  * dimensions in selection_rule.simulation_first (estimator, median): pick the option whose
    simulation-selected metric has the highest jitter-specificity score (results/simulation/<dim>-<opt>/),
    provided its split-half ICC on real data is >= min_split_half_icc;
  * all other dimensions: among options with split-half ICC >= min_split_half_icc, pick the smallest
    |Spearman(ROI primary metric, EMG-sentinel 55-90 Hz power)| (least muscle-driven); ties -> higher ICC.
Writes registry/method_selection.json and prints the table. Put the chosen options into
config/pipeline.yaml before freezing; 03_freeze.py records this file's hash.

Usage
  python scripts/11_select_methods.py --dataset ds004504
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import ROOT, analysis_hash, load_config  # noqa: E402
from nh.stats import icc_2_1  # noqa: E402


def variant_stats(fpath: Path, metric: str) -> dict:
    f = pd.read_csv(fpath)
    out = {"n": int(len(f))}
    col, h1, h2 = f"roi__{metric}", f"roi__sh1_{metric}", f"roi__sh2_{metric}"
    if h1 in f and h2 in f:
        M = f[[h1, h2]].dropna().values
        out["split_half_icc"] = float(icc_2_1(M)) if len(M) >= 10 else np.nan
    emg = "emg_sentinel__emg_logpow"
    if col in f and emg in f:
        d = f[[col, emg]].dropna()
        out["abs_emg_coupling"] = float(abs(spearmanr(d[col], d[emg])[0])) if len(d) >= 10 else np.nan
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    a = ap.parse_args()
    cfg = load_config()
    primary = cfg["statistics"]["primary_feature"]
    rule = cfg["ablations"]["selection_rule"]
    judged_on = rule.get("judged_on", {})        # a dimension is judged on the feature it can change
    fdir = ROOT / "results" / "features" / a.dataset
    rows, choice = [], {}
    for dim, opts in cfg["ablations"]["stage_a"].items():
        metric = judged_on.get(dim, primary)
        cand = []
        for opt, ov in opts.items():
            own_base = dim in set(cfg["ablations"].get("surrogate_dims", []))
            vdir = fdir / ("primary" if (not ov and not own_base) else f"{dim}-{opt}")
            fp = vdir / "features_subject.csv"
            if not fp.exists():
                continue
            st = variant_stats(fp, metric)
            simp = ROOT / "results" / "simulation" / f"{dim}-{opt}" / "metric_selection.json"
            if simp.exists():
                rk = {r["metric"]: r["score"] for r in json.loads(simp.read_text())["ranking"]}
                st["sim_score_primary_metric"] = rk.get(metric, np.nan)
            st.update(dimension=dim, option=opt, judged_on=metric)
            cand.append(st); rows.append(st)
        if not cand:
            continue
        ok = [c for c in cand if c.get("split_half_icc", 0) >= rule["min_split_half_icc"]]
        floor_met = bool(ok)
        ok = ok or cand                    # nothing reliable: still rank, but say so (never silently)
        tag = "among reliable options" if floor_met else \
              f"NO option reached split-half ICC >= {rule['min_split_half_icc']}: ranked among ALL options"
        if dim in rule["simulation_first"] and all("sim_score_primary_metric" in c for c in ok):
            best = max(ok, key=lambda c: (np.nan_to_num(c["sim_score_primary_metric"], nan=-1e9), c.get("split_half_icc", 0)))
            why = f"highest simulation jitter-specificity score {tag}"
        else:
            best = min(ok, key=lambda c: (np.nan_to_num(c.get("abs_emg_coupling", np.nan), nan=1e9), -c.get("split_half_icc", 0)))
            why = f"least EMG coupling {tag}"
        if not floor_met:
            print(f"WARNING [{dim}]: {tag}", flush=True)
        choice[dim] = {"option": best["option"], "overrides": opts[best["option"]], "why": why,
                       "reliability_floor_met": floor_met}
    table = pd.DataFrame(rows)
    out = {"dataset": a.dataset, "primary_metric": primary, "rule": rule, "choice": choice,
           "candidates": table.to_dict("records"), "labels_used": False, **analysis_hash()}
    (ROOT / "registry").mkdir(exist_ok=True)
    (ROOT / "registry" / "method_selection.json").write_text(json.dumps(out, indent=2, default=float))
    print(table.to_string(index=False))
    print(json.dumps(choice, indent=2))


if __name__ == "__main__":
    main()
