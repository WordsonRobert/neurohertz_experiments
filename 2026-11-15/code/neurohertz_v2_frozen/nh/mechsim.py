"""Mechanistic gamma simulator: one circuit, one knob per candidate mechanism.

A stochastic rate model with three populations, pyramidal (E), PV basket (P) and somatostatin (S):

    tau_E dE/dt = -E + F(w_EE E - w_EP g(t) P - w_ES S + mu_E + d_E(t) + sigma_E xi_E)
    tau_P dP/dt = -P + F(w_PE E - w_PP g(t) P - w_PS S + mu_P + d_P(t) + sigma_P xi_P)
    tau_S dS/dt = -S + F(w_SE E + mu_S)

The fast E-P loop (tau ~ 3-5 ms) is a noise-driven damped oscillator near 38 Hz (PING-like);
S adds slower dendritic inhibition. The simulated "EEG" is the net synaptic current onto pyramidal
cells, w_EP g P + w_ES S - w_EE E, which is then mixed with 1/f background, a white floor and
optional muscle noise, and passed through the SAME NeuroHertz feature code as real data.

Each mechanism (config `mechanism.theories`) is a single severity knob k in [0, 1]:

  T1 synapses_onto_pv : w_PE <- w_PE * (1 - 0.15 k)         weaker pyramidal->PV drive (NPTX2/GluA4)
  T2 nav11_pv_output  : g(t) in {0,1}: PV output fails in 2 ms windows with probability
                        p = 0.3 k * sigmoid((P - P*)/0.05)    failure under load (Nav1.1)
  T3 erratic_drive    : d_E(t) = 0.12 k * OU(tau = 1.5 s)      surging/dipping excitatory input (amyloid)
  T4 acetylcholine    : mu_E <- mu_E (1 - 0.1 k), mu_P <- mu_P (1 - 0.3 k); d_E = d_P = 0.06 k * OU(8 s)
                        less tonic (muscarinic) depolarisation + less stable state
  T5 sst_loss         : w_ES, w_PS, w_SE <- w * (1 - 0.3 k)  fewer SST cells
  T6 tau_silencing    : mu_E <- mu_E * (1 - 0.1 k)           general loss of excitatory drive

Linearised check (scratch): with these scalings every knob keeps the fixed point a damped focus up to
k = 1 (T1: 38->35 Hz, decay 25->5 /s; T5 (at 0.5 scaling): 38->28 Hz, 25->6 /s, so 0.3 is used; T6: decay 25->64 /s; T4: 38->42 Hz).
NOTE the rate model says weaker E->PV synapses make gamma LESS damped, the opposite of the verbal
prediction. That disagreement is why a second model family (nh/cyclemodel.py) exists and why only
predictions on which both families agree are treated as firm.

The knob scalings are modelling choices, written here and hashed into the freeze; the fingerprints
are reported per unit knob so only DIRECTIONS and RELATIVE patterns are interpreted, not the
absolute size of k. Nothing here touches data or labels.
"""
from __future__ import annotations

import numpy as np

THEORIES = ["synapses_onto_pv", "nav11_pv_output", "erratic_drive", "acetylcholine", "sst_loss",
            "tau_silencing"]
LOCAL_LOOP = ["synapses_onto_pv", "nav11_pv_output", "sst_loss"]
INPUT_DRIVEN = ["erratic_drive", "acetylcholine", "tau_silencing"]

# Tuned (scratch search on the linearised system) so the fixed point is a damped focus at 38 Hz with
# decay rate 25 /s (Q ~ 4.8): a noise-driven damped oscillator, as reported for cortical gamma.
BASE = dict(tau_E=0.004, tau_P=0.006, tau_S=0.020,
            w_EE=2.18, w_EP=2.186, w_ES=1.0, w_PE=1.729, w_PP=0.533, w_PS=0.6, w_SE=2.0,
            mu_E=1.323, mu_P=0.682, mu_S=-0.6,
            sigma_E=0.3, sigma_P=0.3, gain=3.465, theta=0.55,
            fail_window_s=0.002, fail_center=None)


def _F(x, gain, theta):
    return 1.0 / (1.0 + np.exp(-gain * (x - theta)))


def _ou_batch(n, dt_s, tau, rng, size):
    a = np.exp(-dt_s / tau)
    out = np.empty((n, size))
    out[0] = rng.standard_normal(size)
    e = rng.standard_normal((n, size)) * np.sqrt(1 - a * a)
    for i in range(1, n):
        out[i] = a * out[i - 1] + e[i]
    return out


def subject_base(rng: np.random.Generator) -> dict:
    """A simulated person's own baseline circuit: small log-normal spread of every weight (4%) and of
    the tonic drives, so fingerprints are estimated across people, not around one circuit."""
    b = dict(BASE)
    for k in ("w_EE", "w_EP", "w_ES", "w_PE", "w_PP", "w_PS", "w_SE"):
        b[k] = BASE[k] * float(np.exp(rng.normal(0, 0.04)))
    b["mu_E"] = BASE["mu_E"] + float(rng.normal(0, 0.02))
    b["mu_P"] = BASE["mu_P"] + float(rng.normal(0, 0.02))
    return b


def knob_params(theory: str | None, k: float, base: dict | None = None) -> tuple[dict, dict]:
    """(full parameter dict, drive-fluctuation spec) for one mechanism at severity k."""
    b = dict(BASE if base is None else base)
    p, drive = dict(b), {"E": (0.0, 1.0), "P": (0.0, 1.0)}     # drive: (amplitude, tau_s)
    if theory is None or k == 0:
        return p, drive
    # scalings chosen so every knob stays below the oscillation threshold up to k = 1
    if theory == "synapses_onto_pv":
        p["w_PE"] = b["w_PE"] * (1 - 0.15 * k)
    elif theory == "nav11_pv_output":
        p["fail_prob"] = 0.3 * k
    elif theory == "erratic_drive":
        drive["E"] = (0.12 * k, 1.5)
    elif theory == "acetylcholine":
        p["mu_E"] = b["mu_E"] * (1 - 0.1 * k)
        p["mu_P"] = b["mu_P"] * (1 - 0.3 * k)
        drive["E"] = (0.06 * k, 8.0); drive["P"] = (0.06 * k, 8.0)
    elif theory == "sst_loss":
        for w in ("w_ES", "w_PS", "w_SE"):
            p[w] = b[w] * (1 - 0.3 * k)
    elif theory == "tau_silencing":
        p["mu_E"] = b["mu_E"] * (1 - 0.1 * k)
    else:
        raise KeyError(theory)
    return p, drive


def simulate_circuit(params_list: list[dict], drives: list[dict], dur_s: float = 120.0, fs_out: float = 250.0,
                     dt: float = 2.5e-4, seed: int = 0) -> np.ndarray:
    """Integrate many circuits at once (one column per element of params_list).
    Returns the synaptic-current proxy at fs_out, shape (n_circuits, n_samples), unit variance."""
    rng = np.random.default_rng(seed)
    m = len(params_list)
    P = {k: np.array([{**BASE, **pp}.get(k, BASE.get(k)) for pp in params_list], dtype=float)
         for k in BASE if k not in ("fail_center",)}
    fail_prob = np.array([pp.get("fail_prob", 0.0) for pp in params_list])
    n = int(round(dur_s / dt))
    step_out = int(round(1 / (fs_out * dt)))
    # slow drive fluctuations, generated at 100 Hz and held
    dfs = 100.0
    nd = int(dur_s * dfs) + 2
    dE = np.zeros((nd, m)); dP = np.zeros((nd, m))
    for j, dr in enumerate(drives):
        aE, tE = dr["E"]; aP, tP = dr["P"]
        if aE > 0:
            dE[:, j] = aE * _ou_batch(nd, 1 / dfs, tE, rng, 1)[:, 0]
        if aP > 0:
            dP[:, j] = aP * _ou_batch(nd, 1 / dfs, tP, rng, 1)[:, 0]
    E = np.full(m, 0.2); Pp = np.full(m, 0.2); S = np.full(m, 0.1)
    g = np.ones(m)
    fail_steps = max(1, int(round(BASE["fail_window_s"] / dt)))
    sq = np.sqrt(dt)
    lfp = np.empty((n // step_out, m))
    acc = np.zeros(m); cnt = 0; o = 0
    # PV rate around which failures switch on: each circuit's own mean PV rate over the warm-up
    p_star = None
    warm = int(1.0 / dt)
    p_acc = np.zeros(m)
    for i in range(n + warm):
        di = min(nd - 1, int(max(0, i - warm) * dt * dfs))
        if p_star is not None and i % fail_steps == 0:
            pf = fail_prob / (1 + np.exp(-(Pp - p_star) / 0.05))
            g = (rng.random(m) >= pf).astype(float)
        IE = P["w_EE"] * E - P["w_EP"] * g * Pp - P["w_ES"] * S + P["mu_E"] + dE[di] \
            + P["sigma_E"] * rng.standard_normal(m) / sq * 0.01
        IP = P["w_PE"] * E - P["w_PP"] * g * Pp - P["w_PS"] * S + P["mu_P"] + dP[di] \
            + P["sigma_P"] * rng.standard_normal(m) / sq * 0.01
        IS = P["w_SE"] * E + P["mu_S"]
        E = E + dt / P["tau_E"] * (-E + _F(IE, P["gain"], P["theta"]))
        Pp = Pp + dt / P["tau_P"] * (-Pp + _F(IP, P["gain"], P["theta"]))
        S = S + dt / P["tau_S"] * (-S + _F(IS, P["gain"], P["theta"]))
        if i < warm:
            if i >= warm // 2:
                p_acc += Pp
            continue
        if p_star is None:
            p_star = p_acc / (warm - warm // 2)
        acc += P["w_EP"] * g * Pp + P["w_ES"] * S - P["w_EE"] * E
        cnt += 1
        if cnt == step_out:
            if o < lfp.shape[0]:
                lfp[o] = acc / cnt
            o += 1; acc[:] = 0; cnt = 0
    lfp = lfp[:o] if o < lfp.shape[0] else lfp
    lfp = lfp - lfp.mean(0)
    return (lfp / (lfp.std(0) + 1e-12)).T


def add_background(sig: np.ndarray, fs: float, rng: np.random.Generator, gamma_snr: float = 0.35,
                   chi: float = 1.5, floor: float = 0.05, emg: float = 0.0, scale_uv: float = 10.0) -> np.ndarray:
    """Mix a unit-variance circuit signal into 1/f background + white floor (+ optional muscle)."""
    from .simulate import _colored
    n = sig.shape[-1]
    bg = _colored(n, fs, chi, rng)
    x = bg + gamma_snr * sig + floor * rng.standard_normal(n)
    if emg > 0:
        from scipy.signal import butter, sosfiltfilt
        sos = butter(4, [20, min(120, 0.45 * fs)], btype="band", fs=fs, output="sos")
        e = sosfiltfilt(sos, rng.standard_normal(n))
        x = x + emg * e / e.std()
    return x * scale_uv * 1e-6
