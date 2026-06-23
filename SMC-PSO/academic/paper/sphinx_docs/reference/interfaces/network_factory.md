# interfaces.network.factory

**Source:** `src\interfaces\network\factory.py`

## Module Overview

Network interface factory for creating communication interfaces.
This module provides factory methods and utilities for creating and
configuring various types of network communication interfaces for
control systems applications.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/network/factory.py
:language: python
:linenos:
```



## Classes

### `NetworkInterfaceFactory`

Factory for creating network communication interfaces.

This factory provides centralized creation and configuration of
various network interface types with consistent configuration
patterns and error handling.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/factory.py
:language: python
:pyobject: NetworkInterfaceFactory
:linenos:
```

#### Methods (12)

##### `create_interface(cls, interface_type, name, config_overrides)`

Create network interface of specified type.

[View full source →](#method-networkinterfacefactory-create_interface)

##### `create_udp_interface(cls, host, port, server_mode)`

Create UDP interface with simplified configuration.

[View full source →](#method-networkinterfacefactory-create_udp_interface)

##### `create_tcp_interface(cls, host, port, server_mode)`

Create TCP interface with simplified configuration.

[View full source →](#method-networkinterfacefactory-create_tcp_interface)

##### `create_http_interface(cls, host, port, server_mode)`

Create HTTP interface with simplified configuration.

[View full source →](#method-networkinterfacefactory-create_http_interface)

##### `create_websocket_interface(cls, host, port, server_mode)`

Create WebSocket interface with simplified configuration.

[View full source →](#method-networkinterfacefactory-create_websocket_interface)

##### `create_zeromq_interface(cls, socket_configs)`

Create ZeroMQ interface with socket configuration.

[View full source →](#method-networkinterfacefactory-create_zeromq_interface)

##### `create_rabbitmq_interface(cls, url)`

Create RabbitMQ interface with connection URL.

[View full source →](#method-networkinterfacefactory-create_rabbitmq_interface)

##### `create_hil_interface(cls, controller_endpoint, plant_endpoint, protocol)`

Create Hardware-in-the-Loop interface pair.

[View full source →](#method-networkinterfacefactory-create_hil_interface)

##### `register_interface_type(cls, name, interface_class, default_config)`

Register new interface type with factory.

[View full source →](#method-networkinterfacefactory-register_interface_type)

##### `get_available_types(cls)`

Get list of available interface types.

[View full source →](#method-networkinterfacefactory-get_available_types)

##### `get_default_config(cls, interface_type)`

Get default configuration for interface type.

[View full source →](#method-networkinterfacefactory-get_default_config)

##### `_build_interface_config(cls, interface_type, name, config_overrides)`

Build interface configuration from type and overrides.

[View full source →](#method-networkinterfacefactory-_build_interface_config)



## Functions

### `create_control_communication_pair(protocol, controller_port, plant_port, host)`

Create communication interface pair for control applications.

Parameters
----------
protocol : str
    Communication protocol ('udp', 'tcp', 'websocket')
controller_port : int
    Port for controller interface
plant_port : int
    Port for plant interface
host : str
    Host address

Returns
-------
Dict[str, CommunicationProtocol]
    Dictionary with 'controller' and 'plant' interfaces

#### Source Code

```{literalinclude} ../../../src/interfaces/network/factory.py
:language: python
:pyobject: create_control_communication_pair
:linenos:
```



### `create_monitoring_interface(port, host, interface_type)`

Create monitoring interface for control system observation.

Parameters
----------
port : int
    Port number
host : str
    Host address
interface_type : str
    Type of interface ('http', 'websocket')

Returns
-------
CommunicationProtocol
    Configured monitoring interface

#### Source Code

```{literalinclude} ../../../src/interfaces/network/factory.py
:language: python
:pyobject: create_monitoring_interface
:linenos:
```



### `create_distributed_control_mesh(nodes, protocol)`

Create mesh of communication interfaces for distributed control.

Parameters
----------
nodes : list
    List of node configurations
protocol : str
    Communication protocol ('zeromq', 'rabbitmq')

Returns
-------
Dict[str, CommunicationProtocol]
    Dictionary of node interfaces

#### Source Code

```{literalinclude} ../../../src/interfaces/network/factory.py
:language: python
:pyobject: create_distributed_control_mesh
:linenos:
```



## Dependencies

This module imports:

- `from typing import Dict, Any, Type, Optional, Union`
- `import logging`
- `from ..core.protocols import CommunicationProtocol`
- `from ..core.data_types import InterfaceConfig, InterfaceType`
- `from .udp_interface import UDPInterface, UDPServer, UDPClient`
- `from .tcp_interface import TCPInterface, TCPServer, TCPClient`
- `from .http_interface import HTTPInterface, HTTPServer, HTTPClient`
- `from .websocket_interface import WebSocketInterface, WebSocketServer, WebSocketClient`
- `from .message_queue import MessageQueueInterface, ZeroMQInterface, RabbitMQInterface`
