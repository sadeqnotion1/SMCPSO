# plant.models.lowrank.config

**Source:** `src\plant\models\lowrank\config.py`

## Module Overview

Low-rank DIP Configuration.

Simplified configuration with reduced parameters optimized for computational
efficiency while maintaining essential system characteristics.

## Complete Source Code

```{literalinclude} ../../../src/plant/models/lowrank/config.py
:language: python
:linenos:
```



## Classes

### `LowRankDIPConfig`

**Inherits from:** `BaseDIPConfig`

Configuration for Low-rank Double Inverted Pendulum Model.

Simplified configuration that captures essential dynamics while reducing
computational complexity. Uses representative parameters rather than
full nonlinear effects.

#### Source Code

```{literalinclude} ../../../src/plant/models/lowrank/config.py
:language: python
:pyobject: LowRankDIPConfig
:linenos:
```

#### Methods (12)

##### `__post_init__(self)`

Post-initialization validation and derived parameter computation.

[View full source →](#method-lowrankdipconfig-__post_init__)

##### `_validate_physical_parameters(self)`

Validate simplified physical parameters.

[View full source →](#method-lowrankdipconfig-_validate_physical_parameters)

##### `_compute_derived_parameters(self)`

Compute derived parameters for low-rank dynamics.

[View full source →](#method-lowrankdipconfig-_compute_derived_parameters)

##### `_setup_physics_constants(self)`

Setup simplified physics constants for efficient computation.

[View full source →](#method-lowrankdipconfig-_setup_physics_constants)

##### `get_linearized_matrices(self, equilibrium_point)`

Get linearized system matrices around equilibrium point.

[View full source →](#method-lowrankdipconfig-get_linearized_matrices)

##### `_get_upright_linearization(self)`

Get linearization around upright equilibrium.

[View full source →](#method-lowrankdipconfig-_get_upright_linearization)

##### `_get_downward_linearization(self)`

Get linearization around downward equilibrium (stable).

[View full source →](#method-lowrankdipconfig-_get_downward_linearization)

##### `to_dict(self)`

Convert configuration to dictionary.

[View full source →](#method-lowrankdipconfig-to_dict)

##### `from_dict(cls, config_dict)`

Create configuration from dictionary.

[View full source →](#method-lowrankdipconfig-from_dict)

##### `create_default(cls)`

Create default configuration.

[View full source →](#method-lowrankdipconfig-create_default)

##### `create_fast_prototype(cls)`

Create configuration optimized for fast prototyping.

[View full source →](#method-lowrankdipconfig-create_fast_prototype)

##### `create_educational(cls)`

Create configuration for educational purposes.

[View full source →](#method-lowrankdipconfig-create_educational)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Optional, Tuple, Dict, Any`
- `from dataclasses import dataclass, field`
- `import numpy as np`
- `from ...configurations.base_config import BaseDIPConfig`
