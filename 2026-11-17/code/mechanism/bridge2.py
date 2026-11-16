"""H19b: combined tissue -> EEG bridge. AnG losses measured in SEA-AD (high ADNC vs Not AD/Low, donor bootstrap):
  L2/3 IT loss  -> all pyramidal outputs x (1 - L2/3 share loss * low-pathology L2/3 share)      (as H16 global)
  vulnerable-Sst loss -> slow-loop output wES x (1 - fraction of all Sst neurons lost)
No fitting to EEG; one global offset. Compare L2/3-only, Sst-only, combined."""
import json, sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/work/phaseB"); sys.path.insert(0, "/home/claude/work"); sys.path.insert(0, "/home/claude/work/h19")
import model as M
from bridge import features, FEATS
import importlib.util
spec = importlib.util.spec_from_file_location("sst", "/home/claude/work/h19/sst_supertypes.py")
J = np.load("/home/claude/work/phaseB/out/jacobian.npz", allow_pickle=True); delta, se = J["delta"], J["se"]
cals = json.load(open("/home/claude/work/phaseB/out/good_calibrations.json")); fq = np.arange(2, 50.01, 0.5)
OFF = np.array([1, 1, 1, 1, 0, 0], float)
# donor table for AnG with ADNC
D = "/home/claude/data/seaad"
X = pd.read_csv(f"{D}/AnG.csv", usecols=["Donor ID", "Class", "Subclass", "Supertype", "Overall AD neuropathological Change", "Neurotypical reference"], low_memory=False)
X = X[~X["Neurotypical reference"].astype(str).str.lower().eq("true")]
vul = ['Sst_2', 'Sst_23', 'Sst_20', 'Sst_3', 'Sst_22', 'Sst_11', 'Sst_25']
G = X[X.Class == "Neuronal: GABAergic"]; E = X[X.Class == "Neuronal: Glutamatergic"]
T = pd.DataFrame({"adnc": X.groupby("Donor ID")["Overall AD neuropathological Change"].first(),
                  "l23": E[E.Subclass == "L2/3 IT"].groupby("Donor ID").size() / E.groupby("Donor ID").size(),
                  "sstv": G[G.Supertype.isin(vul)].groupby("Donor ID").size() / G.groupby("Donor ID").size(),
                  "sst": G[G.Subclass == "Sst"].groupby("Donor ID").size() / G.groupby("Donor ID").size()}).fillna(0)
lo, hi = T[T.adnc.isin(["Not AD", "Low"])], T[T.adnc == "High"]
rng = np.random.default_rng(0); draws = []
for _ in range(400):
    a = lo.sample(len(lo), replace=True, random_state=rng.integers(1e9)); b = hi.sample(len(hi), replace=True, random_state=rng.integers(1e9))
    tot_exc = (1 - b.l23.mean() / a.l23.mean()) * a.l23.mean()
    sst_frac_lost = (a.sstv.mean() - b.sstv.mean()) / a.sst.mean()          # share of all Sst neurons lost
    draws.append((tot_exc, sst_frac_lost))
draws = np.array(draws)
print(f"AnG: excitatory-drive loss {np.median(draws[:,0]):.3f} [{np.percentile(draws[:,0],2.5):.3f},{np.percentile(draws[:,0],97.5):.3f}]; "
      f"fraction of Sst neurons lost (vulnerable set) {np.median(draws[:,1]):.3f} [{np.percentile(draws[:,1],2.5):.3f},{np.percentile(draws[:,1],97.5):.3f}]")
def pred(base, tot, sstl):
    q = dict(base)
    for w in ("wEE", "wFE", "wSE"): q[w] = base[w] * (1 - tot)
    q["wES"] = q["wES"] * (1 - max(sstl, 0))
    if not M.stable(q): return None
    d = features(fq, np.log10(M.psd(q, fq))) - features(fq, np.log10(M.psd(base, fq)))
    w = 1 / se ** 2; off = np.sum(w * OFF * (delta - d)) / np.sum(w * OFF); p = d + off * OFF
    return p, float(np.sum(((delta - p) / se) ** 2))
for nm, use in [("L2/3 only", (1, 0)), ("vulnerable Sst only", (0, 1)), ("combined", (1, 1))]:
    rows = []
    for base in cals:
        for t, s in draws[rng.choice(len(draws), 60)]:
            o = pred(base, t * use[0], s * use[1])
            if o: rows.append(dict(chi2=o[1], **dict(zip(FEATS, o[0]))))
    R = pd.DataFrame(rows)
    print(f"\n--- {nm}: chi2 median {R.chi2.median():.1f} [{R.chi2.quantile(.025):.1f},{R.chi2.quantile(.975):.1f}] (offset only 24.5); "
          f"right signs {np.mean((R.b16_23<0)&(R.slope24_47>0)&(R.bump_h11>0)):.2f}")
    for f_, d0, s0 in zip(FEATS, delta, se):
        print(f"   {f_:11s} pred {R[f_].median():+.3f} [{R[f_].quantile(.025):+.3f},{R[f_].quantile(.975):+.3f}]  obs {d0:+.3f}+-{s0:.3f}")
