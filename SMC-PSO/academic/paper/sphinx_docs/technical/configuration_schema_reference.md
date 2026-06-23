# Configuration Schema Reference - Factory Integration ## Complete Configuration Schema Documentation for All Controller Types **Document Version:** 2.0

**Last Updated:** November 2024
**Related Issue:** GitHub Issue #6 - Factory Integration Fixes

---

## Table of Contents 1. [Schema Overview](#schema-overview)

2. [Controller Registry Schema](#controller-registry-schema)
3. [Classical SMC Configuration](#classical-smc-configuration)
4. [Super-Twisting SMC Configuration](#super-twisting-smc-configuration)
5. [Adaptive SMC Configuration](#adaptive-smc-configuration)
6. [Hybrid SMC Configuration](#hybrid-smc-configuration)
7. [Global Configuration Integration](#global-configuration-integration)
8. [Validation Rules and Constraints](#validation-rules-and-constraints)
9. [Configuration Examples](#configuration-examples)

---

## Schema Overview The enhanced factory system provides type-safe configuration schemas for all controller types, with validation based on sliding mode control theory. Each controller type has its own dedicated configuration class with mathematical validation rules. ### Key Features - **Type Safety**: All parameters validated at creation time

- **Mathematical Validation**: Constraints based on SMC stability theory
- **Error Messages**: Detailed feedback for invalid configurations
- **Backwards Compatibility**: Supports legacy configuration formats
- **Auto-Completion**: IDE support through type hints and dataclasses ### Configuration Hierarchy ```
Controller Configuration
├── Common Parameters (all controllers)
│ ├── gains: List[float]
│ ├── max_force: float
│ └── dt: float
├── Classical SMC Specific
│ ├── boundary_layer: float
│ ├── switch_method: Literal
│ └── regularization: float
├── STA SMC Specific
│ ├── power_exponent: float
│ ├── damping_gain: float
│ └── boundary_layer: float
├── Adaptive SMC Specific
│ ├── leak_rate: float
│ ├── dead_zone: float
│ ├── adapt_rate_limit: float
│ └── adaptation bounds
└── Hybrid SMC Specific ├── hybrid_mode: HybridMode ├── classical_config: ClassicalSMCConfig └── adaptive_config: AdaptiveSMCConfig
```

---

## Controller Registry Schema ### Registry Structure The controller registry (`CONTROLLER_REGISTRY`) provides metadata for all available controllers: ```python
# example-metadata:
# runnable: false CONTROLLER_REGISTRY = { 'classical_smc': { 'class': ModularClassicalSMC, 'config_class': ClassicalSMCConfig, 'default_gains': [8.0, 6.0, 4.0, 3.0, 15.0, 2.0], 'gain_count': 6, 'description': 'Classical sliding mode controller with boundary layer', 'supports_dynamics': True, 'required_params': ['gains', 'max_force', 'boundary_layer'] }, # ... other controllers
}
``` ### Registry Fields | Field | Type | Description |

|-------|------|-------------|
| `class` | Type | Controller implementation class |
| `config_class` | Type | Configuration dataclass |
| `default_gains` | List[float] | Tested stable gain values |
| `gain_count` | int | Expected number of gains |
| `description` | str | Human-readable description |
| `supports_dynamics` | bool | Whether controller accepts dynamics model |
| `required_params` | List[str] | Mandatory configuration parameters |

---

## Classical SMC Configuration ### Schema Definition ```python

# example-metadata:

# runnable: false @dataclass(frozen=True)

class ClassicalSMCConfig: """Type-safe configuration for Classical SMC controller.""" # Required Parameters gains: List[float] # [k1, k2, λ1, λ2, K, kd] max_force: float # Control saturation limit [N] boundary_layer: float # Chattering reduction thickness # Optional Parameters with Defaults dt: float = 0.01 # Control timestep [s] boundary_layer_slope: float = 0.0 # Adaptive boundary layer slope switch_method: Literal["tanh", "linear", "sign"] = "tanh" regularization: float = 1e-10 # Matrix regularization controllability_threshold: Optional[float] = None dynamics_model: Optional[object] = None
``` ### Parameter Specifications #### Required Parameters **`gains: List[float]`** - Control gains vector `[k1, k2, λ1, λ2, K, kd]`
- **Length**: Exactly 6 elements
- **Mathematical meaning**: - `k1, k2`: Position gains for joints 1 and 2 - `λ1, λ2`: Sliding surface coefficients for joints 1 and 2 - `K`: Switching gain for reaching condition - `kd`: Derivative gain for damping
- **Constraints**: - All surface gains `[k1, k2, λ1, λ2]` must be positive (Hurwitz stability) - Switching gain `K` must be positive (reaching condition) - Derivative gain `kd` must be non-negative - Range: `1e-12 < gain < 1e5` (numerical stability) **`max_force: float`** - Control saturation limit
- **Unit**: Newtons [N]
- **Constraint**: Must be positive
- **Typical range**: 50.0 - 200.0 N
- **Purpose**: Hardware actuator limits **`boundary_layer: float`** - Chattering reduction thickness
- **Unit**: Dimensionless
- **Constraint**: Must be positive, `> 1e-12`
- **Typical range**: 0.01 - 0.1
- **Purpose**: Smooth approximation of discontinuous switching #### Optional Parameters **`dt: float`** - Control timestep
- **Default**: 0.01 s
- **Constraint**: Must be positive, `> 1e-6`
- **Purpose**: Discrete-time implementation **`boundary_layer_slope: float`** - Adaptive boundary layer slope
- **Default**: 0.0 (non-adaptive)
- **Constraint**: Must be non-negative
- **Purpose**: Time-varying boundary layer adaptation **`switch_method: Literal["tanh", "linear", "sign"]`** - Switching function type
- **Default**: "tanh"
- **Options**: - `"tanh"`: Hyperbolic tangent (smooth) - `"linear"`: Linear saturation - `"sign"`: Discontinuous switching (chattering) **`regularization: float`** - Matrix regularization
- **Default**: 1e-10
- **Constraint**: Must be positive
- **Purpose**: Numerical stability in matrix operations ### Validation Rules The configuration automatically validates parameters based on SMC theory: ```python
# example-metadata:
# runnable: false def _validate_gains(self) -> None: """Validate gain vector according to SMC theory.""" # Check gain count if len(self.gains) != 6: raise ValueError("Classical SMC requires exactly 6 gains") k1, k2, lam1, lam2, K, kd = self.gains # Surface gains must be positive for Hurwitz stability if any(g <= 0 for g in [k1, k2, lam1, lam2]): raise ValueError("Surface gains [k1, k2, λ1, λ2] must be positive for stability") # Switching gain must be positive for reaching condition if K <= 0: raise ValueError("Switching gain K must be positive") # Derivative gain must be non-negative if kd < 0: raise ValueError("Derivative gain kd must be non-negative")
``` ### Configuration Examples #### Stability-Focused Configuration

```python
stability_config = ClassicalSMCConfig( gains=[5.0, 5.0, 3.0, 3.0, 10.0, 1.0], # Conservative gains max_force=100.0, boundary_layer=0.05, # Wide boundary layer for robustness dt=0.01, switch_method="tanh"
)
``` #### Performance-Focused Configuration

```python
performance_config = ClassicalSMCConfig( gains=[15.0, 12.0, 8.0, 6.0, 25.0, 4.0], # Aggressive gains max_force=150.0, boundary_layer=0.01, # Narrow boundary layer for precision dt=0.001, # High frequency control switch_method="linear"
)
```

---

## Super-Twisting SMC Configuration ### Schema Definition ```python

# example-metadata:

# runnable: false @dataclass(frozen=True)

class SuperTwistingSMCConfig: """Configuration for Super-Twisting (STA) SMC controller.""" # Required Parameters gains: List[float] # [K1, K2, k1, k2, λ1, λ2] max_force: float # Control saturation limit [N] dt: float # Integration timestep [s] # Optional STA Algorithm Parameters power_exponent: float = 0.5 # STA convergence exponent α ∈ (0,1) regularization: float = 1e-6 # Numerical stability boundary_layer: float = 0.01 # Chattering reduction switch_method: str = "tanh" # Switching function type damping_gain: float = 0.0 # Additional damping # Optional dynamics model dynamics_model: Optional[object] = None
``` ### Parameter Specifications #### STA Algorithm Theory The Super-Twisting algorithm implements finite-time convergent sliding mode control: ```
u₁ = -K₁|s|^α sign(s) + u₂
u̇₂ = -K₂ sign(s)
``` Where:

- `K₁, K₂` are the STA gains satisfying stability conditions
- `α ∈ (0,1)` is the convergence exponent (typically 0.5)
- The algorithm provides **finite-time convergence** with **continuous control** #### Required Parameters **`gains: List[float]`** - STA control gains vector `[K1, K2, k1, k2, λ1, λ2]`
- **Length**: Exactly 6 elements
- **Mathematical meaning**: - `K1, K2`: Super-twisting algorithm gains - `k1, k2`: Surface gains for joints 1 and 2 - `λ1, λ2`: Sliding surface coefficients (optimized for Issue #2)
- **Constraints**: - All gains must be positive - STA stability condition: `K₂ > (L_f)/(2√(K₁))` where `L_f` is Lipschitz constant **`max_force: float`** - Control saturation limit
- **Unit**: Newtons [N]
- **Constraint**: Must be positive
- **Purpose**: Hardware actuator limits **`dt: float`** - Integration timestep
- **Unit**: Seconds [s]
- **Constraint**: Must be positive
- **Purpose**: Discrete integration of STA algorithm #### Optional Parameters **`power_exponent: float`** - STA convergence exponent
- **Default**: 0.5
- **Constraint**: Must be in range (0, 1)
- **Purpose**: Controls convergence rate (higher = faster convergence) **`boundary_layer: float`** - Chattering reduction
- **Default**: 0.01
- **Purpose**: Smooth approximation near sliding surface ### Issue #2 Optimized Configuration The following configuration resolves the overshoot issues identified in GitHub Issue #2: ```python
# Reduced overshoot configuration (Issue #2 resolution)

optimized_sta_config = SuperTwistingSMCConfig( gains=[8.0, 4.0, 12.0, 6.0, 4.85, 3.43], # Optimized λ₁, λ₂ coefficients max_force=150.0, dt=0.001, power_exponent=0.5, boundary_layer=0.01, switch_method="tanh"
)
``` **Key optimizations**:
- `λ₁ = 4.85`: Reduced from 20.0 for target damping ratio ζ=0.7
- `λ₂ = 3.43`: Optimized for reduced overshoot (<5%)
- `K₂ = 4.0`: Reduced from 8.0 for improved damping

---

## Adaptive SMC Configuration ### Schema Definition ```python
# example-metadata:
# runnable: false @dataclass(frozen=True)
class AdaptiveSMCConfig: """Configuration for Adaptive SMC with parameter estimation.""" # Required Parameters gains: List[float] # [k1, k2, λ1, λ2, γ] max_force: float # Control saturation limit [N] dt: float # Integration timestep [s] # Adaptation Parameters leak_rate: float = 0.01 # Parameter drift prevention σ dead_zone: float = 0.05 # Adaptation dead zone width adapt_rate_limit: float = 10.0 # Maximum adaptation rate K_min: float = 0.1 # Minimum adaptive gain K_max: float = 100.0 # Maximum adaptive gain K_init: float = 10.0 # Initial adaptive gain alpha: float = 0.5 # Adaptation smoothing factor # Control Parameters boundary_layer: float = 0.01 # Smooth switching layer smooth_switch: bool = True # smooth switching # Optional dynamics model dynamics_model: Optional[object] = None
``` ### Parameter Specifications #### Adaptive Control Theory The adaptive SMC automatically adjusts control gains based on system uncertainty: ```

K̇ = γ|s| - σK (outside dead zone)
K̇ = -σK (inside dead zone)
u = -K(t) sign(s)
``` Where:
- `γ > 0` is the adaptation rate (gains[4])
- `σ > 0` is the leakage term preventing parameter drift
- Dead zone prevents adaptation during small tracking errors #### Required Parameters **`gains: List[float]`** - Adaptive control gains `[k1, k2, λ1, λ2, γ]`
- **Length**: Exactly 5 elements
- **Mathematical meaning**: - `k1, k2`: Surface gains for joints 1 and 2 - `λ1, λ2`: Sliding surface coefficients - `γ`: Adaptation rate
- **Constraints**: All gains must be positive #### Adaptation Parameters **`leak_rate: float`** - Parameter drift prevention
- **Default**: 0.01
- **Symbol**: σ in adaptation law
- **Purpose**: Prevents unbounded parameter growth **`dead_zone: float`** - Adaptation dead zone width
- **Default**: 0.05
- **Purpose**: Prevents adaptation during measurement noise **`adapt_rate_limit: float`** - Maximum adaptation rate
- **Default**: 10.0 [1/s]
- **Purpose**: Prevents excessive adaptation transients **`K_min, K_max: float`** - Adaptive gain bounds
- **Defaults**: 0.1, 100.0
- **Purpose**: Bounded adaptation for stability ### Configuration Examples #### Robust Adaptation Configuration
```python
# example-metadata:

# runnable: false robust_adaptive_config = AdaptiveSMCConfig( gains=[15.0, 12.0, 8.0, 6.0, 2.0], # Conservative adaptation rate max_force=150.0, dt=0.001, leak_rate=0.05, # Higher leakage for robustness dead_zone=0.1, # Wider dead zone adapt_rate_limit=5.0, # Conservative adaptation K_min=1.0, K_max=50.0, boundary_layer=0.05

)
``` #### Fast Adaptation Configuration
```python
# example-metadata:

# runnable: false fast_adaptive_config = AdaptiveSMCConfig( gains=[20.0, 15.0, 10.0, 8.0, 5.0], # Aggressive adaptation rate max_force=150.0, dt=0.001, leak_rate=0.001, # Minimal leakage dead_zone=0.02, # Narrow dead zone adapt_rate_limit=20.0, # Fast adaptation K_min=0.1, K_max=200.0, boundary_layer=0.01

)
```

---

## Hybrid SMC Configuration ### Schema Definition ```python
# example-metadata:
# runnable: false @dataclass(frozen=True)
class HybridSMCConfig: """Configuration for Hybrid Adaptive STA-SMC controller.""" # Required Parameters hybrid_mode: HybridMode # Control mode selection dt: float # Integration timestep [s] max_force: float # Control saturation limit [N] # Sub-Controller Configurations classical_config: ClassicalSMCConfig # Classical SMC settings adaptive_config: AdaptiveSMCConfig # Adaptive SMC settings # Hybrid-Specific Parameters k1_init: float = 4.0 # Initial proportional gain k2_init: float = 0.4 # Initial integral gain gamma1: float = 2.0 # k1 adaptation rate gamma2: float = 0.5 # k2 adaptation rate dead_zone: float = 0.05 # Adaptation dead zone # Advanced Options enable_equivalent: bool = False # Model-based equivalent control damping_gain: float = 3.0 # Additional damping adapt_rate_limit: float = 5.0 # Rate limiting sat_soft_width: float = 0.05 # Soft saturation width
``` ### Hybrid Mode Selection ```python

class HybridMode(Enum): """Hybrid controller operational modes.""" CLASSICAL_ADAPTIVE = "classical_adaptive" # Classical + Adaptive switching STA_ADAPTIVE = "sta_adaptive" # STA + Adaptive switching FULL_HYBRID = "full_hybrid" # All algorithms available
``` ### Parameter Specifications #### Sub-Controller Integration The hybrid controller combines multiple SMC algorithms with intelligent switching:

- **Classical SMC**: Provides baseline robust control
- **Adaptive SMC**: Handles parametric uncertainties
- **Super-Twisting**: Finite-time convergence and chattering reduction #### Switching Logic The hybrid controller implements mode-dependent switching: ```
Classical Mode: u = u_classical + u_adaptive (parameter estimation)
STA Mode: u = u_sta + u_adaptive (enhanced robustness)
Full Hybrid: u = f(tracking_error, system_state) selecting optimal algorithm
``` ### Configuration Examples #### Research Configuration

```python
from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig
from src.controllers.smc.algorithms.adaptive.config import AdaptiveSMCConfig
from src.controllers.smc.algorithms.hybrid.config import HybridSMCConfig, HybridMode # Create sub-configurations
classical_sub = ClassicalSMCConfig( gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0], max_force=150.0, boundary_layer=0.02, dt=0.001
) adaptive_sub = AdaptiveSMCConfig( gains=[12.0, 10.0, 6.0, 5.0, 2.5], max_force=150.0, leak_rate=0.01, dead_zone=0.05, dt=0.001
) # Create hybrid configuration
research_hybrid_config = HybridSMCConfig( hybrid_mode=HybridMode.FULL_HYBRID, dt=0.001, max_force=150.0, classical_config=classical_sub, adaptive_config=adaptive_sub, k1_init=4.0, k2_init=0.4, gamma1=2.0, gamma2=0.5, dead_zone=0.05, enable_equivalent=True, # model-based control damping_gain=3.0, adapt_rate_limit=5.0
)
```

---

## Global Configuration Integration ### YAML Configuration Structure The factory integrates with the global `config.yaml` file structure: ```yaml

# Controller default gains

controller_defaults: classical_smc: gains: [8.0, 6.0, 4.0, 3.0, 15.0, 2.0] sta_smc: gains: [8.0, 4.0, 12.0, 6.0, 4.85, 3.43] # Issue #2 optimized adaptive_smc: gains: [12.0, 10.0, 6.0, 5.0, 2.5] hybrid_adaptive_sta_smc: gains: [8.0, 6.0, 4.0, 3.0] # Controller-specific parameters
controllers: classical_smc: max_force: 150.0 boundary_layer: 0.02 dt: 0.001 switch_method: "tanh" sta_smc: max_force: 150.0 dt: 0.001 power_exponent: 0.5 boundary_layer: 0.01 damping_gain: 0.0 adaptive_smc: max_force: 150.0 dt: 0.001 leak_rate: 0.01 dead_zone: 0.05 adapt_rate_limit: 10.0 K_min: 0.1 K_max: 100.0 boundary_layer: 0.01
``` ### Configuration Loading ```python
from src.config import load_config
from src.controllers.factory import create_controller # Load global configuration
config = load_config("config.yaml") # Factory automatically extracts parameters from config structure
controller = create_controller( controller_type='classical_smc', config=config # Gains and parameters automatically loaded from config
)
```

---

## Validation Rules and Constraints ### Mathematical Validation All configuration classes implement validation based on control theory: #### Stability Requirements 1. **Hurwitz Stability**: Surface gains must be positive

2. **Reaching Condition**: Switching gains must be positive
3. **Lyapunov Stability**: Parameter bounds must be satisfied #### Numerical Stability 1. **Finite Values**: All parameters must be finite (no NaN/Inf)
2. **Range Limits**: Parameters within reasonable numerical ranges
3. **Regularization**: Matrix operations protected against singularities ### Validation Error Messages The system provides detailed, actionable error messages: ```python
# Example validation errors

ValueError("Surface gains [k1, k2, λ1, λ2] must be positive for stability")
ValueError("boundary_layer is too small (minimum: 1e-12) which may cause division by zero")
ValueError("Classical SMC requires exactly 6 gains: [k1, k2, lam1, lam2, K, kd]")
``` ### Common Validation Issues | Issue | Cause | Solution |
|-------|-------|----------|
| "Surface gains must be positive" | Negative or zero gain values | Use positive gains > 1e-12 |
| "Requires exactly N gains" | Wrong number of gains | Check controller gain count requirements |
| "boundary_layer too small" | Boundary layer < 1e-12 | Use reasonable boundary layer (0.01-0.1) |
| "max_force must be positive" | Invalid actuator limit | Set realistic force limit (50-200 N) |

---

## Configuration Examples ### Complete Configuration Set ```python
from src.controllers.factory import create_controller
from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig
from src.controllers.smc.algorithms.super_twisting.config import SuperTwistingSMCConfig
from src.controllers.smc.algorithms.adaptive.config import AdaptiveSMCConfig # Classical SMC - Production configuration
classical_config = ClassicalSMCConfig( gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0], max_force=150.0, boundary_layer=0.02, dt=0.001, switch_method="tanh", regularization=1e-8
) # STA SMC - Issue #2 optimized configuration
sta_config = SuperTwistingSMCConfig( gains=[8.0, 4.0, 12.0, 6.0, 4.85, 3.43], max_force=150.0, dt=0.001, power_exponent=0.5, boundary_layer=0.01, damping_gain=0.0
) # Adaptive SMC - Robust configuration
adaptive_config = AdaptiveSMCConfig( gains=[12.0, 10.0, 6.0, 5.0, 2.5], max_force=150.0, dt=0.001, leak_rate=0.01, dead_zone=0.05, adapt_rate_limit=10.0, K_min=0.1, K_max=100.0, boundary_layer=0.01
) # Create controllers with validated configurations
classical_controller = create_controller('classical_smc', config=classical_config)
sta_controller = create_controller('sta_smc', config=sta_config)
adaptive_controller = create_controller('adaptive_smc', config=adaptive_config)
``` ### Configuration Validation Test ```python
# example-metadata:

# runnable: false def validate_all_configurations(): """Test configuration validation for all controller types.""" try: # Test valid configurations configs = { 'classical': ClassicalSMCConfig( gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0], max_force=150.0, boundary_layer=0.02 ), 'sta': SuperTwistingSMCConfig( gains=[8.0, 4.0, 12.0, 6.0, 4.85, 3.43], max_force=150.0, dt=0.001 ), 'adaptive': AdaptiveSMCConfig( gains=[12.0, 10.0, 6.0, 5.0, 2.5], max_force=150.0, dt=0.001 ) } for name, config in configs.items(): controller = create_controller(name + '_smc', config=config) print(f"✅ {name.capitalize()} SMC configuration valid") except Exception as e: print(f"❌ Configuration validation failed: {e}") validate_all_configurations()

``` This configuration schema reference provides complete documentation for all controller types, their parameters, validation rules, and usage examples. The schemas ensure type safety, mathematical correctness, and production reliability for the enhanced factory system.