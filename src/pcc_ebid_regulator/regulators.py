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


def apply_multichannel_action(state: np.ndarray, action: np.ndarray) -> np.ndarray:
    """Apply component-specific multiplicative/logit interventions on the simplex.

    ``action`` is ordered [Pressure, Control, Chaos]. Positive values increase
    a component's relative weight and negative values decrease it. Normalizing
    after exponentiation preserves positivity and total mass. Because the state
    is compositional, a common offset to all three action components has no
    effect; this makes the effective intervention space at most two-dimensional.
    """
    x = np.asarray(state, dtype=float)
    u = np.asarray(action, dtype=float)
    if x.shape != (3,) or u.shape != (3,):
        raise ValueError("state and action must both have shape (3,)")
    if not np.all(np.isfinite(u)):
        raise ValueError("action must contain only finite values")
    logits = np.log(np.clip(x, 1e-12, None)) + u
    logits -= np.max(logits)
    controlled = np.exp(logits)
    return controlled / controlled.sum()


def multichannel_repertoire(
    channels: tuple[int, ...] | list[int],
    *,
    max_action: float = 0.12,
) -> list[np.ndarray]:
    """Return ternary {-a, 0, +a} interventions on accessible channels.

    This defines regulator *channel dimensionality* separately from scalar
    resolution. With k accessible channels the raw repertoire contains 3**k
    candidate action vectors (some are compositionally equivalent when k=3).
    """
    from itertools import product

    channel_tuple = tuple(int(i) for i in channels)
    if not channel_tuple:
        raise ValueError("at least one intervention channel is required")
    if len(set(channel_tuple)) != len(channel_tuple):
        raise ValueError("channels must be unique")
    if any(i not in (0, 1, 2) for i in channel_tuple):
        raise ValueError("channels must be drawn from 0=Pressure, 1=Control, 2=Chaos")

    levels = (-float(max_action), 0.0, float(max_action))
    actions: list[np.ndarray] = []
    for values in product(levels, repeat=len(channel_tuple)):
        action = np.zeros(3, dtype=float)
        for index, value in zip(channel_tuple, values):
            action[index] = value
        actions.append(action)
    return actions


@dataclass
class OracleMultiChannelTopologyRegulator:
    """Greedy topology-aware regulator with configurable intervention channels.

    Experiment 005 uses this optimistic oracle to isolate the effect of
    *qualitatively different intervention access* from structural-model error.
    """

    channels: tuple[int, ...]
    model_strength: float = 1.5
    max_action: float = 0.12

    def choose_topology(
        self,
        state: np.ndarray,
        target: np.ndarray,
        topology: str,
    ) -> np.ndarray:
        scored: list[tuple[float, np.ndarray]] = []
        for action in multichannel_repertoire(self.channels, max_action=self.max_action):
            controlled = apply_multichannel_action(state, action)
            predicted = step(
                controlled,
                strength=self.model_strength,
                topology=topology,
            )
            scored.append((regulation_error(predicted, target), action))
        return min(scored, key=lambda item: item[0])[1].copy()


def matched_directional_repertoire(
    channels: tuple[int, ...] | list[int],
    *,
    cardinality: int,
    max_action: float = 0.12,
    target_mean_norm: float | None = None,
) -> list[np.ndarray]:
    """Build a fixed-cardinality intervention set for capacity-matched tests.

    One-channel sets use evenly spaced scalar levels from ``-max_action`` to
    ``+max_action``. Two-channel sets contain one zero action plus evenly spaced
    directions on a circle in the selected coordinate plane. If
    ``target_mean_norm`` is given, the two-channel radius is chosen so the mean
    L2 norm of the resulting repertoire matches that target.

    The function intentionally supports one or two accessible channels only;
    Experiment 006 asks whether access to a second qualitative intervention
    direction helps when action-set cardinality and average magnitude are held
    fixed.
    """
    channel_tuple = tuple(int(i) for i in channels)
    if len(channel_tuple) not in (1, 2):
        raise ValueError("matched directional repertoires require one or two channels")
    if len(set(channel_tuple)) != len(channel_tuple):
        raise ValueError("channels must be unique")
    if any(i not in (0, 1, 2) for i in channel_tuple):
        raise ValueError("channels must be drawn from 0=Pressure, 1=Control, 2=Chaos")
    if cardinality < 3 or cardinality % 2 == 0:
        raise ValueError("cardinality must be an odd integer >= 3")

    if len(channel_tuple) == 1:
        levels = np.linspace(-float(max_action), float(max_action), cardinality)
        actions: list[np.ndarray] = []
        for value in levels:
            action = np.zeros(3, dtype=float)
            action[channel_tuple[0]] = float(value)
            actions.append(action)
        return actions

    nonzero_count = cardinality - 1
    if target_mean_norm is None:
        radius = float(max_action)
    else:
        radius = float(target_mean_norm) * cardinality / nonzero_count
    actions = [np.zeros(3, dtype=float)]
    for j in range(nonzero_count):
        theta = 2.0 * np.pi * j / nonzero_count
        action = np.zeros(3, dtype=float)
        action[channel_tuple[0]] = radius * np.cos(theta)
        action[channel_tuple[1]] = radius * np.sin(theta)
        actions.append(action)
    return actions


def mean_repertoire_norm(actions: list[np.ndarray]) -> float:
    """Mean L2 norm of an explicit vector-valued action repertoire."""
    if not actions:
        raise ValueError("actions must be non-empty")
    return float(np.mean([np.linalg.norm(np.asarray(action, dtype=float)) for action in actions]))


@dataclass
class OracleFixedActionTopologyRegulator:
    """Topology-aware greedy regulator over an explicit fixed action set."""

    actions: list[np.ndarray]
    model_strength: float = 1.5

    def choose_topology(
        self,
        state: np.ndarray,
        target: np.ndarray,
        topology: str,
    ) -> np.ndarray:
        if not self.actions:
            raise ValueError("actions must be non-empty")

        # Vectorized one-step evaluation keeps capacity-matched sweeps tractable.
        from .topology import topology_matrix

        action_matrix = np.asarray(self.actions, dtype=float)
        x = np.asarray(state, dtype=float)
        target_arr = np.asarray(target, dtype=float)
        logits = np.log(np.clip(x, 1e-12, None))[None, :] + action_matrix
        logits -= np.max(logits, axis=1, keepdims=True)
        controlled = np.exp(logits)
        controlled /= np.sum(controlled, axis=1, keepdims=True)

        matrix = topology_matrix(topology)
        fitness = controlled @ matrix.T
        mean_fitness = np.sum(controlled * fitness, axis=1)
        dx = self.model_strength * controlled * (fitness - mean_fitness[:, None])
        predicted = controlled + 0.02 * dx
        predicted = np.clip(predicted, 1e-12, None)
        predicted /= np.sum(predicted, axis=1, keepdims=True)
        errors = np.linalg.norm(predicted - target_arr[None, :], axis=1)
        return action_matrix[int(np.argmin(errors))].copy()
