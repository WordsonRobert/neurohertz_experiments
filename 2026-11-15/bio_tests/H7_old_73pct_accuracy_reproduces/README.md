# H7 · The earlier 73.8% accuracy (v1 pipeline) reproduces with clean preprocessing

**Hypothesis.** The v1 NeuroHertz pipeline reported 73.85% accuracy (AUC 0.75) for AD vs CN on ds004504 from one feature: the SD of the instantaneous gamma frequency of a VMD mode, with a per-subject VMD settings sweep. If that reflects gamma instability, the same metric computed with clean preprocessing should classify similarly.
**Type.** Exploratory: run after the labels were opened (15 Nov 2026). It generates hypotheses for a new cohort.
**What was run.** The frozen pipeline's `legacy_std` (SD of the instantaneous frequency in 25–80 Hz, no gating; the v1-style metric) was taken from the final-run features. Then:
- repeated stratified 5-fold CV (20 repeats) and leave-one-subject-out logistic regression for AD vs CN;
- the same with the 1/f exponent, then the exponent plus theta/alpha, regressed out inside each training fold;
- the same for the exponent, theta/alpha, gamma envelope and `burst_freq_sd` alone, for comparison;
- Spearman correlations of `legacy_std` with spectral measures.

**Command.** `python explore/01_existing_features.py` (section A) in `../../code/classification_sweep/`
**Code.** `../../code/classification_sweep/explore/01_existing_features.py`

| Output in `results/` | Content |
|---|---|
| `old_metric_reanalysis.csv` | Per model: CV AUC (mean, 2.5–97.5%), accuracy, LOSO AUC and accuracy |
| `OLD_pipeline_session4_final_results.json` | The v1 pipeline's saved results (accuracy 73.85, AUC 0.748, per-subject VMD K 6–9 and alpha 1000–4000, train–test gap 0.26) |

The v1 code (repository `WordsonRobert/neurohertz`, folders `session1`–`session4`) could not be read automatically, so the exact v1 feature computation was not re-run.
