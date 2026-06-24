#======================================================================================
#==================== tests/test_utils/test_reproducibility.py ========================
#======================================================================================

"""Tests for utils.testing.reproducibility (M3 slice 3)."""
from __future__ import annotations

import os
import sys
import random as _random

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils.testing.reproducibility.seed import set_global_seed, SeedManager, create_rng
from utils.testing.reproducibility import (
    set_global_seed as sg_pkg,
    set_seed,
    SeedManager as SM_pkg,
    create_rng as cr_pkg,
    with_seed,
    random_seed_context,
)
from utils import set_global_seed as sg_top


def test_set_global_seed_is_reproducible():
    set_global_seed(123)
    a = (_random.random(), float(np.random.rand()))
    set_global_seed(123)
    b = (_random.random(), float(np.random.rand()))
    assert a == b


def test_set_global_seed_none_is_noop():
    set_global_seed(7)
    first = _random.random()
    set_global_seed(None)
    second = _random.random()
    set_global_seed(7)
    reset_first = _random.random()
    # None is a no-op: the stream advances rather than resetting
    assert reset_first == first
    assert second != first


def test_seed_manager_deterministic_sequence():
    m1 = SeedManager(42)
    m2 = SeedManager(42)
    s1 = [m1.spawn() for _ in range(5)]
    s2 = [m2.spawn() for _ in range(5)]
    assert s1 == s2
    assert m1.history == s1


def test_seed_manager_seed_range_and_history():
    mgr = SeedManager(1)
    seeds = [mgr.spawn() for _ in range(10)]
    assert all(isinstance(s, int) for s in seeds)
    assert all(0 <= s < 2**32 - 1 for s in seeds)
    assert mgr.history == seeds


def test_seed_manager_none_is_valid_int():
    mgr = SeedManager(None)
    s = mgr.spawn()
    assert isinstance(s, int)


def test_create_rng_deterministic():
    r1 = create_rng(99)
    r2 = create_rng(99)
    assert np.array_equal(r1.random(5), r2.random(5))


def test_create_rng_none_returns_generator():
    rng = create_rng(None)
    assert isinstance(rng, np.random.Generator)


def test_create_rng_invalid_seed_falls_back():
    rng = create_rng("not-an-int")
    assert isinstance(rng, np.random.Generator)


def test_set_seed_alias_is_same_function():
    assert set_seed is set_global_seed


def test_with_seed_returns_identity_decorator():
    @with_seed(5)
    def f(x):
        return x + 1
    assert f(1) == 2


def test_random_seed_context_seeds_within_block():
    with random_seed_context(321):
        v = _random.random()
    set_global_seed(321)
    assert _random.random() == v


def test_package_and_top_level_exports_align():
    assert sg_pkg is set_global_seed
    assert SM_pkg is SeedManager
    assert cr_pkg is create_rng
    assert sg_top is set_global_seed
