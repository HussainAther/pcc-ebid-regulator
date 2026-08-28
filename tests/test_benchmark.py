import numpy as np
import pytest

from pcc_ebid_regulator.benchmark import (
    benchmark_step,
    cyclic_benchmark_schedule,
)
from pcc_ebid_regulator.experiments import simulate_multichannel_benchmark_regulation
from pcc_ebid_regulator.regulators import (
    OracleFixedActionBenchmarkRegulator,
    matched_directional_repertoire,
)


def test_benchmark_step_preserves_simplex():
    out = benchmark_step(np.array([0.58, 0.27, 0.15]), regime="pressure_bias")
    assert np.all(out > 0)
    assert np.isclose(out.sum(), 1.0)


def test_unknown_benchmark_regime_rejected():
    with pytest.raises(ValueError):
        benchmark_step(np.array([0.4, 0.3, 0.3]), regime="cyclic_magic")


def test_benchmark_schedule_switches():
    schedule = cyclic_benchmark_schedule(8, ["pressure_bias", "control_bias"], dwell=2)
    assert schedule[:4] == ["pressure_bias", "pressure_bias", "control_bias", "control_bias"]


def test_benchmark_regulation_runs():
    actions = matched_directional_repertoire((0, 1), cardinality=5, max_action=0.12)
    regulator = OracleFixedActionBenchmarkRegulator(actions=actions)
    out = simulate_multichannel_benchmark_regulation(
        regulator,
        regime_schedule=["pressure_bias"] * 5 + ["control_bias"] * 5,
        burn_in=5,
    )
    assert out["mean_error"] >= 0.0
    assert out["switches"] == 1.0
