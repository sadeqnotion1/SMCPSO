# interfaces.network.tcp_interface

**Source:** `src\interfaces\network\tcp_interface.py`

## Module Overview

TCP communication interface for reliable control system communication.
This module provides TCP-based communication with features like connection
pooling, automatic reconnection, message framing, and flow control for
applications requiring reliable message delivery.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/network/tcp_interface.py
:language: python
:linenos:
```



## Classes

### `TCPInterface`

**Inherits from:** `CommunicationProtocol`

Reliable TCP communication interface for control systems.

Features:
- Reliable TCP stream communication
- Message framing with length prefixes
- Connection management and pooling
- Automatic reconnection
- Flow control and backpressure handling
- Statistics collection

#### Source Code

```{literalinclude} ../../../src/interfaces/network/tcp_interface.py
:language: python
:pyobject: TCPInterface
:linenos:
```

#### Methods (16)

##### `__init__(self, config)`

Initialize TCP interface with configuration.

[View full source →](#method-tcpinterface-__init__)

##### `connect(self, config)`

Establish TCP connection.

[View full source →](#method-tcpinterface-connect)

##### `disconnect(self)`

Close TCP connection.

[View full source →](#method-tcpinterface-disconnect)

##### `send(self, data, metadata)`

Send data via TCP with message framing.

[View full source →](#method-tcpinterface-send)

##### `receive(self, timeout)`

Receive data via TCP with timeout.

[View full source →](#method-tcpinterface-receive)

##### `get_connection_state(self)`

Get current connection state.

[View full source →](#method-tcpinterface-get_connection_state)

##### `get_statistics(self)`

Get TCP communication statistics.

[View full source →](#method-tcpinterface-get_statistics)

##### `register_message_handler(self, message_type, handler)`

Register handler for specific message type.

[View full source →](#method-tcpinterface-register_message_handler)

##### `_handle_client_connection(self, reader, writer)`

Handle new client connection in server mode.

[View full source →](#method-tcpinterface-_handle_client_connection)

##### `_receive_message(self, reader, timeout)`

Receive framed message from stream.

[View full source →](#method-tcpinterface-_receive_message)

##### `_receive_loop(self)`

Continuous receive loop for client mode.

[View full source →](#method-tcpinterface-_receive_loop)

##### `_call_handler(self, handler, data, metadata, client_id)`

Call message handler safely.

[View full source →](#method-tcpinterface-_call_handler)

##### `_reconnect(self)`

Attempt to reconnect to server.

[View full source →](#method-tcpinterface-_reconnect)

##### `_parse_endpoint(self, endpoint)`

Parse endpoint string into host and port.

[View full source →](#method-tcpinterface-_parse_endpoint)

##### `_serialize_message(self, data, metadata)`

Serialize message data and metadata.

[View full source →](#method-tcpinterface-_serialize_message)

##### `_deserialize_message(self, data)`

Deserialize message data and metadata.

[View full source →](#method-tcpinterface-_deserialize_message)



### `TCPServer`

**Inherits from:** `TCPInterface`

TCP server for hosting control services.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/tcp_interface.py
:language: python
:pyobject: TCPServer
:linenos:
```

#### Methods (4)

##### `__init__(self, config)`

[View full source →](#method-tcpserver-__init__)

##### `start_server(self, host, port)`

Start TCP server.

[View full source →](#method-tcpserver-start_server)

##### `get_connected_clients(self)`

Get list of connected client IDs.

[View full source →](#method-tcpserver-get_connected_clients)

##### `send_to_client(self, client_id, data, metadata)`

Send message to specific client.

[View full source →](#method-tcpserver-send_to_client)



### `TCPClient`

**Inherits from:** `TCPInterface`

TCP client for connecting to control services.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/tcp_interface.py
:language: python
:pyobject: TCPClient
:linenos:
```

#### Methods (2)

##### `__init__(self, config)`

[View full source →](#method-tcpclient-__init__)

##### `connect_to_server(self, host, port)`

Connect to TCP server.

[View full source →](#method-tcpclient-connect_to_server)



## Dependencies

This module imports:

- `import asyncio`
- `import struct`
- `import time`
- `import json`
- `import pickle`
- `from typing import Optional, Dict, Any, Tuple, Callable, List`
- `import logging`
- `from ..core.protocols import CommunicationProtocol, MessageMetadata, ConnectionState, MessageType, Priority`
- `from ..core.data_types import Message, ConnectionInfo, InterfaceConfig, InterfaceType`
