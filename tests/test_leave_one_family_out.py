import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "experiments" / "017_leave_one_family_out" / "run.py"
spec = importlib.util.spec_from_file_location("exp017", RUN)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)


def test_locked_ratios_match_experiment_016():
    assert mod.CYCLE_RATIOS == [0.50, 0.60, 0.75, 1.00, 1.10, 1.20]


def test_leave_one_family_out_split_is_disjoint_and_counts_match():
    rows = mod.read_csv(mod.SOURCE)
    train, test = mod.split_for_fold(rows, 0.60, 3)
    assert len(train) == 504  # 7 families * 3 structures * 4 strengths * 3 train noise * 2 reps
    assert len(test) == 16    # 1 family * canonical * 4 strengths * 2 test noise * 2 reps
    assert all(int(r["seed_family"]) != 3 for r in train)
    assert all(int(r["seed_family"]) == 3 for r in test)
    assert all(int(r["structure_index"]) != 0 for r in train)
    assert all(int(r["structure_index"]) == 0 for r in test)
