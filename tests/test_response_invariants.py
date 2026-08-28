import numpy as np
from pcc_ebid_regulator.response_invariants import (
    linear_forecast_error, innovation_variance, predictability_decay,
    local_response_features, response_invariants,
)


def smooth_path(n=80):
    t=np.linspace(0,2*np.pi,n)
    z=np.column_stack([1/3+0.08*np.cos(t),1/3+0.08*np.sin(t)])
    third=1-z.sum(axis=1)
    return np.column_stack([z,third])


def identity_step(x,t):
    return np.asarray(x,float)


def test_predictability_metrics_are_finite():
    x=smooth_path()
    for v in (linear_forecast_error(x), innovation_variance(x), predictability_decay(x)):
        assert np.isfinite(v)
        assert v >= 0


def test_identity_response_has_unitish_amplification():
    x=smooth_path()
    f=local_response_features(x,identity_step)
    assert 0.8 < f['resp_perturbation_amplification_mean'] < 1.2
    assert f['resp_jacobian_fro_mean'] > 0


def test_combined_features_have_expected_keys():
    f=response_invariants(smooth_path(),identity_step)
    assert 'resp_linear_forecast_error' in f
    assert 'resp_jacobian_fro_mean' in f
    assert len(f) == 8
