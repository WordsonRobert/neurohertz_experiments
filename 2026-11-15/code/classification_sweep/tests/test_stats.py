"""Calibration of the sweep's statistics (AUDIT 2026-11-15): correct t, correct FWER under the null,
no leakage in prediction."""
import importlib.util, sys
from pathlib import Path
import numpy as np
import pytest

SW = Path(__file__).resolve().parents[1] / "sweep"
sys.path.insert(0, str(SW))


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, SW / fn)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


f20 = _load("f20", "20_frequency_resolved.py")


def test_ols_t_matches_statsmodels_hc0():
    import statsmodels.api as sm
    r = np.random.default_rng(1); n = 50
    X = np.column_stack([np.ones(n), r.standard_normal(n), r.integers(0, 2, n), r.integers(0, 2, n)]).astype(float)
    Y = r.standard_normal((n, 7)) + 0.4 * X[:, [3]]
    t = f20.ols_t(Y, X, 3)
    for k in range(7):
        ref = sm.OLS(Y[:, k], X).fit(cov_type="HC0")
        assert abs(t[k] - ref.tvalues[3]) < 1e-8


def _smooth_null(r, n, nf, nch, adj_dense):
    Z = r.standard_normal((n, nf, nch))
    Z = Z + 0.6 * np.roll(Z, 1, axis=1) + 0.6 * np.roll(Z, -1, axis=1)          # correlated across frequency
    Z = Z + 0.3 * np.einsum("nfc,cd->nfd", Z, adj_dense)                         # and across neighbours
    return Z.reshape(n, -1)


def test_cluster_fwer_is_calibrated_under_the_null():
    chs = ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "T3", "C3", "Cz", "C4", "T4", "T5", "P3", "Pz", "P4", "T6", "O1", "O2"]
    adj_ch = f20.ch_adjacency(chs); nf = 15
    adj = f20.grid_adjacency(nf, adj_ch)
    A = adj_ch.toarray().astype(float); np.fill_diagonal(A, 0)
    r = np.random.default_rng(7); hits = 0; sims = 120
    for s in range(sims):
        n = 40
        Y = _smooth_null(r, n, nf, len(chs), A)
        age = r.normal(70, 6, n); sex = r.integers(0, 2, n); g = r.permutation(np.r_[np.ones(20), np.zeros(20)])
        X = np.column_stack([np.ones(n), (age - age.mean()) / age.std(), sex - sex.mean(), g])
        _, cl, _ = f20.fl_cluster_test(Y, X, 3, adj, 199, r)
        hits += any(c[3] < 0.05 for c in cl)
    rate = hits / sims
    assert rate <= 0.11, rate        # nominal 0.05; binomial 97.5% upper bound for 120 sims is about 0.10


def test_cluster_detects_a_planted_effect():
    chs = ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "T3", "C3", "Cz", "C4", "T4", "T5", "P3", "Pz", "P4", "T6", "O1", "O2"]
    adj_ch = f20.ch_adjacency(chs); nf = 15; adj = f20.grid_adjacency(nf, adj_ch)
    r = np.random.default_rng(3); n = 40
    Y = r.standard_normal((n, nf, len(chs)))
    g = np.r_[np.ones(20), np.zeros(20)]
    Y[g == 1, 5:9, 13:19] += 1.0                                                 # posterior, bins 5-8
    X = np.column_stack([np.ones(n), r.standard_normal(n), g])
    _, cl, _ = f20.fl_cluster_test(Y.reshape(n, -1), X, 2, adj, 199, r)
    best = cl[0]
    fi, ci = np.unravel_index(best[1], (nf, len(chs)))
    assert best[3] < 0.05 and best[0] == 1
    assert set(fi) <= set(range(4, 10))                      # frequency extent is exactly the planted bins
    assert np.mean(ci >= 12) >= 0.8                           # and the cluster is mostly the planted channels


def test_prediction_has_no_leakage_on_noise():
    f50 = _load("f50", "50_predict.py")
    import pandas as pd
    r = np.random.default_rng(11); n = 60
    D = pd.DataFrame(r.standard_normal((n, 2)), columns=["theta_alpha", "iaf"])
    y = r.permutation(np.r_[np.ones(30), np.zeros(30)]).astype(int)
    res, aucs = f50.run_model("slowing", ["slowing"], D, y, list(range(n)), None, None, 10, 0, 1)
    assert 0.35 < res["auc"] < 0.65
