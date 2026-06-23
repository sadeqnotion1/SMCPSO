# Configuration API Guide

**Module:** `src.config`
**Purpose:** Configuration loading, validation, and management
**Level:** Intermediate



## Table of Contents

- [Overview](#overview)
- [Loading Configuration](#loading-configuration)
- [Configuration Schema](#configuration-schema)
- [Programmatic Configuration](#programmatic-configuration)
- [Best Practices](#best-practices)
- [Integration Patterns](#integration-patterns)
- [Troubleshooting](#troubleshooting)



## Overview

The Configuration API provides type-safe, validated configuration management for the DIP SMC PSO framework.

**Key Features:**
- ✅ **YAML-Based:** Human-readable configuration files
- ✅ **Pydantic Validation:** Automatic type checking and validation
- ✅ **Nested Structure:** Organized by domain (physics, controllers, simulation, PSO)
- ✅ **Default Values:** Sensible defaults for all parameters
- ✅ **Environment Variables:** Support for environment-based configuration

**Related Documentation:**
- [User Guide: Configuration Management](../user-guide.md#configuration-management)
- [How-To: Running Simulations](../how-to/running-simulations.md)
- [Technical Reference](../../reference/config/__init__.md)



## Loading Configuration

### Basic Usage

```python
from src.config import load_config

# Load from default config.yaml
config = load_config('config.yaml')

# Access configuration sections
physics = config.dip_params
controllers = config.controllers
simulation = config.simulation
pso = config.pso
```

## Configuration Validation

**Automatic validation on load:**
```python
try:
    config = load_config('config.yaml')
    print("Configuration valid!")
except ValueError as e:
    print(f"Configuration error: {e}")
```

**Strict mode (reject unknown fields):**
```python
# Reject any extra fields not in schema
config = load_config('config.yaml', allow_unknown=False)
```

## Multiple Configuration Files

```python
# Load different configs for different scenarios
config_baseline = load_config('config.yaml')
config_challenging = load_config('config_challenging.yaml')
config_hil = load_config('config_hil.yaml')

# Use appropriate config for each scenario
if scenario == 'baseline':
    runner = SimulationRunner(config_baseline)
elif scenario == 'challenging':
    runner = SimulationRunner(config_challenging)
```

## Partial Configuration Loading

```python
import yaml
from src.config.schemas import DIPParams, SimulationConfig

# Load only specific sections
with open('config.yaml', 'r') as f:
    config_dict = yaml.safe_load(f)

# Create partial config objects
physics = DIPParams(**config_dict['dip_params'])
sim_settings = SimulationConfig(**config_dict['simulation'])
```



## Configuration Schema

### Complete Structure

```yaml
# config.yaml - Complete configuration structure

# ==================== Physics Parameters ====================
dip_params:
  # Masses (kg)
  m0: 1.5      # Cart mass
  m1: 0.5      # First pendulum mass
  m2: 0.75     # Second pendulum mass

  # Lengths (m)
  l1: 0.5      # First pendulum length
  l2: 0.75     # Second pendulum length

  # Inertias (kg⋅m²) - auto-calculated if not specified
  I1: 0.0417   # First pendulum inertia
  I2: 0.0938   # Second pendulum inertia

  # Friction coefficients
  b0: 0.1      # Cart friction
  b1: 0.01     # First pendulum friction
  b2: 0.01     # Second pendulum friction

  # Gravity
  g: 9.81      # Gravitational acceleration (m/s²)

# ==================== Controller Settings ====================
controllers:
  # Classical Sliding Mode Controller
  classical_smc:
    gains: [10.0, 8.0, 15.0, 12.0, 50.0, 5.0]  # [k1, k2, λ1, λ2, K, ε]
    max_force: 100.0           # Control saturation (N)
    boundary_layer: 0.01       # Chattering reduction

  # Super-Twisting Sliding Mode Controller
  sta_smc:
    gains: [25.0, 10.0, 15.0, 12.0, 20.0, 15.0]  # [k1, k2, λ1, λ2, α, β]
    max_force: 100.0
    dt: 0.01                   # Required for STA integration

  # Adaptive Sliding Mode Controller
  adaptive_smc:
    gains: [10.0, 8.0, 15.0, 12.0, 0.5]  # [k1, k2, λ1, λ2, γ]
    max_force: 100.0
    adaptation_rate: 0.5       # Online gain adaptation rate
    leak_rate: 0.1             # Prevent unbounded growth
    rate_limit: 10.0           # Maximum adaptation speed

  # Hybrid Adaptive STA-SMC
  hybrid_adaptive_sta_smc:
    gains: [15.0, 12.0, 18.0, 15.0]  # [k1, k2, λ1, λ2]
    max_force: 100.0
    dt: 0.01
    enable_adaptation: true
    adaptation_rate: 0.3

# ==================== Simulation Settings ====================
simulation:
  duration: 5.0              # Simulation time (seconds)
  dt: 0.01                   # Timestep (seconds)
  use_full_dynamics: false   # false=simplified, true=full nonlinear

# ==================== Initial Conditions ====================
initial_conditions:
  x0: 0.0                    # Cart position (m)
  x0_dot: 0.0                # Cart velocity (m/s)
  theta1_0: 0.1              # First pendulum angle (rad)
  theta1_0_dot: 0.0          # First pendulum angular velocity (rad/s)
  theta2_0: 0.15             # Second pendulum angle (rad)
  theta2_0_dot: 0.0          # Second pendulum angular velocity (rad/s)

# ==================== PSO Optimization ====================
pso:
  n_particles: 30            # Swarm size
  iters: 100                 # Number of iterations
  w: 0.7298                  # Inertia weight
  c1: 1.49618                # Cognitive coefficient
  c2: 1.49618                # Social coefficient

  # Gain bounds for each controller type
  bounds:
    classical_smc:
      - [0.1, 50.0]          # k1
      - [0.1, 50.0]          # k2
      - [0.1, 50.0]          # λ1
      - [0.1, 50.0]          # λ2
      - [1.0, 200.0]         # K
      - [0.0, 50.0]          # ε

    adaptive_smc:
      - [0.1, 50.0]          # k1
      - [0.1, 50.0]          # k2
      - [0.1, 50.0]          # λ1
      - [0.1, 50.0]          # λ2
      - [0.01, 10.0]         # γ

# ==================== Hardware-in-the-Loop ====================
hil:
  enabled: false
  host: "localhost"
  port: 5555
  plant_dt: 0.001            # Plant simulation timestep
  communication_latency: 0.005  # Network delay (seconds)
  sensor_noise_std: 0.01     # Sensor noise standard deviation
```

## Configuration Domains

**1. Physics Parameters (dip_params)**
```python
# example-metadata:
# runnable: false

@dataclass
class DIPParams:
    """Double-inverted pendulum physics parameters."""
    m0: float = 1.5      # Cart mass (kg)
    m1: float = 0.5      # First pendulum mass (kg)
    m2: float = 0.75     # Second pendulum mass (kg)
    l1: float = 0.5      # First pendulum length (m)
    l2: float = 0.75     # Second pendulum length (m)
    I1: Optional[float] = None  # Auto-calculate if None
    I2: Optional[float] = None
    b0: float = 0.1      # Cart friction
    b1: float = 0.01     # Pendulum 1 friction
    b2: float = 0.01     # Pendulum 2 friction
    g: float = 9.81      # Gravity (m/s²)

    def __post_init__(self):
        """Auto-calculate inertias if not provided."""
        if self.I1 is None:
            self.I1 = (1/3) * self.m1 * self.l1**2
        if self.I2 is None:
            self.I2 = (1/3) * self.m2 * self.l2**2
```

**2. Controller Configuration**
```python
# example-metadata:
# runnable: false

@dataclass
class ClassicalSMCConfig:
    """Classical SMC configuration."""
    gains: List[float] = Field(..., min_items=6, max_items=6)
    max_force: float = Field(..., gt=0)
    boundary_layer: float = Field(default=0.01, gt=0)

@dataclass
class AdaptiveSMCConfig:
    """Adaptive SMC configuration."""
    gains: List[float] = Field(..., min_items=5, max_items=5)
    max_force: float = Field(..., gt=0)
    adaptation_rate: float = Field(..., gt=0)
    leak_rate: float = Field(default=0.1, ge=0)
    rate_limit: float = Field(default=10.0, gt=0)
```

**3. Simulation Settings**
```python
# example-metadata:
# runnable: false

@dataclass
class SimulationConfig:
    """Simulation parameters."""
    duration: float = Field(..., gt=0)
    dt: float = Field(..., gt=0, le=0.1)
    use_full_dynamics: bool = False
```



## Programmatic Configuration

### Creating Config Objects in Code

```python
from src.config.schemas import (
    DIPParams, ClassicalSMCConfig, SimulationConfig, Config
)

# Create physics parameters
physics = DIPParams(
    m0=1.5, m1=0.5, m2=0.75,
    l1=0.5, l2=0.75,
    b0=0.1, b1=0.01, b2=0.01,
    g=9.81
)

# Create controller config
controller_cfg = ClassicalSMCConfig(
    gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0],
    max_force=100.0,
    boundary_layer=0.01
)

# Create simulation config
sim_cfg = SimulationConfig(
    duration=5.0,
    dt=0.01,
    use_full_dynamics=False
)

# Assemble complete config
full_config = Config(
    dip_params=physics,
    controllers={'classical_smc': controller_cfg},
    simulation=sim_cfg
)
```

## Overriding Parameters

```python
# Load base config
base_config = load_config('config.yaml')

# Override specific parameters
base_config.simulation.duration = 10.0  # Run for 10 seconds
base_config.simulation.use_full_dynamics = True  # Use full dynamics
base_config.dip_params.m1 = 0.75  # Increase first pendulum mass

# Use modified config
runner = SimulationRunner(base_config)
```

## Configuration Merging

```python
def merge_configs(base_config, override_config):
    """Merge two configurations, with override taking precedence."""
    import copy
    merged = copy.deepcopy(base_config)

    # Override physics params if specified
    if override_config.dip_params is not None:
        merged.dip_params = override_config.dip_params

    # Override simulation settings
    if override_config.simulation is not None:
        merged.simulation = override_config.simulation

    # Merge controller configs
    for ctrl_name, ctrl_config in override_config.controllers.items():
        merged.controllers[ctrl_name] = ctrl_config

    return merged

# Usage
base = load_config('config.yaml')
override = load_config('config_override.yaml')
final_config = merge_configs(base, override)
```

## Environment-Based Configuration

```python
import os
from src.config import load_config

# Use environment variable for config selection
config_file = os.getenv('DIP_CONFIG', 'config.yaml')
config = load_config(config_file)

# Override parameters from environment
if os.getenv('DIP_FULL_DYNAMICS'):
    config.simulation.use_full_dynamics = True

if os.getenv('DIP_DURATION'):
    config.simulation.duration = float(os.getenv('DIP_DURATION'))
```



## Best Practices

### 1. Configuration Versioning

**Track config versions with git:**
```yaml
# config.yaml
metadata:
  version: "1.0.0"
  description: "Baseline configuration for classical SMC"
  last_modified: "2025-10-01"
  author: "Research Team"

# Include metadata in config schema
@dataclass
class ConfigMetadata:
    version: str
    description: str
    last_modified: str
    author: str
```

## 2. Default Values

**Provide sensible defaults:**
```python
# example-metadata:
# runnable: false

@dataclass
class PSOConfig:
    """PSO configuration with sensible defaults."""
    n_particles: int = 30
    iters: int = 100
    w: float = 0.7298        # Canonical PSO inertia
    c1: float = 1.49618      # Cognitive coefficient
    c2: float = 1.49618      # Social coefficient

    def __post_init__(self):
        """Validate PSO parameters."""
        if self.n_particles < 10:
            raise ValueError("Swarm too small (min 10 particles)")
        if self.iters < 20:
            raise ValueError("Too few iterations (min 20)")
```

## 3. Parameter Bounds Validation

```python
# example-metadata:
# runnable: false

def validate_physics_params(params: DIPParams):
    """Validate physical constraints."""
    # Positive masses
    if params.m0 <= 0 or params.m1 <= 0 or params.m2 <= 0:
        raise ValueError("Masses must be positive")

    # Positive lengths
    if params.l1 <= 0 or params.l2 <= 0:
        raise ValueError("Lengths must be positive")

    # Reasonable gravity
    if not (9.0 <= params.g <= 10.0):
        raise ValueError("Gravity should be ~9.81 m/s²")

    # Friction coefficients non-negative
    if params.b0 < 0 or params.b1 < 0 or params.b2 < 0:
        raise ValueError("Friction coefficients must be non-negative")

    return True
```

### 4. Documentation in Config Files

```yaml
# config.yaml with inline documentation

# Physics Parameters
# ------------------
# These define the mechanical properties of the double-inverted pendulum.
# Adjust these to simulate different physical systems.
dip_params:
  m0: 1.5      # Cart mass (kg) - baseline: 1.5
  m1: 0.5      # First pendulum mass (kg) - baseline: 0.5
  m2: 0.75     # Second pendulum mass (kg) - baseline: 0.75

  l1: 0.5      # First pendulum length (m) - affects dynamics coupling
  l2: 0.75     # Second pendulum length (m) - affects stability region

  # Friction coefficients - increase for more realistic behavior
  b0: 0.1      # Cart friction (N⋅s/m)
  b1: 0.01     # First pendulum friction (N⋅m⋅s/rad)
  b2: 0.01     # Second pendulum friction (N⋅m⋅s/rad)
```



## Integration Patterns

### Pattern 1: Development vs Production Configs

```python
# example-metadata:
# runnable: false

# development.yaml
simulation:
  duration: 2.0              # Shorter for faster iteration
  dt: 0.01
  use_full_dynamics: false   # Simplified for speed

pso:
  n_particles: 20            # Smaller swarm for speed
  iters: 50

# production.yaml
simulation:
  duration: 10.0             # Full simulation
  dt: 0.001                  # Fine timestep for accuracy
  use_full_dynamics: true    # Full nonlinear dynamics

pso:
  n_particles: 50            # Larger swarm for better results
  iters: 200
```

**Load appropriate config:**
```python
import os

env = os.getenv('ENVIRONMENT', 'development')
config_file = f'config_{env}.yaml'
config = load_config(config_file)
```

## Pattern 2: Scenario-Based Configuration

```python
# example-metadata:
# runnable: false

# scenarios/baseline.yaml
initial_conditions:
  theta1_0: 0.1    # 5.7 degrees
  theta2_0: 0.15   # 8.6 degrees

# scenarios/challenging.yaml
initial_conditions:
  theta1_0: 0.3    # 17 degrees
  theta2_0: 0.4    # 23 degrees

# scenarios/extreme.yaml
initial_conditions:
  theta1_0: 0.5    # 28 degrees
  theta2_0: 0.6    # 34 degrees
```

**Run all scenarios:**
```python
scenarios = ['baseline', 'challenging', 'extreme']
results = {}

for scenario in scenarios:
    config = load_config(f'scenarios/{scenario}.yaml')
    runner = SimulationRunner(config)
    results[scenario] = runner.run(controller)
```



## Troubleshooting

### Problem: "ValidationError: Invalid configuration"

**Cause:** Configuration doesn't meet schema requirements

**Solution:**
```python
try:
    config = load_config('config.yaml')
except ValueError as e:
    print(f"Validation error: {e}")
    # Check specific fields
    # Fix config.yaml
    # Reload
```

### Problem: Gains validation fails

**Cause:** Wrong number of gains for controller type

**Solution:**
```yaml
# Classical SMC requires 6 gains
controllers:
  classical_smc:
    gains: [10, 8, 15, 12, 50, 5]  # ✅ Correct

# Adaptive SMC requires 5 gains
  adaptive_smc:
    gains: [10, 8, 15, 12, 0.5]     # ✅ Correct
```

## Problem: Unknown fields in config

**Cause:** Typo or deprecated field

**Solution:**
```python
# Use strict validation to catch typos
config = load_config('config.yaml', allow_unknown=False)
# Will raise error if unknown fields present
```



## Next Steps

- **Learn configuration usage:** [User Guide: Configuration](../user-guide.md#configuration-management)
- **Set up simulations:** [Simulation API Guide](simulation.md)
- **Configure controllers:** [Controllers API Guide](controllers.md)
- **Technical details:** [Config Technical Reference](../../reference/config/__init__.md)



**Last Updated:** October 2025
