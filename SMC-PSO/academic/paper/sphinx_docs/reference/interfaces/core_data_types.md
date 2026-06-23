# interfaces.core.data_types

**Source:** `src\interfaces\core\data_types.py`

## Module Overview Core

data types for communication framework

. This module defines standardized data structures used throughout the


communication framework, providing type safety and consistent interfaces
for configuration, monitoring, and data exchange. ## Complete Source Code ```{literalinclude} ../../../src/interfaces/core/data_types.py
:language: python
:linenos:
```

---

## Classes

### `InterfaceType`

**Inherits from:** `Enum` Interface type enumeration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/core/data_types.py
:language: python
:pyobject: InterfaceType
:linenos:
```

---

## `TransportType`

**Inherits from:** `Enum` Transport layer type.

### Source Code ```

{literalinclude} ../../../src/interfaces/core/data_types.py

:language: python
:pyobject: TransportType
:linenos:
```

### `SecurityLevel`

**Inherits from:** `Enum` Security level enumeration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/core/data_types.py
:language: python
:pyobject: SecurityLevel
:linenos:
```

### `Message`

Standard message structure for all communications.

#### Source Code ```

{literalinclude} ../../../src/interfaces/core/data_types.py

:language: python
:pyobject: Message
:linenos:
``` #### Methods (5) ##### `__post_init__(self)` Initialize delivery tracking. [View full source →](#method-message-__post_init__) ##### `is_expired(self)` Check if message has expired. [View full source →](#method-message-is_expired) ##### `age(self)` Get message age in seconds. [View full source →](#method-message-age) ##### `add_header(self, key, value)` Add header to message. [View full source →](#method-message-add_header) ##### `get_header(self, key, default)` Get header value. [View full source →](#method-message-get_header)

### `ConnectionInfo`

Connection information and status.

#### Source Code ```

{literalinclude} ../../../src/interfaces/core/data_types.py
:language: python
:pyobject: ConnectionInfo
:linenos:
``` #### Methods (4) ##### `is_connected(self)` Check if connection is active. [View full source →](#method-connectioninfo-is_connected) ##### `connection_duration(self)` Get connection duration in seconds. [View full source →](#method-connectioninfo-connection_duration) ##### `idle_time(self)` Get idle time since last activity. [View full source →](#method-connectioninfo-idle_time) ##### `update_activity(self)` Update last activity timestamp. [View full source →](#method-connectioninfo-update_activity)

### `InterfaceConfig`

Configuration for communication interfaces.

#### Source Code ```

{literalinclude} ../../../src/interfaces/core/data_types.py

:language: python
:pyobject: InterfaceConfig
:linenos:
``` #### Methods (2) ##### `get_setting(self, key, default)` Get custom setting value. [View full source →](#method-interfaceconfig-get_setting) ##### `set_setting(self, key, value)` Set custom setting value. [View full source →](#method-interfaceconfig-set_setting)

### `ErrorInfo`

Error information for diagnostics.

#### Source Code ```

{literalinclude} ../../../src/interfaces/core/data_types.py
:language: python
:pyobject: ErrorInfo
:linenos:
``` #### Methods (2) ##### `age(self)` Get error age in seconds. [View full source →](#method-errorinfo-age) ##### `add_related_error(self, error_id)` Add related error ID. [View full source →](#method-errorinfo-add_related_error)

### `PerformanceMetrics`

Performance metrics for interfaces.

#### Source Code ```

{literalinclude} ../../../src/interfaces/core/data_types.py

:language: python
:pyobject: PerformanceMetrics
:linenos:
``` #### Methods (2) ##### `measurement_duration(self)` Get measurement duration in seconds. [View full source →](#method-performancemetrics-measurement_duration) ##### `update_latency(self, latency)` Update latency metrics with new sample. [View full source →](#method-performancemetrics-update_latency)

### `CommunicationStats`

communication statistics.

#### Source Code ```

{literalinclude} ../../../src/interfaces/core/data_types.py
:language: python
:pyobject: CommunicationStats
:linenos:
``` #### Methods (3) ##### `reset_counters(self)` Reset all counters. [View full source →](#method-communicationstats-reset_counters) ##### `update_timestamp(self)` Update last update timestamp. [View full source →](#method-communicationstats-update_timestamp) ##### `uptime(self)` Get uptime since last reset in seconds. [View full source →](#method-communicationstats-uptime)

### `QueueConfig`

Configuration for message queues.

#### Source Code ```

{literalinclude} ../../../src/interfaces/core/data_types.py

:language: python
:pyobject: QueueConfig
:linenos:
``` #### Methods (1) ##### `get_warning_size(self)` Get queue size that triggers warning. [View full source →](#method-queueconfig-get_warning_size)

### `DeviceInfo`

Device information structure.

#### Source Code ```

{literalinclude} ../../../src/interfaces/core/data_types.py
:language: python
:pyobject: DeviceInfo
:linenos:
``` #### Methods (3) ##### `is_online(self)` Check if device is online. [View full source →](#method-deviceinfo-is_online) ##### `time_since_seen(self)` Get time since last seen in seconds. [View full source →](#method-deviceinfo-time_since_seen) ##### `update_last_seen(self)` Update last seen timestamp. [View full source →](#method-deviceinfo-update_last_seen)

---

## Dependencies This module imports: - `from __future__ import annotations`

- `from dataclasses import dataclass, field`
- `from typing import Any, Dict, List, Optional, Union, Tuple`
- `from enum import Enum`
- `import time`
- `import uuid`
- `from datetime import datetime`
