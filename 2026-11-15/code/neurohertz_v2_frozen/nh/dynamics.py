"""Mechanism-oriented descriptors of gamma instantaneous frequency (label-free).

Computed from the same per-segment estimator output as nh/gamma.py (raw IF f, median-smoothed IF fm,
envelope A), on real data AND on every IAAFT surrogate, so `<feature>_z` / `<feature>_excess` measure
what is left after a linear-Gaussian process with the SAME spectrum and amplitude distribution has
been accounted for (the "noise baseline": phase slips at low amplitude happen in noise too).

  fast_sd            SD of cycle-scale IF: fm minus its amplitude-weighted 1 s running mean (gated samples)
  slow_sd            SD of that 1 s running mean, sampled at 10 Hz (1-10 s "wander")
  slow_frac          slow_sd^2 / (slow_sd^2 + fast_sd^2)
  slow_tau_s         e-folding time of the slow-IF autocorrelation (s, capped at 20)
  if_env_coupling    Spearman(slow IF, slow log-envelope): drive-like co-modulation (theory 3)
  slip_rate          phase slips per minute: runs where raw IF leaves [band_lo - m, band_hi + m]
  slip_rate_highamp  slips per minute of high-envelope time (local envelope >= its 80th percentile):
                     failure under load (theory 2)
  tail_frac          share of gated raw-IF samples beyond 4 robust SD from the median (heavy tails)
  jitter_amp_slope   slope of the robust IF spread across envelope quintiles vs log10 envelope
                     (negative = jitter falls as the rhythm strengthens)
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.stats import spearmanr

DYN_METRICS = ["fast_sd", "slow_sd", "slow_frac", "slow_tau_s", "if_env_coupling", "slip_rate",
               "slip_rate_highamp", "tail_frac", "jitter_amp_slope"]
DYN_SURR = ["fast_sd", "slow_sd", "slow_frac", "if_env_coupling", "slip_rate", "slip_rate_highamp",
            "tail_frac", "jitter_amp_slope"]


def _runs(mask):
    d = np.diff(np.r_[0, mask.astype(np.int8), 0])
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))


def _acf_tau(series_list, dt, max_lag_s=20.0):
    max_lag = int(max_lag_s / dt)
    num = np.zeros(max_lag + 1); den = np.zeros(max_lag + 1)
    for s in series_list:
        s = s - s.mean()
        v = np.dot(s, s)
        if len(s) < 10 or v <= 0:
            continue
        for L in range(min(max_lag, len(s) - 1) + 1):
            num[L] += np.dot(s[: len(s) - L], s[L:]) / v * (len(s) - L)
            den[L] += len(s) - L
    ok = den > 0
    if not ok[1:].any():
        return np.nan
    acf = np.where(ok, num / np.maximum(den, 1), np.nan)
    below = np.flatnonzero(acf[1:] < np.exp(-1))
    return float((below[0] + 1) * dt) if len(below) else float(max_lag_s)


def dynamics_from_segments(segs, sf: float, band, cfg_feat: dict, gate: float) -> dict:
    """segs: list of (f_raw, f_med, A, xg) per clean segment (edges already trimmed)."""
    dc = cfg_feat.get("dynamics", {})
    w = max(3, int(round(dc.get("slow_window_s", 1.0) * sf)))
    dec = max(1, int(round(sf / dc.get("slow_fs", 10.0))))
    margin = dc.get("slip_margin_hz", 10.0)
    lo, hi = band[0] - margin, band[1] + margin
    fast, slow_if, slow_env, slow_series = [], [], [], []
    n_slip, n_slip_hi, t_total, t_hi = 0, 0, 0.0, 0.0
    allA = np.concatenate([s[2] for s in segs])
    env_hi = np.percentile(uniform_filter1d(allA, max(3, int(0.1 * sf))), 80)
    tails, fm_all, A_all = [], [], []
    for f, fm, A, _ in segs:
        if len(f) < 2 * w:
            continue
        W = A ** 2
        slow = uniform_filter1d(W * fm, w) / (uniform_filter1d(W, w) + 1e-30)
        logA = uniform_filter1d(np.log(A + 1e-30), w)
        core = slice(w // 2, len(f) - w // 2)
        g = A[core] > gate
        fast.append((fm[core] - slow[core])[g])
        si, se = slow[core][::dec], logA[core][::dec]
        slow_series.append(si); slow_if.append(si - si.mean()); slow_env.append(se - se.mean())
        out_band = (f < lo) | (f > hi)
        runs = _runs(out_band)
        locA = uniform_filter1d(A, max(3, int(0.1 * sf)))
        n_slip += len(runs)
        n_slip_hi += sum(1 for a, _ in runs if locA[a] >= env_hi)
        t_total += len(f) / sf
        t_hi += np.sum(locA >= env_hi) / sf
        tails.append(f[A > gate]); fm_all.append(fm); A_all.append(A)
    if not fast:
        return {m: np.nan for m in DYN_METRICS}
    fast = np.concatenate(fast)
    si, se = np.concatenate(slow_if), np.concatenate(slow_env)
    fast_sd = float(np.std(fast)) if len(fast) > 50 else np.nan
    slow_sd = float(np.std(np.concatenate(slow_series))) if len(si) > 10 else np.nan
    raw = np.concatenate(tails)
    med = np.median(raw); rsd = 1.4826 * np.median(np.abs(raw - med)) + 1e-12
    fm_all, A_all = np.concatenate(fm_all), np.concatenate(A_all)
    qs = np.percentile(A_all, [0, 20, 40, 60, 80, 100])
    xs, ys = [], []
    for a, b in zip(qs[:-1], qs[1:]):
        m = (A_all >= a) & (A_all <= b)
        if m.sum() > 50:
            v = fm_all[m]
            xs.append(np.log10(np.median(A_all[m]) + 1e-30)); ys.append(1.4826 * np.median(np.abs(v - np.median(v))))
    return {
        "fast_sd": fast_sd,
        "slow_sd": slow_sd,
        "slow_frac": float(slow_sd ** 2 / (slow_sd ** 2 + fast_sd ** 2)) if np.isfinite(fast_sd * slow_sd) else np.nan,
        "slow_tau_s": _acf_tau([s for s in slow_series if len(s) > 20], dec / sf),
        "if_env_coupling": float(spearmanr(si, se)[0]) if (len(si) > 20 and np.std(si) > 0 and np.std(se) > 0) else np.nan,
        "slip_rate": float(n_slip / (t_total / 60)) if t_total > 0 else np.nan,
        "slip_rate_highamp": float(n_slip_hi / (t_hi / 60)) if t_hi > 1 else np.nan,
        "tail_frac": float(np.mean(np.abs(raw - med) > 4 * rsd)) if len(raw) > 100 else np.nan,
        "jitter_amp_slope": float(np.polyfit(xs, ys, 1)[0]) if (len(xs) >= 3 and np.ptp(xs) > 1e-9) else np.nan,
    }
