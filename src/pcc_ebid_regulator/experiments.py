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


def simulate_dynamic_regulation(
    regulator: object,
    *,
    strength_schedule: np.ndarray,
    initial: np.ndarray | None = None,
    target: np.ndarray | None = None,
    burn_in: int = 500,
) -> dict[str, float]:
    """Simulate regulation when PCC coupling varies over time."""
    strengths = np.asarray(strength_schedule, dtype=float)
    if strengths.ndim != 1 or strengths.size < 1:
        raise ValueError("strength_schedule must be a non-empty 1D array")

    state = np.array([0.58, 0.27, 0.15], dtype=float) if initial is None else np.asarray(initial, dtype=float)
    state = state / state.sum()
    target = np.full(3, 1.0 / 3.0) if target is None else np.asarray(target, dtype=float)

    errors: list[float] = []
    deficits: list[float] = []
    actions: list[float] = []

    for strength in strengths:
        if hasattr(regulator, "choose_dynamic"):
            action = float(regulator.choose_dynamic(state, target, float(strength)))
        else:
            action = float(regulator.choose(state, target))
        controlled = apply_control_action(state, action)
        state = step(controlled, strength=float(strength))
        errors.append(regulation_error(state, target))
        deficits.append(entropy_deficit(state))
        actions.append(abs(action))

    start = max(0, strengths.size - burn_in)
    tail_errors = np.asarray(errors[start:], dtype=float)
    return {
        "mean_error": float(np.mean(tail_errors)),
        "p95_error": float(np.quantile(tail_errors, 0.95)),
        "mean_entropy_deficit": float(np.mean(deficits[start:])),
        "mean_action_magnitude": float(np.mean(actions[start:])),
        "max_error": float(np.max(tail_errors)),
        "strength_mean": float(np.mean(strengths[start:])),
        "strength_std": float(np.std(strengths[start:])),
        "strength_range": float(np.ptp(strengths[start:])),
    }
