# H12 · What the posterior 32–40 Hz "excess" is made of

**Question.** H11 showed AD > CN at 32–40 Hz relative to a local background. Is absolute 32–40 Hz power higher in AD, or do the frequencies around it fall? Does the result depend on the pipeline?
**Type.** Exploratory (labels open). Follow-up to H11.
**When / where.** Cloud, 16 Nov 2026.

**What was run.** Posterior site: the mean of P3, P4 and Pz. Three spectrum sources:

| Source | Origin |
|---|---|
| CSD | your stage-10 spectra |
| average reference | your stage-10 spectra |
| public derivatives | ds004504 public derivatives (A1–A2 reference, 0.5–45 Hz filter, ASR, eye/jaw ICA) |

- **Absolute log power** in 16–23, 24–30, 32–40 and 42–47 Hz.
- **Local slope** over 24–47 Hz.
- **H11 flank-line bump**, using flanks at 24–30 and 42–47 Hz.
- **specparam periodic/aperiodic split** on the CSD spectra.
- **Per-subject agreement** across pipelines (Spearman).

**Code.** `../../code/mechanism/reconcile/flanks.py` (public files) and `reconcile.py` (stage-10 spectra).

| Output in `results/` | Content |
|---|---|
| `H12_reconcile.txt` | Hedges g and Mann–Whitney p for every measure × pipeline; per-subject agreement; periodic/aperiodic split |
| `H12_derivatives_band_powers.csv` | Per-subject measures from the public files |
