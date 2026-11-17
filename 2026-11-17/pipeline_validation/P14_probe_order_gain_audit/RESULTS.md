# Results · P14

## Main results
**1. The controls pass.**
- α = 0 gives G = 0 in every setting.
- Moving the tissue data in the sequence gives |G| ≤ 2 × 10⁻¹⁵. Static data commute, as they must.
- The commuting surrogate with only the final readout gives G = 0 exactly.

**2. H17's G values were inflated by the finite-difference step.** In the local limit (h → 0):

| α | G reported in H17 (h = 0.05) | Local G (h = 0.001) |
|---|---|---|
| 0.05 | 0.15 | 0.15 |
| 0.15 | 0.45 | **0.36** |
| 0.30 | 0.61 | **0.27** |

G does not grow steadily with α.

**3. Most of G is the readout schedule, not non-commutativity** (local limit, all readouts recorded):

| α | G | Commuting probes | Non-commuting (bracket) term | Readout share |
|---|---|---|---|---|
| 0.05 | 0.151 | 0.143 | 0.009 | 94% |
| 0.15 | 0.361 | 0.285 | 0.075 | 79% |
| 0.30 | 0.267 | 0.332 | **−0.065** | > 100% |

- The non-commuting term is real: the final adapted state differs between orders by up to 0.015 (Δa) and depends on θ.
- That term is small (≤ 0.08 nats) and changes sign with α.

**4. Order does not restore identifiability in this model.**
- With only the final resting readout, the smallest eigenvalue of F stays between 10⁻⁸ and 10⁻⁵ in both orders and at every α. That is as unidentifiable as rest alone (8.5 × 10⁻⁵).
- Order only reshuffles information among directions that are already identifiable.
- The gain H17 attributed to the perturbation sequence comes from recording the driven responses, that is, from *adding probes*, not from their *order*.

**5. Mixing orders is useless here.** Tr(F_AB⁻¹ F_BA) is about 2.65, below d = 3. The best labelled mixture is pure AB, with gain 0.

## Consequences
- **Retract the H17 claim** "probe order is a design variable … mechanism identifiability requires non-commuting probes." It is not supported by the H17 model.
- **What stands:**
    - rest is not injective;
    - tissue + driven responses restore identifiability. This is multi-experiment identifiability, as in Hashemi et al. 2024, *MLST*.
- **What does not stand:** any identifiability gain from probe order or non-commutativity in this model.
- **Corrected H17 figures:**
    - The smallest eigenvalue rises 27× over tissue alone (6.4 / 0.24) and 213× over the perturbation sequence alone (6.4 / 0.030), not "about 400×".
    - The order effect is 0.15 / 0.36 / 0.27 nats, of which 0.01 / 0.08 / −0.07 comes from non-commutativity.
- **Why the bracket is weak.** The adaptation acts on one parameter (gE), and every probe moves it the same way. The Lie bracket of two probes that share one scalar direction is small. A genuine order effect needs probes whose state updates act along different, mechanism-dependent directions. One example: a GABAergic drug followed by flicker, against flicker followed by the drug.
- **Method lesson.** Report the decomposition (commuting-surrogate G, bracket term, local step) for every order claim. A raw log det difference is not evidence of non-commutativity.
- **Limits:**
    - one model family;
    - the adaptation form and α are assumed;
    - this audits the model, not the brain, so it cannot rule out non-commutativity in real data.
