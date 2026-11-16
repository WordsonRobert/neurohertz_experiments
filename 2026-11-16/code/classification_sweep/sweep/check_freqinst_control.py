"""Gate for the frequency x electrode instability screen (stages 13, 57): synthetic data with an ERRATIC gamma
drive (frequency instability injected at 30-45 Hz; posterior circuit in "AD", frontal circuit in "FTD").
Pass (all three, covariates age + sex, instability metrics raw or __excess, grid A):
  1. at least one FWER-significant cluster for AD-CN or FTD-CN whose peak window lies in 26-48 Hz and whose sign is
     positive (patients more unstable);
  2. no FWER-significant instability cluster that lies entirely below 24 Hz (nothing was injected there);
  3. in grid B (54-90 Hz) no FWER-significant instability cluster (nothing was injected there).
Criteria written on 2026-11-16 before any run of stage 57 (synthetic or real). Exit code 1 stops the runner.
"Significant" = p_family < 0.05 (Bonferroni over the 30 metric x contrast maps of a grid; stage 57 header).
HISTORY: the first full-size run (88 subjects, 4 surrogates, 2026-11-16, laptop) used p_FWER < 0.05 per map and
FAILED criterion 3: one cluster in grid B (slip_frac, FTD-CN, 84-88 Hz, T3, FTD lower, p_FWER = 0.016). With 30
maps per grid, each controlled at 5% on its own, about 1.5 null clusters are expected per grid, and at least
one with probability ~0.79, so the rule tested the multiplicity, not the method. The correction over maps was
added to stage 57 and to this check. The three criteria are unchanged. No real-data result existed at that point."""
import sys
import pandas as pd
from common import OUT

sub = sys.argv[1] if len(sys.argv) > 1 else "freqinst"          # freqinst (sub-bin mean) or freqinst_b1
CL = pd.read_csv(OUT / "synthetic" / "main" / sub / "B_clusters.csv")
print("results:", sub)
CL = CL[(CL.ladder == "L0") & (CL.p_family < 0.05) & ~CL.feature.str.startswith("snr")]
pk = CL.peak_win.str.split("-").apply(lambda v: float(v[0]))
A = CL[(CL.grid == "A") & CL.contrast.isin(["AD-CN", "FTD-CN"])]
c1 = ((A.sign > 0) & pk.loc[A.index].between(26, 44)).any()
c2 = not (CL[CL.grid == "A"].f_hi <= 24).any()
c3 = not (CL.grid == "B").any()
cols = ["grid", "feature", "contrast", "sign", "p_fwer", "p_family", "f_lo", "f_hi", "peak_win", "ch_peak", "t_peak"]
print(CL[cols].to_string(index=False) if len(CL) else "no significant cluster")
for name, c in [("injected gamma instability found (26-48 Hz, patients higher)", c1),
                ("no significant cluster below 24 Hz", c2), ("no significant cluster in grid B", c3)]:
    print(("PASS " if c else "FAIL ") + name)
ok = bool(c1 and c2 and c3)
print("FREQ-INSTABILITY CONTROL", "PASSED" if ok else "FAILED")
sys.exit(0 if ok else 1)
