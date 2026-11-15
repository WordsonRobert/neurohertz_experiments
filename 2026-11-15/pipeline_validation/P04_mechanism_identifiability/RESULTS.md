# Results · P04

## Main results: recovery accuracy per mechanism

| Fingerprint family → data family | Cholinergic | Erratic drive | PV output | SST loss | Synapses onto PV | Tau silencing | Local vs input |
|---|---|---|---|---|---|---|---|
| rate → rate | 0.95 | 0.97 | 0.99 | 0.99 | 0.08 | 0.59 | 0.94 |
| cycle → cycle | 0.51 | 1.00 | 0.78 | 0.00 | 0.76 | 0.23 | 0.65 |
| rate → cycle | 0.00 | 0.01 | 0.01 | 0.14 | 0.41 | 0.32 | 0.31 |
| cycle → rate | 0.00 | 0.07 | 0.87 | 0.00 | 0.00 | 0.00 | 0.47 |

- Within a simulator family, most mechanisms are recovered. "Synapses onto PV" is the exception in the rate family (0.08).
- Across families, recovery falls to between 0.00 and 0.87 per mechanism (local vs input split: 0.31 and 0.47).
- In `separability.csv`, every pair of mechanisms is flagged separable within a family. The pairwise cosine similarities range from −0.46 to 0.88.

## Consequences
- A mechanism claim requires the two simulator families to agree. With the cross-family recovery above, that requirement is rarely met.
- This is why the mechanism analysis on real data (H6) was pre-specified to make a claim only when both families agree and identifiability is adequate.
