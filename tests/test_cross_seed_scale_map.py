from pathlib import Path
import importlib.util

RUN = Path(__file__).resolve().parents[1] / 'experiments' / '016_cross_seed_scale_map' / 'run.py'
spec = importlib.util.spec_from_file_location('exp016_run', RUN)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_locked_diagnostic_ratios():
    assert mod.CYCLE_RATIOS == [0.50, 0.60, 0.75, 1.00, 1.10, 1.20]


def test_independent_seed_family_count():
    assert len(mod.FAMILY_SEEDS) == 8
    assert len(set(mod.FAMILY_SEEDS)) == 8


def test_family_ratio_seed_is_deterministic_and_distinct():
    a = mod.family_ratio_seed(0, 0.5)
    b = mod.family_ratio_seed(0, 0.5)
    c = mod.family_ratio_seed(1, 0.5)
    d = mod.family_ratio_seed(0, 0.6)
    assert a == b
    assert len({a, c, d}) == 3
