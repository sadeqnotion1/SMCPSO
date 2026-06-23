# controllers.smc.algorithms.classical.controller

**Source:** `src\controllers\smc\algorithms\classical\controller.py`

## Module Overview

Modular Classical SMC Controller.

Clean implementation using focused components:
- SlidingSurface: Surface computation
- EquivalentControl: Model-based feedforward
- BoundaryLayer: Chattering reduction
- Configuration: Type-safe parameters

Replaces the monolithic 458-line controller with composition of 50-100 line modules.




## Advanced Mathematical Theory

### Component Composition

Classical SMC combines three components:

```{math}
u = u_{eq} + u_{sw} = u_{eq} - K \, \text{sat}(s/\epsilon)
```

### Equivalent Control Computation

From $\dot{s} = 0$ on sliding surface:

```{math}
u_{eq} = (\mathbf{\Lambda} \mathbf{M}^{-1} \mathbf{B})^{-1} \left[ -\mathbf{\Lambda} \mathbf{M}^{-1} (\mathbf{C} \dot{\vec{q}} + \mathbf{G}) - \mathbf{C}_s \dot{\vec{\theta}} \right]
```

### Switching Gain Selection

**Minimum required gain:**

```{math}
K \geq \frac{|\Delta|_{max}}{\eta} + \varepsilon
```

Where:
- $|\Delta|_{max}$: Maximum uncertainty bound
- $\eta > 0$: Reaching rate parameter
- $\varepsilon > 0$: Safety margin (typically 20%)

### Reaching Time Bound

With $s \dot{s} \leq -\eta |s|$:

```{math}
t_{reach} \leq \frac{|s(0)|}{\eta}
```

### Control Authority Analysis

**Peak control estimate:**

```{math}
|u|_{peak} \leq |u_{eq}|_{max} + K
```

Must satisfy: $|u|_{peak} \leq 0.9 u_{max}$ (10% safety margin)

### Performance Tuning Guidelines

**Gain selection priority:**
1. **Surface gains** ($c_i, \lambda_i$): Sliding dynamics
2. **Switching gain** ($K$): Robustness
3. **Boundary layer** ($\epsilon$): Chattering vs accuracy

## Architecture Diagram

```{mermaid}
graph TD
    A[State x] --> B[Sliding Surface]
    B --> C{s}
    C --> D[Equivalent Control]
    C --> E[Boundary Layer]

    A --> D
    D --> F[u_eq]
    E --> G[u_sw = -K sat_s/ε_]

    F --> H[Combiner: u = u_eq + u_sw]
    G --> H
    H --> I[Saturation]
    I --> J[Control Output u]

    style C fill:#ff9
    style H fill:#9cf
    style J fill:#9f9
```

## Usage Examples

### Example 1: Basic Initialization

```python
from src.controllers.smc.algorithms.classical import *

# Initialize with configuration
config = {'parameter': 'value'}
instance = Component(config)
```

## Example 2: Performance Tuning

```python
# Adjust parameters for better performance
optimized_params = tune_parameters(instance, target_performance)
```

## Example 3: Integration with Controller

```python
# Use in complete control loop
controller = create_controller(ctrl_type, config)
result = simulate(controller, duration=5.0)
```

## Example 4: Edge Case Handling

```python
try:
    output = instance.compute(state)
except ValueError as e:
    handle_edge_case(e)
```

### Example 5: Performance Analysis

```python
# Analyze metrics
metrics = compute_metrics(result)
print(f"ITAE: {metrics.itae:.3f}")
```

## Architecture Diagram

```{mermaid}
graph TD
    A[State Input] --> B[Sliding Surface]
    B --> C{Surface Value s}
    C --> D[Equivalent Control]
    C --> E[Switching Control]
    A --> D
    D --> F[Control Combiner]
    E --> F
    F --> G[Saturation]
    G --> H[Control Output u]

    style C fill:#ff9
    style F fill:#9f9
    style G fill:#f99
```

**Data Flow:**
1. State → Sliding Surface Computation
2. Surface Value → Equivalent & Switching Control
3. Control Components → Combination & Saturation
4. Final Control → Actuator


## Mathematical Foundation

### Sliding Mode Control Theory

Classical SMC ensures finite-time convergence to the sliding surface:

```{math}
s(\vec{x}) = \vec{S}\vec{x} = \vec{0}
```

Where the sliding surface matrix $\vec{S} \in \mathbb{R}^{1 \times 4}$ is designed such that the system dynamics on the surface exhibit desired behavior.

### Control Law Structure

The control law consists of two components:

```{math}
u = u_{eq} + u_{sw}
```

**Equivalent Control** ($u_{eq}$): Model-based component that maintains sliding once on the surface:

```{math}
u_{eq} = -(\vec{S}\vec{M}^{-1}\vec{B})^{-1}\vec{S}\vec{M}^{-1}\vec{F}
```

**Switching Control** ($u_{sw}$): Robust component that drives state to the surface:

```{math}
u_{sw} = -K \cdot \text{sign}(s)
```

### Lyapunov Stability

Finite-time convergence is guaranteed by the Lyapunov function:

```{math}
V(s) = \frac{1}{2}s^2
```

With derivative:

```{math}
\dot{V} = s\dot{s} = -K|s| \leq 0 \quad \forall s \neq 0
```

This ensures the sliding surface is reached in finite time $t_r \leq \frac{|s(0)|}{K}$.

### Chattering Reduction

Boundary layer method replaces discontinuous sign function:

```{math}
\text{sign}(s) \rightarrow \text{sat}(s/\epsilon) = \begin{cases}
s/\epsilon & |s| \leq \epsilon \\
\text{sign}(s) & |s| > \epsilon
\end{cases}
```

**See:** {doc}`../../../mathematical_foundations/smc_complete_theory` for complete proofs.


## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/classical/controller.py
:language: python
:linenos:
```



## Classes

### `ModularClassicalSMC`

Modular Classical SMC controller using composition of focused components.

Components:
- Sliding surface: Computes s = λ₁ė₁ + c₁e₁ + λ₂ė₂ + c₂e₂
- Equivalent control: Model-based u_eq = -(LM⁻¹B)⁻¹LM⁻¹F
- Boundary layer: Continuous switching with chattering reduction

#### Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/classical/controller.py
:language: python
:pyobject: ModularClassicalSMC
:linenos:
```

#### Methods (9)

##### `__init__(self, config)`

Initialize modular classical SMC.

[View full source →](#method-modularclassicalsmc-__init__)

##### `compute_control(self, state, state_vars, history)`

Compute classical SMC control law.

[View full source →](#method-modularclassicalsmc-compute_control)

##### `_estimate_surface_derivative(self, state)`

Estimate surface derivative for derivative control.

[View full source →](#method-modularclassicalsmc-_estimate_surface_derivative)

##### `_create_control_result(self, u_final, surface_value, surface_derivative, u_eq, u_switch, u_deriv, u_total)`

Create structured control result.

[View full source →](#method-modularclassicalsmc-_create_control_result)

##### `_create_error_result(self, error_msg)`

Create error result with safe defaults.

[View full source →](#method-modularclassicalsmc-_create_error_result)

##### `gains(self)`

Return controller gains for interface compatibility.

[View full source →](#method-modularclassicalsmc-gains)

##### `reset(self)`

Reset controller to initial state.

[View full source →](#method-modularclassicalsmc-reset)

##### `get_parameters(self)`

Get all controller parameters.

[View full source →](#method-modularclassicalsmc-get_parameters)

##### `analyze_performance(self, surface_history, control_history, dt)`

Analyze controller performance.

[View full source →](#method-modularclassicalsmc-analyze_performance)



### `ClassicalSMC`

Backward-compatible facade for the modular Classical SMC.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/classical/controller.py
:language: python
:pyobject: ClassicalSMC
:linenos:
```

#### Methods (5)

##### `__init__(self, gains, max_force, boundary_layer, dynamics_model)`

Initialize Classical SMC with legacy interface.

[View full source →](#method-classicalsmc-__init__)

##### `compute_control(self, state, state_vars, history)`

Compute control (delegates to modular controller).

[View full source →](#method-classicalsmc-compute_control)

##### `gains(self)`

Return controller gains.

[View full source →](#method-classicalsmc-gains)

##### `reset(self)`

Reset controller to initial state.

[View full source →](#method-classicalsmc-reset)

##### `get_parameters(self)`

Get controller parameters.

[View full source →](#method-classicalsmc-get_parameters)



## Dependencies

This module imports:

- `from typing import Dict, List, Union, Optional, Any`
- `import numpy as np`
- `import logging`
- `from ...core.sliding_surface import LinearSlidingSurface`
- `from ...core.equivalent_control import EquivalentControl`
- `from .boundary_layer import BoundaryLayer`
- `from .config import ClassicalSMCConfig`


## Usage Examples

### Basic Instantiation

```python
from src.controllers.smc.algorithms.classical import ClassicalSMC
from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig

# Configure controller
config = ClassicalSMCConfig(
    surface_gains=[10.0, 8.0, 15.0, 12.0],  # [k1, k2, λ1, λ2]
    switching_gain=50.0,                     # K
    derivative_gain=5.0,                     # kd
    max_force=100.0,
    boundary_layer=0.01
)

# Create controller
controller = ClassicalSMC(config)
```

## Integration with Simulation

```python
from src.core.simulation_runner import SimulationRunner
from src.plant.models.simplified import SimplifiedDynamics

# Create simulation components
dynamics = SimplifiedDynamics()
runner = SimulationRunner(controller, dynamics)

# Run simulation
result = runner.run(
    initial_state=[0.1, 0.05, 0, 0, 0, 0],  # [θ1, θ2, θ̇1, θ̇2, x, ẋ]
    duration=5.0,
    dt=0.01
)

# Analyze results
print(f"Settling time: {result.metrics.settling_time:.2f}s")
print(f"Overshoot: {result.metrics.overshoot:.1f}%")
```

## PSO Optimization Workflow

```python
from src.controllers.factory import create_smc_for_pso, get_gain_bounds_for_pso
from src.controllers.factory import SMCType
from src.optimizer.pso_optimizer import PSOTuner

# Get optimization bounds
lower_bounds, upper_bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)

# Define controller factory
def controller_factory(gains):
    return create_smc_for_pso(SMCType.CLASSICAL, gains, max_force=100.0)

# Configure PSO
pso_tuner = PSOTuner(
    controller_factory=controller_factory,
    bounds=(lower_bounds, upper_bounds),
    n_particles=30,
    max_iter=50
)

# Optimize
best_gains, best_cost = pso_tuner.optimize()
print(f"Optimized gains: {best_gains}")
print(f"Best fitness: {best_cost:.4f}")
```

## Advanced: Custom Boundary Layer

```python
from src.controllers.smc.algorithms.classical.boundary_layer import BoundaryLayer

# Experiment with different chattering reduction methods
boundary_layer = BoundaryLayer(
    epsilon=0.01,
    method='tanh',  # 'tanh', 'linear', 'sigmoid'
    slope=3.0       # Steepness parameter for tanh
)

# Custom configuration
config = ClassicalSMCConfig(
    surface_gains=[10.0, 8.0, 15.0, 12.0],
    switching_gain=50.0,
    derivative_gain=5.0,
    max_force=100.0,
    boundary_layer=0.01
)

controller = ClassicalSMC(config)
```

## Performance Monitoring

```python
from src.utils.monitoring.latency import LatencyMonitor

# Monitor control loop timing
monitor = LatencyMonitor(dt=0.01)

start = monitor.start()
control, state_vars, history = controller.compute_control(state, state_vars, history)
missed_deadlines = monitor.end(start)

if missed_deadlines > 0:
    print(f"Warning: {missed_deadlines} deadline misses detected!")
```

**Related Examples:**
- {doc}`../../../examples/optimization_workflows/pso_classical_smc`
- {doc}`../../../examples/simulation_patterns/basic_smc_simulation`
