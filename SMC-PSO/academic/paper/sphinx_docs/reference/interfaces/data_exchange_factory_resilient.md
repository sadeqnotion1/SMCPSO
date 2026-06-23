# interfaces.data_exchange.factory_resilient

**Source:** `src\interfaces\data_exchange\factory_resilient.py`

## Module Overview

RESILIENT Factory for serializers and data exchange components.
This is a production-hardened version that eliminates Single Points of Failure (SPOFs)
identified in the original factory implementation.

Key SPOF Fixes Applied:
1. Eliminated global singleton dependency injection pattern
2. Multiple factory instances with failover capability
3. Graceful degradation when components fail
4. Factory registry with automatic recovery
5. Thread-safe factory management
6. Built-in health monitoring and self-healing

PRODUCTION SAFETY: No single points of failure, automatic recovery mechanisms.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory_resilient.py
:language: python
:linenos:
```



## Classes

### `FactoryState`

**Inherits from:** `Enum`

Factory state enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory_resilient.py
:language: python
:pyobject: FactoryState
:linenos:
```



### `FactoryHealth`

Factory health status.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory_resilient.py
:language: python
:pyobject: FactoryHealth
:linenos:
```

#### Methods (2)

##### `update_success(self)`

Record successful operation.

[View full source →](#method-factoryhealth-update_success)

##### `update_error(self, error_msg)`

Record error operation.

[View full source →](#method-factoryhealth-update_error)



### `ResilientSerializerFactory`

Production-safe serializer factory with SPOF elimination.

Features:
- No global singleton dependencies
- Automatic failover and recovery
- Health monitoring and self-healing
- Thread-safe operations
- Graceful degradation

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory_resilient.py
:language: python
:pyobject: ResilientSerializerFactory
:linenos:
```

#### Methods (11)

##### `__init__(self, factory_id)`

Initialize resilient factory.

[View full source →](#method-resilientserializerfactory-__init__)

##### `create_serializer(self, format_type, compression)`

Create serializer with automatic failover.

[View full source →](#method-resilientserializerfactory-create_serializer)

##### `create_serializer_with_retry(self, format_type, compression, max_retries)`

Create serializer with retry logic.

[View full source →](#method-resilientserializerfactory-create_serializer_with_retry)

##### `get_factory_health(self)`

Get factory health status.

[View full source →](#method-resilientserializerfactory-get_factory_health)

##### `get_statistics(self)`

Get factory statistics.

[View full source →](#method-resilientserializerfactory-get_statistics)

##### `clear_cache_and_recover(self)`

Clear cache and attempt recovery.

[View full source →](#method-resilientserializerfactory-clear_cache_and_recover)

##### `_create_serializer_safe(self, format_type, compression, kwargs)`

Safely create serializer with caching.

[View full source →](#method-resilientserializerfactory-_create_serializer_safe)

##### `_create_serializer_impl(self, format_type, compression, kwargs)`

Implementation of serializer creation.

[View full source →](#method-resilientserializerfactory-_create_serializer_impl)

##### `_init_fallback_serializers(self)`

Initialize fallback serializers for emergency use.

[View full source →](#method-resilientserializerfactory-_init_fallback_serializers)

##### `_get_fallback_serializer(self, format_type)`

Get appropriate fallback serializer.

[View full source →](#method-resilientserializerfactory-_get_fallback_serializer)

##### `_generate_cache_key(self, format_type, compression, kwargs)`

Generate cache key for serializer configuration.

[View full source →](#method-resilientserializerfactory-_generate_cache_key)



### `FactoryRegistry`

Registry for managing multiple factory instances with failover.

Eliminates SPOF by maintaining multiple factory instances and
providing automatic failover when factories fail.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory_resilient.py
:language: python
:pyobject: FactoryRegistry
:linenos:
```

#### Methods (7)

##### `__init__(self)`

[View full source →](#method-factoryregistry-__init__)

##### `register_factory(self, factory, weight)`

Register a factory instance.

[View full source →](#method-factoryregistry-register_factory)

##### `unregister_factory(self, factory_id)`

Unregister a factory instance.

[View full source →](#method-factoryregistry-unregister_factory)

##### `get_healthy_factory(self)`

Get a healthy factory instance.

[View full source →](#method-factoryregistry-get_healthy_factory)

##### `create_serializer_resilient(self, format_type, compression)`

Create serializer using resilient factory selection.

[View full source →](#method-factoryregistry-create_serializer_resilient)

##### `get_registry_status(self)`

Get registry status and factory health.

[View full source →](#method-factoryregistry-get_registry_status)

##### `_init_default_factories(self)`

Initialize default factory instances.

[View full source →](#method-factoryregistry-_init_default_factories)



## Functions

### `get_factory_registry()`

Get factory registry (replaceable, not singleton).

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory_resilient.py
:language: python
:pyobject: get_factory_registry
:linenos:
```



### `set_factory_registry(registry)`

Replace factory registry (eliminates singleton dependency).

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory_resilient.py
:language: python
:pyobject: set_factory_registry
:linenos:
```



### `create_serializer_resilient(format_type, compression)`

Create serializer with full resilience and failover.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory_resilient.py
:language: python
:pyobject: create_serializer_resilient
:linenos:
```



### `get_system_health()`

Get overall system health status.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory_resilient.py
:language: python
:pyobject: get_system_health
:linenos:
```



## Dependencies

This module imports:

- `import threading`
- `import time`
- `import weakref`
- `from typing import Dict, Any, Optional, Type, Union, List, Callable`
- `from enum import Enum`
- `import logging`
- `from dataclasses import dataclass, field`
- `from concurrent.futures import ThreadPoolExecutor`
- `import copy`
- `from .serializers import SerializerInterface, SerializationFormat, SerializationError, JSONSerializer, MessagePackSerializer, PickleSerializer, BinarySerializer, CompressionSerializer`

*... and 2 more*
