# controllers.factory.fallback_configs

**Source:** `src\controllers\factory\fallback_configs.py`

## Module Overview

Fallback configuration classes for SMC controllers.

Provides minimal working configuration classes when the full implementation
config classes are not available. These ensure graceful degradation of the factory.

## Complete Source Code

```{literalinclude} ../../../src/controllers/factory/fallback_configs.py
:language: python
:linenos:
```



## Classes

### `ClassicalSMCConfig`

Fallback minimal configuration for Classical SMC controller.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/fallback_configs.py
:language: python
:pyobject: ClassicalSMCConfig
:linenos:
```

#### Methods (2)

##### `get_surface_gains(self)`

Get sliding surface gains [k1, k2, λ1, λ2].

[View full source →](#method-classicalsmcconfig-get_surface_gains)

##### `get_effective_controllability_threshold(self)`

Get effective controllability threshold.

[View full source →](#method-classicalsmcconfig-get_effective_controllability_threshold)



### `STASMCConfig`

Fallback minimal configuration for Super-Twisting SMC controller.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/fallback_configs.py
:language: python
:pyobject: STASMCConfig
:linenos:
```

#### Methods (2)

##### `get_surface_gains(self)`

Get sliding surface gains [k1, k2, λ1, λ2].

[View full source →](#method-stasmcconfig-get_surface_gains)

##### `get_effective_anti_windup_gain(self)`

Get effective anti-windup gain.

[View full source →](#method-stasmcconfig-get_effective_anti_windup_gain)



### `AdaptiveSMCConfig`

Fallback minimal configuration for Adaptive SMC controller.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/fallback_configs.py
:language: python
:pyobject: AdaptiveSMCConfig
:linenos:
```

#### Methods (2)

##### `get_surface_gains(self)`

Get sliding surface gains [k1, k2, λ1, λ2].

[View full source →](#method-adaptivesmcconfig-get_surface_gains)

##### `get_adaptation_bounds(self)`

Get adaptation bounds (K_min, K_max).

[View full source →](#method-adaptivesmcconfig-get_adaptation_bounds)



### `HybridAdaptiveSTASMCConfig`

Fallback minimal configuration for Hybrid Adaptive STA-SMC controller.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/fallback_configs.py
:language: python
:pyobject: HybridAdaptiveSTASMCConfig
:linenos:
```

#### Methods (1)

##### `get_surface_gains(self)`

Get sliding surface gains [k1, k2, λ1, λ2].

[View full source →](#method-hybridadaptivestasmcconfig-get_surface_gains)



## Dependencies

This module imports:

- `from dataclasses import dataclass`
- `from typing import Any, List`
