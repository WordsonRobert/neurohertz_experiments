"""Tests for the method-review additions: overrides, estimators, seam matching, BSS-CCA,
classifier selection, and the label-free selection script's AST (no label access)."""
import ast
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nh.config import apply_overrides, extraction_hash, load_config  # noqa: E402


def test_apply_overrides_copies_and_parses():
    cfg = load_config()
    before = cfg["preprocessing"]["reference"]
    other = "rest" if before != "rest" else "average"
    new = apply_overrides(cfg, [f"preprocessing.reference={other}", "features.vmd.K=6", "features.if_median.mode=single"])
    assert new["preprocessing"]["reference"] == other and new["features"]["vmd"]["K"] == 6
    assert cfg["preprocessing"]["reference"] == before             # original untouched
    assert apply_overrides(cfg, None) == cfg


def test_extraction_hash_changes_with_override():
    p = ROOT / "config" / "pipeline.yaml"
    cfg = load_config()
    assert extraction_hash(p, cfg) != extraction_hash(p, apply_overrides(cfg, ["features.if_estimator=sst"]))


def _tone(f_inst, sf=250.0, dur=8.0, seed=0):
    rng = np.random.default_rng(seed)
    n = int(sf * dur)
    f = np.full(n, f_inst) if np.isscalar(f_inst) else f_inst
    return np.cos(2 * np.pi * np.cumsum(f) / sf) + 0.05 * rng.standard_normal(n), sf


@pytest.mark.parametrize("est", ["hilbert", "sst", "vmd"])
def test_estimators_recover_constant_frequency(est):
    pytest.importorskip({"sst": "ssqueezepy", "vmd": "vmdpy"}.get(est, "numpy"))
    from nh.gamma import ESTIMATORS
    x, sf = _tone(38.0)
    cfg = load_config()["features"]
    fi, amp, _ = ESTIMATORS[est](x, sf, cfg["gamma_band"], cfg)
    mid = slice(len(x) // 4, 3 * len(x) // 4)
    assert abs(np.nanmedian(fi[mid]) - 38.0) < 1.0
    assert np.all(np.isfinite(amp[mid]))


def test_multi_window_median_less_spiky_than_raw():
    from nh.gamma import _median_smooth
    rng = np.random.default_rng(1)
    f = 38 + rng.standard_normal(2000); f[::50] += 30           # phase-slip spikes
    cfg = load_config()["features"]
    sm = _median_smooth(f, 250.0, cfg)
    assert np.std(sm) < 0.5 * np.std(f)


def test_match_chunks_endpoints():
    from nh.gamma import match_chunks
    rng = np.random.default_rng(2)
    x = np.convolve(rng.standard_normal(250 * 120), np.ones(5) / 5, "same")
    chunks = match_chunks(x, [(0, len(x))], 250.0, 30.0, 0.3)
    assert len(chunks) >= 3
    raw_gap = np.mean([abs(x[s] - x[s + 7500 - 1]) for s in range(0, len(x) - 7500, 7500)])
    gaps = [abs(x[a] - x[b - 1]) for a, b in chunks]
    assert np.mean(gaps) < raw_gap                              # better endpoint match than naive cuts
    assert all(b - a >= 250 * 15 for a, b in chunks)


def test_bss_cca_removes_white_muscle_source():
    mne = pytest.importorskip("mne")
    from nh.preprocess import bss_cca_muscle
    sf, n = 250.0, 250 * 60
    rng = np.random.default_rng(3)
    t = np.arange(n) / sf
    brain = np.stack([np.sin(2 * np.pi * 10 * t + k) for k in range(8)])
    brain += np.cumsum(rng.standard_normal((8, n)), axis=1) * 0.01
    emg = rng.standard_normal(n) * 2.0
    mix = rng.standard_normal(8)
    X = (brain + np.outer(mix, emg)) * 1e-5
    raw = mne.io.RawArray(X, mne.create_info(8, sf, "eeg"), verbose=False)
    before = np.mean(np.abs(np.fft.rfft(raw.get_data(), axis=1))[:, 60 * 60:] ** 2)
    info = bss_cca_muscle(raw, slope_thr=-0.5, band=(15.0, 90.0))
    after = np.mean(np.abs(np.fft.rfft(raw.get_data(), axis=1))[:, 60 * 60:] ** 2)
    assert info["n_removed"] >= 1 and after < 0.5 * before


def test_classifier_auto_candidates_and_score_positive():
    from sklearn.datasets import make_classification
    from nh.predict import classifier, score_positive
    X, y = make_classification(80, 6, n_informative=3, random_state=0)
    m = classifier([0.1, 1.0], 3, 0, candidates=["lr_l2", "linear_svm"]).fit(X, y)
    s = score_positive(m, X)
    assert s.shape == (80,) and np.isfinite(s).all()


def test_selection_and_ablation_scripts_never_touch_labels():
    banned = {"open_labels", "labels", "participants", "group", "mmse"}
    for f in ["10_run_ablations.py", "11_select_methods.py"]:
        tree = ast.parse((ROOT / "scripts" / f).read_text())
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | \
                {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)} | \
                {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
        strs = {n.value.lower() for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        assert not (names & banned), f
        assert not any("participants.tsv" in s for s in strs), f


def test_spec_curve_joint_null_is_calibrated():
    """Under H0 (no group effect in any spec), the joint median-t test should rarely reject."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("sc", ROOT / "scripts" / "12_specification_curve.py")
    sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
    rng = np.random.default_rng(4)
    rejections = 0
    for rep in range(40):
        n = 60; g = np.r_[np.ones(30), np.zeros(30)]
        Z = np.column_stack([np.ones(n), rng.normal(size=n)])
        base = rng.normal(size=n)
        Y = np.column_stack([base + 0.5 * rng.normal(size=n) for _ in range(8)])   # correlated specs
        t_obs = np.median([sc.tstat(Y[:, j], g, Z) for j in range(8)])
        null = [np.median([sc.tstat(Y[:, j], gp, Z) for j in range(8)])
                for gp in (rng.permutation(g) for _ in range(199))]
        p = (np.sum(np.abs(null) >= abs(t_obs)) + 1) / 200
        rejections += p < 0.05
    assert rejections <= 6                                   # ~5% expected; generous bound for 40 reps


def test_if_estimators_scale_invariant():
    """SST and VMD must give the same IF/amplitude shape on EEG in volts as on unit-scale data
    (regression: ssqueezepy's absolute threshold and vmdpy's absolute tolerance zeroed them at 1e-6 V)."""
    import numpy as np
    from nh.config import load_config
    from nh import gamma
    cf = load_config()["features"]
    sf, band = 250.0, cf["gamma_band"]
    rng = np.random.default_rng(3)
    t = np.arange(int(4 * sf)) / sf
    x = np.sin(2 * np.pi * (38 * t + 0.3 * np.cumsum(rng.standard_normal(len(t))) / sf)) \
        + 0.5 * rng.standard_normal(len(t))
    for name in ("sst", "vmd"):
        f1, A1, _ = gamma.ESTIMATORS[name](x, sf, band, cf)
        f2, A2, _ = gamma.ESTIMATORS[name](x * 1e-6, sf, band, cf)
        assert np.mean(A2 == 0) < 0.05, name
        assert band[0] - 3 < np.median(f2) < band[1] + 3, name
        np.testing.assert_allclose(np.median(f1), np.median(f2), atol=0.5, err_msg=name)
        np.testing.assert_allclose(A2 / 1e-6, A1, rtol=1e-3, atol=1e-6 * np.median(A1), err_msg=name)


def test_every_ablation_option_is_the_base_or_sets_its_value():
    """With the FINAL settings in the base config, an option with [] must equal the base setting,
    otherwise e.g. 'reference-average' would silently run CSD."""
    from nh.config import apply_overrides
    cfg = load_config()
    paths = {"reference": "preprocessing.reference", "muscle": "preprocessing.muscle.method",
             "epochs": "preprocessing.epochs.method", "median": "features.if_median.mode",
             "estimator": "features.if_estimator", "aperiodic": "features.spectral.aperiodic_method"}
    for dim, path in paths.items():
        for opt, ov in cfg["ablations"]["stage_a"][dim].items():
            c = apply_overrides(cfg, ov)
            for k in path.split("."):
                c = c[k]
            assert str(c) == opt, (dim, opt, c)


def test_ds004504_never_picks_up_ds006036(tmp_path):
    """Same subject IDs in both datasets: files and participants.tsv of ds006036 sitting under the same
    data root must be invisible to the ds004504 adapter (and vice versa)."""
    from nh.datasets import get_adapter
    for ds, sub in [("ds004504-download", "sub-001_task-eyesclosed_eeg.set"),
                    ("ds006036-download", "sub-001_task-eyesclosed_eeg.set")]:
        d = tmp_path / ds / "sub-001" / "eeg"; d.mkdir(parents=True)
        (d / sub).write_bytes(b"x")
        (tmp_path / ds / "participants.tsv").write_text(f"participant_id\tGroup\nsub-001\t{'A' if '4504' in ds else 'C'}\n")
    a = get_adapter("ds004504", roots=[str(tmp_path)])
    rel = lambda ps: [str(Path(p).relative_to(tmp_path)) for p in ps]     # tmp_path itself contains 'ds004504'
    paths = rel(a.find_recordings().path.tolist())
    assert paths and all("ds006036" not in p for p in paths)
    assert a.read_participants().group.tolist() == ["AD"]
    b = get_adapter("ds006036", roots=[str(tmp_path)])
    pb = rel(b.find_recordings().path.tolist())
    assert pb and all("ds004504" not in p for p in pb)


def test_ds006036_condition_mask_keeps_only_eyes_closed_flicker_free():
    """ds006036 marks flicker and eye state with ZERO-duration events; the mask must turn them into
    intervals (a regex on zero-duration markers drops nothing)."""
    import numpy as np
    from nh.datasets import condition_keep_intervals, get_adapter
    cm = get_adapter("ds006036").condition_mask
    on, de = [0.5], ["closed eyes"]
    on += list(np.arange(20.0, 30.0, 0.2)); de += ["Photo/HV mark"] * 50          # flicker 20-30 s
    on += [24.0, 27.0]; de += ["open eyes", "closed eyes"]                            # eyes open inside flicker
    on += [60.0, 65.0]; de += ["open eyes", "closed eyes"]                            # eyes open, no flicker
    keep = condition_keep_intervals(on, de, 100.0, cm)
    inside = lambda t: any(a <= t < b for a, b in keep)
    assert inside(10) and inside(45) and inside(80)                 # eyes closed, no flicker
    assert not inside(25) and not inside(30.5) and not inside(19.7)  # flicker block + padding
    assert not inside(62) and not inside(0.2)                        # eyes open / unknown state before first event
    total = sum(b - a for a, b in keep)
    assert 75 < total < 85            # 99.5 s closed - 1 s pad - 11.3 s flicker - 7 s open
