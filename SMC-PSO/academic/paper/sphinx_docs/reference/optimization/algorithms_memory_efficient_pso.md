# optimization.algorithms.memory_efficient_pso

**Source:** `src\optimization\algorithms\memory_efficient_pso.py`

## Module Overview Memory-efficient

PSO optimizer with production-grade memory management

.

## Advanced Mathematical Theory

### Memory-Efficient PSO Design


M_{total} = M_{particles} + M_{history} + M_{best} = O(N \cdot d) + O(T \cdot N \cdot d) + O(d)
``` Where $N$ is population size, $d$ is dimensions, $T$ is iterations. **Problem:** Unbounded history growth $O(T \cdot N \cdot d)$ causes memory leaks. ### Bounded Collection Strategy **Circular buffer** for history with max size $H$: ```{math}
M_{history} = O(H \cdot N \cdot d), \quad H \ll T
``` **Maintains constant memory** regardless of iteration count. ### Adaptive Memory Cleanup **Cleanup trigger** based on memory usage: ```{math}

\text{Cleanup if } M_{current} > \alpha M_{max}
``` Where $\alpha \in (0.7, 0.9)$ is safety threshold. **Cleanup operations:**
1. Trim history to last $H$ iterations
2. Remove dominated approaches 3. Compress archive via clustering ### Memory Leak Prevention **Weak references** for large objects: ```{math}
\text{Store: } \{(i, \text{weakref}(obj_i)) : i \in \text{Archive}\}
``` Automatic garbage collection when reference count = 0. ### Production Memory Monitoring **Real-time tracking:** ```{math}

\begin{align}
M_{RSS}(t) &= \text{Resident Set Size at iteration } t \\
\Delta M &= M_{RSS}(t) - M_{RSS}(t-1) \\
\text{Alert if } \Delta M > \epsilon_{leak}
\end{align}
``` Detects memory leaks early. ## Architecture Diagram ```{mermaid}
graph TD A[PSO Iteration] --> B[Memory Check] B --> C{Memory Usage} C -->|< 70% Max| D[Continue Normal] C -->|70-90%| E[Trigger Cleanup] C -->|> 90%| F[Emergency Cleanup] E --> G[Trim History] F --> G G --> H[Remove Dominated] H --> I[Compress Archive] D --> J[Update Population] I --> J J --> K[Memory Tracking] K --> L{Leak Detected?} L -->|Yes| M[Alert & Cleanup] L -->|No| N[Continue] M --> N N --> A style C fill:#ff9 style G fill:#9cf style K fill:#f9c
``` ## Usage Examples ### Example 1: Basic Initialization ```python

from src.optimization.algorithms import * # Initialize with configuration
config = {'parameter': 'value'}
instance = Component(config)
``` ### Example 2: Performance Tuning ```python
# Adjust parameters for better performance
optimized_params = tune_parameters(instance, target_performance)
``` ### Example 3: Integration with Optimization ```python
# Use in complete optimization loop

optimizer = create_optimizer(opt_type, config)
result = optimize(optimizer, problem, max_iter=100)
``` ### Example 4: Edge Case Handling ```python
try: output = instance.compute(parameters)
except ValueError as e: handle_edge_case(e)
``` ### Example 5: Performance Analysis ```python
# Analyze metrics

metrics = compute_metrics(result)
print(f"Best fitness: {metrics.best_fitness:.3f}")
```
This module provides a memory-optimized version of the PSO optimizer specifically
designed to handle large-scale optimization runs without memory leaks or excessive
memory consumption. Implements bounded collections, automatic cleanup, and
real-time memory monitoring for production deployment. Key Features:
- Bounded history collections prevent unbounded memory growth
- Automatic memory cleanup every N iterations
- Real-time memory usage monitoring and alerting
- Graceful degradation under memory pressure
- memory usage statistics ## Complete Source Code ```{literalinclude} ../../../src/optimization/algorithms/memory_efficient_pso.py
:language: python
:linenos:
```

---

## Classes

### `MemoryConfig`

Memory management configuration for PSO optimization.

#### Source Code ```

{literalinclude} ../../../src/optimization/algorithms/memory_efficient_pso.py

:language: python
:pyobject: MemoryConfig
:linenos:
```

### `MemoryTracker`

Real-time memory usage tracker for PSO optimization.

#### Source Code ```

{literalinclude} ../../../src/optimization/algorithms/memory_efficient_pso.py
:language: python
:pyobject: MemoryTracker
:linenos:
``` #### Methods (7) ##### `__init__(self, pid)` [View full source →](#method-memorytracker-__init__) ##### `get_current_memory_mb(self)` Get current memory usage in MB. [View full source →](#method-memorytracker-get_current_memory_mb) ##### `get_memory_growth_mb(self)` Get memory growth since initialization. [View full source →](#method-memorytracker-get_memory_growth_mb) ##### `get_memory_growth_since_gc_mb(self)` Get memory growth since last garbage collection. [View full source →](#method-memorytracker-get_memory_growth_since_gc_mb) ##### `record_gc_event(self)` Record garbage collection event. [View full source →](#method-memorytracker-record_gc_event) ##### `get_memory_trend(self, window_seconds)` Analyze memory usage trend over time window. [View full source →](#method-memorytracker-get_memory_trend) ##### `get_summary(self)` Get memory usage summary. [View full source →](#method-memorytracker-get_summary)

### `BoundedHistory`

Bounded history collection with automatic size management.

#### Source Code ```

{literalinclude} ../../../src/optimization/algorithms/memory_efficient_pso.py

:language: python
:pyobject: BoundedHistory
:linenos:
``` #### Methods (8) ##### `__init__(self, maxlen, compression_enabled)` [View full source →](#method-boundedhistory-__init__) ##### `append(self, item)` Add item to history with automatic compression. [View full source →](#method-boundedhistory-append) ##### `_compress_oldest(self)` Compress oldest data to free up space. [View full source →](#method-boundedhistory-_compress_oldest) ##### `get_recent(self, n)` Get recent items from history. [View full source →](#method-boundedhistory-get_recent) ##### `get_all(self)` Get all items including compressed data. [View full source →](#method-boundedhistory-get_all) ##### `clear(self)` Clear all history data. [View full source →](#method-boundedhistory-clear) ##### `__len__(self)` [View full source →](#method-boundedhistory-__len__) ##### `get_memory_estimate_mb(self)` Estimate memory usage of stored data. [View full source →](#method-boundedhistory-get_memory_estimate_mb)

### `MemoryEfficientPSOTuner`

**Inherits from:** `PSOTuner` Memory-optimized PSO tuner for production use. This class extends the base PSOTuner with memory management
features to prevent memory leaks and handle large-scale optimization
runs efficiently. Features:
- Bounded history collections
- Automatic memory cleanup
- Real-time memory monitoring
- Emergency recovery mechanisms
- Memory pressure adaptation #### Source Code ```{literalinclude} ../../../src/optimization/algorithms/memory_efficient_pso.py
:language: python
:pyobject: MemoryEfficientPSOTuner
:linenos:
``` #### Methods (12) ##### `__init__(self, controller_factory, config, memory_config)` Initialize memory-efficient PSO tuner. [View full source →](#method-memoryefficientpsotuner-__init__) ##### `optimise(self)` Run PSO optimization with memory management. [View full source →](#method-memoryefficientpsotuner-optimise) ##### `_fitness(self, particles)` Memory-aware fitness evaluation with monitoring and cleanup. [View full source →](#method-memoryefficientpsotuner-_fitness) ##### `_periodic_memory_management(self)` Perform periodic memory management tasks. [View full source →](#method-memoryefficientpsotuner-_periodic_memory_management) ##### `_perform_memory_cleanup(self, force)` Perform memory cleanup. [View full source →](#method-memoryefficientpsotuner-_perform_memory_cleanup) ##### `_force_garbage_collection(self)` Force garbage collection and update tracking. [View full source →](#method-memoryefficientpsotuner-_force_garbage_collection) ##### `_check_memory_pressure(self)` Check for memory pressure and take appropriate action. [View full source →](#method-memoryefficientpsotuner-_check_memory_pressure) ##### `_emergency_memory_cleanup(self)` Emergency memory cleanup for critical situations. [View full source →](#method-memoryefficientpsotuner-_emergency_memory_cleanup) ##### `get_memory_statistics(self)` Get memory usage statistics. [View full source →](#method-memoryefficientpsotuner-get_memory_statistics) ##### `get_memory_alerts(self, alert_type)` Get memory alerts, optionally filtered by type. [View full source →](#method-memoryefficientpsotuner-get_memory_alerts) ##### `reset_memory_tracking(self)` Reset memory tracking statistics. [View full source →](#method-memoryefficientpsotuner-reset_memory_tracking) ##### `__del__(self)` Cleanup on deletion. [View full source →](#method-memoryefficientpsotuner-__del__)

---

## Dependencies This module imports: - `import gc`

- `import logging`
- `import psutil`
- `import threading`
- `import time`
- `import weakref`
- `from dataclasses import dataclass, field`
- `from typing import Any, Callable, Dict, List, Optional, Tuple, Union`
- `from collections import deque`
- `import numpy as np` *... and 1 more*
