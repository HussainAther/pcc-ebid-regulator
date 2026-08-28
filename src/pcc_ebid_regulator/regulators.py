"""Simple regulators used to separate action variety from model content."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .dynamics import step
from .metrics import regulation_error


def apply_control_action(state: np.ndarray, action: float) -> np.ndarray:
    """Redistribute mass through the Control component while preserving the simplex."""
    x = np.asarray(state, dtype=float).copy()
    if action >= 0:
        available = x[0] + x[2]
        delta = min(float(action), 0.9 * available)
        if available > 0:
            take_p = delta * x[0] / available
            take_ch = delta - take_p
            x += np.array([-take_p, delta, -take_ch])
    else:
        give = min(abs(float(action)), 0.9 * x[1])
        x += np.array([give / 2.0, -give, give / 2.0])
    x = np.clip(x, 1e-12, None)
    return x / x.sum()


def action_repertoire(variety: int, max_action: float = 0.03) -> np.ndarray:
    if variety < 1:
        raise ValueError("variety must be >= 1")
    if variety == 1:
        return np.array([0.0])
    return np.linspace(-max_action, max_action, variety)


@dataclass
class GreedyModelRegulator:
    """One-step regulator using an explicit internal predictive model."""

    variety: int
    model_strength: float
    max_action: float = 0.03

    def choose(self, state: np.ndarray, target: np.ndarray) -> float:
        actions = action_repertoire(self.variety, self.max_action)
        scored: list[tuple[float, float]] = []
        for action in actions:
            controlled = apply_control_action(state, float(action))
            predicted = step(controlled, strength=self.model_strength)
            scored.append((regulation_error(predicted, target), float(action)))
        return min(scored, key=lambda item: item[0])[1]


@dataclass
class ReactiveRegulator:
    """Model-free regulator using only present Control deviation."""

    variety: int
    gain: float = 0.25
    max_action: float = 0.03

    def choose(self, state: np.ndarray, target: np.ndarray) -> float:
        desired = self.gain * float(target[1] - state[1])
        actions = action_repertoire(self.variety, self.max_action)
        return float(actions[np.argmin(np.abs(actions - desired))])


@dataclass
class TrendRegulator:
    """Short-history regulator extrapolating the recent state trend."""

    variety: int
    gain: float = 0.25
    max_action: float = 0.03
    previous_state: np.ndarray | None = None

    def choose(self, state: np.ndarray, target: np.ndarray) -> float:
        if self.previous_state is None:
            projected = state
        else:
            projected = state + (state - self.previous_state)
            projected = np.clip(projected, 1e-12, None)
            projected = projected / projected.sum()
        desired = self.gain * float(target[1] - projected[1])
        actions = action_repertoire(self.variety, self.max_action)
        action = float(actions[np.argmin(np.abs(actions - desired))])
        self.previous_state = np.asarray(state, dtype=float).copy()
        return action


ControllerFactory = Callable[[], object]

@dataclass
class OracleDynamicRegulator:
    """One-step regulator given the current true coupling strength.

    This deliberately grants perfect instantaneous parameter knowledge so that
    Experiment 003 varies action repertoire while holding model adequacy at an
    optimistic upper bound. It is therefore not a realistic controller.
    """

    variety: int
    max_action: float = 0.03

    def choose_dynamic(self, state: np.ndarray, target: np.ndarray, true_strength: float) -> float:
        actions = action_repertoire(self.variety, self.max_action)
        scored: list[tuple[float, float]] = []
        for action in actions:
            controlled = apply_control_action(state, float(action))
            predicted = step(controlled, strength=true_strength)
            scored.append((regulation_error(predicted, target), float(action)))
        return min(scored, key=lambda item: item[0])[1]

@dataclass
class OracleTopologyRegulator:
    """One-step regulator given the currently active topology.

    Used in Experiment 004A to isolate action repertoire size while granting
    optimistic, perfect structural knowledge.
    """

    variety: int
    model_strength: float = 1.5
    max_action: float = 0.03

    def choose_topology(self, state: np.ndarray, target: np.ndarray, topology: str) -> float:
        actions = action_repertoire(self.variety, self.max_action)
        scored: list[tuple[float, float]] = []
        for action in actions:
            controlled = apply_control_action(state, float(action))
            predicted = step(
                controlled,
                strength=self.model_strength,
                topology=topology,
            )
            scored.append((regulation_error(predicted, target), float(action)))
        return min(scored, key=lambda item: item[0])[1]


@dataclass
class FixedTopologyRegulator:
    """One-step model-based regulator that assumes one fixed topology."""

    variety: int
    model_topology: str = "canonical"
    model_strength: float = 1.5
    max_action: float = 0.03

    def choose(self, state: np.ndarray, target: np.ndarray) -> float:
        actions = action_repertoire(self.variety, self.max_action)
        scored: list[tuple[float, float]] = []
        for action in actions:
            controlled = apply_control_action(state, float(action))
            predicted = step(
                controlled,
                strength=self.model_strength,
                topology=self.model_topology,
            )
            scored.append((regulation_error(predicted, target), float(action)))
        return min(scored, key=lambda item: item[0])[1]
