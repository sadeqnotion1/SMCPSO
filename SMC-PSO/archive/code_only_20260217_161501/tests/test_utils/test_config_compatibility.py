"""
================================================================================
Unit Tests for Configuration Compatibility Module
================================================================================

Unit tests for src/utils/config_compatibility.py

Tests cover:
1. AttributeDictionary class (dict/attribute access)
2. ensure_attribute_access function
3. ensure_dict_access function
4. wrap_physics_config function
5. validate_physics_config function
6. create_minimal_physics_config function

Author: DIP_SMC_PSO Team
Created: December 21, 2025 (Session 15 - Push to 20% Coverage)
"""

import pytest
import warnings
from src.utils.config_compatibility import (
    AttributeDictionary,
    ensure_attribute_access,
    ensure_dict_access,
    wrap_physics_config,
    validate_physics_config,
    create_minimal_physics_config,
    ConfigCompatibilityMixin,
    REQUIRED_PHYSICS_PARAMS,
)


# =============================================================================
# Test AttributeDictionary Class
# =============================================================================

def test_attribute_dict_init():
    """Initialize AttributeDictionary with data."""
    data = {'a': 1, 'b': 2}
    ad = AttributeDictionary(data)
    assert ad._data == data


def test_attribute_dict_getattr():
    """Access dictionary values via attribute notation."""
    ad = AttributeDictionary({'foo': 'bar', 'num': 42})
    assert ad.foo == 'bar'
    assert ad.num == 42


def test_attribute_dict_getitem():
    """Access dictionary values via item notation."""
    ad = AttributeDictionary({'foo': 'bar', 'num': 42})
    assert ad['foo'] == 'bar'
    assert ad['num'] == 42


def test_attribute_dict_setattr():
    """Set values via attribute notation."""
    ad = AttributeDictionary({})
    ad.new_key = 'new_value'
    assert ad.new_key == 'new_value'
    assert ad['new_key'] == 'new_value'


def test_attribute_dict_setitem():
    """Set values via item notation."""
    ad = AttributeDictionary({})
    ad['new_key'] = 'new_value'
    assert ad['new_key'] == 'new_value'
    assert ad.new_key == 'new_value'


def test_attribute_dict_contains():
    """Check if key exists."""
    ad = AttributeDictionary({'a': 1, 'b': 2})
    assert 'a' in ad
    assert 'c' not in ad


def test_attribute_dict_get():
    """Get value with default."""
    ad = AttributeDictionary({'a': 1})
    assert ad.get('a') == 1
    assert ad.get('missing') is None
    assert ad.get('missing', 'default') == 'default'


def test_attribute_dict_keys():
    """Get dictionary keys."""
    ad = AttributeDictionary({'a': 1, 'b': 2})
    keys = list(ad.keys())
    assert set(keys) == {'a', 'b'}


def test_attribute_dict_values():
    """Get dictionary values."""
    ad = AttributeDictionary({'a': 1, 'b': 2})
    values = list(ad.values())
    assert set(values) == {1, 2}


def test_attribute_dict_items():
    """Get dictionary items."""
    ad = AttributeDictionary({'a': 1, 'b': 2})
    items = dict(ad.items())
    assert items == {'a': 1, 'b': 2}


def test_attribute_dict_to_dict():
    """Convert back to plain dictionary."""
    data = {'a': 1, 'b': 2}
    ad = AttributeDictionary(data)
    result = ad.to_dict()

    assert result == data
    assert result is not data  # Should be a copy


def test_attribute_dict_repr():
    """String representation."""
    ad = AttributeDictionary({'a': 1})
    repr_str = repr(ad)
    assert 'AttributeDictionary' in repr_str
    assert "'a': 1" in repr_str


def test_attribute_dict_missing_attribute_raises():
    """Accessing missing attribute should raise AttributeError."""
    ad = AttributeDictionary({'a': 1})
    with pytest.raises(AttributeError, match="object has no attribute 'missing'"):
        _ = ad.missing


def test_attribute_dict_internal_attribute_raises():
    """Accessing internal attribute should raise AttributeError."""
    ad = AttributeDictionary({'a': 1})
    with pytest.raises(AttributeError):
        _ = ad._nonexistent


# =============================================================================
# Test ensure_attribute_access Function
# =============================================================================

def test_ensure_attribute_access_none():
    """None should return None."""
    result = ensure_attribute_access(None)
    assert result is None


def test_ensure_attribute_access_dict():
    """Dictionary should be wrapped in AttributeDictionary."""
    data = {'a': 1, 'b': 2}
    result = ensure_attribute_access(data)

    assert isinstance(result, AttributeDictionary)
    assert result.a == 1
    assert result['b'] == 2


def test_ensure_attribute_access_object():
    """Object with __dict__ should pass through."""
    class TestConfig:
        def __init__(self):
            self.a = 1
            self.b = 2

    config = TestConfig()
    result = ensure_attribute_access(config)

    assert result is config  # Should be same object


def test_ensure_attribute_access_attribute_dict():
    """AttributeDictionary should pass through."""
    ad = AttributeDictionary({'a': 1})
    result = ensure_attribute_access(ad)

    assert result is ad  # Should pass through unchanged


# =============================================================================
# Test ensure_dict_access Function
# =============================================================================

def test_ensure_dict_access_none():
    """None should return empty dict."""
    result = ensure_dict_access(None)
    assert result == {}


def test_ensure_dict_access_dict():
    """Dictionary should pass through."""
    data = {'a': 1, 'b': 2}
    result = ensure_dict_access(data)

    assert result is data  # Should be same dict


def test_ensure_dict_access_attribute_dict():
    """AttributeDictionary should convert to dict."""
    ad = AttributeDictionary({'a': 1, 'b': 2})
    result = ensure_dict_access(ad)

    assert isinstance(result, dict)
    assert result == {'a': 1, 'b': 2}


def test_ensure_dict_access_pydantic_model():
    """Object with model_dump should use it."""
    class MockPydanticModel:
        def model_dump(self):
            return {'a': 1, 'b': 2}

    model = MockPydanticModel()
    result = ensure_dict_access(model)

    assert result == {'a': 1, 'b': 2}


def test_ensure_dict_access_object_with_dict_method():
    """Object with dict() method should use it."""
    class MockConfigWithDict:
        def dict(self):
            return {'a': 1, 'b': 2}

    config = MockConfigWithDict()
    result = ensure_dict_access(config)

    assert result == {'a': 1, 'b': 2}


def test_ensure_dict_access_object_with_dict_attr():
    """Object with __dict__ should use it."""
    class SimpleConfig:
        def __init__(self):
            self.a = 1
            self.b = 2

    config = SimpleConfig()
    result = ensure_dict_access(config)

    assert result == {'a': 1, 'b': 2}


def test_ensure_dict_access_unconvertible_type():
    """Unconvertible type should warn and return empty dict."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = ensure_dict_access(42)  # int cannot convert to dict

        assert len(w) == 1
        assert "Could not convert" in str(w[0].message)
        assert result == {}


# =============================================================================
# Test wrap_physics_config Function
# =============================================================================

def test_wrap_physics_config_dict():
    """Wrap dictionary physics config."""
    config = {'cart_mass': 2.0, 'pendulum1_mass': 0.2}
    result = wrap_physics_config(config)

    # Should be AttributeDictionary
    assert hasattr(result, 'cart_mass')
    assert result.cart_mass == 2.0

    # Should have defaults added
    assert hasattr(result, 'gravity')
    assert result.gravity == 9.81


def test_wrap_physics_config_parameter_mapping():
    """Test regularization parameter mapping."""
    config = {'regularization': 1e-6}
    result = wrap_physics_config(config)

    # Should map regularization → regularization_alpha
    assert result.regularization_alpha == 1e-6


def test_wrap_physics_config_defaults():
    """Test default parameters are added."""
    config = {}
    result = wrap_physics_config(config)

    # Required physics parameters
    assert result.cart_mass == 1.0
    assert result.pendulum1_mass == 0.1
    assert result.pendulum2_mass == 0.1
    assert result.pendulum1_length == 0.5
    assert result.pendulum2_length == 0.5
    assert result.gravity == 9.81

    # Advanced parameters
    assert result.regularization_alpha == 1e-8
    assert result.max_condition_number == 1e12
    assert result.include_coriolis_effects is True


def test_wrap_physics_config_preserves_existing():
    """Test existing parameters are preserved."""
    config = {'cart_mass': 5.0, 'gravity': 10.0}
    result = wrap_physics_config(config)

    # Should preserve custom values
    assert result.cart_mass == 5.0
    assert result.gravity == 10.0

    # Should still add missing defaults
    assert result.pendulum1_mass == 0.1


# =============================================================================
# Test validate_physics_config Function
# =============================================================================

def test_validate_physics_config_valid_dict():
    """Valid dictionary configuration should pass."""
    config = {
        'cart_mass': 1.0,
        'pendulum1_mass': 0.1,
        'pendulum2_mass': 0.1,
        'pendulum1_length': 0.5,
        'pendulum2_length': 0.5,
        'pendulum1_com': 0.25,
        'pendulum2_com': 0.25,
        'pendulum1_inertia': 0.01,
        'pendulum2_inertia': 0.01,
        'gravity': 9.81,
    }

    assert validate_physics_config(config) is True


def test_validate_physics_config_valid_object():
    """Valid object configuration should pass."""
    config = AttributeDictionary({
        'cart_mass': 1.0,
        'pendulum1_mass': 0.1,
        'pendulum2_mass': 0.1,
        'pendulum1_length': 0.5,
        'pendulum2_length': 0.5,
        'pendulum1_com': 0.25,
        'pendulum2_com': 0.25,
        'pendulum1_inertia': 0.01,
        'pendulum2_inertia': 0.01,
        'gravity': 9.81,
    })

    assert validate_physics_config(config) is True


def test_validate_physics_config_missing_param():
    """Configuration missing required parameter should fail."""
    config = {
        'cart_mass': 1.0,
        'pendulum1_mass': 0.1,
        # Missing other required params
    }

    assert validate_physics_config(config) is False


def test_validate_physics_config_required_params_set():
    """REQUIRED_PHYSICS_PARAMS should have expected parameters."""
    expected_params = {
        'cart_mass', 'pendulum1_mass', 'pendulum2_mass',
        'pendulum1_length', 'pendulum2_length',
        'pendulum1_com', 'pendulum2_com',
        'pendulum1_inertia', 'pendulum2_inertia',
        'gravity'
    }

    assert REQUIRED_PHYSICS_PARAMS == expected_params


# =============================================================================
# Test create_minimal_physics_config Function
# =============================================================================

def test_create_minimal_physics_config():
    """Create minimal configuration with defaults."""
    config = create_minimal_physics_config()

    # Should be AttributeDictionary
    assert isinstance(config, AttributeDictionary)

    # Should have all required physics parameters
    assert validate_physics_config(config) is True

    # Check specific defaults
    assert config.cart_mass == 1.0
    assert config.pendulum1_mass == 0.1
    assert config.gravity == 9.81
    assert config.regularization_alpha == 1e-8


def test_create_minimal_physics_config_attribute_access():
    """Minimal config should support attribute access."""
    config = create_minimal_physics_config()

    # Can access via attributes
    assert config.cart_mass == 1.0
    assert config.gravity == 9.81


def test_create_minimal_physics_config_dict_access():
    """Minimal config should support dictionary access."""
    config = create_minimal_physics_config()

    # Can access via dictionary
    assert config['cart_mass'] == 1.0
    assert config['gravity'] == 9.81


# =============================================================================
# Test ConfigCompatibilityMixin
# =============================================================================

def test_config_compatibility_mixin_ensure_config():
    """ConfigCompatibilityMixin should have compatibility methods."""
    class TestClass(ConfigCompatibilityMixin):
        pass

    obj = TestClass()

    # Test ensure_config_compatibility
    dict_config = {'a': 1, 'b': 2}
    result = obj._ensure_config_compatibility(dict_config)
    assert isinstance(result, AttributeDictionary)
    assert result.a == 1


def test_config_compatibility_mixin_ensure_dict():
    """ConfigCompatibilityMixin should convert to dict."""
    class TestClass(ConfigCompatibilityMixin):
        pass

    obj = TestClass()

    # Test _ensure_config_dict
    attr_dict = AttributeDictionary({'a': 1, 'b': 2})
    result = obj._ensure_config_dict(attr_dict)
    assert isinstance(result, dict)
    assert result == {'a': 1, 'b': 2}


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
