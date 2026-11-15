"""Label-blind preprocessing of ONE recording.

Every rule here uses only that recording's own data (robust per-subject thresholds) or fixed
constants from config/pipeline.yaml. No information crosses subjects; no labels are read.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import mne
import numpy as np

mne.set_log_level("ERROR")


@dataclass
class CleanRecording:
    data: np.ndarray                 # (n_channels, n_samples) concatenated clean segments, Volts
    segments: list[tuple[int, int]]  # [start, stop) sample indices of contiguous clean runs in `data`
    sfreq: float
    ch_names: list[str]
    qc: dict = field(default_factory=dict)


class ExcludedRecording(Exception):
    """Raised when a pre-specified exclusion rule applies (reason is logged in QC)."""


def _robust_z(x: np.ndarray) -> np.ndarray:
    med = np.median(x)
    mad = np.median(np.abs(x - med)) * 1.4826
    return (x - med) / (mad if mad > 0 else np.finfo(float).eps)


def _band_logpower(data: np.ndarray, sfreq: float, band, line_freq) -> np.ndarray:
    psd, fr = mne.time_frequency.psd_array_welch(data, sfreq, fmin=band[0], fmax=band[1],
                                                 n_fft=int(sfreq), verbose=False)
    keep = np.ones_like(fr, dtype=bool)
    if line_freq:
        for h in np.arange(line_freq, band[1] + line_freq, line_freq):
            keep &= np.abs(fr - h) > 2.0
    return np.log10(psd[..., keep].mean(-1) + 1e-30)


def _bad_by_correlation(x: np.ndarray, sf: float, thr: float, frac_bad: float, win_s: float = 1.0) -> np.ndarray:
    """PREP correlation criterion (Bigdely-Shamlo et al. 2015): a channel is bad if, in more than
    frac_bad of 1-s windows, its largest |correlation| with any other channel is below thr."""
    n = int(win_s * sf); nw = x.shape[1] // n
    bad_count = np.zeros(x.shape[0])
    for w in range(nw):
        seg = x[:, w * n:(w + 1) * n]
        sd = seg.std(1)
        if (sd == 0).any():
            continue
        c = np.abs(np.corrcoef(seg)); np.fill_diagonal(c, 0)
        bad_count += c.max(1) < thr
    return bad_count / max(nw, 1) > frac_bad


def bss_cca_muscle(raw: mne.io.BaseRaw, slope_thr: float, band=(15.0, 90.0)) -> dict:
    """BSS-CCA (De Clercq et al. 2006) + spectral-slope rejection (Janani et al. 2018).
    Sources are ordered by lag-1 autocorrelation (muscle ~ white noise -> low autocorrelation);
    sources whose log-log spectral slope over `band` is flatter than slope_thr are removed."""
    X = raw.get_data()
    Xf = raw.get_data(reject_by_annotation="omit")                 # unmixing learned on usable time only
    mu = Xf.mean(1, keepdims=True); Xc = X - mu; Xfc = Xf - mu     # (identical to X when no BAD_ spans)
    C = Xfc @ Xfc.T / Xfc.shape[1]
    ev, U = np.linalg.eigh(C)
    keep = ev > ev.max() * 1e-10                                   # average reference -> rank deficit
    W = (U[:, keep] / np.sqrt(ev[keep])).T                         # whitening (r x ch)
    Zf = W @ Xfc
    C1 = (Zf[:, 1:] @ Zf[:, :-1].T + Zf[:, :-1] @ Zf[:, 1:].T) / (2 * (Zf.shape[1] - 1))
    rho, V = np.linalg.eigh(C1)                                    # autocorrelation of each source
    S = V.T @ (W @ Xc)                                             # sources, whole recording
    Sf = V.T @ Zf
    psd, fr = mne.time_frequency.psd_array_welch(Sf, raw.info["sfreq"], fmin=band[0],
                                                 fmax=min(band[1], raw.info["sfreq"] / 2 - 1),
                                                 n_fft=int(raw.info["sfreq"] * 2), verbose=False)
    slopes = np.array([np.polyfit(np.log10(fr), np.log10(p + 1e-30), 1)[0] for p in psd])
    drop = slopes > slope_thr
    S[drop] = 0
    A = np.linalg.pinv(V.T @ W)                                    # mixing back to channels
    raw._data[:] = A @ S + mu
    return {"n_sources": int(len(slopes)), "n_removed": int(drop.sum()),
            "removed_slopes": slopes[drop].round(2).tolist()}


def standardize_channels(raw: mne.io.BaseRaw, cfg: dict) -> tuple[mne.io.BaseRaw, list[str]]:
    com = cfg["common"]
    raw.pick("eeg")
    ren = {c: com["rename"][c] for c in raw.ch_names if c in com["rename"]}
    if ren:
        raw.rename_channels(ren)
    wanted = com["channels"]
    present = [c for c in wanted if c in raw.ch_names]
    missing = [c for c in wanted if c not in raw.ch_names]
    raw.pick(present)
    raw.reorder_channels(present)
    raw.set_montage(mne.channels.make_standard_montage("standard_1020"), on_missing="ignore")
    return raw, missing


def preprocess(raw: mne.io.BaseRaw, cfg: dict, line_freq: float | None, skip_ica: bool = False,
               reference: str | None = None) -> CleanRecording:
    pp, com = cfg["preprocessing"], cfg["common"]
    reference = reference or pp["reference"]
    qc: dict = {"orig_sfreq": float(raw.info["sfreq"]), "orig_duration_s": float(raw.times[-1])}

    raw, missing = standardize_channels(raw, cfg)
    qc["missing_channels"] = missing
    if len(missing) > pp["bad_channels"]["max_bad_fraction"] * len(com["channels"]):
        raise ExcludedRecording(f"too many missing channels: {missing}")

    # ---- filtering at the native rate, then resample to the common rate
    sf0 = raw.info["sfreq"]
    lp = min(pp["lowpass_hz"], 0.45 * sf0, 0.45 * com["sfreq"])
    raw.filter(pp["highpass_hz"], lp, method="fir", fir_design="firwin", phase="zero")
    if pp["notch_harmonics"] and line_freq:
        harms = np.arange(line_freq, lp, line_freq)
        if len(harms):
            raw.notch_filter(harms, method="fir", phase="zero")
    if abs(sf0 - com["sfreq"]) > 1e-6:
        raw.resample(com["sfreq"])
    sf = raw.info["sfreq"]
    qc["filter"] = {"highpass": pp["highpass_hz"], "lowpass": lp, "notch": bool(line_freq),
                    "design": "FIR firwin zero-phase (MNE)"}

    # ---- bad channels, two passes (per-subject robust rules)
    # Pass 1, BEFORE ICA: only electrode faults (flat; uncorrelated with every other channel; extreme
    # variance). Blinks and muscle inflate variance / high-frequency power on healthy frontal and temporal
    # electrodes; with 19 channels that alone used to push recordings past the exclusion threshold.
    # Pass 2, AFTER ICA (+ optional BSS-CCA): the usual variance and high-frequency robust-z rules on the
    # cleaned data. The exclusion threshold applies to the total.
    bc = pp["bad_channels"]
    two_pass = bc.get("two_pass", False)
    x = raw.get_data(reject_by_annotation="omit")     # statistics on usable time only (identical when no BAD_ spans)
    ch = np.array(raw.ch_names)
    std_uv = x.std(1) * 1e6
    bads = set(ch[std_uv < bc["flat_uv"]])
    logvar_z = _robust_z(np.log10(x.var(1) + 1e-30))
    if two_pass:
        bads |= set(ch[np.abs(logvar_z) > bc.get("pre_ica_robust_z", 10.0)])
    else:
        hf_z = _robust_z(_band_logpower(x, sf, cfg["features"]["spectral"]["emg_band"], line_freq))
        bads |= set(ch[(np.abs(logvar_z) > bc["robust_z"]) | (hf_z > bc["robust_z"])])
    corr_cfg = bc.get("correlation")
    if corr_cfg:
        bads |= set(ch[_bad_by_correlation(x, sf, corr_cfg["threshold"], corr_cfg["frac_bad"])])
    qc["bad_channels_pre_ica"] = sorted(bads)
    if len(bads) > bc["max_bad_fraction"] * len(raw.ch_names):
        raise ExcludedRecording(f"too many bad channels (electrode faults): {sorted(bads)}")
    if bads:
        raw.info["bads"] = sorted(bads)
        raw.interpolate_bads(reset_bads=True)

    raw.set_eeg_reference("average", projection=False)

    # ---- ICA + ICLabel
    qc["ica"] = {"enabled": bool(pp["ica"]["enabled"] and not skip_ica)}
    if qc["ica"]["enabled"]:
        from mne_icalabel import label_components
        ica = mne.preprocessing.ICA(n_components=pp["ica"]["n_components"], method="infomax",
                                    fit_params={"extended": True},
                                    random_state=pp["ica"]["random_state"], max_iter="auto")
        ica.fit(raw, reject_by_annotation=True)
        lab = label_components(raw, ica, method="iclabel")
        drop = [i for i, (l, p) in enumerate(zip(lab["labels"], lab["y_pred_proba"]))
                if l in pp["ica"]["reject_labels"] and p >= pp["ica"]["reject_prob"]]
        ica.exclude = drop
        ica.apply(raw)
        qc["ica"].update({"n_components": int(ica.n_components_), "n_removed": len(drop),
                          "removed_labels": [lab["labels"][i] for i in drop],
                          "n_muscle_removed": sum(lab["labels"][i] == "muscle artifact" for i in drop)})

    mus = pp.get("muscle", {"method": "none"})
    if mus.get("method") == "bss_cca":
        qc["muscle_bss_cca"] = bss_cca_muscle(raw, mus.get("slope_threshold", -0.5), tuple(mus.get("band", [15.0, 90.0])))
    qc["muscle_method"] = mus.get("method", "none")

    if two_pass:                                   # pass 2: robust rules on the cleaned data
        x = raw.get_data(reject_by_annotation="omit")
        lz = _robust_z(np.log10(x.var(1) + 1e-30))
        hz = _robust_z(_band_logpower(x, sf, cfg["features"]["spectral"]["emg_band"], line_freq))
        late = set(ch[(np.abs(lz) > bc["robust_z"]) | (hz > bc["robust_z"])]) - bads
        qc["bad_channels_post_ica"] = sorted(late)
        bads |= late
        if len(bads) > bc["max_bad_fraction"] * len(raw.ch_names):
            raise ExcludedRecording(f"too many bad channels after ICA: {sorted(bads)}")
        if late:
            raw.info["bads"] = sorted(late)
            raw.interpolate_bads(reset_bads=True)
            raw.set_eeg_reference("average", projection=False)
    qc["bad_channels"] = sorted(bads)

    qc["reference"] = reference   # applied AFTER epoch rejection, so uV thresholds stay valid

    # ---- fixed-length epochs + per-subject robust rejection
    ep_cfg, dur_cfg = pp["epochs"], pp["duration"]
    ev = mne.make_fixed_length_events(raw, duration=ep_cfg["length_s"])
    epochs = mne.Epochs(raw, ev, tmin=0, tmax=ep_cfg["length_s"] - 1 / sf, baseline=None,
                        reject_by_annotation=True, preload=True, verbose="ERROR")
    E = epochs.get_data(picks="all")                         # (n_ep, n_ch, n_t)
    onsets = epochs.events[:, 0] - raw.first_samp
    ptp = np.ptp(E, axis=-1).max(1) * 1e6                    # worst channel per epoch, µV
    hf = _band_logpower(E, sf, cfg["features"]["spectral"]["emg_band"], line_freq).mean(1)

    def _mad_rule(v, k):
        med = np.median(v); mad = np.median(np.abs(v - med)) * 1.4826
        return v > med + k * mad

    bad_ep = _mad_rule(hf, ep_cfg["hf_mad_k"])                    # EMG-burst rule always applies
    # flat epochs (any channel peak-to-peak < flat_uv: amplifier calibration/reset, disconnection). They
    # are not EEG, and a flat epoch drives autoreject's learned thresholds to 0 (found on ds006036).
    flat = (np.ptp(E, axis=-1).min(1) * 1e6) < pp["bad_channels"]["flat_uv"]
    bad_ep |= flat
    qc["epochs_flat"] = int(flat.sum())
    if ep_cfg.get("method", "mad") == "autoreject":
        # Jas et al. 2017: per-channel thresholds learned by CV within THIS subject; bad channels in an
        # epoch are interpolated, epochs with too many bad channels are dropped (label-free)
        from autoreject import AutoReject
        ar = AutoReject(n_interpolate=[1, 2, 4], random_state=pp["ica"]["random_state"], n_jobs=1, verbose=False)
        use = np.flatnonzero(~flat)
        epochs_clean, log = ar.fit_transform(epochs[use], return_log=True)
        E = epochs.get_data(picks="all")
        ok = use[~log.bad_epochs]
        E[ok] = epochs_clean.get_data(picks="all")
        bad_ep[use[log.bad_epochs]] = True
        qc["autoreject_interpolated_fraction"] = float((log.labels == 2).mean())
    else:
        bad_ep |= (ptp > ep_cfg["abs_ptp_uv"]) | _mad_rule(ptp, ep_cfg["ptp_mad_k"])
    qc["epoch_rejection"] = ep_cfg.get("method", "mad")
    good_idx = np.where(~bad_ep)[0]
    qc["epochs_total"] = int(len(E))
    qc["epochs_rejected"] = int(bad_ep.sum())

    # ---- re-reference the kept data (CSD / REST change units and scale, so thresholds ran on average ref)
    if reference in ("csd", "rest"):
        ep_keep = mne.EpochsArray(E, epochs.info, verbose="ERROR")
        if reference == "csd":
            ep_keep = mne.preprocessing.compute_current_source_density(ep_keep)
        else:
            sphere = mne.make_sphere_model("auto", "auto", ep_keep.info, verbose="ERROR")
            src = mne.setup_volume_source_space(sphere=sphere, exclude=30.0, pos=15.0, verbose="ERROR")
            fwd = mne.make_forward_solution(ep_keep.info, trans=None, src=src, bem=sphere, verbose="ERROR")
            ep_keep.set_eeg_reference("REST", forward=fwd, verbose="ERROR")
        E = ep_keep.get_data(picks="all")

    n_keep = int(round(dur_cfg["max_clean_s"] / ep_cfg["length_s"]))
    if dur_cfg["selection"] != "first":
        raise ValueError("only deterministic 'first' selection is implemented")
    good_idx = good_idx[:n_keep]
    clean_s = len(good_idx) * ep_cfg["length_s"]
    qc["clean_seconds"] = float(clean_s)
    if clean_s < dur_cfg["min_clean_s"]:
        raise ExcludedRecording(f"only {clean_s:.0f}s clean data (< {dur_cfg['min_clean_s']}s)")

    # ---- concatenate into contiguous segments (contiguous epochs stay joined -> fewer edges)
    n_t = E.shape[-1]
    pieces, segments, cur, start = [], [], 0, 0
    for j, i in enumerate(good_idx):
        pieces.append(E[i])
        is_break = j + 1 == len(good_idx) or onsets[good_idx[j + 1]] != onsets[i] + n_t
        cur += n_t
        if is_break:
            segments.append((start, cur)); start = cur
    data = np.concatenate(pieces, axis=-1)
    qc["n_segments"] = len(segments)
    qc["emg_hf_logpower_mean"] = float(hf[good_idx].mean())
    return CleanRecording(data=data, segments=segments, sfreq=sf, ch_names=list(raw.ch_names), qc=qc)
