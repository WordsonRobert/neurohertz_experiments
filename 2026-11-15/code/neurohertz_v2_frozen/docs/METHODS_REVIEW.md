# Methods review: short version

Full review with evidence and sources: Claude Doc "NeuroHertz v2: methods review and tool audit"
(https://claude.ai/artifact/1BUYtnoLGMZkoGcad1yNp2).

## Rules

- No method is chosen by how well it separates AD from controls. Choices come from published
  head-to-head evidence, label-free tests (simulation, split-half ICC, EMG coupling), or nested CV.
- Interpretability: every option outputs a named physical quantity, and the reported model is linear
  (or an EBM with one shape curve per feature). TabPFN and Riemannian models are ceilings only.

## Verdicts

| Stage | Verdict | In code |
|---|---|---|
| Filters, notch | Keep | - |
| Bad channels, reference | Change + ablate | PREP correlation; avg / CSD / REST after epoch rejection; `csd_roi` region |
| Muscle, epochs | Ablate | BSS-CCA + spectral slope; autoreject vs MAD |
| 1/f background | Change + ablate | specparam 3-30 Hz; power law + floor (`gamma_above_floor`); IRASA |
| Instantaneous frequency | Change + ablate | Cohen multi-window median; SST; VMD (fixed: K = 3 on a 22-58 Hz pre-filtered signal, gamma mode = most in-band power) |
| Surrogates | Fix | endpoint-matched chunks, seam trimming, `surr_spectral_mismatch`; chunk length 15/30/60 s |
| Statistics | Change | BCa CI for Hedges g; specification curve + joint permutation test |
| Classifier | Nested | LR-L2 / LR-EN / linear SVM / EBM in inner CV; ceilings in 09 |
| Across datasets | Keep | frozen model, unharmonised; harmonised = secondary |

## Ablation dimensions (config `ablations`)

| Dimension | Options (primary first) | Decided by | Judged on |
|---|---|---|---|
| reference | average, csd, rest | ICC >= 0.6, then min EMG coupling | primary metric |
| muscle | none, bss_cca | same | primary metric |
| epochs | mad, autoreject | same | primary metric |
| aperiodic | specparam, irasa | same | aperiodic_exponent |
| estimator | hilbert, sst, vmd | simulation score, then ICC | primary metric |
| median | multi, single | same | primary metric |
| surr_chunk | 30, 15, 60 s | same | burst_freq_sd_z |

Specification curve grid: reference x muscle x estimator x median = 36 pipelines.

Not yet implemented: bycycle estimator, 1/f-relative burst thresholds, ComBat secondary analysis.


## Estimator bugs found during the ds004504 ablation run (fixed before any selection)

- **SST**: ssqueezepy thresholds coefficients in absolute units. EEG in volts (~1e-6) left 80-96% of the
  in-band ridge at exactly zero, and 7 of 83 subjects crashed. Fix: SST is computed on the unit-SD signal.
- **VMD**: vmdpy's convergence tolerance is absolute. On EEG in volts it stopped after one iteration with
  all-zero modes (59 of 83 subjects crashed; the other 24 were not valid either). Fix: unit-SD input.
  With 8 modes on broadband EEG the "gamma" mode then sat near 48 Hz, so the fixed design became 3 modes
  (flank / gamma / flank) on a 22-58 Hz pre-filtered signal, gamma mode = most power inside 30-45 Hz.
- Both are label-blind implementation fixes; regression test `test_if_estimators_scale_invariant`.
  The estimator-sst and estimator-vmd ablation variants were re-extracted with the fixed code.

## Final method selection (label-free, 2026-11-14)

Full record: `registry/method_selection.json` (hashed by `03_freeze.py`).

- One-at-a-time selection (`11_select_methods.py`): no option reached split-half ICC >= 0.6 on the primary metric,
  so a second, pre-stated step tested the two candidate COMBINED pipelines.
- Rule (stated before the combined runs): primary = burst-to-burst gamma frequency variability (`burst_freq_sd`,
  Hilbert) adjusted for age, sex and 1/f exponent; pipeline = combination with full-length ICC >= 0.6 and EMG
  coupling < 0.2.
- Result: CSD + BSS-CCA + autoreject + single median filter: full-length ICC 0.66 (bootstrap 95% CI 0.46-0.79), EMG
  coupling 0.09 -> FINAL. REST + BSS-CCA + autoreject: 0.53 -> rejected.
- Why not the simulation's pick (`burst_freq_sd_z`): its real-data split-half ICC is about 0 in every pipeline.
  The raw metric's main nuisance in simulation is the 1/f slope; it is handled by the 1/f-exponent covariate
  (ICC 0.98). Freeze with `--override-reason` (text in README).
- Why not IF standard deviation / cycle CV: reliable (~0.75) but ~20x more sensitive to how bursty gamma is than to
  frequency instability in simulation.
