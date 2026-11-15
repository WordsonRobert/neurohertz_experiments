"""Ceiling check: how much accuracy, if any, does the interpretable model give up?

Runs, on the SAME repeated outer splits as the primary model:
  * the primary interpretable model (prediction.primary_model)
  * TabPFN on the same features (black-box tabular model for small data; optional dependency)
  * Riemannian tangent-space + logistic regression on the 19x19 gamma-band covariance matrices
    saved by Stage A (pyriemann; an EEG-native black-box benchmark)
These two are NEVER the reported model. If they beat the interpretable model by less than the CV
error bar, that is evidence the interpretable model leaves nothing important on the table.

Usage
  python scripts/09_ceiling_check.py --dataset ds004504 [--dev-unblind-reason "..."]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import ROOT, analysis_hash, load_config  # noqa: E402
from nh.datasets import get_adapter  # noqa: E402
from nh.featuresets import build  # noqa: E402
from nh.labels import open_labels  # noqa: E402
from nh.predict import classifier, score_positive  # noqa: E402


def cv_auc(make_model, X, y, pc, n_rep):
    outer = RepeatedStratifiedKFold(n_splits=pc["outer"]["n_splits"], n_repeats=n_rep, random_state=pc["seed"])
    k = pc["outer"]["n_splits"]
    oof = np.full((n_rep, len(y)), np.nan)
    for i, (tr, te) in enumerate(outer.split(X, y)):
        m = make_model().fit(X[tr], y[tr])
        oof[i // k, te] = score_positive(m, X[te])
    per = np.array([roc_auc_score(y, oof[r]) for r in range(n_rep)])
    return {"auc_mean": float(per.mean()), "auc_2.5_97.5": [float(np.percentile(per, 2.5)), float(np.percentile(per, 97.5))]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="primary")
    ap.add_argument("--dev-unblind-reason", default=None)
    ap.add_argument("--n-repeats", type=int, default=20)
    a = ap.parse_args()
    cfg = load_config(); pc = cfg["prediction"]
    fdir = ROOT / "results" / "features" / a.dataset / a.variant
    feats = pd.read_csv(fdir / "features_subject.csv"); long = pd.read_csv(fdir / "features_long.csv")
    labels = open_labels(get_adapter(a.dataset), purpose="ceiling check", dev_unblind_reason=a.dev_unblind_reason)
    d = labels[labels.group.isin(["AD", "CN"])].merge(feats, on="subject")
    spec = pc["models"][pc["primary_model"]]
    d, cols = build(d, long, spec["features"], cfg)
    y = (d.group == "AD").astype(int).values
    X = d[cols].values.astype(float)
    out = {"evidence_status": labels.attrs["evidence_status"], **analysis_hash(), "features": cols, "results": {}}
    out["results"]["interpretable_primary"] = cv_auc(lambda: clone(classifier(pc["C_grid"], pc["inner"]["n_splits"], pc["seed"])),
                                                     X, y, pc, a.n_repeats)
    try:
        from tabpfn import TabPFNClassifier
        from sklearn.impute import SimpleImputer
        out["results"]["tabpfn_ceiling"] = cv_auc(lambda: make_pipeline(SimpleImputer(strategy="median"), TabPFNClassifier()),
                                                  X, y, pc, a.n_repeats)
    except Exception as e:
        out["results"]["tabpfn_ceiling"] = {"skipped": f"{type(e).__name__}: {e}"}
    try:
        from pyriemann.estimation import Shrinkage
        from pyriemann.tangentspace import TangentSpace
        covs = []
        for s in d.subject:
            rec = json.loads((fdir / "per_subject" / f"{s}.json").read_text())
            C = np.asarray(rec["cov_gamma"], float)
            covs.append(C)
        C = np.stack(covs)
        out["results"]["riemann_ceiling"] = cv_auc(
            lambda: make_pipeline(Shrinkage(shrinkage=0.1), TangentSpace(metric="riemann"),
                                  LogisticRegression(C=1.0, class_weight="balanced", max_iter=5000)),
            C, y, pc, a.n_repeats)
    except Exception as e:
        out["results"]["riemann_ceiling"] = {"skipped": f"{type(e).__name__}: {e}"}
    odir = ROOT / "results" / "analysis" / a.dataset / a.variant
    odir.mkdir(parents=True, exist_ok=True)
    (odir / "ceiling_check.json").write_text(json.dumps(out, indent=2, default=float))
    print(json.dumps(out["results"], indent=2, default=float))


if __name__ == "__main__":
    main()
