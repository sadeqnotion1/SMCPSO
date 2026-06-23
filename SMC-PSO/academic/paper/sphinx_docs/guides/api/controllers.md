# Controllers API Guide

**Module:** `src.controllers`

**What This API Does:**
This API provides functions to create and configure controllers for the double-inverted pendulum system. Instead of writing controller code from scratch, you use these factory functions to create pre-built controllers with your desired settings.

**Who This Is For:**
- Python developers integrating controllers into applications
- Researchers running controller experiments
- Anyone automating simulations or optimization workflows

**Level:** Intermediate to Advanced

**Quick Start:**
```python
# Create a controller in 2 lines
from src.controllers import create_controller
from src.config import load_config

config = load_config('config.yaml')
controller = create_controller('classical_smc', config.controllers.classical_smc)
```

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Factory System](#factory-system)
- [Controller Types](#controller-types)
- [Custom Controllers](#custom-controllers)
- [Integration Patterns](#integration-patterns)
- [Troubleshooting](#troubleshooting)



## Overview

**What "Factory System" Means:**
A factory is a function that creates objects for you. Instead of manually calling `ClassicalSMC(...)` with many parameters, you call `create_controller('classical_smc', config)` and the factory handles the details.

**Why Use This API:**
The Controllers API provides a clean, type-safe factory system for creating and configuring sliding mode controllers (SMC) for the double-inverted pendulum system. It saves you from writing boilerplate code and reduces errors.

**Key Features:**
- ✅ **Factory Pattern** - Create controllers with one function call
  - `create_controller()` for general use
  - `create_smc_for_pso()` for optimization workflows

- ✅ **4 SMC Variants** - Choose the right controller for your needs
  - Classical SMC (simple, robust)
  - Super-Twisting (reduces chattering)
  - Adaptive SMC (auto-adjusts gains)
  - Hybrid Adaptive STA-SMC (combines adaptive + super-twisting)

- ✅ **Type Safety** - Enum-based selection prevents typos and errors
- ✅ **PSO Integration** - Built-in support for automated gain tuning
- ✅ **Extensible** - Base classes for building custom controllers

**Related Documentation:**
- [Tutorial 02: Controller Comparison](../tutorials/tutorial-02-controller-comparison.md)
- [Tutorial 04: Custom Controller](../tutorials/tutorial-04-custom-controller.md)
- [How-To: Running Simulations](../how-to/running-simulations.md)

**Theory & Foundations:**
- [SMC Theory Guide](../theory/smc-theory.md): Mathematical foundations and design principles



## Architecture

### Controller Hierarchy

```
BaseController (Abstract)
├── ClassicalSMC
├── SuperTwistingSMC (STA-SMC)
├── AdaptiveSMC
└── HybridAdaptiveSTASMC
```

### Key Design Principles

1. **Single Responsibility:** Each controller implements one SMC variant
2. **Configuration First:** All parameters via config objects
3. **Stateless Computation:** `compute_control()` is pure function
4. **Type Safety:** Enums for controller selection, dataclasses for config



## Factory System

### Two Factory Functions

```python
from src.controllers import create_controller, create_smc_for_pso

# Option 1: Full configuration (recommended for general use)
controller = create_controller(
    controller_type='classical_smc',
    config=config.controllers.classical_smc
)

# Option 2: PSO-optimized (recommended for optimization workflows)
controller = create_smc_for_pso(
    smc_type=SMCType.CLASSICAL,
    gains=[10, 8, 15, 12, 50, 5],
    max_force=100.0
)
```

## When to Use Each

| Function | Use Case | Input | Configuration |
|----------|----------|-------|---------------|
| `create_controller()` | General simulation | String name | Full config object |
| `create_smc_for_pso()` | PSO optimization | SMCType enum | Gains array only |

### SMCType Enum

```python
from src.controllers import SMCType

# Available controller types
SMCType.CLASSICAL           # Classical sliding mode control
SMCType.SUPER_TWISTING      # Super-twisting algorithm (STA)
SMCType.ADAPTIVE            # Adaptive SMC with online gain tuning
SMCType.HYBRID              # Hybrid Adaptive STA-SMC
```

## Complete Example: create_controller()

```python
from src.config import load_config
from src.controllers import create_controller

# Load configuration
config = load_config('config.yaml')

# Create controller with full configuration
controller = create_controller(
    controller_type='classical_smc',
    config=config.controllers.classical_smc
)

# Alternatively, specify config inline
from src.config.schemas import ClassicalSMCConfig

controller = create_controller(
    controller_type='classical_smc',
    config=ClassicalSMCConfig(
        gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0],
        max_force=100.0,
        boundary_layer=0.01
    )
)
```

## Complete Example: create_smc_for_pso()

```python
from src.controllers import create_smc_for_pso, SMCType

# Minimal PSO-friendly creation
controller = create_smc_for_pso(
    smc_type=SMCType.CLASSICAL,
    gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0],
    max_force=100.0,
    boundary_layer=0.01  # Optional parameter
)

# Used in PSO fitness function
def fitness_function(gains_array):
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains_array)
    result = simulate(controller)
    return result['cost']
```

## Gain Bounds Helper

```python
from src.controllers import get_gain_bounds_for_pso

# Get recommended bounds for each controller type
bounds_classical = get_gain_bounds_for_pso(SMCType.CLASSICAL)
# Returns: [(0.1, 50), (0.1, 50), (0.1, 50), (0.1, 50), (1.0, 200), (0.0, 50)]

bounds_adaptive = get_gain_bounds_for_pso(SMCType.ADAPTIVE)
# Returns: [(0.1, 50), (0.1, 50), (0.1, 50), (0.1, 50), (0.01, 10)]

# Use with PSO
from src.optimizer import PSOTuner

tuner = PSOTuner(
    controller_type=SMCType.CLASSICAL,
    bounds=bounds_classical,
    n_particles=30,
    iters=100
)
```

## Gain Validation

```python
from src.controllers import validate_smc_gains

# Validate gains before simulation
gains = [10, 8, 15, 12, 50, 5]
is_valid = validate_smc_gains(SMCType.CLASSICAL, gains)

if not is_valid:
    raise ValueError("Invalid gains for Classical SMC")

# Validation checks:
# - Correct number of gains for controller type
# - All gains positive (except epsilon can be 0)
# - Gains within physical bounds
```



## Controller Types

### 1. Classical SMC

**Purpose:** Baseline sliding mode controller with boundary layer for chattering reduction

**Gains:** `[k1, k2, λ1, λ2, K, ε]` (6 gains)
- `k1, k2`: First pendulum sliding surface coefficients
- `λ1, λ2`: Second pendulum sliding surface coefficients
- `K`: Switching gain (control authority)
- `ε`: Boundary layer thickness (chattering reduction)

**Configuration:**

```python
from src.controllers import create_controller

controller = create_controller(
    'classical_smc',
    config=config.controllers.classical_smc
)
```

**config.yaml:**
```yaml
controllers:
  classical_smc:
    gains: [10.0, 8.0, 15.0, 12.0, 50.0, 5.0]
    max_force: 100.0
    boundary_layer: 0.01
```

**Characteristics:**
- ✅ Simple and well-understood
- ✅ Fast computation
- ⚠️ Moderate chattering
- ⚠️ Fixed gains (no adaptation)

**Best For:** Prototyping, known systems, baseline comparisons

**Example:**

```python
from src.controllers import create_smc_for_pso, SMCType
import numpy as np

# Create controller
controller = create_smc_for_pso(
    SMCType.CLASSICAL,
    gains=[10, 8, 15, 12, 50, 5],
    max_force=100.0
)

# Compute control
state = np.array([0, 0, 0.1, 0, 0.15, 0])  # [x, dx, θ₁, dθ₁, θ₂, dθ₂]
state_vars = {}
history = controller.initialize_history()

control, state_vars, history = controller.compute_control(state, state_vars, history)
print(f"Control force: {control:.2f} N")
```



## 2. Super-Twisting SMC (STA-SMC)

**Purpose:** Second-order sliding mode for continuous control and finite-time convergence

**Gains:** `[k1, k2, λ1, λ2, α, β]` (6 gains)
- `k1, k2, λ1, λ2`: Sliding surface coefficients (same as classical)
- `α`: First super-twisting gain
- `β`: Second super-twisting gain

**Configuration:**

```python
controller = create_controller(
    'sta_smc',
    config=config.controllers.sta_smc
)
```

**config.yaml:**
```yaml
controllers:
  sta_smc:
    gains: [25.0, 10.0, 15.0, 12.0, 20.0, 15.0]
    max_force: 100.0
    dt: 0.01  # Required for super-twisting integration
```

**Characteristics:**
- ✅ Smooth control (no chattering)
- ✅ Finite-time convergence
- ✅ Robust to matched disturbances
- ⚠️ Slightly higher computational cost

**Best For:** Chattering-sensitive applications, smooth control requirements

**Example:**

```python
# example-metadata:
# runnable: false

# Create super-twisting controller
controller = create_smc_for_pso(
    SMCType.SUPER_TWISTING,
    gains=[25, 10, 15, 12, 20, 15],
    max_force=100.0,
    dt=0.01  # Required for STA integration
)

# STA maintains internal state for integration
state = np.array([0, 0, 0.1, 0, 0.15, 0])
state_vars = {}
history = controller.initialize_history()

# First call initializes integrator
control1, state_vars, history = controller.compute_control(state, state_vars, history)

# Subsequent calls use integrated state
control2, state_vars, history = controller.compute_control(state, state_vars, history)
```



## 3. Adaptive SMC

**Purpose:** Online gain adaptation for uncertain systems

**Gains:** `[k1, k2, λ1, λ2, γ]` (5 gains)
- `k1, k2, λ1, λ2`: Initial sliding surface coefficients
- `γ`: Adaptation rate (how fast gains adjust)

**Additional Parameters:**
- `leak_rate`: Prevent unbounded gain growth
- `rate_limit`: Maximum adaptation speed

**Configuration:**

```python
controller = create_controller(
    'adaptive_smc',
    config=config.controllers.adaptive_smc
)
```

**config.yaml:**
```yaml
controllers:
  adaptive_smc:
    gains: [10.0, 8.0, 15.0, 12.0, 0.5]  # Note: only 5 gains
    max_force: 100.0
    adaptation_rate: 0.5
    leak_rate: 0.1
    rate_limit: 10.0
```

**Characteristics:**
- ✅ Adapts to parameter variations
- ✅ Robust to disturbances
- ✅ No retuning needed
- ⚠️ Slower initial response
- ⚠️ Requires monitoring adaptation trajectory

**Best For:** Unknown/varying systems, parameter uncertainty

**Example:**

```python
# example-metadata:
# runnable: false

# Create adaptive controller
controller = create_smc_for_pso(
    SMCType.ADAPTIVE,
    gains=[10, 8, 15, 12, 0.5],  # Only 5 gains
    max_force=100.0
)

# Adaptive SMC tracks gain evolution
state = np.array([0, 0, 0.1, 0, 0.15, 0])
state_vars = {}
history = controller.initialize_history()

# Gains adapt during simulation
for i in range(1000):
    control, state_vars, history = controller.compute_control(state, state_vars, history)

    # Monitor adapted gains
    if 'adapted_gains' in state_vars:
        print(f"Step {i}: Adapted gains = {state_vars['adapted_gains']}")
```



### 4. Hybrid Adaptive STA-SMC

**Purpose:** Combines adaptation with super-twisting for maximum performance

**Gains:** `[k1, k2, λ1, λ2]` (4 gains)
- `k1, k2, λ1, λ2`: Initial sliding surface coefficients
- Super-twisting gains (α, β) computed automatically
- Adaptation enabled via `enable_adaptation=True`

**Configuration:**

```python
controller = create_controller(
    'hybrid_adaptive_sta_smc',
    config=config.controllers.hybrid_adaptive_sta_smc
)
```

**config.yaml:**
```yaml
controllers:
  hybrid_adaptive_sta_smc:
    gains: [15.0, 12.0, 18.0, 15.0]  # Only 4 gains
    max_force: 100.0
    dt: 0.01
    enable_adaptation: true
    adaptation_rate: 0.3
```

**Characteristics:**
- ✅ Best overall performance
- ✅ Smooth control + adaptation
- ✅ Handles uncertainty and disturbances
- ⚠️ Most complex configuration
- ⚠️ Highest computational cost

**Best For:** Research applications, maximum performance requirements

**Example:**

```python
# example-metadata:
# runnable: false

# Create hybrid controller
controller = create_smc_for_pso(
    SMCType.HYBRID,
    gains=[15, 12, 18, 15],  # Only 4 gains
    max_force=100.0,
    dt=0.01
)

# Hybrid combines STA integration with adaptation
state = np.array([0, 0, 0.1, 0, 0.15, 0])
state_vars = {}
history = controller.initialize_history()

control, state_vars, history = controller.compute_control(state, state_vars, history)

# Monitor both STA state and adapted gains
print(f"Control: {control:.2f} N")
print(f"STA state: {state_vars.get('sta_integrator_state', 'N/A')}")
print(f"Adapted gains: {state_vars.get('adapted_gains', 'N/A')}")
```



## Controller Comparison

| Controller | Gains | Chattering | Speed | Adaptation | Complexity | Best Use Case |
|------------|-------|------------|-------|------------|------------|---------------|
| **Classical** | 6 | Moderate | Fast | None | Low | Prototyping, baseline |
| **STA** | 6 | None | Good | None | Medium | Smooth control |
| **Adaptive** | 5 | Moderate | Slower | Yes | Medium | Uncertain systems |
| **Hybrid** | 4 | None | Fast | Yes | High | Maximum performance |



## Custom Controllers

### Implementing a Custom Controller

**Step 1: Define your controller class**

```python
# my_custom_controller.py
import numpy as np
from src.controllers.base import BaseController

class TerminalSMC(BaseController):
    """Terminal sliding mode controller with finite-time convergence."""

    def __init__(self, gains, max_force=100.0, alpha=0.5):
        """
        Parameters
        # ---------- (RST section marker)
        gains : list[float]
            [k1, k2, λ1, λ2, K, p, q] where p/q < 1
        max_force : float
            Control saturation limit
        alpha : float
            Terminal attractor exponent
        """
        super().__init__(max_force=max_force)

        if len(gains) != 7:
            raise ValueError("Terminal SMC requires 7 gains")

        self.k1, self.k2, self.lam1, self.lam2 = gains[:4]
        self.K, self.p, self.q = gains[4:]
        self.alpha = alpha

    def compute_control(self, state, state_vars, history):
        """Compute terminal SMC control law."""
        x, dx, theta1, dtheta1, theta2, dtheta2 = state

        # Terminal sliding surface
        s = (self.k1 * theta1 + self.k2 * dtheta1 +
             self.lam1 * theta2 + self.lam2 * dtheta2)

        # Terminal attractor term
        terminal_term = np.sign(s) * np.abs(s)**(self.p / self.q)

        # Control law
        u = -self.K * (s + self.alpha * terminal_term)

        # Saturate
        u = np.clip(u, -self.max_force, self.max_force)

        # Update history
        history['sliding_surface'].append(s)
        history['control'].append(u)

        return u, state_vars, history

    def initialize_history(self):
        """Initialize history tracking."""
        return {
            'sliding_surface': [],
            'control': []
        }
```

**Step 2: Register with factory (optional)**

```python
# In src/controllers/factory/__init__.py
from .my_custom_controller import TerminalSMC

_CONTROLLER_REGISTRY = {
    'classical_smc': ClassicalSMC,
    'sta_smc': SuperTwistingSMC,
    'adaptive_smc': AdaptiveSMC,
    'hybrid_adaptive_sta_smc': HybridAdaptiveSTASMC,
    'terminal_smc': TerminalSMC,  # Add custom controller
}
```

**Step 3: Use your custom controller**

```python
from my_custom_controller import TerminalSMC

# Direct instantiation
controller = TerminalSMC(
    gains=[10, 8, 15, 12, 50, 5, 7],
    max_force=100.0,
    alpha=0.5
)

# Or via factory (if registered)
from src.controllers import create_controller

controller = create_controller(
    'terminal_smc',
    config=terminal_smc_config
)
```

**Step 4: Test your controller**

```python
# tests/test_controllers/test_terminal_smc.py
import pytest
import numpy as np
from my_custom_controller import TerminalSMC

def test_initialization():
    """Test controller initializes correctly."""
    controller = TerminalSMC(gains=[10, 8, 15, 12, 50, 5, 7])
    assert controller.K == 50.0
    assert controller.p == 5.0
    assert controller.q == 7.0

def test_compute_control():
    """Test control computation."""
    controller = TerminalSMC(gains=[10, 8, 15, 12, 50, 5, 7])
    state = np.array([0, 0, 0.1, 0, 0.15, 0])

    control, state_vars, history = controller.compute_control(
        state, {}, controller.initialize_history()
    )

    assert isinstance(control, (float, np.floating))
    assert abs(control) <= 100.0  # Saturation check

def test_saturation():
    """Test control saturates at max_force."""
    controller = TerminalSMC(gains=[10, 8, 15, 12, 500, 5, 7], max_force=100.0)
    state = np.array([0, 0, 0.5, 0, 0.6, 0])  # Large errors

    control, _, _ = controller.compute_control(state, {}, controller.initialize_history())

    assert abs(control) == 100.0
```

See [Tutorial 04: Custom Controller](../tutorials/tutorial-04-custom-controller.md) for complete walkthrough.



## Integration Patterns

### Pattern 1: Single Simulation

```python
from src.config import load_config
from src.controllers import create_controller
from src.core import SimulationRunner

config = load_config('config.yaml')
controller = create_controller('classical_smc', config=config.controllers.classical_smc)
runner = SimulationRunner(config)

result = runner.run(controller)
print(f"ISE: {result['metrics']['ise']:.4f}")
```

### Pattern 2: Controller Comparison

```python
from src.controllers import SMCType, create_smc_for_pso

controllers = {
    'Classical': create_smc_for_pso(SMCType.CLASSICAL, [10, 8, 15, 12, 50, 5]),
    'STA': create_smc_for_pso(SMCType.SUPER_TWISTING, [25, 10, 15, 12, 20, 15], dt=0.01),
    'Adaptive': create_smc_for_pso(SMCType.ADAPTIVE, [10, 8, 15, 12, 0.5]),
    'Hybrid': create_smc_for_pso(SMCType.HYBRID, [15, 12, 18, 15], dt=0.01),
}

for name, controller in controllers.items():
    result = runner.run(controller)
    print(f"{name}: ISE={result['metrics']['ise']:.4f}")
```

### Pattern 3: PSO Optimization Loop

```python
from src.optimizer import PSOTuner
from src.controllers import SMCType, get_gain_bounds_for_pso

bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)
tuner = PSOTuner(controller_type=SMCType.CLASSICAL, bounds=bounds)

best_gains, best_cost = tuner.optimize()

# Use optimized controller
controller = create_smc_for_pso(SMCType.CLASSICAL, best_gains)
result = runner.run(controller)
```



## Troubleshooting

### Problem: "ValueError: Requires X gains, got Y"

**Cause:** Wrong number of gains for controller type

**Solution:**
```python
# Classical and STA: 6 gains
controller = create_smc_for_pso(SMCType.CLASSICAL, [10, 8, 15, 12, 50, 5])

# Adaptive: 5 gains
controller = create_smc_for_pso(SMCType.ADAPTIVE, [10, 8, 15, 12, 0.5])

# Hybrid: 4 gains
controller = create_smc_for_pso(SMCType.HYBRID, [15, 12, 18, 15])
```

## Problem: Control saturates immediately

**Cause:** Gains too large or initial conditions too extreme

**Solution:**
1. Reduce switching gain `K`
2. Use smaller initial perturbations
3. Increase `max_force` limit

```python
# Before: Saturates
controller = create_smc_for_pso(SMCType.CLASSICAL, [10, 8, 15, 12, 500, 5], max_force=100)

# After: Reduced gains
controller = create_smc_for_pso(SMCType.CLASSICAL, [10, 8, 15, 12, 50, 5], max_force=100)
```

## Problem: Excessive chattering

**Cause:** Boundary layer too small or classical SMC with sharp switching

**Solution:**
1. Increase boundary layer `ε`
2. Use STA-SMC for smooth control

```python
# Classical with larger boundary layer
controller = create_smc_for_pso(SMCType.CLASSICAL, [10, 8, 15, 12, 50, 10])  # ε=10

# Or switch to STA for inherently smooth control
controller = create_smc_for_pso(SMCType.SUPER_TWISTING, [25, 10, 15, 12, 20, 15], dt=0.01)
```

## Problem: STA-SMC requires dt parameter

**Cause:** Super-twisting algorithm needs timestep for integration

**Solution:**
```python
# Must specify dt for STA and Hybrid controllers
controller = create_smc_for_pso(SMCType.SUPER_TWISTING, gains, dt=0.01)
controller = create_smc_for_pso(SMCType.HYBRID, gains, dt=0.01)
```



## Next Steps

- **Learn by doing:** [Tutorial 02: Controller Comparison](../tutorials/tutorial-02-controller-comparison.md)
- **Implement custom:** [Tutorial 04: Custom Controller](../tutorials/tutorial-04-custom-controller.md)
- **Optimize gains:** [Optimization API Guide](optimization.md)
- **Technical details:** [Controllers Technical Reference](../../reference/controllers/__init__.md)



**Last Updated:** October 2025
