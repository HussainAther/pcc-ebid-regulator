"""Experiment 009: canonical EBID incremental predictive value.

Freeze the parent PCC/EBID entropy-rate feature family, observe a short
uncontrolled trajectory, then ask whether those features improve held-out
prediction of subsequent regulator difficulty after geometry, generic dynamic
activity, phase/structure, and a matched quadratic-distance trajectory baseline.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.benchmark import benchmark_step
from pcc_ebid_regulator.dynamics import step
from pcc_ebid_regulator.ebid import canonical_ebid_features, quadratic_rate_features
from pcc_ebid_regulator.metrics import regulation_error
from pcc_ebid_regulator.regulators import (
    OracleFixedActionBenchmarkRegulator,
    OracleFixedActionTopologyRegulator,
    apply_multichannel_action,
    matched_directional_repertoire,
)
from pcc_ebid_regulator.signals import benchmark_activity, pcc_interaction_activity, simplex_phase

OUT = ROOT / "results" / "009_canonical_ebid"
OUT.mkdir(parents=True, exist_ok=True)
TARGET = np.ones(3) / 3.0
TOPOLOGIES = ["canonical", "reverse", "no_pressure_control", "no_control_chaos"]
REGIMES = ["pressure_bias", "control_bias", "chaos_bias", "mixed_bias"]
STRENGTHS = [0.5, 1.0, 1.5, 2.0, 3.0]
OBSERVATION_STEPS = 25
FUTURE_HORIZON = 50
K = 9
MAX_ACTION = 0.12
SEED = 20260828
N_SAMPLES = 320

EBID_KEYS = [
    "ebid_initial_entropy", "ebid_mean_entropy", "ebid_end_entropy",
    "ebid_entropy_drop", "ebid_entropy_slope", "ebid_mean_entropy_rate",
    "ebid_min_entropy_rate", "ebid_entropy_rate_variance",
    "ebid_deficit_growth", "ebid_max_deficit_rate",
    "ebid_deficit_rate_variance",
]
QUAD_KEYS = [
    "quad_initial", "quad_mean", "quad_end", "quad_growth", "quad_slope",
    "quad_mean_rate", "quad_min_rate", "quad_max_rate", "quad_rate_variance",
]
ACTIVITY_KEYS = ["activity_initial", "activity_mean", "activity_end", "activity_max", "activity_slope"]


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def slope(values: np.ndarray) -> float:
    t = np.arange(len(values), dtype=float)
    return float(np.polyfit(t, np.asarray(values, dtype=float), 1)[0]) if len(values) > 1 else 0.0


def activity_features(values: list[float]) -> dict[str, float]:
    a = np.asarray(values, dtype=float)
    return {
        "activity_initial": float(a[0]),
        "activity_mean": float(np.mean(a)),
        "activity_end": float(a[-1]),
        "activity_max": float(np.max(a)),
        "activity_slope": slope(a),
    }


def observe_pcc(state: np.ndarray, strength: float, topology: str) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    x = state.copy()
    trajectory = [x.copy()]
    activity = [pcc_interaction_activity(x, strength=strength, topology=topology)]
    for _ in range(OBSERVATION_STEPS):
        x = step(x, strength=strength, topology=topology)
        trajectory.append(x.copy())
        activity.append(pcc_interaction_activity(x, strength=strength, topology=topology))
    return x, np.asarray(trajectory), activity_features(activity)


def observe_benchmark(state: np.ndarray, strength: float, regime: str) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    x = state.copy()
    trajectory = [x.copy()]
    activity = [benchmark_activity(x, strength=strength, regime=regime)]
    for _ in range(OBSERVATION_STEPS):
        x = benchmark_step(x, strength=strength, regime=regime)
        trajectory.append(x.copy())
        activity.append(benchmark_activity(x, strength=strength, regime=regime))
    return x, np.asarray(trajectory), activity_features(activity)


def future_pcc_error(state: np.ndarray, strength: float, topology: str) -> float:
    actions = matched_directional_repertoire((1,), cardinality=K, max_action=MAX_ACTION)
    reg = OracleFixedActionTopologyRegulator(actions=actions, model_strength=strength)
    x = state.copy()
    errors = []
    for _ in range(FUTURE_HORIZON):
        action = reg.choose_topology(x, TARGET, topology)
        x = step(apply_multichannel_action(x, action), strength=strength, topology=topology)
        errors.append(regulation_error(x, TARGET))
    return float(np.mean(errors))


def future_benchmark_error(state: np.ndarray, strength: float, regime: str) -> float:
    actions = matched_directional_repertoire((1,), cardinality=K, max_action=MAX_ACTION)
    reg = OracleFixedActionBenchmarkRegulator(actions=actions, model_strength=strength)
    x = state.copy()
    errors = []
    for _ in range(FUTURE_HORIZON):
        action = reg.choose_regime(x, TARGET, regime)
        x = benchmark_step(apply_multichannel_action(x, action), strength=strength, regime=regime)
        errors.append(regulation_error(x, TARGET))
    return float(np.mean(errors))


def row_from_observation(sample: int, system: str, structure: str, strength: float,
                         endpoint: np.ndarray, trajectory: np.ndarray,
                         activity: dict[str, float], future_error: float) -> dict:
    row = {
        "sample": sample,
        "system": system,
        "structure": structure,
        "strength": strength,
        "P": float(endpoint[0]),
        "C": float(endpoint[1]),
        "Ch": float(endpoint[2]),
        "imbalance": regulation_error(endpoint, TARGET),
        "phase": simplex_phase(endpoint),
        **activity,
        **quadratic_rate_features(trajectory),
        **canonical_ebid_features(trajectory),
        "future_error": future_error,
    }
    return row


def build_dataset(n: int = N_SAMPLES) -> list[dict]:
    rng = np.random.default_rng(SEED)
    initial_states = rng.dirichlet(np.array([1.4, 1.4, 1.4]), size=n)
    rows: list[dict] = []
    for i, initial in enumerate(initial_states):
        strength = float(STRENGTHS[i % len(STRENGTHS)])
        structure_index = (i // len(STRENGTHS)) % 4
        topology = TOPOLOGIES[structure_index]
        regime = REGIMES[structure_index]

        p_end, p_traj, p_activity = observe_pcc(initial, strength, topology)
        b_end, b_traj, b_activity = observe_benchmark(initial, strength, regime)
        rows.append(row_from_observation(
            i, "pcc", topology, strength, p_end, p_traj, p_activity,
            future_pcc_error(p_end, strength, topology),
        ))
        rows.append(row_from_observation(
            i, "benchmark", regime, strength, b_end, b_traj, b_activity,
            future_benchmark_error(b_end, strength, regime),
        ))
    return rows


def numeric_column(rows: list[dict], name: str) -> np.ndarray:
    return np.asarray([float(row[name]) for row in rows], dtype=float)


def design(rows: list[dict], spec: str) -> np.ndarray:
    cols: list[np.ndarray] = []
    P, C, S = numeric_column(rows, "P"), numeric_column(rows, "C"), numeric_column(rows, "strength")
    cols += [P, C, S, P * P, C * C, S * S, P * C, P * S, C * S]

    if "+activity" in spec:
        cols += [numeric_column(rows, key) for key in ACTIVITY_KEYS]

    if "+phase_structure" in spec:
        phase = numeric_column(rows, "phase")
        cols += [np.sin(phase), np.cos(phase)]
        structures = sorted({str(row["structure"]) for row in rows})
        for structure in structures[1:]:
            cols.append(np.asarray([1.0 if row["structure"] == structure else 0.0 for row in rows]))

    if "+quadratic" in spec:
        cols += [numeric_column(rows, key) for key in QUAD_KEYS]

    if "+ebid" in spec:
        cols += [numeric_column(rows, key) for key in EBID_KEYS]

    return np.column_stack([np.ones(len(rows)), *cols])


def cv_predictions(rows: list[dict], spec: str, folds: int = 8, fold_labels: np.ndarray | None = None) -> np.ndarray:
    y = numeric_column(rows, "future_error")
    predictions = np.empty_like(y)
    sample_ids = np.asarray([int(row["sample"]) for row in rows])
    labels = (sample_ids % folds) if fold_labels is None else np.asarray(fold_labels, dtype=int)
    for fold in range(folds):
        test = labels == fold
        train = ~test
        train_rows = [row for j, row in enumerate(rows) if train[j]]
        test_rows = [row for j, row in enumerate(rows) if test[j]]
        X_train = design(train_rows, spec)
        X_test = design(test_rows, spec)
        beta = np.linalg.lstsq(X_train, y[train], rcond=None)[0]
        predictions[test] = X_test @ beta
    return predictions


def score_predictions(rows: list[dict], predictions: np.ndarray) -> tuple[float, float]:
    y = numeric_column(rows, "future_error")
    denominator = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - float(np.sum((y - predictions) ** 2)) / denominator
    mae = float(np.mean(np.abs(y - predictions)))
    return r2, mae


def main() -> None:
    rows = build_dataset()
    write_csv(OUT / "dataset.csv", rows)

    specs = [
        "geometry2",
        "geometry2+activity",
        "geometry2+activity+phase_structure",
        "geometry2+activity+phase_structure+quadratic",
        "geometry2+activity+phase_structure+quadratic+ebid",
    ]
    summaries: list[dict] = []
    for system in ("pcc", "benchmark"):
        sub = [row for row in rows if row["system"] == system]
        print(system.upper())
        for spec in specs:
            pred = cv_predictions(sub, spec)
            r2, mae = score_predictions(sub, pred)
            summaries.append({"system": system, "model": spec, "cv_r2": r2, "cv_mae": mae})
            print(f"  {spec:56s} R2={r2: .4f}  MAE={mae:.5f}")

    write_csv(OUT / "predictive_models.csv", summaries)

    def get(system: str, spec: str, metric: str = "cv_r2") -> float:
        return float(next(row[metric] for row in summaries if row["system"] == system and row["model"] == spec))

    base = "geometry2+activity+phase_structure"
    quad = base + "+quadratic"
    full = quad + "+ebid"
    comparison = []
    for system in ("pcc", "benchmark"):
        comparison.append({
            "system": system,
            "r2_base": get(system, base),
            "r2_plus_quadratic": get(system, quad),
            "r2_plus_ebid": get(system, full),
            "quadratic_increment": get(system, quad) - get(system, base),
            "ebid_increment_beyond_quadratic": get(system, full) - get(system, quad),
            "mae_base": get(system, base, "cv_mae"),
            "mae_plus_quadratic": get(system, quad, "cv_mae"),
            "mae_plus_ebid": get(system, full, "cv_mae"),
        })
    write_csv(OUT / "incremental_value.csv", comparison)

    pcc_gain = next(row["ebid_increment_beyond_quadratic"] for row in comparison if row["system"] == "pcc")
    benchmark_gain = next(row["ebid_increment_beyond_quadratic"] for row in comparison if row["system"] == "benchmark")
    specificity = [{
        "pcc_ebid_increment_beyond_quadratic": pcc_gain,
        "benchmark_ebid_increment_beyond_quadratic": benchmark_gain,
        "pcc_minus_benchmark_increment": pcc_gain - benchmark_gain,
    }]
    write_csv(OUT / "specificity_summary.csv", specificity)

    # Robustness: repeated random sample-level fold assignments, shared between
    # PCC and benchmark. This tests whether the specificity margin depends on
    # the arbitrary deterministic fold partition above.
    repeated_rows = []
    for repeat in range(30):
        rng = np.random.default_rng(SEED + 1000 + repeat)
        shuffled = rng.permutation(N_SAMPLES)
        sample_to_fold = np.empty(N_SAMPLES, dtype=int)
        sample_to_fold[shuffled] = np.arange(N_SAMPLES) % 8
        repeat_gains = {}
        for system in ("pcc", "benchmark"):
            sub = [row for row in rows if row["system"] == system]
            labels = np.asarray([sample_to_fold[int(row["sample"])] for row in sub])
            pred_quad = cv_predictions(sub, quad, fold_labels=labels)
            pred_full = cv_predictions(sub, full, fold_labels=labels)
            r2_quad, _ = score_predictions(sub, pred_quad)
            r2_full, _ = score_predictions(sub, pred_full)
            repeat_gains[system] = r2_full - r2_quad
        repeated_rows.append({
            "repeat": repeat,
            "pcc_ebid_increment": repeat_gains["pcc"],
            "benchmark_ebid_increment": repeat_gains["benchmark"],
            "pcc_minus_benchmark_increment": repeat_gains["pcc"] - repeat_gains["benchmark"],
        })
    write_csv(OUT / "repeated_cv_specificity.csv", repeated_rows)
    margins = np.asarray([row["pcc_minus_benchmark_increment"] for row in repeated_rows], dtype=float)
    robust_summary = [{
        "repeats": len(repeated_rows),
        "median_pcc_minus_benchmark_increment": float(np.median(margins)),
        "min_pcc_minus_benchmark_increment": float(np.min(margins)),
        "max_pcc_minus_benchmark_increment": float(np.max(margins)),
        "positive_margin_fraction": float(np.mean(margins > 0.0)),
    }]
    write_csv(OUT / "robustness_summary.csv", robust_summary)

    print("\nEBID incremental value beyond quadratic trajectory baseline")
    print(f"  PCC:       {pcc_gain:+.4f} CV R2")
    print(f"  benchmark: {benchmark_gain:+.4f} CV R2")
    print(f"  PCC - benchmark: {pcc_gain - benchmark_gain:+.4f}")
    print("Repeated-CV specificity margin")
    print(f"  median: {np.median(margins):+.4f}")
    print(f"  range:  {np.min(margins):+.4f} to {np.max(margins):+.4f}")
    print(f"  positive in {np.mean(margins > 0.0):.1%} of repeats")


if __name__ == "__main__":
    main()
