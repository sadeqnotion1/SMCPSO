#======================================================================================\\\
#================ tests/test_utils/validation/test_range_validators.py ================\\\
#======================================================================================\\\

"""
Comprehensive tests for range validation utilities.

Tests cover:
- require_in_range() - Range validation with inclusive/exclusive bounds
- require_probability() - Probability validation [0, 1]
- Edge cases, boundary conditions, and error messages
"""

import pytest
import math
from src.utils.control.validation.range_validators import require_in_range, require_probability


# =====================================================================================
# Tests for require_in_range()
# =====================================================================================

class TestRequireInRange:
    """Test require_in_range() validation function."""

    def test_value_within_range_inclusive(self):
        """Test validation of value within range (inclusive bounds)."""
        result = require_in_range(5.0, "test", minimum=0.0, maximum=10.0)
        assert result == 5.0

    def test_value_at_lower_bound_inclusive(self):
        """Test that lower bound is accepted with allow_equal=True."""
        result = require_in_range(0.0, "test", minimum=0.0, maximum=10.0, allow_equal=True)
        assert result == 0.0

    def test_value_at_upper_bound_inclusive(self):
        """Test that upper bound is accepted with allow_equal=True."""
        result = require_in_range(10.0, "test", minimum=0.0, maximum=10.0, allow_equal=True)
        assert result == 10.0

    def test_value_at_lower_bound_exclusive(self):
        """Test that lower bound is rejected with allow_equal=False."""
        with pytest.raises(ValueError, match="must satisfy.*<"):
            require_in_range(0.0, "test", minimum=0.0, maximum=10.0, allow_equal=False)

    def test_value_at_upper_bound_exclusive(self):
        """Test that upper bound is rejected with allow_equal=False."""
        with pytest.raises(ValueError, match="must satisfy.*<"):
            require_in_range(10.0, "test", minimum=0.0, maximum=10.0, allow_equal=False)

    def test_value_just_inside_bounds_exclusive(self):
        """Test value just inside exclusive bounds."""
        result = require_in_range(0.01, "test", minimum=0.0, maximum=10.0, allow_equal=False)
        assert result == 0.01

        result = require_in_range(9.99, "test", minimum=0.0, maximum=10.0, allow_equal=False)
        assert result == 9.99

    def test_value_below_range(self):
        """Test that value below range is rejected."""
        with pytest.raises(ValueError, match="must be in the interval"):
            require_in_range(-1.0, "test", minimum=0.0, maximum=10.0)

    def test_value_above_range(self):
        """Test that value above range is rejected."""
        with pytest.raises(ValueError, match="must be in the interval"):
            require_in_range(11.0, "test", minimum=0.0, maximum=10.0)

    def test_integer_value_converted_to_float(self):
        """Test that integer values are converted to float."""
        result = require_in_range(5, "test", minimum=0.0, maximum=10.0)
        assert result == 5.0
        assert isinstance(result, float)

    def test_negative_range(self):
        """Test validation with negative range."""
        result = require_in_range(-5.0, "test", minimum=-10.0, maximum=-1.0)
        assert result == -5.0

    def test_very_narrow_range(self):
        """Test validation with very narrow range."""
        result = require_in_range(1.5, "test", minimum=1.0, maximum=2.0)
        assert result == 1.5

    def test_range_crossing_zero(self):
        """Test validation with range crossing zero."""
        result = require_in_range(-2.5, "test", minimum=-5.0, maximum=5.0)
        assert result == -2.5

        result = require_in_range(2.5, "test", minimum=-5.0, maximum=5.0)
        assert result == 2.5

    def test_none_rejected(self):
        """Test that None is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_in_range(None, "test", minimum=0.0, maximum=10.0)

    def test_infinity_rejected(self):
        """Test that infinity is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_in_range(math.inf, "test", minimum=0.0, maximum=10.0)

    def test_nan_rejected(self):
        """Test that NaN is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_in_range(math.nan, "test", minimum=0.0, maximum=10.0)

    def test_error_message_includes_parameter_name(self):
        """Test that error messages include parameter name."""
        try:
            require_in_range(15.0, "control_gain", minimum=0.0, maximum=10.0)
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert "control_gain" in str(e)

    def test_error_message_includes_bounds(self):
        """Test that error messages include the bounds."""
        try:
            require_in_range(15.0, "test", minimum=0.0, maximum=10.0)
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert "0.0" in str(e) or "0" in str(e)
            assert "10.0" in str(e) or "10" in str(e)

    def test_error_message_includes_actual_value(self):
        """Test that error messages include the actual value."""
        try:
            require_in_range(15.0, "test", minimum=0.0, maximum=10.0)
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert "15.0" in str(e) or "15" in str(e)

    def test_large_range_values(self):
        """Test validation with very large range values."""
        result = require_in_range(1e100, "test", minimum=-1e200, maximum=1e200)
        assert result == 1e100

    def test_very_small_range(self):
        """Test validation with very small (but finite) range."""
        result = require_in_range(1e-100, "test", minimum=0.0, maximum=1e-50)
        assert result == 1e-100

    def test_minimum_equals_maximum_inclusive(self):
        """Test range where minimum equals maximum with allow_equal=True."""
        result = require_in_range(5.0, "test", minimum=5.0, maximum=5.0, allow_equal=True)
        assert result == 5.0

    def test_minimum_equals_maximum_exclusive(self):
        """Test range where minimum equals maximum with allow_equal=False."""
        # No value can satisfy min < value < max when min == max
        with pytest.raises(ValueError):
            require_in_range(5.0, "test", minimum=5.0, maximum=5.0, allow_equal=False)

    def test_reversed_bounds_behavior(self):
        """Test behavior when minimum > maximum (should reject all values)."""
        # With minimum > maximum, no value can satisfy the constraints
        with pytest.raises(ValueError):
            require_in_range(5.0, "test", minimum=10.0, maximum=0.0)


# =====================================================================================
# Tests for require_probability()
# =====================================================================================

class TestRequireProbability:
    """Test require_probability() validation function."""

    def test_valid_probability_mid_range(self):
        """Test validation of probability in middle of range."""
        result = require_probability(0.5, "test")
        assert result == 0.5

    def test_probability_zero(self):
        """Test that probability 0.0 is accepted."""
        result = require_probability(0.0, "test")
        assert result == 0.0

    def test_probability_one(self):
        """Test that probability 1.0 is accepted."""
        result = require_probability(1.0, "test")
        assert result == 1.0

    def test_probability_very_small(self):
        """Test very small but valid probability."""
        result = require_probability(1e-10, "test")
        assert result == 1e-10

    def test_probability_very_close_to_one(self):
        """Test probability very close to 1.0."""
        result = require_probability(0.9999999, "test")
        assert result == 0.9999999

    def test_negative_probability_rejected(self):
        """Test that negative probabilities are rejected."""
        with pytest.raises(ValueError, match="must be in the interval"):
            require_probability(-0.1, "test")

    def test_probability_greater_than_one_rejected(self):
        """Test that probabilities > 1 are rejected."""
        with pytest.raises(ValueError, match="must be in the interval"):
            require_probability(1.1, "test")

    def test_probability_large_value_rejected(self):
        """Test that large values are rejected."""
        with pytest.raises(ValueError, match="must be in the interval"):
            require_probability(100.0, "test")

    def test_probability_none_rejected(self):
        """Test that None is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_probability(None, "test")

    def test_probability_nan_rejected(self):
        """Test that NaN is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_probability(math.nan, "test")

    def test_probability_infinity_rejected(self):
        """Test that infinity is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_probability(math.inf, "test")

    def test_probability_integer_converted(self):
        """Test that integer 0 and 1 are accepted and converted."""
        result = require_probability(0, "test")
        assert result == 0.0
        assert isinstance(result, float)

        result = require_probability(1, "test")
        assert result == 1.0
        assert isinstance(result, float)

    def test_probability_error_message_includes_name(self):
        """Test that error messages include parameter name."""
        try:
            require_probability(1.5, "dropout_rate")
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert "dropout_rate" in str(e)

    def test_probability_uses_inclusive_bounds(self):
        """Test that probability validation uses inclusive bounds."""
        # Both 0 and 1 should be accepted (tested above)
        # This test verifies the function uses allow_equal=True internally
        result_zero = require_probability(0.0, "test")
        result_one = require_probability(1.0, "test")
        assert result_zero == 0.0
        assert result_one == 1.0


# =====================================================================================
# Integration and Edge Cases
# =====================================================================================

class TestRangeValidationIntegration:
    """Test integration scenarios and edge cases."""

    def test_probability_is_special_case_of_range(self):
        """Test that require_probability is equivalent to require_in_range(0, 1)."""
        test_values = [0.0, 0.25, 0.5, 0.75, 1.0]

        for value in test_values:
            result_prob = require_probability(value, "test")
            result_range = require_in_range(value, "test", minimum=0.0, maximum=1.0, allow_equal=True)
            assert result_prob == result_range

    def test_invalid_probability_vs_invalid_range(self):
        """Test that invalid probabilities are rejected same as invalid ranges."""
        invalid_values = [-0.5, 1.5, 2.0]

        for value in invalid_values:
            # Both should raise ValueError
            with pytest.raises(ValueError):
                require_probability(value, "test")
            with pytest.raises(ValueError):
                require_in_range(value, "test", minimum=0.0, maximum=1.0)

    def test_multiple_ranges_same_parameter(self):
        """Test validating same parameter against different ranges."""
        value = 5.0

        # Should pass different range validations
        result1 = require_in_range(value, "param", minimum=0.0, maximum=10.0)
        result2 = require_in_range(value, "param", minimum=4.0, maximum=6.0)
        result3 = require_in_range(value, "param", minimum=5.0, maximum=5.0)

        assert result1 == result2 == result3 == 5.0

    def test_chained_validation_probability_and_range(self):
        """Test using both probability and range validation in sequence."""
        value = 0.5

        # First validate as probability
        prob_value = require_probability(value, "test")

        # Then validate in narrower range
        result = require_in_range(prob_value, "test", minimum=0.25, maximum=0.75)
        assert result == 0.5

    def test_floating_point_precision_at_boundaries(self):
        """Test floating-point precision issues at boundaries."""
        # Value very close to boundary
        almost_one = 1.0 - 1e-15
        result = require_probability(almost_one, "test")
        assert result < 1.0

        # Value at exact boundary
        exact_one = 1.0
        result = require_probability(exact_one, "test")
        assert result == 1.0

    def test_symmetric_ranges(self):
        """Test symmetric ranges around zero."""
        result = require_in_range(0.0, "test", minimum=-10.0, maximum=10.0)
        assert result == 0.0

        result = require_in_range(-5.0, "test", minimum=-10.0, maximum=10.0)
        assert result == -5.0

        result = require_in_range(5.0, "test", minimum=-10.0, maximum=10.0)
        assert result == 5.0

    def test_parameter_name_in_all_error_messages(self):
        """Test that parameter names appear in all error messages."""
        param_name = "adaptive_gain"

        # Test with out-of-range value
        try:
            require_in_range(100.0, param_name, minimum=0.0, maximum=10.0)
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert param_name in str(e)

        # Test with None
        try:
            require_in_range(None, param_name, minimum=0.0, maximum=10.0)
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert param_name in str(e)

    def test_exclusive_vs_inclusive_boundary_behavior(self):
        """Test difference between exclusive and inclusive bounds."""
        boundary_value = 10.0

        # Inclusive should accept boundary
        result = require_in_range(boundary_value, "test", minimum=0.0, maximum=10.0, allow_equal=True)
        assert result == boundary_value

        # Exclusive should reject boundary
        with pytest.raises(ValueError):
            require_in_range(boundary_value, "test", minimum=0.0, maximum=10.0, allow_equal=False)
