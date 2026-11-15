"""Append-only access ledger.

Every time diagnostic labels are read, a line is appended here. The ledger is part of the
paper's audit trail: it shows when labels were first seen relative to when the pipeline was frozen.
"""
from __future__ import annotations

import datetime as _dt
import getpass
import json
from pathlib import Path

from .config import ROOT, analysis_hash

LEDGER_PATH = ROOT / "registry" / "access_ledger.jsonl"


def log_event(event: str, **fields) -> dict:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "user": getpass.getuser(),
        "event": event,
        **analysis_hash(),
        **fields,
    }
    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def read_events(event: str | None = None, **match) -> list[dict]:
    if not LEDGER_PATH.exists():
        return []
    out = []
    for line in LEDGER_PATH.read_text().splitlines():
        r = json.loads(line)
        if event is not None and r.get("event") != event:
            continue
        if all(r.get(k) == v for k, v in match.items()):
            out.append(r)
    return out
