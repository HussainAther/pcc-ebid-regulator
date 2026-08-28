import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.metrics import entropy_deficit, normalized_entropy, regulation_error


def test_uniform_state_has_max_entropy():
    x = np.full(3, 1 / 3)
    assert np.isclose(normalized_entropy(x), 1.0)
    assert np.isclose(entropy_deficit(x), 0.0)


def test_uniform_state_has_zero_regulation_error():
    x = np.full(3, 1 / 3)
    assert np.isclose(regulation_error(x), 0.0)
