# interfaces.monitoring.metrics_collector

**Source:** `src\interfaces\monitoring\metrics_collector.py`

## Module Overview metrics

collection system for interface monitoring

.


This module provides efficient collection, aggregation, and storage
of various metrics including performance counters, resource usage,
business metrics, and custom measurements across all interface
components. ## Complete Source Code ```{literalinclude} ../../../src/interfaces/monitoring/metrics_collector.py
:language: python
:linenos:
```

---

## Classes

### `MetricType`

**Inherits from:** `Enum` Metric type enumeration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/metrics_collector.py
:language: python
:pyobject: MetricType
:linenos:
```

---

## `AggregationType`

**Inherits from:** `Enum` Metric aggregation type.

### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/metrics_collector.py

:language: python
:pyobject: AggregationType
:linenos:
```

### `MetricValue`

Individual metric value with timestamp.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/metrics_collector.py
:language: python
:pyobject: MetricValue
:linenos:
```

### `Metric`

Metric definition and storage.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/metrics_collector.py

:language: python
:pyobject: Metric
:linenos:
``` #### Methods (7) ##### `add_value(self, value, tags, metadata)` Add new value to metric. [View full source →](#method-metric-add_value) ##### `get_current_value(self)` Get current metric value. [View full source →](#method-metric-get_current_value) ##### `get_aggregated_value(self, aggregation, window_seconds)` Get aggregated value over specified window. [View full source →](#method-metric-get_aggregated_value) ##### `get_rate(self, window_seconds)` Calculate rate of change over time window. [View full source →](#method-metric-get_rate) ##### `clean_old_values(self)` Remove values outside retention window. [View full source →](#method-metric-clean_old_values) ##### `get_histogram_buckets(self, bucket_count)` Get histogram distribution of values. [View full source →](#method-metric-get_histogram_buckets) ##### `_percentile(values, percentile)` Calculate percentile of values. [View full source →](#method-metric-_percentile)

### `MetricsCollector`

Main metrics collection and management system.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/metrics_collector.py
:language: python
:pyobject: MetricsCollector
:linenos:
``` #### Methods (19) ##### `__init__(self, retention_window)` [View full source →](#method-metricscollector-__init__) ##### `create_metric(self, name, metric_type, description, unit, tags)` Create new metric. [View full source →](#method-metricscollector-create_metric) ##### `get_metric(self, name)` Get metric by name. [View full source →](#method-metricscollector-get_metric) ##### `increment_counter(self, name, value, tags)` Increment counter metric. [View full source →](#method-metricscollector-increment_counter) ##### `set_gauge(self, name, value, tags)` Set gauge metric value. [View full source →](#method-metricscollector-set_gauge) ##### `record_histogram(self, name, value, tags)` Record histogram value. [View full source →](#method-metricscollector-record_histogram) ##### `record_timer(self, name, duration, tags)` Record timer duration. [View full source →](#method-metricscollector-record_timer) ##### `record_rate(self, name, rate, tags)` Record rate metric. [View full source →](#method-metricscollector-record_rate) ##### `get_all_metrics(self)` Get all metrics. [View full source →](#method-metricscollector-get_all_metrics) ##### `get_metrics_summary(self)` Get summary of all metrics. [View full source →](#method-metricscollector-get_metrics_summary) ##### `add_collector(self, collector)` Add metrics collector function. [View full source →](#method-metricscollector-add_collector) ##### `collect_all(self)` Run all registered collectors. [View full source →](#method-metricscollector-collect_all) ##### `export_metrics(self, format_type)` Export metrics in specified format. [View full source →](#method-metricscollector-export_metrics) ##### `reset_metric(self, name)` Reset metric values. [View full source →](#method-metricscollector-reset_metric) ##### `delete_metric(self, name)` Delete metric. [View full source →](#method-metricscollector-delete_metric) ##### `_get_or_create_metric(self, name, metric_type)` Get existing metric or create new one. [View full source →](#method-metricscollector-_get_or_create_metric) ##### `_record_metric_value(self, name, metric_type, value, tags)` Record metric value with appropriate method. [View full source →](#method-metricscollector-_record_metric_value) ##### `_cleanup_if_needed(self)` Clean up old metric values if needed. [View full source →](#method-metricscollector-_cleanup_if_needed) ##### `_export_prometheus_format(self)` Export metrics in Prometheus format. [View full source →](#method-metricscollector-_export_prometheus_format)

### `SystemMetricsCollector`

System-level metrics collector for system resources.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/metrics_collector.py

:language: python
:pyobject: SystemMetricsCollector
:linenos:
``` #### Methods (5) ##### `__init__(self, collector)` [View full source →](#method-systemmetricscollector-__init__) ##### `start_collection(self)` Start automatic system metrics collection. [View full source →](#method-systemmetricscollector-start_collection) ##### `stop_collection(self)` Stop automatic system metrics collection. [View full source →](#method-systemmetricscollector-stop_collection) ##### `collect_system_metrics(self)` Collect current system metrics. [View full source →](#method-systemmetricscollector-collect_system_metrics) ##### `_collection_loop(self)` Main collection loop. [View full source →](#method-systemmetricscollector-_collection_loop)

### `TimerContext`

Context manager for timing operations.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/metrics_collector.py
:language: python
:pyobject: TimerContext
:linenos:
``` #### Methods (3) ##### `__init__(self, collector, metric_name, tags)` [View full source →](#method-timercontext-__init__) ##### `__enter__(self)` [View full source →](#method-timercontext-__enter__) ##### `__exit__(self, exc_type, exc_val, exc_tb)` [View full source →](#method-timercontext-__exit__)

---

## Functions

### `create_metric(name, metric_type, description, unit, tags)`

Create a metric instance.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/metrics_collector.py

:language: python
:pyobject: create_metric
:linenos:
```

### `timer(collector, metric_name, tags)`

Create timer context manager.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/metrics_collector.py
:language: python
:pyobject: timer
:linenos:
```

### `timed_function(collector, metric_name, tags)`

Decorator to time function execution.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/metrics_collector.py

:language: python
:pyobject: timed_function
:linenos:
```

---

## Dependencies This module imports: - `import time`
- `import threading`
- `import statistics`
- `from abc import ABC, abstractmethod`
- `from dataclasses import dataclass, field`
- `from typing import Dict, List, Optional, Any, Union, Callable, Iterator`
- `from enum import Enum`
- `from collections import defaultdict, deque`
- `import logging`
