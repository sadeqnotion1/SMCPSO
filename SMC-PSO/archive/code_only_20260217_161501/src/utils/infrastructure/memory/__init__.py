#==========================================================================================\\\
#=========================== src/utils/memory/__init__.py =========================\\\
#==========================================================================================\\\

"""Memory management utilities for efficient simulation execution.

This module provides production-grade memory pooling with automatic coalescing
and fragmentation monitoring to optimize memory usage in long-running simulations.

Addresses Issue #17 (CRIT-008): Memory Pool Allocation Issues.

Key Features
------------
- Pre-allocated memory blocks to reduce allocation overhead
- Automatic defragmentation when fragmentation exceeds 20%
- Efficiency and fragmentation monitoring
- Zero-copy block reuse for optimal performance

Example
-------
>>> from src.utils.infrastructure.memory import MemoryPool
>>> import numpy as np
>>>
>>> # Create pool with 20 blocks of shape (100,)
>>> pool = MemoryPool(block_size=(100,), num_blocks=20)
>>>
>>> # Allocate and use blocks
>>> block = pool.get_block()
>>> if block is not None:
...     np.random.randn(*block.shape, out=block)
...     pool.return_block(0)  # Auto-coalesces if needed
>>>
>>> # Monitor pool health
>>> print(f"Efficiency: {pool.get_efficiency():.1f}%")
>>> print(f"Fragmentation: {pool.get_fragmentation():.1f}%")
"""

from .memory_pool import MemoryPool

__all__ = ['MemoryPool']
