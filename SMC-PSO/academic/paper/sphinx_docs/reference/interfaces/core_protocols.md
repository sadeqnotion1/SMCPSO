# interfaces.core.protocols

**Source:** `src\interfaces\core\protocols.py`

## Module Overview

Core protocols and interfaces for communication systems.

This module defines the fundamental protocols that all communication interfaces
must implement, providing consistent abstractions for messaging, connections,
serialization, and error handling in control systems.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/core/protocols.py
:language: python
:linenos:
```



## Classes

### `ConnectionState`

**Inherits from:** `Enum`

Connection state enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/core/protocols.py
:language: python
:pyobject: ConnectionState
:linenos:
```



### `MessageType`

**Inherits from:** `Enum`

Message type enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/core/protocols.py
:language: python
:pyobject: MessageType
:linenos:
```



### `Priority`

**Inherits from:** `Enum`

Message priority levels.

#### Source Code

```{literalinclude} ../../../src/interfaces/core/protocols.py
:language: python
:pyobject: Priority
:linenos:
```



### `MessageMetadata`

Message metadata for tracking and routing.

#### Source Code

```{literalinclude} ../../../src/interfaces/core/protocols.py
:language: python
:pyobject: MessageMetadata
:linenos:
```



### `CommunicationProtocol`

**Inherits from:** `ABC`

Abstract base protocol for all communication interfaces.

This protocol defines the core interface that all communication
systems must implement, providing consistency across different
transport mechanisms.

#### Source Code

```{literalinclude} ../../../src/interfaces/core/protocols.py
:language: python
:pyobject: CommunicationProtocol
:linenos:
```

#### Methods (6)

##### `connect(self, config)`

Establish connection with the remote endpoint.

[View full source →](#method-communicationprotocol-connect)

##### `disconnect(self)`

Close connection gracefully.

[View full source →](#method-communicationprotocol-disconnect)

##### `send(self, data, metadata)`

Send data to the remote endpoint.

[View full source →](#method-communicationprotocol-send)

##### `receive(self, timeout)`

Receive data from the remote endpoint.

[View full source →](#method-communicationprotocol-receive)

##### `get_connection_state(self)`

Get current connection state.

[View full source →](#method-communicationprotocol-get_connection_state)

##### `get_statistics(self)`

Get communication statistics.

[View full source →](#method-communicationprotocol-get_statistics)



### `MessageProtocol`

**Inherits from:** `ABC`

Protocol for message handling and routing.

Defines how messages are processed, routed, and handled
within the communication system.

#### Source Code

```{literalinclude} ../../../src/interfaces/core/protocols.py
:language: python
:pyobject: MessageProtocol
:linenos:
```

#### Methods (4)

##### `process_message(self, data, metadata)`

Process incoming message.

[View full source →](#method-messageprotocol-process_message)

##### `register_handler(self, message_type, handler)`

Register message handler for specific message type.

[View full source →](#method-messageprotocol-register_handler)

##### `unregister_handler(self, message_type)`

Unregister message handler.

[View full source →](#method-messageprotocol-unregister_handler)

##### `route_message(self, data, metadata, destination)`

Route message to specific destination.

[View full source →](#method-messageprotocol-route_message)



### `ConnectionProtocol`

**Inherits from:** `ABC`

Protocol for connection management.

Defines connection lifecycle management, including
establishment, maintenance, and cleanup.

#### Source Code

```{literalinclude} ../../../src/interfaces/core/protocols.py
:language: python
:pyobject: ConnectionProtocol
:linenos:
```

#### Methods (5)

##### `establish_connection(self, endpoint, config)`

Establish new connection.

[View full source →](#method-connectionprotocol-establish_connection)

##### `close_connection(self, connection_id)`

Close specific connection.

[View full source →](#method-connectionprotocol-close_connection)

##### `get_connection_info(self, connection_id)`

Get connection information.

[View full source →](#method-connectionprotocol-get_connection_info)

##### `list_connections(self)`

List all active connections.

[View full source →](#method-connectionprotocol-list_connections)

##### `health_check(self, connection_id)`

Check connection health.

[View full source →](#method-connectionprotocol-health_check)



### `SerializationProtocol`

**Inherits from:** `ABC`

Protocol for data serialization and deserialization.

Provides consistent interface for converting between
Python objects and wire formats.

#### Source Code

```{literalinclude} ../../../src/interfaces/core/protocols.py
:language: python
:pyobject: SerializationProtocol
:linenos:
```

#### Methods (4)

##### `serialize(self, data)`

Serialize data to bytes.

[View full source →](#method-serializationprotocol-serialize)

##### `deserialize(self, data)`

Deserialize bytes to data.

[View full source →](#method-serializationprotocol-deserialize)

##### `get_content_type(self)`

Get serialization content type.

[View full source →](#method-serializationprotocol-get_content_type)

##### `supports_streaming(self)`

Check if serializer supports streaming.

[View full source →](#method-serializationprotocol-supports_streaming)



### `ErrorHandlerProtocol`

**Inherits from:** `ABC`

Protocol for error handling and recovery.

Defines how errors are handled, logged, and recovered
from in communication systems.

#### Source Code

```{literalinclude} ../../../src/interfaces/core/protocols.py
:language: python
:pyobject: ErrorHandlerProtocol
:linenos:
```

#### Methods (4)

##### `handle_error(self, error, context)`

Handle communication error.

[View full source →](#method-errorhandlerprotocol-handle_error)

##### `should_retry(self, error, retry_count)`

Determine if operation should be retried.

[View full source →](#method-errorhandlerprotocol-should_retry)

##### `get_retry_delay(self, retry_count)`

Get delay before retry.

[View full source →](#method-errorhandlerprotocol-get_retry_delay)

##### `log_error(self, error, context)`

Log error with context.

[View full source →](#method-errorhandlerprotocol-log_error)



### `StreamingProtocol`

**Inherits from:** `ABC`

Protocol for streaming data interfaces.

Defines interface for continuous data streaming
with flow control and buffering.

#### Source Code

```{literalinclude} ../../../src/interfaces/core/protocols.py
:language: python
:pyobject: StreamingProtocol
:linenos:
```

#### Methods (5)

##### `start_stream(self, config)`

Start data stream.

[View full source →](#method-streamingprotocol-start_stream)

##### `stop_stream(self, stream_id)`

Stop data stream.

[View full source →](#method-streamingprotocol-stop_stream)

##### `read_stream(self, stream_id, count)`

Read from data stream.

[View full source →](#method-streamingprotocol-read_stream)

##### `write_stream(self, stream_id, data)`

Write to data stream.

[View full source →](#method-streamingprotocol-write_stream)

##### `get_stream_stats(self, stream_id)`

Get stream statistics.

[View full source →](#method-streamingprotocol-get_stream_stats)



### `DeviceProtocol`

**Inherits from:** `ABC`

Protocol for hardware device interfaces.

Defines consistent interface for interacting with
physical devices and hardware components.

#### Source Code

```{literalinclude} ../../../src/interfaces/core/protocols.py
:language: python
:pyobject: DeviceProtocol
:linenos:
```

#### Methods (6)

##### `initialize_device(self, config)`

Initialize device with configuration.

[View full source →](#method-deviceprotocol-initialize_device)

##### `read_from_device(self, register, count)`

Read data from device.

[View full source →](#method-deviceprotocol-read_from_device)

##### `write_to_device(self, register, value)`

Write data to device.

[View full source →](#method-deviceprotocol-write_to_device)

##### `get_device_info(self)`

Get device information.

[View full source →](#method-deviceprotocol-get_device_info)

##### `device_health_check(self)`

Check device health status.

[View full source →](#method-deviceprotocol-device_health_check)

##### `reset_device(self)`

Reset device to initial state.

[View full source →](#method-deviceprotocol-reset_device)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from abc import ABC, abstractmethod`
- `from typing import Any, Dict, List, Optional, Union, Callable, AsyncIterator, Iterator`
- `from dataclasses import dataclass`
- `from enum import Enum`
- `import time`
