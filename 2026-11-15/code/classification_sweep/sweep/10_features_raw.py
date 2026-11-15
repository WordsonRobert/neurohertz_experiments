"""Stage 10 (label-free): raw-level measures for the elimination tree, per subject.

For each cached subject and reference (csd = frozen primary, avg = comparison):
  spectra        log10 PSD per channel at 0.5 Hz (2-s epochs, Hann), 1-70 Hz
  spectra_lowemg the same from each person's lowest-EMG 50% and 25% of epochs (E1)
  irasa          fractal (aperiodic) and periodic parts, 2-47.5 Hz (E3)
  vigilance      per-epoch alpha/theta; ROI 30-48 Hz power inside 4 global vigilance strata (E4)
  bursts (csd)   every 30-48 Hz burst with its descriptors (classifying the instabilities; E1, E2, E6)
  transients     sharp-transient candidates (avg ref, 1-70 Hz) and 30-48 Hz power without them (E6)
  coupling (csd) theta->gamma and alpha->gamma PAC (Tort MI) and alpha 1:4 phase locking, each as a z vs
                 circular time-shift surrogates (E5)
Output: cache/<ds>/<variant>/feat/<sub>.npz and .../bursts/<sub>.csv.gz
"""
from __future__ import annotations
import argparse, json, time, traceback
from fractions import Fraction
from pathlib import Path
import numpy as np, pandas as pd
from scipy.signal import firwin, filtfilt, hilbert, resample_poly, periodogram, find_peaks
from joblib import Parallel, delayed

from common import (variant_dir, load_clean, csd_transform, save_npz, REGION, REGIONS, ROI, EPOCH_S,
                    LINE_EXCL, jsonable)

GAMMA = (30.0, 48.0)
EMG_BAND = (53.0, 68.0)          # above the notch, below the 70 Hz hardware low-pass of ds004504
SEED = 20261115
NFFT_IRASA = 1024                # common zero-padded FFT length so original / up / down spectra share a grid


# ------------------------------------------------------------------ helpers
def epochs_of(x: np.ndarray, sf: float) -> np.ndarray:
    """Clean data are concatenated 2-s epochs, so epoch k is samples [k*n, (k+1)*n)."""
    n = int(round(EPOCH_S * sf))
    k = x.shape[-1] // n
    return x[..., : k * n].reshape(*x.shape[:-1], k, n)


def epoch_psd(x: np.ndarray, sf: float):
    """x (..., n_ep, n) -> freqs, psd (..., n_ep, n_f) with a Hann window (0.5 Hz bins)."""
    f, p = periodogram(x, sf, window="hann", axis=-1, detrend="constant")
    return f, p


def filt_len(sf, lo, trans=None):
    """Hamming-window FIR length for the given transition width (MNE-style 3.3/trans rule), always odd."""
    trans = trans or max(1.0, 0.15 * lo)
    return int(3.3 * sf / trans) | 1


def bandpass(x, sf, lo, hi, trans=None):
    nt = filt_len(sf, lo, trans)
    b = firwin(nt, [lo, hi], pass_zero=False, fs=sf)
    return filtfilt(b, [1.0], x, axis=-1, padlen=min(3 * nt, x.shape[-1] - 1))


def per_segment(x, segments, fn, edge):
    """Apply fn to each contiguous segment (filters never cross epoch-rejection gaps); mask 'edge' samples."""
    out = np.full(x.shape, np.nan, dtype=complex if fn is hilbert else float)
    for a, b in segments:
        if b - a <= 2 * edge + 10:
            continue
        y = fn(x[..., a:b])
        y[..., :edge] = np.nan
        y[..., -edge:] = np.nan
        out[..., a:b] = y
    return out


def analytic(x1, segments, sf, lo, hi, trans=None, edge=0):
    """Per contiguous segment: band-pass then Hilbert (never across rejection gaps). The first and last
    max(edge, half the filter length) samples of each segment are set to NaN: within half a filter length of a
    segment end the output depends on the reflection padding, not on data (AUDIT 2026-11-15: the mask was
    0.25 s, shorter than the 0.37 s half-length of the 30-48 Hz filter)."""
    edge = max(edge, filt_len(sf, lo, trans) // 2)
    out = np.full(x1.shape, np.nan, dtype=complex)
    for a, b in segments:
        if b - a <= 2 * edge + 10:
            continue
        z = hilbert(bandpass(x1[a:b], sf, lo, hi, trans))
        if edge:
            z[:edge] = np.nan; z[-edge:] = np.nan
        out[a:b] = z
    return out


def lowpass_segments(x, segments, sf, fc=70.0, edge=0):
    nt = int(3.3 * sf / 5.0) | 1
    b = firwin(nt, fc, fs=sf)
    edge = max(edge, nt // 2)                      # AUDIT: never keep samples that depend on the padding
    out = np.full(x.shape, np.nan)
    for a, e in segments:
        if e - a <= max(2 * edge + 10, 3 * nt):
            continue
        y = filtfilt(b, [1.0], x[..., a:e], axis=-1)
        if edge:
            y[..., :edge] = np.nan; y[..., -edge:] = np.nan
        out[..., a:e] = y
    return out


def irasa(ep: np.ndarray, sf: float, hset=np.arange(1.1, 1.95, 0.05)):
    """IRASA (Wen & Liu 2016) on 2-s epochs. ep (ch, n_ep, n). Returns f, mixed, fractal (ch, n_f)."""
    # Resampled copies are analysed AT THE ORIGINAL RATE (as in YASA): an oscillation at f0 moves to f0/h and
    # f0*h while a power law only rescales, so the geometric mean of the pair keeps the fractal part.
    kw = dict(fs=sf, window="hann", nfft=NFFT_IRASA, axis=-1, detrend="constant")
    f, mixed = periodogram(ep, **kw)
    mixed = mixed.mean(-2)
    fr = []
    for h in hset:
        fr_h = Fraction(float(h)).limit_denominator(20)
        up = resample_poly(ep, fr_h.numerator, fr_h.denominator, axis=-1)
        dn = resample_poly(ep, fr_h.denominator, fr_h.numerator, axis=-1)
        _, pu = periodogram(up, **kw)
        _, pd_ = periodogram(dn, **kw)
        fr.append(np.sqrt(pu.mean(-2) * pd_.mean(-2)))
    return f, mixed, np.median(np.stack(fr), 0)


def phase_surrogate(x, rng):
    X = np.fft.rfft(x)
    ph = rng.uniform(0, 2 * np.pi, X.shape)
    ph[..., 0] = 0
    return np.fft.irfft(np.abs(X) * np.exp(1j * ph), n=x.shape[-1])


def tort_mi(phase, amp, nb=18):
    bins = np.linspace(-np.pi, np.pi, nb + 1)
    idx = np.clip(np.digitize(phase, bins) - 1, 0, nb - 1)
    m = np.bincount(idx, weights=amp, minlength=nb) / np.maximum(np.bincount(idx, minlength=nb), 1)
    p = m / m.sum()
    return float((np.log(nb) + np.sum(p * np.log(p + 1e-300))) / np.log(nb))


def shift_z(stat_fn, a, b, sf, rng, n=100, min_shift_s=1.0):
    """z of stat_fn(a, b) against circular time shifts of b (keeps each signal's own structure)."""
    obs = stat_fn(a, b)
    L = len(b); lo = int(min_shift_s * sf)
    if L < 3 * lo:
        return obs, np.nan
    null = np.array([stat_fn(a, np.roll(b, int(rng.integers(lo, L - lo)))) for _ in range(n)])
    return obs, float((obs - null.mean()) / (null.std(ddof=1) + 1e-12))


def iaf_from_psd(f, logp_roi):
    """Individual alpha frequency: peak of the 1/f-detrended ROI spectrum in 7-13 Hz."""
    fit = ((f >= 2) & (f <= 40)) & ~((f >= 6) & (f <= 14))
    c = np.polyfit(np.log10(f[fit]), logp_roi[fit], 1)
    res = logp_roi - np.polyval(c, np.log10(np.maximum(f, 1e-3)))
    m = (f >= 7) & (f <= 13)
    return float(f[m][np.argmax(res[m])])


def sp_split(f, psd, fmin=2.0, fmax=48.0):
    """Aperiodic / periodic split with specparam, 'knee' mode, peaks fitted explicitly (up to 8), 2-48 Hz.
    PRIMARY split since 2026-11-15: in the 88-subject synthetic control, IRASA attributed part of a
    gamma-to-beta power shift to the 'fractal' part at 32-41 Hz (fractal g = +1.48 vs periodic g = -4.69;
    wider or narrower resampling ranges were worse), because resampling drags neighbouring peaks into the
    estimate. specparam-knee leaked 0.03 of the effect. Falls back to 'fixed' mode if the knee fit fails.
    Returns log10 aperiodic fit on f (NaN outside fmin-fmax) and the parameters (offset, knee, exponent)."""
    import sys
    from common import CODE
    if str(CODE) not in sys.path:
        sys.path.insert(0, str(CODE))
    from nh.spectral import _spectral_model
    k = (f >= fmin) & (f <= fmax)
    out = np.full(len(f), np.nan); par = (np.nan, np.nan, np.nan)
    import warnings
    for mode in ("knee", "fixed"):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fm = _spectral_model(dict(peak_width_limits=[1.0, 8.0], max_n_peaks=8, min_peak_height=0.05,
                                          aperiodic_mode=mode))
                fm.fit(f[k], psd[k], [fmin, fmax])
                ap = np.atleast_1d(fm.get_params("aperiodic"))
            if mode == "knee":
                if not (np.all(np.isfinite(ap)) and ap[1] > 0):
                    continue
                out[k] = ap[0] - np.log10(ap[1] + f[k] ** ap[2]); par = (ap[0], ap[1], ap[2])
            else:
                out[k] = ap[0] - ap[1] * np.log10(f[k]); par = (ap[0], 0.0, ap[1])
            break
        except Exception:  # noqa: BLE001
            continue
    return out, par


# ------------------------------------------------------------------ bursts
def detect_bursts(xg_env, xg_phase, thr, sf, min_cycles=3.0, merge_s=0.025):
    """Runs where the 30-48 Hz envelope exceeds thr, gaps < merge_s merged, >= min_cycles long."""
    above = np.nan_to_num(xg_env, nan=0.0) > thr
    d = np.diff(np.r_[0, above.astype(int), 0])
    on, off = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    if len(on) == 0:
        return []
    keep_on, keep_off = [on[0]], [off[0]]
    for a, b in zip(on[1:], off[1:]):
        if a - keep_off[-1] < merge_s * sf:
            keep_off[-1] = b
        else:
            keep_on.append(a); keep_off.append(b)
    out = []
    for a, b in zip(keep_on, keep_off):
        ph = np.unwrap(xg_phase[a:b])
        if b - a < 4 or not np.all(np.isfinite(ph)):
            continue
        inst_f = np.diff(ph) * sf / (2 * np.pi)
        fm = float(np.median(inst_f))
        if fm <= 0 or (b - a) / sf * fm < min_cycles:
            continue
        out.append((a, b, inst_f))
    return out


def burst_table(xcsd, xbroad, segments, sf, ch_names, rng):
    edge = int(0.25 * sf)
    A = lambda lo, hi, tr=None: np.vstack([analytic(xcsd[i], segments, sf, lo, hi, tr, edge)  # noqa: E731
                                           for i in range(len(ch_names))])
    za = A(*GAMMA); env, ph = np.abs(za), np.angle(za)
    emg_env = np.abs(A(*EMG_BAND, 3.0))           # AUDIT: 3 Hz transition, so 44-48 Hz gamma cannot leak in
    alpha_ph = np.angle(A(8.0, 12.0, 2.0))
    theta_ph = np.angle(A(4.0, 8.0, 2.0))
    d2 = np.abs(np.diff(xbroad, 2, axis=-1))
    rows, thr_tab = [], {}
    for i, ch in enumerate(ch_names):
        # noise threshold from a phase-randomized copy of the same channel (same spectrum, no bursts beyond chance)
        s = phase_surrogate(np.nan_to_num(xcsd[i]), rng)
        zs = analytic(s, segments, sf, *GAMMA, None, edge)
        senv_all = np.abs(zs)
        senv = senv_all[np.isfinite(senv_all)]
        thr95, thr99 = np.percentile(senv, [95, 99])
        # the same detector on the surrogate: bursts expected from a Gaussian process with this exact spectrum
        n_null = len(detect_bursts(senv_all, np.angle(zs), thr95, sf))
        thr_tab[ch] = (thr95, thr99, n_null)
        med_emg = np.nanmedian(emg_env[i]); med_d2 = np.nanmedian(d2[i])
        if not np.isfinite(med_d2):
            continue
        for a, b, inst_f in detect_bursts(env[i], ph[i], thr95, sf):
            t = np.arange(len(inst_f)) / sf
            w0, w1 = max(0, a - int(0.05 * sf)), min(xbroad.shape[1], b + int(0.05 * sf))
            seg = np.nan_to_num(xbroad[i, w0:w1]) * np.hanning(w1 - w0)
            F = np.fft.rfftfreq(4096, 1 / sf); P = np.abs(np.fft.rfft(seg, 4096)) ** 2
            fm = float(np.median(inst_f))
            nb = (np.abs(F - fm) <= 3)
            bb = (F >= 20) & (F <= 68) & ~((F >= LINE_EXCL[0]) & (F <= LINE_EXCL[1]))
            pk = a + int(np.nanargmax(env[i, a:b]))
            rows.append(dict(
                ch=ch, region=REGION.get(ch, "other"), onset_s=a / sf, dur_s=(b - a) / sf,
                dur_cycles=(b - a) / sf * fm, f_mean=fm,
                f_sd=float(np.std(inst_f)), f_mad=float(np.median(np.abs(inst_f - fm)) * 1.4826),
                chirp_hz_s=float(np.polyfit(t, inst_f, 1)[0]) if len(t) > 3 else np.nan,
                amp_rel95=float(np.nanmax(env[i, a:b]) / thr95), above99=bool(np.nanmax(env[i, a:b]) > thr99),
                nb_index=float(np.log10(P[nb].sum() / max(P[bb].sum(), 1e-30))),
                emg_coact=float(np.log10(np.nanmean(emg_env[i, a:b]) / med_emg)) if med_emg > 0 else np.nan,
                sharp=float(np.log10(np.nanmax(d2[i, max(0, a - 1):b]) / med_d2)) if med_d2 > 0 else np.nan,
                alpha_phase=float(alpha_ph[i, a]), theta_phase_peak=float(theta_ph[i, pk]),
                _a=a, _b=b))
    df = pd.DataFrame(rows)
    if len(df):
        # spatial spread: fraction of OTHER channels with a burst overlapping this one in time
        spans = {ch: g[["_a", "_b"]].to_numpy() for ch, g in df.groupby("ch")}
        spread = np.zeros(len(df))
        for k, (ch, a, b) in enumerate(df[["ch", "_a", "_b"]].itertuples(index=False)):
            n = 0
            for c2, sp in spans.items():
                if c2 != ch and np.any((sp[:, 0] < b) & (sp[:, 1] > a)):
                    n += 1
            spread[k] = n / max(len(spans) - 1, 1)
        df["spread"] = spread
        df = df.drop(columns=["_a", "_b"])
    return df, thr_tab


# ------------------------------------------------------------------ sharp transients (avg ref)
def sharp_transients(xb, sf, ch_names, z_thr=5.0):
    """Candidate interictal-like transients: |x| > z_thr robust SD of the 1-70 Hz signal, peak half-width
    10-100 ms (spike 20-70 ms / sharp wave 70-200 ms span), sharper than the channel's typical peaks.
    Autoreject removed the most extreme epochs upstream, so counts are a LOWER bound."""
    ev = []
    for i, ch in enumerate(ch_names):
        fin = np.isfinite(xb[i])
        x = np.where(fin, xb[i], 0.0)
        if fin.sum() < sf * 10:
            continue
        sd = 1.4826 * np.median(np.abs(x[fin] - np.median(x[fin])))
        if sd <= 0:
            continue
        cand = []
        for sign in (1, -1):
            pk, pr = find_peaks(sign * x, height=z_thr * sd, width=(0.01 * sf, 0.1 * sf), rel_height=0.5)
            cand += [(p, sign, float(sign * x[p] / sd), float(w / sf)) for p, w in zip(pk, pr["widths"])]
        cand.sort()
        last = -10 ** 9
        for p, sign, zz, w in cand:            # a biphasic transient counts once (merge within 50 ms)
            if p - last > 0.05 * sf:
                ev.append((ch, p / sf, sign, zz, w)); last = p
    return pd.DataFrame(ev, columns=["ch", "t_s", "polarity", "z", "halfwidth_s"])


# ------------------------------------------------------------------ main per subject
def process(sub: str, cfile: Path, out: Path, n_surr: int):
    fo = out / "feat" / f"{sub}.npz"
    if fo.exists():
        try:
            if "sp_freqs" in np.load(fo).files:          # cache from before the specparam split -> recompute
                return {"subject": sub, "status": "cached"}
        except Exception:  # noqa: BLE001
            pass
    t0 = time.time()
    try:
        rng = np.random.default_rng([SEED, int("".join(c for c in sub if c.isdigit()) or 0)])
        c = load_clean(cfile)
        x_avg, sf, chs, segs = c["data"].astype(float), float(c["sfreq"]), c["ch_names"], c["segments"]
        # AUDIT: autoreject interpolation after re-referencing leaves a non-zero channel mean (up to 9 uV in the
        # pilot); re-impose the exact average reference so 'avg' means what it says
        x_avg = x_avg - x_avg.mean(0, keepdims=True)
        if x_avg.shape[1] % int(round(EPOCH_S * sf)):
            raise ValueError("clean data are not whole 2-s epochs; epoch-based measures would straddle edges")
        x_csd = csd_transform(x_avg, chs, sf) * 1e6              # arbitrary but fixed scale
        roi_idx = [chs.index(r) for r in ROI if r in chs]
        res = {"ch_names": np.asarray(chs), "sfreq": sf}

        for ref, x in (("csd", x_csd), ("avg", x_avg)):
            ep = epochs_of(x, sf)                                # ch, n_ep, n
            f, p = epoch_psd(ep, sf)
            keep_f = f <= 70
            f = f[keep_f]; p = p[..., keep_f]
            logp_ep = np.log10(p + 1e-30)
            res["freqs"] = f
            res[f"logpsd_{ref}"] = np.log10(p.mean(1) + 1e-30)
            # E1 muscle: per-epoch EMG score = median over channels of z(log 53-68 Hz power)
            em = (f >= EMG_BAND[0]) & (f <= EMG_BAND[1])
            emg_ep = logp_ep[..., em].mean(-1)                   # ch, n_ep
            z = (emg_ep - np.median(emg_ep, 1, keepdims=True)) / (1.4826 * np.median(
                np.abs(emg_ep - np.median(emg_ep, 1, keepdims=True)), 1, keepdims=True) + 1e-12)
            score = np.median(z, 0)
            order = np.argsort(score)
            for frac in (50, 25):
                sel = order[: max(10, int(len(order) * frac / 100))]
                res[f"logpsd_{ref}_lowemg{frac}"] = np.log10(p[:, sel].mean(1) + 1e-30)
            res[f"emg_epoch_{ref}"] = emg_ep.mean(0)
            # E3 aperiodic/periodic split. PRIMARY: specparam-knee (see sp_split); SECONDARY: IRASA
            mp = p.mean(1)
            spl = [sp_split(f, mp[c_]) for c_ in range(mp.shape[0])]
            ap_log = np.vstack([a_[0] for a_ in spl])
            ks = (f >= 2) & (f <= 47.5)
            res["sp_freqs"] = f[ks]
            res[f"sp_aperiodic_{ref}"] = ap_log[:, ks]
            res[f"sp_periodic_{ref}"] = np.log10(mp[:, ks] + 1e-30) - ap_log[:, ks]
            res[f"sp_params_{ref}"] = np.array([a_[1] for a_ in spl])      # offset, knee, exponent per channel
            fi, mixed, fract = irasa(ep, sf)
            mk = (fi >= 2) & (fi <= 47.5)
            res["irasa_freqs"] = fi[mk]
            res[f"irasa_fractal_{ref}"] = np.log10(fract[:, mk] + 1e-30)
            res[f"irasa_periodic_{ref}"] = np.log10(mixed[:, mk] + 1e-30) - np.log10(fract[:, mk] + 1e-30)
            # E4 vigilance per epoch (ROI alpha/theta), gamma power by stratum
            a_ = (f >= 8) & (f <= 12); t_ = (f >= 4) & (f < 8); g_ = (f >= GAMMA[0]) & (f <= 45)
            vig = np.log10(p[roi_idx][..., a_].mean((0, 2)) / p[roi_idx][..., t_].mean((0, 2)))
            res[f"vigilance_epoch_{ref}"] = vig
            res[f"gamma_epoch_{ref}"] = np.log10(p[..., g_].mean(-1) + 1e-30)     # ch, n_ep

        # IAF and coupling on the CSD ROI
        res["iaf"] = iaf_from_psd(res["freqs"], res["logpsd_csd"][roi_idx].mean(0))
        edge = int(0.5 * sf)
        iaf = res["iaf"]
        lo4, hi4 = 4 * iaf - 3, min(4 * iaf + 3, 47.0)    # AUDIT: IAF > 12.5 Hz made lo4 >= hi4 and crashed the subject
        harmonic_ok = hi4 - lo4 >= 3.0
        coup = []
        for i in roi_idx:
            xi = x_csd[i]
            ph_t = np.angle(analytic(xi, segs, sf, 4.0, 8.0, 2.0, edge))
            ph_a = np.angle(analytic(xi, segs, sf, iaf - 2, iaf + 2, 2.0, edge))
            za = analytic(xi, segs, sf, *GAMMA, None, edge)
            zh = analytic(xi, segs, sf, lo4, hi4, None, edge) if harmonic_ok else np.full(len(xi), np.nan + 0j)
            ok = np.isfinite(ph_t) & np.isfinite(za) & np.isfinite(ph_a)
            amp = np.abs(za[ok])
            mi_t, z_t = shift_z(tort_mi, ph_t[ok], amp, sf, rng, n_surr)
            mi_a, z_a = shift_z(tort_mi, ph_a[ok], amp, sf, rng, n_surr)
            plv = lambda pa, ph: float(np.abs(np.mean(np.exp(1j * (4 * pa - ph)))))  # noqa: E731
            okh = ok & np.isfinite(zh)
            pl, z_pl = (shift_z(plv, ph_a[okh], np.angle(zh[okh]), sf, rng, n_surr) if okh.sum() > 10 * sf
                        else (np.nan, np.nan))
            coup.append([mi_t, z_t, mi_a, z_a, pl, z_pl])
        res["coupling_roi"] = np.asarray(coup)            # rows = ROI channels; cols as below
        res["coupling_cols"] = np.asarray(["pac_theta_mi", "pac_theta_z", "pac_alpha_mi", "pac_alpha_z",
                                           "alpha_1to4_plv", "alpha_1to4_z"])

        # E6 sharp transients on avg ref, 1-70 Hz; gamma power with transient windows removed
        xb_avg = lowpass_segments(x_avg, segs, sf, 70.0, edge=int(0.1 * sf))
        tr = sharp_transients(xb_avg, sf, chs)
        dur_min = x_avg.shape[1] / sf / 60
        res["transient_rate_per_min"] = np.array([np.sum(tr.ch == ch) / dur_min for ch in chs])
        mask = np.ones(x_avg.shape[1], bool)
        for t in tr.t_s.to_numpy():
            k = int(t * sf); mask[max(0, k - int(0.25 * sf)): k + int(0.25 * sf)] = False
        n = int(EPOCH_S * sf); ep_ok = mask[: (len(mask) // n) * n].reshape(-1, n).all(1)
        gam = res["gamma_epoch_csd"]
        res["gamma_roi_all"] = float(np.log10(np.mean(10 ** gam[roi_idx], 0)).mean())
        res["gamma_roi_no_transients"] = float(np.log10(np.mean(10 ** gam[roi_idx][:, ep_ok], 0)).mean()) if ep_ok.sum() >= 10 else np.nan
        res["frac_epochs_with_transient"] = float(1 - ep_ok.mean())

        # bursts (CSD, broadband 1-70 for shape measures)
        xb_csd = lowpass_segments(x_csd, segs, sf, 70.0, edge=int(0.1 * sf))
        bt, thr = burst_table(x_csd, xb_csd, segs, sf, chs, rng)
        bt.insert(0, "subject", sub)
        bt["clean_min"] = dur_min
        (out / "bursts").mkdir(parents=True, exist_ok=True)
        bt.to_csv(out / "bursts" / f"{sub}.csv.gz", index=False)
        tr.insert(0, "subject", sub)
        tr.to_csv(out / "bursts" / f"{sub}.transients.csv.gz", index=False)
        res["burst_thr95"] = np.array([thr[c][0] for c in chs]); res["burst_thr99"] = np.array([thr[c][1] for c in chs])
        # burst excess: log ratio of detected bursts to bursts in the matched Gaussian surrogate (0 = no more
        # burst-like 30-48 Hz events than the spectrum alone predicts; > 0 = genuine transient events)
        n_real = bt.groupby("ch").size().reindex(chs).fillna(0).to_numpy() if len(bt) else np.zeros(len(chs))
        res["burst_excess"] = np.log((n_real + 1) / (np.array([thr[c][2] for c in chs]) + 1))
        res["qc"] = np.asarray(json.dumps({**c["qc"], "n_bursts": int(len(bt)), "n_transients": int(len(tr)),
                                           "seconds": round(time.time() - t0, 1)}, default=jsonable))
        save_npz(fo, **res)
        return {"subject": sub, "status": "ok", "seconds": round(time.time() - t0, 1), "n_bursts": int(len(bt))}
    except Exception as e:  # noqa: BLE001
        return {"subject": sub, "status": "error", "reason": f"{type(e).__name__}: {e}",
                "trace": traceback.format_exc()[-1500:]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="main")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--n-surr", type=int, default=100)
    ap.add_argument("--subjects", nargs="*", default=None)
    a = ap.parse_args()
    out = variant_dir(a.dataset, a.variant)
    files = sorted((out / "clean").glob("sub-*.npz"))
    files = [f for f in files if not f.name.endswith(".tmp.npz")]
    if a.subjects:
        files = [f for f in files if f.stem in set(a.subjects)]
    print(f"[10] {a.dataset}/{a.variant}: {len(files)} clean subjects", flush=True)
    res = Parallel(n_jobs=a.jobs, verbose=5)(delayed(process)(f.stem, f, out, a.n_surr) for f in files)
    errs = [r for r in res if r["status"] == "error"]
    for r in errs:
        print("ERROR", r["subject"], r["reason"], "\n", r.get("trace", ""))
    (out / "feat_meta.json").write_text(json.dumps(res, indent=1, default=jsonable))
    print("[10] done:", {s: sum(r["status"] == s for r in res) for s in {r["status"] for r in res}})
