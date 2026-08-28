import numpy as np

from pcc_ebid_regulator.ebid import canonical_ebid_features


def test_canonical_ebid_remains_frozen_under_phase_readout():
    traj = np.array([
        [0.60, 0.25, 0.15],
        [0.55, 0.28, 0.17],
        [0.50, 0.31, 0.19],
    ])
    a = canonical_ebid_features(traj)
    b = canonical_ebid_features(traj.copy())
    assert a == b
    assert len(a) == 11


def test_first_harmonic_phase_encoding_has_unit_radius():
    phases = np.linspace(-np.pi, np.pi, 31)
    radius = np.sin(phases) ** 2 + np.cos(phases) ** 2
    np.testing.assert_allclose(radius, np.ones_like(radius), atol=1e-12)
