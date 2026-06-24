#======================================================================================
#===================== tests/test_utils/test_control_validation.py ====================
#======================================================================================

"""Unit + property tests for utils.control.validation primitives (M3 slice 1)."""

from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest

from utils.control.validation.parameter_validators import (
    require_positive,
    require_finite,
)
from utils.control.validation.range_validators import (
    require_in_range,
    require_probability,
)


# ----- require_positive -----

def test_require_positive_accepts_positive():
    assert require_positive(3, "gain") == 3.0
    assert isinstance(require_positive(3, "gain"), float)


def test_require_positive_rejects_zero_by_default():
    with pytest.raises(ValueError):
        require_positive(0, "gain")


def test_require_positive_allows_zero_when_flagged():
    assert require_positive(0, "gain", allow_zero=True) == 0.0


def test_require_positive_rejects_negative():
    with pytest.raises(ValueError):
        require_positive(-1e-9, "gain")
    with pytest.raises(ValueError):
        require_positive(-5, "gain", allow_zero=True)


def test_require_positive_rejects_none_and_nonfinite():
    for bad in (None, float("nan"), float("inf"), float("-inf"), "1.0"):
        with pytest.raises(ValueError):
            require_positive(bad, "gain")


def test_require_positive_property_returns_same_value():
    for v in (1e-9, 0.5, 1, 2.5, 1e6, 12345.678):
        assert require_positive(v, "g") == float(v)


# ----- require_finite -----

def test_require_finite_accepts_finite():
    assert require_finite(-2.5, "x") == -2.5
    assert require_finite(0, "x") == 0.0


def test_require_finite_rejects_nonfinite():
    for bad in (None, float("nan"), float("inf"), float("-inf"), "0"):
        with pytest.raises(ValueError):
            require_finite(bad, "x")


# ----- require_in_range -----

def test_require_in_range_inclusive_boundaries():
    assert require_in_range(0.0, "p", minimum=0.0, maximum=1.0) == 0.0
    assert require_in_range(1.0, "p", minimum=0.0, maximum=1.0) == 1.0
    assert require_in_range(0.5, "p", minimum=0.0, maximum=1.0) == 0.5


def test_require_in_range_exclusive_rejects_boundaries():
    with pytest.raises(ValueError):
        require_in_range(0.0, "p", minimum=0.0, maximum=1.0, allow_equal=False)
    with pytest.raises(ValueError):
        require_in_range(1.0, "p", minimum=0.0, maximum=1.0, allow_equal=False)
    assert require_in_range(0.5, "p", minimum=0.0, maximum=1.0, allow_equal=False) == 0.5


def test_require_in_range_rejects_out_of_range():
    with pytest.raises(ValueError):
        require_in_range(-0.01, "p", minimum=0.0, maximum=1.0)
    with pytest.raises(ValueError):
        require_in_range(1.01, "p", minimum=0.0, maximum=1.0)


def test_require_in_range_rejects_none_and_nonfinite():
    for bad in (None, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            require_in_range(bad, "p", minimum=0.0, maximum=1.0)


# ----- require_probability -----

def test_require_probability_accepts_unit_interval():
    for v in (0.0, 0.25, 0.5, 1.0):
        assert require_probability(v, "prob") == float(v)


def test_require_probability_rejects_outside_unit_interval():
    for bad in (-1e-6, 1.0000001, 2, -3):
        with pytest.raises(ValueError):
            require_probability(bad, "prob")
