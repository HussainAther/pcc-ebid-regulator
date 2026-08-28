"""Experiment 011: diagnose topology-dependent canonical EBID transfer.

Canonical EBID remains frozen. We reproduce the joint OOD setup from
Experiment 010 while sweeping observation window and future horizon, then map
incremental EBID value across held-out canonical/reverse topology, strength,
and observed cycle phase.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.dynamics import step
from pcc_ebid_regulator.ebid import canonical_ebid_features, quadratic_rate_features
from pcc_ebid_regulator.metrics import regulation_error
from pcc_ebid_regulator.regulators import (
    OracleFixedActionTopologyRegulator,
    apply_multichannel_action,
    matched_directional_repertoire,
)
from pcc_ebid_regulator.signals import pcc_interaction_activity, simplex_phase
from pcc_ebid_regulator.stochastic import perturb_simplex

OUT = ROOT / "results" / "011_ebid_transfer_diagnosis"
OUT.mkdir(parents=True, exist_ok=True)
TARGET = np.ones(3) / 3.0
TOPOLOGIES = ["canonical", "reverse", "no_pressure_control", "no_control_chaos"]
STRENGTHS = [0.5, 1.0, 2.0, 3.0]
TRAIN_NOISE = [0.0, 0.002, 0.005]
TEST_NOISE = [0.01, 0.02]
OBS_WINDOWS = [10, 25, 50]
HORIZONS = [20, 40, 80]
REPLICATES = 4
K = 9
MAX_ACTION = 0.12
SEED = 20260828

EBID_KEYS = [
    "ebid_initial_entropy", "ebid_mean_entropy", "ebid_end_entropy",
    "ebid_entropy_drop", "ebid_entropy_slope", "ebid_mean_entropy_rate",
    "ebid_min_entropy_rate", "ebid_entropy_rate_variance",
    "ebid_deficit_growth", "ebid_max_deficit_rate", "ebid_deficit_rate_variance",
]
QUAD_KEYS = [
    "quad_initial", "quad_mean", "quad_end", "quad_growth", "quad_slope",
    "quad_mean_rate", "quad_min_rate", "quad_max_rate", "quad_rate_variance",
]
ACTIVITY_KEYS = ["activity_initial", "activity_mean", "activity_end", "activity_max", "activity_slope"]
BASE_SPEC = "geometry+activity+phase+quadratic"
EBID_SPEC = BASE_SPEC + "+ebid"


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def slope(a: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    return float(np.polyfit(np.arange(a.size, dtype=float), a, 1)[0]) if a.size > 1 else 0.0


def activity_features(values: list[float]) -> dict[str, float]:
    a = np.asarray(values, dtype=float)
    return {
        "activity_initial": float(a[0]), "activity_mean": float(a.mean()),
        "activity_end": float(a[-1]), "activity_max": float(a.max()),
        "activity_slope": slope(a),
    }


def stochastic_step(x, strength, topology, sigma, rng):
    return perturb_simplex(step(x, strength=strength, topology=topology), sigma, rng)


def observe(initial, strength, topology, sigma, rng, observation_steps):
    x = initial.copy(); traj = [x.copy()]; acts = []
    for _ in range(observation_steps + 1):
        acts.append(pcc_interaction_activity(x, strength=strength, topology=topology))
        if len(traj) <= observation_steps:
            x = stochastic_step(x, strength, topology, sigma, rng)
            traj.append(x.copy())
    return x, np.asarray(traj), activity_features(acts)


def future_error(state, strength, topology, sigma, rng, horizon):
    actions = matched_directional_repertoire((1,), cardinality=K, max_action=MAX_ACTION)
    reg = OracleFixedActionTopologyRegulator(actions=actions, model_strength=strength)
    x = state.copy(); errors = []
    for _ in range(horizon):
        x = apply_multichannel_action(x, reg.choose_topology(x, TARGET, topology))
        x = stochastic_step(x, strength, topology, sigma, rng)
        errors.append(regulation_error(x, TARGET))
    return float(np.mean(errors))


def build_rows(observation_steps: int, horizon: int) -> list[dict]:
    # Reinitialize per window/horizon so all cells share paired starting draws.
    master = np.random.default_rng(SEED + 1000 * observation_steps + horizon)
    rows = []; sample = 0
    for ti, topology in enumerate(TOPOLOGIES):
        for strength in STRENGTHS:
            for sigma in TRAIN_NOISE + TEST_NOISE:
                for rep in range(REPLICATES):
                    initial = master.dirichlet(np.array([1.4, 1.4, 1.4]))
                    rng = np.random.default_rng(int(master.integers(0, 2**31 - 1)))
                    end, traj, act = observe(initial, strength, topology, sigma, rng, observation_steps)
                    ferr = future_error(end, strength, topology, sigma, rng, horizon)
                    rows.append({
                        "sample": sample, "topology_index": ti, "topology": topology,
                        "strength": strength, "noise_sigma": sigma, "replicate": rep,
                        "observation_steps": observation_steps, "future_horizon": horizon,
                        "P": float(end[0]), "C": float(end[1]), "Ch": float(end[2]),
                        "imbalance": regulation_error(end, TARGET), "phase": simplex_phase(end),
                        **act, **quadratic_rate_features(traj), **canonical_ebid_features(traj),
                        "future_error": ferr,
                    })
                    sample += 1
    return rows


def col(rows, key):
    return np.asarray([float(r[key]) for r in rows], dtype=float)


def design(rows, spec):
    P, C, S = col(rows, "P"), col(rows, "C"), col(rows, "strength")
    cols = [P, C, S, P*P, C*C, S*S, P*C, P*S, C*S]
    cols += [col(rows, k) for k in ACTIVITY_KEYS]
    ph = col(rows, "phase"); cols += [np.sin(ph), np.cos(ph)]
    cols += [col(rows, k) for k in QUAD_KEYS]
    if "+ebid" in spec:
        cols += [col(rows, k) for k in EBID_KEYS]
    return np.column_stack([np.ones(len(rows)), *cols])


def fit(train, spec):
    X = design(train, spec); y = col(train, "future_error")
    return np.linalg.lstsq(X, y, rcond=None)[0]


def pred(rows, beta, spec):
    return design(rows, spec) @ beta


def rel_mae_reduction(y, base_pred, ebid_pred):
    b = np.abs(y - base_pred); e = np.abs(y - ebid_pred)
    bm = float(b.mean()); em = float(e.mean())
    return (bm - em) / bm if bm > 0 else float("nan"), bm, em


def phase_bin(phase: float) -> str:
    # Four fixed quadrants around the simplex center; avoids data-dependent bins.
    p = (float(phase) + 2*np.pi) % (2*np.pi)
    q = int(np.floor(p / (np.pi / 2.0))) % 4
    return f"Q{q+1}"


def evaluate_cell(rows, held_out: str, observation_steps: int, horizon: int):
    train = [r for r in rows if r["topology"] != held_out and float(r["noise_sigma"]) in TRAIN_NOISE]
    test = [r for r in rows if r["topology"] == held_out and float(r["noise_sigma"]) in TEST_NOISE]
    b0 = fit(train, BASE_SPEC); b1 = fit(train, EBID_SPEC)
    y = col(test, "future_error"); p0 = pred(test, b0, BASE_SPEC); p1 = pred(test, b1, EBID_SPEC)
    overall, bmae, emae = rel_mae_reduction(y, p0, p1)
    summary = [{
        "held_out": held_out, "observation_steps": observation_steps, "future_horizon": horizon,
        "group_type": "overall", "group": "all", "n": len(test),
        "base_mae": bmae, "ebid_mae": emae, "relative_mae_reduction": overall,
    }]
    # Strength-specific diagnostics.
    for strength in STRENGTHS:
        idx = np.array([float(r["strength"]) == strength for r in test])
        rr, bb, ee = rel_mae_reduction(y[idx], p0[idx], p1[idx])
        summary.append({
            "held_out": held_out, "observation_steps": observation_steps, "future_horizon": horizon,
            "group_type": "strength", "group": str(strength), "n": int(idx.sum()),
            "base_mae": bb, "ebid_mae": ee, "relative_mae_reduction": rr,
        })
    # Fixed cycle-phase quadrants.
    bins = [phase_bin(r["phase"]) for r in test]
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        idx = np.array([z == q for z in bins])
        if idx.sum() == 0:
            continue
        rr, bb, ee = rel_mae_reduction(y[idx], p0[idx], p1[idx])
        summary.append({
            "held_out": held_out, "observation_steps": observation_steps, "future_horizon": horizon,
            "group_type": "phase", "group": q, "n": int(idx.sum()),
            "base_mae": bb, "ebid_mae": ee, "relative_mae_reduction": rr,
        })
    detail = []
    for r, yy, a, b in zip(test, y, p0, p1):
        detail.append({
            "held_out": held_out, "observation_steps": observation_steps, "future_horizon": horizon,
            "strength": r["strength"], "noise_sigma": r["noise_sigma"], "phase": r["phase"],
            "phase_bin": phase_bin(r["phase"]), "future_error": yy,
            "base_abs_error": abs(yy-a), "ebid_abs_error": abs(yy-b),
            "ebid_better": int(abs(yy-b) < abs(yy-a)),
        })
    return summary, detail


def main():
    all_summary = []; all_detail = []; all_rows = []
    for obs in OBS_WINDOWS:
        for horizon in HORIZONS:
            rows = build_rows(obs, horizon)
            all_rows.extend(rows)
            for held in ("canonical", "reverse"):
                s, d = evaluate_cell(rows, held, obs, horizon)
                all_summary.extend(s); all_detail.extend(d)
    write_csv(OUT / "dataset.csv", all_rows)
    write_csv(OUT / "summary.csv", all_summary)
    write_csv(OUT / "test_predictions.csv", all_detail)

    overall = [r for r in all_summary if r["group_type"] == "overall"]
    print("OVERALL")
    for r in overall:
        print(r)
    print("\nCANONICAL FAILURES")
    for r in overall:
        if r["held_out"] == "canonical" and float(r["relative_mae_reduction"]) <= 0:
            print(r)

if __name__ == "__main__":
    main()
