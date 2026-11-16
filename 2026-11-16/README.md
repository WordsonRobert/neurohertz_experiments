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
| pending | Laptop | `run_freq_instability_b1.sh`: synthetic check and ds004504 with b1 (about 15 min, no new feature extraction) | `P11`, `bio_tests/H10` |

## Map

| ID | Kind | Question |
|---|---|---|
| P11 | Pipeline validation | Does the frequency × electrode screen find an injected gamma instability at the right frequency and place, and nothing elsewhere? |
| H10 | Bio test, exploratory | Does the instability of any frequency window at any electrode separate AD, beyond slowing and 1/f? Which cells are reliable and show no group difference? |
