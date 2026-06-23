# interfaces.core.__init__

**Source:** `src\interfaces\core\__init__.py`

## Module Overview

Core interfaces and protocols for the interfaces framework.
This module provides basic data types and communication protocols
for the interface system.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/core/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .protocols import CommunicationProtocol, MessageProtocol, ConnectionProtocol, SerializationProtocol, ErrorHandlerProtocol, DeviceProtocol`
- `from .data_types import Message, ConnectionInfo, InterfaceConfig, ErrorInfo, PerformanceMetrics, CommunicationStats, QueueConfig, DeviceInfo, InterfaceType, TransportType, SecurityLevel`
