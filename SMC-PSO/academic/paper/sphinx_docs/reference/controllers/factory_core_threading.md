# controllers.factory.core.threading

**Source:** `src\controllers\factory\core\threading.py`

## Module Overview

Thread-Safe Factory Operations

Provides thread-safe factory operations with timeout protection, deadlock prevention,
and performance monitoring for concurrent controller creation.

## Complete Source Code

```{literalinclude} ../../../src/controllers/factory/core/threading.py
:language: python
:linenos:
```



## Classes

### `FactoryLockTimeoutError`

**Inherits from:** `Exception`

Raised when factory lock acquisition times out.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/threading.py
:language: python
:pyobject: FactoryLockTimeoutError
:linenos:
```



### `FactoryDeadlockError`

**Inherits from:** `Exception`

Raised when potential deadlock is detected.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/threading.py
:language: python
:pyobject: FactoryDeadlockError
:linenos:
```



### `DeadlockDetector`

Simple deadlock detection based on lock wait times and thread states.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/threading.py
:language: python
:pyobject: DeadlockDetector
:linenos:
```

#### Methods (4)

##### `__init__(self, max_wait_time)`

[View full source →](#method-deadlockdetector-__init__)

##### `register_wait(self, thread_id, function_name)`

Register a thread waiting for the factory lock.

[View full source →](#method-deadlockdetector-register_wait)

##### `unregister_wait(self, thread_id)`

Unregister a thread that has acquired the lock.

[View full source →](#method-deadlockdetector-unregister_wait)

##### `check_for_deadlock(self)`

Check for potential deadlock conditions.

[View full source →](#method-deadlockdetector-check_for_deadlock)



## Functions

### `with_factory_lock(timeout, raise_on_timeout)`

Decorator to make factory functions thread-safe.

Args:
    timeout: Lock acquisition timeout (default: global timeout)
    raise_on_timeout: Raise exception on timeout vs return None

Returns:
    Thread-safe decorated function

Raises:
    FactoryLockTimeoutError: If lock acquisition times out

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/threading.py
:language: python
:pyobject: with_factory_lock
:linenos:
```



### `factory_lock_context(timeout)`

**Decorators:** `@contextmanager`

Context manager for thread-safe factory operations.

Args:
    timeout: Lock acquisition timeout

Yields:
    None when lock is acquired

Raises:
    FactoryLockTimeoutError: If lock acquisition times out

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/threading.py
:language: python
:pyobject: factory_lock_context
:linenos:
```



### `get_lock_statistics()`

Get factory lock performance statistics.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/threading.py
:language: python
:pyobject: get_lock_statistics
:linenos:
```



### `reset_lock_statistics()`

Reset factory lock performance statistics.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/threading.py
:language: python
:pyobject: reset_lock_statistics
:linenos:
```



### `enable_deadlock_detection(enabled)`

Enable or disable deadlock detection.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/threading.py
:language: python
:pyobject: enable_deadlock_detection
:linenos:
```



### `check_thread_safety()`

Check current thread safety status.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/threading.py
:language: python
:pyobject: check_thread_safety
:linenos:
```



### `wait_for_lock_release(timeout)`

Wait for the factory lock to be released by all threads.

Args:
    timeout: Maximum time to wait

Returns:
    True if lock was released, False if timeout occurred

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/threading.py
:language: python
:pyobject: wait_for_lock_release
:linenos:
```



### `force_unlock()`

Force unlock the factory lock (emergency use only).

Returns:
    True if successfully unlocked, False otherwise

Warning:
    This is dangerous and should only be used in emergency situations
    where deadlock recovery is necessary.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/threading.py
:language: python
:pyobject: force_unlock
:linenos:
```



## Dependencies

This module imports:

- `import threading`
- `import time`
- `import logging`
- `from typing import Any, Callable, Optional, TypeVar, ParamSpec`
- `from functools import wraps`
- `from contextlib import contextmanager`
