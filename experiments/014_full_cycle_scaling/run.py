"""Experiment 014: full-cycle scaling of frozen canonical EBID.

Tests whether canonical EBID's OOD predictive value becomes reliable when the
observation window covers a substantial fraction of the intrinsic PCC cycle.
Observation lengths are defined from independently estimated noise-free cycle
periods; EBID itself is unchanged.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.dynamics import step, simulate
from pcc_ebid_regulator.ebid import canonical_ebid_features, quadratic_rate_features
from pcc_ebid_regulator.metrics import regulation_error
from pcc_ebid_regulator.regulators import (
    OracleFixedActionTopologyRegulator,
    apply_multichannel_action,
    matched_directional_repertoire,
)
from pcc_ebid_regulator.signals import pcc_interaction_activity, simplex_phase
from pcc_ebid_regulator.stochastic import perturb_simplex
from pcc_ebid_regulator.timescale import phase_cycle_period

OUT = ROOT / "results" / "014_full_cycle_scaling"
OUT.mkdir(parents=True, exist_ok=True)
TARGET = np.ones(3) / 3.0
TOPOLOGIES = ["canonical", "reverse", "no_pressure_control", "no_control_chaos"]
STRENGTHS = [0.5, 1.0, 2.0, 3.0]
TRAIN_NOISE = [0.0, 0.002, 0.005]
TEST_NOISE = [0.01, 0.02]
CYCLE_RATIOS = [0.10, 0.25, 0.50, 0.75, 1.00, 1.50]
HORIZON = 40
REPLICATES = 2
K = 9
MAX_ACTION = 0.12
SEED = 20260828

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
ACTIVITY_KEYS = [
    "activity_initial", "activity_mean", "activity_end", "activity_max",
    "activity_slope",
]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def slope(values) -> float:
    a = np.asarray(values, dtype=float)
    return float(np.polyfit(np.arange(len(a)), a, 1)[0]) if len(a) > 1 else 0.0


def activity_features(values) -> dict[str, float]:
    a = np.asarray(values, dtype=float)
    return {
        "activity_initial": float(a[0]),
        "activity_mean": float(a.mean()),
        "activity_end": float(a[-1]),
        "activity_max": float(a.max()),
        "activity_slope": slope(a),
    }


def reference_periods() -> list[dict]:
    rng = np.random.default_rng(SEED + 14)
    rows = []
    for strength in STRENGTHS:
        periods = []
        for _ in range(12):
            initial = rng.dirichlet(np.array([1.4, 1.4, 1.4]))
            trajectory = simulate(initial, 2400, strength=strength, topology="canonical")
            period = phase_cycle_period(trajectory, min_turns=0.75)
            if np.isfinite(period):
                periods.append(period)
        rows.append({
            "strength": strength,
            "median_cycle_period": float(np.median(periods)),
            "n_reference": len(periods),
        })
    return rows


def observation_steps(period: float, ratio: float) -> int:
    """Map a pre-specified cycle fraction to an integer observation length."""
    return max(5, int(round(float(period) * float(ratio))))


def stochastic_step(x, strength, topology, sigma, rng):
    return perturb_simplex(step(x, strength=strength, topology=topology), sigma, rng)


def observe(initial, strength, topology, sigma, rng, n):
    x = initial.copy()
    trajectory = [x.copy()]
    activity = []
    for t in range(n + 1):
        activity.append(pcc_interaction_activity(x, strength=strength, topology=topology))
        if t < n:
            x = stochastic_step(x, strength, topology, sigma, rng)
            trajectory.append(x.copy())
    return x, np.asarray(trajectory), activity_features(activity)


def future_error(state, strength, topology, sigma, seed):
    rng = np.random.default_rng(seed)
    actions = matched_directional_repertoire((1,), cardinality=K, max_action=MAX_ACTION)
    regulator = OracleFixedActionTopologyRegulator(actions=actions, model_strength=strength)
    x = state.copy()
    errors = []
    for _ in range(HORIZON):
        action = regulator.choose_topology(x, TARGET, topology)
        x = apply_multichannel_action(x, action)
        x = stochastic_step(x, strength, topology, sigma, rng)
        errors.append(regulation_error(x, TARGET))
    return float(np.mean(errors))


def build_dataset(period_map):
    master = np.random.default_rng(SEED)
    rows = []
    sample = 0
    for ratio in CYCLE_RATIOS:
        for si, topology in enumerate(TOPOLOGIES):
            for strength in STRENGTHS:
                obs = observation_steps(period_map[strength], ratio)
                actual_ratio = obs / period_map[strength]
                for sigma in TRAIN_NOISE + TEST_NOISE:
                    for rep in range(REPLICATES):
                        initial = master.dirichlet(np.array([1.4, 1.4, 1.4]))
                        obs_seed = int(master.integers(0, 2**31 - 1))
                        fut_seed = int(master.integers(0, 2**31 - 1))
                        end, trajectory, activity = observe(
                            initial, strength, topology, sigma,
                            np.random.default_rng(obs_seed), obs,
                        )
                        row = {
                            "sample": sample,
                            "structure_index": si,
                            "structure": topology,
                            "strength": strength,
                            "noise_sigma": sigma,
                            "replicate": rep,
                            "target_cycle_ratio": ratio,
                            "observation_steps": obs,
                            "reference_cycle_period": period_map[strength],
                            "obs_cycle_ratio": actual_ratio,
                            "P": float(end[0]), "C": float(end[1]), "Ch": float(end[2]),
                            "imbalance": regulation_error(end, TARGET),
                            "phase": simplex_phase(end),
                            **activity,
                            **quadratic_rate_features(trajectory),
                            **canonical_ebid_features(trajectory),
                            "future_horizon": HORIZON,
                            "future_error": future_error(end, strength, topology, sigma, fut_seed),
                        }
                        rows.append(row)
                        sample += 1
    return rows


def col(rows, key):
    return np.asarray([float(r[key]) for r in rows], dtype=float)


def design(rows, include_ebid):
    P, C, S = col(rows, "P"), col(rows, "C"), col(rows, "strength")
    R = col(rows, "obs_cycle_ratio")
    L = np.log1p(col(rows, "observation_steps"))
    phase = col(rows, "phase")
    cols = [
        P, C, S, R, L,
        P*P, C*C, S*S, R*R, L*L,
        P*C, P*S, C*S, S*R,
        *[col(rows, k) for k in ACTIVITY_KEYS],
        np.sin(phase), np.cos(phase),
        *[col(rows, k) for k in QUAD_KEYS],
    ]
    if include_ebid:
        cols += [col(rows, k) for k in EBID_KEYS]
    return np.column_stack([np.ones(len(rows)), *cols])


def fit_predict(train, test, include_ebid):
    beta = np.linalg.lstsq(
        design(train, include_ebid), col(train, "future_error"), rcond=None
    )[0]
    return design(test, include_ebid) @ beta


def relative_mae(y, base_pred, ebid_pred):
    base = float(np.mean(np.abs(y - base_pred)))
    ebid = float(np.mean(np.abs(y - ebid_pred)))
    return (base - ebid) / base, base, ebid


def bootstrap_relative_gain(y, p0, p1, seed, n_boot=1000):
    rng = np.random.default_rng(seed)
    n = len(y)
    gains = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        b = float(np.mean(np.abs(y[idx] - p0[idx])))
        e = float(np.mean(np.abs(y[idx] - p1[idx])))
        if b > 1e-12:
            gains.append((b - e) / b)
    return float(np.quantile(gains, 0.025)), float(np.quantile(gains, 0.975))


def evaluate_global(rows):
    train = [
        r for r in rows
        if int(r["structure_index"]) != 0 and float(r["noise_sigma"]) in TRAIN_NOISE
    ]
    out = []
    for ratio in CYCLE_RATIOS:
        test = [
            r for r in rows
            if int(r["structure_index"]) == 0
            and float(r["noise_sigma"]) in TEST_NOISE
            and abs(float(r["target_cycle_ratio"]) - ratio) < 1e-12
        ]
        y = col(test, "future_error")
        p0 = fit_predict(train, test, False)
        p1 = fit_predict(train, test, True)
        gain, b, e = relative_mae(y, p0, p1)
        lo, hi = bootstrap_relative_gain(y, p0, p1, SEED + int(ratio * 1000))
        out.append({
            "target_cycle_ratio": ratio,
            "mean_actual_cycle_ratio": float(np.mean(col(test, "obs_cycle_ratio"))),
            "min_observation_steps": int(np.min(col(test, "observation_steps"))),
            "max_observation_steps": int(np.max(col(test, "observation_steps"))),
            "n_train": len(train),
            "n_test": len(test),
            "base_mae": b,
            "ebid_mae": e,
            "relative_mae_reduction": gain,
            "bootstrap_ci_low": lo,
            "bootstrap_ci_high": hi,
            "ebid_better": int(gain > 0),
            "ci_strictly_positive": int(lo > 0),
        })
    return out



def evaluate_per_ratio(rows):
    """Fit each cycle fraction separately to test local sufficiency.

    This prevents long-window cases from calibrating the EBID readout for
    short-window test cases. It is the primary threshold analysis.
    """
    out = []
    for ratio in CYCLE_RATIOS:
        train = [
            r for r in rows
            if int(r["structure_index"]) != 0
            and float(r["noise_sigma"]) in TRAIN_NOISE
            and abs(float(r["target_cycle_ratio"]) - ratio) < 1e-12
        ]
        test = [
            r for r in rows
            if int(r["structure_index"]) == 0
            and float(r["noise_sigma"]) in TEST_NOISE
            and abs(float(r["target_cycle_ratio"]) - ratio) < 1e-12
        ]
        y = col(test, "future_error")
        p0 = fit_predict(train, test, False)
        p1 = fit_predict(train, test, True)
        gain, b, e = relative_mae(y, p0, p1)
        lo, hi = bootstrap_relative_gain(y, p0, p1, SEED + 9000 + int(ratio * 1000), n_boot=2000)
        out.append({
            "target_cycle_ratio": ratio,
            "mean_actual_cycle_ratio": float(np.mean(col(test, "obs_cycle_ratio"))),
            "min_observation_steps": int(np.min(col(test, "observation_steps"))),
            "max_observation_steps": int(np.max(col(test, "observation_steps"))),
            "n_train": len(train),
            "n_test": len(test),
            "base_mae": b,
            "ebid_mae": e,
            "relative_mae_reduction": gain,
            "bootstrap_ci_low": lo,
            "bootstrap_ci_high": hi,
            "ebid_better": int(gain > 0),
            "ci_strictly_positive": int(lo > 0),
        })
    return out

def main():
    refs = reference_periods()
    write_csv(OUT / "reference_periods.csv", refs)
    period_map = {float(r["strength"]): float(r["median_cycle_period"]) for r in refs}
    rows = build_dataset(period_map)
    write_csv(OUT / "dataset.csv", rows)
    global_summary = evaluate_global(rows)
    write_csv(OUT / "global_summary.csv", global_summary)
    summary = evaluate_per_ratio(rows)
    write_csv(OUT / "summary.csv", summary)
    write_csv(OUT / "per_ratio_fit_summary.csv", summary)

    reliable = [r for r in summary if int(r["ci_strictly_positive"]) == 1]
    threshold = reliable[0]["target_cycle_ratio"] if reliable else ""
    write_csv(OUT / "threshold.csv", [{
        "criterion": "first pre-specified cycle ratio with bootstrap CI > 0",
        "first_reliable_cycle_ratio": threshold,
        "n_reliable_ratios": len(reliable),
        "n_tested_ratios": len(summary),
    }])

    print("REFERENCE PERIODS")
    for r in refs: print(r)
    print("\nPER-RATIO FULL-CYCLE SUMMARY")
    for r in summary: print(r)
    print("\nGLOBAL-CALIBRATION SUMMARY")
    for r in global_summary: print(r)
    print("\nFIRST RELIABLE RATIO", threshold)

if __name__ == "__main__":
    main()
