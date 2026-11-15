"""Is there a gamma oscillation at all, and what are its damped-oscillator parameters? (label-free)

1. Aperiodic background: log10 P(f) = log10(A f^-chi + c), fitted on [fit_lo, max_fit_hz] excluding
   alpha (6-15 Hz), the gamma window (27-52 Hz) and line noise (+-3 Hz). max_fit_hz defaults to 65 Hz
   because ds004504's amplifier low-pass is 70 Hz (dataset README): fitting above it bends the model.
2. Presence test (the gate every mechanistic analysis depends on): per 4-s chunk, peak contrast =
   mean log-residual in 30-45 Hz minus the mean in the flanks (22-27 Hz and 53-62 Hz). A channel has
   an oscillation if the mean contrast >= presence_min_db (in dB) AND a one-sided t-test across chunks
   gives p < presence_alpha. Flank contrast guards against a smooth misfit of the background.
3. Damped-oscillator fit of the linear excess E(f) = P(f) - aperiodic(f) on 25-58 Hz:
   E(f) = a / ((f0^2 - f^2)^2 + (g f)^2)   (power spectrum of a noise-driven damped harmonic oscillator)
   osc_f0 (Hz), osc_width_hz = g (~ full width at half maximum), osc_q = f0 / g.
4. Vigilance (theory 4 confound/marker): log(alpha 8-12 / theta 4-8) power per 30-s window;
   vigilance_mean, vigilance_sd (instability of state) and vigilance_slope (per min, drowsiness trend).
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import welch
from scipy.stats import t as t_dist

OSC_METRICS = ["osc_present", "osc_contrast_db", "osc_contrast_p", "osc_f0", "osc_width_hz", "osc_q",
               "osc_fit_r2", "ap_exponent_65", "ap_floor_log10", "vigilance_mean", "vigilance_sd",
               "vigilance_slope"]


def _ap_model(f, logA, chi, logc):
    return np.log10(10 ** logA * f ** (-chi) + 10 ** logc)


def _ap_mask(fr, lo, hi, line):
    m = (fr >= lo) & (fr <= hi) & ~((fr >= 6) & (fr <= 15)) & ~((fr >= 27) & (fr <= 52))
    for k in (1, 2):
        m &= ~((fr >= line * k - 3) & (fr <= line * k + 3))
    return m


def fit_aperiodic(fr, psd, lo=3.0, hi=65.0, line=50.0):
    m = _ap_mask(fr, lo, hi, line) & (psd > 0)
    y = np.log10(psd[m])
    p0 = [y[0] + 1.0, 1.5, y.min() - 0.5]
    try:
        p, _ = curve_fit(_ap_model, fr[m], y, p0=p0, bounds=([-40, 0, -40], [10, 5, 10]), maxfev=20000)
    except Exception:
        return None
    return p


def _osc_model(f, la, f0, g):
    return 10 ** la / ((f0 ** 2 - f ** 2) ** 2 + (g * f) ** 2)


def channel_oscillation(x: np.ndarray, segments, sf: float, cfg_feat: dict, line: float = 50.0) -> dict:
    oc = cfg_feat.get("oscillation", {})
    hi = min(oc.get("max_fit_hz", 65.0), sf / 2 - 2)
    chunk = int(round(oc.get("chunk_s", 4.0) * sf))
    pieces = [x[a + i: a + i + chunk] for a, b in segments for i in range(0, b - a - chunk + 1, chunk)]
    out = {m: np.nan for m in OSC_METRICS}
    if len(pieces) < 5:
        return out
    P = []
    for pc in pieces:
        fr, p = welch(pc, sf, nperseg=min(len(pc), int(2 * sf)), noverlap=int(sf))
        P.append(p)
    P = np.asarray(P)
    psd = P.mean(0)
    ap = fit_aperiodic(fr, psd, oc.get("fit_lo_hz", 3.0), hi, line)
    if ap is None:
        return out
    out["ap_exponent_65"], out["ap_floor_log10"] = float(ap[1]), float(ap[2])
    base = _ap_model(np.maximum(fr, 0.5), *ap)
    res = np.log10(np.maximum(P, 1e-40)) - base[None]
    core = (fr >= 30) & (fr <= 45)
    flank = ((fr >= 22) & (fr <= 27)) | ((fr >= 53) & (fr <= min(62, hi)))
    con = 10 * (res[:, core].mean(1) - res[:, flank].mean(1))          # dB, per chunk
    mu, sd, n = con.mean(), con.std(ddof=1), len(con)
    tval = mu / (sd / np.sqrt(n)) if sd > 0 else 0.0
    pval = float(1 - t_dist.cdf(tval, n - 1))
    out["osc_contrast_db"], out["osc_contrast_p"] = float(mu), pval
    out["osc_present"] = float(mu >= oc.get("presence_min_db", 0.5) and pval < oc.get("presence_alpha", 0.01))
    m = (fr >= 25) & (fr <= 58) & ~((fr >= line - 3) & (fr <= line + 3))
    E = psd[m] - 10 ** base[m]
    if np.nanmax(E) > 0:
        scale = np.nanmax(E)
        En = E / scale                                            # fit in normalised units (E ~ 1e-12 V^2/Hz)
        f0_init = float(np.clip(fr[m][np.argmax(En)], 29, 49))
        best = None
        for g0 in (3.0, 8.0, 16.0):                               # a few starts: the width surface is not convex
            try:
                la0 = np.log10((g0 * f0_init) ** 2)
                pp, _ = curve_fit(_osc_model, fr[m], En, p0=[la0, f0_init, g0],
                                  bounds=([-10, 28, 1], [12, 50, 40]), maxfev=20000)
            except Exception:
                continue
            fit = _osc_model(fr[m], *pp)
            r2 = 1 - np.sum((En - fit) ** 2) / np.sum((En - En.mean()) ** 2)
            if best is None or r2 > best[1]:
                best = (pp, r2)
        if best is not None:
            pp, r2 = best
            out["osc_fit_r2"] = float(r2)
            if r2 >= oc.get("min_fit_r2", 0.3):
                out.update(osc_f0=float(pp[1]), osc_width_hz=float(pp[2]), osc_q=float(pp[1] / pp[2]))
    # vigilance per 30-s window (contiguous clean data concatenated in order)
    win = int(30 * sf)
    xx = np.concatenate([x[a:b] for a, b in segments])
    vals = []
    for i in range(0, len(xx) - win + 1, win):
        f2, p2 = welch(xx[i:i + win], sf, nperseg=int(2 * sf))
        a = p2[(f2 >= 8) & (f2 <= 12)].mean(); t = p2[(f2 >= 4) & (f2 < 8)].mean()
        vals.append(np.log(a / t))
    if len(vals) >= 3:
        vals = np.asarray(vals)
        out.update(vigilance_mean=float(vals.mean()), vigilance_sd=float(vals.std(ddof=1)),
                   vigilance_slope=float(np.polyfit(np.arange(len(vals)) * 0.5, vals, 1)[0]))
    return out


def oscillation_subject(data, segments, sf, ch_names, cfg_feat, line=50.0) -> dict:
    return {ch: channel_oscillation(data[i], segments, sf, cfg_feat, line) for i, ch in enumerate(ch_names)}
