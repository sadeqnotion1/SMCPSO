# plant.configurations.__init__

**Source:** `src\plant\configurations\__init__.py`

## Module Overview

Configuration management for plant dynamics.

Provides type-safe configuration classes with validation for different
plant dynamics models. Ensures physical consistency and mathematical
correctness of system parameters.

## Complete Source Code

```{literalinclude} ../../../src/plant/configurations/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .base_config import BasePhysicsConfig, BaseDIPConfig, ConfigurationError, ConfigurationWarning`
- `from .unified_config import ConfigurationFactory, UnifiedConfiguration, DIPModelType`
- `from .validation import ParameterValidator, PhysicsParameterValidator, validate_physics_parameters`
