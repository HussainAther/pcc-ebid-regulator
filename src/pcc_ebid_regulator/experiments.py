"""Shared simulation harness for regulator experiments."""

from __future__ import annotations

import numpy as np

from .dynamics import step
from .metrics import entropy_deficit, regulation_error
from .regulators import apply_control_action


def simulate_regulation(
    regulator: object,
    *,
    true_strength: float,
    steps: int = 2000,
    initial: np.ndarray | None = None,
    target: np.ndarray | None = None,
    burn_in: int = 500,
) -> dict[str, float]:
    state = np.array([0.58, 0.27, 0.15], dtype=float) if initial is None else np.asarray(initial, dtype=float)
    state = state / state.sum()
    target = np.full(3, 1.0 / 3.0) if target is None else np.asarray(target, dtype=float)

    errors: list[float] = []
    deficits: list[float] = []
    actions: list[float] = []

    for _ in range(steps):
        action = float(regulator.choose(state, target))
        controlled = apply_control_action(state, action)
        state = step(controlled, strength=true_strength)
        errors.append(regulation_error(state, target))
        deficits.append(entropy_deficit(state))
        actions.append(abs(action))

    start = max(0, steps - burn_in)
    return {
        "mean_error": float(np.mean(errors[start:])),
        "mean_entropy_deficit": float(np.mean(deficits[start:])),
        "mean_action_magnitude": float(np.mean(actions[start:])),
        "max_error": float(np.max(errors[start:])),
    }
