# simulation.orchestrators.__init__

**Source:** `src\simulation\orchestrators\__init__.py`

## Module Overview

Simulation execution orchestrators for different performance strategies.

## Complete Source Code

```{literalinclude} ../../../src/simulation/orchestrators/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .base import BaseOrchestrator`
- `from .sequential import SequentialOrchestrator`
- `from .batch import BatchOrchestrator`
- `from .parallel import ParallelOrchestrator`
- `from .real_time import RealTimeOrchestrator`


## Advanced Mathematical Theory

### Orchestration Architecture Theory

The orchestration subsystem provides multiple execution strategies for simulation campaigns with different performance characteristics.

#### Orchestration Hierarchy

$$
\text{Orchestrator} = \begin{cases}
\text{Sequential} & \text{(Single-threaded, deterministic)} \\
\text{Batch} & \text{(Vectorized, data parallel)} \\
\text{Parallel} & \text{(Multi-threaded, task parallel)} \\
\text{RealTime} & \text{(Hard deadlines, priority-based)}
\end{cases}
$$

#### Performance Metrics

**Throughput** (simulations per second):
$$
\lambda = \frac{N_{\text{sims}}}{T_{\text{total}}}
$$

**Latency** (time per simulation):
$$
L = \frac{1}{\lambda} = \frac{T_{\text{total}}}{N_{\text{sims}}}
$$

**Speedup** (parallel vs sequential):
$$
S(P) = \frac{T_{\text{seq}}}{T_{\text{par}}(P)}
$$

**Efficiency**:
$$
E(P) = \frac{S(P)}{P}
$$

#### Amdahl's Law

For workload with parallelizable fraction $p$:

$$
S(P) = \frac{1}{(1 - p) + \frac{p}{P}}
$$

**Ideal case** ($p = 1$): $S(P) = P$ (linear speedup)
**Typical case** ($p = 0.9$): $S(P) \approx 5.3$ for $P = 10$

### Load Balancing

**Static load balancing:**
$$
N_i = \left\lfloor \frac{N}{P} \right\rfloor \quad \text{or} \quad \left\lceil \frac{N}{P} \right\rceil
$$

**Dynamic load balancing:**
Work queue with task stealing for uneven workloads.

## Architecture Diagram

\`\`\`{mermaid}
graph TD
    A[Orchestrators Package] --> B[Sequential]
    A --> C[Batch]
    A --> D[Parallel]
    A --> E[RealTime]

    B --> F[Single-threaded<br/>Deterministic]
    C --> G[Vectorized<br/>Data Parallel]
    D --> H[Multi-threaded<br/>Task Parallel]
    E --> I[Priority-based<br/>Hard Deadlines]

    J[Simulation Campaign] --> A
    A --> K[Results]

    L[Performance Metrics] --> M[Throughput λ]
    L --> N[Latency L]
    L --> O[Speedup S_P_]
    L --> P[Efficiency E_P_]

    style A fill:#e1f5ff
    style E fill:#fff4e1
    style K fill:#e8f5e9
\`\`\`

## Usage Examples

### Example 1: Sequential Orchestration

\`\`\`python
from src.simulation.orchestrators import SequentialOrchestrator
from src.controllers import create_smc_for_pso, SMCType

# Create orchestrator

orchestrator = SequentialOrchestrator()

# Define simulation campaign

campaign = {
    'controller_type': SMCType.CLASSICAL,
    'gain_sets': [
        [10, 8, 15, 12, 50, 5],
        [12, 10, 18, 15, 60, 8],
        [15, 12, 20, 18, 70, 10]
    ],
    'duration': 10.0,
    'dt': 0.01
}

# Run campaign sequentially

results = orchestrator.run_campaign(campaign)
print(f"Completed {len(results)} simulations sequentially")
\`\`\`

## Example 2: Parallel Orchestration

\`\`\`python
from src.simulation.orchestrators import ParallelOrchestrator
import multiprocessing

# Create parallel orchestrator

num_workers = multiprocessing.cpu_count()
orchestrator = ParallelOrchestrator(num_workers=num_workers)

# Large-scale campaign

campaign = {
    'controller_type': SMCType.HYBRID,
    'n_trials': 1000,  # Monte Carlo analysis
    'duration': 5.0
}

# Run in parallel

results = orchestrator.run_campaign(campaign)
print(f"Parallel execution with {num_workers} workers")
print(f"Throughput: {len(results) / orchestrator.elapsed_time:.2f} sims/sec")
\`\`\`

## Example 3: Real-Time Orchestration

\`\`\`python
from src.simulation.orchestrators import RealTimeOrchestrator

# Real-time orchestrator with deadline

orchestrator = RealTimeOrchestrator(
    period=0.01,  # 100 Hz update rate
    deadline=0.009  # 90% of period
)

# Real-time campaign

campaign = {
    'controller': controller,
    'duration': 60.0,  # 1 minute real-time
    'sync_mode': 'wall_clock'
}

# Run with hard deadlines

results = orchestrator.run_campaign(campaign)
print(f"Deadline violations: {orchestrator.missed_deadlines}")
print(f"Max jitter: {orchestrator.max_jitter:.6f}s")
\`\`\`

## Example 4: Performance Comparison

\`\`\`python
from src.simulation.orchestrators import (
    SequentialOrchestrator,
    BatchOrchestrator,
    ParallelOrchestrator
)
import time

campaign = {'n_trials': 100, 'duration': 5.0}

orchestrators = {
    'sequential': SequentialOrchestrator(),
    'batch': BatchOrchestrator(batch_size=10),
    'parallel': ParallelOrchestrator(num_workers=8)
}

for name, orch in orchestrators.items():
    start = time.perf_counter()
    results = orch.run_campaign(campaign)
    elapsed = time.perf_counter() - start

    print(f"{name:12s}: {elapsed:.2f}s, "
          f"throughput={len(results)/elapsed:.1f} sims/sec")
\`\`\`

### Example 5: Custom Orchestration Strategy

\`\`\`python
from src.simulation.orchestrators import BaseOrchestrator

class AdaptiveOrchestrator(BaseOrchestrator):
    """Adaptive orchestrator that switches strategy based on load."""

    def __init__(self):
        super().__init__()
        self.sequential = SequentialOrchestrator()
        self.parallel = ParallelOrchestrator()
        self.threshold = 10  # Switch to parallel above threshold

    def run_campaign(self, campaign):
        n_trials = campaign.get('n_trials', 1)

        if n_trials < self.threshold:
            print(f"Using sequential (n={n_trials})")
            return self.sequential.run_campaign(campaign)
        else:
            print(f"Using parallel (n={n_trials})")
            return self.parallel.run_campaign(campaign)

# Use adaptive orchestrator

adaptive = AdaptiveOrchestrator()
results_small = adaptive.run_campaign({'n_trials': 5})
results_large = adaptive.run_campaign({'n_trials': 100})
\`\`\`


## Architecture Diagram

\`\`\`{mermaid}
graph TD
    A[Component] --> B[Subcomponent 1]
    A --> C[Subcomponent 2]
    B --> D[Output]
    C --> D

    style A fill:#e1f5ff
    style D fill:#e8f5e9
\`\`\`


## Usage Examples

### Example 1: Basic Usage

\`\`\`python
# Basic usage example

from src.simulation.orchestrators import Component

component = Component()
result = component.process(data)
\`\`\`

## Example 2: Advanced Configuration

\`\`\`python
# Advanced configuration

component = Component(
    option1=value1,
    option2=value2
)
\`\`\`

## Example 3: Integration with Framework

\`\`\`python
# Integration example

from src.simulation import SimulationRunner

runner = SimulationRunner()
runner.use_component(component)
\`\`\`

## Example 4: Performance Optimization

\`\`\`python
# Performance-optimized usage

component = Component(enable_caching=True)
\`\`\`

## Example 5: Error Handling

\`\`\`python
# Error handling

try:
    result = component.process(data)
except ComponentError as e:
    print(f"Error: {e}")
\`\`\`
