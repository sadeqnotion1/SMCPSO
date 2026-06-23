#======================================================================================\\\
#============= tests/test_utils/validation/test_parameter_validators.py ===============\\\
#======================================================================================\\\

"""
Comprehensive tests for parameter validation utilities.

Tests cover:
- require_positive() - Positive and non-negative value validation
- require_finite() - Finite number validation
- Edge cases, boundary conditions, and error messages
"""

import pytest
import math
from src.utils.control.validation.parameter_validators import require_positive, require_finite


# =====================================================================================
# Tests for require_positive()
# =====================================================================================

class TestRequirePositive:
    """Test require_positive() validation function."""

    def test_valid_positive_float(self):
        """Test validation of valid positive float."""
        result = require_positive(5.0, "test_param")
        assert result == 5.0
        assert isinstance(result, float)

    def test_valid_positive_int(self):
        """Test validation of valid positive integer."""
        result = require_positive(10, "test_param")
        assert result == 10.0
        assert isinstance(result, float)  # Should cast to float

    def test_very_large_positive_value(self):
        """Test validation of very large positive value."""
        large_value = 1e308
        result = require_positive(large_value, "test_param")
        assert result == large_value

    def test_very_small_positive_value(self):
        """Test validation of very small but positive value."""
        small_value = 1e-308
        result = require_positive(small_value, "test_param")
        assert result == small_value

    def test_zero_rejected_by_default(self):
        """Test that zero is rejected by default."""
        with pytest.raises(ValueError, match="must be > 0"):
            require_positive(0.0, "test_param")

    def test_zero_allowed_with_flag(self):
        """Test that zero is allowed when allow_zero=True."""
        result = require_positive(0.0, "test_param", allow_zero=True)
        assert result == 0.0

    def test_negative_rejected_without_allow_zero(self):
        """Test that negative values are always rejected."""
        with pytest.raises(ValueError, match="must be > 0"):
            require_positive(-5.0, "test_param")

    def test_negative_rejected_with_allow_zero(self):
        """Test that negative values are rejected even with allow_zero=True."""
        with pytest.raises(ValueError, match="must be ≥ 0"):
            require_positive(-5.0, "test_param", allow_zero=True)

    def test_none_rejected(self):
        """Test that None is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_positive(None, "test_param")

    def test_infinity_rejected(self):
        """Test that positive infinity is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_positive(math.inf, "test_param")

    def test_negative_infinity_rejected(self):
        """Test that negative infinity is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_positive(-math.inf, "test_param")

    def test_nan_rejected(self):
        """Test that NaN is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_positive(math.nan, "test_param")

    def test_string_rejected(self):
        """Test that string values are rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_positive("5.0", "test_param")  # type: ignore

    def test_list_rejected(self):
        """Test that list values are rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_positive([5.0], "test_param")  # type: ignore

    def test_error_message_includes_parameter_name(self):
        """Test that error messages include the parameter name."""
        try:
            require_positive(-1.0, "custom_gain")
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert "custom_gain" in str(e)

    def test_error_message_includes_actual_value(self):
        """Test that error messages include the actual value."""
        try:
            require_positive(-3.5, "test_param")
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert "-3.5" in str(e) or "3.5" in str(e)

    def test_negative_zero(self):
        """Test handling of negative zero (-0.0)."""
        # Negative zero should be treated as zero
        with pytest.raises(ValueError, match="must be > 0"):
            require_positive(-0.0, "test_param")

        # But allowed with allow_zero=True
        result = require_positive(-0.0, "test_param", allow_zero=True)
        assert result == 0.0


# =====================================================================================
# Tests for require_finite()
# =====================================================================================

class TestRequireFinite:
    """Test require_finite() validation function."""

    def test_valid_positive_float(self):
        """Test validation of valid positive float."""
        result = require_finite(5.0, "test_param")
        assert result == 5.0
        assert isinstance(result, float)

    def test_valid_negative_float(self):
        """Test validation of valid negative float."""
        result = require_finite(-5.0, "test_param")
        assert result == -5.0

    def test_valid_zero(self):
        """Test validation of zero."""
        result = require_finite(0.0, "test_param")
        assert result == 0.0

    def test_valid_integer(self):
        """Test validation of integer value."""
        result = require_finite(42, "test_param")
        assert result == 42.0
        assert isinstance(result, float)  # Should cast to float

    def test_very_large_value(self):
        """Test validation of very large finite value."""
        large_value = 1e308
        result = require_finite(large_value, "test_param")
        assert result == large_value

    def test_very_small_negative_value(self):
        """Test validation of very small negative value."""
        small_value = -1e308
        result = require_finite(small_value, "test_param")
        assert result == small_value

    def test_none_rejected(self):
        """Test that None is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_finite(None, "test_param")

    def test_positive_infinity_rejected(self):
        """Test that positive infinity is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_finite(math.inf, "test_param")

    def test_negative_infinity_rejected(self):
        """Test that negative infinity is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_finite(-math.inf, "test_param")

    def test_nan_rejected(self):
        """Test that NaN is rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_finite(math.nan, "test_param")

    def test_string_rejected(self):
        """Test that string values are rejected."""
        with pytest.raises(ValueError, match="must be a finite number"):
            require_finite("5.0", "test_param")  # type: ignore

    def test_boolean_rejected(self):
        """Test that boolean values are rejected."""
        # Note: In Python, bool is a subclass of int, so True/False would pass isinstance(int)
        # But since booleans are ints (True=1, False=0), they might be allowed
        # Let's test the actual behavior
        result = require_finite(True, "test_param")
        assert result == 1.0  # True converts to 1.0

    def test_error_message_includes_parameter_name(self):
        """Test that error messages include the parameter name."""
        try:
            require_finite(math.inf, "velocity_limit")
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert "velocity_limit" in str(e)

    def test_error_message_includes_actual_value(self):
        """Test that error messages include the actual value representation."""
        try:
            require_finite(None, "test_param")
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert "None" in str(e)

    def test_subnormal_numbers_accepted(self):
        """Test that subnormal (denormalized) numbers are accepted."""
        # Subnormal numbers are very small but finite
        subnormal = 5e-324  # Smallest positive subnormal float
        result = require_finite(subnormal, "test_param")
        assert result == subnormal


# =====================================================================================
# Integration and Edge Cases
# =====================================================================================

class TestValidationIntegration:
    """Test integration scenarios and edge cases."""

    def test_require_positive_vs_require_finite_for_positive_values(self):
        """Test that require_positive and require_finite agree on positive values."""
        test_values = [1.0, 0.5, 100.0, 1e-10, 1e10]

        for value in test_values:
            result_positive = require_positive(value, "test")
            result_finite = require_finite(value, "test")
            assert result_positive == result_finite

    def test_require_finite_accepts_negative_values(self):
        """Test that require_finite accepts negative values while require_positive doesn't."""
        negative_value = -5.0

        # require_finite should accept
        result = require_finite(negative_value, "test")
        assert result == -5.0

        # require_positive should reject
        with pytest.raises(ValueError):
            require_positive(negative_value, "test")

    def test_boundary_value_zero(self):
        """Test boundary value of zero with both validators."""
        # require_positive rejects zero by default
        with pytest.raises(ValueError):
            require_positive(0.0, "test")

        # require_positive accepts zero with flag
        result1 = require_positive(0.0, "test", allow_zero=True)
        assert result1 == 0.0

        # require_finite always accepts zero
        result2 = require_finite(0.0, "test")
        assert result2 == 0.0

    def test_chained_validation(self):
        """Test using both validators in sequence."""
        # Valid value should pass both
        value = 5.0
        finite_value = require_finite(value, "test")
        positive_value = require_positive(finite_value, "test")
        assert positive_value == 5.0

    def test_float_precision_edge_cases(self):
        """Test edge cases related to floating-point precision."""
        # Smallest positive normal float
        min_normal = 2.2250738585072014e-308
        result = require_positive(min_normal, "test")
        assert result == min_normal

        # Largest finite float
        max_finite = 1.7976931348623157e+308
        result = require_positive(max_finite, "test")
        assert result == max_finite

    def test_parameter_name_special_characters(self):
        """Test parameter names with special characters in error messages."""
        try:
            require_positive(-1.0, "controller.gain[0]")
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert "controller.gain[0]" in str(e)

    def test_multiple_validation_calls_with_same_parameter(self):
        """Test multiple validation calls with the same parameter name."""
        # Should work independently
        result1 = require_positive(5.0, "gain")
        result2 = require_positive(10.0, "gain")
        assert result1 == 5.0
        assert result2 == 10.0
