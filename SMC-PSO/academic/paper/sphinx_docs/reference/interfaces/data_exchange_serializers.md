# interfaces.data_exchange.serializers

**Source:** `src\interfaces\data_exchange\serializers.py`

## Module Overview

Core serialization framework with multiple format support.
This module provides efficient serializers for various data formats
including JSON, MessagePack, Pickle, and custom binary formats
with compression and performance optimization features.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/serializers.py
:language: python
:linenos:
```



## Classes

### `SerializationFormat`

**Inherits from:** `Enum`

Supported serialization formats.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/serializers.py
:language: python
:pyobject: SerializationFormat
:linenos:
```



### `SerializationError`

**Inherits from:** `Exception`

Exception raised during serialization/deserialization.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/serializers.py
:language: python
:pyobject: SerializationError
:linenos:
```

#### Methods (1)

##### `__init__(self, message, format_type, original_error)`

[View full source →](#method-serializationerror-__init__)



### `SerializerInterface`

**Inherits from:** `ABC`

Abstract interface for serializers.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/serializers.py
:language: python
:pyobject: SerializerInterface
:linenos:
```

#### Methods (5)

##### `serialize(self, data)`

Serialize data to bytes.

[View full source →](#method-serializerinterface-serialize)

##### `deserialize(self, data, target_type)`

Deserialize bytes to data.

[View full source →](#method-serializerinterface-deserialize)

##### `format_type(self)`

Get serialization format type.

[View full source →](#method-serializerinterface-format_type)

##### `content_type(self)`

Get MIME content type.

[View full source →](#method-serializerinterface-content_type)

##### `get_compression_ratio(self, original_data)`

Calculate compression ratio.

[View full source →](#method-serializerinterface-get_compression_ratio)



### `JSONSerializer`

**Inherits from:** `SerializerInterface`

JSON serialization with custom encoder support.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/serializers.py
:language: python
:pyobject: JSONSerializer
:linenos:
```

#### Methods (8)

##### `__init__(self, ensure_ascii, sort_keys, indent, compact)`

[View full source →](#method-jsonserializer-__init__)

##### `format_type(self)`

[View full source →](#method-jsonserializer-format_type)

##### `content_type(self)`

[View full source →](#method-jsonserializer-content_type)

##### `serialize(self, data)`

Serialize data to JSON bytes.

[View full source →](#method-jsonserializer-serialize)

##### `deserialize(self, data, target_type)`

Deserialize JSON bytes to data.

[View full source →](#method-jsonserializer-deserialize)

##### `_json_default(self, obj)`

Default JSON encoder for non-serializable objects.

[View full source →](#method-jsonserializer-_json_default)

##### `_prepare_for_json(self, data)`

Prepare data for JSON serialization.

[View full source →](#method-jsonserializer-_prepare_for_json)

##### `_restore_from_json(self, data)`

Restore data from JSON representation.

[View full source →](#method-jsonserializer-_restore_from_json)



### `MessagePackSerializer`

**Inherits from:** `SerializerInterface`

MessagePack serialization for efficient binary encoding.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/serializers.py
:language: python
:pyobject: MessagePackSerializer
:linenos:
```

#### Methods (5)

##### `__init__(self, use_bin_type, strict_map_key)`

[View full source →](#method-messagepackserializer-__init__)

##### `format_type(self)`

[View full source →](#method-messagepackserializer-format_type)

##### `content_type(self)`

[View full source →](#method-messagepackserializer-content_type)

##### `serialize(self, data)`

Serialize data to MessagePack bytes.

[View full source →](#method-messagepackserializer-serialize)

##### `deserialize(self, data, target_type)`

Deserialize MessagePack bytes to data.

[View full source →](#method-messagepackserializer-deserialize)



### `PickleSerializer`

**Inherits from:** `SerializerInterface`

Pickle serialization for Python object preservation.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/serializers.py
:language: python
:pyobject: PickleSerializer
:linenos:
```

#### Methods (5)

##### `__init__(self, protocol)`

[View full source →](#method-pickleserializer-__init__)

##### `format_type(self)`

[View full source →](#method-pickleserializer-format_type)

##### `content_type(self)`

[View full source →](#method-pickleserializer-content_type)

##### `serialize(self, data)`

Serialize data to pickle bytes.

[View full source →](#method-pickleserializer-serialize)

##### `deserialize(self, data, target_type)`

Deserialize pickle bytes to data.

[View full source →](#method-pickleserializer-deserialize)



### `BinarySerializer`

**Inherits from:** `SerializerInterface`

High-performance binary serializer for structured data.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/serializers.py
:language: python
:pyobject: BinarySerializer
:linenos:
```

#### Methods (5)

##### `__init__(self)`

[View full source →](#method-binaryserializer-__init__)

##### `format_type(self)`

[View full source →](#method-binaryserializer-format_type)

##### `content_type(self)`

[View full source →](#method-binaryserializer-content_type)

##### `serialize(self, data)`

Serialize data to custom binary format.

[View full source →](#method-binaryserializer-serialize)

##### `deserialize(self, data, target_type)`

Deserialize binary data.

[View full source →](#method-binaryserializer-deserialize)



### `CompressionSerializer`

**Inherits from:** `SerializerInterface`

Wrapper serializer that adds compression to any base serializer.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/serializers.py
:language: python
:pyobject: CompressionSerializer
:linenos:
```

#### Methods (6)

##### `__init__(self, base_serializer, compression_type, compression_level)`

[View full source →](#method-compressionserializer-__init__)

##### `format_type(self)`

[View full source →](#method-compressionserializer-format_type)

##### `content_type(self)`

[View full source →](#method-compressionserializer-content_type)

##### `serialize(self, data)`

Serialize and compress data.

[View full source →](#method-compressionserializer-serialize)

##### `deserialize(self, data, target_type)`

Decompress and deserialize data.

[View full source →](#method-compressionserializer-deserialize)

##### `get_compression_stats(self, data)`

Get compression statistics.

[View full source →](#method-compressionserializer-get_compression_stats)



## Functions

### `create_json_serializer(compact, ensure_ascii)`

Create JSON serializer with common settings.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/serializers.py
:language: python
:pyobject: create_json_serializer
:linenos:
```



### `create_msgpack_serializer()`

Create MessagePack serializer.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/serializers.py
:language: python
:pyobject: create_msgpack_serializer
:linenos:
```



### `create_compressed_serializer(base_format, compression_type, compression_level)`

Create compressed serializer.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/serializers.py
:language: python
:pyobject: create_compressed_serializer
:linenos:
```



## Dependencies

This module imports:

- `import json`
- `import pickle`
- `import gzip`
- `import zlib`
- `from abc import ABC, abstractmethod`
- `from typing import Any, Dict, Optional, Union, Type, TypeVar`
- `from enum import Enum`
- `import logging`
- `import time`
- `from .data_types import SerializableData, DataMessage, CompressionType`
