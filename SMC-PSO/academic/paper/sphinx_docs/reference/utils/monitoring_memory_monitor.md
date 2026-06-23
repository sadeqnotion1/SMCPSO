# utils.monitoring.memory_monitor

**Source:** `src\utils\monitoring\memory_monitor.py`

## Module Overview

Production memory monitoring for controllers (Issue #15).

Provides real-time memory leak detection and alerting for production
deployments of SMC controllers. Monitors memory growth trends and triggers
alerts when thresholds are exceeded.

## Complete Source Code

```{literalinclude} ../../../src/utils/monitoring/memory_monitor.py
:language: python
:linenos:
```



## Classes

### `MemoryAlert`

Memory alert data structure.

#### Source Code

```{literalinclude} ../../../src/utils/monitoring/memory_monitor.py
:language: python
:pyobject: MemoryAlert
:linenos:
```



### `ProductionMemoryMonitor`

Real-time memory monitoring for production deployments.

Usage Example:
    >>> monitor = ProductionMemoryMonitor(threshold_mb=500.0)
    >>> # In control loop:
    >>> alert = monitor.check_memory()
    >>> if alert:
    >>>     print(f"Memory alert: {alert.message}")

#### Source Code

```{literalinclude} ../../../src/utils/monitoring/memory_monitor.py
:language: python
:pyobject: ProductionMemoryMonitor
:linenos:
```

#### Methods (6)

##### `__init__(self, threshold_mb, alert_callback, trend_window)`

Initialize production memory monitor.

[View full source →](#method-productionmemorymonitor-__init__)

##### `check_memory(self)`

Check current memory usage against threshold.

[View full source →](#method-productionmemorymonitor-check_memory)

##### `analyze_trend(self)`

Analyze memory growth trend.

[View full source →](#method-productionmemorymonitor-analyze_trend)

##### `reset_baseline(self)`

Reset baseline to current memory usage.

[View full source →](#method-productionmemorymonitor-reset_baseline)

##### `get_memory_report(self)`

Generate human-readable memory report.

[View full source →](#method-productionmemorymonitor-get_memory_report)

##### `_default_alert(self, alert)`

Default alert handler.

[View full source →](#method-productionmemorymonitor-_default_alert)



### `ControllerMemoryTracker`

Specialized memory tracker for SMC controller instantiations.

Tracks memory usage per controller type and provides diagnostics
for memory leak detection during repeated instantiation.

Usage:
    >>> tracker = ControllerMemoryTracker()
    >>> for i in range(1000):
    >>>     controller = ClassicalSMC(...)
    >>>     tracker.track_instantiation("classical", controller)
    >>>     controller.cleanup()
    >>> report = tracker.get_report()

#### Source Code

```{literalinclude} ../../../src/utils/monitoring/memory_monitor.py
:language: python
:pyobject: ControllerMemoryTracker
:linenos:
```

#### Methods (4)

##### `__init__(self)`

Initialize controller memory tracker.

[View full source →](#method-controllermemorytracker-__init__)

##### `track_instantiation(self, controller_type, controller)`

Track a controller instantiation.

[View full source →](#method-controllermemorytracker-track_instantiation)

##### `get_report(self)`

Generate memory tracking report.

[View full source →](#method-controllermemorytracker-get_report)

##### `check_leak_threshold(self, threshold_mb_per_1000)`

Check if any controller type exceeds leak threshold.

[View full source →](#method-controllermemorytracker-check_leak_threshold)



## Functions

### `monitor_controller_loop(controller_class, config, iterations, cleanup_interval)`

Monitor memory usage during a controller control loop.

Args:
    controller_class: Controller class to instantiate
    config: Configuration dictionary for controller
    iterations: Number of control iterations
    cleanup_interval: Call cleanup() every N iterations

Returns:
    Dictionary with monitoring results

#### Source Code

```{literalinclude} ../../../src/utils/monitoring/memory_monitor.py
:language: python
:pyobject: monitor_controller_loop
:linenos:
```



## Dependencies

This module imports:

- `import psutil`
- `import logging`
- `import time`
- `from typing import Callable, Optional, List, Tuple`
- `from dataclasses import dataclass`
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

### Example 1: Basic Usage

\`\`\`python
from src.utils.monitoring_memory_monitor import Component

component = Component()
result = component.process(data)
\`\`\`

### Example 2: Advanced Configuration

\`\`\`python
component = Component(
    option1=value1,
    option2=value2
)
\`\`\`

### Example 3: Integration with Simulation

\`\`\`python
# Integration example

for k in range(num_steps):
    result = component.process(x)
    x = update(x, result)
\`\`\`

## Example 4: Performance Optimization

\`\`\`python
component = Component(enable_caching=True)
\`\`\`

### Example 5: Error Handling

\`\`\`python
try:
    result = component.process(data)
except ComponentError as e:
    print(f"Error: {e}")
\`\`\`
