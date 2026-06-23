# simulation.orchestrators.batch

**Source:** `src\simulation\orchestrators\batch.py`

## Module Overview

Batch simulation orchestrator for vectorized execution.


## Mathematical Foundation

### Batch Simulation Orchestration

Efficient processing of multiple independent simulation runs.

### Batch Processing Model

**Vectorized execution:**
```{math}
\mathbf{X}_{k+1} = \mathbf{X}_k + \Delta t \cdot \mathbf{F}(\mathbf{X}_k, \mathbf{U}_k, t_k)
```

Where:
- $\mathbf{X}_k \in \mathbb{R}^{B \times n}$: Batch of $B$ state vectors
- $\mathbf{U}_k \in \mathbb{R}^{B \times m}$: Batch of control inputs
- $\mathbf{F}$: Vectorized dynamics function

### Vectorization Benefits

**SIMD (Single Instruction Multiple Data):**
- Modern CPUs process multiple data elements in one instruction
- Typical: 256-bit AVX2 (4 doubles), 512-bit AVX-512 (8 doubles)

**Cache efficiency:**
```{math}
\text{Cache hits} = \frac{\text{Sequential accesses}}{\text{Total accesses}} \times 100\%
```

Batch processing: 90-95% cache hit rate vs 60-70% for scattered access

### NumPy Vectorization

**Broadcasting rules:**
```python
# Batch state update (B × n)
x_new = x_batch + dt * f(x_batch, u_batch)  # Element-wise operations
```

**Performance gain:**
```{math}
\text{Speedup}_{\text{vectorized}} = 10-100\times \text{ vs naive Python loops}
```

## Numba JIT Compilation

**Just-In-Time compilation:**
- Compiles Python → LLVM → machine code
- Type specialization
- Loop optimization
- SIMD auto-vectorization

**@njit decorator:**
```python
@njit(parallel=True, fastmath=True)
def batch_simulate(x0_batch, u_batch, dt, steps):
    # Compiled to optimized machine code
```

### Parallel Batch Processing

**Two-level parallelism:**

1. **Batch-level:** Multiple batches processed in parallel
```{math}
\text{Batches} = \lceil \frac{M}{B} \rceil
```

2. **Within-batch:** SIMD vectorization

**Total parallelism:**
```{math}
\text{Parallelism} = N_{\text{cores}} \times \text{SIMD width}
```

### Memory Layout Optimization

**Array-of-Structures (AoS):**
```python
# example-metadata:
# runnable: false

states = [(x1, theta1, theta2, ...), ...]  # Poor cache locality
```

**Structure-of-Arrays (SoA):**
```python
# example-metadata:
# runnable: false

x = [x1, x2, ..., xB]           # Excellent cache locality
theta1 = [θ1_1, θ1_2, ..., θ1_B]  # Contiguous memory
```

**Cache line utilization:**
```{math}
\eta_{\text{cache}} = \frac{\text{Useful bytes loaded}}{64 \text{ bytes (cache line)}} \times 100\%
```

SoA: $\eta_{\text{cache}} \approx 100\%$ vs AoS: $\eta_{\text{cache}} \approx 16.7\%$ (for $n=6$ DIP)

## Load Balancing

**Dynamic batch sizing:**
```{math}
B_{\text{optimal}} = \arg\max_B \frac{\text{Throughput}(B)}{\text{Memory}(B)}
```

**Typical optimal batch size:** $B = 32-256$ for DIP system

### Performance Metrics

**Throughput:**
```{math}
\Theta = \frac{\text{Simulations completed}}{\text{Wall-clock time}} \quad [\text{sims/s}]
```

**Latency per simulation:**
```{math}
L = \frac{T_{\text{batch}}}{B}
```

**Efficiency:**
```{math}
E = \frac{\Theta_{\text{actual}}}{\Theta_{\text{theoretical}}}
```

### Use Cases

**Ideal for:**
- Monte Carlo analysis (thousands of runs)
- Parameter sweeps (grid search)
- Ensemble simulations (uncertainty quantification)
- PSO optimization (population evaluation)

**Performance example:**
- Sequential: 100 sims × 1.0 s = 100 s
- Parallel (8 cores): 100 sims ÷ 8 = 12.5 s (8× speedup)
- Batch (8 cores + vectorization): 100 sims = 2.5 s (40× speedup)

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
from src.simulation.orchestrators import OrchestratorsBatch

# Initialize
instance = OrchestratorsBatch()

# Execute
result = instance.process(data)
```

## Example 2: Advanced Configuration

```python
# Custom configuration
config = {'parameter': 'value'}
instance = OrchestratorsBatch(config)
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

```{literalinclude} ../../../src/simulation/orchestrators/batch.py
:language: python
:linenos:
```



## Classes

### `BatchOrchestrator`

**Inherits from:** `BaseOrchestrator`

Batch simulation orchestrator for vectorized execution.

This orchestrator can execute multiple simulations simultaneously
using vectorized operations, providing significant performance improvements
for Monte Carlo analysis and parameter sweeps.

#### Source Code

```{literalinclude} ../../../src/simulation/orchestrators/batch.py
:language: python
:pyobject: BatchOrchestrator
:linenos:
```

#### Methods (2)

##### `execute(self, initial_state, control_inputs, dt, horizon)`

Execute batch simulation.

[View full source →](#method-batchorchestrator-execute)

##### `_normalize_control_inputs(self, control_inputs, batch_size, horizon)`

Normalize control inputs to consistent batch format.

[View full source →](#method-batchorchestrator-_normalize_control_inputs)



## Functions

### `simulate_batch(initial_states, control_inputs, dt, horizon)`

Vectorized batch simulation function for backward compatibility.

This function provides a simplified interface similar to the original
vector_sim.simulate function.

Parameters
----------
initial_states : np.ndarray
    Initial states - shape (batch_size, state_dim)
control_inputs : np.ndarray
    Control inputs - shape (batch_size, horizon) or (batch_size, horizon, m)
dt : float
    Time step
horizon : int, optional
    Simulation horizon (inferred from control_inputs if None)
energy_limits : float, optional
    Energy limit for safety guards
state_bounds : tuple, optional
    State bounds for safety guards
stop_fn : callable, optional
    Early stopping function
t0 : float, optional
    Initial time
**kwargs
    Additional arguments

Returns
-------
np.ndarray
    Batch state trajectories - shape (batch_size, horizon+1, state_dim)

#### Source Code

```{literalinclude} ../../../src/simulation/orchestrators/batch.py
:language: python
:pyobject: simulate_batch
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import time`
- `from typing import Any, Callable, Optional`
- `import numpy as np`
- `from .base import BaseOrchestrator`
- `from ..core.interfaces import ResultContainer`
- `from ..results.containers import BatchResultContainer`
