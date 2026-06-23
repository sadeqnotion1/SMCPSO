# interfaces.hil.enhanced_hil

**Source:** `src\interfaces\hil\enhanced_hil.py`

## Module Overview Enhanced

Hardware-in-the-Loop (HIL) system for advanced control testing

.


This module provides a HIL framework with real-time features,
fault injection, automated testing, and integration with hardware interfaces
for professional control system validation. ## Mathematical Foundation ### Enhanced HIL features Advanced HIL features beyond basic simulation: ```{math}
\text{HIL}_{\text{enhanced}} = \text{HIL}_{\text{basic}} + \mathcal{F}_{\text{advanced}}
``` Where $\mathcal{F}_{\text{advanced}}$ includes parameter variation, disturbance injection, and adaptive testing. ### Parameter Variation Studies **Systematic Parameter Sweep:**
```{math}

\mathcal{P} = \{p_1, p_2, \ldots, p_n\} \times \{v_1, v_2, \ldots, v_m\}
``` **Monte Carlo Sampling:**
```{math}

p_i \sim \mathcal{D}_i \quad \text{(Distribution for parameter } i\text{)}
``` ### Disturbance Injection **External Disturbances:**
```{math}

\dot{\vec{x}} = f(\vec{x}, u) + g(\vec{x}) \vec{w}(t)
``` Where:
- $g(\vec{x})$: Disturbance coupling matrix
- $\vec{w}(t)$: Disturbance signal **Common Disturbance Types:**
1. **Step**: $w(t) = A \cdot \mathbb{1}(t \geq t_0)$
2. **Ramp**: $w(t) = k \cdot t$
3. **Sinusoidal**: $w(t) = A \sin(\omega t + \phi)$
4. **Random**: $w(t) \sim \mathcal{N}(0, \sigma^2)$ ### Adaptive Testing **Difficulty Adaptation:**
```{math}

\text{Difficulty}(n+1) = \begin{cases}
\text{Difficulty}(n) + \Delta & \text{if PASS} \\
\text{Difficulty}(n) - \Delta & \text{if FAIL}
\end{cases}
``` **Exploration-Exploitation Tradeoff:**
```{math}

\text{Test}(n) = \begin{cases}
\text{Random} & \text{with probability } \epsilon \\
\text{Hardest Failed} & \text{with probability } 1 - \epsilon
\end{cases}
``` ### Multi-Fidelity Simulation **Fidelity Levels:**
```{math}

\mathcal{M} = \{M_{\text{low}}, M_{\text{medium}}, M_{\text{high}}\}
``` **Cost-Accuracy Tradeoff:**
```{math}

\text{Total Cost} = \sum_{i} C_i \cdot N_i
``` Subject to accuracy constraint:
```{math}

\|\text{Error}_{\text{total}}\| < \epsilon_{\text{target}}
``` ### Performance Profiling **Execution Time Distribution:**
```{math}

T_{\text{exec}} \sim \mathcal{D}_{\text{exec}}
``` **Percentile Analysis:**
- P50 (median)
- P95 (tail latency)
- P99 (worst-case) ### Hardware Emulation **Virtual Hardware Models:**
```{math}

\text{Virtual Actuator}: u_{\text{actual}} = h(u_{\text{cmd}}, \vec{p}_{\text{hw}})
``` Where $\vec{p}_{\text{hw}}$ includes hardware parameters (bandwidth, saturation, delay). **Sensor Emulation:**
```{math}

y = C\vec{x} + \vec{v}, \quad \vec{v} \sim \mathcal{N}(0, R)
``` ## Architecture Diagram ```{mermaid}
graph TD A[Enhanced HIL] --> B[Parameter Variation] B --> C[Monte Carlo Sampling] B --> D[Grid Search] A --> E[Disturbance Injection] E --> F[Step Disturbance] E --> G[Sinusoidal Disturbance] E --> H[Random Disturbance] A --> I[Adaptive Testing] I --> J[Difficulty Adaptation] I --> K[Exploration/Exploitation] A --> L[Multi-Fidelity] L --> M[Low Fidelity Model] L --> N[Medium Fidelity Model] L --> O[High Fidelity Model] C --> P[Test Execution] D --> P F --> P G --> P H --> P J --> P K --> P M --> P N --> P O --> P P --> Q[Results Analysis] Q --> R[Performance Profiling] Q --> S[Robustness Assessment] style A fill:#9cf style P fill:#ff9 style Q fill:#f9f
``` **Enhanced Features:**

1. **Parameter Variation**: Systematic exploration of parameter space
2. **Disturbance Injection**: Test robustness under external disturbances
3. **Adaptive Testing**: Dynamically adjust test difficulty
4. **Multi-Fidelity**: Trade accuracy for speed using model hierarchy ## Usage Examples ### Example 1: Parameter Variation Study ```python
from src.interfaces.hil.enhanced_hil import ParameterSweep # Parameter sweep
sweep = ParameterSweep() # Define parameter ranges
sweep.add_parameter("mass_cart", values=np.linspace(0.8, 1.2, 5))
sweep.add_parameter("length_1", values=np.linspace(0.3, 0.5, 5)) # Run sweep
results = sweep.run() # Analyze sensitivity
for param, result in results.items(): print(f"{param}: sensitivity = {result.sensitivity:.4f}")
``` ### Example 2: Disturbance Injection ```python
from src.interfaces.hil.enhanced_hil import DisturbanceInjector # Create disturbance injector
injector = DisturbanceInjector() # Add sinusoidal disturbance
injector.add_disturbance( type="sinusoidal", amplitude=5.0, frequency=1.0, start_time=2.0
) # Simulate with disturbance
for t in np.arange(0, 10, 0.01): state = plant.get_state() control = controller.compute(state) # Add disturbance disturbed_control = injector.apply(control, t) plant.step(disturbed_control)
``` ### Example 3: Multi-Fidelity Simulation ```python

from src.interfaces.hil.enhanced_hil import MultiFidelitySimulator # Multi-fidelity simulator
simulator = MultiFidelitySimulator() # Define fidelity levels
simulator.add_model("low", SimplifiedDynamics())
simulator.add_model("medium", FullDynamics(accuracy="medium"))
simulator.add_model("high", FullDynamics(accuracy="high")) # Run with adaptive fidelity
result = simulator.run_adaptive( initial_fidelity="low", accuracy_target=1e-3, max_cost=100.0
) print(f"Final fidelity: {result.final_fidelity}")
print(f"Total cost: {result.total_cost:.1f}")
print(f"Accuracy achieved: {result.accuracy:.6f}")
``` ### Example 4: Hardware Emulation ```python
from src.interfaces.hil.enhanced_hil import HardwareEmulator # Hardware emulator
emulator = HardwareEmulator() # Configure actuator model
emulator.set_actuator_model( bandwidth=50.0, # 50 Hz bandwidth saturation=100.0, delay=0.01 # 10 ms delay
) # Configure sensor model
emulator.set_sensor_model( noise_std=0.01, bias=0.005, dropout_rate=0.01
) # Simulate with hardware emulation
for t in np.arange(0, 10, 0.01): state = plant.get_state() # Emulate sensor measured_state = emulator.sensor(state) # Compute control control = controller.compute(measured_state) # Emulate actuator actual_control = emulator.actuator(control) plant.step(actual_control)
``` ### Example 5: Performance Profiling ```python

from src.interfaces.hil.enhanced_hil import PerformanceProfiler # Performance profiler
profiler = PerformanceProfiler() # Profile simulation
profiler.start() for t in np.arange(0, 10, 0.01): with profiler.section("dynamics"): state = plant.get_state() with profiler.section("control"): control = controller.compute(state) with profiler.section("communication"): client.send_control(control) profiler.stop() # Report profiling results
report = profiler.generate_report()
print(report.to_string()) # Identify bottlenecks
for section, time in report.sorted_sections(): print(f"{section}: {time:.2f} ms ({report.percentage(section):.1f}%)")
``` ## Complete Source Code ```{literalinclude} ../../../src/interfaces/hil/enhanced_hil.py
:language: python
:linenos:
```

---

## Classes

### `HILMode`

**Inherits from:** `Enum` HIL operation mode enumeration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/enhanced_hil.py

:language: python
:pyobject: HILMode
:linenos:
```

### `HILState`

**Inherits from:** `Enum` HIL system state enumeration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/enhanced_hil.py
:language: python
:pyobject: HILState
:linenos:
```

### `TimingConfig`

HIL timing configuration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/enhanced_hil.py

:language: python
:pyobject: TimingConfig
:linenos:
```

### `TestScenario`

HIL test scenario configuration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/enhanced_hil.py
:language: python
:pyobject: TestScenario
:linenos:
```

### `HILConfig`

HIL system configuration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/enhanced_hil.py

:language: python
:pyobject: HILConfig
:linenos:
```

### `EnhancedHILSystem`

Enhanced Hardware-in-the-Loop system with specific capabilities. This class provides a HIL framework that integrates
simulation, hardware, real-time scheduling, fault injection,
and automated testing for professional control system validation. #### Source Code ```{literalinclude} ../../../src/interfaces/hil/enhanced_hil.py
:language: python
:pyobject: EnhancedHILSystem
:linenos:
``` #### Methods (27) ##### `__init__(self, config)` Initialize enhanced HIL system. [View full source →](#method-enhancedhilsystem-__init__) ##### `state(self)` Get current HIL system state. [View full source →](#method-enhancedhilsystem-state) ##### `config(self)` Get HIL configuration. [View full source →](#method-enhancedhilsystem-config) ##### `performance_metrics(self)` Get performance metrics. [View full source →](#method-enhancedhilsystem-performance_metrics) ##### `initialize(self)` Initialize HIL system components. [View full source →](#method-enhancedhilsystem-initialize) ##### `start(self)` Start HIL system operation. [View full source →](#method-enhancedhilsystem-start) ##### `stop(self)` Stop HIL system operation. [View full source →](#method-enhancedhilsystem-stop) ##### `emergency_stop(self)` Perform emergency stop of HIL system. [View full source →](#method-enhancedhilsystem-emergency_stop) ##### `pause(self)` Pause HIL system operation. [View full source →](#method-enhancedhilsystem-pause) ##### `resume(self)` Resume HIL system operation. [View full source →](#method-enhancedhilsystem-resume) ##### `run_test_scenario(self, scenario)` Run specific test scenario. [View full source →](#method-enhancedhilsystem-run_test_scenario) ##### `get_system_status(self)` Get system status. [View full source →](#method-enhancedhilsystem-get_system_status) ##### `_setup_communication(self)` Setup communication interfaces. [View full source →](#method-enhancedhilsystem-_setup_communication) ##### `_setup_hardware(self)` Setup hardware devices. [View full source →](#method-enhancedhilsystem-_setup_hardware) ##### `_setup_simulation(self)` Setup simulation bridge. [View full source →](#method-enhancedhilsystem-_setup_simulation) ##### `_setup_real_time(self)` Setup real-time scheduler. [View full source →](#method-enhancedhilsystem-_setup_real_time) ##### `_setup_fault_injection(self)` Setup fault injection system. [View full source →](#method-enhancedhilsystem-_setup_fault_injection) ##### `_setup_test_framework(self)` Setup automated test framework. [View full source →](#method-enhancedhilsystem-_setup_test_framework) ##### `_setup_data_logging(self)` Setup data logging system. [View full source →](#method-enhancedhilsystem-_setup_data_logging) ##### `_system_self_test(self)` Perform system self-test. [View full source →](#method-enhancedhilsystem-_system_self_test) ##### `_main_loop(self)` Main HIL execution loop. [View full source →](#method-enhancedhilsystem-_main_loop) ##### `_read_inputs(self)` Read inputs from all sources. [View full source →](#method-enhancedhilsystem-_read_inputs) ##### `_update_simulation(self)` Update simulation model. [View full source →](#method-enhancedhilsystem-_update_simulation) ##### `_write_outputs(self)` Write outputs to all destinations. [View full source →](#method-enhancedhilsystem-_write_outputs) ##### `_apply_initial_conditions(self, conditions)` Apply initial conditions for test scenario. [View full source →](#method-enhancedhilsystem-_apply_initial_conditions) ##### `_apply_parameters(self, parameters)` Apply parameters for test scenario. [View full source →](#method-enhancedhilsystem-_apply_parameters) ##### `_analyze_scenario_results(self, scenario, data)` Analyze test scenario results. [View full source →](#method-enhancedhilsystem-_analyze_scenario_results)

### `TimingMonitor`

Monitor timing performance of HIL system.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/enhanced_hil.py

:language: python
:pyobject: TimingMonitor
:linenos:
``` #### Methods (3) ##### `__init__(self, timing_config)` [View full source →](#method-timingmonitor-__init__) ##### `record_iteration(self, iteration_time)` Record iteration timing. [View full source →](#method-timingmonitor-record_iteration) ##### `get_statistics(self)` Get timing statistics. [View full source →](#method-timingmonitor-get_statistics)

### `HILPerformanceMetrics`

Performance metrics for HIL system.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/enhanced_hil.py
:language: python
:pyobject: HILPerformanceMetrics
:linenos:
``` #### Methods (3) ##### `__init__(self)` [View full source →](#method-hilperformancemetrics-__init__) ##### `update(self, iteration_time)` Update performance metrics. [View full source →](#method-hilperformancemetrics-update) ##### `get_summary(self)` Get performance summary. [View full source →](#method-hilperformancemetrics-get_summary)

### `SafetyMonitor`

Safety monitoring for HIL system.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/enhanced_hil.py

:language: python
:pyobject: SafetyMonitor
:linenos:
``` #### Methods (3) ##### `__init__(self, config)` [View full source →](#method-safetymonitor-__init__) ##### `check_safety(self, inputs, outputs)` Check safety conditions. [View full source →](#method-safetymonitor-check_safety) ##### `get_status(self)` Get safety status. [View full source →](#method-safetymonitor-get_status)

---

## Dependencies This module imports: - `import asyncio`
- `import time`
- `import numpy as np`
- `from dataclasses import dataclass, field`
- `from typing import Dict, Any, Optional, List, Callable, Union`
- `from enum import Enum`
- `import logging`
- `from ..core.protocols import CommunicationProtocol`
- `from ..hardware.device_drivers import DeviceDriver, DeviceManager`
- `from ..network.factory import NetworkInterfaceFactory`
