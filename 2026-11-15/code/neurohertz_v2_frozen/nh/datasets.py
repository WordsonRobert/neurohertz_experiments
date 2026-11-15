"""Dataset adapters: find recordings and load them as MNE Raw objects.

Adapters know where files are. They do NOT read diagnostic labels for feature extraction;
`read_participants()` exists only so that nh/labels.py (the gatekeeper) can call it.
"""
from __future__ import annotations

import glob
import os
import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path

import mne
import numpy as np
import pandas as pd
import yaml

from .config import ROOT

DATASETS_PATH = ROOT / "config" / "datasets.yaml"
# Google Drive mount point on Colab; override with `export NH_DRIVE=/path` anywhere else.
os.environ.setdefault("NH_DRIVE", "/content/drive/MyDrive")


def expand_roots(roots: list[str]) -> list[str]:
    """Expand ${ENV} variables, ~ and wildcards; keep only folders that exist (order preserved)."""
    out = []
    for r in roots or []:
        r = os.path.expanduser(os.path.expandvars(str(r)))
        if not os.path.isabs(r) and "$" not in r:
            r = str(ROOT / r)                       # relative roots are relative to the repository
        hits = sorted(glob.glob(r)) if any(c in r for c in "*?[") else [r]
        for h in hits:
            if Path(h).is_dir() and h not in out:
                out.append(h)
    return out


@dataclass
class Adapter:
    name: str
    role: str
    roots: list[str]
    file_glob: str
    subject_regex: str
    participants_glob: str
    column_map: dict = field(default_factory=dict)
    group_map: dict = field(default_factory=dict)
    exclude_dirs: list[str] = field(default_factory=list)
    line_freq: float | str | None = 50.0
    skip_ica: bool = False
    exclude_annotation_regex: str | None = None
    condition_mask: dict | None = None
    notes: str = ""

    def __post_init__(self):
        self.roots_configured = list(self.roots or [])
        self.roots = expand_roots(self.roots_configured)

    # ---------------------------------------------------------------- discovery
    def _excluded(self, p: Path) -> bool:
        """exclude_dirs entries may be wildcards ('ds006036*'): a folder of ANOTHER dataset that sits under
        the same root (same subject IDs!) must never be picked up."""
        return any(fnmatch.fnmatch(part, pat) for part in p.parts for pat in self.exclude_dirs)

    def _check_ready(self):
        bad = [k for k in ("file_glob", "subject_regex") if "VERIFY" in str(getattr(self, k))]
        if bad or not self.roots:
            raise RuntimeError(f"Dataset '{self.name}' is not configured yet or its folders were not found "
                               f"(configured roots: {self.roots_configured}; VERIFY fields: {bad}). "
                               "Edit config/datasets.yaml, set NH_DRIVE, or pass --roots.")

    def find_recordings(self) -> pd.DataFrame:
        """All candidate files per subject (duplicates across Drive parts are kept for inventory)."""
        self._check_ready()
        rows = []
        rx = re.compile(self.subject_regex)
        for root in self.roots:
            rp = Path(root)
            if not rp.exists():
                continue
            for p in rp.glob(self.file_glob):
                if self._excluded(p):
                    continue
                m = rx.search(p.name)
                if m:
                    rows.append({"subject": m.group(1), "path": str(p), "bytes": p.stat().st_size})
        return pd.DataFrame(rows, columns=["subject", "path", "bytes"])

    def recordings(self) -> dict[str, str]:
        """One file per subject: the largest copy that MNE can open (truncated copies are skipped)."""
        cands = self.find_recordings().sort_values(["subject", "bytes"], ascending=[True, False])
        chosen = {}
        for sub, grp in cands.groupby("subject"):
            for path in grp["path"]:
                try:
                    mne.io.read_raw(path, preload=False, verbose="ERROR")
                    chosen[sub] = path
                    break
                except Exception:
                    continue
        return chosen

    def load_raw(self, path: str) -> mne.io.BaseRaw:
        raw = mne.io.read_raw(path, preload=True, verbose="ERROR")
        if self.condition_mask:
            raw = apply_condition_mask(raw, self.condition_mask)
        if self.exclude_annotation_regex and len(raw.annotations):
            rx = re.compile(self.exclude_annotation_regex)
            a = raw.annotations
            desc = ["BAD_condition" if rx.search(d) else d for d in a.description]
            raw.set_annotations(mne.Annotations(a.onset, a.duration, desc, orig_time=a.orig_time))
        return raw

    # ------------------------------------------------- labels (gatekeeper only)
    def read_participants(self) -> pd.DataFrame:
        """Called ONLY by nh.labels.open_labels. Never call from feature extraction."""
        self._check_ready()
        for root in self.roots:
            hits = sorted(h for h in Path(root).glob(self.participants_glob) if not self._excluded(h))
            if hits:
                sep = "\t" if hits[0].suffix == ".tsv" else ","
                df = pd.read_csv(hits[0], sep=sep)
                df.columns = [c.strip() for c in df.columns]
                df = df.rename(columns=self.column_map)
                if self.group_map and "group" in df:
                    df["group"] = df["group"].astype(str).str.strip().map(self.group_map)
                return df
        raise FileNotFoundError(f"{self.name}: participants file not found under roots")


def condition_keep_intervals(onsets, descriptions, t_end: float, cm: dict, res: float = 0.01):
    """Time intervals to KEEP, from zero-duration event markers (ds006036 style).

    flicker : runs of `flicker_marker` pulses closer than flicker_gap_s form one stimulation block;
              [first - pad_before, last + pad_after] is dropped (SSVEP harmonics of 15/20 Hz flicker
              land on 30/40 Hz).
    state   : eye state follows the `state_events`; only `keep_state` is kept, time before the first
              state event is dropped when unknown_state == 'drop'; +-transition_pad_s around every
              state change is dropped (blinks, movement).
    Returns a list of (start, stop) in seconds."""
    d = [str(x).strip() for x in descriptions]
    on = np.asarray(onsets, float)
    t = np.arange(0.0, t_end, res)
    keep = np.ones(len(t), bool)
    marks = np.sort(on[[x == cm["flicker_marker"] for x in d]])
    if len(marks):
        br = np.r_[0, np.where(np.diff(marks) > cm.get("flicker_gap_s", 1.0))[0] + 1, len(marks)]
        pb, pa = cm.get("flicker_pad_s", [0.5, 1.0])
        for i, j in zip(br[:-1], br[1:]):
            keep &= ~((t >= marks[i] - pb) & (t <= marks[j - 1] + pa))
    se = cm.get("state_events")
    if se:
        inv = {v: k for k, v in se.items()}
        ev = sorted((o, inv[x]) for o, x in zip(on, d) if x in inv)
        state = np.full(len(t), "unknown", dtype=object)
        cur, last = "unknown", 0.0
        for o, k in ev:
            state[(t >= last) & (t < o)] = cur
            cur, last = k, o
        state[t >= last] = cur
        ok = state == cm["keep_state"]
        if cm.get("unknown_state", "drop") == "keep":
            ok |= state == "unknown"
        keep &= ok
        pad = cm.get("transition_pad_s", 1.0)
        for o, _ in ev:
            keep &= ~(np.abs(t - o) <= pad)
    stops = [o for o, x in zip(on, d) if x in cm.get("stop_markers", [])]
    if stops:
        keep &= t < min(stops) - cm.get("transition_pad_s", 1.0)
    dk = np.diff(np.r_[0, keep.astype(np.int8), 0])
    return [(t[a], t[b - 1] + res) for a, b in zip(np.flatnonzero(dk == 1), np.flatnonzero(dk == -1))]


def apply_condition_mask(raw: mne.io.BaseRaw, cm: dict) -> mne.io.BaseRaw:
    """Mark everything outside the kept intervals as BAD_condition (dropped by ICA fitting, epoching
    and bad-channel statistics). Zero-duration markers alone cannot do this."""
    a = raw.annotations
    t_end = float(raw.times[-1])
    keep = condition_keep_intervals(a.onset - raw.first_time if len(a) else [], a.description, t_end, cm)
    bad, cur = [], 0.0
    for s0, s1 in keep:
        if s0 > cur:
            bad.append((cur, s0 - cur))
        cur = s1
    if cur < t_end:
        bad.append((cur, t_end - cur))
    if bad:
        on, du = zip(*bad)
        raw.set_annotations(a + mne.Annotations(np.asarray(on) + raw.first_time, du, ["BAD_condition"] * len(on),
                                                orig_time=a.orig_time))
    raw.info["description"] = f"condition mask kept {sum(s1 - s0 for s0, s1 in keep):.0f}s"
    return raw


def get_adapter(name: str, registry_path: Path | str = DATASETS_PATH, **overrides) -> Adapter:
    reg = yaml.safe_load(Path(registry_path).read_text())
    if name not in reg:
        raise KeyError(f"unknown dataset '{name}'. Known: {list(reg)}")
    spec = {**reg[name], **overrides}
    return Adapter(name=name, **spec)
