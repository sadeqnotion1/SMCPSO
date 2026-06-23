# config.schemas

**Source:** `src\config\schemas.py`

## Module Overview

Configuration schemas and models for the DIP SMC PSO project.

## Complete Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:linenos:
```



## Classes

### `StrictModel`

**Inherits from:** `BaseModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: StrictModel
:linenos:
```



### `PhysicsConfig`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: PhysicsConfig
:linenos:
```

#### Methods (2)

##### `_must_be_strictly_positive(cls, v, info)`

[View full source →](#method-physicsconfig-_must_be_strictly_positive)

##### `_validate_com_within_length(self)`

[View full source →](#method-physicsconfig-_validate_com_within_length)



### `PhysicsUncertaintySchema`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: PhysicsUncertaintySchema
:linenos:
```



### `SimulationConfig`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: SimulationConfig
:linenos:
```

#### Methods (3)

##### `_must_be_positive(cls, v, info)`

[View full source →](#method-simulationconfig-_must_be_positive)

##### `_duration_at_least_dt(self)`

[View full source →](#method-simulationconfig-_duration_at_least_dt)

##### `_initial_state_valid(cls, v)`

[View full source →](#method-simulationconfig-_initial_state_valid)



### `_BaseControllerConfig`

**Inherits from:** `BaseModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: _BaseControllerConfig
:linenos:
```

#### Methods (1)

##### `__iter__(self)`

[View full source →](#method-_basecontrollerconfig-__iter__)



### `ControllerConfig`

**Inherits from:** `_BaseControllerConfig`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: ControllerConfig
:linenos:
```



### `ClassicalSMCConfig`

**Inherits from:** `_BaseControllerConfig`

Configuration for Classical Sliding Mode Controller.

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: ClassicalSMCConfig
:linenos:
```



### `STASMCConfig`

**Inherits from:** `_BaseControllerConfig`

Configuration for Super-Twisting Algorithm Sliding Mode Controller.

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: STASMCConfig
:linenos:
```



### `AdaptiveSMCConfig`

**Inherits from:** `_BaseControllerConfig`

Configuration for Adaptive Sliding Mode Controller.

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: AdaptiveSMCConfig
:linenos:
```

#### Methods (1)

##### `_validate_adaptive_bounds(self)`

[View full source →](#method-adaptivesmcconfig-_validate_adaptive_bounds)



### `SwingUpSMCConfig`

**Inherits from:** `_BaseControllerConfig`

Configuration for Swing-Up Sliding Mode Controller.

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: SwingUpSMCConfig
:linenos:
```



### `HybridAdaptiveSTASMCConfig`

**Inherits from:** `_BaseControllerConfig`

Configuration for Hybrid Adaptive Super-Twisting Sliding Mode Controller.

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: HybridAdaptiveSTASMCConfig
:linenos:
```

#### Methods (1)

##### `_validate_hybrid_constraints(self)`

[View full source →](#method-hybridadaptivestasmcconfig-_validate_hybrid_constraints)



### `PermissiveControllerConfig`

**Inherits from:** `_BaseControllerConfig`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: PermissiveControllerConfig
:linenos:
```

#### Methods (1)

##### `_collect_unknown_params(self)`

[View full source →](#method-permissivecontrollerconfig-_collect_unknown_params)



### `ControllersConfig`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: ControllersConfig
:linenos:
```

#### Methods (4)

##### `keys(self)`

[View full source →](#method-controllersconfig-keys)

##### `__iter__(self)`

[View full source →](#method-controllersconfig-__iter__)

##### `items(self)`

[View full source →](#method-controllersconfig-items)

##### `__getitem__(self, key)`

[View full source →](#method-controllersconfig-__getitem__)



### `PSOBounds`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: PSOBounds
:linenos:
```



### `PSOBoundsWithControllers`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: PSOBoundsWithControllers
:linenos:
```



### `PSOConfig`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: PSOConfig
:linenos:
```



### `CostFunctionWeights`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: CostFunctionWeights
:linenos:
```



### `CombineWeights`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: CombineWeights
:linenos:
```



### `CostFunctionConfig`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: CostFunctionConfig
:linenos:
```



### `VerificationConfig`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: VerificationConfig
:linenos:
```



### `SensorsConfig`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: SensorsConfig
:linenos:
```



### `HILConfig`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: HILConfig
:linenos:
```



### `FDIConfig`

**Inherits from:** `StrictModel`

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: FDIConfig
:linenos:
```

#### Methods (2)

##### `_validate_residual_states(cls, v)`

[View full source →](#method-fdiconfig-_validate_residual_states)

##### `_validate_weights_length(self)`

[View full source →](#method-fdiconfig-_validate_weights_length)



### `LDRConfig`

**Inherits from:** `StrictModel`

Lyapunov Decrease Ratio monitoring configuration.

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: LDRConfig
:linenos:
```



### `SaturationConfig`

**Inherits from:** `StrictModel`

Saturation monitoring configuration.

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: SaturationConfig
:linenos:
```



### `ConditioningConfig`

**Inherits from:** `StrictModel`

Dynamics conditioning monitoring configuration.

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: ConditioningConfig
:linenos:
```



### `DiagnosticsConfig`

**Inherits from:** `StrictModel`

Diagnostic checklist configuration.

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: DiagnosticsConfig
:linenos:
```



### `StabilityMonitoringConfig`

**Inherits from:** `StrictModel`

Stability monitoring configuration for Issue #1 resolution.

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: StabilityMonitoringConfig
:linenos:
```



### `FaultDetectionConfig`

**Inherits from:** `StrictModel`

Fault Detection and Isolation (FDI) configuration - Issue #18 resolution.

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: FaultDetectionConfig
:linenos:
```



## Functions

### `redact_value(value)`

Redact sensitive values for logging.

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: redact_value
:linenos:
```



### `set_allow_unknown_config(_)`

Deprecated - use load_config(..., allow_unknown=True) instead.

#### Source Code

```{literalinclude} ../../../src/config/schemas.py
:language: python
:pyobject: set_allow_unknown_config
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from pathlib import Path`
- `from types import SimpleNamespace`
- `from typing import Any, Dict, List, Optional, Tuple, Type`
- `from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator`
