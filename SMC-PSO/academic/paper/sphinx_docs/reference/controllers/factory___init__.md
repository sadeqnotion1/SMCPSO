# controllers.factory.__init__

**Source:** `src\controllers\factory\__init__.py`

## Module Overview

Controller Factory Package

Provides clean, focused factory interfaces for creating controllers:
- SMC Factory: Type-safe, PSO-optimized interface for 4 core SMC controllers
- Legacy Factory: Backward-compatible factory for existing code

Recommended Usage:
    # Use the clean SMC factory for new code
    from controllers.factory import SMCFactory, SMCType, create_smc_for_pso

    # Use legacy factory only for backward compatibility
    from controllers.factory import create_controller_legacy

## Complete Source Code

```{literalinclude} ../../../src/controllers/factory/__init__.py
:language: python
:linenos:
```



## Functions

### `apply_deprecation_mapping(controller_type, params, allow_unknown)`

Apply deprecation mapping for controller parameters.

This function handles mapping of deprecated parameter names
to their current equivalents for backward compatibility.

Args:
    controller_type: The controller type string to map
    params: Parameters dictionary to process (optional)
    allow_unknown: Whether to allow unknown parameters (ignored)

Returns:
    Processed parameters dictionary with deprecation mappings applied

#### Source Code

```{literalinclude} ../../../src/controllers/factory/__init__.py
:language: python
:pyobject: apply_deprecation_mapping
:linenos:
```



### `_as_dict(obj)`

Convert an object to dictionary representation.

Handles objects with model_dump() method (like Pydantic models)
and regular objects with __dict__.

Args:
    obj: Object to convert to dictionary

Returns:
    Dictionary representation of the object

#### Source Code

```{literalinclude} ../../../src/controllers/factory/__init__.py
:language: python
:pyobject: _as_dict
:linenos:
```



## Dependencies

This module imports:

- `from typing import Dict, List, Any`
- `from .smc_factory import SMCType, SMCConfig, SMCGainSpec, SMCProtocol, SMCFactory, PSOControllerWrapper, create_smc_for_pso, get_gain_bounds_for_pso, validate_smc_gains, SMC_GAIN_SPECS`
- `from .legacy_factory import create_controller as create_controller_legacy`
- `from .legacy_factory import create_controller`
- `from .legacy_factory import build_controller as build_controller_legacy`
- `from .legacy_factory import build_controller`
- `from .legacy_factory import build_all as build_all_legacy`
- `from .legacy_factory import _canonical`
- `from .legacy_factory import FactoryConfigurationError, ConfigValueError, UnknownConfigKeyError`
- `import sys`

*... and 2 more*
