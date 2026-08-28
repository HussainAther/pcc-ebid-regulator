import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('e18',ROOT/'experiments/018_nonpcc_specificity/run.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def test_locked_ratios(): assert m.RATIOS == [0.60,1.00]
def test_shared_period_ruler():
    p=m.period_map(); assert set(p)=={0.5,1.0,2.0,3.0}; assert all(v>0 for v in p.values())
def test_split_is_leave_family_out():
    rows=[]
    for fi in range(2):
      for si in range(2):
       for sig in [0.0,0.01]: rows.append({'target_cycle_ratio':0.6,'seed_family':fi,'structure_index':si,'noise_sigma':sig})
    tr,te=m.split(rows,0.6,0)
    assert all(int(r['seed_family'])!=0 and int(r['structure_index'])!=0 for r in tr)
    assert all(int(r['seed_family'])==0 and int(r['structure_index'])==0 for r in te)
