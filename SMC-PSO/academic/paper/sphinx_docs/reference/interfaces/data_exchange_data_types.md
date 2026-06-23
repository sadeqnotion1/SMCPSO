# interfaces.data_exchange.data_types

**Source:** `src\interfaces\data_exchange\data_types.py`

## Module Overview

Core data types for the data exchange framework.
This module defines fundamental data structures used throughout the
serialization and communication system, including messages, packets,
headers, and metadata structures.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:linenos:
```



## Classes

### `MessageType`

**Inherits from:** `Enum`

Message type enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:pyobject: MessageType
:linenos:
```



### `Priority`

**Inherits from:** `Enum`

Message priority levels.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:pyobject: Priority
:linenos:
```



### `CompressionType`

**Inherits from:** `Enum`

Compression algorithm types.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:pyobject: CompressionType
:linenos:
```



### `EncodingType`

**Inherits from:** `Enum`

Data encoding types.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:pyobject: EncodingType
:linenos:
```



### `MessageHeader`

Message header with metadata.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:pyobject: MessageHeader
:linenos:
```



### `MessageMetadata`

Extended message metadata.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:pyobject: MessageMetadata
:linenos:
```



### `SerializableData`

Base class for serializable data structures.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:pyobject: SerializableData
:linenos:
```

#### Methods (5)

##### `validate(self)`

Validate data structure.

[View full source →](#method-serializabledata-validate)

##### `to_dict(self)`

Convert to dictionary representation.

[View full source →](#method-serializabledata-to_dict)

##### `from_dict(cls, data)`

Create from dictionary representation.

[View full source →](#method-serializabledata-from_dict)

##### `_serialize_data(data)`

Serialize data for JSON compatibility.

[View full source →](#method-serializabledata-_serialize_data)

##### `_deserialize_data(data)`

Deserialize data from JSON representation.

[View full source →](#method-serializabledata-_deserialize_data)



### `DataMessage`

**Inherits from:** `Generic[T]`

Typed data message structure.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:pyobject: DataMessage
:linenos:
```

#### Methods (7)

##### `validate(self)`

Validate message structure.

[View full source →](#method-datamessage-validate)

##### `is_expired(self)`

Check if message has expired based on TTL.

[View full source →](#method-datamessage-is_expired)

##### `get_age(self)`

Get message age in seconds.

[View full source →](#method-datamessage-get_age)

##### `to_dict(self)`

Convert message to dictionary.

[View full source →](#method-datamessage-to_dict)

##### `from_dict(cls, data)`

Create message from dictionary.

[View full source →](#method-datamessage-from_dict)

##### `_serialize_payload(payload)`

Serialize payload for transmission.

[View full source →](#method-datamessage-_serialize_payload)

##### `_deserialize_payload(payload_data)`

Deserialize payload from transmission format.

[View full source →](#method-datamessage-_deserialize_payload)



### `DataPacket`

Low-level data packet for binary transmission.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:pyobject: DataPacket
:linenos:
```

#### Methods (4)

##### `pack(self)`

Pack packet into binary format.

[View full source →](#method-datapacket-pack)

##### `unpack(cls, data)`

Unpack packet from binary format.

[View full source →](#method-datapacket-unpack)

##### `_calculate_checksum(self)`

Calculate simple checksum for packet integrity.

[View full source →](#method-datapacket-_calculate_checksum)

##### `is_valid(self)`

Check if packet is valid.

[View full source →](#method-datapacket-is_valid)



### `ControlMessage`

**Inherits from:** `SerializableData`

Control message for system commands.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:pyobject: ControlMessage
:linenos:
```

#### Methods (1)

##### `__post_init__(self)`

[View full source →](#method-controlmessage-__post_init__)



### `StatusMessage`

**Inherits from:** `SerializableData`

Status message for system state reporting.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:pyobject: StatusMessage
:linenos:
```

#### Methods (2)

##### `__post_init__(self)`

[View full source →](#method-statusmessage-__post_init__)

##### `is_error(self)`

Check if this is an error status.

[View full source →](#method-statusmessage-is_error)



### `TelemetryMessage`

**Inherits from:** `SerializableData`

Telemetry message for sensor data and measurements.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:pyobject: TelemetryMessage
:linenos:
```

#### Methods (2)

##### `__post_init__(self)`

[View full source →](#method-telemetrymessage-__post_init__)

##### `add_measurement(self, name, value, unit, quality)`

Add a measurement to the telemetry.

[View full source →](#method-telemetrymessage-add_measurement)



### `ConfigurationMessage`

**Inherits from:** `SerializableData`

Configuration message for system settings.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/data_types.py
:language: python
:pyobject: ConfigurationMessage
:linenos:
```

#### Methods (1)

##### `__post_init__(self)`

[View full source →](#method-configurationmessage-__post_init__)



## Dependencies

This module imports:

- `import time`
- `import uuid`
- `from dataclasses import dataclass, field`
- `from typing import Any, Dict, Optional, List, Union, TypeVar, Generic`
- `from enum import Enum`
- `import numpy as np`
