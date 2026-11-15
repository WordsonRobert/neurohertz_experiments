"""Shared helpers for the classification sweep (EXPLORATORY; see docs/HYPOTHESIS_TREE.md).

Layout on the laptop:
    neurohertz2/final_run/neurohertz_v2/   frozen code + results (never modified from here)
    neurohertz2/classification/            this folder
The frozen preprocessing (nh.preprocess) is imported read-only from the final_run folder, so cleaned data are
exactly the data the confirmatory analysis used. Override paths with NH_CODE / NH_CLASS_OUT.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
CLS = HERE.parent
CODE = Path(os.environ.get("NH_CODE", CLS.parent / "final_run" / "neurohertz_v2"))
OUT = Path(os.environ.get("NH_CLASS_OUT", CLS / "results"))
CACHE = Path(os.environ.get("NH_CLASS_CACHE", CLS / "cache"))
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

# 10-20 regions (Fp separated: frontal-polar sites carry ocular/saccadic potentials)
REGION = {"Fp1": "fp", "Fp2": "fp", "F7": "frontal", "F3": "frontal", "Fz": "frontal", "F4": "frontal",
          "F8": "frontal", "T3": "temporal", "T4": "temporal", "T5": "temporal", "T6": "temporal",
          "C3": "central", "Cz": "central", "C4": "central", "P3": "parietal", "Pz": "parietal",
          "P4": "parietal", "O1": "occipital", "O2": "occipital"}
REGIONS = ["fp", "frontal", "temporal", "central", "parietal", "occipital"]
ROI = ["P3", "Pz", "P4", "O1", "O2"]          # the pre-registered posterior ROI
EPOCH_S = 2.0
LINE_EXCL = (47.5, 52.5)                       # 50 Hz notch region, never analysed
FMAX_ANALYSIS = 47.5


def variant_dir(dataset: str, variant: str) -> Path:
    return CACHE / dataset / variant


def save_npz(path: Path, **arrs):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.npz")
    np.savez_compressed(tmp, **arrs)
    os.replace(tmp, path)


def load_clean(path: Path) -> dict:
    z = np.load(path, allow_pickle=False)
    d = {k: z[k] for k in z.files}
    d["ch_names"] = [str(c) for c in d["ch_names"]]
    d["qc"] = json.loads(str(d["qc"]))
    return d


def csd_transform(data_uv: np.ndarray, ch_names: list[str], sfreq: float) -> np.ndarray:
    """Spherical-spline CSD (MNE defaults, identical to the frozen pipeline's reference='csd').
    Linear and purely spatial, so applying it to the concatenated clean epochs equals applying it per epoch."""
    import mne
    info = mne.create_info(ch_names, sfreq, "eeg")
    raw = mne.io.RawArray(data_uv * 1e-6, info, verbose="ERROR")
    raw.set_montage("standard_1020", on_missing="ignore", verbose="ERROR")
    raw.set_eeg_reference("average", projection=False, verbose="ERROR")
    raw = mne.preprocessing.compute_current_source_density(raw, verbose="ERROR")
    return raw.get_data()


def participants(dataset: str = "ds004504"):
    """Labels for EXPLORATORY analysis (ds004504 was unblinded at the 2026-11-14 freeze).
    Lockbox datasets are refused: they must go through nh.labels.open_labels after a new freeze."""
    import pandas as pd
    if dataset not in ("ds004504", "synthetic"):
        raise PermissionError(f"{dataset}: labels may only be opened through nh.labels after a new freeze")
    env = os.environ.get("NH_PARTICIPANTS")
    cands = [Path(env)] if env else []
    if dataset == "synthetic":                       # positive-control data with a KNOWN injected mechanism
        cands = [Path(os.environ.get("NH_SYNTH", CACHE / "synth_dataset")) / "participants.tsv"]
    cands += sorted((CLS.parent / "data").glob("ds004504*/**/participants.tsv"))
    for c in cands:
        if c.is_file() and "006036" not in str(c):
            p = pd.read_csv(c, sep="\t")
            p.columns = [x.strip().replace("\xa0", "") for x in p.columns]
            p = p.rename(columns={"participant_id": "subject", "Group": "group", "Age": "age",
                                  "Gender": "sex", "MMSE": "mmse"})
            p["group"] = p["group"].map({"A": "AD", "C": "CN", "F": "FTD"}).fillna(p["group"])
            p["sex_m"] = (p["sex"].astype(str).str.upper() == "M").astype(float)
            return p.set_index("subject")
    raise FileNotFoundError("participants.tsv for ds004504 not found (set NH_PARTICIPANTS)")


def jsonable(o):
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.integer): return int(o)
    if isinstance(o, np.ndarray): return o.tolist()
    return str(o)
