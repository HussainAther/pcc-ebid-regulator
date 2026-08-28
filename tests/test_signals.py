import numpy as np

from pcc_ebid_regulator.signals import benchmark_activity, pcc_interaction_activity, simplex_phase


def test_pcc_activity_zero_at_center():
    assert pcc_interaction_activity(np.ones(3) / 3.0) < 1e-12


def test_activity_nonnegative():
    x = np.array([0.6, 0.25, 0.15])
    assert pcc_interaction_activity(x, strength=1.5) >= 0
    assert benchmark_activity(x, strength=1.5) >= 0


def test_simplex_phase_finite():
    assert np.isfinite(simplex_phase(np.array([0.6, 0.25, 0.15])))
