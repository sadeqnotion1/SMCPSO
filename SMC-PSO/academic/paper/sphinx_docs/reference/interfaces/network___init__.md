# interfaces.network.__init__

**Source:** `src\interfaces\network\__init__.py`

## Module Overview Network

communication module for control system interfaces

.


This module provides network communication features including
UDP, TCP, HTTP, WebSocket, and message queue protocols for distributed
control systems and real-time applications. ## Complete Source Code ```{literalinclude} ../../../src/interfaces/network/__init__.py
:language: python
:linenos:
```

---

## Dependencies This module imports: - `from .udp_interface import UDPInterface, UDPServer, UDPClient`
- `from .tcp_interface import TCPInterface, TCPServer, TCPClient`
- `from .http_interface import HTTPInterface, HTTPServer, HTTPClient`
- `from .websocket_interface import WebSocketInterface, WebSocketServer, WebSocketClient`
- `from .message_queue import MessageQueueInterface, ZeroMQInterface, RabbitMQInterface`
- `from .factory import NetworkInterfaceFactory`
