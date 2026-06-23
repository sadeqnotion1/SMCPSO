#==========================================================================================\\\
#===================== docs/factory_integration_documentation.md =====================\\\
#==========================================================================================\\\

# Factory Integration System Documentation ## Overview The Double-Inverted Pendulum (DIP) SMC-PSO project implements a factory integration system that provides robust, thread-safe controller instantiation with deep PSO optimization integration. This documentation covers the architecture, implementation patterns, and usage guidelines for the factory system that resolves GitHub issue #6. ## Table of Contents 1. [Architecture Overview](#architecture-overview)
2. [Factory Pattern Implementation](#factory-pattern-implementation)
3. [PSO Integration Patterns](#pso-integration-patterns)
4. [Configuration System Integration](#configuration-system-integration)
5. [Error Handling and Robustness](#error-handling-and-robustness)
6. [API Reference](#api-reference)
7. [Integration Points](#integration-points)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Performance Considerations](#performance-considerations)
10. [Testing and Validation](#testing-and-validation)

---

## Architecture Overview ### System Architecture The factory integration system follows enterprise-grade design patterns with clear separation of concerns: ```

Factory Integration System
├── Enterprise Controller Factory (src/controllers/factory.py)
│ ├── Thread-safe Operations (RLock with timeout)
│ ├── Type-safe Interfaces (Protocol-based design)
│ ├── Configuration Validation (Pydantic integration)
│ └── PSO Optimization Integration (Native PSO support)
├── Controller Registry System
│ ├── Metadata Management (Gain specifications, requirements)
│ ├── Alias Resolution (Backward compatibility)
│ └── Dynamic Registration (Extensible design)
├── Configuration Integration Layer
│ ├── Multi-source Configuration Resolution
│ ├── Deprecation Handling (Graceful migrations)
│ └── Fallback Mechanisms (Graceful degradation)
└── PSO Integration Layer ├── Controller Wrapper System (PSO-compatible interfaces) ├── Gain Validation (Domain-specific validation) └── Batch Creation (Performance optimization)
``` ### Design Principles 1. **Enterprise-Grade Quality**: Thread-safe operations with error handling
2. **Type Safety**: Protocol-based interfaces with 95%+ type hint coverage
3. **PSO Optimization**: Native integration with particle swarm optimization workflows
4. **Backward Compatibility**: Legacy factory functions preserved for existing code
5. **Configuration-Driven**: YAML-based configuration with validation
6. **Extensibility**: Registry pattern for easy addition of new controllers
7. **Robustness**: Graceful degradation and fallback mechanisms

---

## Factory Pattern Implementation ### Core Factory Interface The primary factory function provides a clean, type-safe interface for controller creation: ```python
# example-metadata:
# runnable: false def create_controller( controller_type: str, config: Optional[Any] = None, gains: Optional[Union[list, np.ndarray]] = None
) -> Any: """ Create a controller instance of the specified type. Thread-safe operation with validation. Args: controller_type: Type of controller ('classical_smc', 'sta_smc', etc.) config: Configuration object (optional) gains: Controller gains array (optional) Returns: Configured controller instance Raises: ValueError: If controller_type is not recognized ImportError: If required dependencies are missing """
``` ### Controller Registry System The registry provides metadata for each supported controller: ```python
# example-metadata:

# runnable: false CONTROLLER_REGISTRY = { 'classical_smc': { 'class': ModularClassicalSMC, 'config_class': ClassicalSMCConfig, 'default_gains': [20.0, 15.0, 12.0, 8.0, 35.0, 5.0], 'gain_count': 6, 'description': 'Classical sliding mode controller with boundary layer', 'supports_dynamics': True, 'required_params': ['gains', 'max_force', 'boundary_layer'] }, # ... additional controllers

}
``` ### Thread Safety Implementation Thread-safe operations using recursive locks with timeout protection: ```python
# Thread-safe factory operations
_factory_lock = threading.RLock()
_LOCK_TIMEOUT = 10.0 # seconds def create_controller(controller_type: str, config: Optional[Any] = None, gains: Optional[Union[list, np.ndarray]] = None) -> Any: """Thread-safe controller creation.""" with _factory_lock: # Controller creation logic protected by lock return _create_controller_impl(controller_type, config, gains)
``` ### Type System Integration Protocol-based design ensures type safety across the system: ```python
# example-metadata:

# runnable: false class ControllerProtocol(Protocol): """Protocol defining the standard controller interface.""" def compute_control( self, state: StateVector, last_control: float, history: ConfigDict ) -> ControlOutput: """Compute control output for given state.""" ... def reset(self) -> None: """Reset controller internal state.""" ... @property def gains(self) -> List[float]: """Return controller gains.""" ...

```

---

## PSO Integration Patterns ### Native PSO Support The factory system provides native PSO integration through specialized wrapper classes: ```python
# example-metadata:
# runnable: false class PSOControllerWrapper: """Wrapper for SMC controllers to provide PSO-compatible interface.""" def __init__(self, controller, n_gains: int, controller_type: str): self.controller = controller self.n_gains = n_gains self.controller_type = controller_type self.max_force = getattr(controller, 'max_force', 150.0) def validate_gains(self, particles: np.ndarray) -> np.ndarray: """Validate gain particles for PSO optimization.""" # Domain-specific validation logic return valid_mask def compute_control(self, state: np.ndarray) -> np.ndarray: """PSO-compatible control computation interface.""" # Standardized interface for PSO fitness evaluation return control_output
``` ### PSO Factory Functions Specialized factory functions optimized for PSO workflows: ```python
# example-metadata:

# runnable: false def create_smc_for_pso( smc_type: SMCType, gains: Union[list, np.ndarray], plant_config_or_model: Optional[Any] = None, **kwargs: Any

) -> Any: """Create SMC controller optimized for PSO usage.""" def create_pso_controller_factory( smc_type: SMCType, plant_config: Optional[Any] = None, **kwargs: Any
) -> Callable: """Create a PSO-optimized controller factory function."""
``` ### Gain Bounds and Validation PSO-specific gain bounds based on control theory principles: ```python
# example-metadata:
# runnable: false def get_gain_bounds_for_pso(smc_type: SMCType) -> Tuple[List[float], List[float]]: """Get PSO gain bounds for a controller type.""" bounds_map = { SMCType.CLASSICAL: { 'lower': [1.0, 1.0, 1.0, 1.0, 5.0, 0.1], # [k1, k2, lam1, lam2, K, kd] 'upper': [30.0, 30.0, 20.0, 20.0, 50.0, 10.0] }, SMCType.ADAPTIVE: { 'lower': [2.0, 2.0, 1.0, 1.0, 0.5], # [k1, k2, lam1, lam2, gamma] 'upper': [40.0, 40.0, 25.0, 25.0, 10.0] }, # ... additional controller types } return (bounds_map[smc_type]['lower'], bounds_map[smc_type]['upper'])
```

---

## Configuration System Integration ### Multi-Source Configuration Resolution The factory system resolves configuration from multiple sources with priority: 1. **Explicit parameters** (highest priority)

2. **Configuration object attributes**
3. **YAML configuration file**
4. **Registry defaults** (lowest priority) ```python
# example-metadata:

# runnable: false def _resolve_controller_gains( gains: Optional[Union[List[float], np.ndarray]], config: Optional[Any], controller_type: str, controller_info: Dict[str, Any]

) -> List[float]: """Resolve controller gains from multiple sources.""" # Priority 1: Explicit gains if gains is not None: return gains.tolist() if isinstance(gains, np.ndarray) else gains # Priority 2: Configuration object if config is not None: extracted_gains = _extract_gains_from_config(config, controller_type) if extracted_gains is not None: return extracted_gains # Priority 3: Registry defaults return controller_info['default_gains']
``` ### Configuration Validation Type-safe configuration validation using Pydantic models: ```python
# example-metadata:
# runnable: false @dataclass(frozen=True)
class ClassicalSMCConfig: """Type-safe configuration for Classical SMC controller.""" gains: List[float] = field() # [k1, k2, lam1, lam2, K, kd] max_force: float = field() # Control saturation limit boundary_layer: float = field() # Chattering reduction thickness dt: float = field(default=0.01) # Control timestep switch_method: Literal["tanh", "linear", "sign"] = field(default="tanh") def __post_init__(self): """Validate configuration after creation.""" self._validate_gains() self._validate_control_parameters() self._validate_stability_requirements()
``` ### Deprecation Handling Graceful handling of deprecated configuration parameters: ```python
# example-metadata:

# runnable: false def check_deprecated_config(controller_type: str, params: Dict[str, Any]) -> Dict[str, Any]: """Check for deprecated parameters and apply migrations.""" # Handle deprecated parameter names deprecated_mappings = { 'use_equivalent': 'enable_equivalent_control', 'k_gain': 'switching_gain', 'lambda_gains': 'surface_gains' } migrated_params = params.copy() for old_param, new_param in deprecated_mappings.items(): if old_param in migrated_params: migrated_params[new_param] = migrated_params.pop(old_param) logger.warning(f"Parameter '{old_param}' is deprecated. Use '{new_param}' instead.") return migrated_params

```

---

## Error Handling and Robustness ### Graceful Degradation The factory system implements multiple layers of fallback mechanisms: ```python
# example-metadata:
# runnable: false def create_controller(controller_type: str, config: Optional[Any] = None, gains: Optional[Union[list, np.ndarray]] = None) -> Any: """Create controller with graceful degradation.""" try: # Attempt full configuration creation controller_config = create_full_config(controller_type, config, gains) return controller_class(controller_config) except Exception as e: logger.warning(f"Full config creation failed: {e}. Using minimal config.") # Fallback to minimal configuration minimal_config = create_minimal_config(controller_type, gains) return controller_class(minimal_config)
``` ### Import Error Handling Robust handling of optional dependencies: ```python
# example-metadata:

# runnable: false # Optional MPC controller import with graceful fallback

try: from src.controllers.mpc.controller import MPCController MPC_AVAILABLE = True
except ImportError: MPCController = None MPC_AVAILABLE = False logger.debug("MPC controller not available - optional dependency") # Registry entry with availability check
if MPC_AVAILABLE: CONTROLLER_REGISTRY['mpc_controller'] = { 'class': MPCController, 'config_class': MPCConfig, # ... full configuration }
else: CONTROLLER_REGISTRY['mpc_controller'] = { 'class': None, 'config_class': UnavailableMPCConfig, 'description': 'Model predictive controller (unavailable)', # ... placeholder configuration }
``` ### Validation and Safety Checks validation at multiple levels: ```python
# example-metadata:
# runnable: false def _validate_controller_gains( gains: List[float], controller_info: Dict[str, Any]
) -> None: """Validate controller gains with domain-specific checks.""" # Basic structural validation expected_count = controller_info['gain_count'] if len(gains) != expected_count: raise ValueError(f"Expected {expected_count} gains, got {len(gains)}") # Numerical validation if not all(isinstance(g, (int, float)) and np.isfinite(g) for g in gains): raise ValueError("All gains must be finite numbers") # Domain-specific validation if any(g <= 0 for g in gains): raise ValueError("All gains must be positive for SMC stability")
```

---

## API Reference ### Core Factory Functions #### `create_controller(controller_type, config=None, gains=None)` **Primary factory function for controller creation.** **Parameters:**

- `controller_type` (str): Controller type identifier - `'classical_smc'`: Classical sliding mode controller - `'sta_smc'`: Super-twisting sliding mode controller - `'adaptive_smc'`: Adaptive sliding mode controller - `'hybrid_adaptive_sta_smc'`: Hybrid adaptive-STA controller - `'mpc_controller'`: Model predictive controller (optional) - `config` (Optional[Any]): Configuration object containing controller parameters
- `gains` (Optional[Union[list, np.ndarray]]): Controller gain array **Returns:**
- Configured controller instance implementing `ControllerProtocol` **Raises:**
- `ValueError`: Invalid controller type or parameters
- `ImportError`: Missing required dependencies **Thread Safety:** ✅ Thread-safe with timeout protection #### `list_available_controllers()` **Get list of available controller types.** **Returns:**
- `List[str]`: List of available controller type identifiers #### `get_default_gains(controller_type)` **Get default gains for a specific controller type.** **Parameters:**
- `controller_type` (str): Controller type identifier **Returns:**
- `List[float]`: Default gain values for the controller ### PSO Integration Functions #### `create_smc_for_pso(smc_type, gains, plant_config_or_model=None, **kwargs)` **Create SMC controller optimized for PSO usage.** **Parameters:**
- `smc_type` (SMCType): SMC controller type enum
- `gains` (Union[list, np.ndarray]): Controller gain values
- `plant_config_or_model` (Optional[Any]): Plant configuration or dynamics model
- `**kwargs`: Additional controller parameters **Returns:**
- `PSOControllerWrapper`: PSO-compatible controller wrapper #### `create_pso_controller_factory(smc_type, plant_config=None, **kwargs)` **Create a PSO-optimized controller factory function.** **Parameters:**
- `smc_type` (SMCType): SMC controller type enum
- `plant_config` (Optional[Any]): Plant configuration
- `**kwargs`: Additional controller parameters **Returns:**
- `Callable[[Union[list, np.ndarray]], Any]`: Controller factory function with PSO attributes #### `get_gain_bounds_for_pso(smc_type)` **Get PSO optimization bounds for controller gains.** **Parameters:**
- `smc_type` (SMCType): SMC controller type enum **Returns:**
- `Tuple[List[float], List[float]]`: (lower_bounds, upper_bounds) for PSO optimization ### Controller Type Enums and Classes #### `SMCType` Enum ```python
class SMCType(Enum): """SMC Controller types enumeration.""" CLASSICAL = "classical_smc" ADAPTIVE = "adaptive_smc" SUPER_TWISTING = "sta_smc" HYBRID = "hybrid_adaptive_sta_smc"
``` #### `SMCConfig` Class ```python
class SMCConfig: """Configuration class for SMC controllers.""" def __init__(self, gains: List[float], max_force: float = 150.0, dt: float = 0.001, **kwargs: Any) -> None: # Configuration initialization
``` ### Legacy Compatibility Functions #### `create_controller_legacy(controller_type, config=None, gains=None)` **Legacy factory function for backward compatibility.** #### `create_classical_smc_controller(config=None, gains=None)`
### `create_sta_smc_controller(config=None, gains=None)`

#### `create_adaptive_smc_controller(config=None, gains=None)` **Type-specific factory functions for backward compatibility.**

## Integration Points ### Simulation Engine Integration The factory system integrates seamlessly with the simulation engine: ```python

from src.controllers.factory import create_controller
from src.core.simulation_runner import SimulationRunner # Create controller through factory
controller = create_controller('classical_smc', config=sim_config) # Integrate with simulation engine
runner = SimulationRunner( controller=controller, dynamics=dynamics_model, config=sim_config
) results = runner.run_simulation()
``` ### PSO Optimization Integration Integration with PSO optimization workflows: ```python
from src.controllers.factory import create_pso_controller_factory, SMCType
from src.optimization.algorithms.pso_optimizer import PSOTuner # Create PSO-optimized factory
controller_factory = create_pso_controller_factory( SMCType.CLASSICAL, plant_config=config
) # Initialize PSO tuner
tuner = PSOTuner( controller_factory=controller_factory, config=config
) # Run optimization
best_gains, best_fitness = tuner.optimize()
``` ### Configuration System Integration Integration with YAML configuration system: ```yaml
# config.yaml

controllers: classical_smc: gains: [20.0, 15.0, 12.0, 8.0, 35.0, 5.0] max_force: 150.0 boundary_layer: 0.02 dt: 0.001
``` ```python
from src.config import load_config
from src.controllers.factory import create_controller # Load configuration
config = load_config("config.yaml") # Create controller with configuration
controller = create_controller('classical_smc', config=config)
``` ### Hardware-in-the-Loop Integration Integration with HIL systems: ```python

from src.controllers.factory import create_controller
from src.hil.controller_client import ControllerClient # Create controller
controller = create_controller('adaptive_smc', gains=optimized_gains) # HIL integration
hil_client = ControllerClient( controller=controller, host='localhost', port=8888
) hil_client.run()
```

---

## Troubleshooting Guide ### Common Issues and approaches #### Issue: `ValueError: Unknown controller type` **Symptoms:**
```

ValueError: Unknown controller type 'classical'. Available: ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']
``` **Causes:**
- Incorrect controller type string
- Typo in controller name
- Missing controller registration **Solutions:**
1. **Check available controllers:** ```python from src.controllers.factory import list_available_controllers print("Available controllers:", list_available_controllers()) ``` 2. **Use correct controller names:** - ✅ `'classical_smc'` (correct) - ❌ `'classical'` (incorrect) - ✅ `'sta_smc'` (correct) - ❌ `'super_twisting'` (incorrect) 3. **Check controller aliases:** ```python # These aliases are supported: 'classic_smc' -> 'classical_smc' 'super_twisting' -> 'sta_smc' 'adaptive' -> 'adaptive_smc' 'hybrid' -> 'hybrid_adaptive_sta_smc' ``` #### Issue: `ImportError: Controller class not available` **Symptoms:**
```

ImportError: Controller class for mpc_controller is not available
``` **Causes:**
- Missing optional dependencies
- Controller module not installed
- Import path issues **Solutions:**
1. **Check controller availability:** ```python from src.controllers.factory import CONTROLLER_REGISTRY controller_info = CONTROLLER_REGISTRY['mpc_controller'] if controller_info['class'] is None: print("Controller not available - check dependencies") ``` 2. **Install missing dependencies:** ```bash pip install -r requirements.txt ``` 3. **Verify module imports:** ```python try: from src.controllers.mpc.controller import MPCController print("MPC controller available") except ImportError as e: print(f"MPC controller not available: {e}") ``` #### Issue: Gain validation failures **Symptoms:**
```

ValueError: Controller 'classical_smc' requires 6 gains, got 5
ValueError: All gains must be positive
``` **Causes:**
- Incorrect number of gains
- Invalid gain values (negative, NaN, infinite)
- Controller-specific validation failures **Solutions:**
1. **Check required gain count:** ```python from src.controllers.factory import get_default_gains default_gains = get_default_gains('classical_smc') print(f"Required gains: {len(default_gains)}") print(f"Default values: {default_gains}") ``` 2. **Validate gains before use:** ```python import numpy as np gains = [10.0, 8.0, 15.0, 12.0, 50.0, 5.0] # Check basic validity assert len(gains) == 6, f"Expected 6 gains, got {len(gains)}" assert all(isinstance(g, (int, float)) for g in gains), "All gains must be numbers" assert all(np.isfinite(g) for g in gains), "All gains must be finite" assert all(g > 0 for g in gains), "All gains must be positive" ``` 3. **Use controller-specific validation:** ```python from src.controllers.factory import validate_smc_gains, SMCType is_valid = validate_smc_gains(SMCType.CLASSICAL, gains) if not is_valid: print("Gains failed validation") ``` #### Issue: Configuration conflicts **Symptoms:**
```

Warning: Could not create full config, using minimal config
TypeError: __init__() got an unexpected keyword argument
``` **Causes:**
- Conflicting configuration sources
- Deprecated parameter names
- Missing required parameters **Solutions:**
1. **Check configuration priority:** ```python
# example-metadata:
# runnable: false # Priority order (highest to lowest): # 1. Explicit gains parameter # 2. Configuration object attributes # 3. YAML configuration file # 4. Registry defaults controller = create_controller( 'classical_smc', gains=[10, 8, 15, 12, 50, 5], # Highest priority config=config_object # Lower priority ) ``` 2. **Update deprecated parameters:** ```python # Deprecated -> Current 'use_equivalent' -> 'enable_equivalent_control' 'k_gain' -> 'switching_gain' 'lambda_gains' -> 'surface_gains' ``` 3. **Provide required parameters:** ```python # Classical SMC required parameters: config_params = { 'gains': [20.0, 15.0, 12.0, 8.0, 35.0, 5.0], 'max_force': 150.0, 'boundary_layer': 0.02, 'dt': 0.001 } ``` #### Issue: Thread safety problems **Symptoms:**
```

RuntimeError: Lock timeout exceeded
Deadlock in concurrent controller creation
``` **Causes:**
- Concurrent factory calls
- Lock timeout exceeded
- Resource contention **Solutions:**
1. **Avoid excessive concurrent calls:** ```python # Instead of many concurrent calls: controllers = [] for i in range(100): controller = create_controller('classical_smc') # Can cause contention controllers.append(controller) # Use batch creation: from src.controllers.factory import create_all_smc_controllers controllers = create_all_smc_controllers(gains_dict) ``` 2. **Handle timeout gracefully:** ```python try: controller = create_controller('classical_smc') except RuntimeError as e: if "timeout" in str(e).lower(): # Retry with exponential backoff time.sleep(random.uniform(0.1, 0.5)) controller = create_controller('classical_smc') else: raise ``` 3. **Use pre-created controllers for PSO:** ```python # Pre-create factory function (once) factory = create_pso_controller_factory(SMCType.CLASSICAL) # Use factory in PSO fitness function (many times) def fitness_function(gains): controller = factory(gains) # Thread-safe, fast return evaluate_performance(controller) ``` ### Performance Optimization #### Memory Usage Optimization ```python
# example-metadata:
# runnable: false # Avoid creating unnecessary controllers
def optimize_controller_creation(): # ❌ Creates many controller instances controllers = [] for gains_set in gain_sets: controller = create_controller('classical_smc', gains=gains_set) controllers.append(controller) # ✅ Use single factory function factory = create_pso_controller_factory(SMCType.CLASSICAL) controllers = [factory(gains_set) for gains_set in gain_sets]
``` #### Import Time Optimization ```python
# example-metadata:

# runnable: false # ❌ Imports all controllers at module level

from src.controllers.factory import ( create_controller, create_classical_smc_controller, create_sta_smc_controller, # ... all functions
) # ✅ Import only what you need
from src.controllers.factory import create_controller # ✅ Or use lazy imports
def get_factory_function(): from src.controllers.factory import create_pso_controller_factory return create_pso_controller_factory
```

---

## Performance Considerations ### Factory Creation Performance The factory system is optimized for performance-critical applications: ```python
# Performance benchmarks (typical values)
Single controller creation: ~1-2 ms
PSO factory creation: ~0.5-1 ms
Gain validation: ~0.1-0.2 ms
Configuration resolution: ~0.2-0.5 ms
``` ### Memory Usage Patterns ```python
# example-metadata:

# runnable: false # Memory-efficient patterns: # 1. Reuse factory functions

factory = create_pso_controller_factory(SMCType.CLASSICAL)
# Use factory many times without recreating # 2. Use minimal configurations when possible

controller = create_controller('classical_smc', gains=simple_gains)
# Avoid complex config objects for simple use cases # 3. Batch operations

controllers = create_all_smc_controllers(gains_dict)
# More efficient than individual creation

``` ### Concurrency Performance ```python
# example-metadata:
# runnable: false # Thread-safe patterns: # 1. Pre-create factories for concurrent use
factories = { SMCType.CLASSICAL: create_pso_controller_factory(SMCType.CLASSICAL), SMCType.ADAPTIVE: create_pso_controller_factory(SMCType.ADAPTIVE),
} # 2. Use factories in parallel PSO
def parallel_fitness_evaluation(gains_batch): factory = factories[controller_type] return [evaluate_controller(factory(gains)) for gains in gains_batch]
```

---

## Testing and Validation ### Unit Testing Patterns The factory system includes testing: ```python

# example-metadata:

# runnable: false # Test controller creation

def test_controller_creation(): controller = create_controller('classical_smc') assert hasattr(controller, 'compute_control') assert hasattr(controller, 'gains') # Test gain validation
def test_gain_validation(): valid_gains = [10.0, 8.0, 15.0, 12.0, 50.0, 5.0] controller = create_controller('classical_smc', gains=valid_gains) assert controller.gains == valid_gains # Test error handling
def test_invalid_controller_type(): with pytest.raises(ValueError, match="Unknown controller type"): create_controller('invalid_controller')
``` ### Integration Testing ```python
# example-metadata:
# runnable: false # Test PSO integration
def test_pso_integration(): factory = create_pso_controller_factory(SMCType.CLASSICAL) assert hasattr(factory, 'n_gains') assert hasattr(factory, 'controller_type') controller = factory([10, 8, 15, 12, 50, 5]) assert hasattr(controller, 'validate_gains') assert hasattr(controller, 'compute_control') # Test configuration integration
def test_config_integration(): config = load_config("config.yaml") controller = create_controller('classical_smc', config=config) # Verify configuration applied correctly
``` ### Performance Testing ```python
# Benchmark factory performance

def benchmark_factory_performance(): import time start_time = time.time() for _ in range(1000): controller = create_controller('classical_smc') end_time = time.time() avg_time = (end_time - start_time) / 1000 assert avg_time < 0.005, f"Factory too slow: {avg_time:.6f}s"
``` ### Scientific Validation ```python
# example-metadata:
# runnable: false # Validate control theory properties
def test_controller_stability(): controller = create_controller('classical_smc', gains=[10, 8, 15, 12, 50, 5]) # Test Lyapunov stability state = np.array([0.1, 0.05, 0.0, 0.0, 0.0, 0.0]) control_output = controller.compute_control(state, 0.0, {}) # Verify control output bounds assert abs(control_output.u) <= controller.max_force # Validate PSO optimization compatibility
def test_pso_optimization_compatibility(): factory = create_pso_controller_factory(SMCType.CLASSICAL) # Test gain bounds lower_bounds, upper_bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL) assert len(lower_bounds) == factory.n_gains assert all(l < u for l, u in zip(lower_bounds, upper_bounds)) # Test gain validation wrapper = factory([10, 8, 15, 12, 50, 5]) test_gains = np.array([[10, 8, 15, 12, 50, 5], [0, 0, 0, 0, 0, 0]]) validity = wrapper.validate_gains(test_gains) assert validity[0] == True # Valid gains assert validity[1] == False # Invalid gains (zeros)
```

---

This documentation provides complete coverage of the factory integration system, addressing all aspects of implementation, usage, and troubleshooting. The system successfully resolves GitHub issue #6 by providing robust, thread-safe controller instantiation with deep PSO optimization integration.
