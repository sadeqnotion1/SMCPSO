# interfaces.network.http_interface

**Source:** `src\interfaces\network\http_interface.py`

## Module Overview

HTTP/REST communication interface for control system web services.
This module provides HTTP-based communication with RESTful APIs, JSON
serialization, authentication, and CORS support for web-based control
applications and monitoring dashboards.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/network/http_interface.py
:language: python
:linenos:
```



## Classes

### `HTTPInterface`

**Inherits from:** `CommunicationProtocol`

HTTP/REST communication interface for control systems.

Features:
- RESTful HTTP communication
- JSON serialization
- Authentication and authorization
- CORS support for web clients
- Request/response pattern
- Health monitoring endpoints

#### Source Code

```{literalinclude} ../../../src/interfaces/network/http_interface.py
:language: python
:pyobject: HTTPInterface
:linenos:
```

#### Methods (19)

##### `__init__(self, config)`

Initialize HTTP interface with configuration.

[View full source →](#method-httpinterface-__init__)

##### `connect(self, config)`

Establish HTTP connection (server or client).

[View full source →](#method-httpinterface-connect)

##### `disconnect(self)`

Close HTTP connection.

[View full source →](#method-httpinterface-disconnect)

##### `send(self, data, metadata)`

Send HTTP request (client mode).

[View full source →](#method-httpinterface-send)

##### `receive(self, timeout)`

Receive HTTP request/response (not applicable for HTTP).

[View full source →](#method-httpinterface-receive)

##### `get_connection_state(self)`

Get current connection state.

[View full source →](#method-httpinterface-get_connection_state)

##### `get_statistics(self)`

Get HTTP communication statistics.

[View full source →](#method-httpinterface-get_statistics)

##### `add_route(self, method, path, handler)`

Add HTTP route handler.

[View full source →](#method-httpinterface-add_route)

##### `add_middleware(self, middleware)`

Add HTTP middleware.

[View full source →](#method-httpinterface-add_middleware)

##### `set_auth_handler(self, handler)`

Set authentication handler.

[View full source →](#method-httpinterface-set_auth_handler)

##### `_start_server(self, config)`

Start HTTP server.

[View full source →](#method-httpinterface-_start_server)

##### `_register_routes(self)`

Register all configured routes.

[View full source →](#method-httpinterface-_register_routes)

##### `_wrap_handler(self, handler)`

Wrap user handler with standard processing.

[View full source →](#method-httpinterface-_wrap_handler)

##### `_cors_middleware(self, request, handler)`

CORS middleware.

[View full source →](#method-httpinterface-_cors_middleware)

##### `_auth_middleware(self, request, handler)`

Authentication middleware.

[View full source →](#method-httpinterface-_auth_middleware)

##### `_logging_middleware(self, request, handler)`

Logging middleware.

[View full source →](#method-httpinterface-_logging_middleware)

##### `_health_check_handler(self, request)`

Health check endpoint.

[View full source →](#method-httpinterface-_health_check_handler)

##### `_stats_handler(self, request)`

Statistics endpoint.

[View full source →](#method-httpinterface-_stats_handler)

##### `_parse_endpoint(self, endpoint)`

Parse endpoint string into host and port.

[View full source →](#method-httpinterface-_parse_endpoint)



### `HTTPServer`

**Inherits from:** `HTTPInterface`

HTTP server for hosting RESTful control services.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/http_interface.py
:language: python
:pyobject: HTTPServer
:linenos:
```

#### Methods (6)

##### `__init__(self, config)`

[View full source →](#method-httpserver-__init__)

##### `start_server(self, host, port)`

Start HTTP server.

[View full source →](#method-httpserver-start_server)

##### `add_get_route(self, path, handler)`

Add GET route.

[View full source →](#method-httpserver-add_get_route)

##### `add_post_route(self, path, handler)`

Add POST route.

[View full source →](#method-httpserver-add_post_route)

##### `add_put_route(self, path, handler)`

Add PUT route.

[View full source →](#method-httpserver-add_put_route)

##### `add_delete_route(self, path, handler)`

Add DELETE route.

[View full source →](#method-httpserver-add_delete_route)



### `HTTPClient`

**Inherits from:** `HTTPInterface`

HTTP client for calling RESTful control services.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/http_interface.py
:language: python
:pyobject: HTTPClient
:linenos:
```

#### Methods (6)

##### `__init__(self, config)`

[View full source →](#method-httpclient-__init__)

##### `connect_to_server(self, base_url)`

Connect to HTTP server.

[View full source →](#method-httpclient-connect_to_server)

##### `get(self, path, headers)`

Send GET request.

[View full source →](#method-httpclient-get)

##### `post(self, path, data, headers)`

Send POST request.

[View full source →](#method-httpclient-post)

##### `put(self, path, data, headers)`

Send PUT request.

[View full source →](#method-httpclient-put)

##### `delete(self, path, headers)`

Send DELETE request.

[View full source →](#method-httpclient-delete)



## Dependencies

This module imports:

- `import asyncio`
- `import aiohttp`
- `import json`
- `import time`
- `from typing import Optional, Dict, Any, Tuple, Callable, List`
- `import logging`
- `from aiohttp import web, ClientSession, ClientTimeout`
- `from ..core.protocols import CommunicationProtocol, MessageMetadata, ConnectionState, MessageType, Priority`
- `from ..core.data_types import Message, ConnectionInfo, InterfaceConfig, InterfaceType`
