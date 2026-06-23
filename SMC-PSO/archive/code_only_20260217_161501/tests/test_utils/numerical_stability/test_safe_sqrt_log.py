#!/usr/bin/env python
"""
Numerical Stability Tests - Safe Sqrt and Log Operations (Week 3 Session 7)

PURPOSE: Comprehensive unit tests for safe_sqrt and safe_log
COVERAGE TARGET: 90-95% of domain-protected functions
STRATEGY: Test mathematical guarantees, negative/zero handling, warnings

TEST MATRIX:
1. safe_sqrt - Normal operations (positive values, arrays)
2. safe_sqrt - Negative value protection (clipping, min_value)
3. safe_sqrt - Edge cases (zero, very small, very large)
4. safe_log - Normal operations (positive values, e, arrays)
5. safe_log - Zero/negative protection (clipping, min_value)
6. safe_log - Edge cases (underflow, overflow, infinity)
7. Warning system for both functions

Mathematical Guarantees Tested:
- safe_sqrt(x) = √(max(x, min_value))
- safe_log(x) = ln(max(x, min_value))
- Domain protection prevents NaN from negative/zero inputs

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
    safe_sqrt,
    safe_log,
    EPSILON_SQRT,
    EPSILON_LOG,
)

# ==============================================================================
# Test safe_sqrt - Normal Operations
# ==============================================================================

class TestSafeSqrtNormal:
    """Test safe_sqrt with normal (positive) inputs"""

    def test_sqrt_positive_scalars(self):
        """Test square root of positive scalars"""
        assert safe_sqrt(4.0) == 2.0
        assert safe_sqrt(9.0) == 3.0
        assert safe_sqrt(1.0) == 1.0
        assert abs(safe_sqrt(2.0) - 1.414213562) < 1e-8

    def test_sqrt_positive_arrays(self):
        """Test square root of positive arrays"""
        x = np.array([1.0, 4.0, 9.0, 16.0])
        result = safe_sqrt(x)

        expected = np.array([1.0, 2.0, 3.0, 4.0])
        np.testing.assert_array_almost_equal(result, expected)

    def test_sqrt_small_positive_values(self):
        """Test sqrt with small but positive values"""
        x = 1e-10
        result = safe_sqrt(x)

        expected = np.sqrt(1e-10)  # ~3.16e-6
        assert abs(result - expected) < 1e-12

    def test_sqrt_large_values(self):
        """Test sqrt with large values"""
        assert safe_sqrt(1e10) == 1e5
        assert safe_sqrt(1e20) == 1e10

# ==============================================================================
# Test safe_sqrt - Negative Value Protection
# ==============================================================================

class TestSafeSqrtNegativeProtection:
    """Test protection against negative values"""

    def test_sqrt_zero_uses_min_value(self):
        """Test that sqrt(0) uses min_value protection"""
        result = safe_sqrt(0.0, min_value=1e-15)
        expected = np.sqrt(1e-15)
        assert abs(result - expected) < 1e-20

    def test_sqrt_negative_uses_min_value(self):
        """Test that negative values are clipped to min_value"""
        result = safe_sqrt(-0.01, min_value=1e-15)
        expected = np.sqrt(1e-15)
        assert abs(result - expected) < 1e-20

    def test_sqrt_custom_min_value(self):
        """Test custom min_value parameter"""
        result = safe_sqrt(-5.0, min_value=0.01)
        expected = np.sqrt(0.01)  # 0.1
        assert abs(result - expected) < 1e-10

    def test_sqrt_min_value_must_be_non_negative(self):
        """Test that min_value must be non-negative"""
        with pytest.raises(ValueError, match="min_value must be non-negative"):
            safe_sqrt(1.0, min_value=-1e-10)

    def test_sqrt_array_with_mixed_signs(self):
        """Test array with positive, zero, and negative values"""
        x = np.array([4.0, 0.0, -0.001, 9.0, -1e-10])
        result = safe_sqrt(x, min_value=1e-15)

        # Check that all results are valid (no NaN)
        assert np.all(np.isfinite(result))
        assert np.all(result >= 0)  # All sqrt results should be non-negative

        # Check specific values
        assert abs(result[0] - 2.0) < 1e-10  # sqrt(4) = 2
        assert abs(result[3] - 3.0) < 1e-10  # sqrt(9) = 3

# ==============================================================================
# Test safe_sqrt - Warning System
# ==============================================================================

class TestSafeSqrtWarnings:
    """Test warning system for sqrt"""

    def test_sqrt_warns_on_negative(self):
        """Test warning when negative values are clipped"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            safe_sqrt(-0.01, min_value=1e-15, warn=True)

            assert len(w) == 1
            assert "negative" in str(w[0].message).lower() or "clipped" in str(w[0].message).lower()

    def test_sqrt_no_warn_by_default(self):
        """Test that warnings are suppressed by default"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            safe_sqrt(-0.01, min_value=1e-15)  # warn=False by default

            sqrt_warnings = [x for x in w if "negative" in str(x.message).lower()]
            assert len(sqrt_warnings) == 0

# ==============================================================================
# Test safe_log - Normal Operations
# ==============================================================================

class TestSafeLogNormal:
    """Test safe_log with normal (positive) inputs"""

    def test_log_positive_scalars(self):
        """Test natural logarithm of positive scalars"""
        assert abs(safe_log(np.e) - 1.0) < 1e-10
        assert abs(safe_log(1.0) - 0.0) < 1e-10
        assert abs(safe_log(np.e**2) - 2.0) < 1e-10

    def test_log_positive_arrays(self):
        """Test logarithm of positive arrays"""
        x = np.array([1.0, np.e, np.e**2, np.e**3])
        result = safe_log(x)

        expected = np.array([0.0, 1.0, 2.0, 3.0])
        np.testing.assert_array_almost_equal(result, expected, decimal=10)

    def test_log_large_values(self):
        """Test log with large values"""
        result = safe_log(1e10)
        expected = np.log(1e10)  # ~23.0258509
        assert abs(result - expected) < 1e-6

# ==============================================================================
# Test safe_log - Zero/Negative Protection
# ==============================================================================

class TestSafeLogZeroNegativeProtection:
    """Test protection against zero and negative values"""

    def test_log_zero_uses_min_value(self):
        """Test that log(0) uses min_value protection"""
        result = safe_log(0.0, min_value=1e-15)
        expected = np.log(1e-15)  # ~-34.538776
        assert abs(result - expected) < 1e-6

    def test_log_negative_uses_min_value(self):
        """Test that negative values are clipped to min_value"""
        result = safe_log(-0.01, min_value=1e-15)
        expected = np.log(1e-15)
        assert abs(result - expected) < 1e-6

    def test_log_custom_min_value(self):
        """Test custom min_value parameter"""
        result = safe_log(0.0, min_value=0.01)
        expected = np.log(0.01)  # ~-4.605170
        assert abs(result - expected) < 1e-6

    def test_log_min_value_must_be_positive(self):
        """Test that min_value must be positive"""
        with pytest.raises(ValueError, match="min_value must be positive"):
            safe_log(1.0, min_value=0.0)

        with pytest.raises(ValueError, match="min_value must be positive"):
            safe_log(1.0, min_value=-1e-10)

    def test_log_array_with_mixed_signs(self):
        """Test array with positive, zero, and negative values"""
        x = np.array([np.e, 0.0, -0.001, 1.0, -1e-20])
        result = safe_log(x, min_value=1e-15)

        # Check that all results are finite
        assert np.all(np.isfinite(result))

        # Check specific values
        assert abs(result[0] - 1.0) < 1e-10  # log(e) = 1
        assert abs(result[3] - 0.0) < 1e-10  # log(1) = 0

# ==============================================================================
# Test safe_log - Warning System
# ==============================================================================

class TestSafeLogWarnings:
    """Test warning system for log"""

    def test_log_warns_on_non_positive(self):
        """Test warning when zero/negative values are clipped"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            safe_log(0.0, min_value=1e-15, warn=True)

            assert len(w) == 1
            assert ("non-positive" in str(w[0].message).lower() or
                    "clipped" in str(w[0].message).lower())

    def test_log_no_warn_by_default(self):
        """Test that warnings are suppressed by default"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            safe_log(0.0, min_value=1e-15)  # warn=False by default

            log_warnings = [x for x in w if "clipped" in str(x.message).lower()]
            assert len(log_warnings) == 0

# ==============================================================================
# Test Edge Cases
# ==============================================================================

class TestSafeSqrtLogEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_sqrt_with_inf(self):
        """Test sqrt with infinity"""
        assert safe_sqrt(np.inf) == np.inf

    def test_sqrt_with_nan(self):
        """Test sqrt with NaN (should preserve NaN)"""
        result = safe_sqrt(np.nan, min_value=1e-15)
        assert np.isnan(result)

    def test_log_with_inf(self):
        """Test log with infinity"""
        assert safe_log(np.inf, min_value=1e-15) == np.inf

    def test_log_with_nan(self):
        """Test log with NaN (should preserve NaN)"""
        result = safe_log(np.nan, min_value=1e-15)
        assert np.isnan(result)

    def test_sqrt_preserves_scalar_vs_array(self):
        """Test that scalar inputs return scalar, array inputs return array"""
        scalar_result = safe_sqrt(4.0)
        assert isinstance(scalar_result, float)
        assert not isinstance(scalar_result, np.ndarray)

        array_result = safe_sqrt(np.array([4.0]))
        assert isinstance(array_result, np.ndarray)

    def test_log_preserves_scalar_vs_array(self):
        """Test that scalar inputs return scalar, array inputs return array"""
        scalar_result = safe_log(np.e)
        assert isinstance(scalar_result, float)
        assert not isinstance(scalar_result, np.ndarray)

        array_result = safe_log(np.array([np.e]))
        assert isinstance(array_result, np.ndarray)

    def test_sqrt_log_large_arrays(self):
        """Test performance with large arrays"""
        x = np.abs(np.random.randn(1000)) + 0.1  # Ensure positive
        result_sqrt = safe_sqrt(x)
        result_log = safe_log(x)

        assert result_sqrt.shape == (1000,)
        assert result_log.shape == (1000,)
        assert np.all(np.isfinite(result_sqrt))
        assert np.all(np.isfinite(result_log))

# ==============================================================================
# Summary Test
# ==============================================================================

@pytest.mark.unit
def test_safe_sqrt_log_summary():
    """Print summary of safe sqrt/log test coverage"""
    print("\n" + "=" * 80)
    print(" Safe Sqrt/Log Tests - Week 3 Session 7")
    print("=" * 80)
    print(f" Module: src/utils/numerical_stability/safe_operations.py")
    print(f" Functions Tested: safe_sqrt, safe_log")
    print("-" * 80)
    print(" Test Suites:")
    print("   1. Sqrt Normal Operations (4 tests)")
    print("   2. Sqrt Negative Protection (5 tests)")
    print("   3. Sqrt Warning System (2 tests)")
    print("   4. Log Normal Operations (3 tests)")
    print("   5. Log Zero/Negative Protection (5 tests)")
    print("   6. Log Warning System (2 tests)")
    print("   7. Edge Cases (7 tests)")
    print("-" * 80)
    print(" Coverage Strategy:")
    print("   - Mathematical guarantees: safe_sqrt(x) = √max(x,ε)")
    print("   - Mathematical guarantees: safe_log(x) = ln(max(x,ε))")
    print("   - Domain protection: Negative/zero handling")
    print("   - Warning system: warn=True/False behavior")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
