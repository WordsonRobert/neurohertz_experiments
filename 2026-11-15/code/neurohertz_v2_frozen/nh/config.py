"""Configuration loading and content hashing.

The hash of (config file + every .py file in nh/) identifies one exact analysis.
Freezing records that hash; the lockbox refuses to open if the current hash differs.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "pipeline.yaml"
FREEZE_PATH = ROOT / "registry" / "freeze.json"


def load_config(path: Path | str = CONFIG_PATH) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path | str) -> str:
    return _sha256_bytes(Path(path).read_bytes())


def code_hash() -> str:
    """Hash of all analysis code (nh/*.py and scripts/*.py)."""
    h = hashlib.sha256()
    for p in sorted(list((ROOT / "nh").glob("*.py")) + list((ROOT / "scripts").glob("*.py"))):
        h.update(str(p.relative_to(ROOT)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()


STAGE_A_CODE = ["nh/preprocess.py", "nh/spectral.py", "nh/gamma.py", "nh/surrogates.py",
                "nh/dynamics.py", "nh/oscfit.py", "nh/datasets.py", "scripts/01_extract_features.py"]


def apply_overrides(cfg: dict, overrides: list[str] | None) -> dict:
    """'a.b.c=value' strings (value parsed as YAML) applied to a copy of cfg. Used for ablation
    variants; the overrides are recorded and enter the extraction hash."""
    import copy
    cfg = copy.deepcopy(cfg)
    for o in overrides or []:
        key, val = o.split("=", 1)
        node = cfg
        parts = key.split(".")
        for k in parts[:-1]:
            node = node.setdefault(k, {})
        node[parts[-1]] = yaml.safe_load(val)
    return cfg


def extraction_hash(config_path: Path | str = CONFIG_PATH, cfg: dict | None = None) -> str:
    """Hash of everything that determines per-subject features (config sections + Stage-A code).
    Changing the statistics section or `status` does NOT change it, so freezing does not force
    re-extraction, but any change to preprocessing/feature code or parameters does."""
    cfg = cfg if cfg is not None else load_config(config_path)
    h = hashlib.sha256()
    h.update(json.dumps({k: cfg[k] for k in ("common", "preprocessing", "features")}, sort_keys=True).encode())
    for rel in STAGE_A_CODE:
        h.update(rel.encode()); h.update((ROOT / rel).read_bytes())
    return h.hexdigest()


def check_features_match_freeze(run_meta_path: Path | str) -> tuple[bool, str]:
    """True if the feature table was produced by the frozen extraction pipeline."""
    fr = read_freeze()
    meta = json.loads(Path(run_meta_path).read_text())
    if fr is None:
        return False, "not frozen"
    if meta.get("extraction_sha256") != fr.get("extraction_sha256"):
        return False, (f"features were extracted with extraction hash {str(meta.get('extraction_sha256'))[:12]}, "
                       f"frozen pipeline is {fr['extraction_sha256'][:12]}: re-run 01_extract_features.py")
    return True, "ok"


def analysis_hash(config_path: Path | str = CONFIG_PATH) -> dict:
    cfg_h = sha256_file(config_path)
    c_h = code_hash()
    return {"config_sha256": cfg_h, "code_sha256": c_h,
            "analysis_sha256": _sha256_bytes((cfg_h + c_h).encode())}


def read_freeze() -> dict | None:
    if FREEZE_PATH.exists():
        return json.loads(FREEZE_PATH.read_text())
    return None


def is_frozen_and_unchanged(config_path: Path | str = CONFIG_PATH) -> tuple[bool, str]:
    cfg = load_config(config_path)
    fr = read_freeze()
    if cfg.get("status") != "frozen":
        return False, "config status is not 'frozen'"
    if fr is None:
        return False, "registry/freeze.json missing (run scripts/03_freeze.py)"
    now = analysis_hash(config_path)
    if now["analysis_sha256"] != fr["analysis_sha256"]:
        return False, ("config or code changed after freezing "
                       f"(frozen {fr['analysis_sha256'][:12]}, now {now['analysis_sha256'][:12]})")
    return True, fr["analysis_sha256"]
