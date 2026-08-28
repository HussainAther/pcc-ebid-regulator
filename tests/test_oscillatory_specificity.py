import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('exp019',ROOT/'experiments'/'019_oscillatory_specificity'/'run.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

def test_locked_ratios():
    assert M.RATIOS == [0.60, 1.00]

def test_split_sizes_match_protocol():
    pmap=M.period_map(); rows=[]
    for fi in range(8): rows += M.build_family_ratio(fi,0.60,pmap)
    tr,te=M.split(rows,0.60,0)
    assert len(tr)==504
    assert len(te)==16
