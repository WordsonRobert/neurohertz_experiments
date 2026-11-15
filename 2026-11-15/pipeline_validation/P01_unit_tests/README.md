# P01 · Unit tests

**Question.** Do the code's safety checks and estimators behave as specified before anything is run on real data?
**Type.** Pipeline validation. No labels.
**When / where.** 14 Nov 2026 (frozen pipeline) and 15 Nov 2026 (classification sweep), laptop.

**What was run.** Automated tests that run before every full run.
- **Frozen pipeline (55 tests).**
    - Leakage guards: label-free scripts cannot open diagnoses; lockbox labels need a freeze.
    - Estimators are scale-invariant, and the ablation options reproduce the base pipeline.
    - ds004504 never picks up ds006036 files.
    - No p-value is produced without data.
    - The ds006036 condition mask works.
- **Classification sweep (11 tests).**
    - Estimators on synthetic signals with known answers: IRASA, bursts, PAC, harmonic locking, sharp transients, and the surrogate "excess" measure.
    - Statistics: t values match statsmodels; the cluster false-positive rate is about 5% under the null; a planted effect is found; prediction on noise gives AUC about 0.5.

**Commands.**
```bash
cd code/neurohertz_v2_frozen && python -m pytest -q
cd code/classification_sweep && python -m pytest -q tests
```
**Code.** `../../code/neurohertz_v2_frozen/tests/`, `../../code/classification_sweep/tests/`

| Output in `results/` | Content |
|---|---|
| `frozen_pipeline_tests.log` | pytest output of the frozen pipeline |
| `classification_sweep_tests.log` | pytest output of the sweep (laptop, run 2) |
