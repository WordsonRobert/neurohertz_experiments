# H6 · Which circuit mechanism explains a gamma change in AD?

**Hypothesis.** One of six simulated mechanisms (`pipeline_validation/P04`) explains the AD pattern in gamma features. The pre-registered tests M01–M16 each check one predicted pattern: instability in AD, frontal pattern in FTD, peak width and frequency, jitter beyond noise, slips, tails, coupling, MMSE, alpha slowing. Theories are T1–T6 (`../../code/neurohertz_v2_frozen/docs/MECHANISMS.md`).
**Type.** Confirmatory but **gated**. Tests run on subjects with a detectable gamma oscillation, and only if at least a pre-specified fraction of each group has one; otherwise all results are descriptive. A mechanism claim also requires both simulator families to agree.
**When / where.** 14 Nov 2026, laptop (ledger 15:13:44 UTC).

**What was run.**
1. Presence gate: share of subjects whose ROI shows a gamma oscillation above background.
2. M01–M16 on subjects with gamma (refused if any group had fewer than 3).
3. The same tests on all subjects (descriptive).
4. Scorecards per theory.
5. Fingerprint comparison of the AD–CN effect vector with each mechanism.

**Command.** `python scripts/14_mechanism_tests.py --dataset ds004504`
**Code.** `../../code/neurohertz_v2_frozen/scripts/14_mechanism_tests.py`

| Output in `results/` | Content |
|---|---|
| `report.md` | The full mechanism report |
| `presence.csv` | Subjects with a detectable gamma oscillation, per group |
| `tests.csv` | M01–M16 (with-gamma and all-subject versions): effect, CI, p, Holm p |
| `scorecard.csv`, `sensitivity.csv` | Theory scorecards and sensitivity |
| `fingerprint_comparison.json` | Match of the AD–CN effect vector to each mechanism |
