# interfaces.hardware.sensors

**Source:** `src\interfaces\hardware\sensors.py`

## Module Overview

Sensor interface framework for control systems.
This module provides standardized interfaces for various sensor types
commonly used in control systems, including analog sensors, digital sensors,
IMU sensors, and specialized measurement devices.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/hardware/sensors.py
:language: python
:linenos:
```



## Classes

### `SensorType`

**Inherits from:** `Enum`

Sensor type enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/sensors.py
:language: python
:pyobject: SensorType
:linenos:
```



### `SensorReading`

Sensor reading data structure.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/sensors.py
:language: python
:pyobject: SensorReading
:linenos:
```



### `SensorCalibration`

Sensor calibration parameters.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/sensors.py
:language: python
:pyobject: SensorCalibration
:linenos:
```



### `SensorInterface`

**Inherits from:** `DeviceDriver`, `ABC`

Abstract base class for sensor interfaces.

This class defines the standard interface for all sensor types,
providing common functionality for calibration, filtering,
and data acquisition.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/sensors.py
:language: python
:pyobject: SensorInterface
:linenos:
```

#### Methods (10)

##### `__init__(self, config)`

Initialize sensor interface.

[View full source →](#method-sensorinterface-__init__)

##### `sensor_type(self)`

Get sensor type.

[View full source →](#method-sensorinterface-sensor_type)

##### `read_channel(self, channel)`

Read from specific sensor channel.

[View full source →](#method-sensorinterface-read_channel)

##### `read_all_channels(self)`

Read from all available channels.

[View full source →](#method-sensorinterface-read_all_channels)

##### `get_reading_history(self, channel, count)`

Get historical readings for channel.

[View full source →](#method-sensorinterface-get_reading_history)

##### `calibrate_channel(self, channel, calibration)`

Calibrate specific channel.

[View full source →](#method-sensorinterface-calibrate_channel)

##### `get_statistics(self, channel, window_size)`

Get statistical analysis of channel readings.

[View full source →](#method-sensorinterface-get_statistics)

##### `_apply_calibration(self, raw_value, channel)`

Apply calibration to raw sensor value.

[View full source →](#method-sensorinterface-_apply_calibration)

##### `_apply_noise_filter(self, reading, channel)`

Apply noise filtering to sensor reading.

[View full source →](#method-sensorinterface-_apply_noise_filter)

##### `_store_reading(self, reading)`

Store reading in history.

[View full source →](#method-sensorinterface-_store_reading)



### `AnalogSensor`

**Inherits from:** `SensorInterface`

Analog sensor implementation for continuous value measurements.

Supports voltage, current, and resistance measurements with
configurable ADC resolution and reference voltages.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/sensors.py
:language: python
:pyobject: AnalogSensor
:linenos:
```

#### Methods (9)

##### `__init__(self, config)`

Initialize analog sensor.

[View full source →](#method-analogsensor-__init__)

##### `initialize(self)`

Initialize analog sensor.

[View full source →](#method-analogsensor-initialize)

##### `shutdown(self)`

Shutdown analog sensor.

[View full source →](#method-analogsensor-shutdown)

##### `read_data(self, channel)`

Read analog sensor data.

[View full source →](#method-analogsensor-read_data)

##### `write_data(self, data)`

Write data to analog sensor (for configuration).

[View full source →](#method-analogsensor-write_data)

##### `self_test(self)`

Perform analog sensor self-test.

[View full source →](#method-analogsensor-self_test)

##### `read_channel(self, channel)`

Read from specific analog channel.

[View full source →](#method-analogsensor-read_channel)

##### `_read_adc_channel(self, channel)`

Read raw ADC value from channel.

[View full source →](#method-analogsensor-_read_adc_channel)

##### `_add_analog_capabilities(self)`

Add analog sensor support.

[View full source →](#method-analogsensor-_add_analog_capabilities)



### `DigitalSensor`

**Inherits from:** `SensorInterface`

Digital sensor implementation for binary state measurements.

Supports GPIO, switch, and digital encoder inputs with
configurable pull-up/pull-down resistors and debouncing.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/sensors.py
:language: python
:pyobject: DigitalSensor
:linenos:
```

#### Methods (11)

##### `__init__(self, config)`

Initialize digital sensor.

[View full source →](#method-digitalsensor-__init__)

##### `initialize(self)`

Initialize digital sensor.

[View full source →](#method-digitalsensor-initialize)

##### `shutdown(self)`

Shutdown digital sensor.

[View full source →](#method-digitalsensor-shutdown)

##### `read_data(self, channel)`

Read digital sensor data.

[View full source →](#method-digitalsensor-read_data)

##### `write_data(self, data)`

Write data to digital sensor (for configuration).

[View full source →](#method-digitalsensor-write_data)

##### `self_test(self)`

Perform digital sensor self-test.

[View full source →](#method-digitalsensor-self_test)

##### `read_channel(self, channel)`

Read from specific digital channel.

[View full source →](#method-digitalsensor-read_channel)

##### `get_edge_events(self, channel, since)`

Get edge events (rising/falling) for digital channel.

[View full source →](#method-digitalsensor-get_edge_events)

##### `_read_gpio_channel(self, channel)`

Read raw GPIO state from channel.

[View full source →](#method-digitalsensor-_read_gpio_channel)

##### `_apply_debouncing(self, raw_state, channel)`

Apply debouncing to digital signal.

[View full source →](#method-digitalsensor-_apply_debouncing)

##### `_add_digital_capabilities(self)`

Add digital sensor support.

[View full source →](#method-digitalsensor-_add_digital_capabilities)



### `IMUSensor`

**Inherits from:** `SensorInterface`

Inertial Measurement Unit sensor implementation.

Provides accelerometer, gyroscope, and magnetometer readings
with sensor fusion and orientation calculation.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/sensors.py
:language: python
:pyobject: IMUSensor
:linenos:
```

#### Methods (14)

##### `__init__(self, config)`

Initialize IMU sensor.

[View full source →](#method-imusensor-__init__)

##### `initialize(self)`

Initialize IMU sensor.

[View full source →](#method-imusensor-initialize)

##### `shutdown(self)`

Shutdown IMU sensor.

[View full source →](#method-imusensor-shutdown)

##### `read_data(self, channel)`

Read IMU sensor data.

[View full source →](#method-imusensor-read_data)

##### `write_data(self, data)`

Write data to IMU sensor (for configuration).

[View full source →](#method-imusensor-write_data)

##### `self_test(self)`

Perform IMU sensor self-test.

[View full source →](#method-imusensor-self_test)

##### `read_channel(self, channel)`

Read from specific IMU channel.

[View full source →](#method-imusensor-read_channel)

##### `get_orientation(self)`

Get current orientation (roll, pitch, yaw).

[View full source →](#method-imusensor-get_orientation)

##### `_read_imu_data(self)`

Read all IMU sensor data.

[View full source →](#method-imusensor-_read_imu_data)

##### `_read_accelerometer(self)`

Read accelerometer data.

[View full source →](#method-imusensor-_read_accelerometer)

##### `_read_gyroscope(self)`

Read gyroscope data.

[View full source →](#method-imusensor-_read_gyroscope)

##### `_read_magnetometer(self)`

Read magnetometer data.

[View full source →](#method-imusensor-_read_magnetometer)

##### `_update_sensor_fusion(self)`

Update sensor fusion for orientation calculation.

[View full source →](#method-imusensor-_update_sensor_fusion)

##### `_add_imu_capabilities(self)`

Add IMU sensor support.

[View full source →](#method-imusensor-_add_imu_capabilities)



## Dependencies

This module imports:

- `import asyncio`
- `import time`
- `import numpy as np`
- `from abc import ABC, abstractmethod`
- `from dataclasses import dataclass, field`
- `from typing import Dict, Any, Optional, List, Tuple`
- `from enum import Enum`
- `import logging`
- `from .device_drivers import DeviceDriver, DeviceConfig, DeviceCapability, DeviceState`
