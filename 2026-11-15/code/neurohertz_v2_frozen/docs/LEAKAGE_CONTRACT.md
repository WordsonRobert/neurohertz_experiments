# Leakage contract

This file lists, rule by rule, what each part of NeuroHertz v2 is allowed to see, and how the code enforces it. If a rule is broken, the result it touches is reported as **EXPLORATORY**, never as confirmatory.

## Definitions

- **Labels**: diagnosis (AD / CN / FTD / MCI), MMSE or MoCA, and any other clinical outcome.
- **Covariates**: age, sex, education. These are read through the same gate as labels, because they sit in the same file.
- **Fitted across subjects**: any number estimated from more than one subject's data, such as a scaler mean, a classifier weight, a chosen hyper-parameter, a chosen channel or a chosen threshold.
- **Discovery cohort**: ds004504. It was already analysed by NeuroHertz v1, so it is *not* blind; see rule 9.
- **Lockbox cohort**: an independent dataset that is opened once, after freezing (CAUEEG, ds007427, BrainLat, hospital).

## Rules

| # | Rule | Why | Enforced by |
|---|------|-----|-------------|
| 1 | Feature extraction (Stage A) never reads labels or covariates. | Features must not be shaped by the outcome. | `tests/test_leakage.py::test_stage_a_never_touches_labels` parses each Stage-A file and fails if it imports `nh.labels`, calls `read_participants`/`open_labels`, or names a participants file. |
| 2 | Each subject's features depend only on that subject's recording and the frozen config. All rejection thresholds, bad-channel rules and gamma gates are per-subject robust statistics or fixed constants. Nothing is pooled across subjects. | This makes extraction "fold-free": it can run once for everyone without leaking across CV folds. | Code structure: `process_subject` sees one file. Surrogate RNG is seeded from the subject ID, not the run order (`subject_rng`). `test_subject_features_independent_of_batch_and_order`. |
| 3 | Every parameter is fixed in `config/pipeline.yaml` before labels are used confirmatorily. This includes band, ROI, epoch rules, clean duration, surrogate count and metric. | Prevents tuning the analysis to the result (garden of forking paths). | `scripts/03_freeze.py` hashes config + code + analysis plan. `nh/labels.py` checks the hash before opening confirmatory labels. |
| 4 | The primary metric is chosen on **simulated ground truth only**, by a selection rule written in code before any real result is seen. | Removes researcher degrees of freedom in choosing "which instability measure". | `scripts/02_simulation_validation.py` (rule in its docstring). Freezing fails if `statistics.primary_feature` differs from the simulation choice, unless an override is given; any override is recorded with its reason. |
| 5 | The ROI (P3, Pz, P4, O1, O2) and regions are anatomical and pre-specified. No channel is picked because it separates groups. | v1 picked P3 from a sweep; that selection used the full dataset. | Config constant. The scalp-wide max-T test is always reported alongside the ROI result. |
| 6 | Anything fitted across subjects (scaling, C, classifier, recalibration) is refit inside every outer training fold. The test fold is used only by `predict_proba`. | Classic CV leakage. | `nh/predict.py`: an sklearn `Pipeline` inside `GridSearchCV` (inner CV), cloned per outer fold, with an assertion that train and test indices don't overlap. `test_nested_cv_is_not_fooled_by_noise_but_leaky_selection_is` shows the guard works and that the leaky alternative inflates AUC. |
| 7 | Exactly one row per subject in every test and model. | Duplicated subjects (e.g. a subject in two Drive parts) leak between folds. | `assert_one_row_per_subject` in every stats and predict entry point. The adapter keeps one loadable file per subject. |
| 8 | Permutation tests re-run the **whole** pipeline (inner CV included) on shuffled labels. | A permutation test of only the final step understates the null. | `permutation_test_pipeline`. Covariate-adjusted group tests use Freedman–Lane. |
| 9 | Discovery labels open during development only with a written reason. Every such opening is logged, and every result produced from it is stamped `EXPLORATORY`. | ds004504 labels and v1 results are already known to the authors. Honesty requires the paper to say that discovery is not blind. | `nh/labels.py::open_labels` together with `registry/access_ledger.jsonl`. `03_freeze.py` counts and reports prior unblindings. |
| 10 | Lockbox labels open only if the analysis is frozen and unchanged, AND the lockbox feature table was extracted and hashed **after** the freeze, AND the table passed in matches that hash byte for byte. | The external result must come from a pipeline that could not have been adjusted after seeing it. | `nh/labels.py::_check_lockbox`. The first opening is logged as `LOCKBOX_OPENED`; any later one as `LOCKBOX_REOPENED`, which must be disclosed. |
| 11 | The external cohort gets the discovery model **unchanged**: no refit, no threshold or calibration tuning, no harmonisation that uses its labels. | Otherwise "external validation" is just more fitting. | `scripts/06_external_validation.py` loads the frozen model, checks its analysis hash and only calls `predict_proba`. |
| 12 | Cross-dataset harmonisation, if ever needed, may use only label-free information (e.g. per-dataset feature distributions pooled over all subjects), and must be in the config before freezing. | ComBat-style correction with diagnosis as a covariate leaks labels. | Not implemented by default. The primary metrics are designed to be dimensionless (surrogate-normalised) precisely to avoid harmonisation. |
| 13 | Exclusions are pre-specified and label-blind: too many bad channels, less than 120 s of clean data, or a load error. Every exclusion is listed in the output with its reason. | Post-hoc exclusion of "outliers" is a common hidden leak. | `ExcludedRecording`; `qc.csv`; the `excluded` field in the discovery results. |
| 14 | Every subject contributes the same amount of clean data (the first 240 s of clean epochs). | Recording length differs by group in ds004504 (AD 5.1–21.3 min) and affects variability estimates. | `preprocessing.duration` in the config. |
| 15 | The analysis plan is hashed at freeze. Any later edit to it is detectable. | Stops the plan being rewritten to match results. | `analysis_plan_sha256` in `registry/freeze.json`. |
| 16 | Mechanistic predictions (`mechanism.tests` in the config), the presence gate and the fingerprint comparison rule are fixed before unblinding; the fingerprints themselves are hashed at freeze. A `--quick` fingerprint run can never be frozen. | Choosing which mechanism "fits" after seeing the AD pattern would be storytelling, not testing. | `mechanism_fingerprints_sha256` in `registry/freeze.json`; `14_mechanism_tests.py` stamps EXPLORATORY otherwise. |
| 17 | "No difference" predictions are tested as equivalence (90% CI inside the smallest effect of interest), never inferred from p > 0.05. | With 23 FTD patients, absence of evidence is weak; treating it as evidence would favour AD-specific theories for free. | `sesoi_d`, `sesoi_r`, `sesoi_attenuation`; `classify()` in `14_mechanism_tests.py`. |
| 18 | Simulation code and synthetic data never touch real labels; the synthetic dataset has its own label role that is not logged and stamps every output SYNTHETIC. | Keeps dry runs out of the access ledger and out of the evidence. | role `synthetic` in `nh/labels.py`; AST checks in `tests/test_leakage.py`. |

## What is *allowed* before unblinding

- Running Stage A on every dataset. Only QC tables and pooled, **label-free** descriptive statistics may be looked at.
- Calibrating the simulation's base signal to pooled label-free statistics (median gamma SNR, aperiodic exponent, burst rate across *all* subjects).
- Fixing bugs. If a bug is found after unblinding, the fix becomes a new disclosed analysis version: the old freeze record is kept and the new results are stamped with the new hash.

## Known limitations (to state in the paper)

- ds004504 discovery results are **not blind**. v1 already reported AD > CN for an IF-variability feature on this dataset. Only lockbox results are confirmatory.
- ds006036 contains the same people as ds004504. It is paired evidence, never independent replication.
- ICA component rejection uses ICLabel, a pre-trained classifier. It is subject-level and label-blind, but it was trained on other data. Results with ICA off are reported as a sensitivity analysis.
