# interfaces.network.udp_interface

**Source:** `src\interfaces\network\udp_interface.py`

## Module Overview

UDP communication interface for real-time control systems.
This module provides high-performance UDP communication with features like
CRC checking, sequence numbering, and connection state management for
control applications requiring low-latency communication.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/network/udp_interface.py
:language: python
:linenos:
```



## Classes

### `UDPInterface`

**Inherits from:** `CommunicationProtocol`

High-performance UDP communication interface for control systems.

Features:
- Low-latency UDP communication
- Optional CRC integrity checking
- Sequence number tracking
- Connection state management
- Statistics collection
- Message timeout handling

#### Source Code

```{literalinclude} ../../../src/interfaces/network/udp_interface.py
:language: python
:pyobject: UDPInterface
:linenos:
```

#### Methods (12)

##### `__init__(self, config)`

Initialize UDP interface with configuration.

[View full source →](#method-udpinterface-__init__)

##### `connect(self, config)`

Establish UDP connection.

[View full source →](#method-udpinterface-connect)

##### `disconnect(self)`

Close UDP connection.

[View full source →](#method-udpinterface-disconnect)

##### `send(self, data, metadata)`

Send data via UDP with optional CRC and sequence numbering.

[View full source →](#method-udpinterface-send)

##### `receive(self, timeout)`

Receive data via UDP with timeout.

[View full source →](#method-udpinterface-receive)

##### `get_connection_state(self)`

Get current connection state.

[View full source →](#method-udpinterface-get_connection_state)

##### `get_statistics(self)`

Get UDP communication statistics.

[View full source →](#method-udpinterface-get_statistics)

##### `register_message_handler(self, message_type, handler)`

Register handler for specific message type.

[View full source →](#method-udpinterface-register_message_handler)

##### `_parse_endpoint(self, endpoint)`

Parse endpoint string into host and port.

[View full source →](#method-udpinterface-_parse_endpoint)

##### `_serialize_message(self, data, metadata)`

Serialize message data and metadata.

[View full source →](#method-udpinterface-_serialize_message)

##### `_deserialize_message(self, data)`

Deserialize message data and metadata.

[View full source →](#method-udpinterface-_deserialize_message)

##### `_process_received_data(self, data, addr)`

Process received UDP data packet.

[View full source →](#method-udpinterface-_process_received_data)



### `UDPProtocol`

**Inherits from:** `asyncio.DatagramProtocol`

Asyncio UDP protocol handler.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/udp_interface.py
:language: python
:pyobject: UDPProtocol
:linenos:
```

#### Methods (6)

##### `__init__(self, interface)`

[View full source →](#method-udpprotocol-__init__)

##### `connection_made(self, transport)`

Called when connection is established.

[View full source →](#method-udpprotocol-connection_made)

##### `datagram_received(self, data, addr)`

Called when datagram is received.

[View full source →](#method-udpprotocol-datagram_received)

##### `_call_handler(self, handler, data, metadata)`

Call message handler safely.

[View full source →](#method-udpprotocol-_call_handler)

##### `get_next_message(self)`

Get next message from queue.

[View full source →](#method-udpprotocol-get_next_message)

##### `error_received(self, exc)`

Called when error is received.

[View full source →](#method-udpprotocol-error_received)



### `UDPServer`

**Inherits from:** `UDPInterface`

UDP server for hosting control services.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/udp_interface.py
:language: python
:pyobject: UDPServer
:linenos:
```

#### Methods (3)

##### `__init__(self, config)`

[View full source →](#method-udpserver-__init__)

##### `start_server(self, host, port)`

Start UDP server.

[View full source →](#method-udpserver-start_server)

##### `get_connected_clients(self)`

Get list of connected clients.

[View full source →](#method-udpserver-get_connected_clients)



### `UDPClient`

**Inherits from:** `UDPInterface`

UDP client for connecting to control services.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/udp_interface.py
:language: python
:pyobject: UDPClient
:linenos:
```

#### Methods (2)

##### `__init__(self, config)`

[View full source →](#method-udpclient-__init__)

##### `connect_to_server(self, host, port)`

Connect to UDP server.

[View full source →](#method-udpclient-connect_to_server)



## Dependencies

This module imports:

- `import asyncio`
- `import socket`
- `import struct`
- `import time`
- `import zlib`
- `from typing import Optional, Dict, Any, Tuple, Callable`
- `import logging`
- `from ..core.protocols import CommunicationProtocol, MessageMetadata, ConnectionState, MessageType, Priority`
- `from ..core.data_types import Message, ConnectionInfo, InterfaceConfig, InterfaceType, TransportType`
