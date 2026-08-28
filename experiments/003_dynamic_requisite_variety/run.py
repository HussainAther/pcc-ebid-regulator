"""Experiment 003: dynamic requisite variety under parameter drift.

The controller is granted oracle knowledge of the current coupling strength.
That optimistic assumption intentionally holds model adequacy fixed so this
experiment can focus on finite action repertoire size under nonstationarity.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.drift import (  # noqa: E402
    random_walk_strength_schedule,
    sinusoidal_strength_schedule,
)
from pcc_ebid_regulator.experiments import simulate_dynamic_regulation  # noqa: E402
from pcc_ebid_regulator.regulators import OracleDynamicRegulator  # noqa: E402

OUT = ROOT / "results" / "003_dynamic_requisite_variety"
OUT.mkdir(parents=True, exist_ok=True)

VARIETIES = [1, 3, 5, 9, 17]
STEPS = 600
BURN_IN = 200
ERROR_CRITERIA = [0.040, 0.035, 0.030, 0.028]


def run_sinusoidal() -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    for amplitude in [0.0, 0.5, 1.0]:
        for period in [100, 300, 700]:
            schedule = sinusoidal_strength_schedule(
                STEPS, base_strength=1.5, amplitude=amplitude, period=period
            )
            for variety in VARIETIES:
                result = simulate_dynamic_regulation(
                    OracleDynamicRegulator(variety=variety),
                    strength_schedule=schedule,
                    burn_in=BURN_IN,
                )
                rows.append(
                    {
                        "schedule": "sinusoidal",
                        "amplitude": amplitude,
                        "period": period,
                        "seed": -1,
                        "variety": variety,
                        **result,
                    }
                )
    return rows


def run_random_walk() -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    for innovation_std in [0.0, 0.01, 0.03, 0.06, 0.10]:
        for seed in range(3):
            schedule = random_walk_strength_schedule(
                STEPS,
                base_strength=1.5,
                innovation_std=innovation_std,
                reversion=0.02,
                seed=seed,
            )
            for variety in VARIETIES:
                result = simulate_dynamic_regulation(
                    OracleDynamicRegulator(variety=variety),
                    strength_schedule=schedule,
                    burn_in=BURN_IN,
                )
                rows.append(
                    {
                        "schedule": "random_walk",
                        "amplitude": innovation_std,
                        "period": -1,
                        "seed": seed,
                        "variety": variety,
                        **result,
                    }
                )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize_thresholds(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        key = (row["schedule"], row["amplitude"], row["period"], row["seed"])
        grouped.setdefault(key, []).append(row)

    output: list[dict[str, object]] = []
    for key, group in grouped.items():
        group = sorted(group, key=lambda r: int(r["variety"]))
        for criterion in ERROR_CRITERIA:
            passing = [r for r in group if float(r["mean_error"]) <= criterion]
            minimum = min((int(r["variety"]) for r in passing), default=-1)
            output.append(
                {
                    "schedule": key[0],
                    "amplitude": key[1],
                    "period": key[2],
                    "seed": key[3],
                    "error_criterion": criterion,
                    "minimum_variety": minimum,
                    "strength_std": float(group[0]["strength_std"]),
                    "strength_range": float(group[0]["strength_range"]),
                }
            )
    return output


def aggregate_random_walk(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    random_rows = [r for r in rows if r["schedule"] == "random_walk"]
    output: list[dict[str, object]] = []
    for amplitude in sorted({float(r["amplitude"]) for r in random_rows}):
        for variety in VARIETIES:
            cell = [r for r in random_rows if float(r["amplitude"]) == amplitude and int(r["variety"]) == variety]
            output.append(
                {
                    "innovation_std": amplitude,
                    "variety": variety,
                    "mean_error": float(np.mean([float(r["mean_error"]) for r in cell])),
                    "std_error_across_seeds": float(np.std([float(r["mean_error"]) for r in cell])),
                    "mean_p95_error": float(np.mean([float(r["p95_error"]) for r in cell])),
                    "mean_strength_std": float(np.mean([float(r["strength_std"]) for r in cell])),
                }
            )
    return output


def main() -> None:
    rows = run_sinusoidal() + run_random_walk()
    thresholds = summarize_thresholds(rows)
    aggregate = aggregate_random_walk(rows)
    write_csv(OUT / "sweep.csv", rows)
    write_csv(OUT / "thresholds.csv", thresholds)
    write_csv(OUT / "random_walk_aggregate.csv", aggregate)

    print("Experiment 003: dynamic requisite variety under parameter drift")
    print(f"Runs: {len(rows)}")
    print("\nRandom-walk aggregate mean errors:")
    for row in aggregate:
        print(
            f"drift={row['innovation_std']:.3f} variety={int(row['variety']):2d} "
            f"error={row['mean_error']:.6f} p95={row['mean_p95_error']:.6f}"
        )

    print("\nThreshold behavior (random walk, criterion=0.030):")
    selected = [
        r for r in thresholds
        if r["schedule"] == "random_walk" and float(r["error_criterion"]) == 0.030
    ]
    for amplitude in sorted({float(r["amplitude"]) for r in selected}):
        vals = [int(r["minimum_variety"]) for r in selected if float(r["amplitude"]) == amplitude]
        print(f"drift={amplitude:.3f}: thresholds={vals}")


if __name__ == "__main__":
    main()
