# P05 · Synthetic positive controls for the frozen pipeline

**Question.** Synthetic EEG was given a known circuit mechanism: in the posterior circuit for "AD" and in the frontal circuit for "FTD", with group sizes 29 CN / 36 AD / 23 FTD and severity k = 0.75. Do the frozen mechanism tests recover it?
**Type.** Pipeline validation. Synthetic data with ground truth.
**When / where.** Final run on the laptop, 14 Nov 2026.

**What was run.** Two injected mechanisms. For each, a synthetic dataset was generated, the frozen features were extracted (without ICA), and the pre-registered mechanism tests M01–M16 were run. These are the same tests used on real data in H6.
- `synapses_onto_pv`: loss of excitatory synapses onto PV interneurons.
- `erratic_drive`: an irregular excitatory drive, which injects gamma frequency instability.

**Commands.**
```bash
python scripts/00_make_synthetic_dataset.py --mechanism <mechanism> --k 0.75 --n 29 36 23 --out results/synthetic_<mechanism>
python scripts/01_extract_features.py --dataset synthetic --variant synth-<mechanism> --no-ica --jobs 8
python scripts/14_mechanism_tests.py --dataset synthetic --variant synth-<mechanism>
```
**Code.** `../../code/neurohertz_v2_frozen/scripts/00_make_synthetic_dataset.py`, `14_mechanism_tests.py`

| Output in `results/<mechanism>/` | Content |
|---|---|
| `report.md` | Full mechanism report: presence, tests, scorecards, fingerprint comparison |
| `tests.csv` | M01–M16 effect, CI, p, Holm-corrected p |
| `presence.csv` | Share of subjects with a detectable gamma oscillation |
| `scorecard.csv`, `sensitivity.csv`, `fingerprint_comparison.json` | Theory scorecards, sensitivity and fingerprint matching |
| `00_synth_*.log`, `01_synth_*.log` | Generation and extraction logs |
