"""Specification curve (Simonsohn, Simmons & Nelson 2020) for H1 across the method multiverse.

Every factorial variant (scripts/10_run_ablations.py --mode factorial) gives one estimate of the
AD-vs-CN effect on the primary metric (age + sex adjusted). This script REPORTS the whole curve and a
joint test; it is never used to choose the pipeline (that is 11_select_methods.py, label-free).

Joint test: the group labels are permuted ONCE per permutation and applied to every specification
(after residualising each outcome on the covariates), keeping the dependence between specifications.
Statistics: median t across specifications, and the number of specifications significant in the
observed direction. p = share of permutations at least as extreme.

Usage
  python scripts/12_specification_curve.py --dataset ds004504 [--dev-unblind-reason "..."]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import ROOT, analysis_hash, load_config  # noqa: E402
from nh.datasets import get_adapter  # noqa: E402
from nh.labels import open_labels  # noqa: E402
from nh.stats import design, group_effect  # noqa: E402


def tstat(y, g, Z):
    """t of the group term after residualising y and g on covariates Z (Frisch-Waugh-Lovell)."""
    by = np.linalg.lstsq(Z, y, rcond=None)[0]; bg = np.linalg.lstsq(Z, g, rcond=None)[0]
    ry, rg = y - Z @ by, g - Z @ bg
    beta = (rg @ ry) / (rg @ rg)
    res = ry - beta * rg
    se = np.sqrt((res @ res) / (len(y) - Z.shape[1] - 1) / (rg @ rg))
    return beta / se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--dev-unblind-reason", default=None)
    ap.add_argument("--n-perm", type=int, default=2000)
    a = ap.parse_args()
    cfg = load_config(); st = cfg["statistics"]
    P = f"roi__{st['primary_feature']}"
    fdir = ROOT / "results" / "features" / a.dataset
    specs = sorted(p.name for p in fdir.glob("mv__*") if (p / "features_subject.csv").exists())
    if not specs:
        sys.exit("No factorial variants found; run 10_run_ablations.py --mode factorial first.")
    labels = open_labels(get_adapter(a.dataset), purpose="specification curve",
                         dev_unblind_reason=a.dev_unblind_reason)
    lab = labels[labels.group.isin(["AD", "CN"])][["subject", "group", "age", "sex"]]
    covars = [c for c in st["covariates"] if c in lab and lab[c].notna().any()]
    # common subject set across specs (so differences are methods, not samples)
    fcov = [f"roi__{c}" for c in st.get("feature_covariates", [])]     # taken from EACH spec's own features
    tabs = {s: pd.read_csv(fdir / s / "features_subject.csv")[["subject", P] + fcov].dropna() for s in specs}
    common = set(lab.subject)
    for t in tabs.values():
        common &= set(t.subject)
    lab = lab[lab.subject.isin(common)].sort_values("subject").reset_index(drop=True)
    g = (lab.group == "AD").astype(float).values
    Y = np.column_stack([tabs[s].set_index("subject").loc[lab.subject, P].values for s in specs])
    def lab_spec(j):
        t = tabs[specs[j]].set_index("subject").loc[lab.subject]
        return lab.assign(**{c: t[c].values for c in fcov})
    Zs = [design(lab_spec(j), covars + fcov).values for j in range(len(specs))]

    rows = []
    for j, s in enumerate(specs):
        d = lab_spec(j).assign(**{P: Y[:, j]})
        r = group_effect(d, P, "group", "AD", "CN", covars + fcov, 999, 500, st["seed"])
        rows.append({"spec": s, **{k: v for k, v in (p.split("-", 1) for p in s[4:].split("__"))},
                     "hedges_g": r["hedges_g_unadj"], "beta": r["beta_adj"], "ci_lo": r["beta_ci95"][0],
                     "ci_hi": r["beta_ci95"][1], "t": r["t_HC3"], "p": r["p_perm_freedman_lane"]})
    curve = pd.DataFrame(rows).sort_values("beta").reset_index(drop=True)
    t_obs = np.array([tstat(Y[:, j], g, Zs[j]) for j in range(len(specs))])
    sign = np.sign(np.median(t_obs)) or 1.0
    crit = 1.96
    med_obs, n_sig_obs = np.median(t_obs), int(np.sum(sign * t_obs > crit))
    rng = np.random.default_rng(st["seed"])
    med_null, nsig_null = [], []
    for _ in range(a.n_perm):
        gp = rng.permutation(g)
        tp = np.array([tstat(Y[:, j], gp, Zs[j]) for j in range(len(specs))])
        med_null.append(np.median(tp)); nsig_null.append(int(np.sum(sign * tp > crit)))
    med_null, nsig_null = np.array(med_null), np.array(nsig_null)
    joint = {"n_specs": len(specs), "n_subjects": int(len(lab)), "median_t": float(med_obs),
             "p_median_t": float((np.sum(np.abs(med_null) >= abs(med_obs)) + 1) / (a.n_perm + 1)),
             "n_significant_same_direction": n_sig_obs,
             "p_n_significant": float((np.sum(nsig_null >= n_sig_obs) + 1) / (a.n_perm + 1))}
    odir = ROOT / "results" / "analysis" / a.dataset / "specification_curve"
    odir.mkdir(parents=True, exist_ok=True)
    curve.to_csv(odir / "curve.csv", index=False)
    (odir / "joint_test.json").write_text(json.dumps({"evidence_status": labels.attrs["evidence_status"],
                                                      **joint, **analysis_hash()}, indent=2, default=float))
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(max(6, len(specs) * 0.25), 3.6))
        x = np.arange(len(curve))
        ax.errorbar(x, curve.beta, yerr=[curve.beta - curve.ci_lo, curve.ci_hi - curve.beta], fmt="o", ms=3,
                    color="#1f6f8b", ecolor="#9fbfcc")
        ax.axhline(0, color="#888", lw=0.8)
        ax.set_xlabel("specification (sorted by effect)"); ax.set_ylabel("AD - CN, adjusted")
        ax.set_title(f"Specification curve, {len(specs)} pipelines; median t = {med_obs:.2f}, joint p = {joint['p_median_t']:.3f}",
                     fontsize=9)
        fig.tight_layout(); fig.savefig(odir / "curve.png", dpi=140)
    except Exception:
        pass
    print(curve.to_string(index=False)); print(json.dumps(joint, indent=2))


if __name__ == "__main__":
    main()
