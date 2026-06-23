# controllers.factory

**Source:** `src\controllers\factory.py`

## Module Overview Enterprise

Controller Factory - Production-Ready Controller Instantiation This module provides a factory pattern for instantiating different types


of controllers with proper configuration, parameter management, and enterprise-grade
quality standards. Architecture:
- Modular design with clean separation of concerns
- Thread-safe operations with locking
- Type-safe interfaces with 95%+ type hint coverage
- Configuration validation with deprecation handling
- PSO optimization integration
- error handling and logging Supported Controllers:
- Classical SMC: Sliding mode control with boundary layer
- Super-Twisting SMC: Higher-order sliding mode algorithm
- Adaptive SMC: Online parameter adaptation
- Hybrid Adaptive-STA SMC: Combined adaptive and super-twisting
- MPC Controller: Model predictive control (optional) ## Complete Source Code ```{literalinclude} ../../../src/controllers/factory.py
:language: python
:linenos:
```

---

## Classes

### `ConfigValueError`

**Inherits from:** `ValueError` Exception raised for invalid configuration values.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: ConfigValueError
:linenos:
```

---

## `ControllerProtocol`

**Inherits from:** `Protocol` Protocol defining the standard controller interface.

### Source Code ```

{literalinclude} ../../../src/controllers/factory.py

:language: python
:pyobject: ControllerProtocol
:linenos:
``` #### Methods (3) ##### `compute_control(self, state, last_control, history)` Compute control output for given state. [View full source →](#method-controllerprotocol-compute_control) ##### `reset(self)` Reset controller internal state. [View full source →](#method-controllerprotocol-reset) ##### `gains(self)` Return controller gains. [View full source →](#method-controllerprotocol-gains)

### `SMCType`

**Inherits from:** `Enum` SMC Controller types enumeration.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: SMCType
:linenos:
```

### `SMCConfig`

Configuration class for SMC controllers.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py

:language: python
:pyobject: SMCConfig
:linenos:
``` #### Methods (1) ##### `__init__(self, gains, max_force, dt)` [View full source →](#method-smcconfig-__init__)

### `SMCFactory`

Factory class for creating SMC controllers.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: SMCFactory
:linenos:
``` #### Methods (1) ##### `create_controller(smc_type, config)` Create controller using SMCType enum. [View full source →](#method-smcfactory-create_controller)

### `PSOControllerWrapper`

Wrapper for SMC controllers to provide PSO-compatible interface.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py

:language: python
:pyobject: PSOControllerWrapper
:linenos:
``` #### Methods (4) ##### `__init__(self, controller, n_gains, controller_type)` [View full source →](#method-psocontrollerwrapper-__init__) ##### `_add_step_method_to_dynamics(self)` Add step method to dynamics model for simulation compatibility. [View full source →](#method-psocontrollerwrapper-_add_step_method_to_dynamics) ##### `validate_gains(self, particles)` Validate gain particles for PSO optimization. [View full source →](#method-psocontrollerwrapper-validate_gains) ##### `compute_control(self, state)` PSO-compatible control computation interface. [View full source →](#method-psocontrollerwrapper-compute_control)

### `SMCGainSpec`

SMC gain specification with expected interface.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: SMCGainSpec
:linenos:
``` #### Methods (1) ##### `__init__(self, gain_names, gain_bounds, controller_type, n_gains)` [View full source →](#method-smcgainspec-__init__)

---

## Functions

### `_canonicalize_controller_type(name)`

Normalize and alias controller type names. Args: name: Controller type name to normalize Returns: Canonical controller type name Raises: ValueError: If name is not a string or is empty

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py

:language: python
:pyobject: _canonicalize_controller_type
:linenos:
```

### `_get_controller_info(controller_type)`

Get controller information from registry with validation. Args: controller_type: Canonical controller type name Returns: Controller registry information Raises: ValueError: If controller type is not recognized ImportError: If controller type is recognized but unavailable due to missing dependencies

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: _get_controller_info
:linenos:
```

### `_resolve_controller_gains(gains, config, controller_type, controller_info)`

Resolve controller gains from multiple sources. Args: gains: Explicitly provided gains config: Configuration object controller_type: Controller type name controller_info: Controller registry information Returns: Resolved gains list

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py

:language: python
:pyobject: _resolve_controller_gains
:linenos:
```

### `_validate_controller_gains(gains, controller_info, controller_type)`

Validate controller gains with controller-specific rules. Args: gains: Controller gains to validate controller_info: Controller registry information controller_type: Type of controller for specific validation Raises: ValueError: If gains are invalid

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: _validate_controller_gains
:linenos:
```

### `_create_dynamics_model(config)`

Create dynamics model from configuration. Args: config: Configuration object Returns: Dynamics model instance or None

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py

:language: python
:pyobject: _create_dynamics_model
:linenos:
```

### `_extract_controller_parameters(config, controller_type, controller_info)`

Extract controller-specific parameters from configuration. Args: config: Configuration object controller_type: Controller type name controller_info: Controller registry information Returns: Dictionary of controller parameters

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: _extract_controller_parameters
:linenos:
```

### `_validate_mpc_parameters(config_params, controller_params)`

Validate MPC controller parameters. Args: config_params: Main configuration parameters controller_params: Controller-specific parameters Raises: ConfigValueError: If any parameter is invalid

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py

:language: python
:pyobject: _validate_mpc_parameters
:linenos:
```

### `create_controller(controller_type, config, gains)`

Create a controller instance of the specified type. This function is thread-safe and can be called concurrently from multiple threads. Args: controller_type: Type of controller ('classical_smc', 'sta_smc', etc.) config: Configuration object (optional) gains: Controller gains array (optional) Returns: Configured controller instance Raises: ValueError: If controller_type is not recognized ImportError: If required dependencies are missing

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: create_controller
:linenos:
```

### `list_available_controllers()`

Get list of available controller types. Returns: List of controller type names that can actually be instantiated

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py

:language: python
:pyobject: list_available_controllers
:linenos:
```

### `list_all_controllers()`

Get list of all registered controller types, including unavailable ones. Returns: List of all controller type names in the registry

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: list_all_controllers
:linenos:
```

### `get_default_gains(controller_type)`

Get default gains for a controller type. Args: controller_type: Type of controller Returns: Default gains list Raises: ValueError: If controller_type is not recognized

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py

:language: python
:pyobject: get_default_gains
:linenos:
```

### `create_classical_smc_controller(config, gains)`

Create classical SMC controller (backwards compatibility).

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: create_classical_smc_controller
:linenos:
```

### `create_sta_smc_controller(config, gains)`

Create super-twisting SMC controller (backwards compatibility).

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py

:language: python
:pyobject: create_sta_smc_controller
:linenos:
```

### `create_adaptive_smc_controller(config, gains)`

Create adaptive SMC controller (backwards compatibility).

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: create_adaptive_smc_controller
:linenos:
```

### `create_controller_legacy(controller_type, config, gains)`

Legacy factory function (backwards compatibility).

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py

:language: python
:pyobject: create_controller_legacy
:linenos:
```

### `create_smc_for_pso(smc_type, gains, plant_config_or_model)`

Create SMC controller optimized for PSO usage.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: create_smc_for_pso
:linenos:
```

### `create_pso_controller_factory(smc_type, plant_config)`

Create a PSO-optimized controller factory function with required attributes.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py

:language: python
:pyobject: create_pso_controller_factory
:linenos:
```

### `get_expected_gain_count(smc_type)`

Get expected number of gains for a controller type.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: get_expected_gain_count
:linenos:
```

### `get_gain_bounds_for_pso(smc_type)`

Get PSO gain bounds for a controller type. Returns: Tuple of (lower_bounds, upper_bounds) lists

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py

:language: python
:pyobject: get_gain_bounds_for_pso
:linenos:
```

### `validate_smc_gains(smc_type, gains)`

Validate gains for a controller type.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory.py
:language: python
:pyobject: validate_smc_gains
:linenos:
```

---

## Dependencies This module imports: - `import logging`

- `import threading`
- `from enum import Enum`
- `from typing import Any, Callable, Dict, List, Optional, Tuple, Union, Protocol, TypeVar`
- `from dataclasses import dataclass`
- `from abc import ABC, abstractmethod`
- `import numpy as np`
- `from numpy.typing import NDArray`
- `from src.core.dynamics import DIPDynamics`
- `from src.controllers.smc.algorithms.classical.controller import ModularClassicalSMC` *... and 8 more*
