#!/usr/bin/env python
"""
Numerical Stability Tests - Safe Division Operations (Week 3 Session 7)

PURPOSE: Comprehensive unit tests for safe_divide and safe_reciprocal
COVERAGE TARGET: 90-95% of division-related functions
STRATEGY: Test mathematical guarantees, edge cases, broadcasting, warnings

TEST MATRIX:
1. safe_divide - Normal operations (scalar, array, broadcasting)
2. safe_divide - Zero division protection (exact zero, near-zero, epsilon)
3. safe_divide - Sign preservation and fallback behavior
4. safe_divide - Warning system and error handling
5. safe_reciprocal - Wrapper functionality validation
6. Edge cases - NaN, Inf, mixed types, large arrays

Mathematical Guarantees Tested:
- safe_divide(a, b) = a / max(|b|, ε) * sign(b)
- Exact zero → fallback value
- Near-zero → epsilon protection with sign preservation
- Broadcasting follows NumPy rules

Author: Claude Code (Week 3 Session 7)
Date: December 2025
"""

import pytest
import numpy as np
import warnings
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Import safe operations
from src.utils.numerical_stability.safe_operations import (
    safe_divide,
    safe_reciprocal,
    EPSILON_DIV,
)

# ==============================================================================
# Test safe_divide - Normal Operations
# ==============================================================================

class TestSafeDivideNormal:
    """Test safe_divide with normal (non-problematic) inputs"""

    def test_divide_positive_scalars(self):
        """Test division of positive scalars"""
        result = safe_divide(10.0, 2.0)
        assert result == 5.0
        assert isinstance(result, float)

    def test_divide_negative_scalars(self):
        """Test division with negative values"""
        assert safe_divide(-10.0, 2.0) == -5.0
        assert safe_divide(10.0, -2.0) == -5.0
        assert safe_divide(-10.0, -2.0) == 5.0

    def test_divide_scalar_arrays(self):
        """Test division with array inputs"""
        numerator = np.array([10.0, 20.0, 30.0])
        denominator = np.array([2.0, 4.0, 5.0])
        result = safe_divide(numerator, denominator)

        expected = np.array([5.0, 5.0, 6.0])
        np.testing.assert_array_almost_equal(result, expected)
        assert isinstance(result, np.ndarray)

    def test_divide_broadcasting(self):
        """Test NumPy broadcasting rules"""
        numerator = np.array([[1.0, 2.0], [3.0, 4.0]])
        denominator = 2.0
        result = safe_divide(numerator, denominator)

        expected = np.array([[0.5, 1.0], [1.5, 2.0]])
        np.testing.assert_array_almost_equal(result, expected)

    def test_divide_mixed_broadcasting(self):
        """Test broadcasting with different shapes"""
        numerator = np.array([10.0, 20.0, 30.0])
        denominator = np.array([[2.0], [5.0]])
        result = safe_divide(numerator, denominator)

        expected = np.array([[5.0, 10.0, 15.0], [2.0, 4.0, 6.0]])
        np.testing.assert_array_almost_equal(result, expected)

    def test_divide_preserves_dtype_float(self):
        """Test that result is always float (even with integer inputs)"""
        result = safe_divide(10, 3)  # Integer inputs
        assert isinstance(result, float)
        assert abs(result - 3.333333) < 1e-5

# ==============================================================================
# Test safe_divide - Zero Division Protection
# ==============================================================================

class TestSafeDivideZeroProtection:
    """Test epsilon protection and zero division handling"""

    def test_divide_by_exact_zero_uses_fallback(self):
        """Test that exact zero uses fallback value"""
        result = safe_divide(10.0, 0.0, fallback=0.0)
        assert result == 0.0

        result_inf = safe_divide(10.0, 0.0, fallback=np.inf)
        assert result_inf == np.inf

        result_custom = safe_divide(10.0, 0.0, fallback=999.0)
        assert result_custom == 999.0

    def test_divide_by_near_zero_uses_epsilon(self):
        """Test that near-zero denominators use epsilon protection"""
        # Denominator < epsilon should be replaced with epsilon
        small_value = 1e-15  # Much smaller than EPSILON_DIV (1e-12)
        result = safe_divide(1.0, small_value, epsilon=1e-12)

        # Expected: 1.0 / 1e-12 = 1e12
        assert abs(result - 1e12) < 1e10  # Allow some numerical error

    def test_divide_epsilon_sign_preservation(self):
        """Test that epsilon protection preserves sign of denominator"""
        # Positive near-zero
        result_pos = safe_divide(1.0, 1e-15, epsilon=1e-12)
        assert result_pos > 0  # Should be positive

        # Negative near-zero
        result_neg = safe_divide(1.0, -1e-15, epsilon=1e-12)
        assert result_neg < 0  # Should be negative

    def test_divide_array_with_mixed_zeros(self):
        """Test array with exact zeros, near-zeros, and normal values"""
        numerator = np.array([1.0, 1.0, 1.0, 1.0])
        denominator = np.array([2.0, 0.0, 1e-15, -1e-15])
        result = safe_divide(numerator, denominator, epsilon=1e-12, fallback=0.0)

        # Check individual results
        assert abs(result[0] - 0.5) < 1e-10  # Normal division
        assert result[1] == 0.0  # Exact zero → fallback
        assert result[2] > 1e11  # Near-zero positive → large positive
        assert result[3] < -1e11  # Near-zero negative → large negative

    def test_divide_custom_epsilon(self):
        """Test custom epsilon value"""
        result = safe_divide(1.0, 1e-5, epsilon=1e-3)
        # With epsilon=1e-3, denominator 1e-5 < 1e-3, so use epsilon
        # Expected: 1.0 / 1e-3 = 1e3
        assert abs(result - 1e3) < 1e1

    def test_divide_epsilon_must_be_positive(self):
        """Test that epsilon must be positive"""
        with pytest.raises(ValueError, match="Epsilon must be positive"):
            safe_divide(1.0, 2.0, epsilon=0.0)

        with pytest.raises(ValueError, match="Epsilon must be positive"):
            safe_divide(1.0, 2.0, epsilon=-1e-12)

# ==============================================================================
# Test safe_divide - Warning System
# ==============================================================================

class TestSafeDivideWarnings:
    """Test warning system for division protection"""

    def test_divide_warns_on_exact_zero(self):
        """Test warning when dividing by exact zero"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            safe_divide(1.0, 0.0, warn=True, fallback=0.0)

            assert len(w) == 1
            assert "exactly zero" in str(w[0].message).lower()

    def test_divide_warns_on_near_zero(self):
        """Test warning when epsilon protection triggers"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            safe_divide(1.0, 1e-15, epsilon=1e-12, warn=True)

            assert len(w) == 1
            assert "near-zero" in str(w[0].message).lower() or "protected" in str(w[0].message).lower()

    def test_divide_no_warn_by_default(self):
        """Test that warnings are suppressed by default"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            safe_divide(1.0, 0.0, fallback=0.0)  # warn=False by default

            # Should NOT warn (warn=False is default)
            div_warnings = [x for x in w if "zero" in str(x.message).lower()]
            assert len(div_warnings) == 0

# ==============================================================================
# Test safe_reciprocal - Wrapper Validation
# ==============================================================================

class TestSafeReciprocal:
    """Test safe_reciprocal wrapper function"""

    def test_reciprocal_normal_values(self):
        """Test reciprocal with normal values"""
        assert safe_reciprocal(2.0) == 0.5
        assert safe_reciprocal(0.5) == 2.0
        assert safe_reciprocal(-2.0) == -0.5

    def test_reciprocal_arrays(self):
        """Test reciprocal with array inputs"""
        x = np.array([1.0, 2.0, 4.0, 0.5])
        result = safe_reciprocal(x)

        expected = np.array([1.0, 0.5, 0.25, 2.0])
        np.testing.assert_array_almost_equal(result, expected)

    def test_reciprocal_zero_protection(self):
        """Test that reciprocal protects against zero"""
        result = safe_reciprocal(0.0, fallback=0.0)
        assert result == 0.0

        result_inf = safe_reciprocal(0.0, fallback=np.inf)
        assert result_inf == np.inf

    def test_reciprocal_epsilon_protection(self):
        """Test epsilon protection in reciprocal"""
        small_value = 1e-15
        result = safe_reciprocal(small_value, epsilon=1e-12)

        # Expected: 1 / 1e-12 = 1e12
        assert abs(result - 1e12) < 1e10

    def test_reciprocal_equals_safe_divide(self):
        """Test that safe_reciprocal(x) == safe_divide(1, x)"""
        test_values = [2.0, -3.0, 0.5, 1e-15, -1e-15]

        for x in test_values:
            result_reciprocal = safe_reciprocal(x, epsilon=1e-12, fallback=0.0)
            result_divide = safe_divide(1.0, x, epsilon=1e-12, fallback=0.0)

            if np.isfinite(result_reciprocal) and np.isfinite(result_divide):
                assert abs(result_reciprocal - result_divide) < 1e-10

# ==============================================================================
# Test Edge Cases
# ==============================================================================

class TestSafeDivideEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_divide_with_inf(self):
        """Test division involving infinity"""
        assert safe_divide(np.inf, 2.0) == np.inf
        assert safe_divide(1.0, np.inf) == 0.0
        assert np.isnan(safe_divide(np.inf, np.inf))

    def test_divide_with_nan(self):
        """Test division involving NaN"""
        result = safe_divide(np.nan, 2.0)
        assert np.isnan(result)

        result = safe_divide(1.0, np.nan)
        assert np.isnan(result)

    def test_divide_large_arrays(self):
        """Test division with large arrays (performance check)"""
        numerator = np.random.randn(1000)
        denominator = np.random.randn(1000) + 1.0  # Avoid zeros
        result = safe_divide(numerator, denominator)

        assert result.shape == (1000,)
        assert np.all(np.isfinite(result))

    def test_divide_empty_array(self):
        """Test division with empty array"""
        numerator = np.array([])
        denominator = np.array([])
        result = safe_divide(numerator, denominator)

        assert result.shape == (0,)
        assert isinstance(result, np.ndarray)

    def test_divide_preserves_scalar_vs_array(self):
        """Test that scalar inputs return scalar, array inputs return array"""
        # Scalar inputs → scalar output
        scalar_result = safe_divide(1.0, 2.0)
        assert isinstance(scalar_result, float)
        assert not isinstance(scalar_result, np.ndarray)

        # Array inputs → array output
        array_result = safe_divide(np.array([1.0]), np.array([2.0]))
        assert isinstance(array_result, np.ndarray)

    def test_divide_very_small_epsilon(self):
        """Test behavior with very small epsilon (near machine precision)"""
        # Machine epsilon for float64 is ~2.22e-16
        tiny_epsilon = 1e-15
        result = safe_divide(1.0, 1e-16, epsilon=tiny_epsilon)

        # Should use epsilon protection
        assert abs(result - 1e15) < 1e13

# ==============================================================================
# Summary Test
# ==============================================================================

@pytest.mark.unit
def test_safe_division_summary():
    """Print summary of safe division test coverage"""
    print("\n" + "=" * 80)
    print(" Safe Division Tests - Week 3 Session 7")
    print("=" * 80)
    print(f" Module: src/utils/numerical_stability/safe_operations.py")
    print(f" Functions Tested: safe_divide, safe_reciprocal")
    print("-" * 80)
    print(" Test Suites:")
    print("   1. Normal Operations (5 tests)")
    print("   2. Zero Division Protection (6 tests)")
    print("   3. Warning System (3 tests)")
    print("   4. Reciprocal Wrapper (5 tests)")
    print("   5. Edge Cases (7 tests)")
    print("-" * 80)
    print(" Coverage Strategy:")
    print("   - Mathematical guarantees: safe_divide(a,b) = a/max(|b|,ε)*sign(b)")
    print("   - Edge cases: zero, near-zero, NaN, Inf, broadcasting")
    print("   - Warning system: warn=True/False behavior")
    print("   - Reciprocal: wrapper validation vs safe_divide")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
