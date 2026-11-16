# H18 · The AD high-frequency flattening is not a constant noise floor

**Question.** A fixed non-neural floor (amplifier, residual line or muscle) under a lower-power AD spectrum would flatten a 24–47 Hz fit and leave absolute 32–40 Hz unchanged, which is the H12 pattern, without any circuit change. Does a floor explain the flattening?
**Rival tested.** R3, raised by the 17 Nov literature check (van Nifterick 2023 flag environmental noise in the gamma-range exponent).
**Type.** Exploratory.
**When / where.** Cloud, 17 Nov 2026. Stage-10 spectra, P3/P4/Pz, CSD and average reference.

**What was run.**
- **Model, per subject:** P(f) = A·f^(−χ) + F (a neural power law plus a flat floor), fitted in log space over 20–65 Hz, excluding 47–53 Hz.
- **Group comparisons** (AD vs CN and FTD vs CN):
    - χ;
    - log A;
    - log F;
    - the floor's share of 32–40 Hz power;
    - the 24–47 Hz slope of the neural part alone;
    - 55–65 Hz power.
- **Predictions:**

| Account | Predicts |
|---|---|
| R3 (floor) | the neural exponent is not flatter in AD; the floor is the same, and AD's 32–40 Hz sits closer to the floor |
| H\* | the neural exponent itself is flatter |

**Code.** `../../code/mechanism/floor_test.py`

| Output in `results/` | Content |
|---|---|
| `H18_floor_test.txt` | Medians, Hedges g and Mann–Whitney p for each parameter, both references |
| `floor_fits.csv` | Per-subject fits |
