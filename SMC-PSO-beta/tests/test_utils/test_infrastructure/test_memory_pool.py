"""Tests for src.utils.infrastructure.memory.memory_pool.MemoryPool.

Covers pre-allocation, allocation/exhaustion, return + validation, efficiency,
fragmentation metric, coalescing, and reset.
"""

import numpy as np
import pytest

from src.utils.infrastructure.memory import MemoryPool
from src.utils.infrastructure.memory.memory_pool import MemoryPool as MemoryPoolDirect


def test_init_preallocates_blocks():
    pool = MemoryPool(block_size=(100,), num_blocks=20)
    assert len(pool.blocks) == 20
    assert pool.num_blocks == 20
    assert pool.block_size == (100,)
    assert len(pool.available) == 20
    assert pool.allocated == []
    # All pre-allocated blocks are zeroed ndarrays of the requested shape.
    for block in pool.blocks:
        assert isinstance(block, np.ndarray)
        assert block.shape == (100,)
        assert np.all(block == 0.0)


def test_public_and_direct_import_are_same_class():
    assert MemoryPool is MemoryPoolDirect


def test_get_block_returns_array_and_tracks_state():
    pool = MemoryPool(block_size=(10,), num_blocks=5)
    block = pool.get_block()
    assert block is not None
    assert isinstance(block, np.ndarray)
    assert block.shape == (10,)
    assert len(pool.allocated) == 1
    assert len(pool.available) == 4


def test_get_block_exhaustion_returns_none():
    pool = MemoryPool(block_size=(4,), num_blocks=3)
    handed_out = [pool.get_block() for _ in range(3)]
    assert all(b is not None for b in handed_out)
    # Pool is now exhausted.
    assert pool.get_block() is None
    assert len(pool.allocated) == 3
    assert pool.available == []


def test_return_block_restores_availability():
    pool = MemoryPool(block_size=(10,), num_blocks=5)
    _ = pool.get_block()
    # Last allocated index is 4 (popped from the end of available).
    pool.return_block(4)
    assert 4 in pool.available
    assert 4 not in pool.allocated
    assert len(pool.available) == 5


def test_return_block_invalid_index_raises():
    pool = MemoryPool(block_size=(10,), num_blocks=5)
    with pytest.raises(ValueError):
        pool.return_block(99)
    with pytest.raises(ValueError):
        pool.return_block(-1)


def test_efficiency_reflects_allocation_ratio():
    pool = MemoryPool(block_size=(8,), num_blocks=20)
    assert pool.get_efficiency() == pytest.approx(0.0)
    for _ in range(18):
        _ = pool.get_block()
    assert pool.get_efficiency() == pytest.approx(90.0)


def test_fragmentation_zero_when_contiguous():
    pool = MemoryPool(block_size=(4,), num_blocks=10)
    pool.available = [0, 1, 2, 3]
    assert pool.get_fragmentation() == pytest.approx(0.0)


def test_fragmentation_positive_with_gaps_and_coalesce_sorts():
    pool = MemoryPool(block_size=(4,), num_blocks=10)
    # Two gaps among four available indices -> 2/3 * 100.
    pool.available = [0, 1, 5, 9]
    frag = pool.get_fragmentation()
    assert frag == pytest.approx((2 / 3) * 100.0)
    # Coalesce sorts the available indices in place (does not change membership).
    pool.available = [9, 2, 5, 1, 7]
    pool.coalesce()
    assert pool.available == [1, 2, 5, 7, 9]


def test_fragmentation_single_block_is_zero():
    pool = MemoryPool(block_size=(4,), num_blocks=10)
    pool.available = [3]
    assert pool.get_fragmentation() == pytest.approx(0.0)


def test_reset_restores_initial_state():
    pool = MemoryPool(block_size=(10,), num_blocks=5)
    _ = pool.get_block()
    _ = pool.get_block()
    pool.reset()
    assert pool.available == [0, 1, 2, 3, 4]
    assert pool.allocated == []
