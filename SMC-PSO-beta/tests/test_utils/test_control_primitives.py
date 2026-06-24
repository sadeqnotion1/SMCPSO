#======================================================================================
#==================== tests/test_utils/test_control_primitives.py =====================
#======================================================================================

"""Tests for utils.control.primitives.saturation (M3 slice 2)."""
from __future__ import annotations

import os
import sys
import math
import warnings

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils.control.primitives.saturation import saturate, smooth_sign, dead_zone
from utils import saturate as saturate_via_top
from utils.control.primitives import saturate as saturate_via_pkg


def test_saturate_rejects_nonpositive_epsilon():
    with pytest.raises(ValueError):
        saturate(1.0, 0.0)
    with pytest.raises(ValueError):
        saturate(1.0, -0.5)


def test_saturate_unknown_method_raises():
    with pytest.raises(ValueError):
        saturate(1.0, 0.1, method="cubic")


def test_saturate_zero_is_zero():
    assert float(saturate(0.0, 0.1)) == 0.0


def test_saturate_tanh_bounded_and_odd():
    hi = float(saturate(50.0, 0.1, method="tanh"))
    lo = float(saturate(-50.0, 0.1, method="tanh"))
    assert -1.0 <= lo <= 1.0
    assert -1.0 <= hi <= 1.0
    assert hi > 0.99
    assert lo < -0.99
    assert math.isclose(hi, -lo, rel_tol=1e-9, abs_tol=1e-9)


def test_saturate_higher_slope_is_gentler():
    # code computes tanh(sigma/(epsilon*slope)); larger slope -> smaller arg -> gentler
    gentle = abs(float(saturate(0.1, 1.0, method="tanh", slope=3.0)))
    steep = abs(float(saturate(0.1, 1.0, method="tanh", slope=1.0)))
    assert gentle < steep


def test_saturate_linear_clips_and_warns():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        out = saturate(10.0, 1.0, method="linear")
        assert float(out) == 1.0
        assert any(issubclass(x.category, RuntimeWarning) for x in w)
    assert float(saturate(-10.0, 1.0, method="linear")) == -1.0
    assert math.isclose(float(saturate(0.5, 1.0, method="linear")), 0.5, rel_tol=1e-9)


def test_saturate_array_input_preserves_shape():
    arr = np.array([-10.0, 0.0, 10.0])
    out = saturate(arr, 0.1, method="tanh")
    assert isinstance(out, np.ndarray)
    assert out.shape == arr.shape
    assert out[1] == 0.0
    assert out[0] < 0.0 and out[2] > 0.0


def test_saturate_no_overflow_on_huge_input():
    out = float(saturate(1e6, 1e-6, method="tanh", slope=1.0))
    assert math.isfinite(out)
    assert 0.99 < out <= 1.0


def test_smooth_sign_matches_tanh_saturate():
    val = float(smooth_sign(0.2, epsilon=0.05))
    ref = float(saturate(0.2, 0.05, method="tanh"))
    assert math.isclose(val, ref, rel_tol=1e-12)
    assert float(smooth_sign(0.0)) == 0.0


def test_dead_zone_rejects_nonpositive_threshold():
    with pytest.raises(ValueError):
        dead_zone(1.0, 0.0)
    with pytest.raises(ValueError):
        dead_zone(1.0, -1.0)


def test_dead_zone_within_threshold_is_zero_scalar():
    out = dead_zone(0.3, 0.5)
    assert isinstance(out, float)
    assert out == 0.0


def test_dead_zone_outside_threshold_shifts_scalar():
    assert math.isclose(float(dead_zone(2.0, 0.5)), 1.5, rel_tol=1e-9)
    assert math.isclose(float(dead_zone(-2.0, 0.5)), -1.5, rel_tol=1e-9)


def test_dead_zone_array_input():
    arr = np.array([-2.0, 0.1, 2.0])
    out = dead_zone(arr, 0.5)
    assert isinstance(out, np.ndarray)
    assert out[1] == 0.0
    assert math.isclose(out[0], -1.5, rel_tol=1e-9)
    assert math.isclose(out[2], 1.5, rel_tol=1e-9)


def test_convenience_reexports_are_same_function():
    assert saturate_via_top is saturate
    assert saturate_via_pkg is saturate
