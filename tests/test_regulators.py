import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.regulators import action_repertoire, apply_control_action


def test_action_repertoire_has_requested_variety():
    assert len(action_repertoire(9)) == 9
    assert np.allclose(action_repertoire(1), [0.0])


def test_control_action_preserves_simplex():
    x = np.array([0.5, 0.3, 0.2])
    for action in (-0.03, 0.0, 0.03):
        y = apply_control_action(x, action)
        assert np.isclose(y.sum(), 1.0)
        assert np.all(y > 0)
