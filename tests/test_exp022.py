from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('exp022',ROOT/'experiments'/'022_raw_path_invariants'/'run.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

def test_exp022_is_prospective_five_class_panel():
    assert M.SYSTEMS==['pcc','oscillatory_benchmark','damped_oscillator','directional_benchmark','neutral_diffusion']
    assert M.RATIOS==[0.60,1.00]
    assert len(M.FAMILY_SEEDS)==4

def test_exp022_explanatory_features_exclude_ebid_entropy():
    assert len(M.RAW_KEYS)==8
    assert all('ebid' not in k and 'entropy' not in k for k in M.RAW_KEYS)

def test_exp022_primary_protocol_is_leave_class_out_compatible():
    dummy=[]
    for s in M.SYSTEMS:
      for f in range(4):
        for r in M.RATIOS:
          row={'system':s,'heldout_family':f,'target_cycle_ratio':r,'relative_mae_reduction':0.1}
          for k in M.META_KEYS: row[k]=0.2+0.01*f
          dummy.append(row)
    p,q=M.class_cv(dummy)
    assert len(p)==len(dummy)
    assert q[-1]['heldout_system']=='ALL'
