# utils.memory.memory_pool

**Source:** `src\utils\memory\memory_pool.py`

## Module Overview

Production-grade memory pool for efficient memory management.

This module provides a memory pool implementation with automatic coalescing,
fragmentation monitoring, and efficiency tracking. Designed for long-running
simulations and batch operations to minimize memory allocation overhead.

Example:
    >>> import numpy as np
    >>> from src.utils.memory.memory_pool import MemoryPool
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

## Complete Source Code

```{literalinclude} ../../../src/utils/memory/memory_pool.py
:language: python
:linenos:
```



## Classes

### `MemoryPool`

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

#### Source Code

```{literalinclude} ../../../src/utils/memory/memory_pool.py
:language: python
:pyobject: MemoryPool
:linenos:
```

#### Methods (8)

##### `__init__(self, block_size, num_blocks)`

Initialize memory pool with fixed-size blocks.

[View full source →](#method-memorypool-__init__)

##### `get_block(self)`

Allocate a block from the pool.

[View full source →](#method-memorypool-get_block)

##### `return_block(self, block_idx)`

Return a block to the pool with automatic coalescing.

[View full source →](#method-memorypool-return_block)

##### `coalesce(self)`

Defragment the memory pool by sorting available blocks.

[View full source →](#method-memorypool-coalesce)

##### `get_fragmentation(self)`

Calculate internal fragmentation percentage.

[View full source →](#method-memorypool-get_fragmentation)

##### `get_efficiency(self)`

Calculate pool efficiency as percentage of blocks in use.

[View full source →](#method-memorypool-get_efficiency)

##### `reset(self)`

Reset pool to initial state with all blocks available.

[View full source →](#method-memorypool-reset)

##### `__repr__(self)`

String representation of pool state.

[View full source →](#method-memorypool-__repr__)



## Dependencies

This module imports:

- `from typing import Optional, Tuple, List`
- `import numpy as np`
