"""Probe order as a design variable: non-commuting probes and identifiability (design-level demonstration).
State update U for a perturbation probe: an activity-dependent slow adaptation a reduces pyramidal gain,
gE_eff = gE (1 - a), with a = alpha * R(theta) / R(theta0), where R is the circuit's driven response power at the drive
frequency. Because R depends on the mechanism, U depends on the mechanism, so O_rest after U differs from O_rest before
U: the probes do not commute. Static probes (tissue, PET-like readouts) have U = identity.
Mechanism parameters theta = severities of the three candidates the data cannot separate at rest:
  M4 slow/SST loop down, M1- excitatory gain down, L23 loss (all outputs, tissue-scaled).
Observation noise: resting features use the ds004504 bootstrap SEs; driven responses 1.2 dB (ds006036 SE);
tissue L2/3 share uses the SEA-AD bootstrap SE.  alpha = 0.15 is an assumption (15 % gain drop after a block);
results are reported for alpha in {0.05, 0.15, 0.30}.
For each probe sequence: Fisher information F = J^T Sigma^-1 J (J = d observations / d theta at theta0 + small k),
smallest eigenvalue, log det, Cramer-Rao SE per mechanism. Order effect = same probes, different order.
"""
import json, sys, itertools, numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/work/phaseB"); sys.path.insert(0, "/home/claude/work")
import model as M
from bridge import features

OUT = "/home/claude/work/framework/out"
Jz = np.load("/home/claude/work/phaseB/out/jacobian.npz", allow_pickle=True); se_rest = Jz["se"]
cals = json.load(open("/home/claude/work/phaseB/out/good_calibrations.json"))
fq = np.arange(2, 50.01, 0.5); SE_PH = 1.2
tis = pd.read_csv("/home/claude/work/seaad_AnG_donor_fractions.csv", index_col=0)
SE_TIS = tis["L2/3 IT"].std() / np.sqrt(len(tis)) / tis["L2/3 IT"].mean()     # relative share SE
THETA = ["M4_slow_inhib_down", "M1_gain_down", "L23_loss"]


def circuit(base, th):
    q = dict(base)
    q = M.apply(q, "M4_slow_inhib_down", th[0])
    q = M.apply(q, "M1_drive_gain_up", -th[1])
    for w in ("wEE", "wFE", "wSE"): q[w] = q[w] * (1 - 0.12 * th[2])
    return q


def H2(p, f):
    A, Bm, C = M.system(p)
    return np.array([np.abs(C @ np.linalg.solve(2j * np.pi * fi * np.eye(6) - A, Bm[:, 0])) ** 2 for fi in f])


def rel(d): x = np.array(d, float).copy(); x[:4] -= x[:4].mean(); return x


def run_sequence(base, th, seq, alpha):
    """Apply probes in order; return concatenated observations. State = circuit params incl. adapted gain."""
    p = circuit(base, th); a = 0.0; obs = []
    R0 = {}
    for probe in seq:
        q = dict(p); q["gE"] = p["gE"] * (1 - a)
        if probe == "rest":
            obs += list(rel(features(fq, np.log10(M.psd(q, fq)))))
        elif probe.startswith("drive"):
            fd = float(probe[5:])
            r = H2(q, [fd])[0]
            obs.append(10 * np.log10(r))
            r0 = H2(base, [fd])[0]
            a = a + alpha * r / r0                         # activity-dependent adaptation: the state update U
        elif probe == "tissue":
            obs.append(-0.27 * th[2] - 0.0 * th[0])        # L2/3 share responds only to L23 loss (static, U = id)
    return np.array(obs)


def noise(seq):
    s = []
    for probe in seq:
        if probe == "rest": s += list(se_rest)
        elif probe.startswith("drive"): s.append(SE_PH)
        elif probe == "tissue": s.append(SE_TIS)
    return np.array(s)


def fisher(base, seq, alpha, h=0.05):
    th0 = np.array([0.0, 0.0, 0.0]); y0 = run_sequence(base, th0, seq, alpha)
    J = np.column_stack([(run_sequence(base, th0 + h * e, seq, alpha) - y0) / h for e in np.eye(3)])
    S = noise(seq); F = J.T @ np.diag(1 / S ** 2) @ J
    ev = np.linalg.eigvalsh(F)
    return ev.min(), np.sum(np.log(np.maximum(ev, 1e-12))), np.sqrt(np.diag(np.linalg.pinv(F)))


SEQS = {"rest": ["rest"],
        "rest -> drive20 (ds006036 order)": ["rest", "drive20"],
        "drive20 -> rest (reversed)": ["drive20", "rest"],
        "rest -> drive40 -> rest": ["rest", "drive40", "rest"],
        "rest -> drive20 -> drive40 -> rest": ["rest", "drive20", "drive40", "rest"],
        "rest -> drive40 -> drive20 -> rest": ["rest", "drive40", "drive20", "rest"],
        "rest + tissue (static)": ["rest", "tissue"],
        "rest -> drive40 -> rest + tissue": ["rest", "drive40", "rest", "tissue"]}
rows = []
for alpha in (0.05, 0.15, 0.30):
    for nm, seq in SEQS.items():
        vals = [fisher(b, seq, alpha) for b in cals]
        rows.append(dict(alpha=alpha, sequence=nm, min_eig=np.median([v[0] for v in vals]),
                         logdet=np.median([v[1] for v in vals]),
                         **{f"CRLB_{t}": np.median([v[2][i] for v in vals]) for i, t in enumerate(THETA)}))
R = pd.DataFrame(rows); pd.set_option("display.width", 250)
print(R.round(3).to_string(index=False)); R.to_csv(f"{OUT}/probe_order.csv", index=False)
# non-commutativity check: does order change the observation vector itself?
b = cals[0]; th = np.array([0.4, 0.4, 0.4])
for alpha in (0.15,):
    y1 = run_sequence(b, th, ["rest", "drive40"], alpha); y2 = run_sequence(b, th, ["drive40", "rest"], alpha)
    print("\norder changes the resting features measured (alpha 0.15, theta 0.4 each):",
          np.round(y1[:6] - y2[1:7], 4), "| driven response identical:", np.isclose(y1[6], y2[0]))
