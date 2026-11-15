"""Test-retest reliability (healthy test-retest cohort, e.g. ds004148) and split-half reliability.

Two analyses, neither needs diagnostic labels:
  R1  between-session ICC(2,1) of every ROI feature (subject IDs encode session: '<sub>_ses-<k>')
  R2  within-recording split-half: re-extract the primary metric on the first vs second half of
      each subject's clean data (any dataset, including ds004504) -> ICC(2,1) and Spearman-Brown

Usage
  python scripts/07_reliability.py --dataset ds004148
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import ROOT, analysis_hash  # noqa: E402
from nh.stats import icc_2_1  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--variant", default="primary")
    ap.add_argument("--session-sep", default="_ses-")
    ap.add_argument("--retest", default=None,
                    help="second dataset with the SAME subject IDs (e.g. ds006036): between-session ICC per ROI feature")
    a = ap.parse_args()
    f = pd.read_csv(ROOT / "results" / "features" / a.dataset / a.variant / "features_subject.csv")
    odir = ROOT / "results" / "analysis" / a.dataset / a.variant
    odir.mkdir(parents=True, exist_ok=True)

    # R3 between-session reliability across two datasets of the same people (label-free)
    if a.retest:
        g = pd.read_csv(ROOT / "results" / "features" / a.retest / a.variant / "features_subject.csv")
        both = f.merge(g, on="subject", suffixes=("__s1", "__s2"))
        rows = []
        for col in [c for c in f.columns if c.startswith("roi__") and "__sh" not in c and c in g.columns]:
            M = both[[f"{col}__s1", f"{col}__s2"]].dropna().values
            if len(M) >= 10:
                rows.append({"feature": col[5:], "n": len(M), "icc_2_1_between_sessions": icc_2_1(M)})
        r3 = pd.DataFrame(rows, columns=["feature", "n", "icc_2_1_between_sessions"]).sort_values(
            "icc_2_1_between_sessions", ascending=False)
        r3.to_csv(odir / f"retest_icc_vs_{a.retest}.csv", index=False)
        from nh.config import load_config
        prim = load_config()["statistics"]["primary_feature"]
        hit = r3[r3.feature == prim]
        print(f"Between-session ICC ({a.dataset} vs {a.retest}, {len(both)} shared subjects); primary "
              f"{prim}: " + (f"{hit.icc_2_1_between_sessions.iloc[0]:.2f} (n={hit.n.iloc[0]})" if len(hit) else "n/a"))
        print(r3.head(25).to_string(index=False))

    # R2 split-half (requires 01_extract_features.py --split-half)
    sh = [c[len("roi__sh1_"):] for c in f.columns if c.startswith("roi__sh1_")]
    if sh:
        rows = []
        for m in sh:
            M = f[[f"roi__sh1_{m}", f"roi__sh2_{m}"]].dropna().values
            if len(M) >= 10:
                icc = icc_2_1(M)
                rows.append({"metric": m, "n": len(M), "icc_2_1_half": icc,
                             "spearman_brown_full": 2 * icc / (1 + icc)})
        if not rows:
            print("Split-half reliability: fewer than 10 subjects with both halves -> skipped")
            rows = [{"metric": None, "n": 0, "icc_2_1_half": float("nan"), "spearman_brown_full": float("nan")}]
        r2 = pd.DataFrame(rows).sort_values("icc_2_1_half", ascending=False)
        r2.to_csv(odir / "split_half_icc.csv", index=False)
        print("Split-half reliability:\n", r2.to_string(index=False))
    if a.session_sep not in "".join(f["subject"].astype(str)):
        return
    sp = f["subject"].str.split(a.session_sep, n=1, expand=True)
    if sp.shape[1] < 2:
        sys.exit("subject IDs carry no session suffix; configure subject_regex to capture '<sub>_ses-<k>'.")
    f["sub"], f["ses"] = sp[0], sp[1]
    rows = []
    for col in [c for c in f.columns if c.startswith("roi__")]:
        M = f.pivot(index="sub", columns="ses", values=col).dropna()
        if len(M) >= 10 and M.shape[1] >= 2:
            rows.append({"feature": col, "n": len(M), "icc_2_1": icc_2_1(M.values)})
    res = pd.DataFrame(rows).sort_values("icc_2_1", ascending=False)
    res.to_csv(odir / "test_retest_icc.csv", index=False)
    (odir / "reliability_meta.json").write_text(json.dumps(analysis_hash(), indent=2))
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
