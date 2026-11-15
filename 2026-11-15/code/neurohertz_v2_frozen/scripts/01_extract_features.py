"""Stage A: LABEL-BLIND feature extraction, one recording at a time.

This script never imports nh.labels and never reads a participants file (tests/test_leakage.py
checks this). Each subject's features depend only on (that subject's recording, frozen config),
so features can be computed once for everyone without leaking information across CV folds.

Outputs (results/features/<dataset>/<variant>/):
  per_subject/<sub>.json      QC + all channel-level features (resume-safe)
  features_long.csv           subject, channel, feature, value
  features_subject.csv        one row per subject: ROI means (primary ROI + each region)
  qc.csv                      preprocessing QC per subject (incl. exclusions and reasons)
  inventory.csv               every candidate file found (duplicates/truncated copies visible)

Usage
  python scripts/01_extract_features.py --dataset ds004504 --jobs 2
  python scripts/01_extract_features.py --dataset ds004504 --variant csd --reference csd
  python scripts/01_extract_features.py --dataset caueeg --register     # lockbox: hash before labels
"""
from __future__ import annotations

import argparse
import json
import warnings
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# expected, harmless numerical warnings (unfittable floor on flat spectra, empty ROI means); keeps logs readable
warnings.filterwarnings("ignore", message="Covariance of the parameters could not be estimated")
warnings.filterwarnings("ignore", message="Mean of empty slice")
warnings.filterwarnings("ignore", message="Pandas requires version")
from nh.config import ROOT, analysis_hash, apply_overrides, extraction_hash, load_config  # noqa: E402
from nh.datasets import get_adapter  # noqa: E402
from nh.gamma import gii_subject, subject_rng  # noqa: E402
from nh.oscfit import oscillation_subject  # noqa: E402
from nh.preprocess import ExcludedRecording, preprocess  # noqa: E402
from nh.spectral import channel_spectral_features, irasa_exponent, roi_gamma_peak, welch_psd  # noqa: E402


def _jsonable(o):
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, np.ndarray): return o.tolist()
    return str(o)


def process_subject(dataset: str, sub: str, path: str, out_dir: Path, cfg: dict, reference: str | None,
                    skip_ica: bool | None, n_surr: int | None, roots: list[str] | None = None,
                    split_half: bool = False) -> dict:
    fn = out_dir / "per_subject" / f"{sub}.json"
    xh = extraction_hash(cfg=cfg)
    # command-line settings that change the features are part of the cache key too
    run_settings = {"n_surr": int(cfg["features"]["surrogates"]["n"] if n_surr is None else n_surr),
                    "skip_ica": skip_ica, "reference": reference, "split_half": bool(split_half)}
    if fn.exists():
        old = json.loads(fn.read_text())
        if (old.get("extraction_sha256") == xh and old.get("run_settings") == run_settings
                and old.get("status") != "error"):
            return old                                   # resume only if produced by an identical run; errors retry
    ad = get_adapter(dataset, **({"roots": roots} if roots else {}))
    rec = {"subject": sub, "path": path, "status": "ok", "extraction_sha256": xh, "run_settings": run_settings}
    t0 = time.time()
    try:
        raw = ad.load_raw(path)
        lf = ad.line_freq if isinstance(ad.line_freq, (int, float)) else cfg["common"]["line_freq"]
        clean = preprocess(raw, cfg, lf, skip_ica=ad.skip_ica if skip_ica is None else skip_ica,
                           reference=reference)
        rec["qc"] = {**clean.qc, "raw_seconds": float(raw.times[-1]) if len(raw.times) else np.nan}
        feats: dict[str, dict] = {ch: {} for ch in clean.ch_names}

        # conventional spectra
        psd, fr = welch_psd(clean.data, clean.sfreq, cfg["features"]["spectral"]["welch_s"],
                            fmax=min(100.0, clean.sfreq / 2 - 1))
        for i, ch in enumerate(clean.ch_names):
            feats[ch].update(channel_spectral_features(psd[i], fr, cfg, lf))
        if cfg["features"]["spectral"].get("aperiodic_method") == "irasa":
            # IRASA becomes THE aperiodic exponent downstream; the specparam value is kept for comparison
            for ch, d in irasa_exponent(clean.data, clean.sfreq, clean.ch_names, cfg).items():
                feats[ch]["specparam_exponent"] = feats[ch].get("aperiodic_exponent")
                feats[ch].update(d, aperiodic_exponent=d["irasa_exponent"])
        # oscillation presence gate, damped-oscillator fit, vigilance series (nh/oscfit.py)
        for ch, d in oscillation_subject(clean.data, clean.segments, clean.sfreq, clean.ch_names,
                                         cfg["features"], lf).items():
            feats[ch].update(d)
        # band-limited covariance (for the Riemannian ceiling check only; not a model input)
        from nh.gamma import _bandpass
        xg = np.vstack([_bandpass(clean.data[i], clean.sfreq, cfg["features"]["gamma_band"],
                                  cfg["features"]["filter_transition_hz"]) for i in range(len(clean.ch_names))])
        rec["cov_gamma"] = (np.cov(xg) * 1e12).round(6).tolist()           # uV^2
        rec["ch_order"] = clean.ch_names

        # gamma IF metrics, fixed primary band, all channels, with surrogates
        rng = subject_rng(cfg["features"]["surrogates"]["seed"], sub)
        band = cfg["features"]["gamma_band"]
        g = gii_subject(clean.data, clean.segments, clean.sfreq, clean.ch_names, band,
                        cfg["features"], rng, n_surr=n_surr)
        for ch, d in g.items():
            feats[ch].update(d)

        # sensitivity: individual gamma band (ROI only)
        ib = cfg["features"]["individual_band"]
        if ib["enabled"]:
            roi = [c for c in cfg["common"]["primary_roi"] if c in clean.ch_names]
            idx = [clean.ch_names.index(c) for c in roi]
            pk = roi_gamma_peak(psd, fr, idx, cfg)
            rec["roi_gamma_peak_hz"] = pk
            if np.isfinite(pk):
                iband = [max(25.0, pk - ib["half_width_hz"]), min(48.0, pk + ib["half_width_hz"])]
                rec["individual_band"] = iband
                gi = gii_subject(clean.data[idx], clean.segments, clean.sfreq, roi, iband,
                                 cfg["features"], rng, n_surr=n_surr)
                for ch, d in gi.items():
                    feats[ch].update({f"ib_{k}": v for k, v in d.items()})
        # reliability: same metrics on the first vs second half of the clean data (ROI only)
        if split_half:
            roi = [c for c in cfg["common"]["primary_roi"] if c in clean.ch_names]
            idx = [clean.ch_names.index(c) for c in roi]
            half = clean.data.shape[1] // 2
            for tag, (lo, hi) in {"sh1": (0, half), "sh2": (half, clean.data.shape[1])}.items():
                segs = [(max(a, lo) - lo, min(b, hi) - lo) for a, b in clean.segments if min(b, hi) > max(a, lo)]
                gh = gii_subject(clean.data[idx, lo:hi], segs, clean.sfreq, roi, band, cfg["features"], rng,
                                 n_surr=n_surr)
                for ch, d in gh.items():
                    feats[ch].update({f"{tag}_{k}": v for k, v in d.items()})
                for ch, e in _half_exponents(clean.data[idx, lo:hi], clean.sfreq, roi, cfg, lf).items():
                    feats[ch][f"{tag}_aperiodic_exponent"] = e
        rec["features"] = feats
    except ExcludedRecording as e:
        rec.update(status="excluded", reason=str(e))
    except Exception as e:  # recorded, never silently dropped
        rec.update(status="error", reason=f"{type(e).__name__}: {e}", trace=traceback.format_exc()[-2000:])
    rec["seconds"] = round(time.time() - t0, 1)
    fn.parent.mkdir(parents=True, exist_ok=True)
    fn.write_text(json.dumps(rec, default=_jsonable))
    return rec


def _half_exponents(data, sf, chs, cfg, lf) -> dict:
    """Aperiodic exponent on one half of the data, with the configured method (split-half ICC)."""
    if cfg["features"]["spectral"].get("aperiodic_method") == "irasa":
        return {ch: d["irasa_exponent"] for ch, d in irasa_exponent(data, sf, chs, cfg).items()}
    psd, fr = welch_psd(data, sf, cfg["features"]["spectral"]["welch_s"], fmax=min(100.0, sf / 2 - 1))
    return {ch: channel_spectral_features(psd[i], fr, cfg, lf).get("aperiodic_exponent") for i, ch in enumerate(chs)}


def assemble(recs: list[dict], cfg: dict, out_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    long_rows, qc_rows = [], []
    for r in recs:
        q = {"subject": r["subject"], "status": r["status"], "reason": r.get("reason", ""),
             "seconds": r.get("seconds")}
        for k, v in (r.get("qc") or {}).items():
            q[k] = json.dumps(v) if isinstance(v, (list, dict)) else v
        q["roi_gamma_peak_hz"] = r.get("roi_gamma_peak_hz")
        qc_rows.append(q)
        for ch, d in (r.get("features") or {}).items():
            for k, v in d.items():
                long_rows.append((r["subject"], ch, k, v))
    long = pd.DataFrame(long_rows, columns=["subject", "channel", "feature", "value"])
    qc = pd.DataFrame(qc_rows).sort_values("subject")
    regions = {"roi": cfg["common"]["primary_roi"], **cfg["common"]["regions"]}
    rows = []
    import warnings
    warnings.filterwarnings("ignore", message="Mean of empty slice")   # ROI-only features in other regions -> NaN
    for sub, d in long.groupby("subject"):
        row = {"subject": sub}
        piv = d.pivot_table(index="channel", columns="feature", values="value", aggfunc="first")
        for rname, chans in regions.items():
            p = piv.loc[[c for c in chans if c in piv.index]]
            for f in p.columns:
                row[f"{rname}__{f}"] = float(np.nanmean(p[f].astype(float))) if len(p) else np.nan
        em = piv.loc[[c for c in cfg["common"]["emg_sentinel_channels"] if c in piv.index]]
        for f in ("emg_logpow", "hf_slope_30_90"):
            if f in em:
                row[f"emg_sentinel__{f}"] = float(np.nanmean(em[f].astype(float)))
        rows.append(row)
    subj = pd.DataFrame(rows, columns=["subject"] if not rows else None)
    if subj.empty:
        qc.to_csv(out_dir / "qc.csv", index=False)
        raise SystemExit(f"No subject passed preprocessing; see {out_dir / 'qc.csv'} (column 'reason').")
    if not qc.empty:
        subj = subj.merge(qc[["subject", "clean_seconds"]] if "clean_seconds" in qc else qc[["subject"]],
                          on="subject", how="left")
    long.to_csv(out_dir / "features_long.csv", index=False)
    subj.to_csv(out_dir / "features_subject.csv", index=False)
    qc.to_csv(out_dir / "qc.csv", index=False)
    return subj, qc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--variant", default="primary")
    ap.add_argument("--reference", default=None, choices=[None, "average", "csd"])
    ap.add_argument("--no-ica", action="store_true")
    ap.add_argument("--n-surr", type=int, default=None)
    ap.add_argument("--subjects", nargs="*", default=None, help="restrict to these subject IDs")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--roots", nargs="*", default=None, help="override dataset roots from config/datasets.yaml")
    ap.add_argument("--split-half", action="store_true", help="also compute ROI metrics on each half (reliability)")
    ap.add_argument("--set", nargs="*", default=None, metavar="KEY=VALUE",
                    help="config overrides for an ablation variant, e.g. preprocessing.reference=csd")
    ap.add_argument("--register", action="store_true",
                    help="hash features_subject.csv into the access ledger (required before lockbox labels)")
    a = ap.parse_args()

    cfg = apply_overrides(load_config(), a.set)
    ad = get_adapter(a.dataset, **({"roots": a.roots} if a.roots else {}))
    out_dir = ROOT / "results" / "features" / a.dataset / a.variant
    (out_dir / "per_subject").mkdir(parents=True, exist_ok=True)
    ad.find_recordings().to_csv(out_dir / "inventory.csv", index=False)
    recs_map = ad.recordings()
    if a.subjects:
        recs_map = {s: p for s, p in recs_map.items() if s in set(a.subjects)}
    print(f"{a.dataset}: {len(recs_map)} loadable recordings -> {out_dir}")
    recs = Parallel(n_jobs=a.jobs, verbose=5)(
        delayed(process_subject)(a.dataset, s, p, out_dir, cfg, a.reference,
                                 True if a.no_ica else None, a.n_surr, a.roots, a.split_half)
        for s, p in sorted(recs_map.items()))
    subj, qc = assemble(recs, cfg, out_dir)
    meta = {"dataset": a.dataset, "variant": a.variant, "reference": a.reference, "no_ica": a.no_ica,
            "n_found": len(recs_map), "status_counts": qc["status"].value_counts().to_dict(),
            "overrides": a.set or [], "extraction_sha256": extraction_hash(cfg=cfg), **analysis_hash()}
    (out_dir / "run_meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))
    if a.register:
        from nh.ledger import log_event
        from nh.config import sha256_file
        sha = sha256_file(out_dir / "features_subject.csv")
        log_event("FEATURES_REGISTERED", dataset=a.dataset, features_sha256=sha,
                  features_path=str(out_dir / "features_subject.csv"))
        print("registered", sha)


if __name__ == "__main__":
    main()
