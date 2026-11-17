# Snapshot 2026-11-17: tests of the mechanistic hypothesis against its two strongest rivals, and an audit of the probe-order claim

This folder adds to `../2026-11-16/`. Numbering continues (H18 follows H17).
- The hypothesis and its evidence chain: `../2026-11-16/MECHANISM_HYPOTHESIS.md` (updated today).
- The literature check that motivated these tests is summarised in the same file, under "Literature check (17 Nov)".

## Timeline

| When (2026) | Where | Run | Folder |
|---|---|---|---|
| 17 Nov | Cloud | Is the high-frequency flattening a non-neural floor (rival R3)? Neural power law + flat floor fitted per subject | `bio_tests/H18` |
| 17 Nov | Cloud | Audit of the H17 probe-order gain: readout-schedule vs non-commuting term, local limit, controls | `pipeline_validation/P14` |
| 17 Nov | Cloud | Is SST loss hidden below the subclass level in posterior cortex (rival R1)? MTG-vulnerable Sst supertypes tested out of region; combined tissue → EEG bridge | `bio_tests/H19` |

## Map

| ID | Kind | Question |
|---|---|---|
| P14 | Pipeline validation, model only | Is H17's order gain G evidence of non-commutativity? (No: ≥ 79% readout schedule, H17 claim retracted) |
| H18 | Bio test, exploratory | Does a constant noise floor under a quieter AD spectrum explain the flatter 24–47 Hz slope? |
| H19 | Bio test, independent modality + cross-modal prediction | Do the Sst supertypes vulnerable in MTG also decline in angular gyrus? Do L2/3 IT and Sst losses together, sized from tissue, predict the EEG? |

## Code

| File | Status | Purpose |
|---|---|---|
| `code/mechanism/audit/order_audit.py`, `limit_check.py` | new | P14, imports the H17 model |
| `code/mechanism/floor_test.py` | new | H18 |
| `code/mechanism/sst_supertypes.py` | new | H19: discovery in MTG, out-of-region test in AnG and V1C |
| `code/mechanism/bridge2.py` | new | H19: combined L2/3 IT + vulnerable-Sst bridge, imports the H13 model from `../2026-11-16/code/mechanism/phaseB/` |

Input paths are set at the top of each script, as in `../2026-11-16/code/mechanism/`.
