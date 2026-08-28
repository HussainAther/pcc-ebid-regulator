"""Experiment 004: structural requisite variety and topology-model adequacy.

004A isolates action repertoire by granting oracle knowledge of the active
interaction topology. 004B fixes action repertoire and varies internal model
content/structural knowledge.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.experiments import simulate_topology_regulation  # noqa: E402
from pcc_ebid_regulator.regulators import (  # noqa: E402
    FixedTopologyRegulator,
    OracleTopologyRegulator,
    ReactiveRegulator,
    TrendRegulator,
)
from pcc_ebid_regulator.topology import cyclic_topology_schedule  # noqa: E402

OUT = ROOT / "results" / "004_topology_switching"
OUT.mkdir(parents=True, exist_ok=True)

STEPS = 800
BURN_IN = 300
TRUE_STRENGTH = 1.5
VARIETIES = [1, 3, 5, 9, 17]
DWELLS = [20, 50, 100]
ERROR_CRITERIA = [0.040, 0.035, 0.030, 0.028]
TOPOLOGY_ORDER = [
    "canonical",
    "reverse",
    "no_pressure_control",
    "no_control_chaos",
]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_004a() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for topology_count in range(1, len(TOPOLOGY_ORDER) + 1):
        names = TOPOLOGY_ORDER[:topology_count]
        for dwell in DWELLS:
            schedule = cyclic_topology_schedule(STEPS, names, dwell=dwell)
            for variety in VARIETIES:
                result = simulate_topology_regulation(
                    OracleTopologyRegulator(
                        variety=variety,
                        model_strength=TRUE_STRENGTH,
                    ),
                    topology_schedule=schedule,
                    true_strength=TRUE_STRENGTH,
                    burn_in=BURN_IN,
                )
                rows.append(
                    {
                        "topology_count": topology_count,
                        "topologies": ";".join(names),
                        "dwell": dwell,
                        "variety": variety,
                        **result,
                    }
                )
    return rows


def summarize_004a(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for topology_count in range(1, len(TOPOLOGY_ORDER) + 1):
        for dwell in DWELLS:
            cell = [
                r for r in rows
                if int(r["topology_count"]) == topology_count and int(r["dwell"]) == dwell
            ]
            for criterion in ERROR_CRITERIA:
                passing = [r for r in cell if float(r["mean_error"]) <= criterion]
                minimum = min((int(r["variety"]) for r in passing), default=-1)
                output.append(
                    {
                        "topology_count": topology_count,
                        "dwell": dwell,
                        "error_criterion": criterion,
                        "minimum_variety": minimum,
                    }
                )
    return output


def summarize_best_004a(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for topology_count in range(1, len(TOPOLOGY_ORDER) + 1):
        for dwell in DWELLS:
            cell = [
                r for r in rows
                if int(r["topology_count"]) == topology_count and int(r["dwell"]) == dwell
            ]
            best = min(cell, key=lambda r: float(r["mean_error"]))
            output.append(
                {
                    "topology_count": topology_count,
                    "dwell": dwell,
                    "best_variety": int(best["variety"]),
                    "best_mean_error": float(best["mean_error"]),
                    "best_p95_error": float(best["p95_error"]),
                }
            )
    return output


def run_004b() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    names = TOPOLOGY_ORDER
    for dwell in DWELLS:
        schedule = cyclic_topology_schedule(STEPS, names, dwell=dwell)
        factories = {
            "oracle_active_topology": lambda: OracleTopologyRegulator(
                variety=9, model_strength=TRUE_STRENGTH
            ),
            "fixed_canonical_model": lambda: FixedTopologyRegulator(
                variety=9,
                model_topology="canonical",
                model_strength=TRUE_STRENGTH,
            ),
            "fixed_reverse_model": lambda: FixedTopologyRegulator(
                variety=9,
                model_topology="reverse",
                model_strength=TRUE_STRENGTH,
            ),
            "reactive_state_only": lambda: ReactiveRegulator(variety=9),
            "short_history": lambda: TrendRegulator(variety=9),
        }
        for controller, factory in factories.items():
            result = simulate_topology_regulation(
                factory(),
                topology_schedule=schedule,
                true_strength=TRUE_STRENGTH,
                burn_in=BURN_IN,
            )
            rows.append(
                {
                    "controller": controller,
                    "dwell": dwell,
                    "topology_count": len(names),
                    "variety": 9,
                    **result,
                }
            )
    return rows


def main() -> None:
    rows_a = run_004a()
    thresholds = summarize_004a(rows_a)
    best_a = summarize_best_004a(rows_a)
    rows_b = run_004b()
    write_csv(OUT / "004a_sweep.csv", rows_a)
    write_csv(OUT / "004a_thresholds.csv", thresholds)
    write_csv(OUT / "004a_best.csv", best_a)
    write_csv(OUT / "004b_model_comparison.csv", rows_b)

    print("Experiment 004A: topology-switching requisite variety")
    print("criterion=0.030")
    for dwell in DWELLS:
        vals = []
        for count in range(1, 5):
            row = next(
                r for r in thresholds
                if int(r["topology_count"]) == count
                and int(r["dwell"]) == dwell
                and float(r["error_criterion"]) == 0.030
            )
            vals.append(int(row["minimum_variety"]))
        print(f"dwell={dwell:3d}: minimum varieties {vals}")

    print("\nExperiment 004B: same repertoire (9), different model content")
    for dwell in DWELLS:
        print(f"dwell={dwell}")
        for row in [r for r in rows_b if int(r["dwell"]) == dwell]:
            print(
                f"  {str(row['controller']):24s} "
                f"mean={float(row['mean_error']):.6f} "
                f"p95={float(row['p95_error']):.6f} "
                f"max={float(row['max_error']):.6f}"
            )


if __name__ == "__main__":
    main()
