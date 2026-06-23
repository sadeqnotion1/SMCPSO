# simulation.orchestrators.sequential

**Source:** `src\simulation\orchestrators\sequential.py`

## Module Overview

Sequential simulation orchestrator for single-threaded execution.


## Mathematical Foundation

### Sequential Simulation Orchestration

Single-threaded execution of simulation workflows.

### Sequential Execution Model

**Deterministic linear execution:**
```{math}
\text{Result} = \bigcup_{i=1}^{N} \text{Step}_i(x_i, u_i, t_i)
```

**Time complexity:**
```{math}
T_{\text{total}} = \sum_{i=1}^{N} T_{\text{step}}(i)
```

### Simulation Loop

**Standard simulation algorithm:**

1. **Initialize:** $x_0$, $t_0$, controller state
2. **Loop** for $k = 0, 1, 2, \ldots, N-1$:
   - Compute control: $u_k = \pi(x_k, t_k)$
   - Integrate dynamics: $x_{k+1} = x_k + \int_{t_k}^{t_{k+1}} f(x, u_k, t) dt$
   - Update time: $t_{k+1} = t_k + \Delta t$
   - Log data
   - Check termination
3. **Return** trajectory $\{(t_k, x_k, u_k)\}_{k=0}^{N}$

### Determinism

**Reproducibility guarantee:**
```{math}
\text{Seed}(s) \Rightarrow \text{Result}(s, x_0, \text{config}) \text{ is deterministic}
```

Essential for:
- Scientific reproducibility
- Debugging
- Regression testing
- Continuous integration

### Memory Access Pattern

**Temporal locality:**
- Sequential access to state history
- Cache-friendly
- Predictable memory usage

**Memory complexity:**
```{math}
M = O(N \cdot n) \quad \text{where } n = \text{state dimension}
```

### Control Flow

**Linear dependency chain:**
```{math}
x_{k+1} = \Phi(x_k, u_k, \Delta t) \quad \Rightarrow \quad x_{k+1} \text{ depends on } x_k
```

**No parallelization opportunity** within single simulation

### Performance Characteristics

**Advantages:**
- ✅ Deterministic execution
- ✅ Simple debugging
- ✅ Low memory overhead
- ✅ No thread synchronization overhead
- ✅ Cache-friendly access patterns

**Limitations:**
- ❌ Single-core utilization
- ❌ No speedup for batch operations
- ❌ Underutilizes modern multi-core CPUs

### Computational Efficiency

**CPU utilization:**
```{math}
\eta_{\text{CPU}} = \frac{1}{N_{\text{cores}}} \times 100\%
```

For 8-core system: $\eta_{\text{CPU}} = 12.5\%$

### Use Cases

**Ideal for:**
- Single simulation runs
- Debugging and validation
- Real-time applications (deterministic timing)
- Embedded systems (resource constraints)

**Not ideal for:**
- Monte Carlo analysis (many independent runs)
- Parameter sweeps (embarrassingly parallel)
- Multi-objective optimization (parallel evaluations)

## Architecture Diagram

```{mermaid}
graph LR
    A[Input] --> B[Orchestrators Processing]
    B --> C[Output]

    style B fill:#9cf
    style C fill:#9f9
```

## Usage Examples

### Example 1: Basic Usage

```python
from src.simulation.orchestrators import OrchestratorsSequential

# Initialize
instance = OrchestratorsSequential()

# Execute
result = instance.process(data)
```

## Example 2: Advanced Configuration

```python
# Custom configuration
config = {'parameter': 'value'}
instance = OrchestratorsSequential(config)
result = instance.process(data)
```

## Example 3: Error Handling

```python
try:
    result = instance.process(data)
except Exception as e:
    print(f"Error: {e}")
```

### Example 4: Performance Profiling

```python
import time
start = time.time()
result = instance.process(data)
elapsed = time.time() - start
print(f"Execution time: {elapsed:.4f} s")
```

### Example 5: Integration with Other Components

```python
# Combine with other simulation components
result = orchestrator.execute(instance.process(data))
```

## Complete Source Code

```{literalinclude} ../../../src/simulation/orchestrators/sequential.py
:language: python
:linenos:
```



## Classes

### `SequentialOrchestrator`

**Inherits from:** `BaseOrchestrator`

Sequential simulation orchestrator for single-threaded execution.

This orchestrator executes simulations step-by-step in a single thread,
providing compatibility with the original simulation_runner functionality.

#### Source Code

```{literalinclude} ../../../src/simulation/orchestrators/sequential.py
:language: python
:pyobject: SequentialOrchestrator
:linenos:
```

#### Methods (1)

##### `execute(self, initial_state, control_inputs, dt, horizon)`

Execute sequential simulation.

[View full source →](#method-sequentialorchestrator-execute)



## Functions

### `get_step_fn()`

Legacy function for backward compatibility.

Returns
callable
    Step function that dispatches to appropriate dynamics model

#### Source Code

```{literalinclude} ../../../src/simulation/orchestrators/sequential.py
:language: python
:pyobject: get_step_fn
:linenos:
```



### `_load_full_step()`

Load full dynamics step function.

#### Source Code

```{literalinclude} ../../../src/simulation/orchestrators/sequential.py
:language: python
:pyobject: _load_full_step
:linenos:
```



### `_load_lowrank_step()`

Load low-rank dynamics step function.

#### Source Code

```{literalinclude} ../../../src/simulation/orchestrators/sequential.py
:language: python
:pyobject: _load_lowrank_step
:linenos:
```



### `step(x, u, dt)`

Legacy step function for backward compatibility.

Parameters
----------
x : array-like
    Current state
u : array-like
    Control input
dt : float
    Time step

Returns
-------
array-like
    Next state

#### Source Code

```{literalinclude} ../../../src/simulation/orchestrators/sequential.py
:language: python
:pyobject: step
:linenos:
```



### `run_simulation()`

Legacy simulation runner for backward compatibility.

This function maintains the exact interface and behavior of the original
run_simulation function from simulation_runner.py.

Parameters
----------
controller : Any
    Controller object with __call__ or compute_control method
dynamics_model : Any
    Dynamics model with step method
sim_time : float
    Total simulation time
dt : float
    Time step
initial_state : array-like
    Initial state vector
u_max : float, optional
    Control saturation limit
seed : int, optional
    Random seed (deprecated, use rng)
rng : np.random.Generator, optional
    Random number generator
latency_margin : float, optional
    Unused (for future latency control)
fallback_controller : callable, optional
    Fallback controller for deadline misses
**_kwargs
    Additional arguments (ignored)

Returns
-------
tuple
    (times, states, controls) arrays

#### Source Code

```{literalinclude} ../../../src/simulation/orchestrators/sequential.py
:language: python
:pyobject: run_simulation
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import time`
- `from typing import Any, Callable, Optional, Tuple`
- `import numpy as np`
- `from .base import BaseOrchestrator`
- `from ..core.interfaces import ResultContainer`
- `from ..results.containers import StandardResultContainer`
- `from ..safety.guards import apply_safety_guards`
