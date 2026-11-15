"""Gamma instantaneous-frequency (IF) instability metrics.

Per channel, per subject, label-blind. Several CANDIDATE estimators are computed because
simulations (nh/simulate.py) show that naive IF variability is driven by gamma amplitude and
burstiness at least as much as by true frequency jitter. The primary metric is chosen by
scripts/02_simulation_validation.py on ground-truth simulations only (never on labels),
then written into config before freezing.

  x_g(t)        zero-phase FIR band-pass of the clean signal in the gamma band
  A(t), phi(t)  envelope and unwrapped phase of the analytic signal
  f(t)          (1/2pi) dphi/dt  (raw), f_med(t) = median-filtered f(t)
  gate          A(t) > P_q(A), q = amp_gate_percentile (subject's own envelope distribution)

Candidate estimators
  if_sd, if_mad, if_iqr  spread of f_med over gated samples
  if_awsd                amplitude^2-weighted SD of f_med (all samples)
  cycle_cv               CV of zero-crossing cycle periods in gated cycles
  burst_if_sd            mean within-burst SD of f_med (bursts: A > k*median(A) for >= 3 cycles)
  burst_freq_sd          SD of burst mean frequencies (between-burst dispersion)
  xjit_var               SNR-extrapolated IF variance: robust var(f | A) regressed on 1/A^2 across
                         amplitude bins; intercept = IF variance at infinite SNR. For any Gaussian
                         (spectrum-only) process the intercept is ~0 (Rice), so it targets jitter.
  legacy_std             OLD NeuroHertz-style: SD of raw f within 25-80 Hz, no gating (reference only)

Surrogate normalisation (IAAFT, spectrum + amplitude distribution preserved):
  <m>_z = (m_real - mean(m_surr)) / sd(m_surr)   for m in SURR_METRICS
  gii_z is an alias of if_sd_z (the original GII definition).
"""
from __future__ import annotations

import zlib

import numpy as np
from mne.filter import filter_data
from scipy.ndimage import median_filter
from scipy.signal import hilbert

from .dynamics import DYN_METRICS, DYN_SURR, dynamics_from_segments
from .surrogates import iaaft, iaaft_chunked

METRICS = ["if_sd", "if_mad", "if_iqr", "if_median", "if_awsd", "cycle_cv", "burst_if_sd",
           "burst_freq_sd", "burst_rate", "burst_dur", "xjit_var", "env_mean", "env_cv", "legacy_std"]
SURR_METRICS = ["if_sd", "cycle_cv", "burst_if_sd", "burst_freq_sd", "xjit_var"] + DYN_SURR
METRICS = METRICS + DYN_METRICS
BURST_K = 2.0          # burst threshold, multiples of the median envelope
BURST_MIN_CYCLES = 3
XJIT_BINS = 10
XJIT_Q_LO = 50.0


def subject_rng(seed: int, subject: str) -> np.random.Generator:
    """Deterministic per-subject RNG; independent of processing order and of labels."""
    return np.random.default_rng([int(seed), zlib.crc32(subject.encode())])


def _bandpass(x: np.ndarray, sf: float, band, trans: float) -> np.ndarray:
    return filter_data(x.astype(np.float64), sf, band[0], band[1], method="fir",
                       l_trans_bandwidth=trans, h_trans_bandwidth=trans, phase="zero",
                       fir_design="firwin", verbose="ERROR")


def _runs(mask: np.ndarray):
    d = np.diff(np.concatenate([[0], mask.astype(np.int8), [0]]))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def _cycle_periods(xg: np.ndarray, amp: np.ndarray, sf: float, gate: float, band) -> np.ndarray:
    idx = np.where((xg[:-1] < 0) & (xg[1:] >= 0))[0]
    if len(idx) < 3:
        return np.array([])
    zc = idx + (-xg[idx] / (xg[idx + 1] - xg[idx]))
    per = np.diff(zc) / sf
    keep = np.array([amp[int(a):int(np.ceil(b))].mean() > gate if np.ceil(b) > int(a) else False
                     for a, b in zip(zc[:-1], zc[1:])], dtype=bool)
    per = per[keep]
    lo, hi = 1 / (band[1] * 1.5), 1 / (band[0] / 1.5)
    return per[(per > lo) & (per < hi)]


def _xjit(f: np.ndarray, A: np.ndarray) -> float:
    if len(A) < 1000:
        return np.nan
    qs = np.percentile(A, np.linspace(XJIT_Q_LO, 99.5, XJIT_BINS + 1))
    xs, vs, ws = [], [], []
    for lo, hi in zip(qs[:-1], qs[1:]):
        m = (A >= lo) & (A < hi)
        if m.sum() < 50:
            continue
        ff = f[m]
        a = A[m]
        a = a[a > 0]                                   # some estimators (SST ridge) return exact zeros
        if len(a) < 50:
            continue
        mad = np.median(np.abs(ff - np.median(ff))) * 1.4826
        xs.append(np.mean(1.0 / a ** 2)); vs.append(mad ** 2); ws.append(m.sum())
    xs, vs, ws = (np.asarray(v, float) for v in (xs, vs, ws))
    ok = np.isfinite(xs) & np.isfinite(vs)
    xs, vs, ws = xs[ok], vs[ok], ws[ok]
    if len(xs) < 4 or np.ptp(xs) <= 0:
        return np.nan
    xs = xs / np.median(xs)
    try:
        _, b0 = np.polyfit(xs, vs, 1, w=np.sqrt(ws))
    except (np.linalg.LinAlgError, ValueError):     # a secondary metric must never fail a whole subject
        return np.nan
    return float(b0)


# ---------------------------------------------------------------- IF estimators
def _median_smooth(f: np.ndarray, sf: float, cfg_feat: dict) -> np.ndarray:
    """single: one median filter (if_median_filter_ms). multi: Cohen (2014) frequency sliding -
    median filters at n widths up to max_ms, then the median across them."""
    m = cfg_feat.get("if_median", {"mode": "single"})
    if m.get("mode", "single") == "multi":
        widths = np.linspace(m.get("min_ms", 10.0), m["max_ms"], m.get("n", 10))
        outs = []
        for w in widths:
            n = max(1, int(round(w / 1000 * sf)) | 1)
            outs.append(median_filter(f, size=n, mode="nearest") if n > 1 else f)
        return np.median(np.vstack(outs), axis=0)
    n = max(1, int(round(cfg_feat["if_median_filter_ms"] / 1000 * sf)) | 1)
    return median_filter(f, size=n, mode="nearest") if n > 1 else f


def _est_hilbert(x, sf, band, cfg_feat):
    xg = _bandpass(x, sf, band, cfg_feat["filter_transition_hz"])
    z = hilbert(xg)
    amp = np.abs(z)
    f = np.diff(np.unwrap(np.angle(z))) * sf / (2 * np.pi)
    return f, 0.5 * (amp[1:] + amp[:-1]), xg[1:]


def _est_sst(x, sf, band, cfg_feat):
    """Synchrosqueezed CWT (Daubechies, Lu & Wu 2011); frequency = ridge of |Tx| inside the band."""
    from ssqueezepy import ssq_cwt
    xg = _bandpass(x, sf, band, cfg_feat["filter_transition_hz"])
    # unit-SD input: ssqueezepy's coefficient threshold is ABSOLUTE, so EEG in volts (~1e-6) would be
    # zeroed almost everywhere in the gamma band (found on ds004504: 80-96% zero ridge amplitude)
    s = float(np.std(x)) or 1.0
    Tx, _Wx, ssq_freqs, _scales = ssq_cwt(x.astype(np.float64) / s, fs=sf)
    ssq_freqs = np.asarray(ssq_freqs, float)
    rows = np.where((ssq_freqs >= band[0]) & (ssq_freqs <= band[1]))[0]
    ridge = rows[np.argmax(np.abs(Tx[rows]), axis=0)]
    f = ssq_freqs[ridge]
    A = np.abs(Tx[ridge, np.arange(Tx.shape[1])]).astype(float)
    A = A / (np.median(A) + 1e-30) * np.median(np.abs(hilbert(xg)))    # band-pass amplitude scale
    return f[1:], A[1:], xg[1:]


def _est_vmd(x, sf, band, cfg_feat):
    """VMD with FIXED K and alpha (no per-subject tuning); mode = the one whose centre frequency
    lies in the band, closest to its centre; then Hilbert on that mode."""
    from vmdpy import VMD
    v = {"K": 3, "alpha": 2000, "prefilter_hz": [22.0, 58.0], **cfg_feat.get("vmd", {})}
    # Fixed design: pre-filter to the band plus its flanks (the same flanks as the presence test) and
    # decompose into K = 3 modes (low flank / gamma / high flank). On broadband 1/f EEG, K = 8 modes
    # straddled 30-45 Hz and the 'gamma' mode sat near 48 Hz; K = 3 on the pre-filtered signal tracks it
    # and is ~25x faster.
    if v.get("prefilter_hz"):
        x = _bandpass(x, sf, tuple(v["prefilter_hz"]), cfg_feat["filter_transition_hz"])
    # unit-SD input: vmdpy's convergence tolerance is ABSOLUTE, so EEG in volts stops after one
    # iteration with all-zero modes (found on ds004504). Modes are scaled back afterwards.
    s = float(np.std(x)) or 1.0
    xx = x.astype(np.float64) / s
    if len(xx) % 2:
        xx = xx[:-1]
    u, _, _omega = VMD(xx, v["alpha"], 0.0, v["K"], 0, 1, 1e-7)
    # the gamma mode = the mode carrying the most power INSIDE the band (fixed rule; VMD centre
    # frequencies often sit just outside 30-45 Hz, so 'centre frequency in band' is unreliable)
    fr = np.fft.rfftfreq(u.shape[1], 1 / sf)
    inb = (fr >= band[0]) & (fr <= band[1])
    k = int(np.argmax((np.abs(np.fft.rfft(u, axis=1)) ** 2)[:, inb].sum(axis=1)))
    mode = u[k] * s
    if len(mode) < len(x):
        mode = np.append(mode, mode[-1])
    z = hilbert(mode)
    amp = np.abs(z)
    f = np.diff(np.unwrap(np.angle(z))) * sf / (2 * np.pi)
    return f, 0.5 * (amp[1:] + amp[:-1]), mode[1:]


ESTIMATORS = {"hilbert": _est_hilbert, "sst": _est_sst, "vmd": _est_vmd}


def match_chunks(x: np.ndarray, segments, sf: float, chunk_s: float, search_s: float = 0.3):
    """Split each segment into ~chunk_s pieces whose END matches its START in value and slope
    (Schreiber & Schmitz: avoids end-point mismatch in Fourier surrogates). Uses the real signal only."""
    chunk, search = int(round(chunk_s * sf)), int(round(search_s * sf))
    dx = np.gradient(x)
    out = []
    for a, b in segments:
        st = a
        def best_end(lo, hi):
            # chunk x[st:e] ends at sample e-1: match x[e-1], dx[e-1] to x[st], dx[st]
            cand = np.arange(max(lo, st + 2), hi + 1)
            sx, sd = np.std(x[st:hi]) + 1e-30, np.std(dx[st:hi]) + 1e-30
            cost = np.abs(x[cand - 1] - x[st]) / sx + np.abs(dx[cand - 1] - dx[st]) / sd
            return int(cand[np.argmin(cost)])
        while b - st > 1.5 * chunk:
            e = best_end(st + chunk - search, min(st + chunk + search, b - chunk // 2))
            out.append((st, e)); st = e
        # last piece: trim at most `search` samples off its tail to get a matching end
        out.append((st, best_end(b - search, b) if b - st > 2 * search else b))
    return out


def if_metrics_channel(x: np.ndarray, segments, sf: float, band, cfg_feat: dict) -> dict:
    est = ESTIMATORS[cfg_feat.get("if_estimator", "hilbert")]
    trim = int(round(cfg_feat["edge_trim_s"] * sf))
    segs = []
    for a, b in segments:
        if b - a <= 2 * trim + 10:
            continue
        f, A, xg = est(x[a:b], sf, band, cfg_feat)
        fm = _median_smooth(f, sf, cfg_feat)
        sl = slice(trim, len(f) - trim)
        segs.append((f[sl], fm[sl], A[sl], xg[sl]))
    if not segs:
        return {m: np.nan for m in METRICS}
    f, fm, A = (np.concatenate([s[i] for s in segs]) for i in range(3))
    gate = np.percentile(A, cfg_feat["amp_gate_percentile"])
    fg = fm[A > gate]
    if fg.size < 50:                     # estimator returned (almost) no usable amplitude on this channel
        return {m: np.nan for m in METRICS}
    w = A ** 2
    mu_w = np.sum(w * fm) / np.sum(w)
    q75, q25 = np.percentile(fg, [75, 25])
    periods = np.concatenate([_cycle_periods(s[3], s[2], sf, gate, band) for s in segs])

    # bursts (within segments only)
    thr = BURST_K * np.median(A)
    centre = 0.5 * (band[0] + band[1])
    min_len = int(np.ceil(BURST_MIN_CYCLES / centre * sf))
    within, means, lens = [], [], []
    for fs_, fms, As, _ in segs:
        for a, b in _runs(As > thr):
            if b - a >= min_len:
                seg_f = fms[a:b]
                within.append(np.std(seg_f)); means.append(np.mean(seg_f)); lens.append(b - a)
    total_s = len(A) / sf
    leg = f[(f > 25) & (f < 80)]
    return {
        "if_sd": float(np.std(fg)),
        "if_mad": float(np.median(np.abs(fg - np.median(fg))) * 1.4826),
        "if_iqr": float(q75 - q25),
        "if_median": float(np.median(fg)),
        "if_awsd": float(np.sqrt(np.sum(w * (fm - mu_w) ** 2) / np.sum(w))),
        "cycle_cv": float(np.std(periods) / np.mean(periods)) if len(periods) > 20 else np.nan,
        "burst_if_sd": float(np.average(within, weights=lens)) if len(within) >= 5 else np.nan,
        "burst_freq_sd": float(np.std(means)) if len(means) >= 5 else np.nan,
        "burst_rate": float(len(lens) / total_s),
        "burst_dur": float(np.mean(lens) / sf) if lens else np.nan,
        "xjit_var": _xjit(f, A),
        "env_mean": float(A.mean() * 1e6),
        "env_cv": float(A.std() / A.mean()),
        "legacy_std": float(np.std(leg)) if len(leg) > 100 else np.nan,
        **dynamics_from_segments(segs, sf, band, cfg_feat, gate),
    }


def _spectral_mismatch(x, xs, sf, band) -> float:
    X, S = np.abs(np.fft.rfft(x)), np.abs(np.fft.rfft(xs))
    fr = np.fft.rfftfreq(len(x), 1 / sf)
    m = (fr >= band[0]) & (fr <= band[1])
    return float(np.sqrt(np.mean((S[m] - X[m]) ** 2)) / (np.sqrt(np.mean(X[m] ** 2)) + 1e-30))


def gii_subject(data: np.ndarray, segments, sf: float, ch_names: list[str], band,
                cfg_feat: dict, rng: np.random.Generator, n_surr: int | None = None) -> dict:
    """Real + surrogate-normalised metrics for every channel: {channel: {metric: value}}."""
    sc = cfg_feat["surrogates"]
    n_surr = sc["n"] if n_surr is None else n_surr
    out = {}
    for ci, ch in enumerate(ch_names):
        x = data[ci]
        # chunks with matched end points; real and surrogate are measured on the SAME chunks,
        # and every chunk edge (seam) is trimmed in both (if_metrics_channel trims each piece)
        chunks = (match_chunks(x, segments, sf, sc["chunk_s"], sc.get("seam_search_s", 0.3))
                  if sc.get("seam_matching", True) else segments)
        real = if_metrics_channel(x, chunks, sf, band, cfg_feat)
        surr = {m: [] for m in SURR_METRICS}
        mism = []
        for _ in range(n_surr):
            xs = np.empty_like(x)
            for a, b in chunks:
                xs[a:b] = iaaft(x[a:b], rng, sc["iterations"])
                mism.append(_spectral_mismatch(x[a:b], xs[a:b], sf, band))
            ms = if_metrics_channel(xs, chunks, sf, band, cfg_feat)
            for m in SURR_METRICS:
                surr[m].append(ms[m])
        res = dict(real)
        if n_surr > 1:
            for m in SURR_METRICS:
                v = np.asarray(surr[m], float)
                v = v[np.isfinite(v)]
                if len(v) > 1 and np.isfinite(real[m]) and v.std(ddof=1) > 0:
                    res[f"{m}_surr_mean"] = float(v.mean())
                    res[f"{m}_z"] = float((real[m] - v.mean()) / v.std(ddof=1))
                    res[f"{m}_excess"] = float(real[m] - v.mean())
                else:
                    res[f"{m}_surr_mean"] = res[f"{m}_z"] = res[f"{m}_excess"] = np.nan
            res["gii_z"] = res["if_sd_z"]
        # IAAFT accuracy: relative RMS difference of the gamma-band amplitude spectrum (surrogate vs real)
        res["surr_spectral_mismatch"] = float(np.median(mism)) if mism else np.nan
        out[ch] = res
    return out
