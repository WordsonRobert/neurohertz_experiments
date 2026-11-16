# H13 · Which circuit change produces the posterior phenotype?

**Question.** A circuit calibrated to the CN posterior spectrum is changed one mechanism at a time. Which change reproduces the AD − CN difference vector from H12?
**Type.** Exploratory, model-based.
**When / where.** Cloud, 16 Nov 2026. This replaces the P04/P12 simulators for this question.
- In P04 the signal was renormalized to unit variance, which erased amplitude changes.
- In P04 the 1/f slope was independent of mechanism, so it could not respond.

**Model** (`code/mechanism/phaseB/model.py`). One posterior node, linearised.

| Population | Role | Time constant |
|---|---|---|
| E | pyramidal | 1–15 ms |
| F | fast PV-type inhibition, GABA_A | 3–15 ms |
| S | slow dendritic inhibition | 12–60 ms |

- **Synapses:** AMPA gating on top of these.
- **EEG:** the net synaptic current onto E. Its spectrum is closed-form, S(f) = |C (2πif I − A)⁻¹ B|² σ². The aperiodic part comes from the circuit; no 1/f is added and nothing is renormalized.

**Calibration.**
- Fitted to the CN mean CSD spectrum at P3/P4/Pz, 14–47 Hz.
- 60 random starts; the calibrations within 1.5× the best RMS were kept (12).

**Mechanisms** (one knob k each; signed in H17):

| Knob | Change |
|---|---|
| M1 | gain ↑ |
| M2 | PV→E inhibition ↓ |
| M3 | recurrent E ↑ |
| M4 | slow-loop inhibition ↓ |
| M5 | input E/I ↑ |

**Target.**
- Features: Δ absolute log power in 16–23, 24–30, 32–40 and 42–47 Hz, the 24–47 Hz slope, and the H11 bump.
- Uncertainty: bootstrap SE over subjects.
- One free global offset on absolute bands (scalp attenuation).
- Score: χ² over the six features.
- Fits: single knobs and pairs, k ∈ [−1.5, 1.5].

**Command.** `python code/mechanism/phaseB/run.py` (input paths at the top of the script)

| Output in `results/` | Content |
|---|---|
| `target_delta.csv` | Observed AD − CN features and SEs |
| `baseline_params.json`, `good_calibrations.json` | Calibrated circuits |
| `mechanism_fits.csv` | Every single/pair fit: k, χ², predicted features |
| `robustness.csv` | Single-knob fits for each of the 12 calibrations |
| `jacobian.csv` | ∂features/∂k at baseline |
| `H13_run_log.txt` | Full log |
