# Controllers Module

**Total Files**: 58
**Test Coverage**: 95%
**Status**: Stable

---

## Overview

The controllers module implements various control algorithms for stabilizing a double-inverted pendulum (DIP) system. It provides Sliding Mode Control (SMC) variants, Model Predictive Control (MPC), specialized controllers (swing-up), and a factory pattern for controller instantiation.

---

## Directory Structure

```
src/controllers/                (58 files total)
├── base/                       Base classes and interfaces
│   ├── controller_base.py      Abstract controller interface
│   └── smc_base.py             SMC-specific base class
│
├── smc/                        Sliding Mode Control variants
│   ├── classical_smc.py        Classical SMC (most commonly used)
│   ├── adaptive_smc.py         Adaptive SMC (for parameter uncertainty)
│   ├── sta_smc.py              Super-Twisting Algorithm SMC
│   └── hybrid_adaptive_sta_smc.py  Hybrid adaptive+STA variant
│
├── mpc/                        Model Predictive Control
│   └── mpc_controller.py       MPC implementation (experimental)
│
├── specialized/                Special-purpose controllers
│   ├── swing_up_smc.py         Swing-up controller
│   └── lqr_controller.py       Linear Quadratic Regulator (reference)
│
└── factory/                    Controller instantiation system
    ├── __init__.py             Main factory interface
    ├── controller_registry.py  Controller registration
    └── validation.py           Controller parameter validation
```

---

## Controller Types

### 1. Classical SMC (`smc/classical_smc.py`)

**Purpose**: Standard sliding mode control with discontinuous switching.

**Use Case**: General stabilization with robust performance.

**Key Features**:
- Discontinuous control law
- Robust to matched disturbances
- Chattering mitigation via boundary layer

**Example**:
```python
from src.controllers.smc.classical_smc import ClassicalSMC

controller = ClassicalSMC(
    gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],  # [k1, k2, k3, k4, k5, k6]
    config={'boundary_layer': 0.01}
)

u = controller.compute_control(state)
```

**Tuning**: Use PSO optimizer to find optimal gains.

---

### 2. Adaptive SMC (`smc/adaptive_smc.py`)

**Purpose**: SMC with online parameter adaptation for uncertain systems.

**Use Case**: When system parameters (mass, inertia) are unknown or varying.

**Key Features**:
- Online gain adaptation
- Reduced chattering
- Better performance under uncertainty

**Example**:
```python
from src.controllers.smc.adaptive_smc import AdaptiveSMC

controller = AdaptiveSMC(
    gains=[10.0, 5.0, 8.0, 3.0],
    config={
        'adaptation_rate': 0.1,
        'adaptation_bounds': (0.1, 100.0)
    }
)

u = controller.compute_control(state, last_control=u_prev, history=state_history)
```

**Note**: Requires state history for adaptation.

---

### 3. Super-Twisting Algorithm SMC (`smc/sta_smc.py`)

**Purpose**: Higher-order SMC with continuous control (no chattering).

**Use Case**: When smooth control is required (hardware-friendly).

**Key Features**:
- Continuous control law (no chattering)
- Finite-time convergence
- Robust to disturbances

**Example**:
```python
from src.controllers.smc.sta_smc import STASMC

controller = STASMC(
    gains=[5.0, 3.0, 4.0, 2.0],
    config={'alpha': 0.5}  # STA parameter
)

u = controller.compute_control(state)
```

---

### 4. Hybrid Adaptive STA-SMC (`smc/hybrid_adaptive_sta_smc.py`)

**Purpose**: Combines adaptation with super-twisting for best of both worlds.

**Use Case**: Uncertain systems requiring smooth control.

**Key Features**:
- Online adaptation + continuous control
- Excellent performance in research benchmarks
- More complex tuning

**Example**:
```python
from src.controllers.smc.hybrid_adaptive_sta_smc import HybridAdaptiveSTASMC

controller = HybridAdaptiveSTASMC(
    gains=[8.0, 4.0, 6.0, 3.0],
    config={
        'adaptation_rate': 0.15,
        'alpha': 0.5,
        'boundary_layer': 0.01
    }
)

u = controller.compute_control(state, last_control=u_prev, history=state_history)
```

---

### 5. MPC Controller (`mpc/mpc_controller.py`)

**Purpose**: Model Predictive Control with optimization-based control.

**Status**: Experimental

**Key Features**:
- Constraint handling
- Predictive optimization
- Computational cost

**Example**:
```python
from src.controllers.mpc.mpc_controller import MPCController

controller = MPCController(
    prediction_horizon=10,
    control_horizon=5,
    config={'Q': ..., 'R': ..., 'constraints': ...}
)

u = controller.compute_control(state)
```

**Note**: Requires optimization solver (CVXPY). Slower than SMC variants.

---

### 6. Swing-Up Controller (`specialized/swing_up_smc.py`)

**Purpose**: Energy-based swing-up from downward position.

**Use Case**: Starting from pendant (downward) configuration.

**Key Features**:
- Energy shaping control
- Automatic switching to stabilization
- Two-phase control

**Example**:
```python
from src.controllers.specialized.swing_up_smc import SwingUpSMC

swing_up = SwingUpSMC(gains=[...], config={'energy_threshold': 0.95})
stabilizer = ClassicalSMC(gains=[...])

if swing_up.is_swung_up(state):
    u = stabilizer.compute_control(state)
else:
    u = swing_up.compute_control(state)
```

---

## Factory Pattern Usage

### Basic Usage

```python
from src.controllers.factory import create_controller

# Create controller from config
controller = create_controller(
    controller_type='classical_smc',
    config=controller_config,
    gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
)

# Use controller
u = controller.compute_control(state)
```

### Available Controller Types

| String ID | Class | Module |
|-----------|-------|--------|
| `'classical_smc'` | ClassicalSMC | `smc/classical_smc.py` |
| `'adaptive_smc'` | AdaptiveSMC | `smc/adaptive_smc.py` |
| `'sta_smc'` | STASMC | `smc/sta_smc.py` |
| `'hybrid_adaptive_sta_smc'` | HybridAdaptiveSTASMC | `smc/hybrid_adaptive_sta_smc.py` |
| `'mpc'` | MPCController | `mpc/mpc_controller.py` |
| `'swing_up_smc'` | SwingUpSMC | `specialized/swing_up_smc.py` |

### Configuration Integration

```python
from src.config import load_config

# Load from config.yaml
config = load_config('config.yaml')

# Create controller from config
controller = create_controller(
    controller_type=config.controller.type,
    config=config.controller,
    gains=config.controller.gains
)
```

---

## Adding a New Controller

### Step 1: Create Controller Class

Create a new file in the appropriate subdirectory (`smc/`, `mpc/`, or `specialized/`):

```python
# src/controllers/smc/new_smc_variant.py
from src.controllers.base.controller_base import BaseController
import numpy as np

class NewSMCVariant(BaseController):
    """
    Brief description of new SMC variant.

    This controller implements [describe innovation/difference from existing].

    Args:
        gains: Control gains [k1, k2, ...]
        config: Controller configuration dict

    Example:
        >>> controller = NewSMCVariant(gains=[10, 5, 8, 3], config={...})
        >>> u = controller.compute_control(state)
    """
    def __init__(self, gains, config=None):
        super().__init__(gains, config)

        # Extract config parameters
        self.custom_param = config.get('custom_param', 1.0) if config else 1.0

        # Initialize internal state
        self._previous_sliding = 0.0

    def compute_control(self, state, last_control=0.0, history=None):
        """
        Compute control signal for current state.

        Args:
            state: State vector [theta1, theta2, theta1_dot, theta2_dot]
            last_control: Previous control input (for adaptive variants)
            history: State history (for adaptive variants)

        Returns:
            control: Control signal u (scalar)
        """
        # Implement control law
        s = self._compute_sliding_surface(state)
        u = -self.gains[0] * np.sign(s) - self.gains[1] * s

        # Apply saturation
        u = np.clip(u, -self.u_max, self.u_max)

        return u

    def _compute_sliding_surface(self, state):
        """Compute sliding surface."""
        # Implement sliding surface computation
        s = self.gains[2] * state[0] + self.gains[3] * state[2]
        return s
```

### Step 2: Add Configuration Schema

Update `config.yaml`:

```yaml
controller:
  type: new_smc_variant
  gains: [10.0, 5.0, 8.0, 3.0]
  custom_param: 1.0
```

### Step 3: Register in Factory

Update `src/controllers/factory/controller_registry.py`:

```python
from src.controllers.smc.new_smc_variant import NewSMCVariant

CONTROLLER_REGISTRY = {
    'classical_smc': ClassicalSMC,
    'adaptive_smc': AdaptiveSMC,
    'new_smc_variant': NewSMCVariant,  # Add here
    # ...
}
```

### Step 4: Create Tests

Create `tests/test_controllers/test_smc/test_new_smc_variant.py`:

```python
import pytest
import numpy as np
from src.controllers.smc.new_smc_variant import NewSMCVariant

def test_new_smc_initialization():
    """Test controller initialization."""
    controller = NewSMCVariant(gains=[10, 5, 8, 3])
    assert controller.gains == [10, 5, 8, 3]

def test_new_smc_compute_control():
    """Test control computation."""
    controller = NewSMCVariant(gains=[10, 5, 8, 3])
    state = np.array([0.1, 0.05, 0.0, 0.0])
    u = controller.compute_control(state)

    assert isinstance(u, (float, np.number))
    assert -controller.u_max <= u <= controller.u_max

def test_new_smc_closed_loop_stability():
    """Test closed-loop stability."""
    # Integration test with plant
    from src.plant.models.simplified.simplified_dynamics import SimplifiedDynamics
    from src.simulation.engines.simulation_runner import SimulationRunner

    controller = NewSMCVariant(gains=[10, 5, 8, 3])
    plant = SimplifiedDynamics()
    runner = SimulationRunner(controller, plant)

    result = runner.run(t_final=5.0)

    # Verify stability (final state near zero)
    final_state = result['states'][-1]
    assert np.linalg.norm(final_state) < 0.1
```

### Step 5: Update Documentation

1. Add to this README under "Controller Types"
2. Update `src/ARCHITECTURE.md` if significant change
3. Add to `docs/guides/controllers.md`

### Testing Requirements

- **Unit tests**: ≥95% coverage
  - Initialization
  - Control computation
  - Edge cases (saturated control, zero gains)
- **Integration tests**: Closed-loop stability
  - With simplified plant
  - With full nonlinear plant
- **Benchmark tests**: Performance vs baselines
  - ISE (Integral Squared Error)
  - Settling time
  - Overshoot

Run tests:
```bash
python -m pytest tests/test_controllers/test_smc/test_new_smc_variant.py -v
```

---

## PSO Optimization Integration

All controllers can be tuned using PSO:

```python
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.controllers.factory import create_controller

# Define bounds for gains
bounds = [(0.1, 20.0)] * 6  # 6 gains

# Create tuner
tuner = PSOTuner(
    controller_type='classical_smc',
    bounds=bounds,
    config=pso_config
)

# Run optimization
best_gains, best_cost = tuner.optimize()

# Create tuned controller
controller = create_controller('classical_smc', gains=best_gains)
```

See `src/optimization/README.md` for details.

---

## Configuration System

Controllers support configuration via `config.yaml`:

```yaml
controller:
  type: classical_smc           # Controller type
  gains: [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]  # Control gains

  # Controller-specific parameters
  boundary_layer: 0.01          # SMC boundary layer
  adaptation_rate: 0.1          # Adaptive SMC
  alpha: 0.5                    # STA parameter

  # Common parameters
  u_max: 50.0                   # Control saturation
  dt: 0.01                      # Sampling time
```

Load configuration:
```python
from src.config import load_config

config = load_config('config.yaml')
controller = create_controller(
    controller_type=config.controller.type,
    gains=config.controller.gains,
    config=config.controller
)
```

---

## Performance Benchmarks

Typical performance metrics (simplified plant, 5s simulation):

| Controller | ISE | Settling Time | Overshoot | Chattering |
|------------|-----|---------------|-----------|------------|
| Classical SMC | 0.025 | 1.2s | 5% | Medium |
| Adaptive SMC | 0.018 | 1.0s | 3% | Low |
| STA-SMC | 0.020 | 1.1s | 4% | None |
| Hybrid Adaptive STA | 0.015 | 0.9s | 2% | None |
| MPC | 0.030 | 1.5s | 2% | None |

See `benchmarks/` for complete benchmark results and reproduction scripts.

---

## Common Issues & Troubleshooting

### Issue: Controller saturates immediately

**Cause**: Gains too high or initial state too far from equilibrium.

**Solution**: Reduce gains or use swing-up controller first:
```python
# Use swing-up to bring system near upright first
if not near_equilibrium(state):
    u = swing_up_controller.compute_control(state)
else:
    u = stabilizer.compute_control(state)
```

### Issue: Chattering in control signal

**Cause**: Discontinuous switching in classical SMC.

**Solutions**:
1. Increase boundary layer: `config={'boundary_layer': 0.05}`
2. Use STA-SMC (continuous control)
3. Use adaptive SMC (reduces chattering)

### Issue: Unstable closed-loop behavior

**Cause**: Poorly tuned gains.

**Solutions**:
1. Use PSO optimization to find gains
2. Start with conservative gains and increase gradually
3. Check plant model matches actual system

### Issue: ImportError for deprecated paths

**Error**: `from src.controllers.classical_smc import ClassicalSMC`

**Solution**: Update to canonical path:
```python
from src.controllers.smc.classical_smc import ClassicalSMC
```

See `src/deprecated/README.md` for migration guides.

---

## References

- **Architecture**: `src/ARCHITECTURE.md`
- **Configuration**: `config.yaml`, `src/config/README.md`
- **Optimization**: `src/optimization/README.md`
- **Testing**: `tests/test_controllers/`
- **Benchmarks**: `benchmarks/`
- **Research Paper**: `.artifacts/research/paper/` (submission-ready)

---

**Maintained by**: Controllers module team
**Last Review**: December 19, 2025
**Next Review**: March 2026
