# controllers.factory.legacy_factory

**Source:** `src\controllers\factory\legacy_factory.py`

## Module Overview

Controller factory with Pydantic v2 config alignment and robust error handling.

## Complete Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:linenos:
```



## Classes

### `FactoryConfigurationError`

**Inherits from:** `Exception`

Raised when controller configuration or resolution fails.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: FactoryConfigurationError
:linenos:
```



### `ConfigValueError`

**Inherits from:** `ValueError`

Raised when a config value is out of the accepted range.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: ConfigValueError
:linenos:
```



### `UnknownConfigKeyError`

**Inherits from:** `ValueError`

Raised when unexpected/unknown keys appear in a controller config block.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: UnknownConfigKeyError
:linenos:
```



## Functions

### `_try_import(primary_mod, fallback_mod, attr)`

Try importing ``attr`` from ``primary_mod`` then ``fallback_mod``.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: _try_import
:linenos:
```



### `normalize_controller_name(name)`

Normalize controller name and apply aliases.

Lowercase, trim, replace hyphens/spaces/dots with underscores,
then check alias map.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: normalize_controller_name
:linenos:
```



### `normalize_param_key(key)`

Normalize parameter key: lowercase, replace hyphens/spaces with underscores.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: normalize_param_key
:linenos:
```



### `apply_deprecation_mapping(controller_name, params, allow_unknown)`

Apply deprecation mapping for a controller's parameters.

Returns normalized params dict with deprecated keys mapped to current ones.
Emits DeprecationWarning for each deprecated key found.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: apply_deprecation_mapping
:linenos:
```



### `redact_value(value)`

Redact sensitive values for logging.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: redact_value
:linenos:
```



### `register_controller(name)`

Decorator for registering controller constructors.

Registration is idempotent - re-registering the same name overwrites.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: register_controller
:linenos:
```



### `_as_dict(obj)`

Robustly convert an arbitrary object into a plain dict.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: _as_dict
:linenos:
```



### `_get_default_gains(controller_name, config, gains_override)`

Get gains from override, defaults, or raise error.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: _get_default_gains
:linenos:
```



### `_ensure_dynamics_available(use_full)`

Ensure required dynamics model is available.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: _ensure_dynamics_available
:linenos:
```



### `_validate_shared_params(controller_name, dt, max_force)`

Validate common parameters shared by controllers.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: _validate_shared_params
:linenos:
```



### `build_controller(name, cfg)`

Build a single controller from configuration.

Parameters
----------
name : str
    Controller name (will be normalized and aliased).
cfg : dict or Mapping or ControllerConfig
    Controller-specific configuration.
allow_unknown : bool
    If True, unknown parameters are stored as unknown_params on the instance.
    If False, unknown parameters raise FactoryConfigurationError.
config : optional
    Full configuration object (for backward compatibility).
gains : optional
    Explicit gains override.

Returns
-------
Controller instance

Raises
------
FactoryConfigurationError
    If controller name is unknown or configuration is invalid.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: build_controller
:linenos:
```



### `build_all(controllers_cfg)`

Build all controllers from a ControllersConfig.

Parameters
----------
controllers_cfg : ControllersConfig or dict
    Configuration for all controllers.
allow_unknown : bool
    If True, unknown parameters are stored on instances.
    If False, unknown parameters raise errors.
config : optional
    Full configuration object for defaults.

Returns
-------
dict[str, Controller]
    Mapping of controller names to instances.

Raises
------
FactoryConfigurationError
    If any controller fails to build (aggregates all errors).

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: build_all
:linenos:
```



### `_legacy_create_controller(ctrl_name, ctrl_cfg, config, gains, allow_unknown)`

Legacy controller creation for backward compatibility.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: _legacy_create_controller
:linenos:
```



### `_build_classical_smc(key, ctrl_cfg_dict, config, gains, dynamics_model, shared_dt, shared_max_force, allow_unknown)`

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: _build_classical_smc
:linenos:
```



### `_build_sta_smc(key, ctrl_cfg_dict, config, gains, dynamics_model, shared_dt, shared_max_force, allow_unknown)`

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: _build_sta_smc
:linenos:
```



### `_build_adaptive_smc(key, ctrl_cfg_dict, config, gains, shared_dt, shared_max_force, allow_unknown)`

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: _build_adaptive_smc
:linenos:
```



### `_build_swing_up_smc(key, ctrl_cfg_dict, config, gains, dynamics_model, shared_dt, shared_max_force, allow_unknown)`

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: _build_swing_up_smc
:linenos:
```



### `_build_hybrid_adaptive_sta_smc(key, ctrl_cfg_dict, config, gains, dynamics_model, shared_dt, shared_max_force, allow_unknown)`

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: _build_hybrid_adaptive_sta_smc
:linenos:
```



### `_build_mpc_controller(key, ctrl_cfg_dict, config, gains, shared_dt, shared_max_force, allow_unknown)`

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: _build_mpc_controller
:linenos:
```



### `create_controller()`

Backwards-compatible convenience wrapper used by tests and the CLI.
Delegates to build_controller() so mapping/validation stays centralized.

Parameters
name : str
    Controller name (aliases allowed).
**kwargs :
    Per-controller constructor args (e.g., gains, dt, max_force).

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: create_controller
:linenos:
```



### `_canonical(name)`

Legacy/compat alias for tests. Mirrors normalize_controller_name().

#### Source Code

```{literalinclude} ../../../src/controllers/factory/legacy_factory.py
:language: python
:pyobject: _canonical
:linenos:
```



## Dependencies

This module imports:

- `import logging`
- `import math`
- `import threading`
- `import warnings`
- `from collections.abc import MutableMapping`
- `from typing import Optional, List, Any, Dict, Callable, Union, Type, Mapping`
- `import numpy as np`
- `import numbers`
