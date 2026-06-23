# utils.monitoring.latency

**Source:** `src\utils\monitoring\latency.py`

## Module Overview

Real-time latency monitoring for control loops.

Provides tools for monitoring control loop execution times and detecting
deadline violations in real-time systems.

## Complete Source Code

```{literalinclude} ../../../src/utils/monitoring/latency.py
:language: python
:linenos:
```



## Classes

### `LatencyMonitor`

Measure and analyse loop latency.

Parameters
dt : float
    Nominal control period (seconds).
margin : float, optional
    Fraction of ``dt`` regarded as acceptable margin before
    flagging an overrun. Defaults to 0.9; a latency exceeding
    ``dt`` will always be counted as a missed deadline.

#### Source Code

```{literalinclude} ../../../src/utils/monitoring/latency.py
:language: python
:pyobject: LatencyMonitor
:linenos:
```

#### Methods (8)

##### `__init__(self, dt, margin)`

[View full source →](#method-latencymonitor-__init__)

##### `start(self)`

Record the start time and return it.

[View full source →](#method-latencymonitor-start)

##### `end(self, start_time)`

Record the end time and determine if a deadline was missed.

[View full source →](#method-latencymonitor-end)

##### `stats(self)`

Return median and 95th percentile of recorded latencies.

[View full source →](#method-latencymonitor-stats)

##### `missed_rate(self)`

Return the fraction of samples that missed the deadline.

[View full source →](#method-latencymonitor-missed_rate)

##### `enforce(self, m, k)`

Check a weakly‑hard (m,k) deadline miss constraint.

[View full source →](#method-latencymonitor-enforce)

##### `reset(self)`

Clear all recorded samples.

[View full source →](#method-latencymonitor-reset)

##### `get_recent_stats(self, n)`

Get statistics for the most recent n samples.

[View full source →](#method-latencymonitor-get_recent_stats)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import time`
- `from typing import List, Tuple`
- `import numpy as np`


## Advanced Mathematical Theory

### Monitoring Utilities Theory

(Detailed mathematical theory for monitoring utilities to be added...)

**Key concepts:**
- Mathematical foundations
- Algorithmic principles
- Performance characteristics
- Integration patterns


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

### Example 1: Basic Deadline Monitoring

Monitor control loop execution time and detect deadline violations:

\`\`\`python
from src.utils.monitoring.latency import LatencyMonitor

# Create monitor for 10ms control loop (dt=0.01s)
monitor = LatencyMonitor(dt=0.01, margin=0.9)

for step in range(1000):
    # Start timing
    start = monitor.start()

    # ... control computation (should finish in <10ms) ...
    control_output = controller.compute_control(state)

    # End timing and check for deadline miss
    missed = monitor.end(start)

    if missed:
        print(f"WARNING: Deadline missed at step {step}")

# Get performance statistics
median_latency, p95_latency = monitor.stats()
miss_rate = monitor.missed_rate()

print(f"Median latency: {median_latency*1000:.2f}ms")
print(f"95th percentile: {p95_latency*1000:.2f}ms")
print(f"Miss rate: {miss_rate*100:.1f}%")
\`\`\`

### Example 2: Weakly-Hard Real-Time Constraints

Enforce (m,k) weakly-hard constraints - allow at most (k-m) deadline misses in any k consecutive samples:

\`\`\`python
from src.utils.monitoring.latency import LatencyMonitor

monitor = LatencyMonitor(dt=0.01)

for step in range(1000):
    start = monitor.start()
    # ... control loop ...
    monitor.end(start)

    # Check (m,k) = (950, 1000): allow ≤50 misses in 1000 steps
    if step >= 1000 and not monitor.enforce(m=950, k=1000):
        raise RuntimeError(
            f"CRITICAL: Weakly-hard constraint violated! "
            f"More than 50 deadline misses in last 1000 steps"
        )

print("Weakly-hard constraint satisfied throughout simulation")
\`\`\`

### Example 3: Adaptive Monitoring with Reset

Monitor different phases of simulation with periodic reset:

\`\`\`python
from src.utils.monitoring.latency import LatencyMonitor

monitor = LatencyMonitor(dt=0.01)

# Phase 1: Transient response (0-5s)
for step in range(500):
    start = monitor.start()
    # ... control loop ...
    monitor.end(start)

# Analyze transient phase
transient_stats = monitor.get_recent_stats(n=500)
print(f"Transient phase median latency: {transient_stats['median']*1000:.2f}ms")

# Reset for steady-state monitoring
monitor.reset()

# Phase 2: Steady-state (5-10s)
for step in range(500):
    start = monitor.start()
    # ... control loop ...
    monitor.end(start)

# Compare steady-state performance
steady_stats = monitor.get_recent_stats(n=500)
print(f"Steady-state median latency: {steady_stats['median']*1000:.2f}ms")
\`\`\`
