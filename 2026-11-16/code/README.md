# Code added or changed on 16 Nov 2026

Everything else is unchanged from `../../2026-11-15/code/classification_sweep/`. Copy these files over that folder to reproduce.

| File | Status | Purpose |
|---|---|---|
| `classification_sweep/sweep/13_freq_instability.py` | new | Instability in 4-Hz windows every 2 Hz, 2–90 Hz, every electrode (no labels) |
| `classification_sweep/sweep/57_freq_instability_analysis.py` | new; correction over maps added after run 1 | Reliability, cluster tests, reference cells, prediction |
| `classification_sweep/sweep/check_freqinst_control.py` | new; uses p_family after run 1 (history in its header) | Synthetic gate for the screen |
| `classification_sweep/run_freq_instability.sh` | new | Runner: tests → synthetic control → ds004504 |
| `classification_sweep/tests/test_sweep.py` | one test added | Window layout never touches the 50 Hz notch |
