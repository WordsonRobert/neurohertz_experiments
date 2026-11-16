"""Driven (photic) responses from ds006036, AD + CN, raw recordings (70 Hz hardware LP, Cz ref -> average ref).
Blocks are found from the per-flash 'Photo/HV mark' events. Each block is cut into 2-s epochs starting on a flash
(integer number of cycles for 5-20 Hz). Per epoch: FFT, posterior channels. Per block-frequency fd and harmonic n
(n*fd <= 47 Hz, != 50): evoked amplitude (|mean complex FFT|), total power, noise = mean power at +-1..2 Hz,
SNR = evoked^2 / noise. Output: one row per subject x fd x n.
"""
import glob, os, sys, numpy as np, pandas as pd, mne
mne.set_log_level("ERROR")
D = "/home/claude/data/ds006036"; OUT = "/home/claude/work/phaseC/out"; os.makedirs(OUT, exist_ok=True)
POST = ["O1", "O2", "P3", "P4", "Pz"]; EP = 2.0; PTP = 400e-6


def blocks(ev):
    t = np.sort(ev.loc[ev.trial_type == "Photo/HV mark", "onset"].values.astype(float))
    if len(t) < 5: return []
    d = np.diff(t); out = []; i = 0
    while i < len(d):
        j = i
        while j + 1 < len(d) and abs(d[j + 1] - d[i]) < 0.15 * d[i]: j += 1
        n = j - i + 2
        f = 1 / np.median(d[i:j + 1])
        fd = 5 * round(f / 5)
        if n >= 10 and abs(f - fd) < 0.5:
            out.append((fd, t[i], t[j + 1]))
        i = j + 1
    return out


def manual_read(fn):
    import scipy.io as sio
    try:
        h = sio.loadmat(fn, squeeze_me=True, struct_as_record=False)
        h = h.get("EEG", h)
        nb, sr = int(h["nbchan"] if isinstance(h, dict) else h.nbchan), float(h["srate"] if isinstance(h, dict) else h.srate)
        loc = h["chanlocs"] if isinstance(h, dict) else h.chanlocs
        names = [str(c.labels) for c in loc]
        x = np.fromfile(fn[:-4] + ".fdt", dtype="<f4")
        x = x[: (len(x) // nb) * nb].reshape(nb, -1, order="F") * 1e-6
        return mne.io.RawArray(x, mne.create_info(names, sr, "eeg"), verbose=False)
    except Exception as e:  # noqa
        print("manual fail", e); return None


rows = []
P = pd.read_csv(f"{D}/participants.tsv", sep="\t").set_index("participant_id")
for fn in sorted(glob.glob(f"{D}/sub-*_task-photomark_eeg.set")):
    s = os.path.basename(fn)[:7]
    if P.loc[s, "Group"] not in ("A", "C"): continue
    # ds006036 bug: 63/65 .set headers point to ANOTHER subject's .fdt, so mne.read_raw_eeglab loads the wrong
    # person. Always read this subject's own .fdt (its length matches this header's pnts for all 65).
    raw = manual_read(fn)
    if raw is None: continue
    raw.set_eeg_reference("average")
    sf = raw.info["sfreq"]; X = raw.get_data(picks=POST)
    ev = pd.read_csv(f"{D}/{s}_task-photomark_events.tsv", sep="\t")
    flashes = np.sort(ev.loc[ev.trial_type == "Photo/HV mark", "onset"].values.astype(float))
    for fd, t0, t1 in blocks(ev):
        fl = flashes[(flashes >= t0 - 1e-6) & (flashes <= t1 + 1e-6)]
        starts = []; last = -1e9
        for t in fl:
            if t >= last + EP - 1e-6 and t + EP <= t1 + 1 / fd + 1e-6: starts.append(t); last = t
        nE = int(EP * sf); F = np.fft.rfftfreq(nE, 1 / sf); C = []
        for t in starts:
            a = int(round(t * sf)); seg = X[:, a:a + nE]
            if seg.shape[1] < nE or np.ptp(seg, 1).max() > PTP: continue
            C.append(np.fft.rfft(seg - seg.mean(1, keepdims=True), axis=1) / nE)
        if len(C) < 3: continue
        C = np.array(C)                                   # epochs x ch x freq
        evoked = np.abs(C.mean(0))                        # ch x freq
        power = (np.abs(C) ** 2).mean(0)
        for n in range(1, 10):
            fh = n * fd
            if fh > 47 or abs(fh - 50) < 1: continue
            k = int(np.argmin(np.abs(F - fh)))
            nb = [int(np.argmin(np.abs(F - (fh + d)))) for d in (-2, -1.5, -1, 1, 1.5, 2)]
            noise = power[:, nb].mean(1)
            rows.append(dict(sub=s, group=P.loc[s, "Group"], age=P.loc[s, "Age"], fd=fd, n=n, f=fh, n_ep=len(C),
                             evoked=float(np.mean(evoked[:, k])), log_evoked=float(np.log10(np.mean(evoked[:, k] ** 2))),
                             log_noise=float(np.log10(np.mean(noise))),
                             snr_db=float(10 * np.log10(np.mean(evoked[:, k] ** 2) / np.mean(noise))),
                             itc=float(np.mean(np.abs(C[:, :, k].mean(0)) / np.abs(C[:, :, k]).mean(0)))))
    print(s, P.loc[s, "Group"], [(b[0], round(b[2] - b[1], 1)) for b in blocks(ev)], flush=True)
R = pd.DataFrame(rows); R.to_csv(f"{OUT}/photic_responses.csv", index=False)
print(R.groupby(["group", "fd", "n"]).size().unstack(["fd", "n"]).to_string())
