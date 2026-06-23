# interfaces.network.websocket_interface

**Source:** `src\interfaces\network\websocket_interface.py`

## Module Overview

WebSocket communication interface for real-time control system communication.
This module provides WebSocket-based communication with features like real-time
bidirectional messaging, connection management, and support for both client
and server modes for interactive control applications.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/network/websocket_interface.py
:language: python
:linenos:
```



## Classes

### `WebSocketInterface`

**Inherits from:** `CommunicationProtocol`

WebSocket communication interface for control systems.

Features:
- Real-time bidirectional communication
- JSON message serialization
- Connection management
- Heartbeat/ping-pong support
- Message broadcasting
- Client and server modes

#### Source Code

```{literalinclude} ../../../src/interfaces/network/websocket_interface.py
:language: python
:pyobject: WebSocketInterface
:linenos:
```

#### Methods (17)

##### `__init__(self, config)`

Initialize WebSocket interface with configuration.

[View full source →](#method-websocketinterface-__init__)

##### `connect(self, config)`

Establish WebSocket connection.

[View full source →](#method-websocketinterface-connect)

##### `disconnect(self)`

Close WebSocket connection.

[View full source →](#method-websocketinterface-disconnect)

##### `send(self, data, metadata)`

Send data via WebSocket.

[View full source →](#method-websocketinterface-send)

##### `receive(self, timeout)`

Receive data via WebSocket.

[View full source →](#method-websocketinterface-receive)

##### `get_connection_state(self)`

Get current connection state.

[View full source →](#method-websocketinterface-get_connection_state)

##### `get_statistics(self)`

Get WebSocket communication statistics.

[View full source →](#method-websocketinterface-get_statistics)

##### `register_message_handler(self, message_type, handler)`

Register handler for specific message type.

[View full source →](#method-websocketinterface-register_message_handler)

##### `send_to_client(self, client, data, metadata)`

Send message to specific client (server mode).

[View full source →](#method-websocketinterface-send_to_client)

##### `_start_server(self, config)`

Start WebSocket server.

[View full source →](#method-websocketinterface-_start_server)

##### `_connect_client(self, config)`

Connect WebSocket client.

[View full source →](#method-websocketinterface-_connect_client)

##### `_handle_client_connection(self, websocket, path)`

Handle new client connection.

[View full source →](#method-websocketinterface-_handle_client_connection)

##### `_receive_loop(self)`

Continuous receive loop for client mode.

[View full source →](#method-websocketinterface-_receive_loop)

##### `_heartbeat_loop(self)`

Send periodic heartbeat messages.

[View full source →](#method-websocketinterface-_heartbeat_loop)

##### `_call_handler(self, handler, data, metadata, websocket)`

Call message handler safely.

[View full source →](#method-websocketinterface-_call_handler)

##### `_deserialize_message(self, message_json)`

Deserialize WebSocket message.

[View full source →](#method-websocketinterface-_deserialize_message)

##### `_parse_endpoint(self, endpoint)`

Parse endpoint string into host and port.

[View full source →](#method-websocketinterface-_parse_endpoint)



### `WebSocketServer`

**Inherits from:** `WebSocketInterface`

WebSocket server for hosting real-time control services.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/websocket_interface.py
:language: python
:pyobject: WebSocketServer
:linenos:
```

#### Methods (4)

##### `__init__(self, config)`

[View full source →](#method-websocketserver-__init__)

##### `start_server(self, host, port)`

Start WebSocket server.

[View full source →](#method-websocketserver-start_server)

##### `get_connected_clients(self)`

Get set of connected clients.

[View full source →](#method-websocketserver-get_connected_clients)

##### `broadcast(self, data, metadata)`

Broadcast message to all connected clients.

[View full source →](#method-websocketserver-broadcast)



### `WebSocketClient`

**Inherits from:** `WebSocketInterface`

WebSocket client for connecting to real-time control services.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/websocket_interface.py
:language: python
:pyobject: WebSocketClient
:linenos:
```

#### Methods (2)

##### `__init__(self, config)`

[View full source →](#method-websocketclient-__init__)

##### `connect_to_server(self, url)`

Connect to WebSocket server.

[View full source →](#method-websocketclient-connect_to_server)



## Dependencies

This module imports:

- `import asyncio`
- `import websockets`
- `import json`
- `import time`
- `from typing import Optional, Dict, Any, Tuple, Callable, Set`
- `import logging`
- `from ..core.protocols import CommunicationProtocol, MessageMetadata, ConnectionState, MessageType, Priority`
- `from ..core.data_types import Message, ConnectionInfo, InterfaceConfig, InterfaceType`
