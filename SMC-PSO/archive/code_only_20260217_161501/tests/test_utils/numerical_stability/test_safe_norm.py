#!/usr/bin/env python
"""
Numerical Stability Tests - Safe Norm and Normalize Operations (Week 3 Session 7)

PURPOSE: Comprehensive unit tests for safe_norm and safe_normalize
COVERAGE TARGET: 90-95% of normalization functions
STRATEGY: Test mathematical guarantees, zero-vector protection, unit vectors

TEST MATRIX:
1. safe_norm - Normal operations (L1, L2, Linf norms)
2. safe_norm - Zero-vector protection (min_norm threshold)
3. safe_norm - Multi-dimensional arrays (axis parameter)
4. safe_normalize - Unit vector generation (L2 norm)
5. safe_normalize - Zero-vector fallback handling
6. safe_normalize - Multi-dimensional normalization (axis parameter)
7. Edge cases - Single values, large arrays, different norm orders

Mathematical Guarantees Tested:
- safe_norm(v) = max(||v||_p, min_norm)
- safe_normalize(v) = v / max(||v||, min_norm)
- Unit vector property: ||safe_normalize(v)|| ≈ 1
- Zero-vector protection: safe_normalize([0,0]) = fallback

Author: Claude Code (Week 3 Session 7)
Date: December 2025
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Import safe operations
from src.utils.numerical_stability.safe_operations import (
    safe_norm,
    safe_normalize,
    EPSILON_SQRT,
)

# ==============================================================================
# Test safe_norm - Normal Operations
# ==============================================================================

class TestSafeNormNormal:
    """Test safe_norm with normal inputs"""

    def test_norm_l2_pythagorean(self):
        """Test L2 norm (Euclidean) with 3-4-5 triangle"""
        v = np.array([3.0, 4.0])
        result = safe_norm(v, ord=2)
        assert abs(result - 5.0) < 1e-10

    def test_norm_l1(self):
        """Test L1 norm (Manhattan distance)"""
        v = np.array([3.0, 4.0])
        result = safe_norm(v, ord=1)
        assert abs(result - 7.0) < 1e-10  # |3| + |4| = 7

    def test_norm_linf(self):
        """Test L∞ norm (maximum absolute value)"""
        v = np.array([3.0, -5.0, 2.0])
        result = safe_norm(v, ord=np.inf)
        assert abs(result - 5.0) < 1e-10  # max(|3|, |-5|, |2|) = 5

    def test_norm_default_is_l2(self):
        """Test that default norm is L2 (Euclidean)"""
        v = np.array([3.0, 4.0])
        result = safe_norm(v)  # No ord parameter
        assert abs(result - 5.0) < 1e-10

    def test_norm_unit_vector(self):
        """Test norm of unit vectors"""
        v = np.array([1.0, 0.0, 0.0])
        assert abs(safe_norm(v, ord=2) - 1.0) < 1e-10

        v = np.array([0.6, 0.8])  # 3-4-5 triangle normalized
        assert abs(safe_norm(v, ord=2) - 1.0) < 1e-10

# ==============================================================================
# Test safe_norm - Zero-Vector Protection
# ==============================================================================

class TestSafeNormZeroProtection:
    """Test protection against zero-norm vectors"""

    def test_norm_zero_vector_uses_min_norm(self):
        """Test that zero vector returns min_norm"""
        v = np.array([0.0, 0.0, 0.0])
        result = safe_norm(v, min_norm=1e-15)
        assert result == 1e-15

    def test_norm_very_small_vector_uses_min_norm(self):
        """Test that very small vectors use min_norm"""
        v = np.array([1e-20, 1e-20])
        result = safe_norm(v, min_norm=1e-15)

        # Actual norm would be sqrt(2)*1e-20 ~= 1.4e-20 < 1e-15
        assert result == 1e-15

    def test_norm_custom_min_norm(self):
        """Test custom min_norm parameter"""
        v = np.array([0.0, 0.0])
        result = safe_norm(v, min_norm=0.01)
        assert result == 0.01

# ==============================================================================
# Test safe_norm - Multi-Dimensional Arrays
# ==============================================================================

class TestSafeNormMultiDimensional:
    """Test norm with multi-dimensional arrays"""

    def test_norm_matrix_flatten(self):
        """Test norm of matrix (Frobenius norm for matrices)"""
        m = np.array([[3.0, 0.0], [0.0, 4.0]])
        result = safe_norm(m, ord='fro')  # Frobenius norm (like flattened L2)
        expected = np.sqrt(3**2 + 4**2)  # sqrt(25) = 5
        assert abs(result - expected) < 1e-10

    def test_norm_matrix_axis0(self):
        """Test norm along axis 0 (column norms)"""
        m = np.array([[3.0, 0.0], [0.0, 4.0]])
        result = safe_norm(m, ord=2, axis=0)

        expected = np.array([3.0, 4.0])
        np.testing.assert_array_almost_equal(result, expected)

    def test_norm_matrix_axis1(self):
        """Test norm along axis 1 (row norms)"""
        m = np.array([[3.0, 4.0], [5.0, 12.0]])
        result = safe_norm(m, ord=2, axis=1)

        expected = np.array([5.0, 13.0])  # 3-4-5, 5-12-13 triangles
        np.testing.assert_array_almost_equal(result, expected)

# ==============================================================================
# Test safe_normalize - Normal Operations
# ==============================================================================

class TestSafeNormalizeNormal:
    """Test safe_normalize with normal inputs"""

    def test_normalize_creates_unit_vector(self):
        """Test that normalize produces unit vector"""
        v = np.array([3.0, 4.0])
        result = safe_normalize(v)

        # Should be [0.6, 0.8]
        expected = np.array([0.6, 0.8])
        np.testing.assert_array_almost_equal(result, expected)

        # Verify it's a unit vector
        norm = safe_norm(result, ord=2)
        assert abs(norm - 1.0) < 1e-10

    def test_normalize_preserves_direction(self):
        """Test that normalize preserves vector direction"""
        v = np.array([10.0, 20.0, 30.0])
        result = safe_normalize(v)

        # Direction preserved (proportional)
        assert abs(result[0] / result[1] - v[0] / v[1]) < 1e-10
        assert abs(result[1] / result[2] - v[1] / v[2]) < 1e-10

    def test_normalize_different_norms(self):
        """Test normalize with different norm orders"""
        v = np.array([3.0, 4.0])

        # L1 normalization
        result_l1 = safe_normalize(v, ord=1)
        assert abs(safe_norm(result_l1, ord=1) - 1.0) < 1e-10

        # L2 normalization
        result_l2 = safe_normalize(v, ord=2)
        assert abs(safe_norm(result_l2, ord=2) - 1.0) < 1e-10

    def test_normalize_already_unit_vector(self):
        """Test normalizing an already-unit vector"""
        v = np.array([1.0, 0.0, 0.0])
        result = safe_normalize(v)

        np.testing.assert_array_almost_equal(result, v)

# ==============================================================================
# Test safe_normalize - Zero-Vector Handling
# ==============================================================================

class TestSafeNormalizeZeroVectors:
    """Test handling of zero-length vectors"""

    def test_normalize_zero_vector_default_fallback(self):
        """Test that zero vector returns zero by default"""
        v = np.array([0.0, 0.0, 0.0])
        result = safe_normalize(v)

        # Default fallback is zero vector
        expected = np.array([0.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(result, expected)

    def test_normalize_zero_vector_custom_fallback(self):
        """Test zero vector with custom fallback"""
        v = np.array([0.0, 0.0])
        fallback = np.array([1.0, 0.0])
        result = safe_normalize(v, fallback=fallback)

        np.testing.assert_array_almost_equal(result, fallback)

    def test_normalize_very_small_vector(self):
        """Test normalization of very small vector (near-zero)"""
        v = np.array([1e-20, 1e-20])
        result = safe_normalize(v, min_norm=1e-15)

        # Should normalize using min_norm protection (result won't be unit vector)
        assert np.all(np.isfinite(result))
        # Result should be v / min_norm = [1e-20, 1e-20] / 1e-15 = [1e-5, 1e-5]
        expected = np.array([1e-5, 1e-5])
        np.testing.assert_array_almost_equal(result, expected, decimal=20)

# ==============================================================================
# Test safe_normalize - Multi-Dimensional Normalization
# ==============================================================================

class TestSafeNormalizeMultiDimensional:
    """Test normalization of multi-dimensional arrays"""

    def test_normalize_matrix_rows(self):
        """Test normalizing each row independently"""
        m = np.array([[3.0, 4.0], [5.0, 12.0]])
        result = safe_normalize(m, axis=1)

        # Each row should be unit vector
        expected = np.array([[0.6, 0.8], [5.0/13.0, 12.0/13.0]])
        np.testing.assert_array_almost_equal(result, expected)

        # Verify each row is unit vector
        for i in range(result.shape[0]):
            row_norm = safe_norm(result[i, :], ord=2)
            assert abs(row_norm - 1.0) < 1e-10

    def test_normalize_matrix_columns(self):
        """Test normalizing each column independently"""
        m = np.array([[3.0, 0.0], [4.0, 5.0]])
        result = safe_normalize(m, axis=0)

        # Each column should be unit vector
        for j in range(result.shape[1]):
            col_norm = safe_norm(result[:, j], ord=2)
            assert abs(col_norm - 1.0) < 1e-10

# ==============================================================================
# Test Edge Cases
# ==============================================================================

class TestSafeNormNormalizeEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_norm_single_value(self):
        """Test norm of single value"""
        v = np.array([5.0])
        result = safe_norm(v, ord=2)
        assert abs(result - 5.0) < 1e-10

    def test_normalize_single_value(self):
        """Test normalize of single value"""
        v = np.array([5.0])
        result = safe_normalize(v)
        np.testing.assert_array_almost_equal(result, np.array([1.0]))

    def test_norm_negative_values(self):
        """Test norm with negative values (magnitude only)"""
        v = np.array([-3.0, -4.0])
        result = safe_norm(v, ord=2)
        assert abs(result - 5.0) < 1e-10  # Same as [3, 4]

    def test_normalize_negative_values(self):
        """Test normalize with negative values (direction preserved)"""
        v = np.array([-3.0, -4.0])
        result = safe_normalize(v)

        expected = np.array([-0.6, -0.8])
        np.testing.assert_array_almost_equal(result, expected)

    def test_norm_large_arrays(self):
        """Test performance with large arrays"""
        v = np.random.randn(1000)
        result = safe_norm(v, ord=2)

        assert np.isfinite(result)
        assert result > 0

    def test_normalize_preserves_shape(self):
        """Test that normalize preserves input shape"""
        v_1d = np.array([1.0, 2.0, 3.0])
        result_1d = safe_normalize(v_1d)
        assert result_1d.shape == v_1d.shape

        v_2d = np.array([[1.0, 2.0], [3.0, 4.0]])
        result_2d = safe_normalize(v_2d, axis=1)
        assert result_2d.shape == v_2d.shape

# ==============================================================================
# Summary Test
# ==============================================================================

@pytest.mark.unit
def test_safe_norm_summary():
    """Print summary of safe norm test coverage"""
    print("\n" + "=" * 80)
    print(" Safe Norm/Normalize Tests - Week 3 Session 7")
    print("=" * 80)
    print(f" Module: src/utils/numerical_stability/safe_operations.py")
    print(f" Functions Tested: safe_norm, safe_normalize")
    print("-" * 80)
    print(" Test Suites:")
    print("   1. Norm Normal Operations (5 tests)")
    print("   2. Norm Zero Protection (3 tests)")
    print("   3. Norm Multi-Dimensional (3 tests)")
    print("   4. Normalize Normal Operations (4 tests)")
    print("   5. Normalize Zero Vectors (3 tests)")
    print("   6. Normalize Multi-Dimensional (2 tests)")
    print("   7. Edge Cases (7 tests)")
    print("-" * 80)
    print(" Coverage Strategy:")
    print("   - Mathematical guarantees: safe_norm(v) = max(||v||,ε)")
    print("   - Mathematical guarantees: safe_normalize(v) = v/max(||v||,ε)")
    print("   - Unit vector property: ||safe_normalize(v)|| ≈ 1")
    print("   - Zero-vector protection: Fallback handling")
    print("   - Norm orders: L1, L2, L∞")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
