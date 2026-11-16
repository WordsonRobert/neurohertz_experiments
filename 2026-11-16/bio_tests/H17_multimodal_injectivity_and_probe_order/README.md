# H17 · Is the map from mechanisms to characterizations injective, and does probe order matter?

**Question.**
1. **Injectivity.** Over the candidate set B, is b ↦ (signature over the characterization set Φ) injective using resting EEG alone? Using rest + photic + tissue?
2. **Probe order.** For perturbation probes whose state update depends on the mechanism, does the **order** of probes change identifiability? In other words, do the probes fail to commute?

**Type.** Theory and design, computed with the calibrated H13 circuit and observed SEs. Exploratory.
**When / where.** Cloud, 17 Nov 2026.

**What was run.**
- **Injectivity** (`framework/injectivity.py`).
    - **B:** 8 signed mechanisms: M1± gain, M2, M3, M4, M5± and tissue-scaled L2/3 loss.
    - **Φ:**

| Modality | Characterizations | Source of the signature |
|---|---|---|
| REST (6) | bands relative to their mean, slope, bump | circuit model |
| PHOTIC (1) | 20 Hz minus 15 Hz driven change | circuit model |
| TISSUE (3) | L2/3 IT, SST and PV shares | stated mapping assumption: a cell-loss mechanism lowers its own class's share; functional mechanisms change none |

    - **Signature:** each mechanism is scaled to the same whitened effect size as the observed contrast. Each characterization is coded +1 / 0 / −1, using a 2-SE threshold from the observed data.
    - **Outputs:**
        - the number of distinct signatures per modality combination;
        - which mechanisms match the observed signature;
        - cosines between mechanism directions in whitened REST space;
        - the singular values.
- **Probe order** (`framework/probe_order.py`).
    - **Unknowns:** θ = severities of the three candidates that rest can't separate: M4, M1 gain ↓, L2/3 loss.
    - **Perturbation probes** (drive at 20 or 40 Hz): an activity-dependent adaptation a = α·R(θ)/R(θ₀) scales pyramidal gain by (1 − a). Because R depends on θ, the state update U depends on the mechanism.
    - **Static probes** (tissue): U = identity.
    - **Fisher information:** F = Jᵀ Σ⁻¹ J for 8 probe sequences, with α ∈ {0.05, 0.15, 0.30}. α is an assumption.
    - **Noise:** rest = ds004504 bootstrap SEs; drive = 1.2 dB (H14); tissue = SEA-AD SE.

**Interpretation of "quantum".** The probes are modelled as operators on a state. Static readouts commute (U = id). State-changing perturbations generally do not, so the order of measurement is part of the design. This is the non-commutative structure that quantum-probability models formalise. No claim is made about quantum physics in the brain. A quantum-probability test on order data (QQ equality, Wang & Busemeyer 2013) needs counterbalanced probe orders, which no available dataset has.

| Output in `results/` | Content |
|---|---|
| `signatures.csv`, `injectivity.csv`, `observed_signature.json`, `H17_injectivity.txt` | Injectivity analysis |
| `probe_order.csv`, `H17_probe_order.txt` | Fisher information by sequence and α; demonstration of order dependence |
