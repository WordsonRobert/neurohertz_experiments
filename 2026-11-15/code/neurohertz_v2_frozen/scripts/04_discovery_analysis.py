"""Stage B: inferential analysis on the discovery cohort (ds004504), per docs/ANALYSIS_PLAN.md.

Hierarchy (fixed-sequence gatekeeping at alpha = 0.05; a hypothesis is only declared
confirmed if every hypothesis before it was):
  H1  AD vs CN on the primary metric (posterior ROI), adjusted for age + sex
  H2  within AD: partial Spearman(primary metric, MMSE | age, sex)
  H3  H1 survives adjustment for gamma power above 1/f, aperiodic exponent, envelope,
      burst rate, alpha peak frequency and EMG index (the effect is not just spectrum/SNR/muscle)
  H4  specificity: AD vs FTD and FTD vs CN (Holm within H4)
Always reported (no gate): scalp topography with max-T FWER, robustness variants, and an
EXPLORATORY table of every candidate metric (BH-FDR), clearly labelled as such.

Usage
  python scripts/04_discovery_analysis.py --dataset ds004504                   # after freezing
  python scripts/04_discovery_analysis.py --dataset ds004504 --dev-unblind-reason "pipeline debugging"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import ROOT, analysis_hash, check_features_match_freeze, is_frozen_and_unchanged, load_config  # noqa: E402
from nh.datasets import get_adapter  # noqa: E402
from nh.labels import open_labels  # noqa: E402
from nh.stats import (assert_one_row_per_subject, design, fdr_bh, group_effect, holm,  # noqa: E402
                      maxT_channels, partial_spearman)

def _safe(fn, *args, **kw):
    try:
        return fn(*args, **kw)
    except ValueError as e:          # e.g. too few subjects with a defined value
        return {"not_estimable": str(e)}


NUISANCE = ["gamma_above_floor", "aperiodic_exponent", "floor_log10", "env_mean", "burst_rate", "alpha_peak_freq"]
EMG = "emg_sentinel__emg_logpow"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="primary")
    ap.add_argument("--dev-unblind-reason", default=None)
    ap.add_argument("--n-perm", type=int, default=None)
    a = ap.parse_args()
    cfg = load_config(); st = cfg["statistics"]
    n_perm = a.n_perm or st["n_perm"]; seed = st["seed"]
    fdir = ROOT / "results" / "features" / a.dataset / a.variant
    if is_frozen_and_unchanged()[0]:
        ok, why = check_features_match_freeze(fdir / "run_meta.json")
        if not ok:
            sys.exit(f"Refusing confirmatory analysis: {why}")
    feats = pd.read_csv(fdir / "features_subject.csv")
    qc = pd.read_csv(fdir / "qc.csv")
    labels = open_labels(get_adapter(a.dataset), purpose="discovery analysis",
                         dev_unblind_reason=a.dev_unblind_reason)
    status = labels.attrs["evidence_status"]
    df = labels.merge(feats, on="subject", how="inner")
    assert_one_row_per_subject(df)
    covars = [c for c in st["covariates"] if c in df and df[c].notna().any()]
    covars += [f"roi__{c}" for c in st.get("feature_covariates", []) if f"roi__{c}" in df]
    P = f"roi__{st['primary_feature']}"
    out = {"evidence_status": status, **analysis_hash(), "dataset": a.dataset, "variant": a.variant,
           "primary_column": P, "n_by_group": df["group"].value_counts().to_dict(),
           "excluded": qc[qc.status != "ok"][["subject", "status", "reason"]].to_dict("records")}
    alpha = st["alpha"]

    # ---------------- H1
    h1 = group_effect(df, P, "group", "AD", "CN", covars, n_perm, st["n_boot"], seed)
    out["H1"] = h1
    gate = h1["p_perm_freedman_lane"] < alpha

    # ---------------- H2
    ad = df[df.group == "AD"]
    h2 = partial_spearman(ad, P, "mmse", covars, n_perm, st["n_boot"], seed)
    h2["tested_confirmatory"] = gate
    out["H2"] = h2
    gate = gate and h2["p_perm"] < alpha

    # ---------------- H3
    nuis = [f"roi__{n}" for n in NUISANCE if f"roi__{n}" in df and f"roi__{n}" not in covars] + ([EMG] if EMG in df else [])
    h3 = group_effect(df, P, "group", "AD", "CN", covars + nuis, n_perm, st["n_boot"], seed)
    d3 = df[df.group.isin(["AD", "CN"])].dropna(subset=[P] + nuis + covars)
    yb = (d3.group == "AD").astype(int).values
    Xb = design(d3, covars + nuis)
    Xf = Xb.assign(**{P: d3[P].values})
    from scipy.stats import chi2
    try:                       # separation / singular nuisance design must not lose H1-H4
        lb = sm.Logit(yb, Xb).fit(disp=0); lf = sm.Logit(yb, Xf).fit(disp=0)
        lr = 2 * (lf.llf - lb.llf)
        h3["logit_LR_test"] = {"LR": float(lr), "df": 1, "p": float(chi2.sf(lr, 1)), "nuisance_terms": nuis}
    except Exception as e:
        h3["logit_LR_test"] = {"error": f"{type(e).__name__}: {e}", "nuisance_terms": nuis}
    h3["tested_confirmatory"] = gate
    out["H3"] = h3
    gate = gate and h3["p_perm_freedman_lane"] < alpha

    # ---------------- H4
    if (df.group == "FTD").sum() >= 3:
        h4a = group_effect(df, P, "group", "AD", "FTD", covars, n_perm, st["n_boot"], seed)
        h4b = group_effect(df, P, "group", "FTD", "CN", covars, n_perm, st["n_boot"], seed)
        adj = holm({"AD-FTD": h4a["p_perm_freedman_lane"], "FTD-CN": h4b["p_perm_freedman_lane"]})
        h4a["p_holm"], h4b["p_holm"] = adj["AD-FTD"], adj["FTD-CN"]
        out["H4"] = {"AD_vs_FTD": h4a, "FTD_vs_CN": h4b, "tested_confirmatory": gate}
    else:
        out["H4"] = {"note": "no FTD group in this cohort"}

    # ---------------- topography (always reported)
    long = pd.read_csv(fdir / "features_long.csv")
    wide = long[long.feature == st["primary_feature"]].pivot(index="subject", columns="channel", values="value")
    chans = [c for c in cfg["common"]["channels"] if c in wide.columns]
    wide = wide.reset_index().merge(df[["subject", "group"] + covars], on="subject")   # 1/f covariate: ROI exponent
    try:                       # a failure here must not lose H1-H4 (all written at the end)
        topo = maxT_channels(wide, chans, "group", "AD", "CN", covars, n_perm, seed)
        out["topography_AD_vs_CN"] = topo.to_dict("records")
        out["topography_n_complete"] = int(wide[wide.group.isin(["AD", "CN"])].dropna(subset=chans).shape[0])
    except Exception as e:
        topo = None
        out["topography_AD_vs_CN"] = {"error": f"{type(e).__name__}: {e}"}

    # ---------------- robustness (always reported, not gated)
    rob = {}
    for name, extra in {"plus_emg": [EMG], "plus_clean_seconds": ["clean_seconds"]}.items():
        ex = [e for e in extra if e in df]
        rob[name] = _safe(group_effect, df, P, "group", "AD", "CN", covars + ex, n_perm // 10, st["n_boot"] // 10, seed)
    for r in ["frontal", "central", "temporal", "parietal", "occipital"]:
        col = f"{r}__{st['primary_feature']}"
        if col in df:            # the region's own 1/f exponent replaces the ROI one
            rc = [c.replace("roi__", f"{r}__") if c.startswith("roi__") and c.replace("roi__", f"{r}__") in df else c
                  for c in covars]
            rob[f"region_{r}"] = _safe(group_effect, df, col, "group", "AD", "CN", rc, n_perm // 10,
                                              st["n_boot"] // 10, seed)
    if f"roi__ib_{st['primary_feature']}" in df:
        rob["individual_band"] = _safe(group_effect, df, f"roi__ib_{st['primary_feature']}", "group", "AD", "CN",
                                              covars, n_perm // 10, st["n_boot"] // 10, seed)
    out["robustness"] = rob

    # ---------------- exploratory: every candidate metric (FDR), labelled EXPLORATORY
    cands = sorted({c for c in df.columns if c.startswith("roi__")})
    rows = []
    for c in cands:
        try:
            r = group_effect(df, c, "group", "AD", "CN", covars, 999, 200, seed)
            rows.append({"feature": c, "g": r["hedges_g_unadj"], "beta": r["beta_adj"], "p": r["p_perm_freedman_lane"]})
        except Exception:
            pass
    ex = pd.DataFrame(rows)
    if len(ex):
        ex["q_fdr"] = fdr_bh(ex.p.values)
    out["exploratory_all_features_AD_vs_CN"] = {"label": "EXPLORATORY - not confirmatory",
                                                "rows": ex.to_dict("records")}

    odir = ROOT / "results" / "analysis" / a.dataset / a.variant
    odir.mkdir(parents=True, exist_ok=True)
    (odir / "discovery_results.json").write_text(json.dumps(out, indent=2, default=float))
    if topo is not None:
        topo.to_csv(odir / "topography_AD_vs_CN.csv", index=False)
    ex.to_csv(odir / "exploratory_features.csv", index=False)
    print(f"[{status}] H1 g={h1['hedges_g_unadj']:.2f} p={h1['p_perm_freedman_lane']:.4f} | "
          f"H2 rho={h2['rho_partial']:.2f} p={h2['p_perm']:.4f} | H3 p={h3['p_perm_freedman_lane']:.4f}")
    print("->", odir)


if __name__ == "__main__":
    main()
