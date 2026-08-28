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

from pcc_ebid_regulator.regulators import (
    OracleFixedActionTopologyRegulator,
    matched_directional_repertoire,
    mean_repertoire_norm,
)


def test_matched_repertoires_match_cardinality_and_mean_norm():
    one = matched_directional_repertoire((1,), cardinality=9, max_action=0.12)
    target = mean_repertoire_norm(one)
    two = matched_directional_repertoire(
        (0, 2), cardinality=9, max_action=0.12, target_mean_norm=target
    )
    assert len(one) == len(two) == 9
    assert np.isclose(mean_repertoire_norm(one), mean_repertoire_norm(two))


def test_matched_two_channel_set_uses_both_channels():
    actions = matched_directional_repertoire((0, 2), cardinality=9, max_action=0.12)
    assert any(abs(action[0]) > 1e-12 for action in actions)
    assert any(abs(action[2]) > 1e-12 for action in actions)
    assert all(abs(action[1]) < 1e-12 for action in actions)


def test_fixed_action_regulator_runs():
    actions = matched_directional_repertoire((0, 2), cardinality=5, max_action=0.12)
    regulator = OracleFixedActionTopologyRegulator(actions=actions)
    out = simulate_multichannel_topology_regulation(
        regulator,
        topology_schedule=["canonical"] * 5 + ["reverse"] * 5,
        burn_in=5,
    )
    assert out["mean_error"] >= 0.0
