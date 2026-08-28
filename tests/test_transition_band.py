from pathlib import Path
import importlib.util

RUN = Path(__file__).resolve().parents[1] / "experiments" / "015_transition_band" / "run.py"
spec = importlib.util.spec_from_file_location("exp015_run", RUN)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_transition_grid_is_dense_and_prespecified():
    assert mod.CYCLE_RATIOS == [0.40,0.50,0.60,0.70,0.80,0.90,1.00,1.10,1.20]


def test_observation_steps_uses_cycle_fraction():
    assert mod.observation_steps(200.0, 0.4) == 80
    assert mod.observation_steps(200.0, 1.2) == 240
