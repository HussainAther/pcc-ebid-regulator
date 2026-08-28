import numpy as np

from pcc_ebid_regulator.ebid import canonical_ebid_features, quadratic_rate_features


def test_canonical_ebid_equilibrium_is_constant_max_entropy():
    traj = np.tile(np.ones(3) / 3.0, (8, 1))
    f = canonical_ebid_features(traj)
    assert np.isclose(f["ebid_initial_entropy"], np.log(3.0))
    assert np.isclose(f["ebid_entropy_drop"], 0.0, atol=1e-12)
    assert np.isclose(f["ebid_deficit_growth"], 0.0, atol=1e-12)
    assert np.isclose(f["ebid_entropy_rate_variance"], 0.0, atol=1e-12)


def test_canonical_ebid_detects_entropy_loss():
    traj = np.array([
        [1/3, 1/3, 1/3],
        [0.45, 0.30, 0.25],
        [0.60, 0.25, 0.15],
    ])
    f = canonical_ebid_features(traj)
    assert f["ebid_entropy_drop"] > 0
    assert f["ebid_deficit_growth"] > 0
    assert f["ebid_mean_entropy_rate"] < 0
    assert f["ebid_max_deficit_rate"] > 0


def test_quadratic_baseline_detects_departure_from_center():
    traj = np.array([
        [1/3, 1/3, 1/3],
        [0.45, 0.30, 0.25],
        [0.60, 0.25, 0.15],
    ])
    f = quadratic_rate_features(traj)
    assert f["quad_growth"] > 0
    assert f["quad_mean_rate"] > 0
