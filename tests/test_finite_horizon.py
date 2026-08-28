import numpy as np
from pcc_ebid_regulator.dynamics import simulate, step
from pcc_ebid_regulator.finite_horizon import finite_horizon_invariants


def test_finite_horizon_invariants_are_finite_and_positive():
    tr = simulate(np.array([0.55,0.30,0.15]), 80, strength=1.5)
    f = finite_horizon_invariants(tr, lambda x,t: step(x,strength=1.5))
    assert len(f) == 10
    assert all(np.isfinite(v) for v in f.values())
    assert f['fh_memory_amplification_h5'] > 0
    assert f['fh_action_spread_h20'] > 0


def test_identity_transition_preserves_perturbation_memory():
    tr = np.tile(np.array([0.4,0.35,0.25]), (30,1))
    f = finite_horizon_invariants(tr, lambda x,t: x)
    assert abs(f['fh_memory_amplification_h5'] - 1.0) < 1e-6
    assert abs(f['fh_memory_amplification_h20'] - 1.0) < 1e-6
    assert abs(f['fh_memory_persistence_ratio'] - 1.0) < 1e-6
