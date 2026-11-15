"""Gate: the sweep must recover the injected synthetic mechanism before any real-data result is interpreted.

Ground truth (scripts/00_make_synthetic_dataset.py): "AD" = gamma circuit changed in the POSTERIOR region,
"FTD" = the same change in the FRONTAL region, CN = baseline. Pass criteria:
  1. AD-CN: a FWER-significant periodic_csd cluster overlapping 30-48 Hz whose PEAK channel is posterior.
  2. FTD-CN: a FWER-significant periodic_csd cluster overlapping 30-48 Hz whose PEAK channel is frontal.
  (Changed on 2026-11-15 after the first pilot from "most cluster channels posterior": cluster extent spreads
  through channel adjacency, so the peak, not the extent, is the localization test.)
  3. The AD-CN 30-48 Hz change is attributed to the periodic part: no FWER-significant AD-CN fractal_csd
     cluster overlapping 30-48 Hz. (Replaced "no periodic cluster below 25 Hz" after the first pilot: the PV
     mechanism legitimately moves power from gamma into beta, so a beta cluster is a true effect.)
  HISTORY: the first full-size run (88 subjects, 2026-11-15, laptop) FAILED criterion 3 with IRASA as the split
  (AD-CN fractal cluster 32-41 Hz at O1/O2, p = 0.049). Diagnosis in the cloud on the pilot data: IRASA drags
  the injected beta increase into the 'fractal' estimate near 37 Hz (leak 0.32 of the periodic effect; wider
  resampling 0.59-0.66, narrower 1.08-2.80). specparam-knee leaked 0.03, so it became the primary split; the
  criteria themselves are unchanged. No real-data result existed when this was decided.
  2026-11-15 (user decision): criterion 3 is REPORTED, not blocking. The study asks about instability in any
  recognizable band, not gamma attribution specifically; with specparam-knee the 35-45 Hz gamma loss sits in the
  periodic part (t = -6.4 vs aperiodic t = 0.6 in the pilot), and the remaining flag was a 2.5-32 Hz aperiodic
  difference from the injected beta increase touching 32 Hz.
Exit code 1 (stops run_classification.sh) only if criterion 1 or 2 fails.
"""
import sys
import pandas as pd
from common import OUT

POST = {"P3", "Pz", "P4", "O1", "O2", "T5", "T6"}
FRONT = {"Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8"}
CL = pd.read_csv(OUT / "synthetic" / "main" / "freq" / "clusters.csv")
s = CL[(CL.p_fwer < 0.05) & (CL.family == "periodic_csd") & (CL.covariates == "age_sex")]
ok = True


def chans(r):
    return set(str(r.channels).split())


ad = s[(s.contrast == "AD-CN") & (s.f_hi >= 30) & (s.f_lo <= 48)]
c1 = any(r.ch_peak in POST for r in ad.itertuples())
ftd = s[(s.contrast == "FTD-CN") & (s.f_hi >= 30) & (s.f_lo <= 48)]
c2 = any(r.ch_peak in FRONT for r in ftd.itertuples())
fr = CL[(CL.p_fwer < 0.05) & (CL.family == "fractal_csd") & (CL.covariates == "age_sex")]
low = fr[(fr.contrast == "AD-CN") & (fr.f_hi >= 30) & (fr.f_lo <= 48)]
c3 = len(low) == 0
for name, c, info in [("AD-CN posterior gamma cluster", c1, ad), ("FTD-CN frontal gamma cluster", c2, ftd),
                      ("AD-CN gamma change not misattributed to the fractal part", c3, low)]:
    print(("PASS " if c else "FAIL ") + name)
    if len(info):
        print(info[["contrast", "sign", "f_lo", "f_hi", "f_peak", "ch_peak", "p_fwer", "channels"]].to_string(index=False))
    if name.startswith("AD-CN gamma change not misattributed"):
        if not c:
            print("WARNING (reported, not blocking): aperiodic cluster overlaps 30-48 Hz; see 35-45 Hz window in freq/window_35_45.csv")
        continue
    ok &= c
print("POSITIVE CONTROL", "PASSED" if ok else "FAILED")
sys.exit(0 if ok else 1)
