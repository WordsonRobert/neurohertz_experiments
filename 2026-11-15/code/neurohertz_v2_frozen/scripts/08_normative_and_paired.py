"""N1 normative ageing and the paired-condition analysis (ds006036), per docs/ANALYSIS_PLAN.md §8.

normative:  fit metric ~ age + sex in a HEALTHY normative cohort (e.g. LEMON), then express each
            discovery subject as a deviation z = (observed - predicted) / residual SD. Test whether
            AD deviations exceed CN deviations (i.e. beyond what age predicts). The normative model
            never sees discovery labels; discovery labels open only for the final comparison.
paired:     same people, two conditions (ds004504 eyes-closed vs ds006036 eyes-open, flicker-free stretches only):
            metric ~ group * condition + age + sex + (1 | subject)   [MixedLM]. NOT independent evidence.

Usage
  python scripts/08_normative_and_paired.py normative --norm lemon --target ds004504
  python scripts/08_normative_and_paired.py paired --a ds004504 --b ds006036
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import ROOT, analysis_hash, load_config  # noqa: E402
from nh.datasets import get_adapter  # noqa: E402
from nh.labels import open_labels  # noqa: E402
from nh.stats import group_effect  # noqa: E402


def _feats(ds, variant):
    return pd.read_csv(ROOT / "results" / "features" / ds / variant / "features_subject.csv")


def normative(a, cfg):
    st = cfg["statistics"]; P = f"roi__{st['primary_feature']}"
    norm = open_labels(get_adapter(a.norm), purpose="normative model").merge(_feats(a.norm, a.variant), on="subject")
    norm = norm.dropna(subset=[P, "age"])
    norm["sex"] = norm["sex"].astype(str).str.upper().str[0]
    fit = smf.ols(f"Q('{P}') ~ age + C(sex)", data=norm).fit()
    resid_sd = float(np.std(fit.resid, ddof=fit.df_model + 1))
    tlab = open_labels(get_adapter(a.target), purpose="normative deviation",
                       dev_unblind_reason=a.dev_unblind_reason)
    status = tlab.attrs.get("evidence_status")
    tgt = tlab.merge(_feats(a.target, a.variant), on="subject")
    tgt = tgt.dropna(subset=[P, "age"]).copy()
    tgt["sex"] = tgt["sex"].astype(str).str.upper().str[0]
    tgt["norm_z"] = (tgt[P] - fit.predict(tgt)) / resid_sd
    res = {"evidence_status": status, **analysis_hash(),
           "normative_age_slope": float(fit.params["age"]), "normative_age_p": float(fit.pvalues["age"]),
           "normative_n": int(len(norm)), "resid_sd": resid_sd,
           "AD_vs_CN_on_deviation": group_effect(tgt, "norm_z", "group", "AD", "CN", [], st["n_perm"],
                                                 st["n_boot"], st["seed"])}
    return res, tgt[["subject", "group", "norm_z"]]


def paired(a, cfg):
    st = cfg["statistics"]; P = f"roi__{st['primary_feature']}"
    lab = open_labels(get_adapter(a.a), purpose="paired condition", dev_unblind_reason=a.dev_unblind_reason)
    fa, fb = _feats(a.a, a.variant).assign(condition="A"), _feats(a.b, a.variant).assign(condition="B")
    d = pd.concat([fa, fb]).merge(lab[["subject", "group", "age", "sex"]], on="subject")
    d = d[d.group.isin(["AD", "CN"])].dropna(subset=[P, "age"]).rename(columns={P: "y"})
    m = smf.mixedlm("y ~ C(group, Treatment('CN')) * condition + age + C(sex)", d, groups=d["subject"]).fit()
    return {"evidence_status": lab.attrs.get("evidence_status"), **analysis_hash(),
            "note": "same participants in both conditions: paired evidence, not independent replication",
            "params": m.params.to_dict(), "pvalues": m.pvalues.to_dict(), "n_obs": int(len(d)),
            "n_subjects": int(d.subject.nunique())}, None


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    n = sub.add_parser("normative"); n.add_argument("--norm", required=True); n.add_argument("--target", default="ds004504")
    p = sub.add_parser("paired"); p.add_argument("--a", default="ds004504"); p.add_argument("--b", default="ds006036")
    for x in (n, p):
        x.add_argument("--variant", default="primary"); x.add_argument("--dev-unblind-reason", default=None)
    a = ap.parse_args()
    cfg = load_config()
    res, table = normative(a, cfg) if a.mode == "normative" else paired(a, cfg)
    od = ROOT / "results" / "analysis" / (a.target if a.mode == "normative" else a.a) / a.variant
    od.mkdir(parents=True, exist_ok=True)
    (od / f"{a.mode}_results.json").write_text(json.dumps(res, indent=2, default=float))
    if table is not None:
        table.to_csv(od / "normative_deviation.csv", index=False)
    print(json.dumps({k: v for k, v in res.items() if k in ("evidence_status", "normative_age_slope", "note")},
                     indent=2, default=float))


if __name__ == "__main__":
    main()
