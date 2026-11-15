# Results · P09

## Main results
- **Freeze record** (2026-11-14T15:12:21Z):
    - config `218638ff…`, code `5ab5a4a7…`, analysis `023c6127…`, plan `a483b11d…`, metric selection `fb11eb00…`, method selection `c208d6d1…`, fingerprints `4a7fea34…`;
    - primary feature `burst_freq_sd`; simulation-selected `burst_freq_sd_z`;
    - **development unblindings before the freeze: 0**.
- **Ledger entries:**
    1. FROZEN (15:12:21);
    2. labels opened for the discovery analysis (15:12:22), the mechanism tests (15:13:44) and prediction (15:14:50);
    3. frozen model saved (16:36:06);
    4. labels opened for the ceiling check (16:36:07);
    5. ds006036 participant table opened to check IDs (2026-11-15 18:12:46).
- Every entry after the freeze carries the same config and code hashes as the freeze.

## Consequences
- H1–H6 were computed with code and settings fixed before any label was seen. They qualify as confirmatory under the plan.
- Everything run after the ledger's discovery entry (H7–H9 and the classification sweep) used already-opened labels, so it is exploratory.
