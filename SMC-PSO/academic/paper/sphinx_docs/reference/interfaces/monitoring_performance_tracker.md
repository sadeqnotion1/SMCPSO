# interfaces.monitoring.performance_tracker

**Source:** `src\interfaces\monitoring\performance_tracker.py`

## Module Overview Performance-optimized

serialization with monitoring and metrics

.


This module provides high-performance serialization features with performance monitoring, metrics collection,
and adaptive optimization based on runtime characteristics. ## Complete Source Code ```{literalinclude} ../../../src/interfaces/monitoring/performance_tracker.py
:language: python
:linenos:
```

---

## Classes

### `MetricType`

**Inherits from:** `Enum` Performance metric types.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/performance_tracker.py
:language: python
:pyobject: MetricType
:linenos:
```

---

## `PerformanceMetric`

Individual performance metric measurement.

### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/performance_tracker.py

:language: python
:pyobject: PerformanceMetric
:linenos:
```

### `SerializationMetrics`

serialization performance metrics.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/performance_tracker.py
:language: python
:pyobject: SerializationMetrics
:linenos:
``` #### Methods (2) ##### `update_statistics(self)` Update computed statistics from raw data. [View full source →](#method-serializationmetrics-update_statistics) ##### `get_summary(self)` Get metrics summary. [View full source →](#method-serializationmetrics-get_summary)

### `PerformanceMonitor`

Real-time performance monitoring for serialization operations.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/performance_tracker.py

:language: python
:pyobject: PerformanceMonitor
:linenos:
``` #### Methods (9) ##### `__init__(self, window_size, enable_detailed_logging)` [View full source →](#method-performancemonitor-__init__) ##### `record_operation(self, serializer_id, operation_type, duration, data_size, success, error_type)` Record a serialization operation. [View full source →](#method-performancemonitor-record_operation) ##### `get_metrics(self, serializer_id)` Get metrics for a specific serializer or all serializers. [View full source →](#method-performancemonitor-get_metrics) ##### `get_summary(self, serializer_id)` Get performance summary. [View full source →](#method-performancemonitor-get_summary) ##### `reset_metrics(self, serializer_id)` Reset metrics for specific serializer or all serializers. [View full source →](#method-performancemonitor-reset_metrics) ##### `set_performance_threshold(self, metric_name, threshold)` Set performance threshold for alerting. [View full source →](#method-performancemonitor-set_performance_threshold) ##### `add_alert_handler(self, handler)` Add performance alert handler. [View full source →](#method-performancemonitor-add_alert_handler) ##### `_check_performance_alerts(self, serializer_id, metrics)` Check for performance threshold violations. [View full source →](#method-performancemonitor-_check_performance_alerts) ##### `get_recent_metrics(self, serializer_id, count)` Get recent metrics for a serializer. [View full source →](#method-performancemonitor-get_recent_metrics)

### `PerformanceSerializer`

**Inherits from:** `SerializerInterface` Performance-aware serializer wrapper with monitoring and adaptive optimization.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/performance_tracker.py
:language: python
:pyobject: PerformanceSerializer
:linenos:
``` #### Methods (11) ##### `__init__(self, base_serializer, monitor, enable_adaptive_optimization)` [View full source →](#method-performanceserializer-__init__) ##### `format_type(self)` [View full source →](#method-performanceserializer-format_type) ##### `content_type(self)` [View full source →](#method-performanceserializer-content_type) ##### `serialize(self, data)` Serialize data with performance monitoring. [View full source →](#method-performanceserializer-serialize) ##### `deserialize(self, data, target_type)` Deserialize data with performance monitoring. [View full source →](#method-performanceserializer-deserialize) ##### `get_performance_metrics(self)` Get performance metrics for this serializer. [View full source →](#method-performanceserializer-get_performance_metrics) ##### `get_performance_summary(self)` Get performance summary for this serializer. [View full source →](#method-performanceserializer-get_performance_summary) ##### `reset_performance_metrics(self)` Reset performance metrics for this serializer. [View full source →](#method-performanceserializer-reset_performance_metrics) ##### `set_performance_threshold(self, metric_name, threshold)` Set performance threshold for this serializer. [View full source →](#method-performanceserializer-set_performance_threshold) ##### `_check_adaptive_optimization(self)` Check if adaptive optimization should be triggered. [View full source →](#method-performanceserializer-_check_adaptive_optimization) ##### `_suggest_optimizations(self, metrics)` Suggest performance optimizations. [View full source →](#method-performanceserializer-_suggest_optimizations)

### `BatchSerializer`

High-performance batch serialization for multiple data items.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/performance_tracker.py

:language: python
:pyobject: BatchSerializer
:linenos:
``` #### Methods (4) ##### `__init__(self, base_serializer, batch_size, monitor)` [View full source →](#method-batchserializer-__init__) ##### `add_to_batch(self, data)` Add data to batch and return serialized batch if full. [View full source →](#method-batchserializer-add_to_batch) ##### `flush_batch(self)` Serialize and return all items in current batch. [View full source →](#method-batchserializer-flush_batch) ##### `get_batch_metrics(self)` Get batch processing metrics. [View full source →](#method-batchserializer-get_batch_metrics)

---

## Functions

### `get_global_monitor()`

Get global performance monitor instance.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/performance_tracker.py
:language: python
:pyobject: get_global_monitor
:linenos:
```

### `create_performance_serializer(base_serializer, monitor)`

Create performance-aware serializer wrapper.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/performance_tracker.py

:language: python
:pyobject: create_performance_serializer
:linenos:
```

### `get_performance_summary()`

Get performance summary for all monitored serializers.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/performance_tracker.py
:language: python
:pyobject: get_performance_summary
:linenos:
```

---

## Dependencies This module imports: - `import time`

- `import threading`
- `from dataclasses import dataclass, field`
- `from typing import Dict, Any, List, Optional, Union, Callable`
- `from enum import Enum`
- `import logging`
- `import statistics`
- `from collections import deque, defaultdict`
- `from src.interfaces.data_exchange.serializers import SerializerInterface, SerializationFormat`
- `from src.interfaces.data_exchange.data_types import SerializableData`
