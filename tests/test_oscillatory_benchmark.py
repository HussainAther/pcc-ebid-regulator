import numpy as np
from pcc_ebid_regulator.oscillatory_benchmark import REGIMES, oscillatory_bias, oscillatory_step


def test_bias_is_zero_sum_and_periodic():
    for regime in REGIMES:
        b0 = oscillatory_bias(0, period=100, regime=regime)
        b1 = oscillatory_bias(100, period=100, regime=regime)
        assert abs(float(b0.sum())) < 1e-12
        assert np.allclose(b0, b1, atol=1e-12)


def test_step_stays_on_simplex():
    x = np.array([0.2, 0.3, 0.5])
    for regime in REGIMES:
        y = oscillatory_step(x, t=17, period=80, regime=regime, strength=2.0)
        assert np.all(y > 0)
        assert np.isclose(y.sum(), 1.0)


def test_regimes_are_not_identical():
    x = np.array([0.2, 0.3, 0.5])
    ys = [oscillatory_step(x, t=19, period=90, regime=r) for r in REGIMES]
    assert any(not np.allclose(ys[0], y) for y in ys[1:])
