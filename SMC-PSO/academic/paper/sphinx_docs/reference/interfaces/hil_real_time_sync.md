# interfaces.hil.real_time_sync

**Source:** `src\interfaces\hil\real_time_sync.py`

## Module Overview

Real-time synchronization and scheduling for HIL systems.
This module provides real-time features including high-priority scheduling,
deadline monitoring, and timing constraint enforcement for deterministic
control system execution.


## Mathematical Foundation

### Real-Time Synchronization

Maintain synchronized execution across plant and controller:

```{math}
|t_{\text{plant}} - t_{\text{controller}}| < \delta_{\text{sync}}
```

Where $\delta_{\text{sync}}$ is the maximum allowable time skew (default: 1 ms).

### Clock Synchronization

**Network Time Protocol (NTP) Adaptation:**

```{math}
\begin{align}
t_{\text{offset}} &= \frac{(t_2 - t_1) + (t_3 - t_4)}{2} \\
t_{\text{latency}} &= \frac{(t_4 - t_1) - (t_3 - t_2)}{2}
\end{align}
```

Where:
- $t_1$: Client send time
- $t_2$: Server receive time
- $t_3$: Server send time
- $t_4$: Client receive time

### Rate Synchronization

Synchronize simulation rates using PLL-style feedback:

```{math}
\Delta t_{\text{adjusted}} = \Delta t_{\text{nominal}} + K_p (t_{\text{ref}} - t_{\text{local}})
```

Where:
- $K_p$: Proportional gain for rate adjustment
- $t_{\text{ref}}$: Reference time from remote
- $t_{\text{local}}$: Local simulation time

### Deadline-Driven Scheduling

**Earliest Deadline First (EDF) Policy:**

```{math}
\text{Priority}(\text{Task}_i) = \frac{1}{D_i - t}
```

Where:
- $D_i$: Deadline for task $i$
- $t$: Current time
- Higher priority = earlier deadline

### Timing Constraints

**Hard Real-Time Constraint:**
```{math}
T_{\text{exec}} + T_{\text{comm}} \leq \Delta t_{\text{control}}
```

**Jitter Bound:**
```{math}
J = \max_k |t_k - t_{k-1} - \Delta t| < J_{\text{max}}
```

### Synchronization Protocols

**Barrier Synchronization:**
All processes wait at barrier until all arrive:

```{math}
\forall p \in \text{Processes} : t_p \geq t_{\text{barrier}}
```

**Lockstep Execution:**
Synchronize every control cycle:

```{math}
\begin{align}
\text{Plant} &: \text{step}(n) \rightarrow \text{wait}(n) \\
\text{Controller} &: \text{compute}(n) \rightarrow \text{signal}(n)
\end{align}
```

### Time Warp Algorithm

Optimistic synchronization with rollback:

```{math}
\begin{align}
\text{Execute} &: t_{\text{local}} < t_{\text{virtual}} \\
\text{Rollback} &: \text{if } t_{\text{msg}} < t_{\text{virtual}}
\end{align}
```

**Rollback Cost:**
```{math}
C_{\text{rollback}} = C_{\text{restore}} + C_{\text{recompute}}
```

### Performance Monitoring

**Synchronization Quality Metrics:**

1. **Time Skew:**
   ```{math}
   \text{Skew} = |t_{\text{plant}} - t_{\text{controller}}|
   ```

2. **Drift Rate:**
   ```{math}
   \text{Drift} = \frac{d}{dt}(t_{\text{plant}} - t_{\text{controller}})
   ```

3. **Synchronization Efficiency:**
   ```{math}
   \eta_{\text{sync}} = \frac{T_{\text{productive}}}{T_{\text{total}}}
   ```

**Target Metrics:**
- Skew < 1 ms
- Drift < 100 ppm
- Efficiency > 95%

## Architecture Diagram

```{mermaid}
sequenceDiagram
    participant P as Plant
    participant S as Sync Manager
    participant C as Controller

    Note over P,C: Synchronization Cycle

    P->>S: Send Timestamp t_p
    C->>S: Send Timestamp t_c
    S->>S: Compute Offset
    S->>P: Adjust Rate
    S->>C: Adjust Rate

    Note over P,C: Execution Cycle

    P->>P: Step Dynamics
    P->>S: Wait at Barrier
    C->>C: Compute Control
    C->>S: Wait at Barrier
    S->>P: Release
    S->>C: Release

    Note over P,C: Metrics Collection

    S->>S: Log Skew
    S->>S: Log Jitter
    S->>S: Check Violations
```

**Synchronization Protocol:**
1. **Clock Sync Phase**: Exchange timestamps and compute offset
2. **Barrier Phase**: Wait for all processes to reach synchronization point
3. **Release Phase**: All processes proceed together
4. **Monitoring Phase**: Track timing metrics and violations

## Usage Examples

### Example 1: Basic Synchronization

```python
from src.interfaces.hil.real_time_sync import RealTimeSync

# Initialize synchronizer
sync = RealTimeSync(
    processes=["plant", "controller"],
    target_dt=0.01,  # 10 ms control period
    tolerance=0.001  # 1 ms tolerance
)

# Synchronize processes
sync.synchronize()

# Plant and controller

now running at same rate
```

## Example 2: Clock Synchronization

```python
from src.interfaces.hil.real_time_sync import ClockSync

# Create clock synchronizer
clock_sync = ClockSync()

# Client-server clock sync
def client_sync():
    t1 = time.time()
    # Send to server
    t2, t3 = server.get_timestamps()
    t4 = time.time()

    # Compute offset
    offset = clock_sync.compute_offset(t1, t2, t3, t4)
    print(f"Clock offset: {offset * 1000:.2f} ms")

client_sync()
```

### Example 3: Barrier Synchronization

```python
from src.interfaces.hil.real_time_sync import BarrierSync
from threading import Thread

# Create barrier
barrier = BarrierSync(n_processes=2)

def plant_process():
    for step in range(1000):
        # Compute dynamics
        plant.step()
        # Wait for controller
        barrier.wait()

def controller_process():
    for step in range(1000):
        # Compute control
        controller.compute()
        # Wait for plant
        barrier.wait()

# Run synchronized
t1 = Thread(target=plant_process)
t2 = Thread(target=controller_process)
t1.start()
t2.start()
t1.join()
t2.join()
```

## Example 4: Adaptive Rate Synchronization

```python
from src.interfaces.hil.real_time_sync import AdaptiveSync

# Adaptive synchronizer
sync = AdaptiveSync(
    kp=0.1,  # Proportional gain
    target_rate=100.0  # 100 Hz
)

# Plant loop with adaptive timing
plant_time = 0.0
for step in range(10000):
    start = time.time()

    # Step dynamics
    plant.step(dt_adjusted)

    # Measure actual time
    actual_dt = time.time() - start

    # Adjust for next iteration
    dt_adjusted = sync.adjust_rate(actual_dt, step)

    plant_time += dt_adjusted
```

### Example 5: Deadline Monitoring

```python
from src.interfaces.hil.real_time_sync import DeadlineMonitor

# Deadline monitor
monitor = DeadlineMonitor(
    deadline=0.01,  # 10 ms deadline
    tolerance=0.001  # 1 ms tolerance
)

# Control loop with deadline checking
for step in range(5000):
    start = time.time()

    # Compute control
    control = controller.compute(state)

    # Check deadline
    elapsed = time.time() - start
    if not monitor.check_deadline(elapsed):
        print(f"Deadline violation at step {step}: {elapsed*1000:.2f} ms")

# Report violations
print(f"Total violations: {monitor.violation_count}")
print(f"Violation rate: {monitor.violation_rate * 100:.2f}%")
```

## Complete Source Code

```{literalinclude} ../../../src/interfaces/hil/real_time_sync.py
:language: python
:linenos:
```



## Classes

### `SchedulingPolicy`

**Inherits from:** `Enum`

Real-time scheduling policy enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/real_time_sync.py
:language: python
:pyobject: SchedulingPolicy
:linenos:
```



### `TimingViolationType`

**Inherits from:** `Enum`

Timing violation type enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/real_time_sync.py
:language: python
:pyobject: TimingViolationType
:linenos:
```



### `TimingConstraints`

Real-time timing constraints.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/real_time_sync.py
:language: python
:pyobject: TimingConstraints
:linenos:
```



### `TimingEvent`

Timing event record.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/real_time_sync.py
:language: python
:pyobject: TimingEvent
:linenos:
```



### `DeadlineMissHandler`

Handler for deadline miss events.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/real_time_sync.py
:language: python
:pyobject: DeadlineMissHandler
:linenos:
```

#### Methods (4)

##### `__init__(self)`

[View full source →](#method-deadlinemisshandler-__init__)

##### `add_handler(self, handler)`

Add deadline miss handler.

[View full source →](#method-deadlinemisshandler-add_handler)

##### `handle_deadline_miss(self, event)`

Handle deadline miss event.

[View full source →](#method-deadlinemisshandler-handle_deadline_miss)

##### `get_statistics(self)`

Get deadline miss statistics.

[View full source →](#method-deadlinemisshandler-get_statistics)



### `RealTimeScheduler`

Real-time scheduler for HIL systems.

Provides deterministic scheduling with deadline monitoring,
CPU affinity control, and real-time priority management.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/real_time_sync.py
:language: python
:pyobject: RealTimeScheduler
:linenos:
```

#### Methods (14)

##### `__init__(self, sample_time, priority, cpu_affinity)`

Initialize real-time scheduler.

[View full source →](#method-realtimescheduler-__init__)

##### `start(self)`

Start real-time scheduler.

[View full source →](#method-realtimescheduler-start)

##### `stop(self)`

Stop real-time scheduler.

[View full source →](#method-realtimescheduler-stop)

##### `wait_for_next_period(self)`

Wait for next scheduling period.

[View full source →](#method-realtimescheduler-wait_for_next_period)

##### `set_constraints(self, constraints)`

Set timing constraints.

[View full source →](#method-realtimescheduler-set_constraints)

##### `get_timing_statistics(self)`

Get timing performance statistics.

[View full source →](#method-realtimescheduler-get_timing_statistics)

##### `add_deadline_miss_handler(self, handler)`

Add deadline miss handler.

[View full source →](#method-realtimescheduler-add_deadline_miss_handler)

##### `_configure_real_time(self)`

Configure real-time scheduling properties.

[View full source →](#method-realtimescheduler-_configure_real_time)

##### `_configure_linux_rt(self)`

Configure Linux real-time scheduling.

[View full source →](#method-realtimescheduler-_configure_linux_rt)

##### `_configure_psutil_rt(self)`

Configure real-time properties using psutil.

[View full source →](#method-realtimescheduler-_configure_psutil_rt)

##### `_restore_settings(self)`

Restore original scheduling settings.

[View full source →](#method-realtimescheduler-_restore_settings)

##### `_precise_sleep(self, sleep_time)`

High-precision sleep implementation.

[View full source →](#method-realtimescheduler-_precise_sleep)

##### `_handle_deadline_miss(self, current_time, deadline)`

Handle deadline miss event.

[View full source →](#method-realtimescheduler-_handle_deadline_miss)

##### `_record_jitter(self, jitter)`

Record timing jitter.

[View full source →](#method-realtimescheduler-_record_jitter)



### `HighResolutionTimer`

High-resolution timer for precise timing control.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/real_time_sync.py
:language: python
:pyobject: HighResolutionTimer
:linenos:
```

#### Methods (5)

##### `__init__(self)`

[View full source →](#method-highresolutiontimer-__init__)

##### `start(self)`

Start timer.

[View full source →](#method-highresolutiontimer-start)

##### `elapsed(self)`

Get elapsed time in seconds.

[View full source →](#method-highresolutiontimer-elapsed)

##### `elapsed_ns(self)`

Get elapsed time in nanoseconds.

[View full source →](#method-highresolutiontimer-elapsed_ns)

##### `sleep_until(target_time)`

Sleep until specific time.

[View full source →](#method-highresolutiontimer-sleep_until)



### `RTThreadScheduler`

Real-time thread scheduler for CPU-intensive tasks.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/real_time_sync.py
:language: python
:pyobject: RTThreadScheduler
:linenos:
```

#### Methods (4)

##### `__init__(self)`

[View full source →](#method-rtthreadscheduler-__init__)

##### `create_rt_thread(self, target, priority, cpu_affinity)`

Create real-time thread.

[View full source →](#method-rtthreadscheduler-create_rt_thread)

##### `start_all_threads(self)`

Start all created threads.

[View full source →](#method-rtthreadscheduler-start_all_threads)

##### `stop_all_threads(self)`

Stop all threads.

[View full source →](#method-rtthreadscheduler-stop_all_threads)



### `TimingSynchronizer`

Synchronize multiple real-time processes.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/real_time_sync.py
:language: python
:pyobject: TimingSynchronizer
:linenos:
```

#### Methods (4)

##### `__init__(self, num_processes)`

[View full source →](#method-timingsynchronizer-__init__)

##### `create_sync_point(self)`

Create synchronization point.

[View full source →](#method-timingsynchronizer-create_sync_point)

##### `wait_sync_point(self, sync_id, timeout)`

Wait at synchronization point.

[View full source →](#method-timingsynchronizer-wait_sync_point)

##### `get_sync_statistics(self)`

Get synchronization statistics.

[View full source →](#method-timingsynchronizer-get_sync_statistics)



## Dependencies

This module imports:

- `import asyncio`
- `import time`
- `import threading`
- `import os`
- `import signal`
- `from dataclasses import dataclass, field`
- `from typing import Optional, List, Callable, Dict, Any`
- `from enum import Enum`
- `import logging`
