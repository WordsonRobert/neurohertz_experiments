"""Conventional spectral features (the comparators the GII must beat) + EMG/QC indices.

All per-subject, per-channel, label-blind.
"""
from __future__ import annotations

import warnings

import mne
import numpy as np


def _spectral_model(kw: dict):
    try:
        from specparam import SpectralModel
        return SpectralModel(verbose=False, **kw)
    except ImportError:                           # specparam 1.x / fooof fallback
        from fooof import FOOOF
        return FOOOF(verbose=False, **kw)


def welch_psd(data: np.ndarray, sfreq: float, win_s: float, fmax: float):
    n = int(round(win_s * sfreq))
    psd, fr = mne.time_frequency.psd_array_welch(data, sfreq, fmin=0.5, fmax=fmax, n_fft=n,
                                                 n_per_seg=n, n_overlap=0, average="median",
                                                 verbose=False)
    return psd, fr


def _line_mask(fr, line_freq, width=2.0):
    keep = np.ones_like(fr, dtype=bool)
    if line_freq:
        for h in np.arange(line_freq, fr.max() + line_freq, line_freq):
            keep &= np.abs(fr - h) > width
    return keep


def channel_spectral_features(psd_ch: np.ndarray, fr: np.ndarray, cfg: dict, line_freq) -> dict:
    sp = cfg["features"]["spectral"]
    out = {}
    tot = (fr >= 1) & (fr <= 45)
    total = np.trapezoid(psd_ch[tot], fr[tot])
    for name, (lo, hi) in sp["bands"].items():
        m = (fr >= lo) & (fr < hi)
        out[f"relpow_{name}"] = float(np.trapezoid(psd_ch[m], fr[m]) / total)
    out["theta_alpha_ratio"] = out["relpow_theta"] / out["relpow_alpha"]
    g = (fr >= cfg["features"]["gamma_band"][0]) & (fr <= cfg["features"]["gamma_band"][1])
    out["gamma_abs_logpow"] = float(np.log10(psd_ch[g].mean()))

    # aperiodic + peaks
    lo, hi = sp["specparam_range"]
    fm = _spectral_model(sp["specparam_kwargs"])
    rng = (fr >= lo) & (fr <= hi)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            fm.fit(fr[rng], psd_ch[rng], [lo, hi])
            ap = np.atleast_1d(fm.get_params("aperiodic"))
            peaks = np.atleast_2d(fm.get_params("peak"))
        except Exception:
            ap, peaks = np.array([np.nan, np.nan]), np.empty((0, 3))
    offset, expo = float(ap[0]), float(ap[-1])
    out["aperiodic_offset"], out["aperiodic_exponent"] = offset, expo
    peaks = peaks[~np.isnan(peaks).any(1)] if peaks.size else np.empty((0, 3))
    a = peaks[(peaks[:, 0] >= 7) & (peaks[:, 0] <= 14)] if len(peaks) else peaks
    out["alpha_peak_freq"] = float(a[np.argmax(a[:, 1]), 0]) if len(a) else np.nan
    gs = cfg["features"]["individual_band"]["search_hz"]
    gp = peaks[(peaks[:, 0] >= gs[0]) & (peaks[:, 0] <= gs[1])] if len(peaks) else peaks
    out["gamma_peak_freq"] = float(gp[np.argmax(gp[:, 1]), 0]) if len(gp) else np.nan
    out["gamma_peak_height"] = float(gp[:, 1].max()) if len(gp) else 0.0
    if np.isfinite(expo):
        resid = np.log10(psd_ch[g]) - (offset - expo * np.log10(fr[g]))
        out["gamma_osc_logpow"] = float(resid.mean())       # gamma power ABOVE the 1/f background
    else:
        out["gamma_osc_logpow"] = np.nan

    # EMG / high-frequency QC (only where the spectrum reaches the band)
    eb = sp["emg_band"]
    if fr.max() >= eb[1]:
        m = (fr >= eb[0]) & (fr <= eb[1]) & _line_mask(fr, line_freq)
        out["emg_logpow"] = float(np.log10(psd_ch[m].mean()))
        m2 = (fr >= 30) & (fr <= eb[1]) & _line_mask(fr, line_freq)
        out["hf_slope_30_90"] = float(np.polyfit(np.log10(fr[m2]), np.log10(psd_ch[m2]), 1)[0])
    else:
        out["emg_logpow"] = out["hf_slope_30_90"] = np.nan
    out.update(floor_fit(psd_ch, fr, cfg, line_freq))
    return out


def floor_fit(psd_ch: np.ndarray, fr: np.ndarray, cfg: dict, line_freq) -> dict:
    """Background = power law + constant floor:  P(f) = A * f^-chi + c   (fitted in log10 space).
    The floor c captures the high-frequency plateau (amplifier noise / tonic EMG) that biases a pure
    power-law fit (Gerster et al. 2022). Our extension: validate in simulation before relying on it.
    Returns the exponent, the floor, and gamma power ABOVE this background."""
    from scipy.optimize import curve_fit
    ff = cfg["features"]["spectral"].get("floor_fit", {"range": [3.0, 90.0], "exclude": [[6.0, 15.0]]})
    lo, hi = ff["range"][0], min(ff["range"][1], fr.max())
    m = (fr >= lo) & (fr <= hi) & _line_mask(fr, line_freq, 3.0)
    for a, b in ff.get("exclude", []):
        m &= ~((fr >= a) & (fr <= b))
    gb = cfg["features"]["gamma_band"]
    m &= ~((fr >= gb[0]) & (fr <= gb[1]))                       # never fit on the band we measure
    f, y = fr[m], np.log10(psd_ch[m] + 1e-30)

    def model(f, logA, chi, logc):
        return np.log10(10 ** logA * f ** (-chi) + 10 ** logc)
    p0 = [y[0] + 1.5 * np.log10(f[0]), 1.5, y[-1]]
    try:
        with warnings.catch_warnings():               # filters set in the parent do not reach joblib workers
            warnings.simplefilter("ignore")           # (OptimizeWarning: covariance not estimable - fit is still used)
            (logA, chi, logc), _ = curve_fit(model, f, y, p0=p0, maxfev=20000)
    except Exception:
        return {"floor_exponent": np.nan, "floor_log10": np.nan, "gamma_above_floor": np.nan}
    g = (fr >= gb[0]) & (fr <= gb[1])
    resid = np.log10(psd_ch[g] + 1e-30) - model(fr[g], logA, chi, logc)
    return {"floor_exponent": float(chi), "floor_log10": float(logc),
            "gamma_above_floor": float(resid.mean()),
            # frequency where the power law falls to the floor; NaN = no floor inside the measured range
            "floor_onset_hz": (lambda o: float(o) if np.isfinite(o) and o <= fr.max() else np.nan)(
                10 ** ((logA - logc) / chi) if chi > 0 and abs((logA - logc) / chi) < 300 else np.nan)}


def irasa_exponent(data: np.ndarray, sf: float, ch_names, cfg: dict) -> dict:
    """IRASA (Wen & Liu 2016) aperiodic exponent per channel via YASA, same range as specparam."""
    import yasa
    lo, hi = cfg["features"]["spectral"]["specparam_range"]
    _f, _ap, _osc, fit = yasa.irasa(data=data * 1e6, sf=sf, ch_names=list(ch_names), band=(lo, hi),
                                    win_sec=cfg["features"]["spectral"]["welch_s"], return_fit=True)
    fit = fit.set_index("Chan")
    return {ch: {"irasa_exponent": float(-fit.loc[ch, "Slope"]), "irasa_r2": float(fit.loc[ch, "R^2"])}
            for ch in ch_names}


def roi_gamma_peak(psd: np.ndarray, fr: np.ndarray, roi_idx: list[int], cfg: dict) -> float:
    """Gamma peak of the ROI-average spectrum (for the individual-band sensitivity analysis)."""
    sp = cfg["features"]["spectral"]
    lo, hi = sp["specparam_range"]
    rng = (fr >= lo) & (fr <= hi)
    fm = _spectral_model(sp["specparam_kwargs"])
    try:
        fm.fit(fr[rng], psd[roi_idx][:, rng].mean(0), [lo, hi])
        peaks = np.atleast_2d(fm.get_params("peak"))
    except Exception:
        return np.nan
    gs = cfg["features"]["individual_band"]["search_hz"]
    peaks = peaks[~np.isnan(peaks).any(1)] if peaks.size else np.empty((0, 3))
    gp = peaks[(peaks[:, 0] >= gs[0]) & (peaks[:, 0] <= gs[1])] if len(peaks) else peaks
    return float(gp[np.argmax(gp[:, 1]), 0]) if len(gp) else np.nan
