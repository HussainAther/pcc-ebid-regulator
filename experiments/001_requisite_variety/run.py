"""Experiment 001: action variety required under increasing PCC coupling.

The controller class is held fixed (reactive, state-only). Only its discrete
action repertoire changes. This isolates a capacity/requisite-variety question
from the model-content question studied in Experiment 002.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.experiments import simulate_regulation
from pcc_ebid_regulator.regulators import ReactiveRegulator

STRENGTHS = (0.5, 1.0, 1.5, 2.0, 3.0)
VARIETIES = (1, 3, 5, 9, 17, 33)
ERROR_THRESHOLD = 0.08


def main() -> None:
    output_dir = ROOT / "results" / "001_requisite_variety"
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, float | int | bool]] = []
    for strength in STRENGTHS:
        for variety in VARIETIES:
            result = simulate_regulation(
                ReactiveRegulator(variety=variety),
                true_strength=strength,
            )
            row = {
                "strength": strength,
                "variety": variety,
                **result,
                "bounded": result["mean_error"] <= ERROR_THRESHOLD,
            }
            rows.append(row)

    csv_path = output_dir / "sweep.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    threshold_path = output_dir / "thresholds.csv"
    thresholds: list[dict[str, float | int | str]] = []
    for strength in STRENGTHS:
        eligible = [r for r in rows if r["strength"] == strength and r["bounded"]]
        threshold = min((int(r["variety"]) for r in eligible), default=None)
        thresholds.append({
            "strength": strength,
            "error_threshold": ERROR_THRESHOLD,
            "minimum_variety": "not_observed" if threshold is None else threshold,
        })

    with threshold_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=thresholds[0].keys())
        writer.writeheader()
        writer.writerows(thresholds)

    print("strength,variety,mean_error,mean_entropy_deficit,mean_action_magnitude,bounded")
    for row in rows:
        print(
            f'{row["strength"]:.2f},{row["variety"]},{row["mean_error"]:.6f},'
            f'{row["mean_entropy_deficit"]:.6f},{row["mean_action_magnitude"]:.6f},'
            f'{int(bool(row["bounded"]))}'
        )
    print(f"\nWrote {csv_path.relative_to(ROOT)}")
    print(f"Wrote {threshold_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
