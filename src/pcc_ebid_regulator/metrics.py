"""Information and regulation metrics for PCC experiments."""

from __future__ import annotations

import numpy as np


def shannon_entropy(probabilities: np.ndarray) -> float:
    p = np.asarray(probabilities, dtype=float)
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)))


def normalized_entropy(probabilities: np.ndarray) -> float:
    p = np.asarray(probabilities, dtype=float)
    return shannon_entropy(p) / np.log(p.size)


def entropy_deficit(probabilities: np.ndarray) -> float:
    """Distance from maximum normalized entropy; a simple EBID-adjacent observable."""
    return 1.0 - normalized_entropy(probabilities)


def regulation_error(state: np.ndarray, target: np.ndarray | None = None) -> float:
    target = np.full(3, 1.0 / 3.0) if target is None else np.asarray(target, dtype=float)
    return float(np.linalg.norm(np.asarray(state, dtype=float) - target))
