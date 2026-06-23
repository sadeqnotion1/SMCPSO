# SMC Controller Factory System Guide **Double-Inverted Pendulum Sliding Mode Control**

**Advanced Factory Pattern Documentation**

---

## Table of Contents 1. [Overview](#overview)

2. [Architecture](#architecture)
3. [Enterprise Factory System](#enterprise-factory-system)
4. [Clean SMC Factory](#clean-smc-factory)
5. [PSO Integration Patterns](#pso-integration-patterns)
6. [Configuration Management](#configuration-management)
7. [Controller Creation Workflows](#controller-creation-workflows)
8. [Advanced Features](#advanced-features)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## 1. Overview ### 1.1 Purpose The Factory System provides a unified, type-safe interface for instantiating SMC controllers with: - **PSO parameter tuning** - Array-based parameter injection

- **Research consistency** - Reproducible controller creation
- **Performance benchmarking** - Standardized interfaces
- **Clean separation of concerns** - Modular design ### 1.2 Two-Tier Factory Architecture ```
Factory System
├── Enterprise Factory (src/controllers/factory.py)
│ ├── Full registry-based system
│ ├── Thread-safe operations
│ ├── Backwards compatibility
│ ├── Configuration validation
│ └── Deprecation handling
│
└── Clean SMC Factory (src/controllers/factory/smc_factory.py) ├── Focused on 4 core SMC controllers ├── PSO-optimized interface ├── Minimal complexity └── Type-safe design
``` ### 1.3 Supported Controllers | Controller Type | Gain Count | Primary Use Case |
|----------------|------------|------------------|
| **Classical SMC** | 6 | Boundary layer control |
| **Adaptive SMC** | 5 | Online parameter adaptation |
| **Super-Twisting SMC** | 6 | Finite-time convergence |
| **Hybrid Adaptive-STA SMC** | 4 | Combined adaptive + STA |

---

## 2. Architecture ### 2.1 Design Principles ```python
# example-metadata:
# runnable: false # Single Responsibility - Each factory focuses on specific concerns
Enterprise Factory: configuration, backwards compatibility
Clean SMC Factory: PSO optimization, research benchmarking # Dependency Injection - Controllers receive dependencies at creation
controller = create_controller( 'classical_smc', config=config, gains=[10, 8, 15, 12, 50, 5]
) # Type Safety - Explicit typing for all interfaces
def create_controller( controller_type: str, config: Optional[Any] = None, gains: Optional[Union[list, np.ndarray]] = None
) -> Any: ...
``` ### 2.2 Registry Pattern The Enterprise Factory uses a **registry pattern** for dynamic controller lookup: ```python
# example-metadata:

# runnable: false CONTROLLER_REGISTRY = { 'classical_smc': { 'class': ClassicalSMC, 'config_class': ClassicalSMCConfig, 'default_gains': [20.0, 15.0, 12.0, 8.0, 35.0, 5.0], 'gain_count': 6, 'description': 'Classical sliding mode controller with boundary layer', 'supports_dynamics': True, 'required_params': ['gains', 'max_force', 'boundary_layer'] }, 'sta_smc': { 'class': SuperTwistingSMC, 'config_class': STASMCConfig, 'default_gains': [25.0, 15.0, 20.0, 12.0, 8.0, 6.0], 'gain_count': 6, # ... }, # ... additional controllers

}
``` **Benefits:**
- Dynamic controller discovery
- Metadata-driven validation
- Extensible without code changes
- Centralized configuration ### 2.3 PSO Wrapper Pattern For PSO optimization, controllers are wrapped with a simplified interface: ```python
# example-metadata:
# runnable: false class PSOControllerWrapper: """PSO-friendly wrapper that simplifies the control interface.""" def __init__(self, controller: SMCProtocol): self.controller = controller self._history = {} self._state_vars = () # Controller-specific state def compute_control(self, state: np.ndarray) -> np.ndarray: """Simplified interface for PSO fitness evaluation.""" # Full interface: compute_control(state, state_vars, history) # PSO interface: compute_control(state) -> np.ndarray result = self.controller.compute_control(state, self._state_vars, self._history) return np.array([self._extract_control_value(result)])
```

---

## 3. Enterprise Factory System ### 3.1 Core Functions ```python

from src.controllers.factory import ( create_controller, # Main factory function list_available_controllers, # Discovery get_default_gains, # Gain specifications SMCType, # Enum for controller types SMCFactory, # Object-oriented interface
)
``` ### 3.2 Basic Usage ```python
# example-metadata:
# runnable: false # Method 1: String-based creation
controller = create_controller( controller_type='classical_smc', config=config, gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0]
) # Method 2: Enum-based creation (type-safe)
controller = SMCFactory.create_controller( smc_type=SMCType.CLASSICAL, config=SMCConfig(gains=[10, 8, 15, 12, 50, 5], max_force=100, dt=0.01)
) # Method 3: Backwards-compatible aliases
controller = create_classical_smc_controller(config, gains=[...])
``` ### 3.3 Controller Type Normalization The factory supports **multiple aliases** for backwards compatibility: ```python
# example-metadata:

# runnable: false CONTROLLER_ALIASES = { 'classic_smc': 'classical_smc', 'smc_classical': 'classical_smc', 'smc_v1': 'classical_smc', 'super_twisting': 'sta_smc', 'sta': 'sta_smc', 'adaptive': 'adaptive_smc', 'hybrid': 'hybrid_adaptive_sta_smc',

} # All these create the same controller:
create_controller('classical_smc', ...)
create_controller('classic_smc', ...)
create_controller('smc_classical', ...)
``` ### 3.4 Thread-Safe Operations ```python
# example-metadata:
# runnable: false # Thread-safe factory operations with timeout protection
_factory_lock = threading.RLock()
_LOCK_TIMEOUT = 10.0 # seconds def create_controller(controller_type: str, ...) -> Any: with _factory_lock: # Thread-safe controller creation controller_info = _get_controller_info(controller_type) # ... validation and instantiation
``` ### 3.5 Configuration Resolution The factory resolves gains from **multiple sources**: ```python
# example-metadata:

# runnable: false # Priority order:

# 1. Explicitly provided gains parameter

if gains is not None: return gains # 2. Config object with controller_defaults
if hasattr(config, 'controller_defaults'): if controller_type in config.controller_defaults: return config.controller_defaults[controller_type].gains # 3. Registry default gains
return controller_info['default_gains']
``` ### 3.6 Validation Pipeline ```python
# example-metadata:
# runnable: false def _validate_controller_gains(gains, controller_info, controller_type): """Validate controller gains with controller-specific rules.""" # 1. Count validation if len(gains) != controller_info['gain_count']: raise ValueError(f"Expected {controller_info['gain_count']} gains, got {len(gains)}") # 2. Finite values if not all(isinstance(g, (int, float)) and np.isfinite(g) for g in gains): raise ValueError("All gains must be finite numbers") # 3. Positivity if any(g <= 0 for g in gains): raise ValueError("All gains must be positive") # 4. Controller-specific constraints if controller_type == 'sta_smc' and len(gains) >= 2: K1, K2 = gains[0], gains[1] if K1 <= K2: raise ValueError("Super-Twisting stability requires K1 > K2 > 0")
```

---

## 4. Clean SMC Factory ### 4.1 Overview The **Clean SMC Factory** (`src/controllers/factory/smc_factory.py`) is a streamlined factory focused on the 4 core SMC controllers, optimized for PSO parameter tuning and research benchmarking. ```python

from src.controllers.factory.smc_factory import ( SMCFactory, # Core factory class SMCType, # Controller type enum SMCConfig, # Configuration dataclass create_smc_for_pso, # PSO-optimized creation get_gain_bounds_for_pso, # PSO bounds validate_smc_gains, # Gain validation
)
``` ### 4.2 Core Features **1. Frozen Configuration (Immutable)** ```python
# example-metadata:
# runnable: false @dataclass(frozen=True)
class SMCConfig: """Clean configuration for all SMC controllers.""" # Core parameters (common to all SMCs) gains: List[float] max_force: float = 100.0 dt: float = 0.01 # Optional dynamics model dynamics_model: Optional[Any] = None # Controller-specific parameters (use defaults if not specified) boundary_layer: float = 0.01 damping_gain: float = 0.0 # Adaptive SMC specific leak_rate: float = 0.1 adapt_rate_limit: float = 100.0 K_min: float = 0.1 K_max: float = 100.0 # ... additional parameters
``` **2. Gain Specifications** ```python
# example-metadata:

# runnable: false @dataclass(frozen=True)

class SMCGainSpec: """Specification of gain requirements for each SMC type.""" controller_type: SMCType n_gains: int gain_names: List[str] description: str @property def gain_bounds(self) -> List[tuple[float, float]]: """Default gain bounds for PSO optimization.""" if self.controller_type == SMCType.CLASSICAL: # [k1, k2, lam1, lam2, K, kd] return [(0.1, 50.0)] * 4 + [(1.0, 200.0)] + [(0.0, 50.0)] # ... controller-specific bounds # Pre-defined specifications
SMC_GAIN_SPECS = { SMCType.CLASSICAL: SMCGainSpec( SMCType.CLASSICAL, 6, ["k1", "k2", "lam1", "lam2", "K", "kd"], "Classical SMC with switching and damping gains" ), # ... additional specifications
}
``` **3. Simplified Creation** ```python
# example-metadata:
# runnable: false # Direct from gains array
controller = SMCFactory.create_from_gains( smc_type=SMCType.CLASSICAL, gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, dt=0.01
) # From full configuration
config = SMCConfig( gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, dt=0.01, boundary_layer=0.02
)
controller = SMCFactory.create_controller(SMCType.CLASSICAL, config)
```

---

## 5. PSO Integration Patterns ### 5.1 PSO-Optimized Controller Creation ```python

from src.controllers.factory import create_smc_for_pso, get_gain_bounds_for_pso # Get PSO bounds for controller type
lower_bounds, upper_bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)
# lower_bounds = [1.0, 1.0, 1.0, 1.0, 5.0, 0.1]

# upper_bounds = [30.0, 30.0, 20.0, 20.0, 50.0, 10.0] # PSO-friendly controller factory

def controller_factory(gains: np.ndarray): return create_smc_for_pso( smc_type=SMCType.CLASSICAL, gains=gains, max_force=100.0, dt=0.01 ) # Use in PSO optimization
from src.optimization.algorithms.pso_optimizer import PSOTuner tuner = PSOTuner( controller_factory=controller_factory, config='config.yaml', seed=42
) best_gains, best_cost = tuner.optimize( lower_bounds=lower_bounds, upper_bounds=upper_bounds, n_particles=30, n_iterations=100
)
``` ### 5.2 Controller Factory Requirements PSO requires factory functions with specific attributes: ```python
# example-metadata:
# runnable: false def create_pso_controller_factory(smc_type: SMCType, **kwargs) -> Callable: """Create a PSO-optimized controller factory function.""" def controller_factory(gains: Union[list, np.ndarray]) -> Any: return create_smc_for_pso(smc_type, gains, **kwargs) # Add PSO-required attributes spec = SMC_GAIN_SPECS[smc_type] controller_factory.n_gains = spec.n_gains controller_factory.controller_type = smc_type.value controller_factory.max_force = kwargs.get('max_force', 150.0) return controller_factory
``` ### 5.3 PSO Wrapper Interface ```python
# example-metadata:

# runnable: false class PSOControllerWrapper: """PSO-friendly wrapper that simplifies the control interface.""" def __init__(self, controller: SMCProtocol): self.controller = controller self._history = {} # Initialize state_vars based on controller type controller_name = type(controller).__name__ if 'SuperTwisting' in controller_name: self._state_vars = (0.0, 0.0) # (z, sigma) elif 'Hybrid' in controller_name: self._state_vars = (k1_init, k2_init, 0.0) else: self._state_vars = () def compute_control(self, state: np.ndarray) -> np.ndarray: """Simplified compute_control for PSO fitness evaluation.""" result = self.controller.compute_control(state, self._state_vars, self._history) # Extract control value and return as numpy array if hasattr(result, 'u'): control_value = result.u elif isinstance(result, dict) and 'u' in result: control_value = result['u'] else: control_value = result return np.array([control_value])

``` ### 5.4 Gain Validation for PSO ```python
# example-metadata:
# runnable: false def validate_smc_gains(smc_type: SMCType, gains: np.ndarray) -> bool: """Validate gains for PSO particle evaluation.""" spec = SMC_GAIN_SPECS[smc_type] # Check length if len(gains) != spec.n_gains: return False # Check positivity for surface gains if any(g <= 0 for g in gains[:4]): return False # Controller-specific constraints if smc_type == SMCType.SUPER_TWISTING: K1, K2 = gains[0], gains[1] if K1 <= K2: # Stability requirement return False return True
```

---

## 6. Configuration Management ### 6.1 Configuration Sources ```python

# 1. Direct parameter passing

controller = create_controller( 'classical_smc', config=None, gains=[10, 8, 15, 12, 50, 5]
) # 2. Configuration object
from src.config import load_config
config = load_config('config.yaml')
controller = create_controller('classical_smc', config=config) # 3. Configuration with gain override
controller = create_controller( 'classical_smc', config=config, gains=[20, 15, 12, 8, 35, 5] # Overrides config
)
``` ### 6.2 Parameter Extraction ```python
# example-metadata:
# runnable: false def _extract_controller_parameters(config, controller_type, controller_info): """Extract controller-specific parameters from configuration.""" if hasattr(config, 'controllers') and controller_type in config.controllers: controller_config = config.controllers[controller_type] # Pydantic model if hasattr(controller_config, 'model_dump'): return controller_config.model_dump() # Dictionary elif isinstance(controller_config, dict): return controller_config.copy() # Object with attributes else: return { attr: getattr(controller_config, attr) for attr in dir(controller_config) if not attr.startswith('_') and not callable(getattr(controller_config, attr)) } return {}
``` ### 6.3 Deprecation Handling ```python

from src.controllers.factory.deprecation import check_deprecated_config # Automatic migration of deprecated parameters
controller_params = check_deprecated_config(controller_type, controller_params) # Example migration:
# Old: {'switching_gain': 50.0}

# New: {'K': 50.0}

```

---

## 7. Controller Creation Workflows ### 7.1 Classical SMC Creation ```python
# example-metadata:
# runnable: false # Enterprise Factory
controller = create_controller( controller_type='classical_smc', config=config, gains=[20.0, 15.0, 12.0, 8.0, 35.0, 5.0] # [k1, k2, λ1, λ2, K, kd]
) # Clean SMC Factory
controller = SMCFactory.create_from_gains( smc_type=SMCType.CLASSICAL, gains=[20.0, 15.0, 12.0, 8.0, 35.0, 5.0], max_force=100.0, dt=0.01, boundary_layer=0.02
) # Internal creation (ClassicalSMC constructor)
controller = ClassicalSMC( gains=[20.0, 15.0, 12.0, 8.0, 35.0, 5.0], max_force=100.0, boundary_layer=0.02, dynamics_model=dynamics_model
)
``` ### 7.2 Adaptive SMC Creation ```python
# example-metadata:

# runnable: false # Clean SMC Factory

controller = SMCFactory.create_from_gains( smc_type=SMCType.ADAPTIVE, gains=[25.0, 18.0, 15.0, 10.0, 4.0], # [k1, k2, λ1, λ2, γ] max_force=100.0, dt=0.01, leak_rate=0.1, adapt_rate_limit=100.0, K_min=0.1, K_max=100.0, K_init=10.0
) # Internal creation (AdaptiveSMC constructor)
controller = AdaptiveSMC( gains=[25.0, 18.0, 15.0, 10.0, 4.0], dt=0.01, max_force=100.0, leak_rate=0.1, adapt_rate_limit=100.0, K_min=0.1, K_max=100.0, smooth_switch=True, boundary_layer=0.01, dead_zone=0.05
)
``` ### 7.3 Super-Twisting SMC Creation ```python
# example-metadata:
# runnable: false # Clean SMC Factory
controller = SMCFactory.create_from_gains( smc_type=SMCType.SUPER_TWISTING, gains=[25.0, 15.0, 20.0, 12.0, 8.0, 6.0], # [K1, K2, k1, k2, λ1, λ2] max_force=100.0, dt=0.01, damping_gain=0.0, boundary_layer=0.01, dynamics_model=dynamics_model
) # Constraint validation (K1 > K2)
K1, K2 = gains[0], gains[1]
if K1 <= K2: raise ValueError("Super-Twisting stability requires K1 > K2 > 0")
``` ### 7.4 Hybrid Adaptive-STA SMC Creation ```python
# Hybrid controller requires special handling - sub-configs

from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig
from src.controllers.smc.algorithms.adaptive.config import AdaptiveSMCConfig
from src.controllers.smc.algorithms.hybrid.config import HybridMode classical_config = ClassicalSMCConfig( gains=[20.0, 15.0, 12.0, 8.0, 35.0, 5.0], max_force=150.0, dt=0.001, boundary_layer=0.02
) adaptive_config = AdaptiveSMCConfig( gains=[25.0, 18.0, 15.0, 10.0, 4.0], max_force=150.0, dt=0.001
) controller = create_controller( controller_type='hybrid_adaptive_sta_smc', config=None, # Not used for hybrid gains=[18.0, 12.0, 10.0, 8.0] # [k1, k2, λ1, λ2]
)
```

---

## 8. Advanced Features ### 8.1 Dynamic Controller Discovery ```python
# List available controllers
available = list_available_controllers()
# ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc'] # Get controller metadata
spec = SMC_GAIN_SPECS[SMCType.CLASSICAL]
print(f"Controller: {spec.description}")
print(f"Gains: {spec.gain_names}")
print(f"Count: {spec.n_gains}")
``` ### 8.2 Automatic Gain Fixing ```python
# example-metadata:

# runnable: false # Invalid default gains are automatically corrected

controller_gains = [25.0, 15.0, 20.0, 12.0, 8.0, 6.0] try: _validate_controller_gains(controller_gains, controller_info, 'sta_smc')
except ValueError as e: if gains is None: # Only auto-fix if using default gains if controller_type == 'sta_smc': # Fix K1 > K2 requirement controller_gains = [25.0, 15.0, 20.0, 12.0, 8.0, 6.0] # K1=25 > K2=15 # Re-validate after fix _validate_controller_gains(controller_gains, controller_info, controller_type)
``` ### 8.3 Dynamics Model Integration ```python
# example-metadata:
# runnable: false def _create_dynamics_model(config: Any) -> Optional[Any]: """Create dynamics model from configuration.""" # Try to get existing dynamics model if hasattr(config, 'dynamics_model'): return config.dynamics_model elif hasattr(config, 'physics'): return DIPDynamics(config.physics) elif hasattr(config, 'dip_params'): return DIPDynamics(config.dip_params) return None
``` ### 8.4 Fallback Configuration ```python
# example-metadata:

# runnable: false # If config creation fails, use fallback with ALL required parameters

try: controller_config = config_class(**config_params)
except Exception as e: if controller_type == 'classical_smc': fallback_params = { 'gains': controller_gains, 'max_force': 150.0, 'dt': 0.001, 'boundary_layer': 0.02, # Required 'regularization_alpha': 1e-4, 'min_regularization': 1e-10, 'max_condition_number': 1e14, 'use_adaptive_regularization': True } controller_config = config_class(**fallback_params)
```

---

## 9. Best Practices ### 9.1 Factory Selection Guidelines **Use Enterprise Factory when:**
- Need backwards compatibility with legacy code
- Require thread-safe operations
- Using complex configuration objects
- Need deprecation handling and migration support **Use Clean SMC Factory when:**
- Optimizing parameters with PSO
- Benchmarking controller performance
- Require minimal complexity
- Need strict type safety ### 9.2 PSO Integration Best Practices ```python
# example-metadata:
# runnable: false # 1. Use create_pso_controller_factory for consistent interface
factory = create_pso_controller_factory(SMCType.CLASSICAL, max_force=100.0, dt=0.01) # 2. Validate gains before PSO evaluation
valid_mask = np.array([validate_smc_gains(SMCType.CLASSICAL, gains) for gains in particles])
costs[~valid_mask] = PENALTY_VALUE # 3. Use appropriate bounds for each controller type
lower_bounds, upper_bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL) # 4. Add controller-specific constraints to PSO validation
if smc_type == SMCType.SUPER_TWISTING: K1, K2 = gains[0], gains[1] if K1 <= K2: return False # Violates stability constraint
``` ### 9.3 Configuration Best Practices ```python
# example-metadata:

# runnable: false # 1. Use frozen dataclasses for immutable configuration

@dataclass(frozen=True)
class ControllerConfig: gains: List[float] max_force: float # 2. Validate parameters in __post_init__
def __post_init__(self): if self.max_force <= 0: raise ValueError("max_force must be positive") # 3. Provide sensible defaults
boundary_layer: float = 0.01
dt: float = 0.01
``` ### 9.4 Error Handling ```python
# example-metadata:
# runnable: false # 1. Specific exception types
class FactoryConfigurationError(ValueError): pass # 2. Informative error messages
raise ValueError( f"Controller '{controller_info.get('description', 'unknown')}' " f"requires {expected_count} gains, got {len(gains)}"
) # 3. Graceful fallback
try: controller_config = config_class(**config_params)
except Exception as e: logger.debug(f"Could not create full config, using minimal config: {e}") controller_config = config_class(**fallback_params)
```

---

## 10. Troubleshooting ### 10.1 Common Issues **Issue: "Unknown controller type 'classic_smc'"** ```python

# example-metadata:

# runnable: false # Solution: Use canonical name or alias

controller = create_controller('classical_smc', ...) # Canonical
controller = create_controller('classic_smc', ...) # Alias (auto-normalized)
``` **Issue: "Super-Twisting stability requires K1 > K2 > 0"** ```python
# example-metadata:
# runnable: false # Solution: Ensure K1 > K2 in gain array
gains = [25.0, 15.0, ...] # K1=25 > K2=15 ✓
gains = [15.0, 25.0, ...] # K1=15 < K2=25 ✗
``` **Issue: "Adaptive SMC requires exactly 5 gains"** ```python
# Solution: Provide correct number of gains

gains = [k1, k2, lam1, lam2, gamma] # 5 gains
``` **Issue: "MPC controller missing optional dependency"** ```python
# Solution: Install optional dependencies or use available controllers
available = list_available_controllers()
print(f"Available: {available}")
``` ### 10.2 PSO-Specific Issues **Issue: PSO particles rejected with invalid gains** ```python
# Solution: Check gain bounds and constraints

lower, upper = get_gain_bounds_for_pso(SMCType.SUPER_TWISTING)
# Ensure K1 bounds > K2 bounds for STA-SMC

# lower[0] > lower[1], upper[0] > upper[1]

``` **Issue: Controller wrapper returns wrong data type** ```python
# Solution: Ensure wrapper extracts control value correctly
if hasattr(result, 'u'): control_value = result.u
elif isinstance(result, dict) and 'u' in result: control_value = result['u']
else: control_value = result # Fallback
``` ### 10.3 Configuration Issues **Issue: "Could not extract controller parameters"** ```python
# example-metadata:

# runnable: false # Solution: Check configuration structure

# Expected: config.controllers.classical_smc.gains

# Or: config.controller_defaults.classical_smc.gains

``` **Issue: "Dynamics model creation failed"** ```python
# Solution: Ensure config has physics parameters
if hasattr(config, 'physics'): dynamics_model = DIPDynamics(config.physics)
else: # Use None if dynamics not needed dynamics_model = None
```

---

## Conclusion The SMC Controller Factory System provides a robust, flexible, and type-safe mechanism for instantiating controllers with PSO integration. Key takeaways: - **Enterprise Factory**: Comprehensive, backwards-compatible, thread-safe

- **Clean SMC Factory**: Streamlined, PSO-optimized, research-focused
- **PSO Integration**: Simplified wrappers, automatic validation, standardized interfaces
- **Configuration Management**: Multiple sources, automatic resolution, migration support For implementation examples, see:
- `src/controllers/factory.py` - Enterprise factory implementation
- `src/controllers/factory/smc_factory.py` - Clean SMC factory implementation
- `tests/test_factory/` - test suite **Next Steps:**
- Review [Control Primitives Reference](control_primitives_reference.md) for utility functions
- Explore [PSO Optimization Workflow](../guides/workflows/pso-optimization-workflow.md) for tuning workflows
- Study [Classical SMC Technical Guide](classical_smc_technical_guide.md) for controller details

---

**Document Version:** 1.0
**Last Updated:** 2025-10-04
**Part of:** Week 2 Controllers Module Documentation
**Related:** SMC Complete Theory, Controller Comparison Theory, Technical Guides
