# P09 · Pre-registration, freeze and label-access ledger

**Question.** What was fixed before the diagnoses were opened, and when exactly was each label access made?
**Type.** Pipeline validation (audit trail).
**When / where.** Freeze on 14 Nov 2026 at 15:12:21 UTC, laptop.

**What was run.**
1. `03_freeze.py` computed SHA-256 hashes of:
    - the configuration;
    - all analysis code;
    - the analysis plan;
    - the metric and method selections;
    - the mechanism fingerprints.

   It wrote them to `freeze.json` and the ledger. The config was set to `status: frozen`.
2. From then on, every script that opens labels writes an entry to `access_ledger.jsonl` (time, user, hashes, purpose).
3. Before the freeze, the label gate refuses access unless the frozen hashes match.

**Command.** `python scripts/03_freeze.py --override-reason "<reason>"` (the override records why the frozen primary differs from the simulation's pick).
**Code.** `../../code/neurohertz_v2_frozen/scripts/03_freeze.py`, `../../code/neurohertz_v2_frozen/nh/labels.py`, `nh/ledger.py`
**Documents** (in `../../code/neurohertz_v2_frozen/docs/`): `ANALYSIS_PLAN.md` (the pre-registered plan), `LEAKAGE_CONTRACT.md` (rules that keep labels out of label-free steps), `MECHANISMS.md`, `METHODS_REVIEW.md`.

| Output in `results/` | Content |
|---|---|
| `freeze.json` | Hashes, primary feature, simulation pick, override reason, number of development unblindings before the freeze |
| `access_ledger.jsonl` | Every label access after the freeze, one JSON line each |
| `03_freeze.log` | Console log |
