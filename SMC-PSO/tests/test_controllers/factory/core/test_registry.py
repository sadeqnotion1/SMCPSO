#======================================================================================\\
#============= tests/test_controllers/factory/core/test_registry.py ==================\\
#======================================================================================\\

"""
Comprehensive tests for controller registry management.

Tests registry access functions, controller metadata, aliases, and validation.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.controllers.factory.registry import (
    CONTROLLER_REGISTRY,
    CONTROLLER_ALIASES,
    get_controller_info,
    canonicalize_controller_type,
    list_available_controllers,
    get_controllers_by_category,
    get_controllers_by_complexity,
    get_default_gains,
    get_gain_bounds,
    validate_controller_type,
)


class TestControllerRegistry:
    """Test suite for controller registry structure and access."""

    def test_registry_has_expected_controllers(self):
        """Test that registry contains the expected core controllers."""
        expected_controllers = [
            'classical_smc',
            'sta_smc',
            'adaptive_smc',
            'hybrid_adaptive_sta_smc'
        ]

        for controller in expected_controllers:
            assert controller in CONTROLLER_REGISTRY, f"Missing controller: {controller}"

    def test_registry_entries_have_required_fields(self):
        """Test that all registry entries have required metadata fields."""
        required_fields = [
            'class',
            'config_class',
            'default_gains',
            'gain_count',
            'gain_structure',
            'description',
            'supports_dynamics',
            'required_params',
            'gain_bounds',
            'stability_margin',
            'category',
            'complexity'
        ]

        for controller_name, controller_info in CONTROLLER_REGISTRY.items():
            for field in required_fields:
                assert field in controller_info, \
                    f"Controller {controller_name} missing field: {field}"

    def test_controller_aliases_map_to_valid_controllers(self):
        """Test that all aliases map to valid controllers in registry."""
        for alias, canonical in CONTROLLER_ALIASES.items():
            assert canonical in CONTROLLER_REGISTRY, \
                f"Alias {alias} maps to invalid controller: {canonical}"


class TestGetControllerInfo:
    """Test suite for get_controller_info function."""

    def test_get_controller_info_classical_smc(self):
        """Test retrieving classical_smc controller info."""
        info = get_controller_info('classical_smc')

        assert info['gain_count'] == 6
        assert info['category'] == 'classical'
        assert info['complexity'] == 'medium'
        assert len(info['default_gains']) == 6
        assert info['supports_dynamics'] is True

    def test_get_controller_info_sta_smc(self):
        """Test retrieving sta_smc controller info."""
        info = get_controller_info('sta_smc')

        assert info['gain_count'] == 6
        assert info['category'] == 'advanced'
        assert info['complexity'] == 'high'
        assert len(info['default_gains']) == 6

    def test_get_controller_info_adaptive_smc(self):
        """Test retrieving adaptive_smc controller info."""
        info = get_controller_info('adaptive_smc')

        assert info['gain_count'] == 5
        assert info['category'] == 'adaptive'
        assert info['complexity'] == 'high'
        assert len(info['default_gains']) == 5

    def test_get_controller_info_hybrid(self):
        """Test retrieving hybrid controller info."""
        info = get_controller_info('hybrid_adaptive_sta_smc')

        assert info['gain_count'] == 4
        assert info['category'] == 'hybrid'
        assert info['complexity'] == 'very_high'
        assert info['supports_dynamics'] is False

    def test_get_controller_info_returns_copy(self):
        """Test that get_controller_info returns a copy, not reference."""
        info1 = get_controller_info('classical_smc')
        info2 = get_controller_info('classical_smc')

        # Modify first copy
        info1['modified'] = True

        # Second copy should be unaffected
        assert 'modified' not in info2

    def test_get_controller_info_invalid_type_raises_error(self):
        """Test that invalid controller type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown controller type"):
            get_controller_info('nonexistent_controller')

    def test_get_controller_info_non_string_raises_typeerror(self):
        """Test that non-string controller type raises TypeError."""
        with pytest.raises(TypeError, match="Controller type must be string"):
            get_controller_info(123)

    def test_get_controller_info_error_message_lists_available(self):
        """Test that error message includes list of available controllers."""
        try:
            get_controller_info('invalid')
            pytest.fail("Expected ValueError")
        except ValueError as e:
            error_msg = str(e)
            assert 'classical_smc' in error_msg
            assert 'Available' in error_msg


class TestCanonicalizeControllerType:
    """Test suite for canonicalize_controller_type function."""

    def test_canonicalize_standard_name(self):
        """Test canonicalizing standard controller name."""
        result = canonicalize_controller_type('classical_smc')
        assert result == 'classical_smc'

    def test_canonicalize_alias_classic_smc(self):
        """Test canonicalizing 'classic_smc' alias."""
        result = canonicalize_controller_type('classic_smc')
        assert result == 'classical_smc'

    def test_canonicalize_alias_super_twisting(self):
        """Test canonicalizing 'super_twisting' alias."""
        result = canonicalize_controller_type('super_twisting')
        assert result == 'sta_smc'

    def test_canonicalize_alias_sta(self):
        """Test canonicalizing 'sta' alias."""
        result = canonicalize_controller_type('sta')
        assert result == 'sta_smc'

    def test_canonicalize_alias_adaptive(self):
        """Test canonicalizing 'adaptive' alias."""
        result = canonicalize_controller_type('adaptive')
        assert result == 'adaptive_smc'

    def test_canonicalize_alias_hybrid(self):
        """Test canonicalizing 'hybrid' alias."""
        result = canonicalize_controller_type('hybrid')
        assert result == 'hybrid_adaptive_sta_smc'

    def test_canonicalize_uppercase(self):
        """Test canonicalizing uppercase names."""
        result = canonicalize_controller_type('CLASSICAL_SMC')
        assert result == 'classical_smc'

    def test_canonicalize_mixed_case(self):
        """Test canonicalizing mixed case names."""
        result = canonicalize_controller_type('Classical_SMC')
        assert result == 'classical_smc'

    def test_canonicalize_with_spaces(self):
        """Test canonicalizing names with spaces."""
        result = canonicalize_controller_type('classical smc')
        assert result == 'classical_smc'

    def test_canonicalize_with_hyphens(self):
        """Test canonicalizing names with hyphens."""
        result = canonicalize_controller_type('classical-smc')
        assert result == 'classical_smc'

    def test_canonicalize_with_leading_trailing_spaces(self):
        """Test canonicalizing names with leading/trailing spaces."""
        result = canonicalize_controller_type('  classical_smc  ')
        assert result == 'classical_smc'

    def test_canonicalize_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Controller type cannot be empty"):
            canonicalize_controller_type('')

    def test_canonicalize_whitespace_only_raises_error(self):
        """Test that whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="Controller type cannot be empty"):
            canonicalize_controller_type('   ')

    def test_canonicalize_non_string_raises_error(self):
        """Test that non-string input raises ValueError."""
        with pytest.raises(ValueError, match="Controller type must be string"):
            canonicalize_controller_type(123)

    def test_canonicalize_none_raises_error(self):
        """Test that None input raises ValueError."""
        with pytest.raises(ValueError, match="Controller type must be string"):
            canonicalize_controller_type(None)


class TestListAvailableControllers:
    """Test suite for list_available_controllers function."""

    def test_list_available_controllers_returns_list(self):
        """Test that function returns a list."""
        result = list_available_controllers()
        assert isinstance(result, list)

    def test_list_available_controllers_contains_expected(self):
        """Test that list contains expected controllers."""
        result = list_available_controllers()

        expected = ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']
        for controller in expected:
            assert controller in result

    def test_list_available_controllers_is_sorted(self):
        """Test that returned list is sorted."""
        result = list_available_controllers()
        assert result == sorted(result)

    def test_list_available_controllers_no_duplicates(self):
        """Test that list has no duplicates."""
        result = list_available_controllers()
        assert len(result) == len(set(result))


class TestGetControllersByCategory:
    """Test suite for get_controllers_by_category function."""

    def test_get_controllers_by_category_classical(self):
        """Test getting classical category controllers."""
        result = get_controllers_by_category('classical')
        assert 'classical_smc' in result

    def test_get_controllers_by_category_advanced(self):
        """Test getting advanced category controllers."""
        result = get_controllers_by_category('advanced')
        assert 'sta_smc' in result

    def test_get_controllers_by_category_adaptive(self):
        """Test getting adaptive category controllers."""
        result = get_controllers_by_category('adaptive')
        assert 'adaptive_smc' in result

    def test_get_controllers_by_category_hybrid(self):
        """Test getting hybrid category controllers."""
        result = get_controllers_by_category('hybrid')
        assert 'hybrid_adaptive_sta_smc' in result

    def test_get_controllers_by_category_nonexistent(self):
        """Test getting controllers from nonexistent category."""
        result = get_controllers_by_category('nonexistent')
        assert result == []

    def test_get_controllers_by_category_returns_list(self):
        """Test that function returns a list."""
        result = get_controllers_by_category('classical')
        assert isinstance(result, list)


class TestGetControllersByComplexity:
    """Test suite for get_controllers_by_complexity function."""

    def test_get_controllers_by_complexity_medium(self):
        """Test getting medium complexity controllers."""
        result = get_controllers_by_complexity('medium')
        assert 'classical_smc' in result

    def test_get_controllers_by_complexity_high(self):
        """Test getting high complexity controllers."""
        result = get_controllers_by_complexity('high')
        assert 'sta_smc' in result
        assert 'adaptive_smc' in result

    def test_get_controllers_by_complexity_very_high(self):
        """Test getting very_high complexity controllers."""
        result = get_controllers_by_complexity('very_high')
        assert 'hybrid_adaptive_sta_smc' in result

    def test_get_controllers_by_complexity_nonexistent(self):
        """Test getting controllers with nonexistent complexity."""
        result = get_controllers_by_complexity('nonexistent')
        assert result == []

    def test_get_controllers_by_complexity_returns_list(self):
        """Test that function returns a list."""
        result = get_controllers_by_complexity('high')
        assert isinstance(result, list)


class TestGetDefaultGains:
    """Test suite for get_default_gains function."""

    def test_get_default_gains_classical_smc(self):
        """Test getting default gains for classical_smc."""
        gains = get_default_gains('classical_smc')

        assert isinstance(gains, list)
        assert len(gains) == 6
        assert all(isinstance(g, (int, float)) for g in gains)

    def test_get_default_gains_sta_smc(self):
        """Test getting default gains for sta_smc."""
        gains = get_default_gains('sta_smc')

        assert isinstance(gains, list)
        assert len(gains) == 6

    def test_get_default_gains_adaptive_smc(self):
        """Test getting default gains for adaptive_smc."""
        gains = get_default_gains('adaptive_smc')

        assert isinstance(gains, list)
        assert len(gains) == 5

    def test_get_default_gains_hybrid(self):
        """Test getting default gains for hybrid controller."""
        gains = get_default_gains('hybrid_adaptive_sta_smc')

        assert isinstance(gains, list)
        assert len(gains) == 4

    def test_get_default_gains_returns_copy(self):
        """Test that get_default_gains returns a copy."""
        gains1 = get_default_gains('classical_smc')
        gains2 = get_default_gains('classical_smc')

        # Modify first copy
        gains1[0] = 999.0

        # Second copy should be unaffected
        assert gains2[0] != 999.0

    def test_get_default_gains_invalid_controller_raises_error(self):
        """Test that invalid controller raises ValueError."""
        with pytest.raises(ValueError, match="Unknown controller type"):
            get_default_gains('nonexistent')


class TestGetGainBounds:
    """Test suite for get_gain_bounds function."""

    def test_get_gain_bounds_classical_smc(self):
        """Test getting gain bounds for classical_smc."""
        bounds = get_gain_bounds('classical_smc')

        assert isinstance(bounds, list)
        assert len(bounds) == 6
        assert all(isinstance(b, tuple) and len(b) == 2 for b in bounds)

    def test_get_gain_bounds_sta_smc(self):
        """Test getting gain bounds for sta_smc."""
        bounds = get_gain_bounds('sta_smc')

        assert isinstance(bounds, list)
        assert len(bounds) == 6

    def test_get_gain_bounds_adaptive_smc(self):
        """Test getting gain bounds for adaptive_smc."""
        bounds = get_gain_bounds('adaptive_smc')

        assert isinstance(bounds, list)
        assert len(bounds) == 5

    def test_get_gain_bounds_hybrid(self):
        """Test getting gain bounds for hybrid controller."""
        bounds = get_gain_bounds('hybrid_adaptive_sta_smc')

        assert isinstance(bounds, list)
        assert len(bounds) == 4

    def test_get_gain_bounds_returns_copy(self):
        """Test that get_gain_bounds returns a copy."""
        bounds1 = get_gain_bounds('classical_smc')
        bounds2 = get_gain_bounds('classical_smc')

        # Modify first copy
        bounds1[0] = (0.0, 999.0)

        # Second copy should be unaffected
        assert bounds2[0] != (0.0, 999.0)

    def test_get_gain_bounds_invalid_controller_raises_error(self):
        """Test that invalid controller raises ValueError."""
        with pytest.raises(ValueError, match="Unknown controller type"):
            get_gain_bounds('nonexistent')

    def test_get_gain_bounds_structure_valid(self):
        """Test that bounds have valid (lower, upper) structure."""
        bounds = get_gain_bounds('classical_smc')

        for lower, upper in bounds:
            assert isinstance(lower, (int, float))
            assert isinstance(upper, (int, float))
            assert lower < upper, f"Lower bound {lower} should be less than upper {upper}"


class TestValidateControllerType:
    """Test suite for validate_controller_type function."""

    def test_validate_controller_type_valid_canonical(self):
        """Test validation of valid canonical controller types."""
        assert validate_controller_type('classical_smc') is True
        assert validate_controller_type('sta_smc') is True
        assert validate_controller_type('adaptive_smc') is True
        assert validate_controller_type('hybrid_adaptive_sta_smc') is True

    def test_validate_controller_type_valid_alias(self):
        """Test validation of valid controller aliases."""
        assert validate_controller_type('classic_smc') is True
        assert validate_controller_type('super_twisting') is True
        assert validate_controller_type('sta') is True
        assert validate_controller_type('adaptive') is True
        assert validate_controller_type('hybrid') is True

    def test_validate_controller_type_case_insensitive(self):
        """Test validation is case-insensitive."""
        assert validate_controller_type('CLASSICAL_SMC') is True
        assert validate_controller_type('Classical_Smc') is True

    def test_validate_controller_type_with_spaces(self):
        """Test validation with spaces."""
        assert validate_controller_type('classical smc') is True
        assert validate_controller_type('  classical_smc  ') is True

    def test_validate_controller_type_invalid(self):
        """Test validation of invalid controller types."""
        assert validate_controller_type('nonexistent') is False
        assert validate_controller_type('invalid_controller') is False

    def test_validate_controller_type_empty_string(self):
        """Test validation of empty string."""
        assert validate_controller_type('') is False

    def test_validate_controller_type_non_string(self):
        """Test validation of non-string input."""
        assert validate_controller_type(123) is False
        assert validate_controller_type(None) is False
        assert validate_controller_type([]) is False


class TestMPCControllerRegistration:
    """Test suite for optional MPC controller registration."""

    def test_mpc_availability_is_boolean(self):
        """Test that MPC_AVAILABLE is a boolean flag."""
        from src.controllers.factory.registry import MPC_AVAILABLE
        assert isinstance(MPC_AVAILABLE, bool)

    def test_mpc_registration_consistent_with_availability(self):
        """Test that MPC registration is consistent with availability flag."""
        from src.controllers.factory.registry import MPC_AVAILABLE

        if MPC_AVAILABLE:
            # If MPC is available, it should be registered
            assert 'mpc_controller' in CONTROLLER_REGISTRY
        else:
            # If MPC is not available, it should not be registered
            assert 'mpc_controller' not in CONTROLLER_REGISTRY
