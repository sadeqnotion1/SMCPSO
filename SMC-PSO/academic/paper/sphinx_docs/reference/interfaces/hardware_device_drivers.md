# interfaces.hardware.device_drivers

**Source:** `src\interfaces\hardware\device_drivers.py`

## Module Overview

Base device driver framework for hardware abstraction.
This module provides the foundational classes and interfaces for implementing
device drivers in control systems, including device lifecycle management,
error handling, and standardized communication patterns.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/hardware/device_drivers.py
:language: python
:linenos:
```



## Classes

### `DeviceState`

**Inherits from:** `Enum`

Device operational state enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/device_drivers.py
:language: python
:pyobject: DeviceState
:linenos:
```



### `DeviceError`

**Inherits from:** `Exception`

Base exception for device-related errors.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/device_drivers.py
:language: python
:pyobject: DeviceError
:linenos:
```

#### Methods (1)

##### `__init__(self, message, device_id, error_code)`

[View full source →](#method-deviceerror-__init__)



### `DeviceCapability`

Device capability description.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/device_drivers.py
:language: python
:pyobject: DeviceCapability
:linenos:
```



### `DeviceConfig`

Device configuration structure.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/device_drivers.py
:language: python
:pyobject: DeviceConfig
:linenos:
```



### `DeviceStatus`

Device status information.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/device_drivers.py
:language: python
:pyobject: DeviceStatus
:linenos:
```

#### Methods (3)

##### `update_timestamp(self)`

Update the last update timestamp.

[View full source →](#method-devicestatus-update_timestamp)

##### `add_metric(self, name, value)`

Add a performance metric.

[View full source →](#method-devicestatus-add_metric)

##### `add_alert(self, message)`

Add an alert message.

[View full source →](#method-devicestatus-add_alert)



### `DeviceDriver`

**Inherits from:** `ABC`

Abstract base class for all device drivers.

This class defines the standard interface that all device drivers
must implement, providing consistent patterns for device lifecycle
management, communication, and error handling.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/device_drivers.py
:language: python
:pyobject: DeviceDriver
:linenos:
```

#### Methods (26)

##### `__init__(self, config)`

Initialize device driver with configuration.

[View full source →](#method-devicedriver-__init__)

##### `device_id(self)`

Get device identifier.

[View full source →](#method-devicedriver-device_id)

##### `device_type(self)`

Get device type.

[View full source →](#method-devicedriver-device_type)

##### `state(self)`

Get current device state.

[View full source →](#method-devicedriver-state)

##### `status(self)`

Get device status.

[View full source →](#method-devicedriver-status)

##### `features(self)`

Get device .
[View full source →](#method-devicedriver-features)

##### `config(self)`

Get device configuration.

[View full source →](#method-devicedriver-config)

##### `initialize(self)`

Initialize the device.

[View full source →](#method-devicedriver-initialize)

##### `shutdown(self)`

Shutdown the device gracefully.

[View full source →](#method-devicedriver-shutdown)

##### `read_data(self, channel)`

Read data from the device.

[View full source →](#method-devicedriver-read_data)

##### `write_data(self, data)`

Write data to the device.

[View full source →](#method-devicedriver-write_data)

##### `self_test(self)`

Perform device self-test.

[View full source →](#method-devicedriver-self_test)

##### `start(self)`

Start device operation.

[View full source →](#method-devicedriver-start)

##### `stop(self)`

Stop device operation.

[View full source →](#method-devicedriver-stop)

##### `restart(self)`

Restart device operation.

[View full source →](#method-devicedriver-restart)

##### `calibrate(self, calibration_data)`

Calibrate the device.

[View full source →](#method-devicedriver-calibrate)

##### `reset(self)`

Reset device to default state.

[View full source →](#method-devicedriver-reset)

##### `add_capability(self, capability)`

Add device capability.

[View full source →](#method-devicedriver-add_capability)

##### `get_capability(self, name)`

Get specific capability by name.

[View full source →](#method-devicedriver-get_capability)

##### `add_error_handler(self, handler)`

Add error handler callback.

[View full source →](#method-devicedriver-add_error_handler)

##### `add_status_callback(self, callback)`

Add status change callback.

[View full source →](#method-devicedriver-add_status_callback)

##### `_update_loop(self)`

Continuous update loop for device monitoring.

[View full source →](#method-devicedriver-_update_loop)

##### `_update_status(self)`

Update device status information.

[View full source →](#method-devicedriver-_update_status)

##### `_check_safety_limits(self)`

Check safety limits and trigger alerts if violated.

[View full source →](#method-devicedriver-_check_safety_limits)

##### `_handle_error(self, error)`

Handle device errors.

[View full source →](#method-devicedriver-_handle_error)

##### `_notify_status_change(self)`

Notify status change callbacks.

[View full source →](#method-devicedriver-_notify_status_change)



### `BaseDevice`

**Inherits from:** `DeviceDriver`

Base implementation of DeviceDriver with common functionality.

This class provides default implementations for common device operations
and can be used as a starting point for simple device drivers.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/device_drivers.py
:language: python
:pyobject: BaseDevice
:linenos:
```

#### Methods (7)

##### `__init__(self, config)`

Initialize base device.

[View full source →](#method-basedevice-__init__)

##### `initialize(self)`

Initialize base device.

[View full source →](#method-basedevice-initialize)

##### `shutdown(self)`

Shutdown base device.

[View full source →](#method-basedevice-shutdown)

##### `read_data(self, channel)`

Read data from base device.

[View full source →](#method-basedevice-read_data)

##### `write_data(self, data)`

Write data to base device.

[View full source →](#method-basedevice-write_data)

##### `self_test(self)`

Perform base device self-test.

[View full source →](#method-basedevice-self_test)

##### `_update_data_cache(self)`

Update internal data cache.

[View full source →](#method-basedevice-_update_data_cache)



### `DeviceManager`

Manager for multiple device drivers.

This class provides centralized management of multiple devices,
including lifecycle coordination, status monitoring, and
coordinated operations.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/device_drivers.py
:language: python
:pyobject: DeviceManager
:linenos:
```

#### Methods (11)

##### `__init__(self)`

Initialize device manager.

[View full source →](#method-devicemanager-__init__)

##### `add_device(self, device)`

Add device to manager.

[View full source →](#method-devicemanager-add_device)

##### `remove_device(self, device_id)`

Remove device from manager.

[View full source →](#method-devicemanager-remove_device)

##### `get_device(self, device_id)`

Get device by ID.

[View full source →](#method-devicemanager-get_device)

##### `list_devices(self)`

List all device IDs.

[View full source →](#method-devicemanager-list_devices)

##### `get_devices_by_type(self, device_type)`

Get all devices of specific type.

[View full source →](#method-devicemanager-get_devices_by_type)

##### `start_all(self)`

Start all devices.

[View full source →](#method-devicemanager-start_all)

##### `stop_all(self)`

Stop all devices.

[View full source →](#method-devicemanager-stop_all)

##### `restart_all(self)`

Restart all devices.

[View full source →](#method-devicemanager-restart_all)

##### `get_status_summary(self)`

Get status summary for all devices.

[View full source →](#method-devicemanager-get_status_summary)

##### `health_check_all(self)`

Perform health check on all devices.

[View full source →](#method-devicemanager-health_check_all)



## Dependencies

This module imports:

- `import asyncio`
- `import time`
- `from abc import ABC, abstractmethod`
- `from dataclasses import dataclass, field`
- `from typing import Dict, Any, Optional, List, Callable, Union`
- `from enum import Enum`
- `import logging`
- `from ..core.data_types import DeviceInfo, InterfaceType`
