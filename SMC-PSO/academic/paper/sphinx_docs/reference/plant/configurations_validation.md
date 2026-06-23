# plant.configurations.validation

**Source:** `src\plant\configurations\validation.py`

## Module Overview Parameter

Validation for Plant Configurations

. validation utilities for physics parameters ensuring


mathematical correctness, physical realizability, and numerical stability. ## Complete Source Code ```{literalinclude} ../../../src/plant/configurations/validation.py
:language: python
:linenos:
```

---

## Classes

### `ParameterValidator`

**Inherits from:** `Protocol` Protocol for parameter validation strategies.

#### Source Code ```

{literalinclude} ../../../src/plant/configurations/validation.py
:language: python
:pyobject: ParameterValidator
:linenos:
``` #### Methods (2) ##### `validate_parameter(self, name, value)` Validate a single parameter. [View full source →](#method-parametervalidator-validate_parameter) ##### `validate_parameters(self, params)` Validate multiple parameters, return list of errors. [View full source →](#method-parametervalidator-validate_parameters)

---

## `PhysicsParameterValidator`

validator for physics parameters. Provides validation for common physics parameter types with

appropriate bounds checking and consistency verification. #### Source Code ```{literalinclude} ../../../src/plant/configurations/validation.py
:language: python
:pyobject: PhysicsParameterValidator
:linenos:
``` #### Methods (12) ##### `__init__(self, strict_mode, warn_on_unusual)` Initialize parameter validator. [View full source →](#method-physicsparametervalidator-__init__) ##### `validate_mass(self, name, mass)` Validate mass parameter. [View full source →](#method-physicsparametervalidator-validate_mass) ##### `validate_length(self, name, length)` Validate length parameter. [View full source →](#method-physicsparametervalidator-validate_length) ##### `validate_inertia(self, name, inertia)` Validate moment of inertia parameter. [View full source →](#method-physicsparametervalidator-validate_inertia) ##### `validate_friction(self, name, friction)` Validate friction coefficient. [View full source →](#method-physicsparametervalidator-validate_friction) ##### `validate_gravity(self, gravity)` Validate gravity parameter. [View full source →](#method-physicsparametervalidator-validate_gravity) ##### `validate_numerical_parameter(self, name, value, min_value, max_value)` Validate generic numerical parameter with bounds. [View full source →](#method-physicsparametervalidator-validate_numerical_parameter) ##### `validate_geometric_consistency(self, pendulum_length, com_distance, pendulum_name)` Validate geometric consistency between pendulum length and COM. [View full source →](#method-physicsparametervalidator-validate_geometric_consistency) ##### `validate_inertia_consistency(self, mass, length, com_distance, inertia, pendulum_name)` Validate inertia consistency with geometry. [View full source →](#method-physicsparametervalidator-validate_inertia_consistency) ##### `validate_mass_distribution(self, cart_mass, pendulum_masses)` Validate mass distribution for dynamic stability. [View full source →](#method-physicsparametervalidator-validate_mass_distribution) ##### `validate_system_parameters(self, params)` Validate complete system parameter set. [View full source →](#method-physicsparametervalidator-validate_system_parameters) ##### `_setup_validation_rules(self)` Setup validation rules and bounds. [View full source →](#method-physicsparametervalidator-_setup_validation_rules)

---

## Functions

### `validate_physics_parameters(params, strict_mode)`

Convenience function for physics parameter validation. Args: params: Dictionary of parameters to validate strict_mode: Raise exceptions for warnings if True Returns: Tuple of (is_valid, error_messages)

#### Source Code ```

{literalinclude} ../../../src/plant/configurations/validation.py
:language: python
:pyobject: validate_physics_parameters
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`

- `from typing import Dict, Any, List, Tuple, Optional, Protocol`
- `import numpy as np`
- `import warnings`
- `from .base_config import ConfigurationError, ConfigurationWarning`
