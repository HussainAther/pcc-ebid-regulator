"""Experiment 012: pre-specified phase-aware canonical EBID calibration.

This experiment does not change canonical EBID. It reuses the frozen trajectories
and outcomes from Experiment 011 and compares two nested predictors under the
same hard joint-OOD protocol (held-out topology + unseen noise):

  plain:       geometry + activity + phase + quadratic + canonical EBID
  phase-aware: plain + canonical EBID x sin(phase) + canonical EBID x cos(phase)

The phase interaction basis is fixed before evaluation. No interaction selection,
feature tuning, or outcome-dependent binning is performed.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

INFILE = ROOT / "results" / "011_ebid_transfer_diagnosis" / "dataset.csv"
OUT = ROOT / "results" / "012_phase_aware_ebid"
OUT.mkdir(parents=True, exist_ok=True)

TRAIN_NOISE = {0.0, 0.002, 0.005}
TEST_NOISE = {0.01, 0.02}
TOPOLOGIES = ["canonical", "reverse", "no_pressure_control", "no_control_chaos"]

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


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def col(rows: list[dict], key: str) -> np.ndarray:
    return np.asarray([float(r[key]) for r in rows], dtype=float)


def design(rows: list[dict], phase_aware: bool) -> np.ndarray:
    P, C, S = col(rows, "P"), col(rows, "C"), col(rows, "strength")
    phase = col(rows, "phase")
    sinp, cosp = np.sin(phase), np.cos(phase)

    cols = [P, C, S, P*P, C*C, S*S, P*C, P*S, C*S]
    cols += [col(rows, k) for k in ACTIVITY_KEYS]
    cols += [sinp, cosp]
    cols += [col(rows, k) for k in QUAD_KEYS]

    ebid_cols = [col(rows, k) for k in EBID_KEYS]
    cols += ebid_cols

    if phase_aware:
        # Pre-specified first-harmonic modulation of every frozen EBID feature.
        # This changes only the readout model, not EBID itself.
        cols += [e * sinp for e in ebid_cols]
        cols += [e * cosp for e in ebid_cols]

    return np.column_stack([np.ones(len(rows)), *cols])


def fit(train: list[dict], phase_aware: bool) -> np.ndarray:
    X = design(train, phase_aware)
    y = col(train, "future_error")
    return np.linalg.lstsq(X, y, rcond=None)[0]


def predict(rows: list[dict], beta: np.ndarray, phase_aware: bool) -> np.ndarray:
    return design(rows, phase_aware) @ beta


def mae(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean(np.abs(y - p)))


def relative_reduction(base: float, improved: float) -> float:
    return (base - improved) / base if base > 0 else float("nan")


def phase_bin(phase: float) -> str:
    p = (float(phase) + 2*np.pi) % (2*np.pi)
    return f"Q{int(np.floor(p / (np.pi / 2.0))) % 4 + 1}"


def bootstrap_delta(y: np.ndarray, p_plain: np.ndarray, p_phase: np.ndarray,
                    seed: int, draws: int = 2000) -> tuple[float, float, float]:
    """Bootstrap relative MAE reduction of phase-aware vs plain EBID."""
    rng = np.random.default_rng(seed)
    n = len(y)
    vals = []
    for _ in range(draws):
        idx = rng.integers(0, n, n)
        m0 = mae(y[idx], p_plain[idx])
        m1 = mae(y[idx], p_phase[idx])
        vals.append(relative_reduction(m0, m1))
    a = np.asarray(vals)
    return float(np.median(a)), float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975))


def evaluate_cell(cell: list[dict], held_out: str, obs: int, horizon: int) -> tuple[list[dict], list[dict]]:
    train = [r for r in cell if r["topology"] != held_out and float(r["noise_sigma"]) in TRAIN_NOISE]
    test = [r for r in cell if r["topology"] == held_out and float(r["noise_sigma"]) in TEST_NOISE]

    b_plain = fit(train, False)
    b_phase = fit(train, True)
    y = col(test, "future_error")
    p_plain = predict(test, b_plain, False)
    p_phase = predict(test, b_phase, True)
    m0, m1 = mae(y, p_plain), mae(y, p_phase)
    rr = relative_reduction(m0, m1)
    med, lo, hi = bootstrap_delta(y, p_plain, p_phase, seed=20260828 + obs*100 + horizon + TOPOLOGIES.index(held_out))

    summary = [{
        "held_out": held_out, "observation_steps": obs, "future_horizon": horizon,
        "group_type": "overall", "group": "all", "n": len(test),
        "plain_ebid_mae": m0, "phase_aware_mae": m1,
        "relative_mae_reduction": rr,
        "bootstrap_median": med, "bootstrap_lo95": lo, "bootstrap_hi95": hi,
    }]

    # Fixed phase quadrants are diagnostics only; they do not define the fitted interaction.
    bins = np.asarray([phase_bin(float(r["phase"])) for r in test])
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        idx = bins == q
        if not idx.any():
            continue
        qm0, qm1 = mae(y[idx], p_plain[idx]), mae(y[idx], p_phase[idx])
        summary.append({
            "held_out": held_out, "observation_steps": obs, "future_horizon": horizon,
            "group_type": "phase", "group": q, "n": int(idx.sum()),
            "plain_ebid_mae": qm0, "phase_aware_mae": qm1,
            "relative_mae_reduction": relative_reduction(qm0, qm1),
            "bootstrap_median": "", "bootstrap_lo95": "", "bootstrap_hi95": "",
        })

    detail = []
    for r, yy, a, b in zip(test, y, p_plain, p_phase):
        detail.append({
            "held_out": held_out, "observation_steps": obs, "future_horizon": horizon,
            "strength": r["strength"], "noise_sigma": r["noise_sigma"],
            "phase": r["phase"], "phase_bin": phase_bin(float(r["phase"])),
            "future_error": yy, "plain_abs_error": abs(yy-a), "phase_aware_abs_error": abs(yy-b),
            "phase_aware_better": int(abs(yy-b) < abs(yy-a)),
        })
    return summary, detail


def main() -> None:
    rows = read_rows(INFILE)
    summaries: list[dict] = []
    details: list[dict] = []

    obs_values = sorted({int(float(r["observation_steps"])) for r in rows})
    horizon_values = sorted({int(float(r["future_horizon"])) for r in rows})

    for obs in obs_values:
        for horizon in horizon_values:
            cell = [r for r in rows if int(float(r["observation_steps"])) == obs and int(float(r["future_horizon"])) == horizon]
            for held in TOPOLOGIES:
                s, d = evaluate_cell(cell, held, obs, horizon)
                summaries.extend(s); details.extend(d)

    write_csv(OUT / "summary.csv", summaries)
    write_csv(OUT / "test_predictions.csv", details)

    overall = [r for r in summaries if r["group_type"] == "overall"]
    print("OVERALL PHASE-AWARE VS PLAIN EBID")
    for r in overall:
        print(r)

    canonical = [r for r in overall if r["held_out"] == "canonical"]
    short = [r for r in canonical if int(r["observation_steps"]) <= 25]
    long = [r for r in canonical if int(r["observation_steps"]) == 50]
    print("\nCANONICAL SHORT-WINDOW POSITIVE CELLS", sum(float(r["relative_mae_reduction"]) > 0 for r in short), "/", len(short))
    print("CANONICAL LONG-WINDOW POSITIVE CELLS", sum(float(r["relative_mae_reduction"]) > 0 for r in long), "/", len(long))

if __name__ == "__main__":
    main()
