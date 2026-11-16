# H14 · Driven (photic) responses in the same people, and the mechanism test

**Question.** Do flicker-driven responses, recorded right after the eyes-closed rest in the same 65 AD/CN subjects (ds006036), separate the two mechanisms left by H13?
- **Slow-loop loss:** predicts a selective drop at 15–20 Hz.
- **Lower excitatory gain:** predicts a broad drop.

**Type.** Exploratory.
**When / where.** Cloud, 16 Nov 2026. Raw files (70 Hz hardware low-pass), average reference. Each subject's own `.fdt` is read (see P13).

**What was run.**
- **Blocks:** found from the per-flash `Photo/HV mark` events.
- **Epochs:** 2-s epochs starting on a flash, posterior channels O1 O2 P3 P4 Pz.
- **Per drive frequency and harmonic up to 47 Hz:**
    - evoked power (complex mean);
    - noise (±1–2 Hz);
    - SNR;
    - inter-trial coherence.
- **Reliable cells:** CN median SNR ≥ 3 dB.
- **Group difference:** AD − CN in dB, bootstrap SE.
- **Mechanism test:** prediction 10·log10(|H_mech(f)|² / |H_base(f)|²) at the k fitted to **rest** (no refit), plus one free offset, scored only at f ≥ 14 Hz, the model's calibrated range.
- **Within-person link:** resting band power (ds004504) vs driven power (ds006036).

**Code.** `../../code/mechanism/phaseC/photic.py`, `test.py`

| Output in `results/` | Content |
|---|---|
| `photic_responses.csv` | Per subject × block × drive × harmonic |
| `photic_group_delta.csv` | AD − CN per reliable cell |
| `photic_mechanism_chi2.csv` | χ² per mechanism × calibration |
| `H14_photic_test.txt` | Full output, including the restricted-range test and the within-person correlations |
