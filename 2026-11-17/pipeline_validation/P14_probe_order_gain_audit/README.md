# P14 · Audit of the probe-order gain G reported in H17

**Question.** H17 reported that the same probes in a different order carry different information. The log-determinant difference was 0.15 / 0.45 / 0.61 at α = 0.05 / 0.15 / 0.30, and H17 read this as non-commutativity. A non-zero G has three possible sources. Which one produced these numbers?
1. **Readout schedule.** Each probe is read at a different accumulated state, even when the state updates themselves commute.
2. **True non-commutativity.** The state update depends on the current state, so the final state depends on the order.
3. **Approximation.** The finite-difference step, or static data treated as a probe.

**Why.** The 17 Nov literature review (cross-field report on probe order as an identifiability resource) showed the following. G is exactly 0 for static data and for reset linear time-invariant systems. G is non-zero for commuting probes whenever readouts are cumulative. The order term attributable to non-commutativity is, to leading order, the θ-derivative of the probes' Lie bracket. So a non-zero G does not by itself show non-commutativity.
**Type.** Pipeline validation. Model only, no labels.
**When / where.** Cloud, 17 Nov 2026. It reuses the H17 model (`../../../2026-11-16/code/mechanism/framework/probe_order.py`) and the 12 Phase B calibrations.

**What was run.**
- **Commuting surrogate.** The adaptation increment is computed on the unadapted circuit, so the increments commute and the final state does not depend on order. The readouts are unchanged. Then G_bracket = G_full − G_commute.
- **Readout variants:**
    - every probe recorded (as in H17);
    - only the final rest block recorded, with the drives acting purely as state updates.
- **Step size.** h = 0.05 (H17's value), 0.01, 0.003 and 0.001, to obtain the local Fisher limit.
- **Controls:**
    - α = 0;
    - tissue moved from the end of the sequence to the start, which must give G = 0 exactly;
    - the final adapted state compared between the two orders.
- **Design check.** Labelled mixture of the two orders. Mixing beats pure AB under D-optimality iff Tr(F_AB⁻¹ F_BA) > d.

**Code.** `../../code/mechanism/audit/order_audit.py` and `limit_check.py`. Paths are set at the top, as in H17.

| Output in `results/` | Content |
|---|---|
| `G_decomposition.csv` | G by α × mode × readout × step, with quartiles over calibrations and the mixture trace |
| `G_limit.csv` | Local limit (h → 0): full, commuting and bracket term |
| `controls.json` | Tissue-permutation G, mixture optimum per calibration |
| `audit_log.txt` | All printed numbers |
