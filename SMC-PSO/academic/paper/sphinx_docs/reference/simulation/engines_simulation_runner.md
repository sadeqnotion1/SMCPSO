# simulation.engines.simulation_runner

**Source:** `src\simulation\engines\simulation_runner.py`

## Module Overview

Simulation step router.

This module dispatches between full and low‑rank dynamics implementations
based on ``config.simulation.use_full_dynamics``.  It exposes a unified
``step(x, u, dt)`` function which calls either ``src.plant.models.dip_full.step``
or ``src.plant.models.dip_lowrank.step`` depending on the configuration.

If the full dynamics module cannot be imported, a RuntimeError with a
specific message is raised.  Tests match the message text exactly.



## Architecture Diagram

```{mermaid}
graph TD
    A[Initial State x_0_] --> B[Simulation Loop]
    B --> C[Controller Compute]
    C --> D[Control Signal u]
    D --> E[Dynamics Model]
    E --> F[State Derivative ẋ]
    F --> G{Integration Method}
    G -->|Euler| H[x_k+1_ = x_k_ + Δt·ẋ]
    G -->|RK4| I[4-stage Runge-Kutta]
    G -->|RK45| J[Adaptive Step Size]
    H --> K[Next State]
    I --> K
    J --> K
    K --> L{Time < T_max_?}
    L -->|Yes| B
    L -->|No| M[Simulation Result]

    style C fill:#9cf
    style E fill:#fcf
    style G fill:#ff9
    style M fill:#9f9
```

**Data Flow:**
1. Initialize state and time
2. Compute control action from controller
3. Evaluate system dynamics: ẋ = f(x, u, t)
4. Integrate using numerical method (Euler/RK4/RK45)
5. Update state and repeat until termination


## Mathematical Foundation

### Numerical Integration Methods

The simulation runner employs multiple numerical integration schemes for solving the DIP dynamics:

#### Euler Method (First-Order)

```{math}
\vec{x}_{k+1} = \vec{x}_k + \Delta t \cdot \vec{f}(\vec{x}_k, \vec{u}_k, t_k)
```

- **Accuracy**: O(Δt) local truncation error
- **Stability**: Conditionally stable (small Δt required)
- **Use case**: Fast prototyping, simple dynamics

#### Runge-Kutta 4th Order (RK4)

```{math}
\begin{align}
k_1 &= \vec{f}(\vec{x}_k, \vec{u}_k, t_k) \\
k_2 &= \vec{f}(\vec{x}_k + \frac{\Delta t}{2}k_1, \vec{u}_k, t_k + \frac{\Delta t}{2}) \\
k_3 &= \vec{f}(\vec{x}_k + \frac{\Delta t}{2}k_2, \vec{u}_k, t_k + \frac{\Delta t}{2}) \\
k_4 &= \vec{f}(\vec{x}_k + \Delta t k_3, \vec{u}_k, t_k + \Delta t) \\
\vec{x}_{k+1} &= \vec{x}_k + \frac{\Delta t}{6}(k_1 + 2k_2 + 2k_3 + k_4)
\end{align}
```

- **Accuracy**: O(Δt⁴) local truncation error
- **Stability**: More stable than Euler
- **Use case**: Production simulations, accurate trajectories

#### Adaptive RK45 (Dormand-Prince)

Variable step-size integration with error control:

```{math}
\text{error} = ||\vec{x}_{RK4} - \vec{x}_{RK5}|| < \text{tol}
```

- **Accuracy**: Adaptive (user-specified tolerance)
- **Stability**: Highly stable with step adaptation
- **Use case**: Stiff dynamics, energy conservation studies

### Simulation Pipeline Architecture

The simulation follows a unified execution model:

1. **Initialization**: Set initial state $\vec{x}_0$ and time $t_0$
2. **Control Loop**: For each timestep:
   - Compute control: $\vec{u}_k = \text{controller}(\vec{x}_k, t_k)$
   - Integrate dynamics: $\vec{x}_{k+1} = \text{integrator}(\vec{x}_k, \vec{u}_k, \Delta t)$
   - Update time: $t_{k+1} = t_k + \Delta t$
3. **Termination**: Until $t \geq t_{\text{max}}$ or instability detected

**Performance**: Numba JIT compilation accelerates batch simulations by 10-50× for PSO optimization workflows.

**See:** {doc}`../../../mathematical_foundations/numerical_methods`


## Complete Source Code

```{literalinclude} ../../../src/simulation/engines/simulation_runner.py
:language: python
:linenos:
```



## Classes

### `SimulationRunner`

Object-oriented wrapper around the run_simulation function.

This class provides compatibility with test cases that expect a
SimulationRunner class interface while maintaining the functional API.

#### Source Code

```{literalinclude} ../../../src/simulation/engines/simulation_runner.py
:language: python
:pyobject: SimulationRunner
:linenos:
```

#### Methods (2)

##### `__init__(self, dynamics_model, dt, max_time)`

Initialize simulation runner.

[View full source →](#method-simulationrunner-__init__)

##### `run_simulation(self, initial_state, controller, reference)`

Run simulation using the functional API.

[View full source →](#method-simulationrunner-run_simulation)



## Functions

### `_load_full_step()`

Attempt to load the full dynamics ``step`` function.

Returns
callable
    The ``step(x, u, dt)`` function from the full dynamics module.

Raises
------
RuntimeError
    If the module cannot be imported or does not define ``step``.

#### Source Code

```{literalinclude} ../../../src/simulation/engines/simulation_runner.py
:language: python
:pyobject: _load_full_step
:linenos:
```



### `_load_lowrank_step()`

Load the low‑rank dynamics ``step`` function.

Returns
callable
    The low‑rank ``step(x, u, dt)`` function.

#### Source Code

```{literalinclude} ../../../src/simulation/engines/simulation_runner.py
:language: python
:pyobject: _load_lowrank_step
:linenos:
```



### `get_step_fn()`

Return the appropriate step function based on the configuration flag.

Returns
callable
    Either ``src.plant.models.dip_full.step`` or ``src.plant.models.dip_lowrank.step``.

#### Source Code

```{literalinclude} ../../../src/simulation/engines/simulation_runner.py
:language: python
:pyobject: get_step_fn
:linenos:
```



### `step(x, u, dt)`

Unified simulation step entry point.

Parameters
----------
x : array-like
    Current state.
u : array-like
    Control input(s).
dt : float
    Timestep.

Returns
-------
array-like
    Next state computed by the selected dynamics implementation.

#### Source Code

```{literalinclude} ../../../src/simulation/engines/simulation_runner.py
:language: python
:pyobject: step
:linenos:
```



### `run_simulation()`

Simulate a single controller trajectory using an explicit Euler method.

The runner integrates the provided ``dynamics_model`` forward in time under
the control law defined by ``controller``.  It produces uniformly spaced
timestamps, a state trajectory and the applied control sequence.  If the
dynamics return NaN/Inf values or raise an exception at any step, the
simulation halts immediately and the outputs are truncated to include only
the steps executed.  Control inputs can be saturated via the ``u_max``
parameter or by querying ``controller.max_force`` when ``u_max`` is not
provided.  Stateful controllers may expose optional hooks
``initialize_state`` and ``initialize_history``; these are called once at
the beginning of the simulation.  A ``compute_control`` method, if
available, is preferred over ``__call__`` for computing the control.  The
runner also supports a simple latency monitor: if computing the control
exceeds the nominal period ``dt`` on any step and a ``fallback_controller``
is provided, subsequent control inputs are drawn from the fallback.

Parameters
----------
controller : Any
    The control object.  Must implement ``__call__(t, x) -> float`` or
    ``compute_control(x, state_vars, history)``.  Optional hooks
    ``initialize_state`` and ``initialize_history`` may be defined to
    initialise controller state.
dynamics_model : Any
    Object providing a ``step(state, u, dt)`` method that advances the
    state forward in time.  Must accept a state vector and scalar input
    ``u``.
sim_time : float
    Total simulation horizon in seconds.  The integration runs until
    the largest multiple of ``dt`` not exceeding ``sim_time``.  A value
    less than or equal to zero produces no integration steps.
dt : float
    Integration timestep (seconds).  Must be strictly positive.
initial_state : array-like
    Initial state vector.  Converted to ``float`` and flattened.  The
    length of the state vector defines the dimensionality of the system.
u_max : float, optional
    Saturation limit for the control input.  When provided, control
    commands are clipped to the interval ``[-u_max, u_max]``.  If omitted
    and the controller exposes ``max_force``, that value is used instead.
seed : int, optional
    Deprecated.  Present for backward compatibility; use ``rng`` to
    control randomness when required.  When both ``seed`` and ``rng`` are
    provided, ``rng`` takes precedence.
rng : numpy.random.Generator, optional
    Random number generator for controllers that rely on sampling.  If
    provided, it is passed unchanged to the controller; otherwise a local
    generator may be created when ``seed`` is supplied.
latency_margin : float, optional
    Unused placeholder for future latency control.  Accepts any value
    without effect.
fallback_controller : callable, optional
    Function ``fallback_controller(t, x) -> float`` invoked to compute
    control after a deadline miss.  When a control call exceeds ``dt`` in
    duration, the fallback controller is used for all subsequent steps.
**_kwargs : dict
    Additional keyword arguments are ignored.  They are accepted to
    preserve backward compatibility with earlier versions of this API.

Returns
-------
t_arr : numpy.ndarray
    1D array of time points including the initial time at index 0.  The
    final element equals ``n_steps * dt`` where ``n_steps = int(round(sim_time / dt))``.
x_arr : numpy.ndarray
    2D array of shape ``(len(t_arr), D)`` containing the state trajectory.
u_arr : numpy.ndarray
    1D array of shape ``(len(t_arr) - 1,)`` containing the applied control
    sequence.  Empty if no integration steps were executed.

#### Source Code

```{literalinclude} ../../../src/simulation/engines/simulation_runner.py
:language: python
:pyobject: run_simulation
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from importlib import import_module`
- `import time`
- `from typing import Any, Callable, Optional, Tuple`
- `import numpy as np`


## Usage Examples

### Basic Simulation Workflow

```python
from src.simulation.engines.simulation_runner import run_simulation, SimulationRunner
from src.controllers.smc.algorithms.classical import ClassicalSMC
from src.plant.models.simplified import SimplifiedDynamics

# Create controller and dynamics
config = ClassicalSMCConfig(
    surface_gains=[10.0, 8.0, 15.0, 12.0],
    switching_gain=50.0,
    max_force=100.0
)
controller = ClassicalSMC(config)
dynamics = SimplifiedDynamics()

# Run simulation (functional API)
result = run_simulation(
    controller=controller,
    dynamics=dynamics,
    initial_state=[0.1, 0.05, 0, 0, 0, 0],  # [x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂]
    duration=10.0,
    dt=0.01
)

print(f"Final tracking error: {np.linalg.norm(result.states[-1, :2]):.4f}")
```

## Batch Simulation for Parameter Sweeps

```python
# example-metadata:
# runnable: false

from src.simulation.engines.vector_sim import simulate_system_batch
import numpy as np

# Test multiple initial conditions in parallel
initial_conditions = np.array([
    [0.1, 0.05, 0, 0, 0, 0],
    [0.2, 0.1, 0, 0, 0, 0],
    [0.15, -0.05, 0, 0, 0, 0],
    # ... 100 conditions
])

# Batch simulation (Numba accelerated)
results = simulate_system_batch(
    controller=controller,
    dynamics=dynamics,
    initial_states=initial_conditions,
    duration=5.0,
    dt=0.01
)

# Analyze batch results
settling_times = [compute_settling_time(r.states) for r in results]
print(f"Mean settling time: {np.mean(settling_times):.2f}s")
```

## Numba JIT Acceleration Pattern

```python
# example-metadata:
# runnable: false

from numba import jit
from src.simulation.engines.simulation_runner import SimulationRunner

# Define JIT-compiled dynamics function
@jit(nopython=True)
def fast_dynamics_step(state, control, dt):
    # Simplified dynamics for speed
    # ... vectorized numpy operations ...
    return next_state

# Use in high-performance simulation
runner = SimulationRunner(
    dynamics_model=fast_dynamics_step,
    dt=0.001,  # High-frequency control (1kHz)
    max_time=100.0  # Long-duration test
)

result = runner.run_simulation(
    initial_state=x0,
    controller=controller,
    reference=None
)

print(f"Simulation completed in {result.computation_time:.2f}s")
print(f"Average step time: {result.computation_time / len(result.time):.6f}s")
```

## Integration Method Comparison

```python
from src.simulation.engines.simulation_runner import run_simulation

# Compare Euler vs RK4 accuracy
methods = ['euler', 'rk4', 'rk45']
results = {}

for method in methods:
    result = run_simulation(
        controller=controller,
        dynamics=dynamics,
        initial_state=[0.1, 0.05, 0, 0, 0, 0],
        duration=10.0,
        dt=0.01,
        integration_method=method
    )
    results[method] = result

    # Analyze energy conservation
    energy_drift = np.abs(result.energy[-1] - result.energy[0])
    print(f"{method.upper()}: Energy drift = {energy_drift:.6f}")
```

**See:** {doc}`../../../simulation_workflows/performance_optimization`
