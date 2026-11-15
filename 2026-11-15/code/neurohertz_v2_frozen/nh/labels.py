"""The ONLY module allowed to read diagnostic labels or clinical scores.

Feature-extraction code (nh/preprocess.py, nh/spectral.py, nh/gamma.py, nh/surrogates.py,
scripts/01_extract_features.py) must never import this module; tests/test_leakage.py enforces it.

Gates
-----
role == "discovery"  : labels open only if the analysis is frozen, OR the caller passes
                       dev_unblind_reason=... . A dev unblinding is logged and every result
                       produced afterwards must be labelled EXPLORATORY.
role == "lockbox"    : labels open only if (1) the analysis is frozen and unchanged,
                       (2) the feature table was registered (hashed) AFTER the freeze, and
                       (3) the feature table passed in is byte-identical to the registered one.
                       First opening is logged as LOCKBOX_OPENED; any re-opening is logged as
                       LOCKBOX_REOPENED and must be disclosed in the paper.
role in {"reliability", "normative", "paired"} : demographic/clinical columns open, logged.
role == "synthetic"  : generated dry-run data (scripts/00_make_synthetic_dataset.py); open, not logged,
                       every output stamped SYNTHETIC.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import is_frozen_and_unchanged, read_freeze, sha256_file
from .ledger import log_event, read_events

STANDARD_COLUMNS = ["subject", "group", "age", "sex", "mmse", "education"]


class LabelAccessError(RuntimeError):
    pass


def register_features(dataset: str, features_path: Path | str) -> str:
    """Hash a feature table BEFORE any labels of that dataset are opened."""
    sha = sha256_file(features_path)
    log_event("FEATURES_REGISTERED", dataset=dataset, features_sha256=sha,
              features_path=str(features_path))
    return sha


def _check_lockbox(dataset: str, features_path: Path | str) -> None:
    ok, msg = is_frozen_and_unchanged()
    if not ok:
        raise LabelAccessError(f"LOCKBOX '{dataset}' refused: {msg}")
    frozen_at = read_freeze()["utc"]
    sha = sha256_file(features_path)
    regs = [r for r in read_events("FEATURES_REGISTERED", dataset=dataset)
            if r["features_sha256"] == sha and r["utc"] >= frozen_at]
    if not regs:
        raise LabelAccessError(
            f"LOCKBOX '{dataset}' refused: feature table {Path(features_path).name} "
            "was not registered after the freeze (run scripts/01_extract_features.py --register).")


def open_labels(adapter, *, features_path: Path | str | None = None,
                purpose: str, dev_unblind_reason: str | None = None) -> pd.DataFrame:
    role = adapter.role
    ds = adapter.name
    status = "CONFIRMATORY"
    if role == "discovery":
        ok, msg = is_frozen_and_unchanged()
        if not ok:
            if not dev_unblind_reason:
                raise LabelAccessError(
                    f"Discovery labels for '{ds}' are blinded during development ({msg}). "
                    "Freeze the analysis, or pass dev_unblind_reason='...' (logged; results become EXPLORATORY).")
            status = "EXPLORATORY"
            log_event("DISCOVERY_DEV_UNBLINDED", dataset=ds, purpose=purpose, reason=dev_unblind_reason)
        else:
            log_event("DISCOVERY_LABELS_OPENED", dataset=ds, purpose=purpose)
    elif role == "lockbox":
        if features_path is None:
            raise LabelAccessError("Lockbox labels require the registered feature table path.")
        _check_lockbox(ds, features_path)
        prior = read_events("LOCKBOX_OPENED", dataset=ds)
        log_event("LOCKBOX_REOPENED" if prior else "LOCKBOX_OPENED", dataset=ds, purpose=purpose,
                  features_sha256=sha256_file(features_path))
        if prior:
            status = "CONFIRMATORY_REOPENED"
    elif role == "synthetic":
        status = "SYNTHETIC"                    # pipeline dry run on generated data: nothing to blind, nothing logged
    else:
        log_event("LABELS_OPENED", dataset=ds, role=role, purpose=purpose)

    df = adapter.read_participants()
    missing = [c for c in ["subject", "group"] if c not in df.columns]
    if missing:
        raise ValueError(f"{ds}: participants table lacks {missing}")
    for c in STANDARD_COLUMNS:
        if c not in df.columns:
            df[c] = pd.NA
    df = df[STANDARD_COLUMNS + [c for c in df.columns if c not in STANDARD_COLUMNS]].copy()
    df.attrs["evidence_status"] = status
    return df
