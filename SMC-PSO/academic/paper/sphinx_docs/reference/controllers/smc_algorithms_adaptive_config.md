# controllers.smc.algorithms.adaptive.config

**Source:** `src\controllers\smc\algorithms\adaptive\config.py`

## Module Overview

Configuration Schema for Adaptive SMC.

Type-safe configuration for Adaptive Sliding Mode Control with online gain adaptation.
Replaces parameter validation from the original 427-line monolithic controller.

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/adaptive/config.py
:language: python
:linenos:
```



## Classes

### `AdaptiveSMCConfig`

Type-safe configuration for Adaptive SMC controller.

Based on adaptive SMC theory:
- Surface gains [k1, k2, λ1, λ2] must be positive for Hurwitz stability
- Adaptation rate γ must be positive but bounded for stability
- Adaptation bounds [K_min, K_max] ensure bounded gains

#### Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/adaptive/config.py
:language: python
:pyobject: AdaptiveSMCConfig
:linenos:
```

#### Methods (18)

##### `__post_init__(self)`

Validate configuration after creation.

[View full source →](#method-adaptivesmcconfig-__post_init__)

##### `_validate_gains(self)`

Validate gain vector according to adaptive SMC theory.

[View full source →](#method-adaptivesmcconfig-_validate_gains)

##### `_validate_adaptation_parameters(self)`

Validate adaptation-specific parameters.

[View full source →](#method-adaptivesmcconfig-_validate_adaptation_parameters)

##### `_validate_other_parameters(self)`

Validate other configuration parameters.

[View full source →](#method-adaptivesmcconfig-_validate_other_parameters)

##### `k1(self)`

Joint 1 position gain.

[View full source →](#method-adaptivesmcconfig-k1)

##### `k2(self)`

Joint 2 position gain.

[View full source →](#method-adaptivesmcconfig-k2)

##### `lam1(self)`

Joint 1 velocity gain (λ₁).

[View full source →](#method-adaptivesmcconfig-lam1)

##### `lam2(self)`

Joint 2 velocity gain (λ₂).

[View full source →](#method-adaptivesmcconfig-lam2)

##### `gamma(self)`

Adaptation rate (γ).

[View full source →](#method-adaptivesmcconfig-gamma)

##### `adaptation_rate(self)`

Adaptation rate for compatibility.

[View full source →](#method-adaptivesmcconfig-adaptation_rate)

##### `adaptation_rate_array(self)`

Adaptation rate as array for 3-DOF system.

[View full source →](#method-adaptivesmcconfig-adaptation_rate_array)

##### `uncertainty_bound(self)`

Uncertainty bound for adaptation law.

[View full source →](#method-adaptivesmcconfig-uncertainty_bound)

##### `initial_estimates(self)`

Initial uncertainty estimates.

[View full source →](#method-adaptivesmcconfig-initial_estimates)

##### `get_surface_gains(self)`

Get sliding surface gains [k1, k2, λ1, λ2].

[View full source →](#method-adaptivesmcconfig-get_surface_gains)

##### `get_adaptation_bounds(self)`

Get adaptation bounds (K_min, K_max).

[View full source →](#method-adaptivesmcconfig-get_adaptation_bounds)

##### `to_dict(self)`

Convert configuration to dictionary.

[View full source →](#method-adaptivesmcconfig-to_dict)

##### `from_dict(cls, config_dict)`

Create configuration from dictionary.

[View full source →](#method-adaptivesmcconfig-from_dict)

##### `create_default(cls, gains, max_force, dt)`

Create configuration with sensible defaults.

[View full source →](#method-adaptivesmcconfig-create_default)



## Dependencies

This module imports:

- `from typing import List, Optional`
- `from dataclasses import dataclass, field`
- `import numpy as np`
