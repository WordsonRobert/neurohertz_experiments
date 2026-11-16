"""H18: is the AD high-frequency flattening a non-neural floor (R3)?
Per subject, P3/P4/Pz (CSD and average reference), linear power 20-65 Hz excluding 47-53 Hz:
   P(f) = A * f^(-chi) + F       (neural power law + flat floor), least squares in log space.
Compare chi (neural exponent), log A, log F between AD and CN; floor share of 32-40 Hz power; slope of the
neural part alone over 24-47 Hz; and 55-65 Hz power (floor proxy).
R3 predicts: AD neural exponent NOT flatter (or steeper), equal floor, AD 32-40 Hz closer to floor.
H* predicts: neural exponent itself flatter in AD (or beta-shoulder loss), not explained by a common floor.
"""
import glob, os, numpy as np, pandas as pd
from scipy.optimize import least_squares
from scipy.stats import mannwhitneyu
F = "/mnt/user-data/uploads/neurohertz2/classification/cache/ds004504/main/feat"
P = pd.read_csv("/home/claude/data/ds004504/participants.tsv", sep="\t").set_index("participant_id")
def g(a, b):
    s = np.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2)); return (a.mean()-b.mean())/s
rows = []
for fn in sorted(glob.glob(F + "/sub-*.npz")):
    s = os.path.basename(fn)[:7]; grp = P.loc[s, "Group"]
    if grp not in ("A", "C", "F"): continue
    z = np.load(fn); f = z["freqs"]; ch = list(z["ch_names"]); idx = [ch.index(c) for c in ["P3", "P4", "Pz"]]
    for ref in ("csd", "avg"):
        p = np.mean(10 ** z["logpsd_" + ref][idx], 0)
        m = (f >= 20) & (f <= 65) & ~((f >= 47) & (f <= 53))
        ff, pp = f[m], p[m]
        def res(v): return np.log10(10 ** v[0] * ff ** (-v[1]) + 10 ** v[2]) - np.log10(pp)
        best = None
        for chi0 in (0.5, 1.5, 3.0):
            v0 = [np.log10(pp[0]) + chi0 * np.log10(20), chi0, np.log10(pp[-1]) - 0.5]
            r = least_squares(res, v0, bounds=([-20, 0, -20], [20, 8, 20]))
            if best is None or r.cost < best.cost: best = r
        A, chi, Fl = best.x
        neural = lambda x: 10 ** A * x ** (-chi)
        k = (f >= 32) & (f <= 40); band = p[k].mean()
        fs = f[(f >= 24) & (f <= 47)]
        rows.append(dict(sub=s, group=grp, ref=ref, chi=chi, logA=A, logFloor=Fl,
                         floor_share_32_40=10 ** Fl / band, rms=np.sqrt(np.mean(best.fun ** 2)),
                         neural_slope_24_47=np.polyfit(np.log10(fs), np.log10(neural(fs)), 1)[0],
                         p55_65=np.log10(p[(f >= 55) & (f <= 65)].mean())))
D = pd.DataFrame(rows); D.to_csv("/home/claude/work/h18/floor_fits.csv", index=False)
for ref in ("csd", "avg"):
    d = D[D.ref == ref]; print(f"\n=== {ref}  (fit rms median {d.rms.median():.3f})")
    for c in ["chi", "neural_slope_24_47", "logA", "logFloor", "floor_share_32_40", "p55_65"]:
        a, b, ft = d[d.group == "A"][c], d[d.group == "C"][c], d[d.group == "F"][c]
        print(f"  {c:20s} AD {a.median():+.3f} CN {b.median():+.3f}  g(AD-CN)={g(a,b):+.2f} p={mannwhitneyu(a,b).pvalue:.3f} | FTD-CN g={g(ft,b):+.2f}")
