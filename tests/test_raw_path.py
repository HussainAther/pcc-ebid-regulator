import numpy as np
from pcc_ebid_regulator.raw_path import raw_path_features, recurrence_rate

def test_raw_path_features_finite_and_nonentropy():
    t=np.linspace(0,2*np.pi,100)
    x=np.column_stack([1/3+.08*np.cos(t),1/3+.08*np.cos(t-2*np.pi/3),1/3+.08*np.cos(t+2*np.pi/3)])
    f=raw_path_features(x)
    assert len(f)==8
    assert all(np.isfinite(list(f.values())))
    assert not any('entropy' in k or 'ebid' in k for k in f)
    assert f['raw_path_length']>f['raw_net_displacement']
    assert f['raw_spectral_concentration']>0

def test_recurrence_higher_for_returning_path_than_line():
    t=np.linspace(0,2*np.pi,100)
    loop=np.column_stack([1/3+.08*np.cos(t),1/3+.08*np.cos(t-2*np.pi/3),1/3+.08*np.cos(t+2*np.pi/3)])
    a=np.linspace(0,1,100);line=np.column_stack([.6-.3*a,.2+.15*a,.2+.15*a])
    assert recurrence_rate(loop)>recurrence_rate(line)
