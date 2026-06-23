# interfaces.data_exchange.__init__

**Source:** `src\interfaces\data_exchange\__init__.py`

## Module Overview

Data exchange and serialization framework for interfaces.
This module provides efficient, type-safe serialization and deserialization
across multiple formats including JSON, MessagePack, Protocol Buffers,
and custom binary formats optimized for real-time applications.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .serializers import SerializationFormat, SerializerInterface, SerializationError, JSONSerializer, MessagePackSerializer, PickleSerializer, BinarySerializer, CompressionSerializer`
- `from .schemas import SchemaValidator, ValidationError, DataSchema, JSONSchema, MessageSchema, FieldType`
- `from .data_types import SerializableData, DataMessage, DataPacket, MessageHeader, MessageMetadata`
- `from .factory import SerializerFactory, create_serializer`
- `from .streaming import StreamingSerializer, DataStream, StreamConfig`
