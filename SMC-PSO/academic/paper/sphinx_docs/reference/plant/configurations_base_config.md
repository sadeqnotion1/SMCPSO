# plant.configurations.base_config

**Source:** `src\plant\configurations\base_config.py`

## Module Overview

Base Configuration Classes for Plant Dynamics.

Provides abstract base classes and common functionality for physics
configuration with validation and type safety.

## Complete Source Code

```{literalinclude} ../../../src/plant/configurations/base_config.py
:language: python
:linenos:
```



## Classes

### `PhysicsConfig`

**Inherits from:** `Protocol`

Protocol for physics configuration classes.

#### Source Code

```{literalinclude} ../../../src/plant/configurations/base_config.py
:language: python
:pyobject: PhysicsConfig
:linenos:
```

#### Methods (3)

##### `validate(self)`

Validate physics parameters.

[View full source →](#method-physicsconfig-validate)

##### `to_dict(self)`

Convert to dictionary.

[View full source →](#method-physicsconfig-to_dict)

##### `from_dict(cls, config_dict)`

Create from dictionary.

[View full source →](#method-physicsconfig-from_dict)



### `BasePhysicsConfig`

**Inherits from:** `ABC`

Abstract base class for physics configurations.

Provides common functionality for validation, serialization,
and parameter management across different physics models.

#### Source Code

```{literalinclude} ../../../src/plant/configurations/base_config.py
:language: python
:pyobject: BasePhysicsConfig
:linenos:
```

#### Methods (13)

##### `validate(self)`

Validate physics parameters for consistency and physical realizability.

[View full source →](#method-basephysicsconfig-validate)

##### `get_physical_parameters(self)`

Get dictionary of physical parameters.

[View full source →](#method-basephysicsconfig-get_physical_parameters)

##### `get_numerical_parameters(self)`

Get dictionary of numerical parameters.

[View full source →](#method-basephysicsconfig-get_numerical_parameters)

##### `to_dict(self)`

Convert configuration to dictionary.

[View full source →](#method-basephysicsconfig-to_dict)

##### `from_dict(cls, config_dict)`

Create configuration from dictionary.

[View full source →](#method-basephysicsconfig-from_dict)

##### `create_default(cls)`

Create configuration with default parameters.

[View full source →](#method-basephysicsconfig-create_default)

##### `get_mass_properties(self)`

Get mass-related parameters.

[View full source →](#method-basephysicsconfig-get_mass_properties)

##### `get_length_properties(self)`

Get length-related parameters.

[View full source →](#method-basephysicsconfig-get_length_properties)

##### `get_inertia_properties(self)`

Get inertia-related parameters.

[View full source →](#method-basephysicsconfig-get_inertia_properties)

##### `get_friction_properties(self)`

Get friction-related parameters.

[View full source →](#method-basephysicsconfig-get_friction_properties)

##### `estimate_characteristic_scales(self)`

Estimate characteristic scales for the system.

[View full source →](#method-basephysicsconfig-estimate_characteristic_scales)

##### `check_physical_consistency(self)`

Check physical consistency of parameters.

[View full source →](#method-basephysicsconfig-check_physical_consistency)

##### `get_dimensionless_parameters(self)`

Compute dimensionless parameter groups.

[View full source →](#method-basephysicsconfig-get_dimensionless_parameters)



### `BaseDIPConfig`

**Inherits from:** `BasePhysicsConfig`

Base configuration class for Double Inverted Pendulum models.

Provides common interface and validation for all DIP implementations
(simplified, full, low-rank) with essential physical parameters.

#### Source Code

```{literalinclude} ../../../src/plant/configurations/base_config.py
:language: python
:pyobject: BaseDIPConfig
:linenos:
```

#### Methods (8)

##### `__post_init__(self)`

Post-initialization validation.

[View full source →](#method-basedipconfig-__post_init__)

##### `validate(self)`

Validate DIP configuration parameters.

[View full source →](#method-basedipconfig-validate)

##### `get_physical_parameters(self)`

Get dictionary of physical parameters.

[View full source →](#method-basedipconfig-get_physical_parameters)

##### `get_numerical_parameters(self)`

Get dictionary of numerical parameters.

[View full source →](#method-basedipconfig-get_numerical_parameters)

##### `from_dict(cls, config_dict)`

Create configuration from dictionary.

[View full source →](#method-basedipconfig-from_dict)

##### `create_default(cls)`

Create configuration with default parameters.

[View full source →](#method-basedipconfig-create_default)

##### `check_physical_consistency(self)`

Check physical consistency of DIP parameters.

[View full source →](#method-basedipconfig-check_physical_consistency)

##### `get_system_scales(self)`

Get characteristic scales for the DIP system.

[View full source →](#method-basedipconfig-get_system_scales)



### `ConfigurationError`

**Inherits from:** `ValueError`

Raised when configuration validation fails.

#### Source Code

```{literalinclude} ../../../src/plant/configurations/base_config.py
:language: python
:pyobject: ConfigurationError
:linenos:
```



### `ConfigurationWarning`

**Inherits from:** `UserWarning`

Issued when configuration parameters are unusual but valid.

#### Source Code

```{literalinclude} ../../../src/plant/configurations/base_config.py
:language: python
:pyobject: ConfigurationWarning
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Dict, Any, Optional, Protocol`
- `from abc import ABC, abstractmethod`
- `from dataclasses import dataclass`
- `import numpy as np`
