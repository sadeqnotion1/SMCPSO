# interfaces.hardware.actuators

**Source:** `src\interfaces\hardware\actuators.py`

## Module Overview

Actuator interface framework for control systems.
This module provides standardized interfaces for various actuator types
commonly used in control systems, including servo motors, stepper motors,
pneumatic actuators, and other motion control devices.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/hardware/actuators.py
:language: python
:linenos:
```



## Classes

### `ActuatorType`

**Inherits from:** `Enum`

Actuator type enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/actuators.py
:language: python
:pyobject: ActuatorType
:linenos:
```



### `ActuatorMode`

**Inherits from:** `Enum`

Actuator control mode enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/actuators.py
:language: python
:pyobject: ActuatorMode
:linenos:
```



### `ActuatorCommand`

Actuator command data structure.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/actuators.py
:language: python
:pyobject: ActuatorCommand
:linenos:
```



### `ActuatorStatus`

Actuator status data structure.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/actuators.py
:language: python
:pyobject: ActuatorStatus
:linenos:
```



### `ActuatorLimits`

Actuator operational limits.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/actuators.py
:language: python
:pyobject: ActuatorLimits
:linenos:
```



### `ActuatorInterface`

**Inherits from:** `DeviceDriver`, `ABC`

Abstract base class for actuator interfaces.

This class defines the standard interface for all actuator types,
providing common functionality for motion control, safety limits,
and position feedback.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/actuators.py
:language: python
:pyobject: ActuatorInterface
:linenos:
```

#### Methods (18)

##### `__init__(self, config)`

Initialize actuator interface.

[View full source →](#method-actuatorinterface-__init__)

##### `actuator_type(self)`

Get actuator type.

[View full source →](#method-actuatorinterface-actuator_type)

##### `control_mode(self)`

Get current control mode.

[View full source →](#method-actuatorinterface-control_mode)

##### `current_status(self)`

Get current actuator status.

[View full source →](#method-actuatorinterface-current_status)

##### `limits(self)`

Get actuator limits.

[View full source →](#method-actuatorinterface-limits)

##### `move_to_position(self, position, velocity)`

Move actuator to specific position.

[View full source →](#method-actuatorinterface-move_to_position)

##### `set_velocity(self, velocity)`

Set actuator velocity.

[View full source →](#method-actuatorinterface-set_velocity)

##### `set_force(self, force)`

Set actuator force/torque.

[View full source →](#method-actuatorinterface-set_force)

##### `stop(self)`

Stop actuator motion.

[View full source →](#method-actuatorinterface-stop)

##### `home(self)`

Move actuator to home position.

[View full source →](#method-actuatorinterface-home)

##### `set_control_mode(self, mode)`

Set actuator control mode.

[View full source →](#method-actuatorinterface-set_control_mode)

##### `set_limits(self, limits)`

Set actuator operational limits.

[View full source →](#method-actuatorinterface-set_limits)

##### `is_at_target(self, tolerance)`

Check if actuator is at target position.

[View full source →](#method-actuatorinterface-is_at_target)

##### `wait_for_motion_complete(self, timeout)`

Wait for actuator to reach target position.

[View full source →](#method-actuatorinterface-wait_for_motion_complete)

##### `emergency_stop(self)`

Perform emergency stop.

[View full source →](#method-actuatorinterface-emergency_stop)

##### `clear_faults(self)`

Clear actuator fault conditions.

[View full source →](#method-actuatorinterface-clear_faults)

##### `_check_safety_limits(self, command)`

Check if command violates safety limits.

[View full source →](#method-actuatorinterface-_check_safety_limits)

##### `_add_command_to_queue(self, command)`

Add command to execution queue.

[View full source →](#method-actuatorinterface-_add_command_to_queue)



### `ServoActuator`

**Inherits from:** `ActuatorInterface`

Servo motor actuator implementation.

Provides position control with encoder feedback, velocity control,
and PID control loop functionality.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/actuators.py
:language: python
:pyobject: ServoActuator
:linenos:
```

#### Methods (15)

##### `__init__(self, config)`

Initialize servo actuator.

[View full source →](#method-servoactuator-__init__)

##### `initialize(self)`

Initialize servo actuator.

[View full source →](#method-servoactuator-initialize)

##### `shutdown(self)`

Shutdown servo actuator.

[View full source →](#method-servoactuator-shutdown)

##### `read_data(self, channel)`

Read servo actuator data.

[View full source →](#method-servoactuator-read_data)

##### `write_data(self, data)`

Write data to servo actuator.

[View full source →](#method-servoactuator-write_data)

##### `self_test(self)`

Perform servo actuator self-test.

[View full source →](#method-servoactuator-self_test)

##### `move_to_position(self, position, velocity)`

Move servo to specific position.

[View full source →](#method-servoactuator-move_to_position)

##### `set_velocity(self, velocity)`

Set servo velocity.

[View full source →](#method-servoactuator-set_velocity)

##### `set_force(self, force)`

Set servo force/torque.

[View full source →](#method-servoactuator-set_force)

##### `stop(self)`

Stop servo motion.

[View full source →](#method-servoactuator-stop)

##### `home(self)`

Move servo to home position.

[View full source →](#method-servoactuator-home)

##### `_position_control_loop(self, target_position, max_velocity)`

Position control loop with PID controller.

[View full source →](#method-servoactuator-_position_control_loop)

##### `_velocity_control_loop(self, target_velocity)`

Velocity control loop.

[View full source →](#method-servoactuator-_velocity_control_loop)

##### `_update_status(self)`

Update servo status.

[View full source →](#method-servoactuator-_update_status)

##### `_add_servo_capabilities(self)`

Add servo actuator support.

[View full source →](#method-servoactuator-_add_servo_capabilities)



### `StepperMotor`

**Inherits from:** `ActuatorInterface`

Stepper motor actuator implementation.

Provides precise position control through step counting,
with configurable step size and acceleration profiles.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/actuators.py
:language: python
:pyobject: StepperMotor
:linenos:
```

#### Methods (15)

##### `__init__(self, config)`

Initialize stepper motor.

[View full source →](#method-steppermotor-__init__)

##### `initialize(self)`

Initialize stepper motor.

[View full source →](#method-steppermotor-initialize)

##### `shutdown(self)`

Shutdown stepper motor.

[View full source →](#method-steppermotor-shutdown)

##### `read_data(self, channel)`

Read stepper motor data.

[View full source →](#method-steppermotor-read_data)

##### `write_data(self, data)`

Write data to stepper motor.

[View full source →](#method-steppermotor-write_data)

##### `self_test(self)`

Perform stepper motor self-test.

[View full source →](#method-steppermotor-self_test)

##### `move_to_position(self, position, velocity)`

Move stepper to specific position.

[View full source →](#method-steppermotor-move_to_position)

##### `move_to_step(self, target_step)`

Move stepper to specific step.

[View full source →](#method-steppermotor-move_to_step)

##### `move_steps(self, step_count)`

Move stepper by relative step count.

[View full source →](#method-steppermotor-move_steps)

##### `set_velocity(self, velocity)`

Set stepper velocity (not directly applicable).

[View full source →](#method-steppermotor-set_velocity)

##### `set_force(self, force)`

Set stepper force (holding torque).

[View full source →](#method-steppermotor-set_force)

##### `stop(self)`

Stop stepper motion.

[View full source →](#method-steppermotor-stop)

##### `home(self)`

Home stepper motor.

[View full source →](#method-steppermotor-home)

##### `_step_control_loop(self, target_step)`

Step control loop.

[View full source →](#method-steppermotor-_step_control_loop)

##### `_add_stepper_capabilities(self)`

Add stepper motor support.

[View full source →](#method-steppermotor-_add_stepper_capabilities)



### `PneumaticActuator`

**Inherits from:** `ActuatorInterface`

Pneumatic actuator implementation.

Provides pressure-based control for linear and rotary
pneumatic actuators with pressure feedback.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/actuators.py
:language: python
:pyobject: PneumaticActuator
:linenos:
```

#### Methods (13)

##### `__init__(self, config)`

Initialize pneumatic actuator.

[View full source →](#method-pneumaticactuator-__init__)

##### `initialize(self)`

Initialize pneumatic actuator.

[View full source →](#method-pneumaticactuator-initialize)

##### `shutdown(self)`

Shutdown pneumatic actuator.

[View full source →](#method-pneumaticactuator-shutdown)

##### `read_data(self, channel)`

Read pneumatic actuator data.

[View full source →](#method-pneumaticactuator-read_data)

##### `write_data(self, data)`

Write data to pneumatic actuator.

[View full source →](#method-pneumaticactuator-write_data)

##### `self_test(self)`

Perform pneumatic actuator self-test.

[View full source →](#method-pneumaticactuator-self_test)

##### `move_to_position(self, position, velocity)`

Move pneumatic actuator to position.

[View full source →](#method-pneumaticactuator-move_to_position)

##### `set_pressure(self, pressure)`

Set pneumatic pressure.

[View full source →](#method-pneumaticactuator-set_pressure)

##### `set_velocity(self, velocity)`

Set pneumatic velocity (flow rate control).

[View full source →](#method-pneumaticactuator-set_velocity)

##### `set_force(self, force)`

Set pneumatic force.

[View full source →](#method-pneumaticactuator-set_force)

##### `stop(self)`

Stop pneumatic motion.

[View full source →](#method-pneumaticactuator-stop)

##### `home(self)`

Move pneumatic actuator to home position.

[View full source →](#method-pneumaticactuator-home)

##### `_add_pneumatic_capabilities(self)`

Add pneumatic actuator support.

[View full source →](#method-pneumaticactuator-_add_pneumatic_capabilities)



## Dependencies

This module imports:

- `import asyncio`
- `import time`
- `import numpy as np`
- `from abc import ABC, abstractmethod`
- `from dataclasses import dataclass, field`
- `from typing import Dict, Any, Optional, List, Tuple`
- `from enum import Enum`
- `import logging`
- `from .device_drivers import DeviceDriver, DeviceConfig, DeviceCapability, DeviceState`
