import numpy as np
import pytest

from pcc_ebid_regulator.dynamics import step
from pcc_ebid_regulator.topology import cyclic_topology_schedule, topology_matrix


def test_canonical_topology_matches_original_equations():
    state = np.array([0.58, 0.27, 0.15], dtype=float)
    strength = 1.7
    dt = 0.02
    p, c, ch = state
    expected = np.array([
        p + dt * strength * p * (ch - c),
        c + dt * strength * c * (p - ch),
        ch + dt * strength * ch * (c - p),
    ])
    expected = np.clip(expected, 1e-12, None)
    expected /= expected.sum()
    assert np.allclose(step(state, dt=dt, strength=strength), expected)


def test_topology_schedule_cycles_by_dwell():
    schedule = cyclic_topology_schedule(7, ["canonical", "reverse"], dwell=2)
    assert schedule == [
        "canonical", "canonical", "reverse", "reverse",
        "canonical", "canonical", "reverse",
    ]


def test_unknown_topology_is_rejected():
    with pytest.raises(ValueError):
        topology_matrix("not-a-topology")


def test_topology_regulation_counts_switches():
    from pcc_ebid_regulator.experiments import simulate_topology_regulation
    from pcc_ebid_regulator.regulators import OracleTopologyRegulator

    schedule = ["canonical"] * 3 + ["reverse"] * 3
    out = simulate_topology_regulation(
        OracleTopologyRegulator(variety=3),
        topology_schedule=schedule,
        burn_in=3,
    )
    assert out["switches"] == 1.0
    assert out["mean_error"] >= 0.0
