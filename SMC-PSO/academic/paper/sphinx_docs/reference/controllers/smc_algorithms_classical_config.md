# controllers.smc.algorithms.classical.config

**Source:** `src\controllers\smc\algorithms\classical\config.py`

## Module Overview

Configuration Schema for Classical SMC.

Type-safe configuration using Pydantic with validation rules based on SMC theory.
Replaces parameter validation scattered throughout the original 458-line controller.

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/classical/config.py
:language: python
:linenos:
```



## Classes

### `ClassicalSMCConfig`

Type-safe configuration for Classical SMC controller.

Based on SMC theory requirements:
- Surface gains [k1, k2, λ1, λ2] must be positive for Hurwitz stability
- Switching gain K must be positive for reaching condition
- Derivative gain kd must be non-negative for damping

#### Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/classical/config.py
:language: python
:pyobject: ClassicalSMCConfig
:linenos:
```

#### Methods (14)

##### `__post_init__(self)`

Validate configuration after creation.

[View full source →](#method-classicalsmcconfig-__post_init__)

##### `_validate_gains(self)`

Validate gain vector according to SMC theory.

[View full source →](#method-classicalsmcconfig-_validate_gains)

##### `_validate_parameters(self)`

Validate other configuration parameters.

[View full source →](#method-classicalsmcconfig-_validate_parameters)

##### `k1(self)`

Joint 1 position gain.

[View full source →](#method-classicalsmcconfig-k1)

##### `k2(self)`

Joint 2 position gain.

[View full source →](#method-classicalsmcconfig-k2)

##### `lam1(self)`

Joint 1 velocity gain (λ₁).

[View full source →](#method-classicalsmcconfig-lam1)

##### `lam2(self)`

Joint 2 velocity gain (λ₂).

[View full source →](#method-classicalsmcconfig-lam2)

##### `K(self)`

Switching gain.

[View full source →](#method-classicalsmcconfig-k)

##### `kd(self)`

Derivative gain.

[View full source →](#method-classicalsmcconfig-kd)

##### `get_surface_gains(self)`

Get sliding surface gains [k1, k2, λ1, λ2].

[View full source →](#method-classicalsmcconfig-get_surface_gains)

##### `get_effective_controllability_threshold(self)`

Get effective controllability threshold.

[View full source →](#method-classicalsmcconfig-get_effective_controllability_threshold)

##### `to_dict(self)`

Convert configuration to dictionary.

[View full source →](#method-classicalsmcconfig-to_dict)

##### `from_dict(cls, config_dict, dynamics_model)`

Create configuration from dictionary.

[View full source →](#method-classicalsmcconfig-from_dict)

##### `create_default(cls, gains, max_force, dt, boundary_layer)`

Create configuration with sensible defaults.

[View full source →](#method-classicalsmcconfig-create_default)



## Dependencies

This module imports:

- `from typing import List, Optional, Literal`
- `from dataclasses import dataclass, field`
- `from pydantic import BaseModel, Field, validator`
- `import numpy as np`
