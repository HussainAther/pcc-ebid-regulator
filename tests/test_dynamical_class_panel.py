from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('exp020',ROOT/'experiments'/'020_dynamical_class_panel'/'run.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

def test_panel_is_pre_specified_five_classes():
    props=M.class_properties()
    assert [p['system'] for p in props]==['pcc','oscillatory_benchmark','damped_oscillator','directional_benchmark','neutral_diffusion']

def test_panel_ratios_are_frozen_survivors():
    assert M.RATIOS==[0.60,1.00]

def test_new_classes_use_eight_family_protocol():
    assert len(M.FAMILY_SEEDS)==8
