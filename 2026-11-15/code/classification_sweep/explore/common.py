"""Shared loading for the EXPLORATORY classification work (post-freeze; ds004504 labels already opened).
Nothing here is confirmatory: ds004504 has been unblinded. Leads found here must be re-tested on a fresh
cohort (hospital data / ds007427 lockbox) with a new freeze before they can be claimed."""
from __future__ import annotations
import os, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(os.environ.get("NH_FINAL", Path(__file__).resolve().parents[2] / "final_run" / "neurohertz_v2"))
PART = Path(os.environ.get("NH_PARTICIPANTS", ""))

def _participants() -> pd.DataFrame:
    cands = [PART] if PART.is_file() else []
    base = ROOT.parents[1] / "data"
    cands += sorted(base.glob("ds004504*/**/participants.tsv")) if base.exists() else []
    for c in cands:
        if c.is_file() and "006036" not in str(c):
            p = pd.read_csv(c, sep="\t")
            p.columns = [x.strip().replace("\xa0", "") for x in p.columns]
            p = p.rename(columns={"participant_id": "subject", "Group": "group", "Age": "age",
                                  "Gender": "sex", "MMSE": "mmse"})
            p["group"] = p["group"].map({"A": "AD", "C": "CN", "F": "FTD"})
            p["sex_m"] = (p["sex"].astype(str).str.upper() == "M").astype(float)
            return p.set_index("subject")
    raise FileNotFoundError("ds004504 participants.tsv not found; set NH_PARTICIPANTS")

def load(variant: str = "primary") -> pd.DataFrame:
    f = pd.read_csv(ROOT / "results" / "features" / "ds004504" / variant / "features_subject.csv", index_col=0)
    q = pd.read_csv(ROOT / "results" / "features" / "ds004504" / variant / "qc.csv", index_col="subject")
    q = q[[c for c in ["clean_seconds", "epochs_rejected", "emg_hf_logpower_mean"] if c in q]].add_prefix("qc__")
    return _participants().join(f, how="inner").join(q, how="left")

def hedges_g(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    na, nb = len(a), len(b)
    s = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    return (a.mean() - b.mean()) / s * (1 - 3 / (4 * (na + nb) - 9))
