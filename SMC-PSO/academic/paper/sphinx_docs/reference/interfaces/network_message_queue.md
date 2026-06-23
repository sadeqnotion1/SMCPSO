# interfaces.network.message_queue

**Source:** `src\interfaces\network\message_queue.py`

## Module Overview

Message queue communication interfaces for distributed control systems.
This module provides message queue-based communication with support for
ZeroMQ, RabbitMQ, and other queue systems for scalable, reliable
messaging in distributed control applications.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/network/message_queue.py
:language: python
:linenos:
```



## Classes

### `MessageQueueInterface`

**Inherits from:** `CommunicationProtocol`, `ABC`

Abstract base class for message queue interfaces.

Features:
- Publish/subscribe messaging patterns
- Request/reply patterns
- Message persistence
- Load balancing
- Acknowledgments and reliability

#### Source Code

```{literalinclude} ../../../src/interfaces/network/message_queue.py
:language: python
:pyobject: MessageQueueInterface
:linenos:
```

#### Methods (6)

##### `__init__(self, config)`

Initialize message queue interface.

[View full source →](#method-messagequeueinterface-__init__)

##### `publish(self, topic, data, metadata)`

Publish message to topic.

[View full source →](#method-messagequeueinterface-publish)

##### `subscribe(self, topic, handler)`

Subscribe to topic with message handler.

[View full source →](#method-messagequeueinterface-subscribe)

##### `unsubscribe(self, topic)`

Unsubscribe from topic.

[View full source →](#method-messagequeueinterface-unsubscribe)

##### `request(self, data, timeout)`

Send request and wait for reply.

[View full source →](#method-messagequeueinterface-request)

##### `reply(self, request_data, response_data)`

Send reply to request.

[View full source →](#method-messagequeueinterface-reply)



### `ZeroMQInterface`

**Inherits from:** `MessageQueueInterface`

ZeroMQ communication interface for high-performance messaging.

Features:
- Multiple socket patterns (PUB/SUB, REQ/REP, PUSH/PULL)
- High throughput and low latency
- Built-in load balancing
- No broker required

#### Source Code

```{literalinclude} ../../../src/interfaces/network/message_queue.py
:language: python
:pyobject: ZeroMQInterface
:linenos:
```

#### Methods (18)

##### `__init__(self, config)`

Initialize ZeroMQ interface.

[View full source →](#method-zeromqinterface-__init__)

##### `connect(self, config)`

Establish ZeroMQ connection.

[View full source →](#method-zeromqinterface-connect)

##### `disconnect(self)`

Close ZeroMQ connection.

[View full source →](#method-zeromqinterface-disconnect)

##### `send(self, data, metadata)`

Send data via ZeroMQ (using default socket).

[View full source →](#method-zeromqinterface-send)

##### `receive(self, timeout)`

Receive data via ZeroMQ (from default socket).

[View full source →](#method-zeromqinterface-receive)

##### `get_connection_state(self)`

Get current connection state.

[View full source →](#method-zeromqinterface-get_connection_state)

##### `get_statistics(self)`

Get ZeroMQ communication statistics.

[View full source →](#method-zeromqinterface-get_statistics)

##### `publish(self, topic, data, metadata)`

Publish message to topic using PUB socket.

[View full source →](#method-zeromqinterface-publish)

##### `subscribe(self, topic, handler)`

Subscribe to topic with message handler.

[View full source →](#method-zeromqinterface-subscribe)

##### `unsubscribe(self, topic)`

Unsubscribe from topic.

[View full source →](#method-zeromqinterface-unsubscribe)

##### `request(self, data, timeout)`

Send request and wait for reply using REQ socket.

[View full source →](#method-zeromqinterface-request)

##### `reply(self, request_data, response_data)`

Send reply to request using REP socket.

[View full source →](#method-zeromqinterface-reply)

##### `_create_socket(self, socket_config)`

Create and configure ZeroMQ socket.

[View full source →](#method-zeromqinterface-_create_socket)

##### `_subscribe_receive_loop(self)`

Receive loop for SUB socket.

[View full source →](#method-zeromqinterface-_subscribe_receive_loop)

##### `_reply_receive_loop(self, rep_socket)`

Receive loop for REP socket.

[View full source →](#method-zeromqinterface-_reply_receive_loop)

##### `_call_handler(self, handler, data, metadata, topic)`

Call message handler safely.

[View full source →](#method-zeromqinterface-_call_handler)

##### `_serialize_message(self, data, metadata)`

Serialize message data and metadata.

[View full source →](#method-zeromqinterface-_serialize_message)

##### `_deserialize_message(self, data)`

Deserialize message data and metadata.

[View full source →](#method-zeromqinterface-_deserialize_message)



### `RabbitMQInterface`

**Inherits from:** `MessageQueueInterface`

RabbitMQ communication interface for reliable messaging.

Features:
- Message persistence and durability
- Routing and exchanges
- Acknowledgments and reliability
- Dead letter queues

#### Source Code

```{literalinclude} ../../../src/interfaces/network/message_queue.py
:language: python
:pyobject: RabbitMQInterface
:linenos:
```

#### Methods (16)

##### `__init__(self, config)`

Initialize RabbitMQ interface.

[View full source →](#method-rabbitmqinterface-__init__)

##### `connect(self, config)`

Establish RabbitMQ connection.

[View full source →](#method-rabbitmqinterface-connect)

##### `disconnect(self)`

Close RabbitMQ connection.

[View full source →](#method-rabbitmqinterface-disconnect)

##### `send(self, data, metadata)`

Send data via RabbitMQ (using default exchange).

[View full source →](#method-rabbitmqinterface-send)

##### `receive(self, timeout)`

Receive data via RabbitMQ.

[View full source →](#method-rabbitmqinterface-receive)

##### `get_connection_state(self)`

Get current connection state.

[View full source →](#method-rabbitmqinterface-get_connection_state)

##### `get_statistics(self)`

Get RabbitMQ communication statistics.

[View full source →](#method-rabbitmqinterface-get_statistics)

##### `publish(self, routing_key, data, metadata, exchange)`

Publish message to RabbitMQ exchange.

[View full source →](#method-rabbitmqinterface-publish)

##### `subscribe(self, queue_name, handler)`

Subscribe to RabbitMQ queue with message handler.

[View full source →](#method-rabbitmqinterface-subscribe)

##### `unsubscribe(self, queue_name)`

Unsubscribe from RabbitMQ queue.

[View full source →](#method-rabbitmqinterface-unsubscribe)

##### `request(self, data, timeout)`

Send request and wait for reply using RabbitMQ RPC pattern.

[View full source →](#method-rabbitmqinterface-request)

##### `reply(self, request_data, response_data)`

Send reply to request using RabbitMQ.

[View full source →](#method-rabbitmqinterface-reply)

##### `_handle_rabbitmq_message(self, message, handler)`

Handle incoming RabbitMQ message.

[View full source →](#method-rabbitmqinterface-_handle_rabbitmq_message)

##### `_call_handler(self, handler, data, metadata)`

Call message handler safely.

[View full source →](#method-rabbitmqinterface-_call_handler)

##### `_serialize_message(self, data, metadata)`

Serialize message data and metadata.

[View full source →](#method-rabbitmqinterface-_serialize_message)

##### `_deserialize_message(self, data)`

Deserialize message data and metadata.

[View full source →](#method-rabbitmqinterface-_deserialize_message)



## Dependencies

This module imports:

- `import asyncio`
- `import time`
- `import json`
- `import pickle`
- `from typing import Optional, Dict, Any, Tuple, Callable, List`
- `import logging`
- `from abc import ABC, abstractmethod`
- `from ..core.protocols import CommunicationProtocol, MessageMetadata, ConnectionState, MessageType, Priority`
- `from ..core.data_types import Message, ConnectionInfo, InterfaceConfig, InterfaceType`
