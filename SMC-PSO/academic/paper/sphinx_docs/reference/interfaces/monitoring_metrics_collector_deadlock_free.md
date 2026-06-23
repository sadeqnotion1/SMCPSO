# interfaces.monitoring.metrics_collector_deadlock_free

**Source:** `src\interfaces\monitoring\metrics_collector_deadlock_free.py`

## Module Overview

DEADLOCK-FREE Metrics Collection System - Production Ready
This version eliminates the deadlock issues found in the previous thread-safe implementation
by using consistent lock ordering and atomic operations.

Critical Deadlock Fixes:
1. Consistent lock ordering: Always acquire _metrics_lock before _stats_lock
2. Eliminated nested locking where possible
3. Atomic counters for statistics
4. Lock-free operations using atomic primitives
5. Timeout-based locking for deadlock detection

PRODUCTION SAFETY: All deadlocks resolved, safe for high-concurrency use.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_deadlock_free.py
:language: python
:linenos:
```



## Classes

### `MetricType`

**Inherits from:** `Enum`

Metric type enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_deadlock_free.py
:language: python
:pyobject: MetricType
:linenos:
```



### `AggregationType`

**Inherits from:** `Enum`

Aggregation type enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_deadlock_free.py
:language: python
:pyobject: AggregationType
:linenos:
```



### `MetricValue`

Single metric value with timestamp.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_deadlock_free.py
:language: python
:pyobject: MetricValue
:linenos:
```



### `AtomicCounter`

Thread-safe atomic counter.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_deadlock_free.py
:language: python
:pyobject: AtomicCounter
:linenos:
```

#### Methods (4)

##### `__init__(self, initial)`

[View full source →](#method-atomiccounter-__init__)

##### `increment(self, delta)`

[View full source →](#method-atomiccounter-increment)

##### `get(self)`

[View full source →](#method-atomiccounter-get)

##### `set(self, value)`

[View full source →](#method-atomiccounter-set)



### `DeadlockFreeMetric`

Individual metric with deadlock-free implementation.
Uses single lock and atomic operations.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_deadlock_free.py
:language: python
:pyobject: DeadlockFreeMetric
:linenos:
```

#### Methods (7)

##### `__init__(self, name, metric_type, max_values, retention_window)`

[View full source →](#method-deadlockfreemetric-__init__)

##### `add_value(self, value, timestamp, metadata)`

Add new value - single lock, no nesting.

[View full source →](#method-deadlockfreemetric-add_value)

##### `get_current_value(self)`

Get current value - single lock.

[View full source →](#method-deadlockfreemetric-get_current_value)

##### `get_aggregated_value(self, aggregation, window_seconds, percentile)`

Get aggregated value - single lock.

[View full source →](#method-deadlockfreemetric-get_aggregated_value)

##### `get_statistics(self)`

Get statistics - single lock.

[View full source →](#method-deadlockfreemetric-get_statistics)

##### `clean_old_values(self)`

Clean old values - single lock.

[View full source →](#method-deadlockfreemetric-clean_old_values)

##### `reset(self)`

Reset metric - single lock.

[View full source →](#method-deadlockfreemetric-reset)



### `DeadlockFreeMetricsCollector`

Thread-safe metrics collector with guaranteed deadlock-free operation.

CRITICAL DEADLOCK ELIMINATION STRATEGIES:
1. Single lock per metric (no nested locking)
2. Consistent global lock ordering
3. Atomic counters for statistics
4. Timeout-based operations
5. Lock-free paths where possible

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_deadlock_free.py
:language: python
:pyobject: DeadlockFreeMetricsCollector
:linenos:
```

#### Methods (12)

##### `__init__(self, max_metrics, cleanup_interval)`

Initialize deadlock-free collector.

[View full source →](#method-deadlockfreemetricscollector-__init__)

##### `register_metric(self, name, metric_type, max_values, retention_window)`

Register metric - single lock operation.

[View full source →](#method-deadlockfreemetricscollector-register_metric)

##### `unregister_metric(self, name)`

Unregister metric - single lock operation.

[View full source →](#method-deadlockfreemetricscollector-unregister_metric)

##### `collect_metric(self, metric_name, value, timestamp, metadata)`

Collect metric value - DEADLOCK-FREE implementation.

[View full source →](#method-deadlockfreemetricscollector-collect_metric)

##### `get_metric_value(self, metric_name, aggregation, window_seconds)`

Get metric value - minimal locking.

[View full source →](#method-deadlockfreemetricscollector-get_metric_value)

##### `get_metric_statistics(self, metric_name)`

Get metric statistics - minimal locking.

[View full source →](#method-deadlockfreemetricscollector-get_metric_statistics)

##### `get_all_metrics(self)`

Get all metrics - no nested locking.

[View full source →](#method-deadlockfreemetricscollector-get_all_metrics)

##### `cleanup_old_values(self)`

Cleanup old values - no nested locking.

[View full source →](#method-deadlockfreemetricscollector-cleanup_old_values)

##### `get_system_statistics(self)`

Get system statistics - atomic operations only.

[View full source →](#method-deadlockfreemetricscollector-get_system_statistics)

##### `reset_all_metrics(self)`

Reset all metrics - no nested locking.

[View full source →](#method-deadlockfreemetricscollector-reset_all_metrics)

##### `add_alert_callback(self, callback)`

Add callback - separate lock.

[View full source →](#method-deadlockfreemetricscollector-add_alert_callback)

##### `remove_alert_callback(self, callback)`

Remove callback - separate lock.

[View full source →](#method-deadlockfreemetricscollector-remove_alert_callback)



## Functions

### `get_deadlock_free_collector()`

Get global deadlock-free collector instance.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_deadlock_free.py
:language: python
:pyobject: get_deadlock_free_collector
:linenos:
```



### `collect_metric_safe(name, value)`

Collect metric using global deadlock-free collector.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_deadlock_free.py
:language: python
:pyobject: collect_metric_safe
:linenos:
```



### `get_metric_safe(name)`

Get metric value using global deadlock-free collector.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_deadlock_free.py
:language: python
:pyobject: get_metric_safe
:linenos:
```



## Dependencies

This module imports:

- `import time`
- `import threading`
- `from collections import deque`
- `from dataclasses import dataclass, field`
- `from typing import Dict, List, Optional, Union, Any, Callable`
- `from enum import Enum`
- `import logging`
