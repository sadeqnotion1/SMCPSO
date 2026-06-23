# simulation.orchestrators.real_time

**Source:** `src\simulation\orchestrators\real_time.py`

## Module Overview

Real-time simulation orchestrator with timing constraints.

## Complete Source Code

```{literalinclude} ../../../src/simulation/orchestrators/real_time.py
:language: python
:linenos:
```



## Classes

### `RealTimeOrchestrator`

**Inherits from:** `BaseOrchestrator`

Real-time simulation orchestrator with timing constraints.

This orchestrator executes simulations with real-time timing constraints,
useful for hardware-in-the-loop testing and real-time control verification.

#### Source Code

```{literalinclude} ../../../src/simulation/orchestrators/real_time.py
:language: python
:pyobject: RealTimeOrchestrator
:linenos:
```

#### Methods (5)

##### `__init__(self, context, real_time_factor, tolerance)`

Initialize real-time orchestrator.

[View full source →](#method-realtimeorchestrator-__init__)

##### `execute(self, initial_state, control_inputs, dt, horizon)`

Execute real-time simulation.

[View full source →](#method-realtimeorchestrator-execute)

##### `_compute_control(self, controller, t, state, step)`

Compute control input with timing measurement.

[View full source →](#method-realtimeorchestrator-_compute_control)

##### `get_real_time_statistics(self)`

Get real-time execution statistics.

[View full source →](#method-realtimeorchestrator-get_real_time_statistics)

##### `set_real_time_factor(self, factor)`

Set real-time scaling factor.

[View full source →](#method-realtimeorchestrator-set_real_time_factor)



### `HardwareInLoopOrchestrator`

**Inherits from:** `RealTimeOrchestrator`

Hardware-in-the-loop simulation orchestrator.

Extends real-time orchestrator with hardware interface .
#### Source Code

```{literalinclude} ../../../src/simulation/orchestrators/real_time.py
:language: python
:pyobject: HardwareInLoopOrchestrator
:linenos:
```

#### Methods (4)

##### `__init__(self, context, hardware_interface, real_time_factor, tolerance)`

Initialize HIL orchestrator.

[View full source →](#method-hardwareinlooporchestrator-__init__)

##### `_read_hardware_state(self)`

Read state from hardware sensors.

[View full source →](#method-hardwareinlooporchestrator-_read_hardware_state)

##### `_write_hardware_control(self, control)`

Write control to hardware actuators.

[View full source →](#method-hardwareinlooporchestrator-_write_hardware_control)

##### `execute_hil(self, controller, horizon, dt)`

Execute hardware-in-the-loop simulation.

[View full source →](#method-hardwareinlooporchestrator-execute_hil)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import time`
- `from typing import Any, Callable, Optional`
- `import numpy as np`
- `from .base import BaseOrchestrator`
- `from ..core.interfaces import ResultContainer`
- `from ..core.time_domain import RealTimeScheduler`
- `from ..results.containers import StandardResultContainer`


## Advanced Mathematical Theory

### Real-Time Scheduling Theory

Real-time orchestration ensures simulations meet hard timing deadlines with predictable execution.

#### Rate Monotonic Scheduling (RMS)

**Priority assignment:** Higher rate → Higher priority

For tasks with periods $T_i$, priorities ordered:
$$
T_1 < T_2 < \cdots < T_n \quad \Rightarrow \quad P_1 > P_2 > \cdots > P_n
$$

**Schedulability test** (Liu & Layland):
$$
\sum_{i=1}^n \frac{C_i}{T_i} \leq n(2^{1/n} - 1)
$$

where $C_i$ is worst-case execution time (WCET) and $T_i$ is period.

For large $n$: Bound approaches $\ln 2 \approx 0.693$

#### Earliest Deadline First (EDF)

**Dynamic priority:** Earliest deadline → Highest priority

**Schedulability test:**
$$
\sum_{i=1}^n \frac{C_i}{T_i} \leq 1
$$

**Optimal:** If any algorithm can schedule tasks, EDF can.

#### Deadline Analysis

**Response time** $R_i$ for task $i$:
$$
R_i = C_i + \sum_{j \in hp(i)} \left\lceil \frac{R_i}{T_j} \right\rceil C_j
$$

where $hp(i)$ is set of higher-priority tasks.

**Schedulability:** $R_i \leq D_i$ for all tasks

#### Jitter Analysis

**Jitter** (variation in response time):
$$
J_i = R_i^{\max} - R_i^{\min}
$$

**Total jitter** (including release jitter):
$$
J_i^{\text{total}} = J_i^{\text{release}} + J_i^{\text{response}}
$$

#### Weakly-Hard Real-Time Constraints

**$(m, k)$-firm deadlines:** At most $m$ out of any $k$ consecutive deadlines can be missed.

**Constraint check:**
$$
\sum_{i=n-k+1}^{n} \mathbb{1}_{\text{miss}}(i) \leq m
$$

**Example:** $(1, 10)$-firm means at most 1 miss in any 10 consecutive deadlines.

### Performance Guarantees

**Average-case guarantee:**
$$
P(R_i \leq D_i) \geq 1 - \epsilon
$$

for small $\epsilon$ (e.g., $\epsilon = 0.01$ for 99% deadline guarantee).

## Architecture Diagram

\`\`\`{mermaid}
graph TD
    A[Real-Time Orchestrator] --> B[Task Queue]
    B --> C{Priority Scheduler}

    C -->|RMS| D[Rate-based Priority]
    C -->|EDF| E[Deadline-based Priority]

    D --> F[Execute Task]
    E --> F

    F --> G[Start Timer]
    G --> H[Simulation Step]
    H --> I[End Timer]

    I --> J{Deadline Check}
    J -->|t_exec ≤ deadline| K[Success]
    J -->|t_exec > deadline| L[Violation]

    K --> M[Update Stats]
    L --> M

    M --> N{_m, k_-firm Check}
    N -->|Pass| O[Continue]
    N -->|Fail| P[Alert/Recovery]

    Q[Real-Time Clock] --> R[Period Sync]
    R --> B

    style C fill:#fff4e1
    style L fill:#ffebee
    style O fill:#e8f5e9
\`\`\`

## Usage Examples

### Example 1: Basic Real-Time Orchestration

\`\`\`python
from src.simulation.orchestrators import RealTimeOrchestrator
import time

# Create real-time orchestrator (100 Hz)

orchestrator = RealTimeOrchestrator(
    period=0.01,  # 10ms period
    deadline=0.009,  # 9ms deadline (90%)
    scheduler='rms'  # Rate monotonic scheduling
)

# Real-time simulation

campaign = {
    'controller': controller,
    'dynamics': dynamics,
    'duration': 10.0
}

start = time.perf_counter()
results = orchestrator.run_campaign(campaign)
elapsed = time.perf_counter() - start

print(f"Real-time execution: {elapsed:.2f}s (expected: 10.0s)")
print(f"Deadline violations: {orchestrator.stats['violations']}")
print(f"Max jitter: {orchestrator.stats['max_jitter']:.6f}s")
\`\`\`

## Example 2: Priority-Based Scheduling

\`\`\`python
from src.simulation.orchestrators import RealTimeOrchestrator

# Multiple tasks with different priorities

tasks = [
    {'name': 'critical', 'period': 0.01, 'deadline': 0.009, 'priority': 10},
    {'name': 'normal', 'period': 0.05, 'deadline': 0.045, 'priority': 5},
    {'name': 'background', 'period': 0.1, 'deadline': 0.09, 'priority': 1}
]

orchestrator = RealTimeOrchestrator(scheduler='rms')

for task in tasks:
    orchestrator.add_task(
        name=task['name'],
        period=task['period'],
        deadline=task['deadline'],
        callback=lambda: run_simulation(task)
    )

# Run all tasks with priority scheduling

orchestrator.start()

# Monitor performance

stats = orchestrator.get_statistics()
for task_name, task_stats in stats.items():
    print(f"{task_name}:")
    print(f"  Violations: {task_stats['violations']}")
    print(f"  Mean latency: {task_stats['mean_latency']:.6f}s")
    print(f"  95th percentile: {task_stats['p95_latency']:.6f}s")
\`\`\`

## Example 3: Deadline Monitoring and Recovery

\`\`\`python
from src.simulation.orchestrators import RealTimeOrchestrator

# Real-time with recovery callback

def deadline_violation_handler(task_name, actual_time, deadline):
    print(f"WARNING: {task_name} missed deadline: "
          f"{actual_time:.6f}s > {deadline:.6f}s")
    # Trigger recovery action
    return 'continue'  # or 'abort', 'degrade'

orchestrator = RealTimeOrchestrator(
    period=0.01,
    deadline=0.009,
    violation_handler=deadline_violation_handler
)

# Weakly-hard (1, 10)-firm constraint

orchestrator.set_weakly_hard_constraint(m=1, k=10)

results = orchestrator.run_campaign(campaign)

# Check constraint satisfaction

if orchestrator.check_weakly_hard():
    print("(1, 10)-firm constraint satisfied!")
else:
    print("Constraint violated - too many deadline misses")
\`\`\`

## Example 4: Jitter Analysis

\`\`\`python
from src.simulation.orchestrators import RealTimeOrchestrator
import matplotlib.pyplot as plt

orchestrator = RealTimeOrchestrator(period=0.01, deadline=0.009)

# Run simulation with jitter tracking

results = orchestrator.run_campaign(campaign, track_jitter=True)

# Analyze jitter

jitter_data = orchestrator.get_jitter_data()

print(f"Mean jitter: {jitter_data['mean']:.6f}s")
print(f"Max jitter: {jitter_data['max']:.6f}s")
print(f"Std dev jitter: {jitter_data['std']:.6f}s")

# Plot jitter distribution

plt.figure(figsize=(10, 6))
plt.hist(jitter_data['samples'], bins=50, density=True)
plt.xlabel('Jitter (s)')
plt.ylabel('Probability Density')
plt.title('Response Time Jitter Distribution')
plt.axvline(jitter_data['mean'], color='r', linestyle='--', label='Mean')
plt.axvline(jitter_data['p95'], color='g', linestyle='--', label='95th percentile')
plt.legend()
plt.grid(True)
plt.show()
\`\`\`

## Example 5: Schedulability Analysis

\`\`\`python
from src.simulation.orchestrators import RealTimeOrchestrator

def check_schedulability(tasks):
    """Check schedulability using Liu & Layland bound."""

    # Sort tasks by period (Rate Monotonic)
    tasks_sorted = sorted(tasks, key=lambda t: t['period'])

    # Compute utilization
    utilization = sum(t['wcet'] / t['period'] for t in tasks_sorted)

    # Liu & Layland bound
    n = len(tasks_sorted)
    bound = n * (2**(1/n) - 1)

    print(f"Utilization: {utilization:.4f}")
    print(f"Liu & Layland bound: {bound:.4f}")

    if utilization <= bound:
        print("✓ Schedulable by RMS (sufficient test)")
        return True
    elif utilization <= 1.0:
        print("? May be schedulable (exact test required)")
        return None
    else:
        print("✗ Not schedulable (utilization > 1)")
        return False

# Example task set

tasks = [
    {'period': 0.01, 'wcet': 0.003},  # 30% utilization
    {'period': 0.05, 'wcet': 0.010},  # 20% utilization
    {'period': 0.1, 'wcet': 0.020}    # 20% utilization
]

is_schedulable = check_schedulability(tasks)

if is_schedulable:
    orchestrator = RealTimeOrchestrator(scheduler='rms')
    # ... configure and run
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
