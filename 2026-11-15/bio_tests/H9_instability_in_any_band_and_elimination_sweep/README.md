# H9 · Frequency instability in any band separates AD, beyond slowing and the 1/f background

**Hypothesis.** The instability of any recognisable rhythm (delta, theta, alpha at the individual peak ± 2 Hz, low beta, high beta, gamma) separates AD from CN (and FTD), beyond what slowing and the 1/f background already explain. In parallel, an elimination sweep tests whether any 30–48 Hz difference is explained by:
- muscle;
- eye movements;
- the 1/f background;
- vigilance;
- alpha harmonics;
- sharp transients;
- filter edges;
- medication (untestable here).

**Type.** Exploratory: run after the labels were opened (15 Nov 2026). It generates hypotheses for a new cohort.
**Status at this snapshot.** The code is complete and validated (`pipeline_validation/P10`). Laptop run 2 was in progress when this snapshot was made, so **no real-data results are included yet**. When it finishes, its outputs go in `results/`.

**What the run does** (`../../code/classification_sweep/run_classification.sh`). Each stage is documented in `../../code/classification_sweep/docs/HYPOTHESIS_TREE.md`. Labels are used only from stage 20 on.
- `00` Re-runs the frozen preprocessing, with and without BSS-CCA muscle removal.
- `10` Computes, without labels:
    - 0.5 Hz spectra;
    - spectra from the lowest-EMG epochs;
    - specparam-knee periodic/aperiodic split (IRASA as secondary);
    - per-epoch vigilance;
    - every 30–48 Hz burst with descriptors;
    - sharp transients;
    - PAC;
    - alpha 1:4 harmonic locking.
- `12` Instability in every band, label-free: five measures (IF spread, phase slips, cycle-period CV, epoch-to-epoch peak-frequency SD, burst-frequency SD). Each is computed at matched SNR and against 10 spectrum-matched surrogates (`__excess`), on all data and on each half.
- `20` Frequency × electrode cluster permutation tests (Freedman–Lane, age, sex, ± EMG) for each spectrum family and contrast; vigilance-stratified test.
- `30` Burst types found without labels (Gaussian mixture), then compared by group.
- `40` Normative deviation per mechanism axis; patients clustered with diagnosis hidden.
- `50` Nested CV by feature family; gain over slowing + 1/f.
- `55` Instability characterisation:
    - reliability gate;
    - spectral share;
    - PCA structure;
    - family-wise (maxT) group tests under a covariate ladder: age/sex, then +slowing, then +1/f, then +rhythm presence;
    - time-on-task drift;
    - MMSE within AD;
    - nested prediction with in-fold selection and whole-pipeline permutation.
- `60` Elimination table. Its verdict rules were written before any real result.

**Expected outputs** (written by the run into `classification/results/ds004504/main/`; copy them into `results/` here):
- `REPORT.md` (elimination verdicts) and `bandinst/REPORT_INSTABILITY.md`
- `freq/clusters.csv`, `freq/window_35_45.csv`, `freq/tmap_*.png`
- `bursts_p95/`, `bursts_p99/`, `stratify/`, `predict/prediction.csv`, `subject_table.csv`
