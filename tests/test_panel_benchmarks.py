import numpy as np
import pytest
from pcc_ebid_regulator.panel_benchmarks import (
    damped_oscillatory_step, damped_activity, neutral_step, neutral_activity,
)


def test_damped_step_stays_on_simplex():
    x=np.array([0.5,0.3,0.2])
    y=damped_oscillatory_step(x,t=20,period=300,regime='circular')
    assert y.shape==(3,)
    assert np.all(y>0)
    assert np.isclose(y.sum(),1.0)


def test_damping_reduces_activity_over_matching_phase():
    x=np.array([0.5,0.3,0.2]); p=200
    a0=damped_activity(x,t=0,period=p,regime='circular',strength=1.5)
    a2=damped_activity(x,t=2*p,period=p,regime='circular',strength=1.5)
    assert a2 < a0


def test_neutral_step_is_identity_on_simplex():
    x=np.array([0.5,0.3,0.2])
    y=neutral_step(x,regime='neutral_c')
    assert np.allclose(x,y)
    assert neutral_activity(x,regime='neutral_c')==0.0


def test_invalid_regime_rejected():
    with pytest.raises(ValueError):
        neutral_step(np.ones(3)/3,regime='bad')
