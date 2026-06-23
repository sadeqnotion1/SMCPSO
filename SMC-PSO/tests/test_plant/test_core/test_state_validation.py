"""
Unit tests for state validation (src/plant/core/state_validation.py).

Tests cover:
- DIPStateValidator: initialization, validation, sanitization, error handling
- MinimalStateValidator: performance-critical validation
- StateValidationError: custom exception
- Statistics tracking and bounds checking
"""

import numpy as np
import pytest
import warnings

from src.plant.core.state_validation import (
    DIPStateValidator,
    MinimalStateValidator,
    StateValidationError
)


# ======================================================================================
# DIPStateValidator - Initialization Tests
# ======================================================================================

class TestDIPStateValidatorInitialization:
    """Test DIPStateValidator initialization."""

    def test_default_initialization(self):
        """Should initialize with default bounds."""
        validator = DIPStateValidator()

        assert validator.position_bounds == (-10.0, 10.0)
        assert validator.angle_bounds == (-4*np.pi, 4*np.pi)
        assert validator.velocity_bounds == (-20.0, 20.0)
        assert validator.angular_velocity_bounds == (-50.0, 50.0)
        assert validator.wrap_angles is True
        assert validator.strict_validation is False

    def test_custom_bounds(self):
        """Should accept custom bounds."""
        validator = DIPStateValidator(
            position_bounds=(-5.0, 5.0),
            angle_bounds=(-np.pi, np.pi),
            velocity_bounds=(-10.0, 10.0),
            angular_velocity_bounds=(-25.0, 25.0),
            wrap_angles=False,
            strict_validation=True
        )

        assert validator.position_bounds == (-5.0, 5.0)
        assert validator.angle_bounds == (-np.pi, np.pi)
        assert validator.velocity_bounds == (-10.0, 10.0)
        assert validator.angular_velocity_bounds == (-25.0, 25.0)
        assert validator.wrap_angles is False
        assert validator.strict_validation is True

    def test_statistics_initialized_to_zero(self):
        """Should initialize statistics to zero."""
        validator = DIPStateValidator()

        assert validator.validation_count == 0
        assert validator.sanitization_count == 0
        assert validator.failure_count == 0


# ======================================================================================
# DIPStateValidator - Validation Tests
# ======================================================================================

class TestDIPStateValidatorValidation:
    """Test DIPStateValidator.validate_state()."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return DIPStateValidator()

    def test_valid_state_returns_true(self, validator):
        """Should return True for valid state."""
        state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])
        assert validator.validate_state(state) is True
        assert validator.validation_count == 1

    def test_zero_state_is_valid(self, validator):
        """Should accept zero state as valid."""
        state = np.zeros(6)
        assert validator.validate_state(state) is True

    def test_invalid_shape_returns_false(self, validator):
        """Should return False for wrong shape."""
        state = np.array([0.0, 0.0, 0.0])  # Only 3 elements
        assert validator.validate_state(state) is False

    def test_nan_state_returns_false(self, validator):
        """Should return False for NaN values."""
        state = np.array([0.0, np.nan, 0.1, 0.0, 0.0, 0.0])
        assert validator.validate_state(state) is False

    def test_inf_state_returns_false(self, validator):
        """Should return False for infinite values."""
        state = np.array([0.0, np.inf, 0.1, 0.0, 0.0, 0.0])
        assert validator.validate_state(state) is False

    def test_out_of_bounds_position_returns_false(self, validator):
        """Should return False for position out of bounds."""
        state = np.array([15.0, 0.1, 0.1, 0.0, 0.0, 0.0])  # x=15 > 10
        assert validator.validate_state(state) is False

    def test_out_of_bounds_velocity_returns_false(self, validator):
        """Should return False for velocity out of bounds."""
        state = np.array([0.0, 0.1, 0.1, 25.0, 0.0, 0.0])  # x_dot=25 > 20
        assert validator.validate_state(state) is False

    def test_strict_validation_raises_on_invalid(self):
        """Should raise StateValidationError in strict mode."""
        validator = DIPStateValidator(strict_validation=True)
        state = np.array([0.0, np.nan, 0.0, 0.0, 0.0, 0.0])

        with pytest.raises(StateValidationError, match="invalid numerical values"):
            validator.validate_state(state)


# ======================================================================================
# DIPStateValidator - Sanitization Tests
# ======================================================================================

class TestDIPStateValidatorSanitization:
    """Test DIPStateValidator.sanitize_state()."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return DIPStateValidator()

    def test_sanitize_valid_state_unchanged(self, validator):
        """Should return unchanged state if already valid."""
        state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])
        sanitized = validator.sanitize_state(state)

        np.testing.assert_array_almost_equal(sanitized, state)
        # Sanitization count may be non-zero due to angle wrapping

    def test_sanitize_nan_values(self, validator):
        """Should replace NaN with zeros."""
        state = np.array([0.0, np.nan, 0.1, 0.0, 0.0, 0.0])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            sanitized = validator.sanitize_state(state)

        assert np.isfinite(sanitized).all()
        assert sanitized[1] == 0.0  # NaN replaced
        assert validator.sanitization_count == 1

    def test_sanitize_inf_values(self, validator):
        """Should clip infinite values."""
        state = np.array([0.0, np.inf, -np.inf, 0.0, 0.0, 0.0])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            sanitized = validator.sanitize_state(state)

        assert np.isfinite(sanitized).all()
        # After fixing numerical issues, bounds are applied (angle bounds)
        assert sanitized[1] != np.inf  # Finite
        assert sanitized[2] != -np.inf  # Finite

    def test_sanitize_out_of_bounds(self, validator):
        """Should clip out-of-bounds values."""
        state = np.array([15.0, 0.1, 0.1, 0.0, 0.0, 0.0])  # x=15 > 10

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            sanitized = validator.sanitize_state(state)

        assert sanitized[0] == 10.0  # Clipped to max
        assert validator.sanitization_count == 1

    def test_sanitize_wraps_angles(self, validator):
        """Should wrap angles to [-π, π] if enabled."""
        state = np.array([0.0, 4*np.pi, -4*np.pi, 0.0, 0.0, 0.0])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            sanitized = validator.sanitize_state(state)

        # Angles should be wrapped
        assert -np.pi <= sanitized[1] <= np.pi
        assert -np.pi <= sanitized[2] <= np.pi

    def test_sanitize_no_angle_wrapping(self):
        """Should not wrap angles if disabled."""
        validator = DIPStateValidator(wrap_angles=False)
        state = np.array([0.0, 2*np.pi, 0.0, 0.0, 0.0, 0.0])

        sanitized = validator.sanitize_state(state)

        # Angle not wrapped (but may be clipped if out of bounds)
        assert sanitized[1] == pytest.approx(2*np.pi, abs=1e-10)

    def test_sanitize_emits_warning(self, validator):
        """Should emit UserWarning when state modified."""
        state = np.array([15.0, 0.1, 0.1, 0.0, 0.0, 0.0])  # Out of bounds

        with pytest.warns(UserWarning, match="modified during sanitization"):
            validator.sanitize_state(state)

    def test_sanitize_list_input(self, validator):
        """Should accept list and convert to array."""
        state = [0.0, 0.1, 0.1, 0.0, 0.0, 0.0]
        sanitized = validator.sanitize_state(state)

        assert isinstance(sanitized, np.ndarray)
        assert sanitized.shape == (6,)

    def test_sanitize_invalid_structure_raises(self, validator):
        """Should raise StateValidationError for invalid structure."""
        state = np.array([0.0, 0.0, 0.0])  # Only 3 elements

        with pytest.raises(StateValidationError, match="invalid state structure"):
            validator.sanitize_state(state)


# ======================================================================================
# DIPStateValidator - State Info Tests
# ======================================================================================

class TestDIPStateValidatorStateInfo:
    """Test DIPStateValidator.get_state_info()."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return DIPStateValidator()

    def test_get_state_info_valid(self, validator):
        """Should return detailed info for valid state."""
        state = np.array([1.0, 0.2, 0.3, 0.5, 0.1, 0.1])
        info = validator.get_state_info(state)

        assert info["is_valid"] == True
        assert info["structure_valid"] == True
        assert info["numerically_valid"] == True
        assert info["within_bounds"] == True
        assert info["cart_position"] == 1.0
        assert info["pendulum1_angle"] == 0.2
        assert info["pendulum2_angle"] == 0.3
        assert "total_energy_estimate" in info
        assert "angular_momentum_estimate" in info

    def test_get_state_info_invalid(self, validator):
        """Should return partial info for invalid state."""
        state = np.array([0.0, np.nan, 0.0, 0.0, 0.0, 0.0])
        info = validator.get_state_info(state)

        assert info["is_valid"] == False
        assert info["numerically_valid"] == False


# ======================================================================================
# DIPStateValidator - Statistics Tests
# ======================================================================================

class TestDIPStateValidatorStatistics:
    """Test DIPStateValidator statistics tracking."""

    def test_reset_statistics(self):
        """Should reset all statistics to zero."""
        validator = DIPStateValidator()
        state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])

        # Perform some operations
        validator.validate_state(state)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            validator.sanitize_state(np.array([15.0, 0.1, 0.1, 0.0, 0.0, 0.0]))

        # Reset
        validator.reset_statistics()

        assert validator.validation_count == 0
        assert validator.sanitization_count == 0
        assert validator.failure_count == 0

    def test_get_statistics_zero_count(self):
        """Should handle zero validation count."""
        validator = DIPStateValidator()
        stats = validator.get_statistics()

        assert stats["validation_count"] == 0
        assert stats["sanitization_rate"] == 0.0
        assert stats["failure_rate"] == 0.0

    def test_get_statistics_with_data(self):
        """Should compute statistics correctly."""
        validator = DIPStateValidator()
        valid_state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])
        invalid_state = np.array([0.0, np.nan, 0.0, 0.0, 0.0, 0.0])

        # Perform operations
        validator.validate_state(valid_state)
        validator.validate_state(invalid_state)  # Fails
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            validator.sanitize_state(np.array([15.0, 0.1, 0.1, 0.0, 0.0, 0.0]))  # Sanitizes

        stats = validator.get_statistics()

        assert stats["validation_count"] == 2
        # Note: sanitization_count is separate from validation_count
        assert isinstance(stats["sanitization_rate"], float)
        assert isinstance(stats["failure_rate"], float)


# ======================================================================================
# MinimalStateValidator Tests
# ======================================================================================

class TestMinimalStateValidator:
    """Test MinimalStateValidator."""

    @pytest.fixture
    def validator(self):
        """Create minimal validator instance."""
        return MinimalStateValidator()

    def test_validate_state_valid(self, validator):
        """Should return True for valid state."""
        state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])
        assert validator.validate_state(state) == True

    def test_validate_state_wrong_shape(self, validator):
        """Should return False for wrong shape."""
        state = np.array([0.0, 0.0, 0.0])
        assert validator.validate_state(state) == False

    def test_validate_state_nan(self, validator):
        """Should return False for NaN."""
        state = np.array([0.0, np.nan, 0.0, 0.0, 0.0, 0.0])
        assert validator.validate_state(state) == False

    def test_sanitize_state_valid(self, validator):
        """Should return unchanged valid state."""
        state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])
        sanitized = validator.sanitize_state(state)

        np.testing.assert_array_equal(sanitized, state)

    def test_sanitize_state_nan(self, validator):
        """Should replace NaN with zeros."""
        state = np.array([0.0, np.nan, 0.1, 0.0, 0.0, 0.0])
        sanitized = validator.sanitize_state(state)

        assert np.isfinite(sanitized).all()
        assert sanitized[1] == 0.0

    def test_sanitize_state_list_input(self, validator):
        """Should convert list to array."""
        state = [0.0, 0.1, 0.1, 0.0, 0.0, 0.0]
        sanitized = validator.sanitize_state(state)

        assert isinstance(sanitized, np.ndarray)
        assert sanitized.shape == (6,)

    def test_sanitize_invalid_shape_raises(self, validator):
        """Should raise StateValidationError for invalid shape."""
        state = np.array([0.0, 0.0, 0.0])

        with pytest.raises(StateValidationError, match="6-element vector"):
            validator.sanitize_state(state)


# ======================================================================================
# Edge Cases for 100% Safety-Critical Coverage
# ======================================================================================

class TestStateValidationEdgeCases:
    """Test edge cases for 100% coverage of safety-critical code."""

    def test_strict_validation_invalid_structure_raises(self):
        """Test line 104: strict_validation raises on invalid structure."""
        validator = DIPStateValidator(strict_validation=True)
        invalid_state = np.array([1.0, 2.0, 3.0])  # Wrong shape

        with pytest.raises(StateValidationError, match="Invalid state vector structure"):
            validator.validate_state(invalid_state)

    def test_strict_validation_physical_bounds_raises(self):
        """Test line 116: strict_validation raises on physical bounds violation."""
        validator = DIPStateValidator(
            strict_validation=True,
            position_bounds=(-1.0, 1.0)  # Tight bounds
        )
        state = np.array([5.0, 0.0, 0.0, 0.0, 0.0, 0.0])  # x=5.0 exceeds bounds

        with pytest.raises(StateValidationError, match="violates physical bounds"):
            validator.validate_state(state)

    def test_strict_validation_exception_handling(self):
        """Test line 125: strict_validation exception handling path."""
        validator = DIPStateValidator(strict_validation=True)

        # Trigger an exception during validation by passing incompatible type
        # This will cause an exception that's caught and re-raised
        with pytest.raises(StateValidationError, match="State validation failed"):
            validator.validate_state(None)  # None will cause exception

    def test_check_physical_bounds_invalid_structure(self):
        """Test line 246: _check_physical_bounds early return on invalid structure."""
        validator = DIPStateValidator()
        invalid_state = np.array([1.0, 2.0, 3.0])  # Wrong shape

        # This triggers the internal _check_physical_bounds which checks structure first
        result = validator.validate_state(invalid_state)
        assert result is False

    def test_angular_velocity_bounds_violation_theta1(self):
        """Test line 266: theta1_dot bounds violation."""
        validator = DIPStateValidator(
            angular_velocity_bounds=(-10.0, 10.0)  # Tight bounds
        )
        # State format: [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
        state = np.array([0.0, 0.0, 0.0, 0.0, 15.0, 0.0])  # theta1_dot=15.0 at index 4

        result = validator.validate_state(state)
        assert result is False

    def test_angular_velocity_bounds_violation_theta2(self):
        """Test line 268: theta2_dot bounds violation."""
        validator = DIPStateValidator(
            angular_velocity_bounds=(-10.0, 10.0)  # Tight bounds
        )
        # State format: [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
        state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 15.0])  # theta2_dot=15.0 at index 5

        result = validator.validate_state(state)
        assert result is False

    def test_non_strict_validation_returns_false_on_error(self):
        """Test non-strict mode returns False instead of raising."""
        validator = DIPStateValidator(strict_validation=False)

        # Test with None (fails structure check but doesn't raise in non-strict mode)
        result = validator.validate_state(None)
        assert result is False
        # Verify validation was attempted
        assert validator.validation_count > 0


# ======================================================================================
# StateValidationError Tests
# ======================================================================================

class TestStateValidationError:
    """Test StateValidationError exception."""

    def test_is_value_error_subclass(self):
        """Should be subclass of ValueError."""
        assert issubclass(StateValidationError, ValueError)

    def test_can_be_raised(self):
        """Should be raisable with message."""
        with pytest.raises(StateValidationError, match="test message"):
            raise StateValidationError("test message")


# ======================================================================================
# Integration Tests
# ======================================================================================

class TestStateValidationIntegration:
    """Integration tests across validators."""

    def test_dip_and_minimal_validators_consistent(self):
        """Both validators should accept same valid state."""
        dip_validator = DIPStateValidator()
        min_validator = MinimalStateValidator()

        valid_state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])

        assert dip_validator.validate_state(valid_state) == True
        assert min_validator.validate_state(valid_state) == True

    def test_dip_and_minimal_validators_reject_nan(self):
        """Both validators should reject NaN values."""
        dip_validator = DIPStateValidator()
        min_validator = MinimalStateValidator()

        invalid_state = np.array([0.0, np.nan, 0.0, 0.0, 0.0, 0.0])

        assert dip_validator.validate_state(invalid_state) == False
        assert min_validator.validate_state(invalid_state) == False

    def test_validators_sanitize_consistently(self):
        """Both validators should sanitize NaN similarly."""
        dip_validator = DIPStateValidator()
        min_validator = MinimalStateValidator()

        nan_state = np.array([0.0, np.nan, 0.0, 0.0, 0.0, 0.0])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            dip_sanitized = dip_validator.sanitize_state(nan_state)
            min_sanitized = min_validator.sanitize_state(nan_state)

        # Both should replace NaN with 0
        assert dip_sanitized[1] == 0.0
        assert min_sanitized[1] == 0.0
