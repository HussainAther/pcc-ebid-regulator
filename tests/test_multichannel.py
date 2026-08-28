import numpy as np
import pytest

from pcc_ebid_regulator.experiments import simulate_multichannel_topology_regulation
from pcc_ebid_regulator.regulators import (
    OracleMultiChannelTopologyRegulator,
    apply_multichannel_action,
    multichannel_repertoire,
)


def test_multichannel_action_preserves_simplex():
    state = np.array([0.58, 0.27, 0.15])
    out = apply_multichannel_action(state, np.array([0.1, -0.1, 0.0]))
    assert np.all(out > 0.0)
    assert np.isclose(out.sum(), 1.0)


def test_common_action_offset_is_compositionally_redundant():
    state = np.array([0.58, 0.27, 0.15])
    out = apply_multichannel_action(state, np.array([0.2, 0.2, 0.2]))
    assert np.allclose(out, state)


def test_repertoire_size_scales_with_channel_count():
    assert len(multichannel_repertoire((1,))) == 3
    assert len(multichannel_repertoire((0, 1))) == 9
    assert len(multichannel_repertoire((0, 1, 2))) == 27


def test_invalid_channels_rejected():
    with pytest.raises(ValueError):
        multichannel_repertoire(())
    with pytest.raises(ValueError):
        multichannel_repertoire((0, 0))


def test_multichannel_topology_simulation_runs():
    regulator = OracleMultiChannelTopologyRegulator(channels=(0, 1))
    out = simulate_multichannel_topology_regulation(
        regulator,
        topology_schedule=["canonical"] * 5 + ["reverse"] * 5,
        burn_in=5,
    )
    assert out["mean_error"] >= 0.0
    assert out["switches"] == 1.0
