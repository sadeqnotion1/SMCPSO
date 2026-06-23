# interfaces.monitoring.health_monitor

**Source:** `src\interfaces\monitoring\health_monitor.py`

## Module Overview Health

monitoring system for interface components

.


This module provides health checking features for monitoring the status and operational health of all
interface components including network connections, hardware
devices, and system services. ## Complete Source Code ```{literalinclude} ../../../src/interfaces/monitoring/health_monitor.py
:language: python
:linenos:
```

---

## Classes

### `HealthStatus`

**Inherits from:** `Enum` Health status enumeration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/health_monitor.py
:language: python
:pyobject: HealthStatus
:linenos:
```

---

## `CheckResult`

**Inherits from:** `Enum` Health check result enumeration.

### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/health_monitor.py

:language: python
:pyobject: CheckResult
:linenos:
```

### `HealthCheck`

Individual health check definition.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/health_monitor.py
:language: python
:pyobject: HealthCheck
:linenos:
``` #### Methods (1) ##### `__post_init__(self)` [View full source →](#method-healthcheck-__post_init__)

### `HealthCheckResult`

Result of a health check execution.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/health_monitor.py

:language: python
:pyobject: HealthCheckResult
:linenos:
``` #### Methods (2) ##### `is_healthy(self)` [View full source →](#method-healthcheckresult-is_healthy) ##### `is_critical_failure(self)` [View full source →](#method-healthcheckresult-is_critical_failure)

### `ComponentHealth`

Health status of a system component.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/health_monitor.py
:language: python
:pyobject: ComponentHealth
:linenos:
``` #### Methods (5) ##### `update_status(self, new_status)` Update component health status. [View full source →](#method-componenthealth-update_status) ##### `add_check_result(self, result, max_history)` Add health check result and maintain history. [View full source →](#method-componenthealth-add_check_result) ##### `_update_overall_status(self)` Update overall status based on recent check results. [View full source →](#method-componenthealth-_update_overall_status) ##### `get_success_rate(self, window_size)` Get success rate for recent checks. [View full source →](#method-componenthealth-get_success_rate) ##### `get_average_response_time(self, window_size)` Get average response time for recent checks. [View full source →](#method-componenthealth-get_average_response_time)

### `HealthMonitor`

Health monitor for individual components.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/health_monitor.py

:language: python
:pyobject: HealthMonitor
:linenos:
``` #### Methods (15) ##### `__init__(self, component_name)` [View full source →](#method-healthmonitor-__init__) ##### `add_health_check(self, health_check)` Add health check to monitor. [View full source →](#method-healthmonitor-add_health_check) ##### `remove_health_check(self, check_name)` Remove health check from monitor. [View full source →](#method-healthmonitor-remove_health_check) ##### `enable_check(self, check_name)` a health check. [View full source →](#method-healthmonitor-enable_check) ##### `disable_check(self, check_name)` Disable a health check. [View full source →](#method-healthmonitor-disable_check) ##### `start_monitoring(self)` Start health monitoring. [View full source →](#method-healthmonitor-start_monitoring) ##### `stop_monitoring(self)` Stop health monitoring. [View full source →](#method-healthmonitor-stop_monitoring) ##### `run_single_check(self, check_name)` Run a single health check immediately. [View full source →](#method-healthmonitor-run_single_check) ##### `run_all_checks(self)` Run all health checks immediately. [View full source →](#method-healthmonitor-run_all_checks) ##### `get_component_health(self)` Get current component health status. [View full source →](#method-healthmonitor-get_component_health) ##### `add_status_change_handler(self, handler)` Add handler for status changes. [View full source →](#method-healthmonitor-add_status_change_handler) ##### `update_component_metrics(self, metrics)` Update component metrics. [View full source →](#method-healthmonitor-update_component_metrics) ##### `_run_health_check_loop(self, health_check)` Run health check in a loop with specified interval. [View full source →](#method-healthmonitor-_run_health_check_loop) ##### `_execute_health_check(self, health_check)` Execute a single health check with retry logic. [View full source →](#method-healthmonitor-_execute_health_check) ##### `_process_check_result(self, result, health_check)` Process health check result and update component status. [View full source →](#method-healthmonitor-_process_check_result)

### `SystemHealthMonitor`

System-wide health monitor coordinating multiple component monitors.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/health_monitor.py
:language: python
:pyobject: SystemHealthMonitor
:linenos:
``` #### Methods (10) ##### `__init__(self)` [View full source →](#method-systemhealthmonitor-__init__) ##### `add_component_monitor(self, monitor)` Add component monitor to system. [View full source →](#method-systemhealthmonitor-add_component_monitor) ##### `remove_component_monitor(self, component_name)` Remove component monitor from system. [View full source →](#method-systemhealthmonitor-remove_component_monitor) ##### `start_system_monitoring(self)` Start monitoring all components. [View full source →](#method-systemhealthmonitor-start_system_monitoring) ##### `stop_system_monitoring(self)` Stop monitoring all components. [View full source →](#method-systemhealthmonitor-stop_system_monitoring) ##### `get_system_health(self)` Get health status of all components. [View full source →](#method-systemhealthmonitor-get_system_health) ##### `get_overall_system_status(self)` Get overall system health status. [View full source →](#method-systemhealthmonitor-get_overall_system_status) ##### `add_system_health_handler(self, handler)` Add handler for system health changes. [View full source →](#method-systemhealthmonitor-add_system_health_handler) ##### `run_system_health_check(self)` Run health checks for all components. [View full source →](#method-systemhealthmonitor-run_system_health_check) ##### `_on_component_status_change(self, component_health)` Handle component status change. [View full source →](#method-systemhealthmonitor-_on_component_status_change)

---

## Functions

### `create_ping_check(name, host, timeout, interval)`

Create network ping health check.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/health_monitor.py

:language: python
:pyobject: create_ping_check
:linenos:
```

### `create_port_check(name, host, port, timeout, interval)`

Create TCP port connectivity health check.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/health_monitor.py
:language: python
:pyobject: create_port_check
:linenos:
```

### `create_memory_check(name, threshold_percent, interval)`

Create memory usage health check.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/health_monitor.py

:language: python
:pyobject: create_memory_check
:linenos:
```

### `create_disk_check(name, path, threshold_percent, interval)`

Create disk usage health check.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/health_monitor.py
:language: python
:pyobject: create_disk_check
:linenos:
```

---

## Dependencies This module imports: - `import asyncio`

- `import time`
- `import threading`
- `from abc import ABC, abstractmethod`
- `from dataclasses import dataclass, field`
- `from typing import Dict, List, Optional, Callable, Any, Set`
- `from enum import Enum`
- `import logging`
