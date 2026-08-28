"""Matched stochastic perturbations for PCC and benchmark OOD experiments."""
from __future__ import annotations

import numpy as np


def perturb_simplex(state: np.ndarray, sigma: float, rng: np.random.Generator) -> np.ndarray:
    """Add isotropic Gaussian noise in the simplex tangent plane, then renormalize."""
    x = np.asarray(state, dtype=float)
    if x.shape != (3,):
        raise ValueError("state must have shape (3,)")
    if sigma < 0:
        raise ValueError("sigma must be >= 0")
    if sigma == 0:
        return x.copy()
    z = rng.normal(0.0, sigma, size=3)
    z -= np.mean(z)
    y = np.clip(x + z, 1e-12, None)
    return y / np.sum(y)
