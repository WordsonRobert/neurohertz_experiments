# Results · P05

## Main results

**Erratic drive (injected frequency instability):**
- Gamma presence: 100% in every group.
- **M07** (cycle-scale jitter beyond noise): effect 0.98, Holm p = 0.006.
- **M08** (1–10 s wander beyond noise): effect 1.15, Holm p = 0.003.
- **M01** (the primary metric, `burst_freq_sd`): effect 0.27, p = 0.25, Holm p = 1.
- Fingerprint comparison: best single match `erratic_drive` (rate family) and `sst_loss` (cycle family). First-split claim: none.

**Synapses onto PV:**
- Gamma presence: 100%.
- **M03** (FTD vs AD frontally at matched MMSE): effect −0.90, Holm p = 0.003.
- All other tests: Holm p = 1.
- Fingerprint comparison: best single match `nav11_pv_output` (rate) and `sst_loss` (cycle). First-split claim: none.

## Consequences
- The jitter-specific tests (M07, M08) detect an injected frequency instability at these group sizes. The primary metric `burst_freq_sd` does not.
- A null result for `burst_freq_sd` on real data (H1) is therefore compatible with an instability of this size being present.
- The fingerprint step did not name the injected mechanism in either control. This is consistent with the cross-family identifiability in P04.
