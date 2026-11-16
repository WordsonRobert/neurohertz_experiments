"""Tissue -> EEG bridge, no fitting to EEG.
Take the AnG L2/3 IT loss measured in SEA-AD (High ADNC vs Not AD/Low), convert to a loss of excitatory drive in
the calibrated Phase B circuit, predict the AD - CN resting EEG features, compare with the observed ds004504 deltas.
Variants (how L2/3 loss enters the circuit):
  global      : all pyramidal outputs (wEE, wFE, wSE) scaled by (1 - total excitatory loss)
  superficial : L2/3 = supragranular drive -> recurrent excitation wEE and drive into the slow/beta loop wSE scaled
                by (1 - L2/3 loss); PV loop drive untouched
Only free parameter: one global log offset on absolute band powers (scalp attenuation), as in Phase B.
Uncertainty: bootstrap over SEA-AD donors (loss estimate) x ensemble of good calibrations.
"""
import json, sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/work/phaseB")
import model as M

FEATS = ["b16_23", "b24_30", "b32_40", "b42_47", "slope24_47", "bump_h11"]


def features(f, lp):
    o = {}
    for nm, (a, b) in dict(b16_23=(16, 23), b24_30=(24, 30), b32_40=(32, 40), b42_47=(42, 47)).items():
        o[nm] = lp[(f >= a) & (f <= b)].mean()
    m = (f >= 24) & (f <= 47); o["slope24_47"] = np.polyfit(np.log10(f[m]), lp[m], 1)[0]
    fl = ((f >= 24) & (f <= 30)) | ((f >= 42) & (f <= 47)); c = np.polyfit(np.log10(f[fl]), lp[fl], 1)
    k = (f >= 32) & (f <= 40); o["bump_h11"] = np.mean(lp[k] - np.polyval(c, np.log10(f[k])))
    return np.array([o[x] for x in FEATS])


if __name__ == "__main__":
    J = np.load("/home/claude/work/phaseB/out/jacobian.npz", allow_pickle=True)
    delta, se = J["delta"], J["se"]
    OFF = np.array([1, 1, 1, 1, 0, 0], float)
    cals = json.load(open("/home/claude/work/phaseB/out/good_calibrations.json"))
    fq = np.arange(2, 50.01, 0.5)
    
    # ---- tissue loss estimates (AnG), bootstrap over donors
    T = pd.read_csv("/home/claude/work/seaad_AnG_donor_fractions.csv", index_col=0)
    lo, hi = T[T.adnc_n <= 1], T[T.adnc_n >= 3]
    rng = np.random.default_rng(0); L23, TOT = [], []
    for _ in range(1000):
        a = lo.sample(len(lo), replace=True, random_state=rng.integers(1e9)); b = hi.sample(len(hi), replace=True, random_state=rng.integers(1e9))
        r = b["L2/3 IT"].mean() / a["L2/3 IT"].mean()
        L23.append(1 - r); TOT.append((1 - r) * a["L2/3 IT"].mean())
    L23, TOT = np.array(L23), np.array(TOT)
    print(f"TISSUE (AnG): L2/3 IT loss = {np.median(L23):.2f} [{np.percentile(L23,2.5):.2f}, {np.percentile(L23,97.5):.2f}]; "
          f"implied total excitatory-drive loss = {np.median(TOT):.3f} [{np.percentile(TOT,2.5):.3f}, {np.percentile(TOT,97.5):.3f}]")
    
    
    def apply_loss(p, variant, l23, tot):
        q = dict(p)
        if variant == "global":
            for k in ("wEE", "wFE", "wSE"): q[k] = p[k] * (1 - tot)
        else:
            q["wEE"] = p["wEE"] * (1 - l23); q["wSE"] = p["wSE"] * (1 - l23)
        return q
    
    
    def predict(base, variant, l23, tot):
        q = apply_loss(base, variant, l23, tot)
        if not M.stable(q): return None
        d = features(fq, np.log10(M.psd(q, fq))) - features(fq, np.log10(M.psd(base, fq)))
        w = 1 / se ** 2; off = np.sum(w * OFF * (delta - d)) / np.sum(w * OFF)
        pred = d + off * OFF
        return pred, float(np.sum(((delta - pred) / se) ** 2)), off
    
    
    null = float(np.sum(((delta - (np.sum(OFF * delta / se**2) / np.sum(OFF / se**2)) * OFF) / se) ** 2))
    print(f"EEG observed delta: {dict(zip(FEATS, np.round(delta, 3)))}")
    print(f"offset-only chi2 = {null:.1f}   (6 features)\n")
    idx = rng.choice(len(L23), 200)
    for variant in ["global", "superficial"]:
        rows = []
        for ci, base in enumerate(cals):
            for i in idx:
                out = predict(base, variant, L23[i], TOT[i])
                if out: rows.append(dict(cal=ci, chi2=out[1], **dict(zip(FEATS, out[0]))))
        R = pd.DataFrame(rows)
        med = predict(cals[0], variant, np.median(L23), np.median(TOT))
        print(f"--- variant: {variant}  (prediction from tissue, no EEG fitting)")
        print("   predicted (median, 95% over tissue bootstrap x calibrations):")
        for fz, d0, s0 in zip(FEATS, delta, se):
            q = R[fz]; print(f"     {fz:11s} pred {q.median():+.3f} [{q.quantile(.025):+.3f},{q.quantile(.975):+.3f}]   observed {d0:+.3f} +- {s0:.3f}")
        print(f"   chi2 median {R.chi2.median():.1f} [{R.chi2.quantile(.025):.1f}, {R.chi2.quantile(.975):.1f}] vs offset-only {null:.1f}")
        print(f"   fraction of draws with right signs (beta down, slope flatter, bump up): "
              f"{np.mean((R.b16_23 < 0) & (R.slope24_47 > 0) & (R.bump_h11 > 0)):.2f}\n")
