"""Ground-truth simulations: does each metric measure frequency instability, or something else?

Signal = aperiodic 1/f^chi background + alpha rhythm + gamma bursts whose instantaneous
frequency follows an Ornstein-Uhlenbeck process (SD = jitter_hz) + optional EMG bursts.
Each validation sweep changes ONE factor and records every metric, so the paper can show which
metrics track true jitter and which are driven by amplitude, 1/f slope, peak frequency,
burst duration or muscle noise.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfiltfilt

BASE = dict(sf=250.0, dur_s=240.0, chi=1.5, alpha_amp=1.0, gamma_f0=36.0, gamma_amp=0.6,
            jitter_hz=2.0, jitter_tau_s=0.05, burst_rate=1.5, burst_dur_s=0.25,
            emg_level=0.0, scale_uv=10.0)


def _colored(n, sf, chi, rng):
    w = rng.standard_normal(n)
    W = np.fft.rfft(w)
    f = np.fft.rfftfreq(n, 1 / sf)
    f[0] = f[1]
    W *= 1.0 / (1.0 + f) ** (chi / 2)
    x = np.fft.irfft(W, n)
    return x / x.std()


def _ou(n, sf, tau, rng):
    a = np.exp(-1 / (tau * sf))
    e = rng.standard_normal(n) * np.sqrt(1 - a ** 2)
    x = np.empty(n); x[0] = rng.standard_normal()
    for i in range(1, n):
        x[i] = a * x[i - 1] + e[i]
    return x


def _bursts(n, sf, rate, dur, rng):
    env = np.zeros(n)
    k = rng.poisson(rate * n / sf)
    for on in rng.integers(0, n, size=k):
        L = max(4, int(rng.gamma(4.0, dur / 4.0) * sf))
        w = np.hanning(L)
        st, sp = on, min(n, on + L)
        env[st:sp] = np.maximum(env[st:sp], w[: sp - st])
    return env


def simulate(seed: int = 0, **kw) -> tuple[np.ndarray, float]:
    p = {**BASE, **kw}
    rng = np.random.default_rng(seed)
    sf, n = p["sf"], int(p["dur_s"] * p["sf"])
    t = np.arange(n) / sf
    bg = _colored(n, sf, p["chi"], rng)
    alpha = p["alpha_amp"] * np.sin(2 * np.pi * 10 * t + rng.uniform(0, 2 * np.pi)) * \
        (0.6 + 0.4 * _bursts(n, sf, 0.5, 2.0, rng))
    fr = p["gamma_f0"] + p["jitter_hz"] * _ou(n, sf, p["jitter_tau_s"], rng)
    phase = 2 * np.pi * np.cumsum(fr) / sf
    gam = p["gamma_amp"] * _bursts(n, sf, p["burst_rate"], p["burst_dur_s"], rng) * np.sin(phase)
    x = bg + alpha + gam
    if p["emg_level"] > 0:
        sos = butter(4, [20, min(120, 0.45 * sf)], btype="band", fs=sf, output="sos")
        emg = sosfiltfilt(sos, rng.standard_normal(n))
        emg = emg / emg.std() * p["emg_level"] * (0.3 + _bursts(n, sf, 0.2, 1.5, rng))
        x = x + emg
    return x * p["scale_uv"] * 1e-6, sf


SWEEPS = {
    "jitter_hz":   [0.0, 1.0, 2.0, 3.0, 4.0],      # the thing we WANT to measure
    "gamma_amp":   [0.2, 0.4, 0.6, 0.9, 1.2],      # nuisance: gamma power / SNR
    "chi":         [1.0, 1.5, 2.0, 2.5],           # nuisance: 1/f slope
    "gamma_f0":    [33.0, 36.0, 39.0],             # nuisance: peak frequency (AD peak is lower)
    "burst_dur_s": [0.1, 0.25, 0.5, 1.0],          # nuisance: burstiness
    "emg_level":   [0.0, 0.3, 0.6, 1.0],           # nuisance: muscle contamination
}
