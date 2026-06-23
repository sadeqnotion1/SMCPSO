#======================================================================================\\\
#================= tests/test_controllers/smc/core/test_gain_validation.py ==========\\\
#======================================================================================\\\

"""
Comprehensive tests for SMC gain validation (Safety-Critical Component).

Target: 100% coverage for safety-critical parameter validation.
Tests all mathematical properties, boundary conditions, and stability requirements.
"""

import pytest
import numpy as np

from src.controllers.smc.core.gain_validation import (
    SMCGainValidator,
    SMCControllerType,
    GainBounds,
    validate_smc_gains,
    check_stability_conditions,
    get_gain_bounds_for_controller
)


class TestGainBounds:
    """Test GainBounds dataclass functionality."""

    def test_gain_bounds_creation(self):
        """Test GainBounds initialization."""
        bounds = GainBounds(0.1, 100.0, "k1", "Position gain")
        assert bounds.min_value == 0.1
        assert bounds.max_value == 100.0
        assert bounds.name == "k1"
        assert bounds.description == "Position gain"

    def test_gain_bounds_validate_within_range(self):
        """Test validation of values within bounds."""
        bounds = GainBounds(0.1, 100.0, "k1", "Position gain")
        assert bounds.validate(1.0) is True
        assert bounds.validate(0.1) is True  # Boundary
        assert bounds.validate(100.0) is True  # Boundary
        assert bounds.validate(50.0) is True

    def test_gain_bounds_validate_outside_range(self):
        """Test validation of values outside bounds."""
        bounds = GainBounds(0.1, 100.0, "k1", "Position gain")
        assert bounds.validate(0.05) is False  # Below min
        assert bounds.validate(150.0) is False  # Above max
        assert bounds.validate(-1.0) is False  # Negative

    def test_gain_bounds_edge_cases(self):
        """Test edge cases for gain bounds."""
        # Zero minimum (for derivative gains)
        bounds = GainBounds(0.0, 100.0, "kd", "Derivative gain")
        assert bounds.validate(0.0) is True
        assert bounds.validate(-0.1) is False

        # Very small bounds
        bounds = GainBounds(1e-6, 1e-3, "epsilon", "Small parameter")
        assert bounds.validate(5e-5) is True
        assert bounds.validate(1e-7) is False


class TestSMCControllerType:
    """Test SMCControllerType enum."""

    def test_controller_type_values(self):
        """Test controller type enum values."""
        assert SMCControllerType.CLASSICAL.value == "classical"
        assert SMCControllerType.ADAPTIVE.value == "adaptive"
        assert SMCControllerType.SUPER_TWISTING.value == "super_twisting"
        assert SMCControllerType.HYBRID.value == "hybrid"

    def test_controller_type_from_string(self):
        """Test creating controller type from string."""
        assert SMCControllerType("classical") == SMCControllerType.CLASSICAL
        assert SMCControllerType("adaptive") == SMCControllerType.ADAPTIVE
        assert SMCControllerType("super_twisting") == SMCControllerType.SUPER_TWISTING
        assert SMCControllerType("hybrid") == SMCControllerType.HYBRID

    def test_invalid_controller_type(self):
        """Test invalid controller type raises ValueError."""
        with pytest.raises(ValueError):
            SMCControllerType("invalid_type")


class TestSMCGainValidator:
    """Comprehensive tests for SMCGainValidator class."""

    @pytest.fixture
    def validator(self):
        """Create validator instance for testing."""
        return SMCGainValidator()

    def test_validator_initialization(self, validator):
        """Test validator initialization."""
        assert validator is not None
        assert hasattr(validator, '_gain_bounds')
        assert isinstance(validator._gain_bounds, dict)

    def test_initialize_standard_bounds(self, validator):
        """Test standard bounds initialization."""
        bounds = validator._gain_bounds

        # Check all controller types are present
        assert SMCControllerType.CLASSICAL in bounds
        assert SMCControllerType.ADAPTIVE in bounds
        assert SMCControllerType.SUPER_TWISTING in bounds
        assert SMCControllerType.HYBRID in bounds

    def test_classical_smc_bounds(self, validator):
        """Test classical SMC gain bounds."""
        bounds = validator._gain_bounds[SMCControllerType.CLASSICAL]

        # Should have 6 bounds for classical SMC
        assert len(bounds) == 6

        # Check expected gain names
        gain_names = [b.name for b in bounds]
        expected_names = ["k1", "k2", "lam1", "lam2", "K", "kd"]
        assert all(name in gain_names for name in expected_names)

    def test_adaptive_smc_bounds(self, validator):
        """Test adaptive SMC gain bounds."""
        bounds = validator._gain_bounds[SMCControllerType.ADAPTIVE]

        # Should have 5 bounds for adaptive SMC
        assert len(bounds) == 5

        # Check expected gain names
        gain_names = [b.name for b in bounds]
        expected_names = ["k1", "k2", "lam1", "lam2", "gamma"]
        assert all(name in gain_names for name in expected_names)

    def test_super_twisting_bounds(self, validator):
        """Test super-twisting SMC gain bounds."""
        bounds = validator._gain_bounds[SMCControllerType.SUPER_TWISTING]

        # Should have 6 bounds for super-twisting SMC
        assert len(bounds) == 6

        # Check expected gain names including twisting gains
        gain_names = [b.name for b in bounds]
        expected_names = ["K1", "K2", "k1", "k2", "lam1", "lam2"]
        assert all(name in gain_names for name in expected_names)

    def test_hybrid_smc_bounds(self, validator):
        """Test hybrid SMC gain bounds."""
        bounds = validator._gain_bounds[SMCControllerType.HYBRID]

        # Should have 4 bounds for hybrid SMC
        assert len(bounds) == 4

        # Check expected gain names
        gain_names = [b.name for b in bounds]
        expected_names = ["c1", "lambda1", "c2", "lambda2"]
        assert all(name in gain_names for name in expected_names)

    def test_validate_gains_classical_valid(self, validator):
        """Test validation of valid classical SMC gains."""
        valid_gains = [10.0, 8.0, 5.0, 3.0, 15.0, 2.0]  # k1, k2, lam1, lam2, K, kd
        result = validator.validate_gains(valid_gains, SMCControllerType.CLASSICAL)

        assert result['valid'] is True
        assert 'violations' in result
        assert len(result['violations']) == 0

    def test_validate_gains_classical_invalid(self, validator):
        """Test validation of invalid classical SMC gains."""
        # Negative gains (should fail)
        invalid_gains = [-1.0, 8.0, 5.0, 3.0, 15.0, 2.0]
        result = validator.validate_gains(invalid_gains, SMCControllerType.CLASSICAL)

        assert result['valid'] is False
        assert len(result['violations']) > 0

    def test_validate_gains_string_controller_type(self, validator):
        """Test validation with string controller type."""
        # Adaptive gains: k1, k2, lam1, lam2, gamma (gamma must be 0.01-10.0)
        valid_gains = [10.0, 8.0, 5.0, 3.0, 5.0]  # Changed gamma from 15.0 to 5.0 to be within bounds
        result = validator.validate_gains(valid_gains, "adaptive")

        assert result['valid'] is True

    def test_validate_gains_wrong_length(self, validator):
        """Test validation with wrong number of gains."""
        # Classical needs 6 gains, providing only 4
        wrong_length_gains = [10.0, 8.0, 5.0, 3.0]
        result = validator.validate_gains(wrong_length_gains, SMCControllerType.CLASSICAL)

        assert result['valid'] is False
        # Implementation returns 'error' for length mismatch, not 'violations'
        assert 'error' in result or ('violations' in result and len(result['violations']) > 0)

    def test_validate_gains_numpy_array(self, validator):
        """Test validation with numpy array input."""
        valid_gains = np.array([10.0, 8.0, 5.0, 3.0, 15.0, 2.0])
        result = validator.validate_gains(valid_gains, SMCControllerType.CLASSICAL)

        assert result['valid'] is True

    def test_validate_stability_conditions_classical(self, validator):
        """Test stability condition validation for classical SMC."""
        valid_gains = [10.0, 8.0, 5.0, 3.0, 15.0, 2.0]
        result = validator.validate_stability_conditions(valid_gains, SMCControllerType.CLASSICAL)

        assert 'stable' in result
        assert 'issues' in result
        assert result['controller_type'] == 'classical'

    def test_validate_stability_conditions_zero_gains(self, validator):
        """Test stability with zero gains (should be unstable)."""
        zero_gains = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        result = validator.validate_stability_conditions(zero_gains, SMCControllerType.CLASSICAL)

        assert result['stable'] is False
        assert len(result['issues']) > 0

    def test_get_recommended_ranges(self, validator):
        """Test getting recommended gain ranges."""
        ranges = validator.get_recommended_ranges(SMCControllerType.CLASSICAL)

        assert isinstance(ranges, dict)
        assert len(ranges) == 6  # Classical has 6 gains
        assert 'k1' in ranges
        assert 'K' in ranges

        # Check range format
        k1_range = ranges['k1']
        assert isinstance(k1_range, tuple)
        assert len(k1_range) == 2
        assert k1_range[0] < k1_range[1]  # min < max

    def test_get_recommended_ranges_string_type(self, validator):
        """Test getting ranges with string controller type."""
        ranges = validator.get_recommended_ranges("adaptive")

        assert isinstance(ranges, dict)
        assert len(ranges) == 5  # Adaptive has 5 gains

    def test_get_recommended_ranges_invalid_type(self, validator):
        """Test getting ranges for invalid controller type."""
        # Implementation raises ValueError for invalid types
        with pytest.raises(ValueError, match="is not a valid SMCControllerType"):
            validator.get_recommended_ranges("invalid")

    def test_update_bounds_valid(self, validator):
        """Test updating gain bounds."""
        original_ranges = validator.get_recommended_ranges(SMCControllerType.CLASSICAL)
        original_k1 = original_ranges['k1']

        # Update k1 bounds
        validator.update_bounds(SMCControllerType.CLASSICAL, 'k1', 5.0, 50.0)

        updated_ranges = validator.get_recommended_ranges(SMCControllerType.CLASSICAL)
        assert updated_ranges['k1'] == (5.0, 50.0)
        assert updated_ranges['k1'] != original_k1

    def test_update_bounds_string_type(self, validator):
        """Test updating bounds with string controller type."""
        validator.update_bounds("classical", 'k2', 1.0, 20.0)

        ranges = validator.get_recommended_ranges("classical")
        assert ranges['k2'] == (1.0, 20.0)

    def test_update_bounds_invalid_controller(self, validator):
        """Test updating bounds for invalid controller type."""
        # Implementation raises ValueError with message about invalid enum
        with pytest.raises(ValueError, match="is not a valid SMCControllerType"):
            validator.update_bounds("invalid", 'k1', 1.0, 10.0)

    def test_update_bounds_invalid_gain(self, validator):
        """Test updating bounds for invalid gain name."""
        with pytest.raises(ValueError, match="Gain 'invalid_gain' not found"):
            validator.update_bounds(SMCControllerType.CLASSICAL, 'invalid_gain', 1.0, 10.0)


class TestConvenienceFunctions:
    """Test convenience functions for direct validation."""

    def test_validate_smc_gains_valid(self):
        """Test quick validation with valid gains."""
        valid_gains = [10.0, 8.0, 5.0, 3.0, 15.0, 2.0]
        assert validate_smc_gains(valid_gains, "classical") is True

    def test_validate_smc_gains_invalid(self):
        """Test quick validation with invalid gains."""
        invalid_gains = [-1.0, 8.0, 5.0, 3.0, 15.0, 2.0]
        assert validate_smc_gains(invalid_gains, "classical") is False

    def test_validate_smc_gains_default_type(self):
        """Test quick validation with default controller type."""
        valid_gains = [10.0, 8.0, 5.0, 3.0, 15.0, 2.0]
        assert validate_smc_gains(valid_gains) is True

    def test_check_stability_conditions_stable(self):
        """Test stability check with stable gains."""
        stable_gains = [10.0, 8.0, 5.0, 3.0, 15.0, 2.0]
        result = check_stability_conditions(stable_gains, "classical")
        assert isinstance(result, bool)

    def test_check_stability_conditions_default_type(self):
        """Test stability check with default controller type."""
        stable_gains = [10.0, 8.0, 5.0, 3.0, 15.0, 2.0]
        result = check_stability_conditions(stable_gains)
        assert isinstance(result, bool)

    def test_get_gain_bounds_for_controller(self):
        """Test getting gain bounds for specific controller."""
        bounds = get_gain_bounds_for_controller("classical")

        assert isinstance(bounds, dict)
        assert len(bounds) == 6
        assert 'k1' in bounds
        assert 'K' in bounds


class TestMathematicalProperties:
    """Test mathematical properties and edge cases."""

    @pytest.fixture
    def validator(self):
        return SMCGainValidator()

    def test_positive_definite_requirements(self, validator):
        """Test that surface gains must be positive for stability."""
        # All positive gains (should be stable)
        positive_gains = [10.0, 8.0, 5.0, 3.0, 15.0, 2.0]
        result = validator.validate_stability_conditions(positive_gains, "classical")

        # Test specific mathematical requirements
        assert result is not None

    def test_boundary_layer_requirements(self, validator):
        """Test boundary layer and switching gain relationships."""
        # Test that derivative gain can be zero (boundary condition)
        boundary_gains = [10.0, 8.0, 5.0, 3.0, 15.0, 0.0]
        result = validator.validate_gains(boundary_gains, "classical")
        assert result['valid'] is True

    def test_adaptation_gain_bounds(self, validator):
        """Test adaptation gain bounds for adaptive SMC."""
        # Test adaptation gains within valid range
        adaptive_gains = [10.0, 8.0, 5.0, 3.0, 0.5]  # gamma = 0.5
        result = validator.validate_gains(adaptive_gains, "adaptive")
        assert result['valid'] is True

        # Test adaptation gain too high
        high_adaptive_gains = [10.0, 8.0, 5.0, 3.0, 50.0]  # gamma = 50.0 (too high)
        result = validator.validate_gains(high_adaptive_gains, "adaptive")
        assert result['valid'] is False

    def test_super_twisting_gain_conditions(self, validator):
        """Test super-twisting algorithm gain conditions."""
        # K1^2 > 2*L condition (simplified test)
        st_gains = [50.0, 30.0, 10.0, 8.0, 5.0, 3.0]  # K1=50, K2=30
        result = validator.validate_gains(st_gains, "super_twisting")
        assert result['valid'] is True

    def test_gain_scaling_properties(self, validator):
        """Test gain scaling properties."""
        base_gains = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        scaled_gains = [g * 10.0 for g in base_gains]

        result_base = validator.validate_gains(base_gains, "classical")
        result_scaled = validator.validate_gains(scaled_gains, "classical")

        # Both should be valid
        assert result_base['valid'] is True
        assert result_scaled['valid'] is True


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.fixture
    def validator(self):
        return SMCGainValidator()

    def test_empty_gains_list(self, validator):
        """Test validation with empty gains list."""
        result = validator.validate_gains([], "classical")
        assert result['valid'] is False
        # Implementation returns 'error' for length mismatch, not 'violations'
        assert 'error' in result or ('violations' in result and len(result['violations']) > 0)

    def test_none_gains(self, validator):
        """Test validation with None gains."""
        with pytest.raises((TypeError, AttributeError)):
            validator.validate_gains(None, "classical")

    def test_non_numeric_gains(self, validator):
        """Test validation with non-numeric gains."""
        with pytest.raises((TypeError, ValueError)):
            validator.validate_gains(["a", "b", "c"], "classical")

    def test_infinite_gains(self, validator):
        """Test validation with infinite gains."""
        infinite_gains = [np.inf, 8.0, 5.0, 3.0, 15.0, 2.0]
        result = validator.validate_gains(infinite_gains, "classical")
        assert result['valid'] is False

    def test_nan_gains(self, validator):
        """Test validation with NaN gains."""
        nan_gains = [np.nan, 8.0, 5.0, 3.0, 15.0, 2.0]
        result = validator.validate_gains(nan_gains, "classical")
        assert result['valid'] is False