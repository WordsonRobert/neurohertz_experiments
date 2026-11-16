"""Phase B run: calibrate to CN, score mechanisms against the AD-CN posterior difference vector."""
import glob, itertools, json, os, sys
import numpy as np, pandas as pd
from scipy.optimize import least_squares, minimize
sys.path.insert(0, os.path.dirname(__file__))
import model as M

FEAT = "/mnt/user-data/uploads/neurohertz2/classification/cache/ds004504/main/feat"
PART = "/home/claude/data/ds004504/participants.tsv"
OUT = os.path.join(os.path.dirname(__file__), "out"); os.makedirs(OUT, exist_ok=True)
SITES = ["P3", "P4", "Pz"]
FIT = (14.0, 47.0)
FEATS = ["b16_23", "b24_30", "b32_40", "b42_47", "slope24_47", "bump_h11"]


def features(f, lp):
    out = {}
    for nm, (a, b) in dict(b16_23=(16, 23), b24_30=(24, 30), b32_40=(32, 40), b42_47=(42, 47)).items():
        out[nm] = lp[(f >= a) & (f <= b)].mean()
    m = (f >= 24) & (f <= 47); out["slope24_47"] = np.polyfit(np.log10(f[m]), lp[m], 1)[0]
    fl = ((f >= 24) & (f <= 30)) | ((f >= 42) & (f <= 47))
    c = np.polyfit(np.log10(f[fl]), lp[fl], 1); k = (f >= 32) & (f <= 40)
    out["bump_h11"] = np.mean(lp[k] - np.polyval(c, np.log10(f[k])))
    return np.array([out[k] for k in FEATS])


# ---------------- data
P = pd.read_csv(PART, sep="\t").set_index("participant_id")
spec, grp = {}, {}
for fn in sorted(glob.glob(FEAT + "/sub-*.npz")):
    s = os.path.basename(fn)[:-4]
    if P.loc[s, "Group"] not in ("A", "C"): continue
    z = np.load(fn); f = z["freqs"]; ch = list(z["ch_names"]); idx = [ch.index(c) for c in SITES]
    spec[s] = np.log10(np.mean(10 ** z["logpsd_csd"][idx], 0)); grp[s] = P.loc[s, "Group"]
subs = sorted(spec); L = np.array([spec[s] for s in subs]); g = np.array([grp[s] for s in subs])
Fm = np.array([features(f, l) for l in L])
delta = Fm[g == "A"].mean(0) - Fm[g == "C"].mean(0)
rng = np.random.default_rng(0); boots = []
for _ in range(2000):
    a = rng.choice(np.where(g == "A")[0], (g == "A").sum()); c = rng.choice(np.where(g == "C")[0], (g == "C").sum())
    boots.append(Fm[a].mean(0) - Fm[c].mean(0))
se = np.array(boots).std(0)
print("DATA  AD-CN delta (log10 units / slope units):")
for n, d, s_ in zip(FEATS, delta, se): print(f"  {n:11s} {d:+.3f}  +- {s_:.3f}   z={d/s_:+.1f}")

# ---------------- calibrate baseline to CN mean spectrum
fm = (f >= FIT[0]) & (f <= FIT[1]); ff = f[fm]
target = L[g == "C"].mean(0)[fm]
logkeys = {"scale", "floor"}


def unpack(v):
    p = dict(M.PAR)
    for k, x in zip(M.FREE, v): p[k] = float(np.exp(x)) if k in logkeys else float(x)
    return p


def resid(v):
    p = unpack(v)
    if not M.stable(p): return np.full(len(ff), 10.0)
    return np.log10(M.psd(p, ff)) - target


lo = [np.log(M.BOUNDS[k][0]) if k in logkeys else M.BOUNDS[k][0] for k in M.FREE]
hi = [np.log(M.BOUNDS[k][1]) if k in logkeys else M.BOUNDS[k][1] for k in M.FREE]
cals = []
best = None
for trial in range(60):
    v0 = np.array([rng.uniform(l, h) for l, h in zip(lo, hi)])
    p0 = unpack(v0)
    v0[M.FREE.index("scale")] = np.log(10 ** target.mean() / np.mean(M.psd({**p0, "scale": 1, "floor": 0}, ff)) + 1e-30)
    try:
        r = least_squares(resid, v0, bounds=(lo, hi), max_nfev=3000)
    except Exception:
        continue
    cals.append(r)
    if best is None or r.cost < best.cost: best = r
base = unpack(best.x)
rms = np.sqrt(np.mean(resid(best.x) ** 2))
print(f"\nCALIBRATION to CN 14-47 Hz: rms log10 error {rms:.3f}; resonances (Hz, damping/s): {M.eig_summary(base)}")
print("  params:", {k: round(base[k], 4) for k in M.FREE})
json.dump(base, open(f"{OUT}/baseline_params.json", "w"), indent=1)
f0 = features(f[f > 0], np.log10(M.psd(base, f[f > 0])))
print("  model CN features:", dict(zip(FEATS, np.round(f0, 3))), "\n  data  CN features:",
      dict(zip(FEATS, np.round(Fm[g == 'C'].mean(0), 3))))

fpos = f[(f >= 2) & (f <= 50)]


def model_delta(ks):
    p = dict(base)
    for m, k in ks.items(): p = M.apply(p, m, k)
    if not M.stable(p): return None
    return features(fpos, np.log10(M.psd(p, fpos))) - features(fpos, np.log10(M.psd(base, fpos)))


OFF = np.array([1, 1, 1, 1, 0, 0], float)        # global log offset (skull/atrophy/scalp gain) moves only absolute bands


def score(ks_vec, mechs):
    d = model_delta(dict(zip(mechs, ks_vec)))
    if d is None: return 1e6, None, None
    w = 1 / se ** 2
    off = np.sum(w * OFF * (delta - d)) / np.sum(w * OFF)          # best nuisance offset, closed form
    pred = d + off * OFF
    return float(np.sum(((delta - pred) / se) ** 2)), pred, off


chi0 = float(np.sum((delta / se) ** 2)); chi_off = score([0.0], [M.MECHS[0]])[0] if True else None
print(f"\nNULL chi2 (no change) = {chi0:.1f}; offset-only chi2 = {score([0.0],[M.MECHS[0]])[0]:.1f}  (6 features)")
rows = []
for r in (1, 2):
    for mechs in itertools.combinations(M.MECHS, r):
        bestfit = None
        for start in itertools.product(*[[-0.6, 0.3, 0.9]] * r):
            res = minimize(lambda v: score(v, mechs)[0], start, bounds=[(-1.5, 1.5)] * r, method="L-BFGS-B")
            if bestfit is None or res.fun < bestfit.fun: bestfit = res
        chi, pred, off = score(bestfit.x, mechs)
        signs_ok = bool(pred is not None and pred[0] < 0 and pred[4] > 0 and pred[5] > 0
                        and abs(pred[2] - delta[2]) < 2 * se[2])
        rows.append(dict(mechs="+".join(mechs), k=np.round(bestfit.x, 2).tolist(), chi2=round(chi, 1),
                         offset=None if off is None else round(off, 3), phenotype_signs=signs_ok,
                         **{f"pred_{n}": None if pred is None else round(v, 3) for n, v in zip(FEATS, pred if pred is not None else [None]*6)}))
R = pd.DataFrame(rows).sort_values("chi2"); R.to_csv(f"{OUT}/mechanism_fits.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 20)
print("\nFITS (lower chi2 better; 6 features; signs = beta down, slope flatter, bump up, 32-40 within 2 SE):")
print(R.to_string(index=False))

# ---------------- identifiability at k = 0 (+ offset nuisance)
h = 0.05
J = np.column_stack([model_delta({m: h}) / h for m in M.MECHS] + [OFF])
W = np.diag(1 / se ** 2); Fi = J.T @ W @ J
ev = np.linalg.eigvalsh(Fi)[::-1]
cr = np.sqrt(np.diag(np.linalg.pinv(Fi)))
Jn = J[:, :5] / np.linalg.norm(J[:, :5], axis=0)
print("\nIDENTIFIABILITY (Jacobian w.r.t. k at baseline, features weighted by bootstrap SE, + offset nuisance)")
print("  J columns (per unit k):"); print(pd.DataFrame(J[:, :5], index=FEATS, columns=M.MECHS).round(3).to_string())
print("  Fisher eigenvalues:", np.round(ev, 2))
print("  CRLB SE of k:", dict(zip(M.MECHS + ["offset"], np.round(cr, 3))))
print("  cosine between mechanism columns:"); print(pd.DataFrame(Jn.T @ Jn, index=M.MECHS, columns=M.MECHS).round(2).to_string())
np.savez(f"{OUT}/jacobian.npz", J=J, se=se, delta=delta, feats=FEATS, mechs=M.MECHS)

# ---------------- robustness across the ensemble of good calibrations
good = sorted(cals, key=lambda r: r.cost)
good = [r for r in good if np.sqrt(np.mean(resid(r.x) ** 2)) < 1.5 * rms][:12]
print(f"\nROBUSTNESS: {len(good)} calibrations within 1.5x best rms")
ens = []
for ci, rcal in enumerate(good):
    base = unpack(rcal.x)
    bnd = [n for n in M.FREE if n not in logkeys and (abs(base[n]-M.BOUNDS[n][0]) < 1e-6 or abs(base[n]-M.BOUNDS[n][1]) < 1e-6)]
    for mm in M.MECHS:
        bestfit = None
        for st in (-0.6, 0.3, 0.9):
            res = minimize(lambda v: score(v, [mm])[0], [st], bounds=[(-1.5, 1.5)], method="L-BFGS-B")
            if bestfit is None or res.fun < bestfit.fun: bestfit = res
        ens.append(dict(cal=ci, rms=round(float(np.sqrt(np.mean(resid(rcal.x)**2))),3), at_bounds=",".join(bnd),
                        resonances=[(round(a,1),round(b,1)) for a,b in M.eig_summary(base)], mech=mm,
                        k=round(float(bestfit.x[0]),2), chi2=round(float(bestfit.fun),1)))
E = pd.DataFrame(ens); E.to_csv(f"{OUT}/robustness.csv", index=False)
json.dump([unpack(rc.x) for rc in good], open(f"{OUT}/good_calibrations.json", "w"))
print(E.pivot_table(index="cal", columns="mech", values="chi2").round(1).to_string())
print(E.pivot_table(index="cal", columns="mech", values="k").round(2).to_string())
print(E.drop_duplicates("cal")[["cal","rms","at_bounds","resonances"]].to_string(index=False))
