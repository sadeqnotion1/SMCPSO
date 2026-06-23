# interfaces.network.udp_interface_deadlock_free

**Source:** `src\interfaces\network\udp_interface_deadlock_free.py`

## Module Overview

DEADLOCK-FREE UDP communication interface for real-time control systems.
This version eliminates all deadlock risks found in the thread-safe implementation
by using consistent lock ordering and atomic operations.

Critical Deadlock Fixes:
1. Single lock for all shared state (eliminates lock ordering issues)
2. Atomic operations for counters and sequences
3. Lock-free statistics where possible
4. Consistent ordering when multiple locks needed
5. Minimal critical sections

PRODUCTION SAFETY: All deadlocks eliminated, safe for high-concurrency use.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/network/udp_interface_deadlock_free.py
:language: python
:linenos:
```



## Classes

### `AtomicInteger`

Thread-safe atomic integer.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/udp_interface_deadlock_free.py
:language: python
:pyobject: AtomicInteger
:linenos:
```

#### Methods (5)

##### `__init__(self, value)`

[View full source →](#method-atomicinteger-__init__)

##### `get(self)`

[View full source →](#method-atomicinteger-get)

##### `set(self, value)`

[View full source →](#method-atomicinteger-set)

##### `increment(self)`

[View full source →](#method-atomicinteger-increment)

##### `add(self, delta)`

[View full source →](#method-atomicinteger-add)



### `AtomicFloat`

Thread-safe atomic float.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/udp_interface_deadlock_free.py
:language: python
:pyobject: AtomicFloat
:linenos:
```

#### Methods (3)

##### `__init__(self, value)`

[View full source →](#method-atomicfloat-__init__)

##### `get(self)`

[View full source →](#method-atomicfloat-get)

##### `set(self, value)`

[View full source →](#method-atomicfloat-set)



### `DeadlockFreeUDPInterface`

DEADLOCK-FREE UDP communication interface.

CRITICAL DEADLOCK ELIMINATION STRATEGIES:
1. Single main lock for all shared state
2. Atomic counters for statistics
3. Lock-free reads where possible
4. Minimal critical sections
5. No nested locking

#### Source Code

```{literalinclude} ../../../src/interfaces/network/udp_interface_deadlock_free.py
:language: python
:pyobject: DeadlockFreeUDPInterface
:linenos:
```

#### Methods (13)

##### `__init__(self, config)`

Initialize deadlock-free UDP interface.

[View full source →](#method-deadlockfreeudpinterface-__init__)

##### `connect(self, config)`

Establish UDP connection - single lock operation.

[View full source →](#method-deadlockfreeudpinterface-connect)

##### `disconnect(self)`

Disconnect UDP interface - single lock operation.

[View full source →](#method-deadlockfreeudpinterface-disconnect)

##### `send(self, data, destination, priority, metadata)`

Send data via UDP - deadlock-free implementation.

[View full source →](#method-deadlockfreeudpinterface-send)

##### `receive(self, timeout)`

Receive data via UDP with timeout.

[View full source →](#method-deadlockfreeudpinterface-receive)

##### `get_connection_state(self)`

Get current connection state - single lock.

[View full source →](#method-deadlockfreeudpinterface-get_connection_state)

##### `get_statistics(self)`

Get statistics - mostly atomic reads.

[View full source →](#method-deadlockfreeudpinterface-get_statistics)

##### `register_message_handler(self, message_type, handler)`

Register message handler - single lock.

[View full source →](#method-deadlockfreeudpinterface-register_message_handler)

##### `unregister_message_handler(self, message_type)`

Unregister message handler - single lock.

[View full source →](#method-deadlockfreeudpinterface-unregister_message_handler)

##### `get_message_handler(self, message_type)`

Get message handler - single lock.

[View full source →](#method-deadlockfreeudpinterface-get_message_handler)

##### `reset_statistics(self)`

Reset all statistics - atomic operations.

[View full source →](#method-deadlockfreeudpinterface-reset_statistics)

##### `is_connected(self)`

Check if connected - single lock.

[View full source →](#method-deadlockfreeudpinterface-is_connected)

##### `close(self)`

Close interface and cleanup - single lock.

[View full source →](#method-deadlockfreeudpinterface-close)



## Functions

### `create_deadlock_free_udp_interface(config)`

Create a deadlock-free UDP interface.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/udp_interface_deadlock_free.py
:language: python
:pyobject: create_deadlock_free_udp_interface
:linenos:
```



### `get_global_udp_interface()`

Get global UDP interface instance.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/udp_interface_deadlock_free.py
:language: python
:pyobject: get_global_udp_interface
:linenos:
```



### `set_global_udp_interface(interface)`

Set global UDP interface instance.

#### Source Code

```{literalinclude} ../../../src/interfaces/network/udp_interface_deadlock_free.py
:language: python
:pyobject: set_global_udp_interface
:linenos:
```



## Dependencies

This module imports:

- `import asyncio`
- `import socket`
- `import struct`
- `import time`
- `import zlib`
- `import threading`
- `from typing import Optional, Dict, Any, Tuple, Callable, Union`
- `import logging`
- `from concurrent.futures import ThreadPoolExecutor`
- `from contextlib import contextmanager`

*... and 1 more*
