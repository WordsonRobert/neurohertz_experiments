"""Gate for the band-instability stages (12, 55): synthetic data in which "AD" (posterior circuit) and "FTD"
(frontal circuit) have an ERRATIC gamma drive (injected frequency instability; erratic_drive mechanism).
Pass (all three):
  1. for AD-CN and for FTD-CN, the top-ranked instability measure (raw or excess, age + sex) is a GAMMA measure
     (right band) and is larger in the patient group (more unstable);
  2. at least one of the two contrasts is family-wise significant (maxT p < 0.05);
  3. no non-gamma measure is family-wise significant (nothing was injected elsewhere).
Criterion set on 2026-11-15 after a cloud pilot at n = 10/10/8 with 2 surrogates (FTD-CN p = 0.003; AD-CN top
measure gamma, t = 3.1, p = 0.28: underpowered at that size), BEFORE the full-size control (29/36/23, 10 surrogates).
Exit code 1 stops run_classification.sh."""
import sys
import pandas as pd
from common import OUT

D = pd.read_csv(OUT / "synthetic" / "main" / "bandinst" / "D_group_tests.csv")
D = D[(D.ladder == "L0") & D.family.isin(["raw", "excess"])]
ok = True
for con in ("AD-CN", "FTD-CN"):
    g = D[D.contrast == con].sort_values("p_maxT")
    top = g.iloc[0]
    c1 = top.feature.startswith("gamma|") and top.t > 0
    print(f"{con}: top {top.feature} t = {top.t:.2f} p_maxT = {top.p_maxT:.4f} -> {'ok' if c1 else 'WRONG'}")
    ok &= bool(c1)
sig = D[(D.contrast.isin(["AD-CN", "FTD-CN"])) & (D.p_maxT < 0.05)]
c2 = len(sig[sig.feature.str.startswith("gamma|")]) > 0
c3 = len(sig[~sig.feature.str.startswith("gamma|")]) == 0
print("family-wise significant gamma measure:", c2, "| no spurious other-band measure:", c3)
ok &= c2 and c3
print("INSTABILITY CONTROL", "PASSED" if ok else "FAILED")
sys.exit(0 if ok else 1)
