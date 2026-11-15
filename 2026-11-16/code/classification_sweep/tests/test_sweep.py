"""Ground-truth checks for the sweep's estimators on synthetic signals (run: pytest -q tests)."""
import importlib.util, sys
from pathlib import Path
import numpy as np
import pytest

SW = Path(__file__).resolve().parents[1] / "sweep"
sys.path.insert(0, str(SW))
spec = importlib.util.spec_from_file_location("f10", SW / "10_features_raw.py")
f10 = importlib.util.module_from_spec(spec); spec.loader.exec_module(f10)
SF = 250.0
rng = np.random.default_rng(0)


def pink(n, beta=1.0, seed=0):
    r = np.random.default_rng(seed)
    X = np.fft.rfft(r.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SF); f[0] = f[1]
    return np.fft.irfft(X / f ** (beta / 2), n=n)


def test_irasa_separates_peak_from_powerlaw():
    n = int(120 * SF); t = np.arange(n) / SF
    x = pink(n, 2.0); x /= x.std()
    x2 = x + 0.15 * np.sin(2 * np.pi * 40 * t)
    ep = f10.epochs_of(np.vstack([x, x2]), SF)
    f, mixed, fract = f10.irasa(ep, SF)
    per = np.log10(mixed) - np.log10(fract)
    m40 = (f > 39) & (f < 41); mfl = (f > 25) & (f < 35)
    assert per[1, m40].max() > 0.5            # the sine shows up only in the periodic part
    assert abs(per[0, m40].mean()) < 0.15     # pure power law: no periodic residue
    sl = np.polyfit(np.log10(f[(f > 3) & (f < 45)]), np.log10(fract[0, (f > 3) & (f < 45)]), 1)[0]
    assert -2.4 < sl < -1.6                    # fractal slope recovered (~ -2)


def test_bursts_narrowband_vs_broadband():
    n = int(60 * SF); t = np.arange(n) / SF
    base = pink(n, 1.0, 1); base /= base.std()
    osc = base.copy(); emg = base.copy()
    for k in range(20):
        a = int((2 + 2.8 * k) * SF); L = int(0.2 * SF)
        osc[a:a + L] += 3 * np.sin(2 * np.pi * 40 * t[a:a + L]) * np.hanning(L)
        w = f10.bandpass(rng.standard_normal(L + 400), SF, 20, 110)[200:200 + L]
        emg[a:a + L] += 6 * w / w.std() * np.hanning(L)
    segs = np.array([[0, n]])
    out = {}
    for name, x in (("osc", osc), ("emg", emg)):
        X = np.vstack([x, base])
        xb = f10.lowpass_segments(X, segs, SF, 70.0, edge=25)
        df, thr = f10.burst_table(X, xb, segs, SF, ["P3", "Pz"], np.random.default_rng(1))
        out[name] = df[df.ch == "P3"]
    o, e = out["osc"], out["emg"]
    assert len(o) >= 15
    assert abs(o.f_mean.median() - 40) < 2.0
    big_o = o[o.amp_rel95 > 1.5]; big_e = e[e.amp_rel95 > 1.5]
    assert big_o.nb_index.median() > big_e.nb_index.median() + 0.2   # oscillation is narrowband
    assert big_e.emg_coact.median() > big_o.emg_coact.median()        # muscle-like burst co-activates 53-68 Hz


def test_pac_and_harmonic_locking():
    n = int(120 * SF); t = np.arange(n) / SF
    r = np.random.default_rng(3)
    # drifting theta phase (real rhythms are not perfectly periodic; a perfectly periodic toy signal stays
    # coupled under any circular shift, which would make every time-shift null degenerate)
    phi = 2 * np.pi * np.cumsum(6 + 1.5 * f10.bandpass(r.standard_normal(n), SF, 0.1, 1.0, 0.1) * 10) / SF
    th = np.sin(phi)
    amp = 1 + 0.8 * np.cos(phi)
    x = th + 0.3 * amp * np.sin(2 * np.pi * 40 * t) + 0.3 * r.standard_normal(n)
    segs = np.array([[0, n]])
    ph = np.angle(f10.analytic(x, segs, SF, 4, 8, 2.0, 125)); za = f10.analytic(x, segs, SF, 30, 48, None, 125)
    ok = np.isfinite(ph) & np.isfinite(za)
    _, z = f10.shift_z(f10.tort_mi, ph[ok], np.abs(za[ok]), SF, r, 50)
    assert z > 5
    y = 0.3 * r.standard_normal(n) + np.sin(phi) + 0.3 * np.sin(2 * np.pi * 40 * t)   # no coupling
    ph = np.angle(f10.analytic(y, segs, SF, 4, 8, 2.0, 125)); za = f10.analytic(y, segs, SF, 30, 48, None, 125)
    ok = np.isfinite(ph) & np.isfinite(za)
    _, z0 = f10.shift_z(f10.tort_mi, ph[ok], np.abs(za[ok]), SF, r, 50)
    assert abs(z0) < 3.5
    # non-sinusoidal 10 Hz alpha (sawtooth-like) -> strong 1:4 locking with its 40 Hz harmonic
    pa_true = 2 * np.pi * np.cumsum(10 + 2 * f10.bandpass(r.standard_normal(n), SF, 0.1, 1.0, 0.1) * 10) / SF
    saw = sum(np.sin(k * pa_true) / k for k in range(1, 6)) + 0.2 * r.standard_normal(n)
    pa = np.angle(f10.analytic(saw, segs, SF, 8, 12, 2.0, 125)); pg = np.angle(f10.analytic(saw, segs, SF, 37, 43, None, 125))
    ok = np.isfinite(pa) & np.isfinite(pg)
    plv = lambda a, b: float(np.abs(np.mean(np.exp(1j * (4 * a - b)))))
    _, zh = f10.shift_z(plv, pa[ok], pg[ok], SF, r, 50)
    assert zh > 5


def test_sharp_transients():
    n = int(60 * SF)
    x = pink(n, 1.0, 5); x /= x.std()
    pos = np.arange(5, 55, 5) * int(SF)
    k = np.arange(-10, 11); spike = 12 * np.exp(-0.5 * (k / 3.0) ** 2)
    for p in pos:
        x[p - 10:p + 11] += spike
    df = f10.sharp_transients(x[None], SF, ["Cz"])
    hits = sum(np.any(np.abs(df.t_s.to_numpy() * SF - p) < 5) for p in pos)
    assert hits >= 9 and len(df) <= 14


# ---------------------------------------------------------------- stage 12: SNR-matched instability
spec12 = importlib.util.spec_from_file_location("f12", SW / "12_band_instability.py")
f12 = importlib.util.module_from_spec(spec12); spec12.loader.exec_module(f12)


def _alpha(n, jitter_hz, amp, seed):
    """Pink background + a 10 Hz rhythm whose frequency wanders (OU process, SD = jitter_hz), bursting on/off."""
    r = np.random.default_rng(seed)
    bg = pink(n, 1.0, seed); bg /= bg.std()
    w = np.zeros(n); k = np.exp(-1 / (0.3 * SF))
    e = r.standard_normal(n) * jitter_hz * np.sqrt(1 - k ** 2)
    for i in range(1, n):
        w[i] = k * w[i - 1] + e[i]
    ph = 2 * np.pi * np.cumsum(10 + w) / SF
    env = 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * np.arange(n) / SF + r.uniform(0, 6))   # waxing and waning
    return bg + amp * env * np.sin(ph)


def _ifsd(x, matched=True):
    n = len(x); segs = np.array([[0, n]])
    ep = f10.epochs_of(x[None], SF)
    fi, _, fract = f10.irasa(ep, SF)
    bgv = f12.background_power(fract[0], fi, 8, 12)
    m = f12.channel_metrics(x, segs, SF, 8, 12, bgv, np.log10(fract[0] + 1e-30), fi)
    return m["if_sd_b1"] if matched else m["if_sd_naive"]


# AUDIT 2026-11-15: a test that instantaneous-SNR matching alone removes the amplitude confound FAILED
# (same jitter, amplitude 0.45 vs 1.2: matched gap 17.5%, naive gap 17%). Matching equalizes the measurement
# noise of each sample but not the mixture of rhythm and background at that SNR. The spectrum-matched surrogate
# excess (tests below) is therefore the primary SNR control; matching is kept as a secondary safeguard.


def test_snr_matched_instability_still_sees_true_jitter():
    n = int(240 * SF)
    calm = [_ifsd(_alpha(n, 0.3, 0.8, s)) for s in range(3)]
    shaky = [_ifsd(_alpha(n, 1.5, 0.8, s + 20)) for s in range(3)]
    assert np.mean(shaky) > 1.3 * np.mean(calm)


def _gauss_like(x, seed):
    return f10.phase_surrogate(x, np.random.default_rng(seed))


def _excess(x, seeds=range(6)):
    n = len(x); segs = np.array([[0, n]])
    ep = f10.epochs_of(x[None], SF); fi, _, fract = f10.irasa(ep, SF)
    bgv = f12.background_power(fract[0], fi, 8, 12); lb = np.log10(fract[0] + 1e-30)
    obs = f12.channel_metrics(x, segs, SF, 8, 12, bgv, lb, fi)
    sur = [f12.channel_metrics(_gauss_like(x, 100 + s), segs, SF, 8, 12, bgv, lb, fi) for s in seeds]
    return {k: obs[k] - np.nanmean([d[k] for d in sur]) for k in ("if_sd_b1", "period_cv_b1", "if_sd_naive")}


def test_excess_is_zero_for_gaussian_processes_at_any_snr():
    n = int(240 * SF)
    for amp in (0.45, 1.2):                      # a Gaussian process with a weak or a strong alpha peak
        g = _gauss_like(_alpha(n, 0.6, amp, 1), 7)
        e = _excess(g)
        assert abs(e["if_sd_b1"]) < 0.05 and abs(e["period_cv_b1"]) < 0.02, e


def test_excess_detects_slow_frequency_wander():
    """A rhythm that wanders slowly in frequency (non-Gaussian dynamics) differs from its own Gaussian twin."""
    n = int(240 * SF); r = np.random.default_rng(5)
    bg = pink(n, 1.0, 9); bg /= bg.std()
    k = np.exp(-1 / (4.0 * SF)); w = np.zeros(n); e = r.standard_normal(n) * 1.2 * np.sqrt(1 - k ** 2)
    for i in range(1, n):
        w[i] = k * w[i - 1] + e[i]
    x = bg + 1.0 * np.sin(2 * np.pi * np.cumsum(10 + w) / SF)        # constant amplitude, slowly wandering frequency
    ex = _excess(x)
    assert abs(ex["if_sd_b1"]) > 0.05 or abs(ex["period_cv_b1"]) > 0.02, ex


def test_freq_windows_avoid_line_noise_and_cover_range():
    s13 = importlib.util.spec_from_file_location("s13", SW / "13_freq_instability.py")
    m = importlib.util.module_from_spec(s13); s13.loader.exec_module(m)
    w = m.windows()
    assert all(not (lo < 52.5 and hi > 47.5) for lo, hi, _ in w)          # never touches the 50 Hz notch
    assert w[0][:2] == (2.0, 6.0) and w[-1][:2] == (86.0, 90.0)
    assert {g for *_, g in w} == {"A", "B"} and all((hi <= 47.5) == (g == "A") for _, hi, g in w)
