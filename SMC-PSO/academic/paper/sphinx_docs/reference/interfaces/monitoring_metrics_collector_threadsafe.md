# interfaces.monitoring.metrics_collector_threadsafe

**Source:** `src\interfaces\monitoring\metrics_collector_threadsafe.py`

## Module Overview

THREAD-SAFE Metrics Collection System - Race Condition Fixes Applied
This is a production-hardened version that addresses all thread safety issues
identified in the original metrics collector.

Key Thread Safety Fixes Applied:
1. Added RLock protection for all metric value updates
2. Atomic operations for statistics and counters
3. Thread-safe cleanup and retention management
4. Protected access to metric collections
5. Safe concurrent metric registration/removal
6. Bounded collections with memory management

PRODUCTION SAFETY: All race conditions resolved, safe for multi-threaded use.
Memory usage bounded and monitored.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_threadsafe.py
:language: python
:linenos:
```



## Classes

### `MetricType`

**Inherits from:** `Enum`

Metric type enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_threadsafe.py
:language: python
:pyobject: MetricType
:linenos:
```



### `AggregationType`

**Inherits from:** `Enum`

Aggregation type enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_threadsafe.py
:language: python
:pyobject: AggregationType
:linenos:
```



### `MetricValue`

Individual metric value with metadata.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_threadsafe.py
:language: python
:pyobject: MetricValue
:linenos:
```



### `ThreadSafeMetric`

Thread-safe metric container with bounded memory usage.

Fixes applied:
- All value updates protected by RLock
- Atomic statistics operations
- Bounded collection with automatic cleanup
- Thread-safe aggregation operations

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_threadsafe.py
:language: python
:pyobject: ThreadSafeMetric
:linenos:
```

#### Methods (9)

##### `__init__(self, name, metric_type, max_values, retention_window)`

Initialize thread-safe metric.

[View full source →](#method-threadsafemetric-__init__)

##### `add_value(self, value, tags, metadata)`

Add new value to metric with thread safety.

[View full source →](#method-threadsafemetric-add_value)

##### `get_current_value(self)`

Get current metric value safely.

[View full source →](#method-threadsafemetric-get_current_value)

##### `get_aggregated_value(self, aggregation, window_seconds, percentile)`

Get aggregated value over specified window with thread safety.

[View full source →](#method-threadsafemetric-get_aggregated_value)

##### `get_statistics(self)`

Get metric statistics safely.

[View full source →](#method-threadsafemetric-get_statistics)

##### `clean_old_values(self)`

Clean values older than retention window.

[View full source →](#method-threadsafemetric-clean_old_values)

##### `reset(self)`

Reset metric to initial state.

[View full source →](#method-threadsafemetric-reset)

##### `_maybe_cleanup(self)`

Perform cleanup if interval has passed.

[View full source →](#method-threadsafemetric-_maybe_cleanup)

##### `_estimate_memory_usage(self)`

Estimate memory usage of stored values.

[View full source →](#method-threadsafemetric-_estimate_memory_usage)



### `ThreadSafeMetricsCollector`

Thread-safe metrics collection system.

Production safety features:
- All operations protected by locks
- Bounded memory usage with automatic cleanup
- Thread-safe metric registration/removal
- Concurrent collection support
- Memory monitoring and alerts

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_threadsafe.py
:language: python
:pyobject: ThreadSafeMetricsCollector
:linenos:
```

#### Methods (14)

##### `__init__(self, max_metrics, cleanup_interval)`

Initialize thread-safe metrics collector.

[View full source →](#method-threadsafemetricscollector-__init__)

##### `register_metric(self, name, metric_type, max_values, retention_window)`

Register new metric with thread safety.

[View full source →](#method-threadsafemetricscollector-register_metric)

##### `unregister_metric(self, name)`

Unregister metric safely.

[View full source →](#method-threadsafemetricscollector-unregister_metric)

##### `collect(self, metric_name, value, tags, metadata)`

Collect metric value with thread safety.

[View full source →](#method-threadsafemetricscollector-collect)

##### `get_metric_value(self, metric_name, aggregation, window_seconds)`

Get metric value safely.

[View full source →](#method-threadsafemetricscollector-get_metric_value)

##### `get_metric_statistics(self, metric_name)`

Get metric statistics safely.

[View full source →](#method-threadsafemetricscollector-get_metric_statistics)

##### `get_all_metrics(self)`

Get statistics for all metrics safely.

[View full source →](#method-threadsafemetricscollector-get_all_metrics)

##### `cleanup_old_values(self)`

Clean old values from all metrics.

[View full source →](#method-threadsafemetricscollector-cleanup_old_values)

##### `get_system_statistics(self)`

Get system-wide statistics.

[View full source →](#method-threadsafemetricscollector-get_system_statistics)

##### `reset_all_metrics(self)`

Reset all metrics to initial state.

[View full source →](#method-threadsafemetricscollector-reset_all_metrics)

##### `add_alert_callback(self, callback)`

Add alert callback safely.

[View full source →](#method-threadsafemetricscollector-add_alert_callback)

##### `remove_alert_callback(self, callback)`

Remove alert callback safely.

[View full source →](#method-threadsafemetricscollector-remove_alert_callback)

##### `_maybe_cleanup(self)`

Perform cleanup if interval has passed.

[View full source →](#method-threadsafemetricscollector-_maybe_cleanup)

##### `cleanup(self)`

Cleanup resources.

[View full source →](#method-threadsafemetricscollector-cleanup)



## Functions

### `get_global_threadsafe_collector()`

Get global thread-safe metrics collector (singleton pattern).

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_threadsafe.py
:language: python
:pyobject: get_global_threadsafe_collector
:linenos:
```



### `reset_global_threadsafe_collector()`

Reset global thread-safe collector.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_threadsafe.py
:language: python
:pyobject: reset_global_threadsafe_collector
:linenos:
```



### `collect_metric(metric_name, value, tags, metadata)`

Collect metric using global thread-safe collector.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_threadsafe.py
:language: python
:pyobject: collect_metric
:linenos:
```



### `register_metric(name, metric_type, max_values, retention_window)`

Register metric using global thread-safe collector.

#### Source Code

```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector_threadsafe.py
:language: python
:pyobject: register_metric
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
- `from concurrent.futures import ThreadPoolExecutor`
- `import weakref`
