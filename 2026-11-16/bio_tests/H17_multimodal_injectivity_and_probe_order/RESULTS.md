# Results · H17

## Main results
**Injectivity (8 mechanisms).**

| Characterization set | Distinct signatures | Matching the observed |
|---|---|---|
| REST | 5 | none exactly |
| PHOTIC | 3 | uninformative |
| TISSUE | 3 | M1− (gain ↓) and L2/3 loss |
| REST + TISSUE | 6 | — |
| REST + PHOTIC + TISSUE | 7 | — |

- **Remaining collision:** M2 (PV→E inhibition ↓) and M5+ (input E/I ↑). Both are excitation-up, and the data reject both.
- **REST direction space:** singular values 2.74, 0.69, 0.18, then ≈ 0. Rest effectively spans about 2–3 dimensions.
- **Cosine with the observed AD − CN direction:**

| Mechanism | Cosine |
|---|---|
| L2/3 loss | **0.97** |
| M4 | 0.94 |
| M1 gain ↓ | 0.93 |
| M5− | 0.76 |
| M2, M3, M5+, M1+ | −0.62 to −0.92 (opposite) |

- **Rest-indistinguishable pairs** (cosine ≥ 0.98): L2/3 loss, M4 and M1↓.

**Probe order** (median over 12 calibrations).

| Sequence | min eigenvalue of F | log det F | CRLB M4 / M1↓ / L2/3 (α = 0.15) |
|---|---|---|---|
| rest | 0 | −4.4 | 17 / 47 / 72 (not identifiable) |
| rest → drive20 (ds006036 order) | 0.015 | 3.37 | 0.94 / 3.2 / 7.5 |
| drive20 → rest | 0.012 | 3.11 | 1.06 / 3.6 / 8.5 |
| rest → drive40 → rest | 0.030 | 4.69 | 0.63 / 2.2 / 5.3 |
| rest → drive20 → drive40 → rest | 0.034 | **5.28** | 0.59 / 2.1 / 5.0 |
| rest → drive40 → drive20 → rest | 0.031 | **4.83** | 0.62 / 2.2 / 5.2 |
| rest + tissue (static) | 0.24 | 7.16 | 0.95 / 1.8 / 0.23 |
| rest → drive40 → rest + tissue | **6.4** | **10.98** | **0.18 / 0.35 / 0.23** |

- **Order effect grows with adaptation strength** (same probes, different order):

| α | log det difference |
|---|---|
| 0.05 | 0.15 |
| 0.15 | 0.45 |
| 0.30 | 0.61 |

- **Non-commutativity is explicit:** resting features measured after a 40 Hz block differ from those measured before it. The slope changes by −0.14 at θ = 0.4 and α = 0.15. The driven response itself is identical.

## Consequences
- **Rest alone is not injective** on the plausible mechanisms. The three survivors (L2/3 loss, slow-loop loss, lower gain) are indistinguishable at rest.
- **Multimodal characterization restores identifiability.**
    - Tissue (static, commuting) pins down the L2/3 component.
    - A perturbation sequence (non-commuting) separates slow-loop loss from lower gain.
    - Together, all three become estimable, with the smallest eigenvalue up about 400× compared with either source alone.
- **Probe order is a design variable.** With activity-dependent state change, the same probes in a different order carry different information. The ds006036 order (rest, then flicker) is not the best available one. This supports the claim: mechanism identifiability requires non-commuting probes, and probe order is part of the experimental design.
- **Limits:**
    - α and the adaptation form are assumptions;
    - the tissue map is assumed, not modelled;
    - these are design-level results until counterbalanced probe-order data exist.
