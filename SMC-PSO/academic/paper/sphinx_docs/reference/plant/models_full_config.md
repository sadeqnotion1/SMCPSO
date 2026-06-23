# plant.models.full.config

**Source:** `src\plant\models\full\config.py`

## Module Overview

Configuration for Full Fidelity DIP Dynamics.

Type-safe configuration for the high-fidelity double inverted pendulum model
with complete nonlinear dynamics, coupling effects, and advanced numerical
integration features.

## Complete Source Code

```{literalinclude} ../../../src/plant/models/full/config.py
:language: python
:linenos:
```



## Classes

### `FullDIPConfig`

Type-safe configuration for full-fidelity DIP dynamics.

High-Fidelity Features:
- Complete nonlinear dynamics with all coupling terms
- Advanced friction models (viscous + Coulomb)
- Flexible joint constraints and limits
- High-precision numerical integration
- Wind/disturbance modeling capability

#### Source Code

```{literalinclude} ../../../src/plant/models/full/config.py
:language: python
:pyobject: FullDIPConfig
:linenos:
```

#### Methods (13)

##### `__post_init__(self)`

Validate configuration after creation.

[View full source →](#method-fulldipconfig-__post_init__)

##### `_validate_physical_parameters(self)`

Validate physical parameters for high-fidelity model.

[View full source →](#method-fulldipconfig-_validate_physical_parameters)

##### `_validate_numerical_parameters(self)`

Validate numerical parameters for high-fidelity integration.

[View full source →](#method-fulldipconfig-_validate_numerical_parameters)

##### `_validate_advanced_features(self)`

Validate advanced feature combinations.

[View full source →](#method-fulldipconfig-_validate_advanced_features)

##### `create_high_fidelity(cls)`

Create high-fidelity configuration with realistic parameters.

[View full source →](#method-fulldipconfig-create_high_fidelity)

##### `create_research_grade(cls)`

Create research-grade configuration with aerodynamics and disturbances.

[View full source →](#method-fulldipconfig-create_research_grade)

##### `to_dict(self)`

Convert configuration to dictionary.

[View full source →](#method-fulldipconfig-to_dict)

##### `get_complexity_level(self)`

Get complexity level description.

[View full source →](#method-fulldipconfig-get_complexity_level)

##### `cart_friction(self)`

Get cart friction coefficient (alias for viscous friction).

[View full source →](#method-fulldipconfig-cart_friction)

##### `joint1_friction(self)`

Get joint 1 friction coefficient (alias for viscous friction).

[View full source →](#method-fulldipconfig-joint1_friction)

##### `joint2_friction(self)`

Get joint 2 friction coefficient (alias for viscous friction).

[View full source →](#method-fulldipconfig-joint2_friction)

##### `create_default(cls)`

Create default full DIP configuration.

[View full source →](#method-fulldipconfig-create_default)

##### `from_dict(cls, config_dict)`

Create configuration from dictionary with parameter mapping.

[View full source →](#method-fulldipconfig-from_dict)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Optional, Dict, Any, List`
- `from dataclasses import dataclass, field`
- `import numpy as np`
