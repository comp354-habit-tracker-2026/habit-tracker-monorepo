import pytest
from activities.adapters.iactivity_adapter import IActivityAdapter

def test_interface_exists():
    assert IActivityAdapter is not None

def test_cannot_instantiate_interface():
    with pytest.raises(TypeError):
        IActivityAdapter()

def test_methods_exist():
    methods = dir(IActivityAdapter)
    assert "parse" in methods
    assert "get_provider_name" in methods
    assert "register_hooks" in methods