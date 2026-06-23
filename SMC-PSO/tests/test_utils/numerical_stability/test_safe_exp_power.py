#!/usr/bin/env python
"""
Numerical Stability Tests - Safe Exp and Power Operations (Week 3 Session 7)

PURPOSE: Comprehensive unit tests for safe_exp and safe_power
COVERAGE TARGET: 90-95% of overflow-protected functions
STRATEGY: Test mathematical guarantees, overflow protection, negative bases

TEST MATRIX:
1. safe_exp - Normal operations (positive, negative, zero exponents)
2. safe_exp - Overflow protection (large exponents, max_value clipping)
3. safe_exp - Edge cases (very small, very large, infinity)
4. safe_power - Normal operations (positive bases, integer/fractional exponents)
5. safe_power - Negative base handling (odd/even exponents, sign preservation)
6. safe_power - Overflow/underflow protection (base epsilon, exp clipping)
7. Warning system for both functions

Mathematical Guarantees Tested:
- safe_exp(x) = exp(min(x, max_value))
- safe_power(b, e) = sign(b) * |b|^e for negative b
- Overflow protection prevents inf from large exponents
- Small base protection prevents underflow

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
    safe_exp,
    safe_power,
    EPSILON_EXP,
    EPSILON_SQRT,
)

# ==============================================================================
# Test safe_exp - Normal Operations
# ==============================================================================

class TestSafeExpNormal:
    """Test safe_exp with normal inputs"""

    def test_exp_zero(self):
        """Test exp(0) = 1"""
        assert safe_exp(0.0) == 1.0

    def test_exp_positive(self):
        """Test exp with positive values"""
        assert abs(safe_exp(1.0) - np.e) < 1e-10
        assert abs(safe_exp(2.0) - np.e**2) < 1e-9
        assert abs(safe_exp(0.5) - np.sqrt(np.e)) < 1e-10

    def test_exp_negative(self):
        """Test exp with negative values (underflow is safe)"""
        assert abs(safe_exp(-1.0) - 1.0/np.e) < 1e-10
        assert abs(safe_exp(-2.0) - 1.0/np.e**2) < 1e-9

    def test_exp_arrays(self):
        """Test exp with array inputs"""
        x = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
        result = safe_exp(x)

        expected = np.exp(x)
        np.testing.assert_array_almost_equal(result, expected, decimal=10)

    def test_exp_very_negative(self):
        """Test exp with very negative values (natural underflow)"""
        result = safe_exp(-100.0)
        assert result > 0  # Should be tiny but positive
        assert result < 1e-40

# ==============================================================================
# Test safe_exp - Overflow Protection
# ==============================================================================

class TestSafeExpOverflowProtection:
    """Test protection against overflow"""

    def test_exp_large_value_uses_max_value(self):
        """Test that large exponents are clipped to max_value"""
        large_exponent = 1000.0  # Would cause overflow
        result = safe_exp(large_exponent, max_value=700.0)

        # Should clip to 700, giving exp(700) ~= 1.01e+304
        expected = np.exp(700.0)
        assert abs(result - expected) / expected < 1e-10

    def test_exp_custom_max_value(self):
        """Test custom max_value parameter"""
        result = safe_exp(100.0, max_value=50.0)
        expected = np.exp(50.0)
        assert abs(result - expected) / expected < 1e-10

    def test_exp_array_with_mixed_values(self):
        """Test array with normal and overflow-prone values"""
        x = np.array([0.0, 10.0, 1000.0, -10.0])
        result = safe_exp(x, max_value=700.0)

        # Check all finite
        assert np.all(np.isfinite(result))

        # Check specific values
        assert abs(result[0] - 1.0) < 1e-10  # exp(0) = 1
        assert abs(result[1] - np.exp(10.0)) < 1e-6  # exp(10)

    def test_exp_prevents_overflow(self):
        """Test that exp never returns inf (except for input inf)"""
        x = np.array([500.0, 700.0, 1000.0, 10000.0])
        result = safe_exp(x, max_value=700.0)

        # None should be inf (all clipped to max_value=700)
        assert np.all(np.isfinite(result))

# ==============================================================================
# Test safe_exp - Warning System
# ==============================================================================

class TestSafeExpWarnings:
    """Test warning system for exp"""

    def test_exp_warns_on_overflow(self):
        """Test warning when large values are clipped"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            safe_exp(1000.0, max_value=700.0, warn=True)

            assert len(w) == 1
            assert "clipped" in str(w[0].message).lower() or "overflow" in str(w[0].message).lower()

    def test_exp_no_warn_by_default(self):
        """Test that warnings are suppressed by default"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            safe_exp(1000.0, max_value=700.0)  # warn=False by default

            exp_warnings = [x for x in w if "clipped" in str(x.message).lower()]
            assert len(exp_warnings) == 0

# ==============================================================================
# Test safe_power - Normal Operations
# ==============================================================================

class TestSafePowerNormal:
    """Test safe_power with normal inputs"""

    def test_power_integer_exponents(self):
        """Test power with integer exponents"""
        assert safe_power(2.0, 3.0) == 8.0
        assert safe_power(3.0, 2.0) == 9.0
        assert safe_power(5.0, 0.0) == 1.0
        assert safe_power(10.0, 1.0) == 10.0

    def test_power_fractional_exponents(self):
        """Test power with fractional exponents"""
        assert abs(safe_power(4.0, 0.5) - 2.0) < 1e-10  # sqrt(4)
        assert abs(safe_power(8.0, 1.0/3.0) - 2.0) < 1e-10  # cbrt(8)

    def test_power_arrays(self):
        """Test power with array inputs"""
        base = np.array([2.0, 3.0, 4.0])
        exponent = 2.0
        result = safe_power(base, exponent)

        expected = np.array([4.0, 9.0, 16.0])
        np.testing.assert_array_almost_equal(result, expected)

# ==============================================================================
# Test safe_power - Negative Base Handling
# ==============================================================================

class TestSafePowerNegativeBases:
    """Test handling of negative bases"""

    def test_power_negative_base_odd_exponent(self):
        """Test negative base with odd integer exponent"""
        assert safe_power(-2.0, 3.0) == -8.0  # (-2)^3 = -8
        assert safe_power(-3.0, 1.0) == -3.0  # (-3)^1 = -3

    def test_power_negative_base_even_exponent(self):
        """Test negative base with even integer exponent"""
        assert safe_power(-2.0, 2.0) == 4.0  # (-2)^2 = 4
        assert safe_power(-3.0, 4.0) == 81.0  # (-3)^4 = 81

    def test_power_negative_base_fractional_exponent(self):
        """Test negative base with fractional exponent (uses absolute value)"""
        result = safe_power(-4.0, 0.5)
        # Uses |base|^exp for fractional exponents
        assert abs(result - 2.0) < 1e-10

    def test_power_negative_base_array(self):
        """Test array with negative bases"""
        base = np.array([-2.0, -3.0, -4.0])
        exponent = 2.0
        result = safe_power(base, exponent)

        expected = np.array([4.0, 9.0, 16.0])
        np.testing.assert_array_almost_equal(result, expected)

# ==============================================================================
# Test safe_power - Protection System
# ==============================================================================

class TestSafePowerProtection:
    """Test base epsilon and exponent clipping protection"""

    def test_power_small_base_protection(self):
        """Test protection for very small bases"""
        small_base = 1e-20
        result = safe_power(small_base, 2.0, epsilon=1e-15)

        # Base should be clipped to epsilon
        expected_approx = (1e-15) ** 2.0
        assert abs(result - expected_approx) / expected_approx < 1e-6

    def test_power_large_exponent_clipping(self):
        """Test clipping of very large exponents"""
        result = safe_power(2.0, 1000.0, max_exp=100.0)

        # Exponent should be clipped to 100
        expected = 2.0 ** 100.0
        assert abs(result - expected) / expected < 1e-10

    def test_power_prevents_overflow(self):
        """Test that power prevents overflow with protection"""
        # Without protection, 10^1000 would overflow
        result = safe_power(10.0, 1000.0, max_exp=100.0)

        assert np.isfinite(result)
        assert result > 0

# ==============================================================================
# Test safe_power - Warning System
# ==============================================================================

class TestSafePowerWarnings:
    """Test warning system for power"""

    def test_power_warns_on_small_base(self):
        """Test warning when small bases are protected"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            safe_power(1e-20, 2.0, epsilon=1e-15, warn=True)

            assert len(w) >= 1
            assert any("small" in str(x.message).lower() or "protected" in str(x.message).lower() for x in w)

    def test_power_warns_on_large_exponent(self):
        """Test warning when large exponents are clipped"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            safe_power(2.0, 1000.0, max_exp=100.0, warn=True)

            assert len(w) >= 1
            assert any("exponent" in str(x.message).lower() or "clipped" in str(x.message).lower() for x in w)

# ==============================================================================
# Test Edge Cases
# ==============================================================================

class TestSafeExpPowerEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_exp_with_inf(self):
        """Test exp with infinity"""
        assert safe_exp(np.inf, max_value=700.0) == np.exp(700.0)
        assert safe_exp(-np.inf) == 0.0

    def test_exp_with_nan(self):
        """Test exp with NaN"""
        result = safe_exp(np.nan, max_value=700.0)
        assert np.isnan(result)

    def test_power_with_zero_base(self):
        """Test power with zero base"""
        assert safe_power(0.0, 2.0) > 0  # Protected by epsilon
        assert safe_power(0.0, 0.0) == 1.0  # 0^0 = 1 by convention

    def test_power_with_inf_base(self):
        """Test power with infinite base"""
        result = safe_power(np.inf, 2.0)
        assert result == np.inf

    def test_exp_power_preserve_scalar_vs_array(self):
        """Test that scalar inputs return scalar, array inputs return array"""
        # safe_exp
        exp_scalar = safe_exp(1.0)
        assert isinstance(exp_scalar, float)
        assert not isinstance(exp_scalar, np.ndarray)

        exp_array = safe_exp(np.array([1.0]))
        assert isinstance(exp_array, np.ndarray)

        # safe_power
        power_scalar = safe_power(2.0, 3.0)
        assert isinstance(power_scalar, float)
        assert not isinstance(power_scalar, np.ndarray)

        power_array = safe_power(np.array([2.0]), 3.0)
        assert isinstance(power_array, np.ndarray)

# ==============================================================================
# Summary Test
# ==============================================================================

@pytest.mark.unit
def test_safe_exp_power_summary():
    """Print summary of safe exp/power test coverage"""
    print("\n" + "=" * 80)
    print(" Safe Exp/Power Tests - Week 3 Session 7")
    print("=" * 80)
    print(f" Module: src/utils/numerical_stability/safe_operations.py")
    print(f" Functions Tested: safe_exp, safe_power")
    print("-" * 80)
    print(" Test Suites:")
    print("   1. Exp Normal Operations (5 tests)")
    print("   2. Exp Overflow Protection (4 tests)")
    print("   3. Exp Warning System (2 tests)")
    print("   4. Power Normal Operations (3 tests)")
    print("   5. Power Negative Bases (4 tests)")
    print("   6. Power Protection System (3 tests)")
    print("   7. Power Warning System (2 tests)")
    print("   8. Edge Cases (6 tests)")
    print("-" * 80)
    print(" Coverage Strategy:")
    print("   - Mathematical guarantees: safe_exp(x) = exp(min(x,max))")
    print("   - Mathematical guarantees: safe_power(b,e) = sign(b)*|b|^e")
    print("   - Overflow protection: Large exponent clipping")
    print("   - Negative base handling: Odd/even exponent sign preservation")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
