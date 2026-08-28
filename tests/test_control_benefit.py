import numpy as np
from pcc_ebid_regulator.control_benefit import greedy_control_benefit
from pcc_ebid_regulator.dynamics import step

def test_control_benefit_is_finite_and_bounded_above_one():
    tr=lambda x,h: step(x,strength=1.0,topology='canonical')
    out=greedy_control_benefit(np.array([0.6,0.25,0.15]),tr,horizon=8,cardinality=5)
    assert all(np.isfinite(v) for v in out.values())
    assert out['control_relative_benefit'] <= 1.0 + 1e-12

def test_oracle_not_worse_than_uncontrolled_for_centering_repertoire():
    tr=lambda x,h: step(x,strength=1.0,topology='canonical')
    out=greedy_control_benefit(np.array([0.55,0.30,0.15]),tr,horizon=10,cardinality=9)
    assert out['control_oracle_error'] <= out['control_uncontrolled_error'] + 1e-12
