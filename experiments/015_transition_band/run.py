"""Experiment 015: independent replication of the EBID cycle-coverage transition band.

Canonical EBID remains frozen. Observation windows cover 0.4--1.2 intrinsic
canonical-PCC cycles. Each ratio is calibrated independently using a fixed,
standardized ridge readout to reduce small-sample coefficient instability.
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

OUT = ROOT / "results" / "015_transition_band"
OUT.mkdir(parents=True, exist_ok=True)
TARGET = np.ones(3) / 3.0
TOPOLOGIES = ["canonical", "reverse", "no_pressure_control", "no_control_chaos"]
STRENGTHS = [0.5, 1.0, 2.0, 3.0]
TRAIN_NOISE = [0.0, 0.002, 0.005]
TEST_NOISE = [0.01, 0.02]
CYCLE_RATIOS = [0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.10, 1.20]
HORIZON = 40
REPLICATES = 4
K = 9
MAX_ACTION = 0.12
RIDGE_ALPHA = 0.10
SEED = 20260915

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
        w.writeheader(); w.writerows(rows)


def slope(values) -> float:
    a = np.asarray(values, dtype=float)
    return float(np.polyfit(np.arange(len(a)), a, 1)[0]) if len(a) > 1 else 0.0


def activity_features(values) -> dict[str, float]:
    a = np.asarray(values, dtype=float)
    return {
        "activity_initial": float(a[0]), "activity_mean": float(a.mean()),
        "activity_end": float(a[-1]), "activity_max": float(a.max()),
        "activity_slope": slope(a),
    }


def reference_periods() -> list[dict]:
    """Independent period estimates using seeds not used in Experiments 013/014."""
    rng = np.random.default_rng(SEED + 1500)
    rows = []
    for strength in STRENGTHS:
        periods = []
        for _ in range(16):
            initial = rng.dirichlet(np.array([1.4, 1.4, 1.4]))
            trajectory = simulate(initial, 2600, strength=strength, topology="canonical")
            period = phase_cycle_period(trajectory, min_turns=0.75)
            if np.isfinite(period): periods.append(period)
        rows.append({
            "strength": strength,
            "median_cycle_period": float(np.median(periods)),
            "n_reference": len(periods),
        })
    return rows


def observation_steps(period: float, ratio: float) -> int:
    return max(5, int(round(float(period) * float(ratio))))


def stochastic_step(x, strength, topology, sigma, rng):
    return perturb_simplex(step(x, strength=strength, topology=topology), sigma, rng)


def observe(initial, strength, topology, sigma, rng, n):
    x = initial.copy(); trajectory = [x.copy()]; activity = []
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
    x = state.copy(); errors = []
    for _ in range(HORIZON):
        action = regulator.choose_topology(x, TARGET, topology)
        x = apply_multichannel_action(x, action)
        x = stochastic_step(x, strength, topology, sigma, rng)
        errors.append(regulation_error(x, TARGET))
    return float(np.mean(errors))


def build_ratio_dataset(period_map, ratio):
    """Generate one locked ratio cell family with a ratio-specific seed."""
    ratio_seed = SEED + int(round(float(ratio) * 10000))
    master = np.random.default_rng(ratio_seed)
    rows = []; sample = 0
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
                    rows.append({
                        "sample": sample, "structure_index": si, "structure": topology,
                        "strength": strength, "noise_sigma": sigma, "replicate": rep,
                        "target_cycle_ratio": ratio, "observation_steps": obs,
                        "reference_cycle_period": period_map[strength],
                        "obs_cycle_ratio": actual_ratio,
                        "P": float(end[0]), "C": float(end[1]), "Ch": float(end[2]),
                        "imbalance": regulation_error(end, TARGET),
                        "phase": simplex_phase(end), **activity,
                        **quadratic_rate_features(trajectory),
                        **canonical_ebid_features(trajectory),
                        "future_horizon": HORIZON,
                        "future_error": future_error(end, strength, topology, sigma, fut_seed),
                    }); sample += 1
    return rows


def build_dataset(period_map):
    rows = []
    offset = 0
    for ratio in CYCLE_RATIOS:
        part = build_ratio_dataset(period_map, ratio)
        for r in part:
            r["sample"] = offset + int(r["sample"])
        offset += len(part)
        rows.extend(part)
    return rows


def col(rows, key): return np.asarray([float(r[key]) for r in rows], dtype=float)


def raw_design(rows, include_ebid):
    P, C, S = col(rows, "P"), col(rows, "C"), col(rows, "strength")
    phase = col(rows, "phase")
    cols = [
        P, C, S, P*P, C*C, S*S, P*C, P*S, C*S,
        *[col(rows, k) for k in ACTIVITY_KEYS],
        np.sin(phase), np.cos(phase),
        *[col(rows, k) for k in QUAD_KEYS],
    ]
    if include_ebid: cols += [col(rows, k) for k in EBID_KEYS]
    return np.column_stack(cols)


def ridge_fit_predict(train, test, include_ebid, alpha=RIDGE_ALPHA):
    """Fixed standardized ridge; intercept is not penalized."""
    X = raw_design(train, include_ebid); Z = raw_design(test, include_ebid)
    mu = X.mean(axis=0); sd = X.std(axis=0)
    sd[sd < 1e-10] = 1.0
    Xs = (X - mu) / sd; Zs = (Z - mu) / sd
    Xa = np.column_stack([np.ones(len(Xs)), Xs])
    Za = np.column_stack([np.ones(len(Zs)), Zs])
    penalty = np.eye(Xa.shape[1]); penalty[0, 0] = 0.0
    beta = np.linalg.solve(Xa.T @ Xa + alpha * penalty, Xa.T @ col(train, "future_error"))
    return Za @ beta


def relative_mae(y, p0, p1):
    b = float(np.mean(np.abs(y-p0))); e = float(np.mean(np.abs(y-p1)))
    return (b-e)/b, b, e


def bootstrap_relative_gain(y, p0, p1, seed, n_boot=2000):
    rng = np.random.default_rng(seed); n = len(y); gains = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        b = float(np.mean(np.abs(y[idx]-p0[idx]))); e = float(np.mean(np.abs(y[idx]-p1[idx])))
        if b > 1e-12: gains.append((b-e)/b)
    return float(np.quantile(gains, .025)), float(np.quantile(gains, .975))


def evaluate_per_ratio(rows):
    out = []
    for ratio in CYCLE_RATIOS:
        train = [r for r in rows if int(r["structure_index"]) != 0 and float(r["noise_sigma"]) in TRAIN_NOISE and abs(float(r["target_cycle_ratio"])-ratio) < 1e-12]
        test = [r for r in rows if int(r["structure_index"]) == 0 and float(r["noise_sigma"]) in TEST_NOISE and abs(float(r["target_cycle_ratio"])-ratio) < 1e-12]
        y = col(test, "future_error")
        p0 = ridge_fit_predict(train, test, False); p1 = ridge_fit_predict(train, test, True)
        gain, b, e = relative_mae(y, p0, p1)
        lo, hi = bootstrap_relative_gain(y, p0, p1, SEED + 15000 + int(ratio*1000))
        out.append({
            "target_cycle_ratio": ratio,
            "mean_actual_cycle_ratio": float(np.mean(col(test,"obs_cycle_ratio"))),
            "min_observation_steps": int(np.min(col(test,"observation_steps"))),
            "max_observation_steps": int(np.max(col(test,"observation_steps"))),
            "n_train": len(train), "n_test": len(test),
            "ridge_alpha": RIDGE_ALPHA,
            "base_mae": b, "ebid_mae": e,
            "relative_mae_reduction": gain,
            "bootstrap_ci_low": lo, "bootstrap_ci_high": hi,
            "ebid_better": int(gain > 0), "ci_strictly_positive": int(lo > 0),
        })
    return out


def main():
    refs = reference_periods(); write_csv(OUT/"reference_periods.csv", refs)
    period_map = {float(r["strength"]): float(r["median_cycle_period"]) for r in refs}
    rows = build_dataset(period_map); write_csv(OUT/"dataset.csv", rows)
    summary = evaluate_per_ratio(rows); write_csv(OUT/"summary.csv", summary)
    reliable = [r for r in summary if int(r["ci_strictly_positive"]) == 1]
    first = reliable[0]["target_cycle_ratio"] if reliable else ""
    write_csv(OUT/"transition.csv", [{
        "criterion": "first dense-band ratio with bootstrap CI > 0",
        "first_reliable_cycle_ratio": first,
        "n_reliable_ratios": len(reliable), "n_tested_ratios": len(summary),
    }])
    print("REFERENCE PERIODS")
    for r in refs: print(r)
    print("\nTRANSITION-BAND SUMMARY")
    for r in summary: print(r)
    print("\nFIRST RELIABLE RATIO", first)

if __name__ == "__main__": main()
