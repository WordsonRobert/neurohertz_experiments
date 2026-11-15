"""Second mechanistic model family: a cycle-by-cycle PING map ("theory as stated").

The rate model (nh/mechsim.py) is a dynamical system whose predictions can differ from verbal
reasoning (it says weaker pyramidal->PV synapses make gamma LESS damped). This family instead writes
each gamma cycle down directly, so each theory acts exactly as the plan describes it. Fingerprints
from both families are compared; only predictions on which they AGREE are treated as firm, the
rest are reported as model-dependent.

Cycle n:   T_n = L_n + R_n - kappa * (T_{n-1} - T_ref)
  L_n  PV recruitment latency after the pyramidal volley: L0 / s + (sigma_L / s) * eps   (s = E->PV strength)
  R_n  recovery from PV inhibition: R0 * (D0 / D_n) ** eta + sigma_R * eps               (D_n = excitatory drive)
  kappa  SST feedback that pulls the next cycle back towards the reference length (dendritic inhibition
         timed to pyramidal bursts; Onorato et al. preprint 2023)
Cycle amplitude a_n = s * (D_n / D0) * B(t), B = slow log-normal burst envelope.
PV output failure (Nav1.1): with probability p_n the PV volley is missing; the cycle then ends after
L_n only (a short "slip" cycle) at 20% amplitude.

  T1 synapses_onto_pv : s = 1 - 0.5 k
  T2 nav11_pv_output  : p_n = 0.25 k * sigmoid((a_n - 1) / 0.25)            failure under load
  T3 erratic_drive    : D_n = D0 (1 + 0.25 k OU_1.5s)
  T4 acetylcholine    : D0 <- D0 (1 - 0.25 k);  D_n *= (1 + 0.15 k OU_8s)
  T5 sst_loss         : kappa <- kappa (1 - 0.7 k)
  T6 tau_silencing    : D0 <- D0 (1 - 0.25 k)
"""
from __future__ import annotations

import numpy as np

CBASE = dict(f_ref=38.0, L0=0.006, sigma_L=0.0025, sigma_R=0.0045, eta=0.6, kappa=0.3, D0=1.0,
             burst_tau_s=0.3, burst_sd=0.6)


def _ou_at(times, tau, rng):
    out = np.empty(len(times)); out[0] = rng.standard_normal()
    for i in range(1, len(times)):
        a = np.exp(-(times[i] - times[i - 1]) / tau)
        out[i] = a * out[i - 1] + np.sqrt(1 - a * a) * rng.standard_normal()
    return out


def subject_base(rng: np.random.Generator) -> dict:
    """A simulated person's own baseline: reference frequency +-1.5 Hz, noise and SST feedback +-15%."""
    c = dict(CBASE)
    c["f_ref"] = CBASE["f_ref"] + float(rng.normal(0, 1.5))
    for k in ("sigma_L", "sigma_R", "kappa", "burst_sd"):
        c[k] = CBASE[k] * float(np.exp(rng.normal(0, 0.15)))
    return c


def simulate_cycles(theory: str | None, k: float, dur_s: float = 120.0, fs: float = 250.0,
                    seed: int = 0, base: dict | None = None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    c = dict(CBASE if base is None else base)
    s, D0, kappa, fail, dr_fast, dr_slow = 1.0, c["D0"], c["kappa"], 0.0, 0.0, 0.0
    if theory == "synapses_onto_pv":
        s = 1 - 0.5 * k
    elif theory == "nav11_pv_output":
        fail = 0.25 * k
    elif theory == "erratic_drive":
        dr_fast = 0.25 * k
    elif theory == "acetylcholine":
        D0 *= (1 - 0.25 * k); dr_slow = 0.15 * k
    elif theory == "sst_loss":
        kappa *= (1 - 0.7 * k)
    elif theory == "tau_silencing":
        D0 *= (1 - 0.25 * k)
    elif theory is not None:
        raise KeyError(theory)
    T_ref = 1.0 / c["f_ref"]
    R0 = T_ref - c["L0"]
    n_max = int(dur_s * 80) + 10
    grid = np.arange(n_max) * T_ref                     # drive processes sampled at nominal cycle times
    ou_f, ou_s, ou_b = (_ou_at(grid, 1.5, rng), _ou_at(grid, 8.0, rng), _ou_at(grid, c["burst_tau_s"], rng))
    burst = np.exp(c["burst_sd"] * ou_b - 0.5 * c["burst_sd"] ** 2)
    t, Tprev, ends, amps = 0.0, T_ref, [], []
    i = 0
    while t < dur_s and i < n_max - 1:
        D = D0 * (1 + dr_fast * ou_f[i]) * (1 + dr_slow * ou_s[i])
        D = max(D, 0.05)
        a = s * (D / c["D0"]) * burst[i]
        L = c["L0"] / s + c["sigma_L"] / s * rng.standard_normal()
        failed = fail > 0 and rng.random() < fail / (1 + np.exp(-(a - 1) / 0.25))
        if failed:
            T = max(L, 0.004); a *= 0.2
        else:
            R = R0 * (c["D0"] / D) ** c["eta"] + c["sigma_R"] * rng.standard_normal()
            T = L + R - kappa * (Tprev - T_ref)
            T = min(max(T, 0.012), 0.08)
            Tprev = T
        t += T; ends.append(t); amps.append(a); i += 1
    ends = np.asarray(ends); amps = np.asarray(amps)
    n = int(dur_s * fs)
    ts = np.arange(n) / fs
    starts = np.r_[0.0, ends[:-1]]
    idx = np.clip(np.searchsorted(ends, ts, side="right"), 0, len(ends) - 1)
    phase = 2 * np.pi * (idx + (ts - starts[idx]) / (ends[idx] - starts[idx]))
    x = np.interp(ts, ends, amps) * np.cos(phase)
    x -= x.mean()
    return x / (x.std() + 1e-12)
