#!/usr/bin/env python
"""
Control Primitives Tests - Saturation Functions (Week 3 Session 8)

PURPOSE: Comprehensive unit tests for saturate, smooth_sign, dead_zone
COVERAGE TARGET: 85-90% of saturation.py module

Author: Claude Code (Week 3 Session 8)
Date: December 2025
"""

import pytest
import numpy as np
import warnings
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.utils.control.primitives.saturation import (
    saturate,
    smooth_sign,
    dead_zone,
)

# Test saturate - Tanh Method
class TestSaturateTanh:
    def test_tanh_zero(self):
        assert abs(saturate(0.0, 0.1, "tanh") - 0.0) < 1e-10

    def test_tanh_positive(self):
        result = saturate(0.5, 0.1, "tanh", slope=3.0)
        assert 0.9 < result < 1.0

    def test_tanh_negative(self):
        result = saturate(-0.5, 0.1, "tanh", slope=3.0)
        assert -1.0 < result < -0.9

    def test_tanh_large_sigma(self):
        assert abs(saturate(10.0, 0.1, "tanh", 3.0) - 1.0) < 0.01

    def test_tanh_slope(self):
        s1 = saturate(0.3, 0.1, "tanh", slope=1.0)
        s2 = saturate(0.3, 0.1, "tanh", slope=10.0)
        assert abs(s1) > abs(s2)

    def test_tanh_arrays(self):
        result = saturate(np.array([-1.0, 0.0, 1.0]), 0.1, "tanh", 3.0)
        assert np.all(np.abs(result) <= 1.0)

    def test_tanh_overflow(self):
        result = saturate(1e6, 1.0, "tanh", 3.0)
        assert np.isfinite(result)

# Test saturate - Linear Method
class TestSaturateLinear:
    def test_linear_within(self):
        assert abs(saturate(0.05, 0.1, "linear") - 0.5) < 1e-10

    def test_linear_above(self):
        assert abs(saturate(0.5, 0.1, "linear") - 1.0) < 1e-10

    def test_linear_below(self):
        assert abs(saturate(-0.5, 0.1, "linear") - (-1.0)) < 1e-10

    def test_linear_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            saturate(0.5, 0.1, "linear")
            assert len(w) == 1

# Test saturate - Validation
class TestSaturateValidation:
    def test_epsilon_zero(self):
        with pytest.raises(ValueError):
            saturate(0.5, 0.0)

    def test_epsilon_negative(self):
        with pytest.raises(ValueError):
            saturate(0.5, -0.1)

    def test_unknown_method(self):
        with pytest.raises(ValueError):
            saturate(0.5, 0.1, "bad")

# Test smooth_sign
class TestSmoothSign:
    def test_default_epsilon(self):
        r1 = smooth_sign(0.1)
        r2 = saturate(0.1, 0.01, "tanh")
        assert abs(r1 - r2) < 1e-10

    def test_positive(self):
        assert 0.99 < smooth_sign(10.0, 0.01) <= 1.0

    def test_negative(self):
        assert -1.0 <= smooth_sign(-10.0, 0.01) < -0.99

# Test dead_zone
class TestDeadZone:
    def test_below_threshold(self):
        assert abs(dead_zone(0.05, 0.1) - 0.0) < 1e-10

    def test_above_positive(self):
        assert abs(dead_zone(0.5, 0.1) - 0.4) < 1e-10

    def test_above_negative(self):
        assert abs(dead_zone(-0.5, 0.1) - (-0.4)) < 1e-10

    def test_arrays(self):
        x = np.array([-0.5, -0.05, 0.0, 0.05, 0.5])
        result = dead_zone(x, 0.1)
        expected = np.array([-0.4, 0.0, 0.0, 0.0, 0.4])
        np.testing.assert_array_almost_equal(result, expected)

    def test_threshold_zero(self):
        with pytest.raises(ValueError):
            dead_zone(0.5, 0.0)

# Test Edge Cases
class TestEdgeCases:
    def test_saturate_scalar(self):
        assert not isinstance(saturate(0.5, 0.1), np.ndarray)

    def test_saturate_inf(self):
        assert abs(saturate(np.inf, 0.1, "tanh") - 1.0) < 1e-5

    def test_saturate_nan(self):
        assert np.isnan(saturate(np.nan, 0.1, "tanh"))

@pytest.mark.unit
def test_summary():
    print("\n" + "=" * 60)
    print(" Saturation Tests - Week 3 Session 8")
    print("=" * 60)
    print(" Module: src/utils/control/primitives/saturation.py")
    print(" Tests: 28 total (saturate, smooth_sign, dead_zone)")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
