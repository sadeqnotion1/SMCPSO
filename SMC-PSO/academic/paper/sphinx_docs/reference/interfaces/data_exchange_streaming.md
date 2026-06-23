# interfaces.data_exchange.streaming

**Source:** `src\interfaces\data_exchange\streaming.py`

## Module Overview

Streaming serialization support for large datasets and real-time processing.
This module provides efficient streaming serialization features
for processing large amounts of data, real-time data streams,
and memory-efficient handling of continuous data flows.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:linenos:
```



## Classes

### `StreamMode`

**Inherits from:** `Enum`

Stream processing modes.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: StreamMode
:linenos:
```



### `StreamState`

**Inherits from:** `Enum`

Stream state enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: StreamState
:linenos:
```



### `BackpressureStrategy`

**Inherits from:** `Enum`

Backpressure handling strategies.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: BackpressureStrategy
:linenos:
```



### `StreamConfig`

Configuration for streaming operations.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: StreamConfig
:linenos:
```



### `StreamMetrics`

Streaming performance metrics.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: StreamMetrics
:linenos:
```

#### Methods (1)

##### `update(self, items, bytes_count, processing_time)`

Update metrics with new data.

[View full source →](#method-streammetrics-update)



### `StreamBuffer`

Thread-safe streaming buffer with backpressure handling.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: StreamBuffer
:linenos:
```

#### Methods (8)

##### `__init__(self, max_size, backpressure_strategy)`

[View full source →](#method-streambuffer-__init__)

##### `put(self, item, timeout)`

Put item into buffer with backpressure handling.

[View full source →](#method-streambuffer-put)

##### `get(self, timeout)`

Get item from buffer.

[View full source →](#method-streambuffer-get)

##### `get_batch(self, batch_size, timeout)`

Get batch of items from buffer.

[View full source →](#method-streambuffer-get_batch)

##### `size(self)`

Get current buffer size.

[View full source →](#method-streambuffer-size)

##### `is_full(self)`

Check if buffer is full.

[View full source →](#method-streambuffer-is_full)

##### `close(self)`

Close the buffer.

[View full source →](#method-streambuffer-close)

##### `_wait_for_space(self, timeout)`

Wait for space in buffer.

[View full source →](#method-streambuffer-_wait_for_space)



### `DataStream`

**Inherits from:** `ABC`

Abstract base class for data streams.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: DataStream
:linenos:
```

#### Methods (9)

##### `__init__(self, config)`

[View full source →](#method-datastream-__init__)

##### `state(self)`

[View full source →](#method-datastream-state)

##### `metrics(self)`

[View full source →](#method-datastream-metrics)

##### `start(self)`

Start the stream.

[View full source →](#method-datastream-start)

##### `stop(self)`

Stop the stream.

[View full source →](#method-datastream-stop)

##### `pause(self)`

Pause the stream.

[View full source →](#method-datastream-pause)

##### `resume(self)`

Resume the stream.

[View full source →](#method-datastream-resume)

##### `add_error_handler(self, handler)`

Add error handler.

[View full source →](#method-datastream-add_error_handler)

##### `_handle_error(self, error)`

Handle stream error.

[View full source →](#method-datastream-_handle_error)



### `StreamingSerializer`

Main streaming serializer for processing data streams.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: StreamingSerializer
:linenos:
```

#### Methods (8)

##### `__init__(self, serializer, config)`

[View full source →](#method-streamingserializer-__init__)

##### `start(self)`

Start streaming serialization.

[View full source →](#method-streamingserializer-start)

##### `stop(self)`

Stop streaming serialization.

[View full source →](#method-streamingserializer-stop)

##### `add_data(self, data, timeout)`

Add data to the stream for serialization.

[View full source →](#method-streamingserializer-add_data)

##### `add_output_handler(self, handler)`

Add handler for serialized output.

[View full source →](#method-streamingserializer-add_output_handler)

##### `_process_stream(self)`

Main stream processing loop.

[View full source →](#method-streamingserializer-_process_stream)

##### `_process_batch(self, batch)`

Process a batch of data items.

[View full source →](#method-streamingserializer-_process_batch)

##### `get_metrics(self)`

Get streaming metrics.

[View full source →](#method-streamingserializer-get_metrics)



### `StreamingDeserializer`

Streaming deserializer for processing serialized data streams.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: StreamingDeserializer
:linenos:
```

#### Methods (8)

##### `__init__(self, serializer, config)`

[View full source →](#method-streamingdeserializer-__init__)

##### `start(self)`

Start streaming deserialization.

[View full source →](#method-streamingdeserializer-start)

##### `stop(self)`

Stop streaming deserialization.

[View full source →](#method-streamingdeserializer-stop)

##### `add_serialized_data(self, data, timeout)`

Add serialized data to the stream for deserialization.

[View full source →](#method-streamingdeserializer-add_serialized_data)

##### `add_output_handler(self, handler)`

Add handler for deserialized output.

[View full source →](#method-streamingdeserializer-add_output_handler)

##### `_process_stream(self)`

Main stream processing loop.

[View full source →](#method-streamingdeserializer-_process_stream)

##### `_process_batch(self, batch)`

Process a batch of serialized data.

[View full source →](#method-streamingdeserializer-_process_batch)

##### `get_metrics(self)`

Get streaming metrics.

[View full source →](#method-streamingdeserializer-get_metrics)



### `MessageStream`

**Inherits from:** `DataStream`

Message-oriented data stream with protocol support.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: MessageStream
:linenos:
```

#### Methods (9)

##### `__init__(self, serializer, config)`

[View full source →](#method-messagestream-__init__)

##### `start(self)`

Start message stream.

[View full source →](#method-messagestream-start)

##### `stop(self)`

Stop message stream.

[View full source →](#method-messagestream-stop)

##### `pause(self)`

Pause message stream.

[View full source →](#method-messagestream-pause)

##### `resume(self)`

Resume message stream.

[View full source →](#method-messagestream-resume)

##### `send_message(self, message, timeout)`

Send message through the stream.

[View full source →](#method-messagestream-send_message)

##### `add_message_handler(self, message_type, handler)`

Add handler for specific message type.

[View full source →](#method-messagestream-add_message_handler)

##### `_route_message(self, message_data)`

Route message to appropriate handlers.

[View full source →](#method-messagestream-_route_message)

##### `get_stream_metrics(self)`

Get metrics for all stream components.

[View full source →](#method-messagestream-get_stream_metrics)



### `FileStreamProcessor`

Stream processor for file-based data processing.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: FileStreamProcessor
:linenos:
```

#### Methods (2)

##### `__init__(self, serializer, config)`

[View full source →](#method-filestreamprocessor-__init__)

##### `process_file_stream(self, input_file, output_file, transform_func)`

Process file stream with optional transformation.

[View full source →](#method-filestreamprocessor-process_file_stream)



## Functions

### `create_streaming_serializer(serializer, config)`

Create streaming serializer.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: create_streaming_serializer
:linenos:
```



### `create_streaming_deserializer(serializer, config)`

Create streaming deserializer.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: create_streaming_deserializer
:linenos:
```



### `create_message_stream(serializer, config)`

Create message stream.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: create_message_stream
:linenos:
```



### `create_stream_config(buffer_size, batch_size, flush_interval, backpressure_strategy)`

Create stream configuration.

#### Source Code

```{literalinclude} ../../../src/interfaces/data_exchange/streaming.py
:language: python
:pyobject: create_stream_config
:linenos:
```



## Dependencies

This module imports:

- `import asyncio`
- `import time`
- `import threading`
- `from abc import ABC, abstractmethod`
- `from dataclasses import dataclass, field`
- `from typing import Any, AsyncIterator, Iterator, Optional, Dict, List, Callable, Union`
- `from enum import Enum`
- `import logging`
- `from collections import deque`
- `from .serializers import SerializerInterface, SerializationError`

*... and 1 more*
