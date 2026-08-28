import importlib.util
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('exp021',ROOT/'experiments'/'021_trajectory_statistics'/'run.py'); M=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(M)

def test_panel_has_all_80_fold_cells():
    p=M.build_panel(); assert len(p)==5*2*8
    assert set(r['system'] for r in p)==set(M.DATASETS)

def test_no_ebid_features_in_descriptor_set():
    assert all('ebid' not in d.lower() and 'entropy' not in d.lower() for d in M.DESC)

def test_descriptors_finite():
    p=M.build_panel()
    for r in p:
        for d in M.DESC: assert np.isfinite(float(r[d]))

def test_class_cv_holds_out_entire_class():
    p=M.build_panel();preds,_=M.class_cv(p)
    assert len(preds)==80
    assert all('heldout_system' in r for r in preds)
