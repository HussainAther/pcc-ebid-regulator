import numpy as np

from pcc_ebid_regulator.drift import random_walk_strength_schedule, sinusoidal_strength_schedule
from pcc_ebid_regulator.experiments import simulate_dynamic_regulation
from pcc_ebid_regulator.regulators import OracleDynamicRegulator


def test_sinusoidal_schedule_has_expected_bounds():
    x = sinusoidal_strength_schedule(1000, base_strength=1.5, amplitude=0.5, period=100)
    assert np.isclose(x.min(), 1.0, atol=1e-6)
    assert np.isclose(x.max(), 2.0, atol=1e-6)


def test_random_walk_is_reproducible():
    a = random_walk_strength_schedule(100, seed=7)
    b = random_walk_strength_schedule(100, seed=7)
    assert np.allclose(a, b)


def test_dynamic_simulation_runs():
    schedule = sinusoidal_strength_schedule(100, amplitude=0.2)
    result = simulate_dynamic_regulation(
        OracleDynamicRegulator(variety=5),
        strength_schedule=schedule,
        burn_in=20,
    )
    assert result["mean_error"] >= 0.0
    assert result["strength_std"] > 0.0
