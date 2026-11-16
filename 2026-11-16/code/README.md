# Code added or changed on 16 Nov 2026

Everything else is unchanged from `../../2026-11-15/code/classification_sweep/`. Copy these files over that folder to reproduce.

| File | Status | Purpose |
|---|---|---|
| `classification_sweep/sweep/13_freq_instability.py` | new | Instability in 4-Hz windows every 2 Hz, 2–90 Hz, every electrode (no labels) |
| `classification_sweep/sweep/57_freq_instability_analysis.py` | new; correction over maps added after run 1; `--subbin b1` added after run 2 | Reliability, cluster tests, reference cells, prediction |
| `classification_sweep/sweep/check_freqinst_control.py` | new; uses p_family after run 1 (history in its header); takes the results folder as an argument | Synthetic gate for the screen |
| `classification_sweep/run_freq_instability_b1.sh` | new | Re-analysis with the low-SNR sub-bin: synthetic check, then ds004504 |
| `classification_sweep/run_freq_instability.sh` | new | Runner: tests → synthetic control → ds004504 |
| `classification_sweep/tests/test_sweep.py` | one test added | Window layout never touches the 50 Hz notch |
| `classification_sweep/explore/02_local_aperiodic_check.py` | new | H11: local-background test of the posterior 32–40 Hz excess |
| `fisher/fisher_identifiability.py` | new | P12: Jacobian, Fisher information and Cramér–Rao bounds from P04's `sim_features.csv` |
| `mechanism/reconcile/flanks.py`, `reconcile.py` | new | H12: band powers, local slope and bump across pipelines; periodic/aperiodic split |
| `mechanism/phaseB/model.py`, `run.py` | new | H13: linearised E/PV/slow-inhibition circuit, closed-form spectrum, calibration to CN, mechanism fits, robustness |
| `mechanism/phaseC/photic.py`, `test.py` | new | H14 + P13: ds006036 driven responses (own-file reader), mechanism test |
| `mechanism/tissue/seaad_celltypes.py`, `seaad_regions_tau.py` | new | H15: SEA-AD cell-type shares vs pathology, region comparison, Aβ vs pTau |
| `mechanism/bridge.py` | new | H16: tissue-measured L2/3 loss → circuit → predicted EEG |
| `mechanism/framework/injectivity.py`, `probe_order.py` | new | H17: multimodal signatures, injectivity, probe-order Fisher information |

The `mechanism/` scripts read input paths set at the top of each file (cloud paths: `/home/claude/data/...` for the OpenNeuro and SEA-AD downloads, `/mnt/user-data/uploads/neurohertz2/...` for the stage-10 spectra copied from the laptop). Change those lines to rerun elsewhere.
