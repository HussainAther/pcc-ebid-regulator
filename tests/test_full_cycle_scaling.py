from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "014_full_cycle_scaling"))
from run import observation_steps


def test_observation_steps_scales_with_period():
    assert observation_steps(100.0, 0.5) == 50
    assert observation_steps(100.0, 1.5) == 150


def test_observation_steps_has_minimum():
    assert observation_steps(20.0, 0.1) == 5
