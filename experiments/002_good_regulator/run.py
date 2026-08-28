"""Experiment 002: regulation performance as internal model content changes.

Action repertoire is matched across controllers. We compare a present-state
reactive controller, a short-history trend controller, a correctly specified
PCC predictive model, and misspecified predictive models.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.experiments import simulate_regulation
from pcc_ebid_regulator.regulators import GreedyModelRegulator, ReactiveRegulator, TrendRegulator

TRUE_STRENGTHS = (0.75, 1.5, 2.5)
VARIETY = 9


def regulator_specs(true_strength: float):
    return (
        ("state_only", lambda: ReactiveRegulator(variety=VARIETY)),
        ("short_history", lambda: TrendRegulator(variety=VARIETY)),
        ("correct_pcc_model", lambda: GreedyModelRegulator(variety=VARIETY, model_strength=true_strength)),
        ("weak_pcc_model", lambda: GreedyModelRegulator(variety=VARIETY, model_strength=0.5 * true_strength)),
        ("strong_pcc_model", lambda: GreedyModelRegulator(variety=VARIETY, model_strength=1.5 * true_strength)),
    )


def main() -> None:
    output_dir = ROOT / "results" / "002_good_regulator"
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for true_strength in TRUE_STRENGTHS:
        for name, factory in regulator_specs(true_strength):
            result = simulate_regulation(factory(), true_strength=true_strength)
            rows.append({
                "true_strength": true_strength,
                "regulator": name,
                "variety": VARIETY,
                **result,
            })

    path = output_dir / "model_comparison.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("true_strength,regulator,variety,mean_error,mean_entropy_deficit,mean_action_magnitude")
    for row in rows:
        print(
            f'{row["true_strength"]:.2f},{row["regulator"]},{row["variety"]},'
            f'{row["mean_error"]:.6f},{row["mean_entropy_deficit"]:.6f},'
            f'{row["mean_action_magnitude"]:.6f}'
        )
    print(f"\nWrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
