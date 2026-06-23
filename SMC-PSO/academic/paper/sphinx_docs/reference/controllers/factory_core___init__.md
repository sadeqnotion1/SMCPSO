# controllers.factory.core.__init__

**Source:** `src\controllers\factory\core\__init__.py`

## Module Overview

Factory Core Module - Central Factory Infrastructure

Core components for the controller factory system including:
- Base factory interfaces and protocols
- Registry management
- Configuration validation
- Thread-safe operations

## Complete Source Code

```{literalinclude} ../../../src/controllers/factory/core/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .registry import CONTROLLER_REGISTRY, get_controller_info`
- `from .protocols import ControllerProtocol, ControllerFactoryProtocol`
- `from .validation import validate_controller_gains, validate_configuration`
- `from .threading import factory_lock, with_factory_lock`
