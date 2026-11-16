# P11 · Synthetic control for the frequency × electrode instability screen

**Question.** Before the screen (H10) is run on real data: does it find an injected frequency instability at the right frequency and electrodes, and produce no significant result where nothing was injected?
**Type.** Pipeline validation; synthetic data.
**When / where.**
- Cloud pilot: 15–16 Nov 2026 (28 subjects, 2 surrogates, 2–60 Hz).
- Laptop run 1: 16 Nov 2026, 00:52–03:19 (88 subjects, 4 surrogates, 2–90 Hz).
- Laptop run 2: 16 Nov 2026, 04:05–04:08 (same features, corrected rule).

**Data.** The erratic-drive synthetic dataset from P10 control 2: 29 "CN", 36 "AD", 23 "FTD". Gamma (30–45 Hz) frequency instability was injected in the posterior circuit for "AD" and in the frontal circuit for "FTD". Nothing was injected at any other frequency.

**What was run.**
1. **Stage 13** (no labels). Five SNR-matched instability measures, the same as in H9:
    - instantaneous-frequency spread
    - phase slips
    - cycle-period CV
    - epoch-to-epoch peak-frequency SD
    - burst-frequency SD

    Each is computed in 4-Hz windows every 2 Hz, at all 19 electrodes, both raw and beyond the spectrum (`__excess`, against phase-randomized surrogates). The windows avoid 47.5–52.5 Hz (the 50 Hz notch), which gives two grids:
    - grid A: 2–46 Hz
    - grid B: 54–90 Hz
2. **Stage 57.**
    - Split-half reliability of every cell.
    - Freedman–Lane cluster permutation over window × electrode, for each measure, contrast and covariate set.
    - Reference cells.
    - Nested-CV prediction.
3. **Check** (`sweep/check_freqinst_control.py`). Criteria written before any run of stage 57; covariates age + sex. Pass requires all three:
    1. a significant AD–CN or FTD–CN cluster, patients higher, peaking at 26–48 Hz;
    2. no significant cluster entirely below 24 Hz;
    3. no significant cluster in grid B.

**Commands.** `bash run_freq_instability.sh` (steps `f00`–`f03`) in `../../code/classification_sweep/`.
**Code.** `sweep/13_freq_instability.py`, `sweep/57_freq_instability_analysis.py`, `sweep/check_freqinst_control.py`, `tests/test_sweep.py` (test of the window layout).

| Output in `results/` | Content |
|---|---|
| `run1_uncorrected/f00_tests.log` … `f03_synth_check.log` | Logs of laptop run 1 (unit tests, stage 13, stage 57, check) |
| `run1_uncorrected/B_clusters.csv` | Every cluster from run 1, with its p within its own map (`p_fwer`) |
| `run1_uncorrected/A_reliability_summary.csv`, `C_reference_cells.csv`, `D_prediction.csv`, `REPORT_FREQ_INSTABILITY.md` | Other run-1 outputs |
| `run1_clusters_with_correction_over_maps.csv` | The same clusters with `p_family` = min(1, 30 × p_fwer) added |
| `run2_corrected/` | Run 2 (corrected rule): logs `f00`–`f03`, clusters and report |
