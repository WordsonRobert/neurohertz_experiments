"""Checks for the mechanism programme: dynamics descriptors, oscillation fit, simulators,
fingerprint comparison, scorecard rules, Drive path handling."""
import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nh.config import load_config  # noqa: E402

CF = load_config()["features"]
SF = 250.0


def _segs_from(f_raw, A, fm=None):
    fm = f_raw if fm is None else fm
    return [(f_raw, fm, A, np.zeros_like(A))]


def test_slip_counting_exact():
    from nh.dynamics import dynamics_from_segments
    n = int(60 * SF)
    f = np.full(n, 38.0); A = np.ones(n)
    for i in np.linspace(1000, n - 1000, 12).astype(int):
        f[i:i + 3] = 120.0                                      # 12 out-of-band excursions
    r = dynamics_from_segments(_segs_from(f, A), SF, [30, 45], CF, gate=0.5)
    assert r["slip_rate"] == pytest.approx(12.0, rel=0.01)       # 12 per minute


def test_slow_vs_fast_split_and_coupling():
    from nh.dynamics import dynamics_from_segments
    rng = np.random.default_rng(0)
    n = int(120 * SF)
    t = np.arange(n) / SF
    slow = 2.0 * np.sin(2 * np.pi * 0.2 * t)                     # 5-s wander
    A = np.exp(0.5 * np.sin(2 * np.pi * 0.2 * t))                 # envelope moves WITH frequency
    fast = rng.normal(0, 0.5, n)
    r_slow = dynamics_from_segments(_segs_from(38 + slow + fast, A), SF, [30, 45], CF, gate=0)
    r_fast = dynamics_from_segments(_segs_from(38 + 0.1 * slow + 4 * fast, np.ones(n)), SF, [30, 45], CF, gate=0)
    assert r_slow["slow_frac"] > 0.6 > r_fast["slow_frac"]
    assert r_slow["if_env_coupling"] > 0.8
    assert 0.7 < r_slow["slow_tau_s"] < 1.3                     # acf of a 5-s sinusoid hits 1/e at ~0.95 s


def test_presence_gate_and_width_recovery():
    from nh.mechsim import add_background, simulate_circuit
    from nh.oscfit import channel_oscillation
    x = simulate_circuit([{}], [{"E": (0, 1), "P": (0, 1)}], dur_s=120, seed=4)[0]
    seg = [(0, len(x))]
    none = channel_oscillation(add_background(x, SF, np.random.default_rng(0), gamma_snr=0.0), seg, SF, CF)
    some = channel_oscillation(add_background(x, SF, np.random.default_rng(0), gamma_snr=0.35), seg, SF, CF)
    assert none["osc_present"] == 0.0 and some["osc_present"] == 1.0
    assert some["osc_width_hz"] == pytest.approx(2 * 25 / (2 * np.pi), rel=0.3)   # linearised decay 25 /s
    assert 33 < some["osc_f0"] < 41


@pytest.mark.parametrize("theory", ["synapses_onto_pv", "sst_loss", "acetylcholine", "tau_silencing"])
def test_rate_knobs_keep_a_damped_gamma_rhythm(theory):
    from scipy.signal import welch
    from nh.mechsim import knob_params, simulate_circuit
    p, d = knob_params(theory, 1.0)
    x = simulate_circuit([p], [d], dur_s=20, seed=1)[0]
    f, P = welch(x, SF, nperseg=1000)
    m = (f > 15) & (f < 100)
    assert np.isfinite(x).all() and 20 < f[m][np.argmax(P[m])] < 50


def test_cycle_model_runs_every_theory():
    from nh.cyclemodel import simulate_cycles
    from nh.mechsim import THEORIES
    for th in [None] + THEORIES:
        x = simulate_cycles(th, 0.5, dur_s=10, seed=0)
        assert x.shape == (int(10 * SF),) and np.isfinite(x).all()


def test_fingerprint_compare_recovers_planted_mixture():
    from nh.fingerprint import compare
    rng = np.random.default_rng(1)
    feats = [f"f{i}" for i in range(10)]
    F = pd.DataFrame(rng.normal(size=(4, 10)), index=["a", "b", "c", "d"], columns=feats)
    eff = pd.Series(2.0 * F.loc["b"].values + rng.normal(0, 0.1, 10), index=feats)
    r = compare(eff, F, local=["a", "b"], inputs=["c", "d"])
    assert r["best_single"] == "b" and r["local_share"] > 0.8


def test_scorecard_classification_rules():
    spec = importlib.util.spec_from_file_location("m14", ROOT / "scripts" / "14_mechanism_tests.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    c = m.classify
    assert c("+", 0.8, 0.01, False, 0.05) == "consistent"
    assert c("+", -0.8, 0.01, False, 0.05) == "inconsistent"
    assert c("+", 0.1, 0.40, True, 0.05) == "inconsistent"           # equivalence refutes a predicted effect
    assert c("+", 0.3, 0.30, False, 0.05) == "inconclusive"
    assert c("0", 0.05, 0.80, True, 0.05) == "consistent"
    assert c("0", 0.9, 0.001, False, 0.05) == "inconsistent"
    assert c("?", 0.9, 0.001, False, 0.05) == "no_prediction"


def test_mechanism_tests_script_only_opens_labels_through_the_gate():
    src = (ROOT / "scripts" / "14_mechanism_tests.py").read_text()
    assert "open_labels(" in src and "read_participants" not in src and "participants.tsv" not in src


def test_roots_expand_env_glob_and_relative(tmp_path, monkeypatch):
    from nh.datasets import expand_roots
    (tmp_path / "ds004504-download-part1").mkdir(); (tmp_path / "ds004504-download-part2").mkdir()
    monkeypatch.setenv("NH_DRIVE", str(tmp_path))
    got = expand_roots(["${NH_DRIVE}/ds004504-download*", "${NH_DRIVE}/missing", "nh"])
    assert got[:2] == [str(tmp_path / "ds004504-download-part1"), str(tmp_path / "ds004504-download-part2")]
    assert got[2] == str(ROOT / "nh")
    assert len(got) == 3


def test_xjit_survives_zero_envelope():
    """SST ridge amplitudes can be exactly 0; a secondary metric must never crash a subject."""
    from nh.gamma import _xjit
    rng = np.random.default_rng(0)
    A = np.abs(rng.normal(1, 0.5, 20000)); A[::7] = 0
    assert np.isfinite(_xjit(38 + rng.normal(0, 1, 20000), A))
    assert np.isnan(_xjit(np.full(20000, 38.0), np.zeros(20000)))


def test_no_permutation_p_without_data():
    """Regression: with 0 subjects (e.g. nobody passes the gamma presence gate) partial_spearman returned
    p = 1/(n_perm+1) because NaN comparisons are False. Both tests must refuse instead."""
    import numpy as np, pandas as pd, pytest
    from nh.stats import group_effect, partial_spearman
    empty = pd.DataFrame({"subject": [], "group": [], "x": [], "y": [], "age": []})
    with pytest.raises(ValueError):
        partial_spearman(empty, "x", "y", ["age"], 99, 10, 0)
    const = pd.DataFrame({"subject": [f"s{i}" for i in range(12)], "group": ["AD"] * 6 + ["CN"] * 6,
                          "x": np.ones(12), "y": np.arange(12.0), "age": np.arange(12.0)})
    with pytest.raises(ValueError):
        partial_spearman(const, "x", "y", ["age"], 99, 10, 0)
    with pytest.raises(ValueError):
        group_effect(const, "x", "group", "AD", "CN", ["age"], 99, 10, 0)
