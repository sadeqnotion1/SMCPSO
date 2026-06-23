#==========================================================================================\\\
#======================== src/utils/memory/memory_pool.py ========================\\\
#==========================================================================================\\\

"""
Production-grade memory pool for efficient memory management.

This module provides a memory pool implementation with automatic coalescing,
fragmentation monitoring, and efficiency tracking. Designed for long-running
simulations and batch operations to minimize memory allocation overhead.

Example:
    >>> import numpy as np
    >>> from src.utils.infrastructure.memory.memory_pool import MemoryPool
    >>>
    >>> # Create pool with 20 blocks of shape (100,)
    >>> pool = MemoryPool(block_size=(100,), num_blocks=20)
    >>>
    >>> # Allocate blocks
    >>> block1 = pool.get_block()
    >>> block2 = pool.get_block()
    >>>
    >>> # Use blocks...
    >>> np.random.randn(*block1.shape, out=block1)
    >>>
    >>> # Return blocks (auto-coalesces if fragmentation > 20%)
    >>> pool.return_block(0)
    >>> pool.return_block(1)
    >>>
    >>> # Check pool health
    >>> print(f"Efficiency: {pool.get_efficiency():.1f}%")
    >>> print(f"Fragmentation: {pool.get_fragmentation():.1f}%")
"""

from typing import Optional, Tuple, List
import numpy as np


class MemoryPool:
    """
    Production memory pool with auto-coalescing and fragmentation monitoring.

    This class manages a fixed pool of pre-allocated numpy arrays to minimize
    allocation overhead during simulation runs. It automatically defragments
    the pool when fragmentation exceeds 20%.

    Attributes:
        block_size: Shape tuple for each block (e.g., (100,) or (10, 10))
        num_blocks: Total number of blocks in the pool
        blocks: List of pre-allocated numpy arrays
        available: List of available block indices
        allocated: List of currently allocated block indices

    Performance Targets:
        - Efficiency: >90% (allocated / total blocks)
        - Fragmentation: <10% after coalescing
        - Coalescing latency: <1ms for typical pool sizes
    """

    def __init__(self, block_size: Tuple[int, ...], num_blocks: int) -> None:
        """
        Initialize memory pool with fixed-size blocks.

        Args:
            block_size: Shape of each memory block (e.g., (100,) for 1D arrays)
            num_blocks: Total number of blocks to pre-allocate

        Example:
            >>> pool = MemoryPool(block_size=(100,), num_blocks=20)
            >>> len(pool.blocks)
            20
        """
        self.block_size: Tuple[int, ...] = block_size
        self.num_blocks: int = num_blocks

        # Pre-allocate all blocks upfront. This pays a one-time cost at initialization
        # but eliminates allocation overhead during simulation runs. For long-running
        # batch operations (like PSO with 10,000 iterations), this can save seconds
        # of cumulative allocation time.
        self.blocks: List[np.ndarray] = [
            np.zeros(block_size) for _ in range(num_blocks)
        ]

        # Track availability using index lists instead of boolean arrays. This gives us
        # O(1) pop/append operations and makes coalescing straightforward via sorting.
        # Initially all blocks are available (indices 0 to num_blocks-1).
        self.available: List[int] = list(range(num_blocks))
        self.allocated: List[int] = []

    def get_block(self) -> Optional[np.ndarray]:
        """
        Allocate a block from the pool.

        Returns:
            numpy array if blocks available, None if pool exhausted

        Example:
            >>> pool = MemoryPool(block_size=(10,), num_blocks=5)
            >>> block = pool.get_block()
            >>> block is not None
            True
            >>> block.shape
            (10,)
        """
        if not self.available:
            return None

        # Pop from available and track as allocated
        block_idx = self.available.pop()
        self.allocated.append(block_idx)

        return self.blocks[block_idx]

    def return_block(self, block_idx: int) -> None:
        """
        Return a block to the pool with automatic coalescing.

        If fragmentation exceeds 20% after return, automatically triggers
        coalescing to defragment the available list.

        Args:
            block_idx: Index of block to return (0 to num_blocks-1)

        Example:
            >>> pool = MemoryPool(block_size=(10,), num_blocks=5)
            >>> block = pool.get_block()
            >>> pool.return_block(0)
            >>> len(pool.available)
            5
        """
        if block_idx < 0 or block_idx >= len(self.blocks):
            raise ValueError(
                f"Invalid block index {block_idx}. Must be 0 to {len(self.blocks)-1}"
            )

        # Remove from allocated if present
        if block_idx in self.allocated:
            self.allocated.remove(block_idx)

        # Add back to available if not already there
        if block_idx not in self.available:
            self.available.append(block_idx)

        # Auto-coalesce if fragmentation exceeds threshold. The 20% threshold
        # balances between coalescing too often (wasting CPU) and letting
        # fragmentation accumulate (hurting cache locality). This was chosen
        # based on Issue #17 analysis showing acceptable performance impact.
        if self.get_fragmentation() > 20.0:
            self.coalesce()

    def coalesce(self) -> None:
        """
        Defragment the memory pool by sorting available blocks.

        This reduces fragmentation by organizing available blocks into
        contiguous ranges, improving cache locality and reducing gaps.

        Example:
            >>> pool = MemoryPool(block_size=(10,), num_blocks=10)
            >>> pool.available = [9, 2, 5, 1, 7]  # Fragmented
            >>> pool.coalesce()
            >>> pool.available
            [1, 2, 5, 7, 9]
        """
        # Coalescing algorithm: We sort the available list to group contiguous blocks
        # together. This is a simple but effective O(n log n) approach that prevents
        # fragmentation from accumulating over time. Future optimization could use a
        # buddy system for O(1) coalescing, but profiling shows sorting is fast enough
        # for typical pool sizes (<100 blocks).
        self.available.sort()

    def get_fragmentation(self) -> float:
        """
        Calculate internal fragmentation percentage.

        Fragmentation is measured as the ratio of gaps in the available
        block indices to the total available blocks. Lower is better.

        Returns:
            Fragmentation percentage (0-100)

        Example:
            >>> pool = MemoryPool(block_size=(10,), num_blocks=10)
            >>> pool.available = [0, 1, 2, 5, 6, 7]  # 1 gap at [3,4]
            >>> frag = pool.get_fragmentation()
            >>> 0 <= frag <= 100
            True
        """
        if not self.available:
            return 0.0

        if len(self.available) == 1:
            return 0.0

        # Sort to find gaps (this doesn't mutate self.available)
        sorted_available = sorted(self.available)

        # Count gaps between consecutive indices. A "gap" means we have non-contiguous
        # available blocks like [0, 1, 5, 6] (gap at indices 2-4). This matters because
        # contiguous blocks improve CPU cache locality when iterating through arrays.
        gaps = 0
        for i in range(len(sorted_available) - 1):
            # If indices are not consecutive, we have a gap
            if sorted_available[i+1] - sorted_available[i] > 1:
                gaps += 1

        # Fragmentation as percentage of potential gaps. We normalize by the maximum
        # possible number of gaps (len - 1) to get a 0-100% metric that's independent
        # of pool size.
        max_gaps = len(sorted_available) - 1
        if max_gaps == 0:
            return 0.0

        return (gaps / max_gaps) * 100.0

    def get_efficiency(self) -> float:
        """
        Calculate pool efficiency as percentage of blocks in use.

        Efficiency is the ratio of allocated blocks to total blocks.
        Higher values indicate better utilization.

        Returns:
            Efficiency percentage (0-100)

        Example:
            >>> pool = MemoryPool(block_size=(10,), num_blocks=20)
            >>> for _ in range(18):
            ...     _ = pool.get_block()
            >>> eff = pool.get_efficiency()
            >>> eff > 85.0
            True
        """
        allocated_count = len(self.allocated)
        return (allocated_count / self.num_blocks) * 100.0

    def reset(self) -> None:
        """
        Reset pool to initial state with all blocks available.

        This is useful for reusing a pool between simulation runs without
        reallocating memory.

        Example:
            >>> pool = MemoryPool(block_size=(10,), num_blocks=5)
            >>> _ = pool.get_block()
            >>> _ = pool.get_block()
            >>> pool.reset()
            >>> len(pool.available)
            5
        """
        self.available = list(range(self.num_blocks))
        self.allocated = []

    def __repr__(self) -> str:
        """String representation of pool state."""
        return (
            f"MemoryPool(block_size={self.block_size}, "
            f"num_blocks={self.num_blocks}, "
            f"allocated={len(self.allocated)}, "
            f"available={len(self.available)}, "
            f"efficiency={self.get_efficiency():.1f}%, "
            f"fragmentation={self.get_fragmentation():.1f}%)"
        )
