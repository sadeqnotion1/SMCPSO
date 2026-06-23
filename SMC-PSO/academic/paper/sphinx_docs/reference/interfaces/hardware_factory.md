# interfaces.hardware.factory

**Source:** `src\interfaces\hardware\factory.py`

## Module Overview

Hardware interface factory for creating device drivers.
This module provides factory methods and utilities for creating and
configuring various types of hardware interfaces for control systems,
including sensors, actuators, DAQ systems, and communication devices.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/hardware/factory.py
:language: python
:linenos:
```



## Classes

### `HardwareInterfaceFactory`

Factory for creating hardware device interfaces.

This factory provides centralized creation and configuration of
various hardware interface types with consistent configuration
patterns and error handling.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/factory.py
:language: python
:pyobject: HardwareInterfaceFactory
:linenos:
```

#### Methods (12)

##### `create_device(cls, device_type, device_id, config_overrides)`

Create hardware device of specified type.

[View full source →](#method-hardwareinterfacefactory-create_device)

##### `create_sensor(cls, sensor_type, device_id)`

Create sensor with simplified configuration.

[View full source →](#method-hardwareinterfacefactory-create_sensor)

##### `create_actuator(cls, actuator_type, device_id)`

Create actuator with simplified configuration.

[View full source →](#method-hardwareinterfacefactory-create_actuator)

##### `create_daq_system(cls, daq_type, device_id, channels)`

Create DAQ system with channel configuration.

[View full source →](#method-hardwareinterfacefactory-create_daq_system)

##### `create_modbus_device(cls, device_id, port, baudrate, registers)`

Create Modbus device with register configuration.

[View full source →](#method-hardwareinterfacefactory-create_modbus_device)

##### `create_can_device(cls, device_id, channel, bitrate, interface)`

Create CAN device with simplified configuration.

[View full source →](#method-hardwareinterfacefactory-create_can_device)

##### `create_device_manager(cls, devices)`

Create device manager with optional initial devices.

[View full source →](#method-hardwareinterfacefactory-create_device_manager)

##### `create_control_system(cls, sensors, actuators, daq_config)`

Create complete control system with sensors, actuators, and DAQ.

[View full source →](#method-hardwareinterfacefactory-create_control_system)

##### `register_device_type(cls, name, device_class, default_config)`

Register new device type with factory.

[View full source →](#method-hardwareinterfacefactory-register_device_type)

##### `get_available_types(cls)`

Get list of available device types.

[View full source →](#method-hardwareinterfacefactory-get_available_types)

##### `get_default_config(cls, device_type)`

Get default configuration for device type.

[View full source →](#method-hardwareinterfacefactory-get_default_config)

##### `_build_device_config(cls, device_type, device_id, config_overrides)`

Build device configuration from type and overrides.

[View full source →](#method-hardwareinterfacefactory-_build_device_config)



## Functions

### `create_sensor_array(sensor_type, count, base_id)`

Create array of sensors of the same type.

Parameters
----------
sensor_type : str
    Type of sensor
count : int
    Number of sensors to create
base_id : str
    Base identifier for sensors
**kwargs
    Configuration for all sensors

Returns
-------
List[SensorInterface]
    List of created sensors

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/factory.py
:language: python
:pyobject: create_sensor_array
:linenos:
```



### `create_actuator_array(actuator_type, count, base_id)`

Create array of actuators of the same type.

Parameters
----------
actuator_type : str
    Type of actuator
count : int
    Number of actuators to create
base_id : str
    Base identifier for actuators
**kwargs
    Configuration for all actuators

Returns
-------
List[ActuatorInterface]
    List of created actuators

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/factory.py
:language: python
:pyobject: create_actuator_array
:linenos:
```



### `create_multi_axis_system(axes, sensors_per_axis, actuators_per_axis)`

Create multi-axis control system.

Parameters
----------
axes : List[Dict[str, Any]]
    Axis configurations
sensors_per_axis : int
    Number of sensors per axis
actuators_per_axis : int
    Number of actuators per axis

Returns
-------
Dict[str, List[DeviceDriver]]
    Dictionary of axis devices

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/factory.py
:language: python
:pyobject: create_multi_axis_system
:linenos:
```



### `create_distributed_io_system(modbus_devices, can_devices)`

Create distributed I/O system with Modbus and CAN devices.

Parameters
----------
modbus_devices : List[Dict[str, Any]]
    Modbus device configurations
can_devices : List[Dict[str, Any]], optional
    CAN device configurations

Returns
-------
Dict[str, DeviceDriver]
    Dictionary of communication devices

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/factory.py
:language: python
:pyobject: create_distributed_io_system
:linenos:
```



## Dependencies

This module imports:

- `from typing import Dict, Any, Type, Optional, Union, List`
- `import logging`
- `from .device_drivers import DeviceDriver, DeviceConfig, DeviceManager`
- `from .sensors import SensorInterface, AnalogSensor, DigitalSensor, IMUSensor, SensorType`
- `from .actuators import ActuatorInterface, ServoActuator, StepperMotor, PneumaticActuator, ActuatorType`
- `from .daq_systems import DAQInterface, NIDAQInterface, AdcInterface, ChannelConfig, ChannelType`
- `from .serial_devices import SerialDevice, ModbusDevice, CANDevice, SerialProtocol, ModbusRegister, DataType`
