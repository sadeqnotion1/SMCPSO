#==========================================================================================\\\
#===================== docs/api/factory_methods_reference.md =========================\\\
#==========================================================================================\\\

# Factory Methods API Reference ## Overview This document provides API reference documentation for the Enterprise Controller Factory system. The factory provides thread-safe, type-safe controller instantiation with deep PSO integration and robust error handling. ## Table of Contents 1. [Core Factory Functions](#core-factory-functions)
2. [PSO Integration Functions](#pso-integration-functions)
3. [Controller Registry Functions](#controller-registry-functions)
4. [Configuration Functions](#configuration-functions)
5. [Validation Functions](#validation-functions)
6. [Type Definitions](#type-definitions)
7. [Exceptions](#exceptions)
8. [Examples](#examples)

---

## Core Factory Functions ### `create_controller()` **Primary factory function for creating controller instances.** ```python

def create_controller( controller_type: str, config: Optional[Any] = None, gains: Optional[Union[list, np.ndarray]] = None
) -> Any
``` #### Parameters - **`controller_type`** (`str`): Controller type identifier - `'classical_smc'`: Classical sliding mode controller with boundary layer - `'sta_smc'`: Super-twisting sliding mode controller (2nd order) - `'adaptive_smc'`: Adaptive sliding mode controller with online parameter estimation - `'hybrid_adaptive_sta_smc'`: Hybrid adaptive super-twisting controller - `'mpc_controller'`: Model predictive controller (requires optional dependencies) - **`config`** (`Optional[Any]`): Configuration object containing controller parameters - Can be a Pydantic model, dataclass, or dict-like object - If provided, parameters are extracted based on controller type - Takes lower priority than explicit `gains` parameter - **`gains`** (`Optional[Union[list, np.ndarray]]`): Controller gain values - Takes highest priority in parameter resolution - Must match expected gain count for controller type - Automatically converted from numpy arrays to lists #### Returns - **Controller instance**: Configured controller implementing `ControllerProtocol` - Has `compute_control(state, last_control, history)` method - Has `reset()` method for state reset - Has `gains` property returning gain values #### Raises - **`ValueError`**: Invalid controller type or parameters - Unknown controller type - Invalid gain count or values - Parameter validation failures - **`ImportError`**: Missing required dependencies - MPC controller without optional dependencies - Missing controller implementation modules - **`ConfigValueError`**: Invalid configuration values - MPC parameter validation failures - Domain-specific parameter constraints #### Thread Safety ✅ **Thread-safe** with recursive lock and 10-second timeout protection. #### Parameter Resolution Priority 1. **Explicit `gains` parameter** (highest priority)
2. **Configuration object attributes**
3. **YAML configuration file values**
4. **Registry default values** (lowest priority) #### Example Usage ```python
# Basic usage with default parameters
controller = create_controller('classical_smc') # With explicit gains
controller = create_controller( 'classical_smc', gains=[20.0, 15.0, 12.0, 8.0, 35.0, 5.0]
) # With configuration object
from src.config import load_config
config = load_config("config.yaml")
controller = create_controller('adaptive_smc', config=config) # Combined parameters (gains override config)
controller = create_controller( 'sta_smc', config=config, gains=[25.0, 15.0, 20.0, 12.0, 8.0, 6.0] # Takes priority
)
``` #### Controller-Specific Requirements ##### Classical SMC

```python
# Required gains: [k1, k2, lambda1, lambda2, K, kd]
# Required parameters: max_force, boundary_layer, dt
controller = create_controller( 'classical_smc', gains=[20.0, 15.0, 12.0, 8.0, 35.0, 5.0]
)
``` ##### Super-Twisting SMC

```python
# Required gains: [K1, K2, k1, k2, lambda1, lambda2]
# Required parameters: max_force, dt
controller = create_controller( 'sta_smc', gains=[25.0, 15.0, 20.0, 12.0, 8.0, 6.0]
)
``` ##### Adaptive SMC

```python
# Required gains: [k1, k2, lambda1, lambda2, gamma]
# Required parameters: max_force, dt
controller = create_controller( 'adaptive_smc', gains=[25.0, 18.0, 15.0, 10.0, 4.0]
)
``` ##### Hybrid Adaptive-STA SMC

```python
# Required gains: [k1, k2, lambda1, lambda2]
# Special handling: Creates sub-controllers automatically
controller = create_controller( 'hybrid_adaptive_sta_smc', gains=[18.0, 12.0, 10.0, 8.0]
)
``` ##### MPC Controller

```python
# No traditional gains
# Required parameters: horizon, q_x, q_theta, r_u
controller = create_controller('mpc_controller') # Uses defaults
```

---

## `list_available_controllers()` **Get list of currently available controller types.** ```python

# example-metadata:

# runnable: false def list_available_controllers() -> List[str]

``` #### Returns - **`List[str]`**: List of controller type names that can actually be instantiated - Excludes controllers with missing dependencies - Only includes controllers with available implementation classes #### Example Usage ```python
available = list_available_controllers()
print("Available controllers:", available)
# Output: ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']
# Note: 'mpc_controller' only included if optional dependencies available
```

---

## `list_all_controllers()` **Get list of all registered controller types, including unavailable ones.** ```python

# example-metadata:

# runnable: false def list_all_controllers() -> List[str]

``` #### Returns - **`List[str]`**: List of all controller type names in the registry - Includes unavailable controllers for completeness - Useful for documentation and error messages #### Example Usage ```python
all_controllers = list_all_controllers()
available = list_available_controllers() unavailable = set(all_controllers) - set(available)
if unavailable: print(f"Unavailable controllers: {unavailable}") print("Check dependencies and installation")
```

---

## `get_default_gains()` **Get default gains for a specific controller type.** ```python

# example-metadata:

# runnable: false def get_default_gains(controller_type: str) -> List[float]

``` #### Parameters - **`controller_type`** (`str`): Controller type identifier #### Returns - **`List[float]`**: Default gain values for the controller - Copy of registry defaults (safe to modify) - Optimized for double-inverted pendulum system #### Raises - **`ValueError`**: Unknown controller type #### Example Usage ```python
# example-metadata:
# runnable: false # Get default gains for different controllers
classical_gains = get_default_gains('classical_smc')
print(f"Classical SMC defaults: {classical_gains}")
# Output: [20.0, 15.0, 12.0, 8.0, 35.0, 5.0] adaptive_gains = get_default_gains('adaptive_smc')
print(f"Adaptive SMC defaults: {adaptive_gains}")
# Output: [25.0, 18.0, 15.0, 10.0, 4.0] # Use as starting point for optimization
optimized_gains = optimize_controller_gains( controller_type='classical_smc', initial_gains=get_default_gains('classical_smc')
)
```

---

## PSO Integration Functions ### `create_smc_for_pso()` **Create SMC controller optimized for PSO usage.** ```python

def create_smc_for_pso( smc_type: SMCType, gains: Union[list, np.ndarray], plant_config_or_model: Optional[Any] = None, **kwargs: Any
) -> PSOControllerWrapper
``` #### Parameters - **`smc_type`** (`SMCType`): SMC controller type enum - `SMCType.CLASSICAL`: Classical sliding mode controller - `SMCType.ADAPTIVE`: Adaptive sliding mode controller - `SMCType.SUPER_TWISTING`: Super-twisting sliding mode controller - `SMCType.HYBRID`: Hybrid adaptive-STA controller - **`gains`** (`Union[list, np.ndarray]`): Controller gain values - Must match expected count for controller type - Validated for positive, finite values - **`plant_config_or_model`** (`Optional[Any]`): Plant configuration or dynamics model - Used for model-based equivalent control - Optional for most controller types - **`**kwargs`**: Additional controller parameters - `max_force`: Control saturation limit (default: 150.0) - `dt`: Control timestep (default: 0.001) - Controller-specific parameters #### Returns - **`PSOControllerWrapper`**: PSO-compatible controller wrapper - Implements standardized PSO interface - Has `validate_gains(particles)` method - Has `compute_control(state)` method - Includes safety mechanisms and error handling #### Example Usage ```python
from src.controllers.factory import create_smc_for_pso, SMCType # Create PSO-compatible controller
gains = [20.0, 15.0, 12.0, 8.0, 35.0, 5.0]
controller = create_smc_for_pso( SMCType.CLASSICAL, gains=gains, max_force=150.0, dt=0.001
) # Use in PSO fitness function
def fitness_function(test_gains): controller = create_smc_for_pso(SMCType.CLASSICAL, test_gains) return evaluate_controller_performance(controller) # Validate particle swarm
particles = np.array([ [20, 15, 12, 8, 35, 5], [25, 20, 15, 10, 40, 6], [0, 0, 0, 0, 0, 0] # Invalid
])
validity = controller.validate_gains(particles)
print(f"Particle validity: {validity}")
# Output: [True, True, False]
```

---

## `create_pso_controller_factory()` **Create a PSO-optimized controller factory function.** ```python

def create_pso_controller_factory( smc_type: SMCType, plant_config: Optional[Any] = None, **kwargs: Any
) -> Callable[[Union[list, np.ndarray]], PSOControllerWrapper]
``` #### Parameters - **`smc_type`** (`SMCType`): SMC controller type enum
- **`plant_config`** (`Optional[Any]`): Plant configuration
- **`**kwargs`**: Additional controller parameters #### Returns - **Factory function** with PSO attributes: - `factory.n_gains`: Number of gains required - `factory.controller_type`: Controller type string - `factory.max_force`: Force saturation limit - **Function signature**: `(gains) -> PSOControllerWrapper` #### Performance Benefits - ✅ **Factory overhead paid only once** (vs. per-evaluation)
- ✅ **Optimized for high-frequency PSO calls**
- ✅ **Thread-safe operation**
- ✅ **Built-in PSO metadata** #### Example Usage ```python
# example-metadata:
# runnable: false # Create factory once (expensive operation)
factory = create_pso_controller_factory( SMCType.CLASSICAL, plant_config=config.physics, max_force=150.0
) # Check factory attributes
print(f"Required gains: {factory.n_gains}")
print(f"Controller type: {factory.controller_type}")
print(f"Max force: {factory.max_force}") # Use factory many times (fast operation)
def pso_fitness_function(gains): controller = factory(gains) # Fast! return evaluate_controller_performance(controller) # PSO optimization
tuner = PSOTuner( controller_factory=pso_fitness_function, config=config
)
best_gains, best_fitness = tuner.optimize()
```

---

## `get_gain_bounds_for_pso()` **Get PSO optimization bounds for controller gains.** ```python

# example-metadata:

# runnable: false def get_gain_bounds_for_pso(smc_type: SMCType) -> Tuple[List[float], List[float]]

``` #### Parameters - **`smc_type`** (`SMCType`): SMC controller type enum #### Returns - **`Tuple[List[float], List[float]]`**: (lower_bounds, upper_bounds) - Based on control theory principles - Ensures stability and practical performance - Prevents excessive chattering and control effort #### Bounds Specifications ##### Classical SMC Bounds
```python
# Gains: [k1, k2, lambda1, lambda2, K, kd]

lower_bounds = [1.0, 1.0, 1.0, 1.0, 5.0, 0.1]
upper_bounds = [30.0, 30.0, 20.0, 20.0, 50.0, 10.0]
``` ##### Adaptive SMC Bounds
```python
# Gains: [k1, k2, lambda1, lambda2, gamma]

lower_bounds = [2.0, 2.0, 1.0, 1.0, 0.5]
upper_bounds = [40.0, 40.0, 25.0, 25.0, 10.0]
``` ##### Super-Twisting SMC Bounds
```python
# Gains: [K1, K2, k1, k2, lambda1, lambda2]

lower_bounds = [3.0, 2.0, 2.0, 2.0, 0.5, 0.5]
upper_bounds = [50.0, 30.0, 30.0, 30.0, 20.0, 20.0]
``` ##### Hybrid SMC Bounds
```python
# Gains: [k1, k2, lambda1, lambda2]

lower_bounds = [2.0, 2.0, 1.0, 1.0]
upper_bounds = [30.0, 30.0, 20.0, 20.0]
``` #### Example Usage ```python
# example-metadata:
# runnable: false # Get bounds for PSO optimization
bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)
lower_bounds, upper_bounds = bounds print(f"Lower bounds: {lower_bounds}")
print(f"Upper bounds: {upper_bounds}") # Use with PSO optimizer
pso_config = { 'bounds': bounds, 'n_particles': 30, 'max_iter': 100
} # Validate bounds make sense
assert len(lower_bounds) == 6 # Classical SMC has 6 gains
assert all(l < u for l, u in zip(lower_bounds, upper_bounds))
```

---

## `validate_smc_gains()` **Validate gains for a specific controller type.** ```python

# example-metadata:

# runnable: false def validate_smc_gains(smc_type: SMCType, gains: Union[list, np.ndarray]) -> bool

``` #### Parameters - **`smc_type`** (`SMCType`): SMC controller type enum
- **`gains`** (`Union[list, np.ndarray]`): Gain values to validate #### Returns - **`bool`**: True if gains are valid, False otherwise #### Validation Criteria 1. **Correct length**: Matches expected gain count for controller type
2. **Numeric type**: All gains are int or float
3. **Finite values**: No NaN or infinite values
4. **Positive values**: All gains must be positive (SMC stability requirement) #### Example Usage ```python
# example-metadata:
# runnable: false # Validate gains before expensive simulation
def robust_fitness_function(gains): if not validate_smc_gains(SMCType.CLASSICAL, gains): return float('inf') # Invalid gains get worst fitness controller = create_smc_for_pso(SMCType.CLASSICAL, gains) return evaluate_controller_performance(controller) # Test various gain sets
test_gains = [ [20, 15, 12, 8, 35, 5], # Valid [20, 15, 12, 8, 35], # Wrong length [20, 15, 12, 8, -35, 5], # Negative value [20, 15, 12, 8, np.inf, 5], # Infinite value
] for i, gains in enumerate(test_gains): valid = validate_smc_gains(SMCType.CLASSICAL, gains) print(f"Gains {i+1}: {'Valid' if valid else 'Invalid'}")
```

---

## Controller Registry Functions ### Registry Access Functions #### `get_controller_info()` **Internal function to get controller registry information.** ```python

# example-metadata:

# runnable: false def _get_controller_info(controller_type: str) -> Dict[str, Any]

``` **Note**: This is an internal function. Use public functions like `list_available_controllers()` instead. #### Registry Structure The `CONTROLLER_REGISTRY` contains metadata for each controller: ```python
# example-metadata:
# runnable: false CONTROLLER_REGISTRY = { 'controller_type': { 'class': ControllerClass, # Implementation class 'config_class': ConfigClass, # Configuration class 'default_gains': [float, ...], # Default gain values 'gain_count': int, # Expected number of gains 'description': str, # Human-readable description 'supports_dynamics': bool, # Supports dynamics model 'required_params': [str, ...] # Required parameters }
}
``` #### Controller Aliases The following aliases are supported for backward compatibility: ```python
# example-metadata:

# runnable: false CONTROLLER_ALIASES = { 'classic_smc': 'classical_smc', 'smc_classical': 'classical_smc', 'smc_v1': 'classical_smc', 'super_twisting': 'sta_smc', 'sta': 'sta_smc', 'adaptive': 'adaptive_smc', 'hybrid': 'hybrid_adaptive_sta_smc', 'hybrid_sta': 'hybrid_adaptive_sta_smc',

}
```

---

## Configuration Functions ### Configuration Resolution The factory system resolves configuration from multiple sources with the following priority: 1. **Explicit parameters** (highest priority)
2. **Configuration object attributes**
3. **YAML configuration defaults**
4. **Registry defaults** (lowest priority) ### `_resolve_controller_gains()` **Internal function for gain resolution from multiple sources.** ```python
def _resolve_controller_gains( gains: Optional[Union[List[float], np.ndarray]], config: Optional[Any], controller_type: str, controller_info: Dict[str, Any]
) -> List[float]
``` #### Configuration Extraction Patterns The factory supports multiple configuration patterns: ```python
# Pattern 1: Direct controller configuration

config.controllers.classical_smc.gains = [20, 15, 12, 8, 35, 5] # Pattern 2: Controller defaults
config.controller_defaults.classical_smc.gains = [20, 15, 12, 8, 35, 5] # Pattern 3: Dictionary-style access
config.controllers['classical_smc']['gains'] = [20, 15, 12, 8, 35, 5]
``` ### Deprecation Handling ```python
def check_deprecated_config(controller_type: str, params: Dict[str, Any]) -> Dict[str, Any]: """Check for deprecated parameters and apply migrations."""
``` #### Common Deprecation Mappings ```python

deprecated_mappings = { 'use_equivalent': 'enable_equivalent_control', 'k_gain': 'switching_gain', 'lambda_gains': 'surface_gains'
}
```

---

## Validation Functions ### Controller Gain Validation #### `_validate_controller_gains()` **gain validation with domain-specific checks.** ```python
def _validate_controller_gains( gains: List[float], controller_info: Dict[str, Any]
) -> None
``` #### Validation Checks 1. **Length validation**: Correct number of gains

2. **Type validation**: All gains are numeric
3. **Finite validation**: No NaN or infinite values
4. **Positivity validation**: All gains positive (SMC requirement) ### MPC Parameter Validation #### `_validate_mpc_parameters()` **Specialized validation for MPC controller parameters.** ```python
def _validate_mpc_parameters( config_params: Dict[str, Any], controller_params: Dict[str, Any]
) -> None
``` #### MPC Validation Rules ```python
# example-metadata:
# runnable: false # Horizon must be positive integer
if 'horizon' in params and (not isinstance(params['horizon'], int) or params['horizon'] < 1): raise ConfigValueError("horizon must be ≥ 1") # Geometric constraints
if 'max_cart_pos' in params and params['max_cart_pos'] <= 0: raise ConfigValueError("max_cart_pos must be > 0") # Weight parameters must be non-negative
weight_params = ['q_x', 'q_theta', 'r_u']
for param in weight_params: if param in params and params[param] < 0: raise ConfigValueError(f"{param} must be ≥ 0")
```

---

## Type Definitions ### Core Types ```python

# Type aliases for better type safety

StateVector = NDArray[np.float64] # System state vector
ControlOutput = Union[float, NDArray[np.float64]] # Control output
GainsArray = Union[List[float], NDArray[np.float64]] # Gain values
ConfigDict = Dict[str, Any] # Configuration dictionary # Generic type for controller instances
ControllerT = TypeVar('ControllerT')
``` ### Protocol Definitions #### `ControllerProtocol` **Standard interface that all controllers must implement.** ```python
# example-metadata:
# runnable: false class ControllerProtocol(Protocol): """Protocol defining the standard controller interface.""" def compute_control( self, state: StateVector, last_control: float, history: ConfigDict ) -> ControlOutput: """Compute control output for given state.""" ... def reset(self) -> None: """Reset controller internal state.""" ... @property def gains(self) -> List[float]: """Return controller gains.""" ...
``` ### Enum Definitions #### `SMCType` **Enumeration of supported SMC controller types.** ```python

class SMCType(Enum): """SMC Controller types enumeration.""" CLASSICAL = "classical_smc" ADAPTIVE = "adaptive_smc" SUPER_TWISTING = "sta_smc" HYBRID = "hybrid_adaptive_sta_smc"
``` #### `HybridMode` **Enumeration for hybrid controller operation modes.** ```python
class HybridMode(Enum): """Hybrid controller operation modes.""" CLASSICAL_ADAPTIVE = "classical_adaptive" STA_ADAPTIVE = "sta_adaptive" DYNAMIC_SWITCHING = "dynamic_switching"
```

---

## Exceptions ### Custom Exception Classes #### `ConfigValueError` **Exception raised for invalid configuration values.** ```python

class ConfigValueError(ValueError): """Exception raised for invalid configuration values.""" pass
``` **Usage Example:**
```python

try: controller = create_controller('mpc_controller', config=invalid_config)
except ConfigValueError as e: print(f"Configuration error: {e}") # Handle invalid configuration
``` ### Standard Exceptions #### `ValueError` **Raised for invalid controller types or parameters.** ```python
# example-metadata:
# runnable: false # Unknown controller type
try: controller = create_controller('invalid_controller')
except ValueError as e: print(f"Error: {e}") # Output: Unknown controller type 'invalid_controller'. Available: [...] # Invalid gain count
try: controller = create_controller('classical_smc', gains=[1, 2, 3]) # Need 6 gains
except ValueError as e: print(f"Error: {e}") # Output: Controller 'classical_smc' requires 6 gains, got 3
``` #### `ImportError` **Raised for missing dependencies or unavailable controllers.** ```python
# example-metadata:

# runnable: false # MPC without optional dependencies

try: controller = create_controller('mpc_controller')
except ImportError as e: print(f"Import error: {e}") # Output: MPC controller missing optional dependency. Available controllers: [...]
``` ### Error Handling Patterns #### Robust Error Handling ```python
# example-metadata:
# runnable: false def create_controller_safely(controller_type: str, **kwargs) -> Optional[Any]: """Create controller with error handling.""" try: return create_controller(controller_type, **kwargs) except ValueError as e: logger.error(f"Configuration error for {controller_type}: {e}") return None except ImportError as e: logger.warning(f"Import error for {controller_type}: {e}") return None except Exception as e: logger.error(f"Unexpected error creating {controller_type}: {e}") return None
``` #### Graceful Degradation ```python
# example-metadata:

# runnable: false def create_best_available_controller(preferred_types: List[str]) -> Any: """Create first available controller from preference list.""" available = list_available_controllers() for controller_type in preferred_types: if controller_type in available: try: return create_controller(controller_type) except Exception as e: logger.warning(f"Failed to create {controller_type}: {e}") continue # Fallback to any available controller if available: return create_controller(available[0]) else: raise RuntimeError("No controllers available")

```

---

## Examples ### Basic Factory Usage ```python
#!/usr/bin/env python3
"""Basic factory usage examples.""" from src.controllers.factory import create_controller, list_available_controllers def basic_factory_examples(): """Demonstrate basic factory usage patterns.""" # Check available controllers available = list_available_controllers() print(f"Available controllers: {available}") # Create controller with defaults controller = create_controller('classical_smc') print(f"Default gains: {controller.gains}") # Create with explicit gains custom_gains = [25.0, 20.0, 15.0, 10.0, 40.0, 6.0] controller = create_controller('classical_smc', gains=custom_gains) print(f"Custom gains: {controller.gains}") # Test controller functionality import numpy as np state = np.array([0.1, 0.05, 0.0, 0.0, 0.0, 0.0]) control_output = controller.compute_control(state, 0.0, {}) print(f"Control output: {control_output}") if __name__ == "__main__": basic_factory_examples()
``` ### PSO Integration Example ```python

#!/usr/bin/env python3
"""PSO integration examples.""" from src.controllers.factory import ( create_pso_controller_factory, get_gain_bounds_for_pso, validate_smc_gains, SMCType
)
import numpy as np def pso_integration_example(): """Demonstrate PSO integration patterns.""" # Get optimization bounds bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL) lower_bounds, upper_bounds = bounds print(f"Optimization bounds: {lower_bounds} to {upper_bounds}") # Create PSO-optimized factory factory = create_pso_controller_factory(SMCType.CLASSICAL) print(f"Factory requires {factory.n_gains} gains") # Define fitness function def fitness_function(gains: np.ndarray) -> float: """PSO fitness function with validation.""" # Pre-validate gains if not validate_smc_gains(SMCType.CLASSICAL, gains): return float('inf') try: # Create controller controller = factory(gains) # Simplified performance evaluation test_state = np.array([0.1, 0.05, 0.0, 0.0, 0.0, 0.0]) control_output = controller.compute_control(test_state) # Simple fitness (control effort) return abs(control_output.u) if hasattr(control_output, 'u') else abs(control_output) except Exception: return float('inf') # Test fitness function test_gains = np.array([20.0, 15.0, 12.0, 8.0, 35.0, 5.0]) fitness = fitness_function(test_gains) print(f"Test fitness: {fitness}") # Simulate PSO particle validation particles = np.random.uniform( low=lower_bounds, high=upper_bounds, size=(10, len(lower_bounds)) ) valid_particles = [] for particle in particles: if validate_smc_gains(SMCType.CLASSICAL, particle): valid_particles.append(particle) print(f"Valid particles: {len(valid_particles)}/{len(particles)}") if __name__ == "__main__": pso_integration_example()
``` ### Advanced Configuration Example ```python
#!/usr/bin/env python3
"""Advanced configuration examples.""" from src.controllers.factory import create_controller
from src.config import load_config
import numpy as np def advanced_configuration_example(): """Demonstrate advanced configuration patterns.""" # Load configuration from file config = load_config("config.yaml") # Create controllers with various configuration methods controllers = {} # Method 1: Configuration file only controllers['config_only'] = create_controller('classical_smc', config=config) # Method 2: Override gains from config custom_gains = [30.0, 25.0, 18.0, 12.0, 45.0, 8.0] controllers['override_gains'] = create_controller( 'classical_smc', config=config, gains=custom_gains # Overrides config gains ) # Method 3: Different controller types for controller_type in ['classical_smc', 'adaptive_smc', 'sta_smc']: try: controllers[controller_type] = create_controller(controller_type, config=config) except ImportError as e: print(f"Skipping {controller_type}: {e}") # Compare controller properties for name, controller in controllers.items(): print(f"{name}:") print(f" Gains: {controller.gains}") print(f" Max force: {getattr(controller, 'max_force', 'N/A')}") # Test control computation test_state = np.array([0.1, 0.05, 0.0, 0.0, 0.0, 0.0]) try: control_output = controller.compute_control(test_state, 0.0, {}) control_value = control_output.u if hasattr(control_output, 'u') else control_output print(f" Control output: {control_value:.3f}") except Exception as e: print(f" Control computation failed: {e}") print() if __name__ == "__main__": advanced_configuration_example()
``` ### Error Handling Example ```python

#!/usr/bin/env python3
"""Error handling examples.""" from src.controllers.factory import create_controller, list_available_controllers
import logging logging.basicConfig(level=logging.INFO) def error_handling_example(): """Demonstrate robust error handling patterns.""" test_cases = [ # Valid cases ('classical_smc', [20, 15, 12, 8, 35, 5], "Valid classical SMC"), ('adaptive_smc', [25, 18, 15, 10, 4], "Valid adaptive SMC"), # Error cases ('invalid_controller', None, "Unknown controller type"), ('classical_smc', [1, 2, 3], "Invalid gain count"), ('classical_smc', [-20, 15, 12, 8, 35, 5], "Negative gains"), ('mpc_controller', None, "Potentially missing dependencies"), ] for controller_type, gains, description in test_cases: print(f"Testing: {description}") try: if gains is not None: controller = create_controller(controller_type, gains=gains) else: controller = create_controller(controller_type) print(f" ✅ Success: {controller_type} created") print(f" Gains: {controller.gains}") except ValueError as e: print(f" ❌ Configuration Error: {e}") except ImportError as e: print(f" ⚠️ Import Error: {e}") available = list_available_controllers() print(f" Available: {available}") except Exception as e: print(f" 💥 Unexpected Error: {e}") print() if __name__ == "__main__": error_handling_example()
```

---

This API reference provides complete documentation for all factory methods, including detailed parameter specifications, return values, error handling, and practical examples. The documentation covers both basic usage patterns and advanced integration scenarios, ensuring developers can effectively use the factory system for their specific requirements.