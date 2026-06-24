#======================================================================================
#==================== tests/test_utils/test_numerical_stability.py ====================
#======================================================================================

"""Tests for utils.numerical_stability.safe_operations (M3 slice 4)."""
from __future__ import annotations

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils.numerical_stability import (
    safe_divide,
    safe_reciprocal,
    safe_sqrt,
    safe_log,
    safe_exp,
    safe_power,
    safe_norm,
    safe_normalize,
    is_safe_denominator,
    clip_to_safe_range,
    EPSILON_DIV,
    EPSILON_SQRT,
    EPSILON_LOG,
    EPSILON_EXP,
)
from utils.numerical_stability.safe_operations import safe_divide as sd_mod
import utils.numerical_stability as nstab


def test_constants_values():
    assert EPSILON_DIV == 1e-12
    assert EPSILON_SQRT == 1e-15
    assert EPSILON_LOG == 1e-15
    assert EPSILON_EXP == 700.0


def test_safe_divide_normal_scalar():
    assert safe_divide(1.0, 2.0) == 0.5
    assert isinstance(safe_divide(1.0, 2.0), float)


def test_safe_divide_near_zero_protected():
    assert np.isclose(safe_divide(1.0, 1e-15), 1e12)


def test_safe_divide_sign_preserved_near_zero():
    assert np.isclose(safe_divide(1.0, -1e-15), -1e12)


def test_safe_divide_exact_zero_uses_fallback():
    assert safe_divide(1.0, 0.0) == 0.0
    assert safe_divide(1.0, 0.0, fallback=np.inf) == np.inf


def test_safe_divide_array_broadcast():
    out = safe_divide(np.array([1.0, 2.0, 3.0]), np.array([2.0, 1e-15, 4.0]))
    assert np.allclose(out, [0.5, 2e12, 0.75])


def test_safe_divide_rejects_nonpositive_epsilon():
    with pytest.raises(ValueError):
        safe_divide(1.0, 1.0, epsilon=0.0)
    with pytest.raises(ValueError):
        safe_divide(1.0, 1.0, epsilon=-1e-9)


def test_safe_reciprocal():
    assert safe_reciprocal(2.0) == 0.5
    assert np.isclose(safe_reciprocal(1e-15), 1e12)


def test_safe_sqrt_normal():
    assert safe_sqrt(4.0) == 2.0


def test_safe_sqrt_negative_clipped_to_sqrt_minvalue():
    # Clipped to min_value=EPSILON_SQRT=1e-15, so result is sqrt(1e-15),
    # NOT 1e-7 as the source docstring example wrongly claims (S4-A2).
    assert np.isclose(safe_sqrt(-0.001), np.sqrt(1e-15))
    assert not np.isclose(safe_sqrt(-0.001), 1e-7)


def test_safe_sqrt_rejects_negative_minvalue():
    with pytest.raises(ValueError):
        safe_sqrt(1.0, min_value=-1.0)


def test_safe_log_normal():
    assert np.isclose(safe_log(np.e), 1.0)


def test_safe_log_zero_clipped():
    assert np.isclose(safe_log(0.0), np.log(1e-15))


def test_safe_log_rejects_nonpositive_minvalue():
    with pytest.raises(ValueError):
        safe_log(1.0, min_value=0.0)


def test_safe_exp_normal():
    assert np.isclose(safe_exp(0.0), 1.0)


def test_safe_exp_overflow_clipped():
    assert np.isclose(safe_exp(1000.0), np.exp(700.0))


def test_safe_power_normal():
    assert safe_power(2.0, 3.0) == 8.0


def test_safe_power_negative_odd_exponent():
    assert safe_power(-2.0, 3.0) == -8.0


def test_safe_power_negative_even_exponent():
    assert safe_power(-2.0, 2.0) == 4.0


def test_safe_power_small_base_protected():
    assert np.isclose(safe_power(1e-20, 2.0), 1e-30)


def test_safe_norm_euclidean():
    assert safe_norm(np.array([3.0, 4.0])) == 5.0


def test_safe_norm_floor():
    assert np.isclose(safe_norm(np.array([1e-20, 1e-20])), 1e-15)


def test_safe_norm_axis():
    out = safe_norm(np.array([[1.0, 0.0], [0.0, 1.0]]), axis=1)
    assert np.allclose(out, [1.0, 1.0])


def test_safe_normalize_unit():
    assert np.allclose(safe_normalize(np.array([3.0, 4.0])), [0.6, 0.8])


def test_safe_normalize_zero_vector():
    assert np.allclose(safe_normalize(np.array([0.0, 0.0])), [0.0, 0.0])


def test_safe_normalize_axis():
    out = safe_normalize(np.array([[1.0, 0.0], [0.0, 2.0]]), axis=1)
    assert np.allclose(out, [[1.0, 0.0], [0.0, 1.0]])


def test_is_safe_denominator_scalar():
    assert is_safe_denominator(1.0) is True
    assert is_safe_denominator(1e-15) is False


def test_is_safe_denominator_array():
    out = is_safe_denominator(np.array([1.0, 1e-15, -2.0]))
    assert list(out) == [True, False, True]


def test_clip_to_safe_range_scalar():
    assert clip_to_safe_range(1e15) == 1e10
    assert clip_to_safe_range(-1e15) == -1e10


def test_clip_to_safe_range_array():
    out = clip_to_safe_range(np.array([-1e12, 0.0, 1e12]))
    assert np.allclose(out, [-1e10, 0.0, 1e10])


def test_package_namespace_exposes_ops():
    assert nstab.safe_divide is safe_divide
    assert sd_mod is safe_divide
