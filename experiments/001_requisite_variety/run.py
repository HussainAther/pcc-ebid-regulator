"""Experiment 001: empirical regulator-variety threshold in a toy PCC system.

This is a baseline experiment, not a theorem test. It creates discrete regulator
actions that shift mass toward/away from Control, then asks how repertoire size
affects average distance from the symmetric target.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.dynamics import step
from pcc_ebid_regulator.metrics import entropy_deficit, regulation_error


def apply_action(state: np.ndarray, action: float) -> np.ndarray:
    x = state.copy()
    # Positive action transfers a small amount from Pressure/Chaos to Control;
    # negative action reverses that direction.
    delta = min(abs(action), 0.45 * min(x[0] + x[2], x[1] + 1e-12))
    if action >= 0:
        take_p = delta * x[0] / (x[0] + x[2])
        take_ch = delta - take_p
        x += np.array([-take_p, delta, -take_ch])
    else:
        give = min(delta, x[1] * 0.9)
        x += np.array([give / 2, -give, give / 2])
    x = np.clip(x, 1e-12, None)
    return x / x.sum()


def run(variety: int, strength: float, steps: int = 2000) -> tuple[float, float]:
    state = np.array([0.58, 0.27, 0.15], dtype=float)
    actions = np.linspace(-0.03, 0.03, variety)
    errors = []
    deficits = []
    target = np.full(3, 1 / 3)

    for _ in range(steps):
        # Greedy one-step regulator over a finite action repertoire.
        candidates = []
        for action in actions:
            controlled = apply_action(state, float(action))
            nxt = step(controlled, strength=strength)
            candidates.append((regulation_error(nxt, target), nxt))
        _, state = min(candidates, key=lambda item: item[0])
        errors.append(regulation_error(state, target))
        deficits.append(entropy_deficit(state))

    return float(np.mean(errors[-500:])), float(np.mean(deficits[-500:]))


if __name__ == "__main__":
    print("strength,variety,mean_error,mean_entropy_deficit")
    for strength in (0.5, 1.0, 1.5, 2.0):
        for variety in (1, 3, 5, 9, 17):
            error, deficit = run(variety=variety, strength=strength)
            print(f"{strength:.2f},{variety},{error:.6f},{deficit:.6f}")
