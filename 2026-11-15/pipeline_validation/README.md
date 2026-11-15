# Pipeline validation

These runs test the **method**, not the biology. Most use no diagnosis labels at all. They answer: is each measure reliable; does it measure what it claims (shown on simulated data with a known answer); were the method choices made without seeing diagnoses; and could information about the diagnoses have leaked into the analysis?

| Folder | Question | Labels used? |
|---|---|---|
| `P01_unit_tests` | Do the code's safety checks and estimators behave as specified? | No |
| `P02_method_ablations` | Which preprocessing and estimator settings give a reliable, muscle-free measure? | No |
| `P03_simulation_metric_selection` | Which metric tracks frequency jitter and not nuisances (simulated EEG)? | No |
| `P04_mechanism_identifiability` | Can simulated circuit mechanisms be told apart from EEG features? | No |
| `P05_synthetic_positive_controls_frozen_pipeline` | Does the frozen pipeline recover a mechanism injected into synthetic EEG? | Synthetic only |
| `P06_feature_extraction_and_quality_control` | How many recordings were usable, and how much clean data each had | No |
| `P07_reliability_split_half` | How reliable is each measure within a recording? | No |
| `P08_second_session_ds006036` | Does each measure repeat in the same people's second recording? | No (IDs checked against the participant table) |
| `P09_preregistration_freeze_and_leakage_control` | What was fixed before the labels were opened, and when were labels accessed? | Records label access |
| `P10_classification_sweep_validation` | Do the sweep's estimators and statistics recover known effects and keep false positives at 5%? | Synthetic only |
