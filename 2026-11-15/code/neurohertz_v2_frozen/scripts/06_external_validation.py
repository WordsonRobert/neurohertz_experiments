"""Stage C: one-shot external validation on a LOCKBOX dataset (CAUEEG, ds007427, BrainLat, hospital).

Order enforced by code:
  1. analysis frozen and unchanged                         (nh.config.is_frozen_and_unchanged)
  2. lockbox features extracted with the frozen pipeline and registered (hashed) AFTER the freeze
  3. only then are the lockbox labels opened (logged LOCKBOX_OPENED; any re-run -> LOCKBOX_REOPENED)
  4. the discovery model is applied UNCHANGED (no refit, no recalibration, no threshold tuning)

Endpoints
  E1  replication of H1: AD > CN on the primary metric, adjusted for age + sex (one-sided, alpha .05)
  E2  discrimination of the frozen discovery model: AUC with DeLong 95% CI
  E3  calibration of the frozen model (intercept, slope) -- descriptive
  E4  (if the cohort has MCI) ordered trend CN < MCI < AD (Jonckheere-type via Spearman on ranks)
  E5  (if MMSE/MoCA) partial Spearman with cognition within patients

Usage
  python scripts/01_extract_features.py --dataset caueeg --register
  python scripts/06_external_validation.py --dataset caueeg --model models/frozen_ds004504_<primary_model>.joblib
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import ROOT, analysis_hash, check_features_match_freeze, load_config  # noqa: E402
from nh.datasets import get_adapter  # noqa: E402
from nh.featuresets import build  # noqa: E402
from nh.labels import open_labels  # noqa: E402
from nh.stats import assert_one_row_per_subject, delong_auc, group_effect, partial_spearman  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--variant", default="primary")
    ap.add_argument("--model", required=True)
    a = ap.parse_args()
    cfg = load_config(); st = cfg["statistics"]
    fpath = ROOT / "results" / "features" / a.dataset / a.variant / "features_subject.csv"
    ad = get_adapter(a.dataset)
    if ad.role != "lockbox":
        sys.exit(f"{a.dataset} is not a lockbox dataset (role={ad.role}).")
    ok, why = check_features_match_freeze(fpath.parent / "run_meta.json")
    if not ok:
        sys.exit(f"Refusing external validation: {why}")
    labels = open_labels(ad, features_path=fpath, purpose="external validation")
    feats = pd.read_csv(fpath)
    df = labels.merge(feats, on="subject")
    assert_one_row_per_subject(df)
    bundle = joblib.load(a.model)
    if bundle["analysis_sha256"] != analysis_hash()["analysis_sha256"]:
        sys.exit("Frozen model was produced by a different analysis version.")
    P = f"roi__{st['primary_feature']}"          # E1 replicates H1 on the pre-specified ROI metric
    long = pd.read_csv(fpath.parent / "features_long.csv")
    df["sex_m"] = (df["sex"].astype(str).str.upper().str[0] == "M").astype(float)
    df, model_cols = build(df, long, bundle["feature_specs"], cfg)
    if model_cols != bundle["features"]:
        sys.exit("Lockbox feature columns do not match the frozen model.")
    covars = [c for c in st["covariates"] if c in df and df[c].notna().any()]
    covars += [f"roi__{c}" for c in st.get("feature_covariates", []) if f"roi__{c}" in df]
    out = {"evidence_status": labels.attrs["evidence_status"], **analysis_hash(), "dataset": a.dataset,
           "n_by_group": df.group.value_counts().to_dict(), "model": a.model}

    e1 = group_effect(df, P, "group", "AD", "CN", covars, st["n_perm"], st["n_boot"], st["seed"])
    t = e1["t_HC3"]
    e1["p_one_sided_AD_gt_CN_param"] = float(e1["p_param"] / 2 if t > 0 else 1 - e1["p_param"] / 2)
    out["E1_replication"] = e1

    d = df[df.group.isin(["AD", "CN"])]
    y = (d.group == "AD").astype(int).values
    m = bundle["model"]                        # imputer/scaler/selection/classifier all frozen from discovery
    from nh.predict import score_positive
    s = score_positive(m, d[model_cols].values.astype(float))
    out["model_name"] = bundle.get("model_name")
    out["E2_frozen_model_auc"] = delong_auc(y, s)
    lo = np.log(np.clip(s, 1e-6, 1 - 1e-6) / (1 - np.clip(s, 1e-6, 1 - 1e-6)))
    cal = sm.Logit(y, sm.add_constant(lo)).fit(disp=0)
    out["E3_calibration"] = {"intercept": float(cal.params[0]), "slope": float(cal.params[1])}

    if "MCI" in set(df.group):
        from scipy.stats import spearmanr
        dd = df[df.group.isin(["CN", "MCI", "AD"])].dropna(subset=[P])
        r, p = spearmanr(dd.group.map({"CN": 0, "MCI": 1, "AD": 2}), dd[P])
        out["E4_ordered_trend"] = {"spearman": float(r), "p": float(p), "n": int(len(dd))}
    pts = df[df.group.isin(["AD", "MCI"])]
    if pts["mmse"].notna().sum() >= 15:
        out["E5_cognition"] = partial_spearman(pts, P, "mmse", covars, st["n_perm"], st["n_boot"], st["seed"])

    odir = ROOT / "results" / "analysis" / a.dataset / a.variant
    odir.mkdir(parents=True, exist_ok=True)
    (odir / "external_validation.json").write_text(json.dumps(out, indent=2, default=float))
    print(json.dumps({k: out[k] for k in ("evidence_status", "E2_frozen_model_auc")}, indent=2, default=float))


if __name__ == "__main__":
    main()
