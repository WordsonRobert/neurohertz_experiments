"""Turn a pre-specified feature-set definition into a subject x feature matrix.

Feature spec strings (written in config/pipeline.yaml -> prediction.models):
  "roi:<feature>"            mean over the pre-specified posterior ROI
  "region:<name>:<feature>"  mean over a region (frontal / central / temporal / parietal / occipital)
  "ch:<channel>:<feature>"   one electrode
  "allch:<feature>"          all 19 electrodes as separate columns (used with in-fold selection)
  "emg:<feature>"            EMG-sentinel channel mean (QC covariate)
  "cov:<column>"             a participant column (age, sex_m, education)
"{primary}" inside a spec is replaced by statistics.primary_feature.

Building the matrix uses only Stage-A outputs (label-free) plus covariates. Nothing is chosen
here from the data: which electrodes/features enter a model is fixed in the config, and any
data-driven selection (select_k) happens INSIDE the CV pipeline on training folds only.
"""
from __future__ import annotations

import pandas as pd


def expand(specs: list[str], cfg: dict) -> list[str]:
    prim = cfg["statistics"]["primary_feature"]
    out = []
    for s in specs:
        s = s.replace("{primary}", prim)
        if s.startswith("allch:"):
            f = s.split(":", 1)[1]
            out += [f"ch:{c}:{f}" for c in cfg["common"]["channels"]]
        else:
            out.append(s)
    return out


def column_name(spec: str) -> str:
    kind, *rest = spec.split(":")
    if kind == "roi": return f"roi__{rest[0]}"
    if kind == "region": return f"{rest[0]}__{rest[1]}"
    if kind == "emg": return f"emg_sentinel__{rest[0]}"
    if kind == "ch": return f"ch__{rest[0]}__{rest[1]}"
    if kind == "cov": return rest[0]
    raise ValueError(f"bad feature spec {spec}")


def build(subject_df: pd.DataFrame, long_df: pd.DataFrame | None, specs: list[str], cfg: dict) -> tuple[pd.DataFrame, list[str]]:
    """Returns (df with the requested columns added, resolved column names)."""
    specs = expand(specs, cfg)
    df = subject_df.copy()
    ch_specs = [s for s in specs if s.startswith("ch:")]
    if ch_specs:
        if long_df is None:
            raise ValueError("channel-level specs need features_long.csv")
        need = {(s.split(":")[1], s.split(":")[2]) for s in ch_specs}
        feats = {f for _, f in need}
        sub = long_df[long_df.feature.isin(feats)]
        wide = sub.pivot_table(index="subject", columns=["channel", "feature"], values="value", aggfunc="first")
        wide.columns = [f"ch__{c}__{f}" for c, f in wide.columns]
        keep = [f"ch__{c}__{f}" for c, f in need if f"ch__{c}__{f}" in wide.columns]
        df = df.merge(wide[keep].reset_index(), on="subject", how="left")
    cols = [column_name(s) for s in specs]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"feature columns not found: {missing[:6]}")
    return df, cols
