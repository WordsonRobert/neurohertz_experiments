"""Discriminating test: driven-response profile AD - CN vs Phase B mechanism predictions.
Model: drive enters pyramidal input; response power at f scales as |H(f)|^2 (same flash harmonic content in both
groups, so the input cancels in AD - CN). Prediction per mechanism: 10*log10(|H_mech(f)|^2 / |H_base(f)|^2) dB,
at the k fitted to the RESTING phenotype in Phase B (no refit to photic data). Free: one additive offset (overall
scalp/attenuation gain). Data: per-subject mean over blocks of 10*log10(evoked power), cells (fd, n) where the CN
median SNR >= 3 dB. Group difference + bootstrap SE.
"""
import json, sys, numpy as np, pandas as pd
from scipy.optimize import minimize_scalar
sys.path.insert(0, "/home/claude/work/phaseB")
import model as M

R = pd.read_csv("/home/claude/work/phaseC/out/photic_responses.csv")
R["evoked_db"] = 10 * R["log_evoked"]
S = R.groupby(["sub", "group", "fd", "n", "f"], as_index=False)[["evoked_db", "snr_db"]].mean()
cn_snr = S[S.group == "C"].groupby(["fd", "n"]).snr_db.median()
cells = [c for c, v in cn_snr.items() if v >= 3.0]
rng = np.random.default_rng(1); rows = []
for fd, n in cells:
    d = S[(S.fd == fd) & (S.n == n)]
    a = d[d.group == "A"].evoked_db.values; c = d[d.group == "C"].evoked_db.values
    if len(a) < 10 or len(c) < 10: continue
    bs = [rng.choice(a, len(a)).mean() - rng.choice(c, len(c)).mean() for _ in range(2000)]
    sa = S[(S.fd == fd) & (S.n == n) & (S.group == "A")].snr_db.median()
    rows.append(dict(fd=fd, n=n, f=fd * n, nA=len(a), nC=len(c), cn_snr=round(cn_snr[(fd, n)], 1), ad_snr=round(sa, 1),
                     delta_db=a.mean() - c.mean(), se=np.std(bs)))
T = pd.DataFrame(rows).sort_values(["f", "fd"])

cals = json.load(open("/home/claude/work/phaseB/out/good_calibrations.json"))
rob = pd.read_csv("/home/claude/work/phaseB/out/robustness.csv")


def H2(p, f):
    A, B, C = M.system(p)
    return np.array([np.abs(C @ np.linalg.solve(2j * np.pi * fi * np.eye(6) - A, B[:, 0])) ** 2 for fi in f])


def chi(pred):
    w = 1 / T.se.values ** 2; r = T.delta_db.values - pred
    off = np.sum(w * r) / np.sum(w)
    return float(np.sum(((r - off) / T.se.values) ** 2)), off


preds = {}; out = []
for ci, base in enumerate(cals):
    for mech in ["M4_slow_inhib_down", "M1_drive_gain_up", "M5_input_EI_up", "M2_PV_to_E_down"]:
        k = float(rob[(rob.cal == ci) & (rob.mech == mech)].k.iloc[0])
        q = M.apply(base, mech, k)
        if not M.stable(q): continue
        pred = 10 * np.log10(H2(q, T.f.values) / H2(base, T.f.values))
        c2, off = chi(pred); preds[(ci, mech)] = pred
        out.append(dict(cal=ci, mech=mech, k_rest=k, chi2=round(c2, 1), offset_db=round(off, 2)))
O = pd.DataFrame(out)
null_chi, null_off = chi(np.zeros(len(T)))
pd.set_option("display.width", 220)
print("DATA: AD - CN evoked power (dB) per response cell (CN median SNR >= 3 dB):")
print(T.round(2).to_string(index=False))
print(f"\nNULL (uniform AD-CN difference only): chi2 = {null_chi:.1f}, offset {null_off:.2f} dB, dof = {len(T)-1}")
print("\nMECHANISM PREDICTIONS at the k fitted to REST (no refit), + 1 free offset:")
print(O.pivot_table(index="cal", columns="mech", values="chi2").round(1).to_string())
for mech in ["M4_slow_inhib_down", "M1_drive_gain_up"]:
    for ci in (0, 1):
        if (ci, mech) in preds:
            print(f"  cal{ci} {mech:20s} predicted dB by f:", dict(zip(T.f.astype(int), np.round(preds[(ci, mech)], 2))))
T.to_csv("/home/claude/work/phaseC/out/photic_group_delta.csv", index=False)
O.to_csv("/home/claude/work/phaseC/out/photic_mechanism_chi2.csv", index=False)

print("\n--- restricted to the model's calibrated range (f >= 14 Hz) ---")
keep = T.f.values >= 14
T2 = T[keep].reset_index(drop=True)
def chi2r(pred):
    w = 1 / T2.se.values ** 2; r = T2.delta_db.values - pred; off = np.sum(w * r) / np.sum(w)
    return float(np.sum(((r - off) / T2.se.values) ** 2))
print(f"NULL chi2 = {chi2r(np.zeros(len(T2))):.2f} (dof {len(T2)-1})")
for mech in ["M4_slow_inhib_down", "M1_drive_gain_up", "M2_PV_to_E_down", "M5_input_EI_up"]:
    v = [chi2r(preds[(ci, mech)][keep]) for ci in range(len(cals)) if (ci, mech) in preds]
    print(f"  {mech:20s} chi2 range over calibrations {min(v):.2f} - {max(v):.2f}")

# within-person: does resting beta (ds004504, CSD P3/P4/Pz) predict driven 15-20 Hz evoked power (ds006036)?
import glob, os
from scipy.stats import spearmanr
F = "/mnt/user-data/uploads/neurohertz2/classification/cache/ds004504/main/feat"
rest = {}
for fn in glob.glob(F + "/sub-*.npz"):
    z = np.load(fn); f = z["freqs"]; ch = list(z["ch_names"]); idx = [ch.index(c) for c in ["P3", "P4", "Pz", "O1", "O2"]]
    lp = np.log10(np.mean(10 ** z["logpsd_avg"][idx], 0))
    rest[os.path.basename(fn)[:7]] = dict(beta=10 * lp[(f >= 16) & (f <= 23)].mean(), alpha=10 * lp[(f >= 8) & (f <= 12)].mean(),
                                         g=10 * lp[(f >= 32) & (f <= 40)].mean())
Rr = pd.DataFrame(rest).T
for (fd, n), lab in [((20, 1), "20 Hz drive"), ((10, 2), "20 Hz harmonic"), ((15, 1), "15 Hz drive"), ((10, 1), "10 Hz drive")]:
    d = S[(S.fd == fd) & (S.n == n)].set_index("sub").join(Rr, how="inner")
    col = "alpha" if fd * n == 10 else "beta"
    r_all = spearmanr(d.evoked_db, d[col])[0]
    r_w = np.mean([spearmanr(d[d.group == gname].evoked_db, d[d.group == gname][col])[0] for gname in ("A", "C")])
    print(f"  {lab:15s} evoked vs resting {col}: rho all = {r_all:+.2f}, mean within-group = {r_w:+.2f} (n={len(d)})")
