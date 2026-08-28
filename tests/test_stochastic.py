import numpy as np
from pcc_ebid_regulator.stochastic import perturb_simplex


def test_zero_noise_identity():
    x=np.array([0.2,0.3,0.5]); y=perturb_simplex(x,0.0,np.random.default_rng(1))
    assert np.allclose(x,y)


def test_perturbation_stays_on_simplex():
    x=np.array([0.2,0.3,0.5]); y=perturb_simplex(x,0.02,np.random.default_rng(2))
    assert np.all(y>0); assert np.isclose(y.sum(),1.0)


def test_negative_sigma_rejected():
    import pytest
    with pytest.raises(ValueError): perturb_simplex(np.ones(3)/3,-0.1,np.random.default_rng(1))
