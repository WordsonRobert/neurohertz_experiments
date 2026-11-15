"""Freeze the analysis: hash config + code + analysis plan + simulation-based metric selection.

Preconditions (all checked):
  1. config/pipeline.yaml has `status: frozen`
  2. results/simulation/metric_selection.json exists (scripts/02_simulation_validation.py)
  3. statistics.primary_feature equals the simulation-selected metric, OR --override-reason is given
     (the override and its reason are written into the freeze record and must be reported)
  4. docs/ANALYSIS_PLAN.md exists (its hash is recorded -> any later edit is detectable)

After this, discovery labels can be opened without the EXPLORATORY flag, and lockbox datasets can
be opened once each, provided their features are extracted + registered after this timestamp.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import FREEZE_PATH, ROOT, analysis_hash, extraction_hash, load_config, sha256_file  # noqa: E402
from nh.ledger import log_event, read_events  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--override-reason", default=None)
    a = ap.parse_args()
    cfg = load_config()
    if cfg.get("status") != "frozen":
        sys.exit("Set `status: frozen` in config/pipeline.yaml first.")
    sel_p = ROOT / "results" / "simulation" / "metric_selection.json"
    if not sel_p.exists():
        sys.exit("Run scripts/02_simulation_validation.py first.")
    sel = json.loads(sel_p.read_text())
    primary = cfg["statistics"]["primary_feature"]
    if primary != sel["primary_metric"] and not a.override_reason:
        sys.exit(f"primary_feature '{primary}' != simulation-selected '{sel['primary_metric']}'. "
                 "Change the config or pass --override-reason.")
    plan = ROOT / "docs" / "ANALYSIS_PLAN.md"
    if FREEZE_PATH.exists():
        sys.exit("Already frozen. A second freeze must be a new, disclosed version (move the old record).")
    prior_unblind = read_events("DISCOVERY_DEV_UNBLINDED")
    # mechanistic fingerprints (13_mechanism_fingerprints.py): frozen with everything else, or the
    # mechanism analyses stay EXPLORATORY. A --quick run can never be frozen.
    fp_p = ROOT / "results" / "mechanism" / "fingerprints.json"
    fp_sha = None
    if fp_p.exists():
        if json.loads(fp_p.read_text()).get("quick"):
            sys.exit("results/mechanism/fingerprints.json comes from a --quick run. Re-run 13 without --quick.")
        fp_sha = sha256_file(fp_p)
    else:
        print("WARNING: no mechanism fingerprints; 14_mechanism_tests.py will be EXPLORATORY.")
    method_sel = ROOT / "registry" / "method_selection.json"
    rec = {"utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           **analysis_hash(), "extraction_sha256": extraction_hash(),
           "analysis_plan_sha256": sha256_file(plan),
           "metric_selection_sha256": sha256_file(sel_p),
           "primary_feature": primary, "simulation_selected": sel["primary_metric"],
           "override_reason": a.override_reason,
           "mechanism_fingerprints_sha256": fp_sha,
           "method_selection_sha256": sha256_file(method_sel) if method_sel.exists() else None,
           "discovery_dev_unblindings_before_freeze": len(prior_unblind)}
    FREEZE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FREEZE_PATH.write_text(json.dumps(rec, indent=2))
    log_event("FROZEN", **{k: v for k, v in rec.items() if k not in ("config_sha256", "code_sha256", "analysis_sha256")})
    print(json.dumps(rec, indent=2))
    if prior_unblind:
        print(f"\nNOTE: discovery labels were opened {len(prior_unblind)}x during development. "
              "Discovery results are therefore NOT blind; say so in the paper. Lockbox datasets remain blind.")


if __name__ == "__main__":
    main()
