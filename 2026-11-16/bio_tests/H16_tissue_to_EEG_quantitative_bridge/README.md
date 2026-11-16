# H16 · Does the tissue-measured L2/3 loss predict the EEG effect sizes? (no fitting to EEG)

**Question.** If the AnG L2/3 IT loss from H15 is put into the H13 circuit as a loss of excitatory output, does it predict the AD − CN resting features from H12/H13, in sign and size?
**Type.** Cross-modal prediction. The only free parameter is the global offset on absolute bands.
**When / where.** Cloud, 16 Nov 2026.

**What was run.**
- **Loss from tissue:** the L2/3 IT share in high-ADNC vs Not-AD/Low donors, bootstrapped over donors (1000×).
    - L2/3 loss = 1 − ratio;
    - total excitatory loss = L2/3 loss × the low-pathology L2/3 share.
- **Two ways the loss enters the circuit:**

| Variant | Change |
|---|---|
| global | all pyramidal outputs (wEE, wFE, wSE) × (1 − total loss) |
| superficial | wEE and the drive into the slow/beta loop (wSE) × (1 − L2/3 loss) |

- **Prediction:** 200 tissue draws × 12 calibrations; predicted Δfeatures compared with the observed values (χ²).

**Code.** `../../code/mechanism/bridge.py`

| Output in `results/` | Content |
|---|---|
| `H16_bridge.txt` | Tissue loss with CI; predicted vs observed per feature; χ²; sign agreement |
