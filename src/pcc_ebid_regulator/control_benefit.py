"""Standardized finite-horizon control-benefit targets for Experiment 025."""
from __future__ import annotations
import numpy as np
from .regulators import apply_multichannel_action, matched_directional_repertoire

TARGET = np.full(3, 1.0/3.0)

def squared_error(state: np.ndarray, target: np.ndarray = TARGET) -> float:
    d=np.asarray(state,float)-np.asarray(target,float)
    return float(d@d)

def greedy_control_benefit(
    initial: np.ndarray,
    transition,
    *,
    horizon: int = 40,
    cardinality: int = 9,
    max_action: float = 0.06,
    channels: tuple[int,...]=(0,1),
    target: np.ndarray = TARGET,
) -> dict[str,float]:
    """Compare uncontrolled future with a standardized oracle-controlled future.

    ``transition(state, future_step)`` must provide the correct deterministic
    one-step dynamics for the class/regime being probed. The regulator uses the
    same fixed action repertoire for every dynamical class.
    """
    if horizon < 1: raise ValueError("horizon must be >= 1")
    x0=np.asarray(initial,float)
    if x0.shape!=(3,): raise ValueError("initial must have shape (3,)")
    actions=matched_directional_repertoire(channels,cardinality=cardinality,max_action=max_action)
    xu=x0.copy(); xc=x0.copy(); ue=[]; ce=[]
    for h in range(horizon):
        xu=transition(xu,h); ue.append(squared_error(xu,target))
        best=None
        for a in actions:
            z=apply_multichannel_action(xc,a)
            pred=transition(z,h)
            score=squared_error(pred,target)
            if best is None or score < best[0]: best=(score,pred)
        assert best is not None
        xc=best[1]; ce.append(best[0])
    u=float(np.mean(ue)); c=float(np.mean(ce)); benefit=u-c
    return {
        'control_uncontrolled_error':u,
        'control_oracle_error':c,
        'control_absolute_benefit':benefit,
        'control_relative_benefit':float(benefit/max(u,1e-12)),
        'control_final_uncontrolled_error':float(ue[-1]),
        'control_final_oracle_error':float(ce[-1]),
    }
