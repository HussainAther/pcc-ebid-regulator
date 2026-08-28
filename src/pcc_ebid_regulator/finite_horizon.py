"""Finite-horizon controllability and response-memory descriptors.

These descriptors are intentionally distinct from EBID. They ask how small
state perturbations and standardized intervention choices alter *future* states
under a supplied deterministic transition rule.
"""
from __future__ import annotations

import numpy as np

from .regulators import apply_multichannel_action


def _validate(traj: np.ndarray) -> np.ndarray:
    x = np.asarray(traj, dtype=float)
    if x.ndim != 2 or x.shape[1] != 3 or len(x) < 4:
        raise ValueError("trajectory must have shape (time>=4, 3)")
    return x


def _project_simplex(v: np.ndarray) -> np.ndarray:
    y = np.clip(np.asarray(v, float), 1e-12, None)
    return y / y.sum()


def _rollout(state: np.ndarray, t0: int, horizon: int, transition) -> np.ndarray:
    x = np.asarray(state, float).copy()
    for k in range(int(horizon)):
        x = np.asarray(transition(x, int(t0 + k)), float)
    return _project_simplex(x)


def finite_horizon_invariants(
    trajectory: np.ndarray,
    transition,
    *,
    horizons: tuple[int, int] = (5, 20),
    sample_points: int = 6,
    perturb_eps: float = 1e-3,
    intervention_scale: float = 0.06,
) -> dict[str, float]:
    """Compute multi-step response-memory and intervention-spread statistics.

    At evenly spaced points on the observed path, two fixed simplex-tangent
    perturbations probe state-memory amplification. Four fixed logit-space
    interventions probe how widely alternative controlled futures separate.
    The same probes are used for every dynamical class.
    """
    x = _validate(trajectory)
    h1, h2 = (int(horizons[0]), int(horizons[1]))
    if h1 < 1 or h2 <= h1:
        raise ValueError("horizons must satisfy 1 <= h1 < h2")
    if perturb_eps <= 0 or intervention_scale <= 0:
        raise ValueError("probe scales must be positive")

    e1 = np.array([1.0, -1.0, 0.0]) / np.sqrt(2.0)
    e2 = np.array([1.0, 1.0, -2.0]) / np.sqrt(6.0)
    tangent_dirs = (e1, e2)
    action_dirs = (
        np.array([1.0, -1.0, 0.0]),
        np.array([-1.0, 1.0, 0.0]),
        np.array([0.0, 1.0, -1.0]),
        np.array([0.0, -1.0, 1.0]),
    )
    idx = np.unique(np.linspace(0, len(x) - 2, min(sample_points, len(x) - 1), dtype=int))

    mem: dict[int, list[float]] = {h1: [], h2: []}
    mem_anis: dict[int, list[float]] = {h1: [], h2: []}
    spread: dict[int, list[float]] = {h1: [], h2: []}
    spread_sd: dict[int, list[float]] = {h1: [], h2: []}

    for t in idx:
        state = x[t]
        for h in (h1, h2):
            base = _rollout(state, int(t), h, transition)

            amps = []
            for d in tangent_dirs:
                zp = _project_simplex(state + perturb_eps * d)
                fp = _rollout(zp, int(t), h, transition)
                amps.append(float(np.linalg.norm(fp - base) / max(np.linalg.norm(zp - state), 1e-12)))
            mem[h].append(float(np.mean(amps)))
            mem_anis[h].append(float((max(amps) - min(amps)) / max(max(amps) + min(amps), 1e-12)))

            dists = []
            for d in action_dirs:
                controlled = apply_multichannel_action(state, intervention_scale * d)
                future = _rollout(controlled, int(t), h, transition)
                dists.append(float(np.linalg.norm(future - base)))
            spread[h].append(float(np.mean(dists)))
            spread_sd[h].append(float(np.std(dists)))

    m1, m2 = float(np.mean(mem[h1])), float(np.mean(mem[h2]))
    s1, s2 = float(np.mean(spread[h1])), float(np.mean(spread[h2]))
    return {
        f"fh_memory_amplification_h{h1}": m1,
        f"fh_memory_amplification_h{h2}": m2,
        f"fh_memory_anisotropy_h{h1}": float(np.mean(mem_anis[h1])),
        f"fh_memory_anisotropy_h{h2}": float(np.mean(mem_anis[h2])),
        f"fh_action_spread_h{h1}": s1,
        f"fh_action_spread_h{h2}": s2,
        f"fh_action_spread_sd_h{h1}": float(np.mean(spread_sd[h1])),
        f"fh_action_spread_sd_h{h2}": float(np.mean(spread_sd[h2])),
        "fh_memory_persistence_ratio": float(m2 / max(m1, 1e-12)),
        "fh_action_persistence_ratio": float(s2 / max(s1, 1e-12)),
    }
