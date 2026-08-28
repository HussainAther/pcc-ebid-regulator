from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('exp023',ROOT/'experiments'/'023_response_invariants'/'run.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

def test_response_key_family_is_non_ebid():
    assert M.RESP_KEYS
    assert all('ebid' not in k.lower() and 'entropy' not in k.lower() for k in M.RESP_KEYS)

def test_locked_panel_and_scales():
    assert len(M.SYSTEMS)==5
    assert M.RATIOS==[0.60,1.00]
    assert list(M.FAMILIES)==[0,1,2,3]
