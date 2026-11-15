"""Method sanity checks. Run: python -m pytest -q tests/"""
from __future__ import annotations

import numpy as np


def test_iaaft_preserves_amplitude_distribution_and_spectrum():
    from nh.surrogates import iaaft
    rng = np.random.default_rng(0)
    t = np.arange(5000) / 250
    x = np.sin(2 * np.pi * 10 * t) * (1 + 0.5 * np.sin(2 * np.pi * 0.3 * t)) + 0.3 * rng.standard_normal(t.size)
    s = iaaft(x, rng, iterations=100)
    assert np.allclose(np.sort(s), np.sort(x))                     # exact amplitude distribution
    px, ps = np.abs(np.fft.rfft(x)) ** 2, np.abs(np.fft.rfft(s)) ** 2
    rel = np.abs(np.convolve(px, np.ones(25), "same") - np.convolve(ps, np.ones(25), "same")).sum() / px.sum()
    assert rel < 0.1, rel                                           # spectrum matched (smoothed)


def test_if_of_pure_tone_is_its_frequency():
    from nh.config import load_config
    from nh.gamma import if_metrics_channel
    cf = load_config()["features"]
    sf = 250.0; t = np.arange(int(60 * sf)) / sf
    x = np.sin(2 * np.pi * 38.0 * t) + 1e-3 * np.random.default_rng(1).standard_normal(t.size)
    m = if_metrics_channel(x, [(0, x.size)], sf, cf["gamma_band"], cf)
    assert abs(m["if_median"] - 38.0) < 0.05
    assert m["if_sd"] < 0.05


def test_delong_matches_mann_whitney():
    from scipy.stats import mannwhitneyu
    from nh.stats import delong_auc
    rng = np.random.default_rng(2)
    y = np.r_[np.zeros(40), np.ones(35)].astype(int)
    s = rng.standard_normal(75) + 0.8 * y
    u = mannwhitneyu(s[y == 1], s[y == 0]).statistic / (35 * 40)
    assert abs(delong_auc(y, s)["auc"] - u) < 1e-12


def test_icc_perfect_and_null():
    from nh.stats import icc_2_1
    rng = np.random.default_rng(3)
    a = rng.standard_normal(50)
    assert icc_2_1(np.c_[a, a]) > 0.999
    assert abs(icc_2_1(rng.standard_normal((400, 2)))) < 0.15
