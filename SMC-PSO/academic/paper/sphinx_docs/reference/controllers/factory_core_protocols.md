# controllers.factory.core.protocols

**Source:** `src\controllers\factory\core\protocols.py`

## Module Overview

Core Protocols and Interfaces for Controller Factory

Defines the fundamental protocols and interfaces that all controllers and factory
components must adhere to for type safety and consistency.

## Complete Source Code

```{literalinclude} ../../../src/controllers/factory/core/protocols.py
:language: python
:linenos:
```



## Classes

### `ControllerProtocol`

**Inherits from:** `Protocol`

Protocol defining the standard controller interface.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/protocols.py
:language: python
:pyobject: ControllerProtocol
:linenos:
```

#### Methods (4)

##### `compute_control(self, state, last_control, history)`

Compute control output for given state.

[View full source →](#method-controllerprotocol-compute_control)

##### `reset(self)`

Reset controller internal state.

[View full source →](#method-controllerprotocol-reset)

##### `gains(self)`

Return controller gains.

[View full source →](#method-controllerprotocol-gains)

##### `max_force(self)`

Return maximum force limit.

[View full source →](#method-controllerprotocol-max_force)



### `ConfigurationProtocol`

**Inherits from:** `Protocol`

Protocol for controller configuration objects.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/protocols.py
:language: python
:pyobject: ConfigurationProtocol
:linenos:
```

#### Methods (3)

##### `gains(self)`

Controller gains.

[View full source →](#method-configurationprotocol-gains)

##### `max_force(self)`

Maximum force limit.

[View full source →](#method-configurationprotocol-max_force)

##### `dt(self)`

Time step.

[View full source →](#method-configurationprotocol-dt)



### `ControllerFactoryProtocol`

**Inherits from:** `Protocol`

Protocol for controller factory functions.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/protocols.py
:language: python
:pyobject: ControllerFactoryProtocol
:linenos:
```

#### Methods (3)

##### `create_controller(self, controller_type, config, gains)`

Create a controller instance.

[View full source →](#method-controllerfactoryprotocol-create_controller)

##### `list_available_controllers(self)`

List available controller types.

[View full source →](#method-controllerfactoryprotocol-list_available_controllers)

##### `get_default_gains(self, controller_type)`

Get default gains for controller type.

[View full source →](#method-controllerfactoryprotocol-get_default_gains)



### `PSOOptimizableProtocol`

**Inherits from:** `Protocol`

Protocol for PSO-optimizable controllers.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/protocols.py
:language: python
:pyobject: PSOOptimizableProtocol
:linenos:
```

#### Methods (4)

##### `compute_control(self, state)`

Compute control output for PSO optimization.

[View full source →](#method-psooptimizableprotocol-compute_control)

##### `n_gains(self)`

Number of optimization parameters.

[View full source →](#method-psooptimizableprotocol-n_gains)

##### `controller_type(self)`

Controller type identifier.

[View full source →](#method-psooptimizableprotocol-controller_type)

##### `max_force(self)`

Maximum force limit.

[View full source →](#method-psooptimizableprotocol-max_force)



### `ValidationProtocol`

**Inherits from:** `Protocol`

Protocol for validation functions.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/core/protocols.py
:language: python
:pyobject: ValidationProtocol
:linenos:
```

#### Methods (2)

##### `validate_gains(self, gains, controller_type)`

Validate controller gains.

[View full source →](#method-validationprotocol-validate_gains)

##### `validate_configuration(self, config, controller_type)`

Validate configuration object.

[View full source →](#method-validationprotocol-validate_configuration)



## Dependencies

This module imports:

- `from typing import Protocol, Any, Dict, List, Optional, Union`
- `import numpy as np`
- `from numpy.typing import NDArray`
