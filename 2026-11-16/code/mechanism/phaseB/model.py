"""Phase B: linearised three-population posterior cortical node, closed-form EEG spectrum.

States x = [rE, rF, rS, sA, sF, sS]
  population rates   tau_p  d r_p/dt = -r_p + gain_p * input_p (+ noise on E, F)
  synaptic gating    tau_s  d s/dt   = -s + r_pre      (sA: AMPA from E; sF: fast GABA_A from PV; sS: slow GABA from S)
Inputs
  E: + wEE sA - wEF sF - wES sS + xi_E
  F: + wFE sA - wFF sF        + xi_F
  S: + wSE sA
EEG y = net synaptic current onto pyramidal cells = wEE sA - wEF sF - wES sS, scaled, plus white floor.
S(f) = |C (i 2 pi f I - A)^-1 B|^2 weighted by input noise variances.
"""
import numpy as np

PAR = dict(tauE=0.004, tauF=0.002, tauS=0.010, tA=0.002, tF=0.008, tS=0.030,
           wEE=1.0, wEF=2.0, wES=1.0, wFE=2.0, wFF=0.5, wSE=1.5,
           gE=1.0, gF=1.0, gS=1.0, sigE=1.0, sigF=0.3, scale=1.0, floor=1e-3)
FREE = ["tauE", "tF", "tS", "wEE", "wEF", "wES", "wFE", "wFF", "wSE", "sigF", "scale", "floor"]
BOUNDS = dict(tauE=(0.001, 0.015), tF=(0.003, 0.015), tS=(0.012, 0.060), wEE=(0.0, 2.0), wEF=(0.2, 6.0),
              wES=(0.0, 6.0), wFE=(0.2, 6.0), wFF=(0.0, 6.0), wSE=(0.0, 6.0), sigF=(0.05, 3.0),
              scale=(1e-6, 1e12), floor=(1e-12, 1e6))


def system(p):
    A = np.zeros((6, 6)); B = np.zeros((6, 2))
    rE, rF, rS, sA, sF, sS = range(6)
    A[rE, rE] = -1 / p["tauE"]; A[rE, sA] = p["gE"] * p["wEE"] / p["tauE"]
    A[rE, sF] = -p["gE"] * p["wEF"] / p["tauE"]; A[rE, sS] = -p["gE"] * p["wES"] / p["tauE"]
    A[rF, rF] = -1 / p["tauF"]; A[rF, sA] = p["gF"] * p["wFE"] / p["tauF"]; A[rF, sF] = -p["gF"] * p["wFF"] / p["tauF"]
    A[rS, rS] = -1 / p["tauS"]; A[rS, sA] = p["gS"] * p["wSE"] / p["tauS"]
    for s, r, t in ((sA, rE, "tA"), (sF, rF, "tF"), (sS, rS, "tS")):
        A[s, s] = -1 / p[t]; A[s, r] = 1 / p[t]
    B[rE, 0] = p["gE"] * p["sigE"] / p["tauE"]; B[rF, 1] = p["gF"] * p["sigF"] / p["tauF"]
    C = np.zeros(6); C[sA], C[sF], C[sS] = p["wEE"], -p["wEF"], -p["wES"]
    return A, B, C


def stable(p):
    return np.max(np.linalg.eigvals(system(p)[0]).real) < -1.0


def psd(p, f):
    A, B, C = system(p)
    out = np.empty(len(f))
    for i, fi in enumerate(f):
        H = C @ np.linalg.solve(2j * np.pi * fi * np.eye(6) - A, B)
        out[i] = np.sum(np.abs(H) ** 2)
    return p["scale"] * out + p["floor"]


def eig_summary(p):
    ev = np.linalg.eigvals(system(p)[0]); ev = ev[ev.imag > 0]
    return sorted([(float(e.imag / 2 / np.pi), float(-e.real)) for e in ev])   # (freq Hz, damping 1/s)


# ---- mechanisms: one knob each, k in [0, 1]; magnitudes are modelling choices (directions interpreted)
def apply(p, mech, k):
    q = dict(p)
    if mech == "M1_drive_gain_up":        q["gE"] = p["gE"] * (1 + 0.5 * k); q["gF"] = p["gF"] * (1 + 0.25 * k)
    elif mech == "M2_PV_to_E_down":       q["wEF"] = p["wEF"] * (1 - 0.5 * k)
    elif mech == "M3_recurrent_E_up":     q["wEE"] = p["wEE"] * (1 + 0.1 * k)
    elif mech == "M4_slow_inhib_down":    q["wES"] = p["wES"] * (1 - 0.6 * k); q["wSE"] = p["wSE"] * (1 - 0.3 * k)
    elif mech == "M5_input_EI_up":        q["sigF"] = p["sigF"] * (1 - 0.6 * k); q["sigE"] = p["sigE"] * (1 + 0.3 * k)
    else: raise KeyError(mech)
    return q


MECHS = ["M1_drive_gain_up", "M2_PV_to_E_down", "M3_recurrent_E_up", "M4_slow_inhib_down", "M5_input_EI_up"]
