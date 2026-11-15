# classification/: narrowing down what (if anything) happens near 40 Hz in AD

**EXPLORATORY.** ds004504 was unblinded by the frozen confirmatory run (2026-11-14), so nothing here is a
confirmatory result. Whatever survives this sweep is frozen as a new, narrow hypothesis and tested on data
nobody has looked at (hospital cohort, or the ds007427 lockbox).

The reasoning, every alternative explanation, and the test that removes each one are in
`docs/HYPOTHESIS_TREE.md`. Read that first.

## Run it (laptop)

```bash
cd /media/wordson22/Expansion/projects2/neurohertz2/classification
conda activate nh
bash run_classification.sh          # JOBS=8 by default; about 3-4 h in total
```

- It uses the frozen code in `../final_run/neurohertz_v2` read-only and never writes there.
- Finished subjects are cached, so re-running after a crash continues where it stopped.
- Two **positive controls** run first. Control 2 injects an *erratic gamma drive* (frequency instability). The band-instability stages must find it in gamma, and only in gamma; in the cloud pilot FTD–CN reached family-wise p = 0.003. Control 1 is synthetic EEG with a known PV-interneuron gamma change
  (posterior in "AD", frontal in "FTD"). If the sweep does not find it, the run stops before touching real
  data. A pilot of this control already passed in the cloud:
  - AD-CN: a cluster at 31–44 Hz with its peak at O2;
  - FTD-CN: a cluster at 30–45 Hz with its peak at F3;
  - no leakage into the aperiodic part.

## Stages

| Stage | Labels? | What it answers |
|---|---|---|
| `sweep/00_cache_clean.py` | no | The frozen preprocessing, cached once per subject. Two variants: `main` and `nomuscle` (BSS-CCA off) |
| `sweep/10_features_raw.py` | no | Per subject, measured in both CSD and average reference: 0.5-Hz spectra; spectra from the lowest-EMG epochs; IRASA periodic/fractal split; per-epoch vigilance; every 30–48 Hz burst and its descriptors; sharp transients; PAC; alpha 1:4 harmonic locking |
| `sweep/12_band_instability.py` | no | **Instability in every band** (delta, theta, alpha at IAF ± 2 Hz, low/high beta, gamma): IF spread, phase slips, cycle-period CV, epoch-to-epoch peak-frequency SD, burst-frequency SD. Each is measured at matched SNR against the person's own 1/f background and against 10 spectrum-matched surrogates (`__excess` = beyond the spectrum), on all data and on each half |
| `sweep/15_subject_table.py` | no | One row of mechanistic summaries per subject |
| `sweep/20_frequency_resolved.py` | yes | Freedman–Lane cluster permutation over frequency × channel (age, sex; ± EMG) for every spectrum family and contrast, plus the vigilance-stratified test |
| `sweep/30_burst_types.py` | typing no, tests yes | **Classifies the instabilities.** Burst types come from a Gaussian mixture fitted label-free; then the groups are compared on type rates and on within-burst frequency instability |
| `sweep/40_stratify.py` | norms only | Each patient's normative z per mechanism axis; patients clustered with diagnosis hidden; afterwards, the clusters are checked against diagnosis and MMSE |
| `sweep/50_predict.py` | yes | Nested CV by mechanism family; AUC, balanced accuracy and accuracy; gain over the slowing + aperiodic baseline; every data-driven step is fit inside the folds |
| `sweep/55_band_instability_analysis.py` | A–C no, D–G yes | Characterizes every instability measure: reliability gate, spectral share, PCA structure, family-wise group tests under a covariate ladder (age/sex, then +slowing, then +1/f, then +rhythm presence), time-on-task drift, severity within AD, and nested-CV prediction with in-fold selection and whole-pipeline permutation |
| `sweep/60_report.py` | yes | `results/ds004504/main/REPORT.md`: the elimination table with verdict rules fixed before any real result |

## Already done (existing features, no raw data): `explore/01_existing_features.py`

Results are in `results/explore01/report.md`:

- The old 73.8% does not reproduce. The same metric, computed after clean preprocessing, gives AUC 0.48.
- Absolute 30–45 Hz power is not higher in AD (g = −0.26).
- The "above 1/f" gamma excess follows the steeper spectrum and slowing.
- Muscle is not higher in AD.
- There is no sign of alpha harmonics.
- The real separators are slowing (AUC 0.83) and the 1/f slope (AUC 0.77).
