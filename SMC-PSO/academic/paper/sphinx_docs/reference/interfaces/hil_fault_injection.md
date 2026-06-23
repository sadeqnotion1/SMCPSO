# interfaces.hil.fault_injection

**Source:** `src\interfaces\hil\fault_injection.py`

## Module Overview Fault

injection system for HIL testing and validation

.


This module provides fault injection features including
sensor faults, actuator faults, communication failures, and system-level
fault scenarios for robust control system testing.


## Mathematical Foundation

### Fault Injection Models

Systematic fault injection for robustness testing: ```{math}
\tilde{\vec{x}}(t) = \vec{x}(t) + \vec{f}_{\text{fault}}(t)
``` Where $\vec{f}_{\text{fault}}$ depends on fault type and severity. ### Sensor Fault Models **1. Bias Fault:**
```{math}

\tilde{x}_i(t) = x_i(t) + b_i
``` **2. Scaling Fault:**
```{math}

\tilde{x}_i(t) = \alpha_i x_i(t), \quad \alpha_i \neq 1
``` **3. Dropout Fault:**
```{math}

\tilde{x}_i(t) = \begin{cases}
x_i(t) & \text{with probability } 1 - p_{\text{drop}} \\
x_i(t - \tau) & \text{with probability } p_{\text{drop}}
\end{cases}
``` **4. Noise Injection:**
```{math}

\tilde{x}_i(t) = x_i(t) + \eta_i(t), \quad \eta_i \sim \mathcal{N}(0, \sigma_i^2)
``` ### Actuator Fault Models **1. Saturation Fault:**
```{math}

u_{\text{actual}} = \text{clip}(u_{\text{cmd}}, u_{\text{min}}^{\text{fault}}, u_{\text{max}}^{\text{fault}})
``` **2. Delay Fault:**
```{math}

u_{\text{actual}}(t) = u_{\text{cmd}}(t - \tau_{\text{delay}})
``` **3. Degradation Fault:**
```{math}

u_{\text{actual}}(t) = \beta(t) \cdot u_{\text{cmd}}(t), \quad 0 < \beta < 1
``` **4. Stuck-at Fault:**
```{math}

u_{\text{actual}}(t) = u_{\text{stuck}}, \quad \forall t > t_{\text{fault}}
``` ### Communication Fault Models **1. Packet Loss:**
```{math}

P(\text{packet received}) = 1 - p_{\text{loss}}
``` **2. Latency Spike:**
```{math}

\tau_{\text{actual}} = \begin{cases}
\tau_{\text{nominal}} & \text{with probability } 1 - p_{\text{spike}} \\
\tau_{\text{nominal}} + \Delta \tau & \text{with probability } p_{\text{spike}}
\end{cases}
``` **3. Message Corruption:**
```{math}

P(\text{bit flip}) = p_{\text{corrupt}}
``` ### Fault Injection Strategies **1. Random Injection:**
```{math}

P(\text{fault at } t) = \lambda \cdot \Delta t
``` Poisson process with rate $\lambda$. **2. Scenario-Based Injection:**
Deterministic fault at specific times:
```{math}

\text{Fault}(t) = \begin{cases}
\text{Active} & \text{if } t \in [t_{\text{start}}, t_{\text{end}}] \\
\text{Inactive} & \text{otherwise}
\end{cases}
``` **3. Stress Testing:**
Multiple concurrent faults:
```{math}

\vec{f}_{\text{total}} = \sum_{i=1}^{N} \alpha_i \vec{f}_i(t)
``` ### Fault Detection Metrics **1. Detection Time:**
```{math}

T_{\text{detect}} = t_{\text{detected}} - t_{\text{fault}}
``` **2. False Positive Rate:**
```{math}

\text{FPR} = \frac{\text{False Alarms}}{\text{Total Samples}}
``` **3. False Negative Rate:**
```{math}

\text{FNR} = \frac{\text{Missed Faults}}{\text{Total Faults}}
``` ### Fault Severity Levels **Categorization:**
1. **Low**: $\|\vec{f}\| < \epsilon_{\text{low}}$ (minor disturbance)
2. **Medium**: $\epsilon_{\text{low}} \leq \|\vec{f}\| < \epsilon_{\text{high}}$ (degraded performance)
3. **High**: $\|\vec{f}\| \geq \epsilon_{\text{high}}$ (critical failure)
4. **Catastrophic**: System divergence or safety violation ## Architecture Diagram ```{mermaid}
graph TD A[Fault Injection Manager] --> B{Fault Type} B -->|Sensor| C[Sensor Fault Injector] B -->|Actuator| D[Actuator Fault Injector] B -->|Communication| E[Comm Fault Injector] C --> F[Add Bias] C --> G[Add Noise] C --> H[Dropout] C --> I[Scaling] D --> J[Saturation] D --> K[Delay] D --> L[Stuck-at] D --> M[Degradation] E --> N[Packet Loss] E --> O[Latency Spike] E --> P[Corruption] A --> Q[Fault Scheduler] Q --> R{Injection Time} R -->|Random| S[Poisson Process] R -->|Deterministic| T[Scenario-Based] style A fill:#9cf style Q fill:#ff9 style B fill:#f9f
``` **Fault Injection Workflow:**

1. **Configure Faults**: Define type, severity, timing
2. **Schedule Injection**: Random or scenario-based
3. **Apply Fault**: Modify sensor/actuator/communication
4. **Monitor Response**: Track detection and recovery
5. **Record Metrics**: Log fault events and system response ## Usage Examples ### Example 1: Sensor Bias Fault ```python
from src.interfaces.hil.fault_injection import FaultInjector, FaultType # Create fault injector
injector = FaultInjector() # Add sensor bias fault
injector.add_fault( fault_type=FaultType.SENSOR_BIAS, target="theta1", # First pendulum angle bias=0.1, # 0.1 radian bias start_time=2.0, # Start at 2 seconds duration=3.0 # Last for 3 seconds
) # Apply fault during simulation
for t in np.arange(0, 10, 0.01): state = plant.get_state() faulty_state = injector.apply(state, t) control = controller.compute(faulty_state)
``` ### Example 2: Actuator Saturation Fault ```python
from src.interfaces.hil.fault_injection import FaultInjector, FaultType # Actuator fault
injector = FaultInjector() injector.add_fault( fault_type=FaultType.ACTUATOR_SATURATION, target="control", saturation_min=-50.0, # Reduced from -100 saturation_max=50.0, # Reduced from +100 start_time=5.0
) # Simulation with fault
for t in np.arange(0, 10, 0.01): state = plant.get_state() control = controller.compute(state) faulty_control = injector.apply(control, t) plant.step(faulty_control)
``` ### Example 3: Communication Fault (Packet Loss) ```python

from src.interfaces.hil.fault_injection import FaultInjector, FaultType # Packet loss fault
injector = FaultInjector() injector.add_fault( fault_type=FaultType.PACKET_LOSS, loss_probability=0.2, # 20% packet loss start_time=3.0, duration=5.0
) # HIL with communication faults
for t in np.arange(0, 10, 0.01): # Request state from server state_msg = client.request_state() # Apply packet loss if injector.check_packet_loss(t): # Use last known state state = last_state else: state = state_msg.state control = controller.compute(state) client.send_control(control) last_state = state
``` ### Example 4: Multiple Concurrent Faults ```python
from src.interfaces.hil.fault_injection import FaultInjector # Multiple faults
injector = FaultInjector() # Sensor noise
injector.add_fault( fault_type=FaultType.SENSOR_NOISE, target="theta1", noise_std=0.05, start_time=0.0
) # Actuator delay
injector.add_fault( fault_type=FaultType.ACTUATOR_DELAY, delay_time=0.05, # 50 ms delay start_time=4.0
) # Communication latency spike
injector.add_fault( fault_type=FaultType.LATENCY_SPIKE, spike_probability=0.1, spike_duration=0.1, start_time=2.0
) # Run with all faults
for t in np.arange(0, 10, 0.01): state = plant.get_state() faulty_state = injector.apply_all(state, t) control = controller.compute(faulty_state) faulty_control = injector.apply_all(control, t) plant.step(faulty_control)
``` ### Example 5: Fault Detection Testing ```python

from src.interfaces.hil.fault_injection import FaultInjector
from src.analysis.fault_detection import FDISystem # Create fault injector and detector
injector = FaultInjector()
fdi = FDISystem(threshold=0.15) # Inject sensor bias
injector.add_fault( fault_type=FaultType.SENSOR_BIAS, target="theta2", bias=0.2, start_time=5.0
) # Track detection performance
detection_time = None
false_positives = 0 for t in np.arange(0, 10, 0.01): state = plant.get_state() faulty_state = injector.apply(state, t) # Check fault detection fault_detected = fdi.check(faulty_state) if fault_detected and detection_time is None and t >= 5.0: detection_time = t print(f"Fault detected at t={t:.2f}s (actual fault at 5.0s)") if fault_detected and t < 5.0: false_positives += 1 # Report results
print(f"Detection delay: {detection_time - 5.0:.3f}s")
print(f"False positives: {false_positives}")
``` ## Complete Source Code ```{literalinclude} ../../../src/interfaces/hil/fault_injection.py
:language: python
:linenos:
```

---

## Classes

### `FaultType`

**Inherits from:** `Enum` Fault type enumeration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/fault_injection.py

:language: python
:pyobject: FaultType
:linenos:
```

### `FaultSeverity`

**Inherits from:** `Enum` Fault severity enumeration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/fault_injection.py
:language: python
:pyobject: FaultSeverity
:linenos:
```

### `FaultProfile`

Fault injection profile configuration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/fault_injection.py

:language: python
:pyobject: FaultProfile
:linenos:
```

### `FaultScenario`

Complete fault scenario with multiple fault profiles.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/fault_injection.py
:language: python
:pyobject: FaultScenario
:linenos:
```

### `FaultEvent`

Fault event record.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/fault_injection.py

:language: python
:pyobject: FaultEvent
:linenos:
```

### `FaultInjector`

fault injection system for HIL testing. Provides systematic fault injection features for sensors,
actuators, communication, and system-level components to validate
control system robustness and fault tolerance. #### Source Code ```{literalinclude} ../../../src/interfaces/hil/fault_injection.py
:language: python
:pyobject: FaultInjector
:linenos:
``` #### Methods (29) ##### `__init__(self, device_manager, communication_interfaces)` Initialize fault injector. [View full source →](#method-faultinjector-__init__) ##### `enabled(self)` Check if fault injection is enabled. [View full source →](#method-faultinjector-enabled) ##### `active_faults(self)` Get currently active faults. [View full source →](#method-faultinjector-active_faults) ##### `statistics(self)` Get fault injection statistics. [View full source →](#method-faultinjector-statistics) ##### `enable(self)` fault injection. [View full source →](#method-faultinjector-enable) ##### `disable(self)` Disable fault injection. [View full source →](#method-faultinjector-disable) ##### `inject_fault(self, fault_id, profile)` Inject a specific fault. [View full source →](#method-faultinjector-inject_fault) ##### `remove_fault(self, fault_id)` Remove an active fault. [View full source →](#method-faultinjector-remove_fault) ##### `clear_all_faults(self)` Clear all active faults. [View full source →](#method-faultinjector-clear_all_faults) ##### `configure_scenario(self, scenario)` Configure fault scenario. [View full source →](#method-faultinjector-configure_scenario) ##### `execute_scenario(self, scenario_name)` Execute fault scenario. [View full source →](#method-faultinjector-execute_scenario) ##### `stop_scenario(self)` Stop current scenario execution. [View full source →](#method-faultinjector-stop_scenario) ##### `get_fault_history(self, since, fault_type)` Get fault event history. [View full source →](#method-faultinjector-get_fault_history) ##### `_execute_fault(self, fault_id, profile)` Execute fault injection task. [View full source →](#method-faultinjector-_execute_fault) ##### `_apply_fault(self, device, profile)` Apply specific fault to device. [View full source →](#method-faultinjector-_apply_fault) ##### `_apply_sensor_bias(self, device, profile)` Apply sensor bias fault. [View full source →](#method-faultinjector-_apply_sensor_bias) ##### `_apply_sensor_drift(self, device, profile)` Apply sensor drift fault. [View full source →](#method-faultinjector-_apply_sensor_drift) ##### `_apply_sensor_noise(self, device, profile)` Apply sensor noise fault. [View full source →](#method-faultinjector-_apply_sensor_noise) ##### `_apply_sensor_stuck(self, device, profile)` Apply sensor stuck fault. [View full source →](#method-faultinjector-_apply_sensor_stuck) ##### `_apply_actuator_bias(self, device, profile)` Apply actuator bias fault. [View full source →](#method-faultinjector-_apply_actuator_bias) ##### `_apply_actuator_stuck(self, device, profile)` Apply actuator stuck fault. [View full source →](#method-faultinjector-_apply_actuator_stuck) ##### `_apply_communication_delay(self, profile)` Apply communication delay fault. [View full source →](#method-faultinjector-_apply_communication_delay) ##### `_apply_communication_loss(self, profile)` Apply communication loss fault. [View full source →](#method-faultinjector-_apply_communication_loss) ##### `_execute_scenario_task(self, scenario)` Execute complete fault scenario. [View full source →](#method-faultinjector-_execute_scenario_task) ##### `_inject_scenario_fault(self, fault_id, profile)` Inject fault as part of scenario. [View full source →](#method-faultinjector-_inject_scenario_fault) ##### `_validate_fault_profile(self, profile)` Validate fault profile configuration. [View full source →](#method-faultinjector-_validate_fault_profile) ##### `_cleanup_fault(self, fault_id, profile)` Clean up fault after completion or cancellation. [View full source →](#method-faultinjector-_cleanup_fault) ##### `_record_fault_event(self, event)` Record fault event in history. [View full source →](#method-faultinjector-_record_fault_event) ##### `set_safety_limits(self, device_id, limits)` Set safety limits for fault injection. [View full source →](#method-faultinjector-set_safety_limits)

---

## Functions

### `create_sensor_fault_scenario(sensor_name, fault_types, duration)`

Create common sensor fault scenario.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/fault_injection.py

:language: python
:pyobject: create_sensor_fault_scenario
:linenos:
```

### `create_actuator_fault_scenario(actuator_name, severity)`

Create common actuator fault scenario.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/fault_injection.py
:language: python
:pyobject: create_actuator_fault_scenario
:linenos:
```

---

## Dependencies This module imports: - `import asyncio`

- `import time`
- `import random`
- `import numpy as np`
- `from dataclasses import dataclass, field`
- `from typing import Dict, Any, Optional, List, Callable, Union`
- `from enum import Enum`
- `import logging`
