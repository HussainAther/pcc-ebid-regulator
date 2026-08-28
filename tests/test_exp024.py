from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_exp024_declares_unseen_class_primary_protocol():
    text=(ROOT/'experiments/024_finite_horizon_controllability/run.py').read_text()
    assert 'heldout_system' in text
    assert 'finite_horizon_invariants' in text
    assert 'relative_mae_reduction' in text

def test_exp024_feature_names_exclude_ebid_entropy():
    text=(ROOT/'experiments/024_finite_horizon_controllability/run.py').read_text()
    start=text.index('FH_KEYS=[');end=text.index('META_KEYS=',start)
    block=text[start:end].lower()
    assert 'ebid' not in block
    assert 'entropy' not in block
