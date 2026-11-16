# Snapshot 2026-11-16: frequency × electrode instability screen

This folder adds to `../2026-11-15/`. Code that is not listed in `code/` is unchanged from `../2026-11-15/code/classification_sweep/`.

## Timeline

| When (2026) | Where | Run | Folder |
|---|---|---|---|
| 15–16 Nov | Cloud | Screen code written: instability in 4-Hz windows every 2 Hz, 2–90 Hz, all 19 electrodes. Pilot on 28 synthetic subjects | `code/`, `P11` |
| 16 Nov, 00:52–03:19 | Laptop | Screen, run 1: synthetic control at full size. Stopped at check 3 (one cluster in the 54–90 Hz grid) | `P11` |
| 16 Nov | Cloud | Cause found: the check counted single-map results across 30 maps without correcting for the number of maps. Correction over maps added; the three criteria are unchanged | `P11`, `code/` |
| 16 Nov, 04:05–11:56 | Laptop | Screen, run 2: synthetic check passed; ds004504 screen (instability measures from both SNR sub-bins) | `P11`, `bio_tests/H10` |
| 16 Nov | Cloud | Coverage of the both-sub-bin measures found too low in 2–46 Hz; re-analysis with the low-SNR sub-bin (b1) added | `code/`, `bio_tests/H10` |
| 16 Nov | Cloud | Is the posterior 32–40 Hz excess a 1/f-fitting artefact? Local-background test, rule fixed and hashed before the data were loaded: SURVIVES | `bio_tests/H11` |
| 16 Nov | Cloud | Fisher-information identifiability of the six P04 mechanisms (reuses P04 simulations) | `P12` |
| 16 Nov | Cloud | What the posterior excess is made of: beta loss + flattening; absolute 32–40 Hz unchanged; bump pipeline-dependent | `bio_tests/H12` |
| 16 Nov | Cloud | ds006036 headers point to another subject's data file (63/65); own-file reader | `P13` |
| 16 Nov | Cloud | Calibrated 3-population circuit: which mechanism reproduces the phenotype (excitation-up rejected) | `bio_tests/H13` |
| 16 Nov | Cloud | Photic driven responses in the same people; mechanism test (underpowered) | `bio_tests/H14` |
| 16–17 Nov | Cloud | SEA-AD human tissue: L2/3 excitatory loss under P3/P4, tau-linked; SST loss temporal only | `bio_tests/H15` |
| 16 Nov | Cloud | Tissue-measured loss predicts the EEG phenotype with no fitting (signs 99%, about half the size) | `bio_tests/H16` |
| 17 Nov | Cloud | Multimodal injectivity map and probe-order (non-commuting) identifiability | `bio_tests/H17` |
| pending | Laptop | `run_freq_instability_b1.sh`: synthetic check and ds004504 with b1 (about 15 min, no new feature extraction) | `P11`, `bio_tests/H10` |

## Map

| ID | Kind | Question |
|---|---|---|
| P11 | Pipeline validation | Does the frequency × electrode screen find an injected gamma instability at the right frequency and place, and nothing elsewhere? |
| H11 | Bio test, exploratory | Is the posterior 32–40 Hz excess in AD an artefact of the global 1/f fit? |
| P12 | Pipeline validation, exploratory | How many of the six P04 mechanisms can a 36 vs 29 study resolve (Jacobian rank, Cramér–Rao bounds)? |
| H12 | Bio test, exploratory | Is the 32–40 Hz excess more gamma, or less of everything around it? Does it depend on the pipeline? |
| P13 | Pipeline validation | Does MNE load each ds006036 subject's own EEG? (No: header pointers are wrong) |
| H13 | Bio test, model | Which circuit change, in a model calibrated to CN, reproduces the AD − CN posterior spectrum? |
| H14 | Bio test, exploratory | Do driven responses in the same people separate the two surviving mechanisms? |
| H15 | Bio test, independent modality | Which neurons decline with AD pathology in posterior cortex (human tissue), and with tau or amyloid? |
| H16 | Bio test, cross-modal prediction | Does the tissue-measured loss predict the EEG effect sizes without fitting? |
| H17 | Theory / design | Is mechanism → characterization injective at rest? With tissue and probes? Does probe order matter? |
| H10 | Bio test, exploratory | Does the instability of any frequency window at any electrode separate AD, beyond slowing and 1/f? Which cells are reliable and show no group difference? |

The hypothesis that H12–H17 test, and the evidence chain across all modalities, is in `MECHANISM_HYPOTHESIS.md`.
