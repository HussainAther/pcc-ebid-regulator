import numpy as np
from pcc_ebid_regulator.dynamics import simulate
from pcc_ebid_regulator.timescale import phase_cycle_period


def test_phase_cycle_period_is_finite_for_long_canonical_cycle():
    tr = simulate(np.array([0.60, 0.25, 0.15]), 1800, strength=2.0, topology="canonical")
    p = phase_cycle_period(tr)
    assert np.isfinite(p)
    assert p > 50


def test_phase_cycle_period_rejects_too_short_arc():
    tr = simulate(np.array([0.60, 0.25, 0.15]), 5, strength=1.0, topology="canonical")
    assert np.isnan(phase_cycle_period(tr))
