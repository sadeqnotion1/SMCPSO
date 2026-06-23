# interfaces.data_exchange.factory

**Source:** `src\interfaces\data_exchange\factory.py`

## Module Overview

Factory for creating serializers and data exchange components.
This module provides a unified factory interface for creating
serializers, validators, and other data exchange components
with automatic configuration and optimization.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory.py
:language: python
:linenos:
```



## Classes

### `SerializerPreset`

**Inherits from:** `Enum`

Predefined serializer configurations.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory.py
:language: python
:pyobject: SerializerPreset
:linenos:
```



### `OptimizationMode`

**Inherits from:** `Enum`

Optimization modes for serializer selection.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory.py
:language: python
:pyobject: OptimizationMode
:linenos:
```



### `SerializerFactory`

Factory for creating and managing serializers.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory.py
:language: python
:pyobject: SerializerFactory
:linenos:
```

#### Methods (17)

##### `__init__(self)`

[View full source →](#method-serializerfactory-__init__)

##### `create_serializer(self, format_type, compression)`

Create serializer with specified format and options.

[View full source →](#method-serializerfactory-create_serializer)

##### `create_from_preset(self, preset)`

Create serializer from predefined preset.

[View full source →](#method-serializerfactory-create_from_preset)

##### `create_optimized(self, optimization_mode, data_characteristics)`

Create serializer optimized for specific use case.

[View full source →](#method-serializerfactory-create_optimized)

##### `auto_select_serializer(self, sample_data, requirements)`

Automatically select best serializer based on data analysis.

[View full source →](#method-serializerfactory-auto_select_serializer)

##### `benchmark_serializers(self, test_data, formats)`

Benchmark different serializers with test data.

[View full source →](#method-serializerfactory-benchmark_serializers)

##### `clear_cache(self)`

Clear serializer cache.

[View full source →](#method-serializerfactory-clear_cache)

##### `get_cache_info(self)`

Get cache statistics.

[View full source →](#method-serializerfactory-get_cache_info)

##### `_create_serializer_impl(self, format_type, compression, kwargs)`

Internal serializer creation implementation.

[View full source →](#method-serializerfactory-_create_serializer_impl)

##### `_initialize_presets(self)`

Initialize predefined serializer configurations.

[View full source →](#method-serializerfactory-_initialize_presets)

##### `_get_optimized_config(self, mode, characteristics)`

Get optimized configuration for specific mode.

[View full source →](#method-serializerfactory-_get_optimized_config)

##### `_analyze_data_characteristics(self, data)`

Analyze data to determine characteristics for optimization.

[View full source →](#method-serializerfactory-_analyze_data_characteristics)

##### `_contains_binary_data(self, data)`

Check if data contains binary content.

[View full source →](#method-serializerfactory-_contains_binary_data)

##### `_assess_complexity(self, data, depth)`

Assess data structure complexity.

[View full source →](#method-serializerfactory-_assess_complexity)

##### `_has_repetitive_patterns(self, data)`

Check for repetitive patterns that benefit from compression.

[View full source →](#method-serializerfactory-_has_repetitive_patterns)

##### `_benchmark_serializer(self, serializer, test_data, iterations)`

Benchmark a serializer with test data.

[View full source →](#method-serializerfactory-_benchmark_serializer)

##### `_generate_cache_key(self, format_type, compression, kwargs)`

Generate cache key for serializer configuration.

[View full source →](#method-serializerfactory-_generate_cache_key)



## Functions

### `create_serializer(format_type, compression)`

Create serializer using global factory.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory.py
:language: python
:pyobject: create_serializer
:linenos:
```



### `create_from_preset(preset)`

Create serializer from preset using global factory.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory.py
:language: python
:pyobject: create_from_preset
:linenos:
```



### `auto_select_serializer(sample_data, requirements)`

Auto-select optimal serializer using global factory.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory.py
:language: python
:pyobject: auto_select_serializer
:linenos:
```



### `benchmark_serializers(test_data, formats)`

Benchmark serializers using global factory.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory.py
:language: python
:pyobject: benchmark_serializers
:linenos:
```



### `get_recommended_serializer(use_case)`

Get recommended serializer for common use cases.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/factory.py
:language: python
:pyobject: get_recommended_serializer
:linenos:
```



## Dependencies

This module imports:

- `from typing import Dict, Any, Optional, Type, Union`
- `from enum import Enum`
- `import logging`
- `from .serializers import SerializerInterface, SerializationFormat, SerializationError, JSONSerializer, MessagePackSerializer, PickleSerializer, BinarySerializer, CompressionSerializer, create_json_serializer, create_msgpack_serializer, create_compressed_serializer`
- `from .schemas import SchemaValidator, DataSchema, MessageSchema`
- `from .data_types import CompressionType`
