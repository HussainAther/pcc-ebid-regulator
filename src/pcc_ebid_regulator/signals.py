"""Dynamic signal descriptors for PCC-specificity experiments."""

from __future__ import annotations

import numpy as np

from .benchmark import benchmark_bias
from .topology import topology_matrix


def pcc_interaction_activity(state: np.ndarray, *, strength: float = 1.0, topology: str = "canonical") -> float:
    """Instantaneous norm of the endogenous PCC replicator vector field.

    This is an EBID-adjacent dynamic observable used experimentally; it is not
    asserted to be a canonical EBID definition.
    """
    x = np.asarray(state, dtype=float)
    matrix = topology_matrix(topology)
    fitness = matrix @ x
    mean_fitness = float(x @ fitness)
    dx = float(strength) * x * (fitness - mean_fitness)
    return float(np.linalg.norm(dx))


def benchmark_activity(state: np.ndarray, *, strength: float = 1.0, regime: str = "pressure_bias") -> float:
    """Analogous instantaneous vector-field norm for the non-PCC benchmark."""
    x = np.asarray(state, dtype=float)
    bias = benchmark_bias(regime)
    mean_bias = float(x @ bias)
    dx = float(strength) * x * (bias - mean_bias)
    return float(np.linalg.norm(dx))


def simplex_phase(state: np.ndarray) -> float:
    """Angular position around the symmetric simplex center in a 2D basis."""
    x = np.asarray(state, dtype=float)
    centered = x - np.full(3, 1.0 / 3.0)
    e1 = np.array([1.0, -1.0, 0.0]) / np.sqrt(2.0)
    e2 = np.array([1.0, 1.0, -2.0]) / np.sqrt(6.0)
    return float(np.arctan2(centered @ e2, centered @ e1))
