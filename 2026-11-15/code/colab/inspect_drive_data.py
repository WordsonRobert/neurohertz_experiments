# NeuroHertz: LABEL-BLIND inspection of everything in Google Drive.
# Run in Colab (CPU is enough). It prints a report and saves it to
#   MyDrive/neurohertz_inspection/report.txt  (+ report.json)
# Send report.txt back so the pipeline can be wired to the real file layout.
#
# What it shows: folder trees, file naming patterns, EEG headers (sampling rate, channels,
# duration, filters, events), the real bandwidth of the signal (does gamma survive?),
# .mat internals, and table COLUMN NAMES only.
# What it never prints: values of diagnosis / MMSE / group-like columns, or names/DOBs
# stored in EEG headers (it only flags that they exist).

# %% [1] setup ---------------------------------------------------------------------------
import os, sys, re, json, glob, zipfile, traceback, collections, datetime as dt
IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    from google.colab import drive
    drive.mount("/content/drive")
    os.system("pip -q install mne pymatreader h5py openpyxl > /dev/null")

ROOT = "/content/drive/MyDrive" if IN_COLAB else os.environ.get("NH_ROOT", ".")
FOLDERS = [                       # folders to inspect (edit if names differ)
    "EEG raw Ultimatum Game",
    "mask_unmask_preprocessed_data",
    "data",
    "ds004504-download",
    "eeg_alzheimer_pipeline",
]
if os.environ.get("NH_FOLDERS"):  # local testing only
    FOLDERS = os.environ["NH_FOLDERS"].split("|")
OUT_DIR = os.path.join(ROOT, "neurohertz_inspection")
SAMPLES_PER_TYPE = 3              # files opened per (folder, file type)
TREE_LINES = 60                   # max tree lines printed per folder

import numpy as np
import pandas as pd
import mne
mne.set_log_level("ERROR")

LABEL_LIKE = re.compile(r"group|diag|dx|class|label|mmse|moca|cdr|status|condition|ad\b|mci|control|patient|score|cognit", re.I)
PHI_LIKE = re.compile(r"name|dob|birth|phone|address|email|aadhaar|mrn|hospital.?no|uhid", re.I)
EEG_EXT = {".set", ".edf", ".bdf", ".vhdr", ".cnt", ".fif", ".gdf", ".eeg", ".mff", ".nxe", ".cdt", ".egi", ".lay", ".data"}
TABLE_EXT = {".csv", ".tsv", ".xlsx", ".xls"}
REPORT, JSONREP = [], {}


def say(*a):
    line = " ".join(str(x) for x in a)
    print(line); REPORT.append(line)


def human(n):
    for u in ["B", "KB", "MB", "GB"]:
        if n < 1024: return f"{n:.0f}{u}"
        n /= 1024
    return f"{n:.1f}TB"


def compact(o):
    """Lists of plain values -> one line, so the report stays short."""
    if isinstance(o, dict): return {k: compact(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        if all(isinstance(x, (str, int, float, bool)) or x is None for x in o):
            return ", ".join(str(x) for x in o)
        return [compact(x) for x in o]
    return o


def pattern(name):
    return re.sub(r"\d+", "#", name)


# %% [2] folder trees + naming patterns ---------------------------------------------------
def walk(folder):
    files = []
    for dp, dn, fn in os.walk(folder):
        dn.sort()
        for f in sorted(fn):
            p = os.path.join(dp, f)
            try: sz = os.path.getsize(p)
            except OSError: sz = -1
            files.append((p, sz))
    return files


INVENTORY = {}
for name in FOLDERS:
    folder = os.path.join(ROOT, name)
    say("\n" + "=" * 100); say(f"FOLDER: {name}")
    if not os.path.isdir(folder):
        say("  (not found)"); continue
    files = walk(folder)
    INVENTORY[name] = files
    by_ext = collections.Counter(os.path.splitext(p)[1].lower() or "(none)" for p, _ in files)
    size_ext = collections.Counter()
    for p, s in files: size_ext[os.path.splitext(p)[1].lower() or "(none)"] += max(s, 0)
    say(f"  files: {len(files)}   total: {human(sum(max(s,0) for _, s in files))}")
    for e, c in by_ext.most_common():
        say(f"   {e:8s} {c:6d} files  {human(size_ext[e])}")
    pats = collections.Counter(pattern(os.path.relpath(p, folder)) for p, _ in files)
    say("  naming patterns (digits -> #):")
    for pt, c in pats.most_common(25):
        say(f"   {c:5d} x  {pt}")
    say("  tree (first lines):")
    shown = 0
    for dp, dn, fn in os.walk(folder):
        depth = os.path.relpath(dp, folder).count(os.sep) + (0 if dp == folder else 1)
        say("   " + "  " * depth + os.path.basename(dp) + f"/  ({len(fn)} files, {len(dn)} dirs)")
        shown += 1
        for f in sorted(fn)[:3]:
            say("   " + "  " * (depth + 1) + f); shown += 1
        if shown > TREE_LINES:
            say("   ..."); break
    JSONREP[name] = {"n_files": len(files), "by_ext": dict(by_ext), "patterns": dict(pats.most_common(50))}


# %% [3] EEG headers + real bandwidth ----------------------------------------------------
def bandwidth_report(raw, seconds=60):
    sf = raw.info["sfreq"]
    n = int(min(raw.n_times, seconds * sf))
    start = int(min(raw.n_times - n, 30 * sf)) if raw.n_times > n else 0
    picks = "eeg" if "eeg" in raw.get_channel_types() else None
    x = raw.get_data(start=start, stop=start + n, picks=picks)
    return bandwidth_from_array(x, sf)


def bandwidth_from_array(x, sf):
    """x: (channels, samples) in Volts."""
    n = x.shape[-1]
    if x.size == 0 or n < sf: return {"note": "too short for a spectrum"}
    psd, fr = mne.time_frequency.psd_array_welch(x, sf, fmin=1, fmax=sf / 2 - 1, n_fft=int(min(2 * sf, n)), verbose=False)
    lp = np.log10(np.median(psd, 0) + 1e-30)
    def at(f): return float(lp[np.argmin(np.abs(fr - f))]) if fr.max() >= f else None
    ref30 = at(30)
    out = {"log10_psd_median_ch": {f: at(f) for f in (5, 10, 20, 30, 40, 45, 55, 70, 90, 120) if at(f) is not None}}
    # first frequency above 30 Hz where power is 20 dB (2 log units) below the 30 Hz level
    cut = None
    if ref30 is not None:
        for f, v in zip(fr, lp):
            if f > 30 and v < ref30 - 2: cut = float(f); break
    out["effective_lowpass_hz(-20dB vs 30Hz)"] = cut
    out["gamma_30_45_usable"] = bool(cut is None or cut > 45)
    out["amplitude_uV_median_std"] = float(np.median(x.std(1)) * 1e6)
    out["max_abs_uV"] = float(np.abs(x).max() * 1e6)
    return out


def open_eeg(p):
    ext = os.path.splitext(p)[1].lower()
    if ext == ".set":
        try: return mne.io.read_raw_eeglab(p, preload=False), "raw"
        except Exception:
            return mne.read_epochs_eeglab(p), "epochs"
    if ext == ".eeg":
        vh = os.path.splitext(p)[0] + ".vhdr"
        if os.path.exists(vh): return mne.io.read_raw_brainvision(vh, preload=False), "raw"
        return mne.io.read_raw_nihon(p, preload=False), "raw"
    return mne.io.read_raw(p, preload=False), "raw"


def inspect_eeg(p):
    r = {"file": p}
    obj, kind = open_eeg(p)
    info = obj.info
    r.update(kind=kind, sfreq=info["sfreq"], n_channels=len(info["ch_names"]), ch_names=info["ch_names"],
             ch_types=dict(collections.Counter(obj.get_channel_types())),
             highpass=info["highpass"], lowpass=info["lowpass"],
             line_freq=info.get("line_freq"),
             meas_date_present=info["meas_date"] is not None,
             subject_info_fields=sorted((info.get("subject_info") or {}).keys()))
    if r["subject_info_fields"]:
        r["WARNING"] = "header stores subject_info fields (values hidden) - check de-identification"
    if kind == "raw":
        r["duration_min"] = round(obj.n_times / info["sfreq"] / 60, 2)
        ann = obj.annotations
        r["n_annotations"] = len(ann)
        r["annotation_types"] = dict(collections.Counter(ann.description).most_common(40))
        try:
            ev, ev_id = mne.events_from_annotations(obj, verbose=False)
            r["event_ids"] = {k: int(v) for k, v in list(ev_id.items())[:40]}
        except Exception: pass
        r["bandwidth"] = bandwidth_report(obj)
    else:
        r["n_epochs"] = len(obj); r["epoch_tmin_tmax"] = (float(obj.tmin), float(obj.tmax))
        r["event_id"] = {k: int(v) for k, v in list(obj.event_id.items())[:40]}
        e = obj.get_data()[:200]                       # (epochs, ch, t) -> concatenate in time
        r["bandwidth_concatenated_epochs"] = bandwidth_from_array(np.concatenate(list(e), axis=-1), info["sfreq"])
    return r


# %% [4] .mat / numpy / tables / text --------------------------------------------------
def describe_array(a):
    a = np.asarray(a)
    d = {"shape": list(a.shape), "dtype": str(a.dtype)}
    if a.dtype.kind in "fiu" and a.size:
        flat = a.ravel()[: 5_000_000].astype(float)
        d.update(min=float(np.nanmin(flat)), max=float(np.nanmax(flat)), std=float(np.nanstd(flat)))
    return d


def inspect_mat(p):
    r = {"file": p}
    try:
        import scipy.io as sio
        m = sio.loadmat(p, squeeze_me=True, struct_as_record=False)
        r["format"] = "matlab<7.3"
        for k, v in m.items():
            if k.startswith("__"): continue
            if hasattr(v, "_fieldnames"):
                fields = {}
                for fn in v._fieldnames:
                    x = getattr(v, fn)
                    if isinstance(x, np.ndarray) and x.dtype.kind in "fiu":
                        fields[fn] = describe_array(x)
                    elif np.isscalar(x):
                        fields[fn] = x if not isinstance(x, bytes) else x.decode(errors="ignore")
                    else:
                        fields[fn] = type(x).__name__
                r[k] = {"struct_fields": fields}
                if {"srate", "nbchan", "data"} & set(v._fieldnames):
                    r[k]["looks_like"] = "EEGLAB EEG struct"
                    try: r[k]["chan_labels"] = [c.labels for c in np.atleast_1d(v.chanlocs)][:80]
                    except Exception: pass
                    try: r[k]["event_types"] = dict(collections.Counter(str(e.type) for e in np.atleast_1d(v.event)).most_common(30))
                    except Exception: pass
            elif isinstance(v, np.ndarray):
                r[k] = describe_array(v)
            else:
                r[k] = type(v).__name__
    except NotImplementedError:
        import h5py
        r["format"] = "matlab v7.3 (HDF5); dimensions shown in HDF5 order = REVERSED Matlab order"
        with h5py.File(p, "r") as h:
            def visit(name, obj):
                if isinstance(obj, h5py.Dataset):
                    r[name] = {"shape_hdf5": list(obj.shape), "matlab_shape": list(obj.shape[::-1]),
                               "dtype": str(obj.dtype), "matlab_class": str(obj.attrs.get("MATLAB_class", b""))}
                    if obj.size and obj.dtype.kind in "fiu" and obj.size < 50_000_000:
                        a = obj[()]
                        r[name].update(min=float(a.min()), max=float(a.max()), std=float(a.std()))
            h.visititems(visit)
    return r


def inspect_table(p):
    ext = os.path.splitext(p)[1].lower()
    if ext in (".xlsx", ".xls"):
        sheets = pd.read_excel(p, sheet_name=None)
    else:
        sheets = {"_": pd.read_csv(p, sep="\t" if ext == ".tsv" else None, engine="python")}
    out = {"file": p, "sheets": {}}
    for sn, df in sheets.items():
        cols = []
        for c in df.columns:
            col = {"name": str(c), "dtype": str(df[c].dtype), "n_missing": int(df[c].isna().sum()),
                   "n_unique": int(df[c].nunique())}
            if LABEL_LIKE.search(str(c)): col["note"] = "LABEL-LIKE: values hidden"
            if PHI_LIKE.search(str(c)): col["note"] = "POSSIBLE PERSONAL DATA: values hidden; remove before analysis"
            cols.append(col)
        out["sheets"][sn] = {"n_rows": int(len(df)), "columns": cols}
    return out


def inspect_text(p, n=30):
    name = os.path.basename(p).lower()
    if "participant" in name or LABEL_LIKE.search(name):
        return {"file": p, "note": "looks like a participant/label file: content not printed"}
    with open(p, errors="ignore") as f:
        return {"file": p, "head": [next(f, "").rstrip() for _ in range(n)]}


def inspect_zip(p):
    with zipfile.ZipFile(p) as z:
        names = z.namelist()
    return {"file": p, "n_members": len(names), "first": names[:40]}


def dispatch(p):
    ext = os.path.splitext(p)[1].lower()
    if ext in EEG_EXT:
        return inspect_eeg(p)
    if ext == ".mat": return inspect_mat(p)
    if ext in (".npy",): return {"file": p, **describe_array(np.load(p, mmap_mode="r")[:])} if os.path.getsize(p) < 2e9 else {"file": p}
    if ext == ".npz":
        z = np.load(p); return {"file": p, **{k: describe_array(z[k]) for k in z.files[:20]}}
    if ext in TABLE_EXT: return inspect_table(p)
    if ext in (".json", ".txt", ".md", ".log", ".vmrk", ".hdr", ".ini") or os.path.basename(p).upper().startswith("README"):
        return inspect_text(p)
    if ext == ".zip": return inspect_zip(p)
    return None


# %% [5] run the per-file inspection -------------------------------------------------------
for name, files in INVENTORY.items():
    say("\n" + "#" * 100); say(f"DETAILS: {name}")
    done = collections.Counter()
    JSONREP[name]["samples"] = []
    # tables and READMEs are always shown (column names only); EEG/mat: a few per pattern
    for p, sz in files:
        ext = os.path.splitext(p)[1].lower()
        key = (ext, pattern(os.path.basename(p)))
        always = ext in TABLE_EXT or os.path.basename(p).upper().startswith("README") or ext == ".zip"
        if not always and done[key] >= SAMPLES_PER_TYPE: continue
        if ext == ".eeg" and os.path.exists(os.path.splitext(p)[0] + ".vhdr"): continue   # read via .vhdr
        if ext == ".fdt": continue                                                          # read via .set
        try:
            res = dispatch(p)
        except Exception as e:
            res = {"file": p, "ERROR": f"{type(e).__name__}: {e}"}
        if res is None: continue
        done[key] += 1
        res["size"] = human(sz)
        JSONREP[name]["samples"].append(res)
        say("-" * 100)
        say(json.dumps(compact(res), indent=1, default=str)[:6000])

# %% [6] save -------------------------------------------------------------------------------
os.makedirs(OUT_DIR, exist_ok=True)
stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
with open(os.path.join(OUT_DIR, f"report_{stamp}.txt"), "w") as f:
    f.write("\n".join(REPORT))
with open(os.path.join(OUT_DIR, f"report_{stamp}.json"), "w") as f:
    json.dump(JSONREP, f, indent=1, default=str)
say(f"\nSaved: {OUT_DIR}/report_{stamp}.txt  (send this file back)")
