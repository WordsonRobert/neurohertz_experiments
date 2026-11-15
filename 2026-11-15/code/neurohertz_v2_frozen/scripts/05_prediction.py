"""Stage B (secondary): leakage-safe multi-feature prediction on the discovery cohort.

For every model in config prediction.models (feature lists fixed before unblinding):
  P1  AD vs CN: repeated nested-CV AUC (impute -> scale -> [select k in-fold] -> logistic regression),
      full-pipeline permutation p (PRIMARY model: n_perm_pipeline; others: n_perm_secondary),
      how often each electrode/feature was selected across outer folds, and the final model's
      standardised coefficients (which electrodes carry the weight).
  P2  incremental value: base [age, sex, conventional spectra] vs base + model features (same splits)
  P3  MMSE within AD: nested ridge regression R^2, base vs base + model features (descriptive, n=36)
  P4  (only when frozen) the PRIMARY model is fitted on all AD+CN subjects -> models/ for the lockbox
Multiplicity: only prediction.primary_model is confirmatory; the others are reported as secondary.

Usage
  python scripts/05_prediction.py --dataset ds004504 [--models M1_roi_single M2_posterior_electrodes]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import (ROOT, analysis_hash, check_features_match_freeze, is_frozen_and_unchanged,  # noqa: E402
                       load_config, sha256_file)
from nh.datasets import get_adapter  # noqa: E402
from nh.featuresets import build  # noqa: E402
from nh.labels import open_labels  # noqa: E402
from nh.ledger import log_event  # noqa: E402
from nh.predict import (fit_frozen_model, incremental_auc, nested_cv_auc, nested_cv_r2,  # noqa: E402
                        permutation_test_pipeline, standardized_coefficients)
from nh.stats import assert_one_row_per_subject  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="primary")
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--dev-unblind-reason", default=None)
    ap.add_argument("--n-perm", type=int, default=None, help="override permutations (quick checks only)")
    ap.add_argument("--n-repeats", type=int, default=None, help="override outer repeats (quick checks only)")
    ap.add_argument("--jobs", type=int, default=1, help="parallel permutations (results identical to --jobs 1)")
    a = ap.parse_args()
    cfg = load_config(); pc = cfg["prediction"]
    pc["n_jobs"] = a.jobs
    if a.n_repeats:
        pc["outer"]["n_repeats"] = a.n_repeats
    fdir = ROOT / "results" / "features" / a.dataset / a.variant
    if is_frozen_and_unchanged()[0]:
        ok, why = check_features_match_freeze(fdir / "run_meta.json")
        if not ok:
            sys.exit(f"Refusing confirmatory analysis: {why}")
    feats = pd.read_csv(fdir / "features_subject.csv")
    long = pd.read_csv(fdir / "features_long.csv")
    labels = open_labels(get_adapter(a.dataset), purpose="discovery prediction",
                         dev_unblind_reason=a.dev_unblind_reason)
    status = labels.attrs["evidence_status"]
    df = labels.merge(feats, on="subject")
    df["sex_m"] = (df["sex"].astype(str).str.upper().str[0] == "M").astype(float)
    assert_one_row_per_subject(df)
    d = df[df.group.isin(["AD", "CN"])].copy()
    d, base_cols = build(d, long, pc["base_features"], cfg)
    d = d.dropna(subset=["age"])
    y = (d.group == "AD").astype(int).values
    models = a.models or list(pc["models"])
    primary = pc["primary_model"]
    out = {"evidence_status": status, **analysis_hash(), "n_AD": int(y.sum()), "n_CN": int((1 - y).sum()),
           "primary_model": primary, "models": {}}

    for name in models:
        spec = pc["models"][name]
        dm, cols = build(d, long, spec["features"], cfg)
        X = dm[cols].values.astype(float)
        kw = {k: spec[k] for k in ("select_k", "penalty", "classifier") if k in spec}
        n_perm = a.n_perm or spec.get("n_perm") or (pc["n_perm_pipeline"] if name == primary else pc["n_perm_secondary"])
        res = {"role": "PRIMARY" if name == primary else "secondary", "features": cols,
               "missing_fraction": float(np.isnan(X).mean())}
        cv = nested_cv_auc(X, y, pc, model_kw=kw, feature_names=cols)
        cv.pop("oof_mean_score")
        res["P1_cv"] = cv
        res["P1_permutation"] = permutation_test_pipeline(X, y, pc, n_perm=n_perm, model_kw=kw)
        res["final_model"] = standardized_coefficients(fit_frozen_model(X, y, pc, model_kw=kw), cols)
        res["P2_incremental"] = incremental_auc(dm, y, base_cols, [c for c in cols if c not in base_cols], pc)
        ad = dm[dm.group == "AD"].dropna(subset=["mmse"])
        if len(ad) >= 20:
            res["P3_mmse_within_AD"] = {
                "warning": "small n and coarse MMSE; descriptive only",
                "base": nested_cv_r2(ad[base_cols].values.astype(float), ad["mmse"].values.astype(float), pc),
                "base_plus_model": nested_cv_r2(ad[base_cols + cols].values.astype(float),
                                                ad["mmse"].values.astype(float), pc,
                                                select_k=spec.get("select_k"))}
        out["models"][name] = res
        print(f"[{status}] {name:28s} AUC={cv['auc_mean_over_repeats']:.3f} "
              f"perm p={res['P1_permutation']['p_perm']:.4f} dAUC={res['P2_incremental']['delta_auc_mean']:+.3f}")

    frozen, _ = is_frozen_and_unchanged()
    if frozen and primary in models:
        spec = pc["models"][primary]
        dm, cols = build(d, long, spec["features"], cfg)
        kw = {k: spec[k] for k in ("select_k", "penalty", "classifier") if k in spec}
        model = fit_frozen_model(dm[cols].values.astype(float), y, pc, model_kw=kw)
        mdir = ROOT / "models"; mdir.mkdir(exist_ok=True)
        mp = mdir / f"frozen_{a.dataset}_{primary}.joblib"
        joblib.dump({"model": model, "model_name": primary, "feature_specs": spec["features"], "features": cols,
                     "trained_on": a.dataset, "features_sha256": sha256_file(fdir / "features_subject.csv"),
                     **analysis_hash()}, mp)
        log_event("FROZEN_MODEL_SAVED", dataset=a.dataset, model=primary, model_sha256=sha256_file(mp))
        out["P4_frozen_model"] = str(mp)

    odir = ROOT / "results" / "analysis" / a.dataset / a.variant
    odir.mkdir(parents=True, exist_ok=True)
    (odir / "prediction_results.json").write_text(json.dumps(out, indent=2, default=float))
    rows = [{"model": n, "role": r["role"], "n_features": len(r["features"]),
             "auc": r["P1_cv"]["auc_mean_over_repeats"], "perm_p": r["P1_permutation"]["p_perm"],
             "delta_auc_vs_base": r["P2_incremental"]["delta_auc_mean"]} for n, r in out["models"].items()]
    pd.DataFrame(rows).to_csv(odir / "prediction_summary.csv", index=False)
    print("->", odir)


if __name__ == "__main__":
    main()
