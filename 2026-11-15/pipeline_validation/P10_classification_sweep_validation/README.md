# P10 · Validation of the classification sweep

**Question.** Before the exploratory sweep (H9) is run on real data, do its estimators and statistics recover known effects and keep false positives at the nominal rate?
**Type.** Pipeline validation. Synthetic data and simulated nulls.
**When / where.** Cloud, 15 Nov 2026 (code audit, unit tests, pilots). Laptop, 15 Nov 2026 (full-size controls inside `run_classification.sh`).

**What was run.**
1. **Code audit.** Six bugs were found and fixed (listed in RESULTS).
2. **Unit tests** (see P01).
3. **Synthetic control 1, PV-output loss.**
    - Injected: gamma reduced in the posterior circuit for "AD" and the frontal circuit for "FTD".
    - Checks: (1) an AD–CN 30–48 Hz cluster with its peak at a posterior electrode; (2) an FTD–CN cluster with its peak at a frontal electrode; (3) the change attributed to the periodic, not the aperiodic, part.
4. **Synthetic control 2, erratic drive.**
    - Injected: gamma frequency instability.
    - Checks: the band-instability stages must rank a gamma measure first for AD–CN and FTD–CN, at least one contrast must be family-wise significant, and no other band may be.
5. **Laptop run 1.** It stopped at control 1, check 3. The cause was diagnosed in the cloud on pilot data, and the periodic/aperiodic split was changed from IRASA to specparam in knee mode. Check 3 was then made a reported warning (decision recorded in `sweep/check_positive_control.py`). These decisions were made before any real-data result of the sweep existed.

**Commands.** `bash run_classification.sh` (steps `t00`, `c00`–`c16`) in `../../code/classification_sweep/`.
**Code.** `sweep/check_positive_control.py`, `sweep/check_instability_control.py`, `tests/test_sweep.py`, `tests/test_stats.py`

| Output in `results/` | Content |
|---|---|
| `cloud_pilot_PV_loss_control_REPORT.md` | Pilot of control 1 (28 subjects, IRASA split, 300 permutations) |
| `cloud_pilot_erratic_drive_control_REPORT.md` | Pilot of control 2 (28 subjects, 2 surrogates) |
| `laptop_run1_c05_synth_check_FAILED.log` | The control-1 check of laptop run 1 (88 subjects); after re-running, this file holds run 2's log |
