# interfaces.hardware.serial_devices

**Source:** `src\interfaces\hardware\serial_devices.py`

## Module Overview

*No module docstring available.*

## Complete Source Code

```{literalinclude} ../../../src/interfaces/hardware/serial_devices.py
:language: python
:linenos:
```



## Classes

### `SerialProtocol`

**Inherits from:** `Enum`

Serial communication protocol enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/serial_devices.py
:language: python
:pyobject: SerialProtocol
:linenos:
```



### `DataType`

**Inherits from:** `Enum`

Data type enumeration for serial communication.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/serial_devices.py
:language: python
:pyobject: DataType
:linenos:
```



### `SerialConfig`

Serial communication configuration.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/serial_devices.py
:language: python
:pyobject: SerialConfig
:linenos:
```



### `ModbusRegister`

Modbus register configuration.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/serial_devices.py
:language: python
:pyobject: ModbusRegister
:linenos:
```



### `CANMessage`

CAN message structure.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/serial_devices.py
:language: python
:pyobject: CANMessage
:linenos:
```



### `SerialDevice`

**Inherits from:** `DeviceDriver`, `ABC`

Abstract base class for serial communication devices.

This class provides common functionality for serial communication
including connection management, message framing, and error handling.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/serial_devices.py
:language: python
:pyobject: SerialDevice
:linenos:
```

#### Methods (8)

##### `__init__(self, config)`

Initialize serial device.

[View full source →](#method-serialdevice-__init__)

##### `is_connected(self)`

Check if serial device is connected.

[View full source →](#method-serialdevice-is_connected)

##### `send_message(self, data)`

Send message over serial interface.

[View full source →](#method-serialdevice-send_message)

##### `receive_message(self, timeout)`

Receive message from serial interface.

[View full source →](#method-serialdevice-receive_message)

##### `connect_serial(self)`

Connect to serial device.

[View full source →](#method-serialdevice-connect_serial)

##### `disconnect_serial(self)`

Disconnect from serial device.

[View full source →](#method-serialdevice-disconnect_serial)

##### `add_message_handler(self, handler)`

Add message handler for received data.

[View full source →](#method-serialdevice-add_message_handler)

##### `_receive_loop(self)`

Continuous receive loop.

[View full source →](#method-serialdevice-_receive_loop)



### `ModbusDevice`

**Inherits from:** `SerialDevice`

Modbus RTU/TCP device implementation.

Provides Modbus communication for reading and writing
holding registers, input registers, coils, and discrete inputs.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/serial_devices.py
:language: python
:pyobject: ModbusDevice
:linenos:
```

#### Methods (13)

##### `__init__(self, config)`

Initialize Modbus device.

[View full source →](#method-modbusdevice-__init__)

##### `initialize(self)`

Initialize Modbus device.

[View full source →](#method-modbusdevice-initialize)

##### `shutdown(self)`

Shutdown Modbus device.

[View full source →](#method-modbusdevice-shutdown)

##### `read_data(self, channel)`

Read data from Modbus device.

[View full source →](#method-modbusdevice-read_data)

##### `write_data(self, data)`

Write data to Modbus device.

[View full source →](#method-modbusdevice-write_data)

##### `self_test(self)`

Perform Modbus device self-test.

[View full source →](#method-modbusdevice-self_test)

##### `send_message(self, data)`

Send raw Modbus message.

[View full source →](#method-modbusdevice-send_message)

##### `receive_message(self, timeout)`

Receive raw Modbus message.

[View full source →](#method-modbusdevice-receive_message)

##### `add_register(self, register)`

Add Modbus register configuration.

[View full source →](#method-modbusdevice-add_register)

##### `read_register(self, register_name)`

Read value from Modbus register.

[View full source →](#method-modbusdevice-read_register)

##### `write_register(self, register_name, value)`

Write value to Modbus register.

[View full source →](#method-modbusdevice-write_register)

##### `_decode_value(self, decoder, data_type, scaling, offset)`

Decode value from Modbus registers.

[View full source →](#method-modbusdevice-_decode_value)

##### `_encode_value(self, builder, data_type, value)`

Encode value to Modbus registers.

[View full source →](#method-modbusdevice-_encode_value)



### `CANDevice`

**Inherits from:** `SerialDevice`

CAN bus device implementation.

Provides CAN bus communication for sending and receiving
CAN messages with configurable filters and arbitration IDs.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/serial_devices.py
:language: python
:pyobject: CANDevice
:linenos:
```

#### Methods (11)

##### `__init__(self, config)`

Initialize CAN device.

[View full source →](#method-candevice-__init__)

##### `initialize(self)`

Initialize CAN device.

[View full source →](#method-candevice-initialize)

##### `shutdown(self)`

Shutdown CAN device.

[View full source →](#method-candevice-shutdown)

##### `read_data(self, channel)`

Read data from CAN device.

[View full source →](#method-candevice-read_data)

##### `write_data(self, data)`

Write data to CAN device.

[View full source →](#method-candevice-write_data)

##### `self_test(self)`

Perform CAN device self-test.

[View full source →](#method-candevice-self_test)

##### `send_message(self, data)`

Send raw CAN message.

[View full source →](#method-candevice-send_message)

##### `receive_message(self, timeout)`

Receive raw CAN message.

[View full source →](#method-candevice-receive_message)

##### `send_can_message(self, arbitration_id, data, is_extended)`

Send CAN message with specific arbitration ID.

[View full source →](#method-candevice-send_can_message)

##### `add_message_filter(self, arbitration_id, mask)`

Add CAN message filter.

[View full source →](#method-candevice-add_message_filter)

##### `_can_message_handler(self, message)`

Handle received CAN messages.

[View full source →](#method-candevice-_can_message_handler)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import asyncio`
- `import serial`
- `import struct`
- `import time`
- `from abc import ABC, abstractmethod`
- `from dataclasses import dataclass, field`
- `from typing import Dict, Any, Optional, List, Tuple, Union`
- `from enum import Enum`
- `import logging`

*... and 1 more*
