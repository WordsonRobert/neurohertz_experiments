# Snapshot 2026-11-15: every run from the last Colab session to the classification sweep

## Timeline of what was run

| When (2026) | Where | Run | Folder |
|---|---|---|---|
| 13 Nov | Google Colab | Feature extraction, primary and preprocessing variants (reference, muscle removal, epoch rejection, aperiodic method); simulation | `pipeline_validation/P02`, `P03` |
| 13–14 Nov | Laptop | Estimator variants (Hilbert / SST / VMD), median filter, surrogate chunk length; re-run after an estimator scale fix | `P02`, `P03` |
| 14 Nov | Laptop | Combined pipelines (CSD vs REST) and the final method decision | `P02` |
| 14 Nov | Laptop | **Final frozen run**: tests → features (ds004504, ds006036) → reliability → simulation → mechanism fingerprints → synthetic controls → **freeze** → labels opened → discovery, mechanism, prediction, ceiling | `P01`, `P03`–`P09`, `bio_tests/H1`–`H6` |
| 14 Nov | Cloud (from laptop files) | ds006036 participant table opened to check subject IDs | `P08` |
| 15 Nov | Cloud | Exploratory re-analysis of existing features: the old 73% result, and 30–45 Hz power against alternative explanations | `bio_tests/H7`, `H8` |
| 15 Nov | Cloud | Classification-sweep code built, audited and pilot-tested on synthetic data | `P10`, `code/classification_sweep` |
| 15 Nov | Laptop | Classification sweep, run 1: stopped at a synthetic check; method changed (IRASA → specparam); run 2 completed: both controls passed, real-data results in H9 | `P10`, `bio_tests/H9` |

## Hypothesis map

| ID | Hypothesis tested | Kind | Status |
|---|---|---|---|
| H1 | Gamma frequency instability (`burst_freq_sd`) differs between AD and CN | Confirmatory | Run |
| H2 | Gamma instability tracks MMSE within AD | Confirmatory, gated on H1 | Run (descriptive, because H1 was not significant) |
| H3 | Any AD–CN difference survives spectral and nuisance covariates | Confirmatory, gated on H1 | Run (descriptive) |
| H4 | Gamma instability separates AD from FTD | Confirmatory, gated on H1 | Run (descriptive) |
| H5 | Gamma instability classifies AD vs CN | Confirmatory prediction | Run |
| H6 | A specific circuit mechanism explains a gamma change | Confirmatory, gated on gamma presence | Run (descriptive only) |
| H7 | The earlier 73.8% accuracy of the v1 pipeline reproduces with clean preprocessing | Exploratory | Run |
| H8 | 30–45 Hz power differs in AD beyond muscle, 1/f, slowing and harmonics | Exploratory | Run |
| H9 | Frequency instability in **any** band separates AD, beyond slowing and 1/f | Exploratory | Run |

## Pipeline-validation map

| ID | What it checks |
|---|---|
| P01 | Unit tests: leakage guards, estimator checks, statistics calibration |
| P02 | Method ablations: which preprocessing and estimator settings to use (no labels) |
| P03 | Simulation: which instability metric tracks injected jitter and not nuisances |
| P04 | Mechanism identifiability: can six simulated circuit mechanisms be told apart? |
| P05 | Synthetic positive controls for the frozen pipeline |
| P06 | Feature extraction and quality control (exclusions, clean data per subject) |
| P07 | Split-half reliability of every measure |
| P08 | Second-session (ds006036) reliability and subject-ID check |
| P09 | Pre-registration, freeze hashes, and the label-access ledger |
| P10 | Validation of the classification sweep (estimators, statistics, synthetic controls) |

## Shared files

- `code/`: the exact code (`neurohertz_v2_frozen` produced P01–P09 and H1–H6; `classification_sweep` produced H7–H9 and P10).
- `data_tables/`: per-subject features, quality control and participant lists.
