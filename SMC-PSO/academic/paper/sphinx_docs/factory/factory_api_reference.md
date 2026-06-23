#==========================================================================================\\\
#==================== docs/factory/factory_api_reference.md ========================\\\
#==========================================================================================\\\

# Factory API Reference
## GitHub Issue #6 Enhanced Controller Factory System ### Overview This API reference documents the enhanced controller factory system implemented as part of GitHub Issue #6 resolution. The factory provides thread-safe, type-safe controller instantiation with advanced validation and PSO optimization support. ## Core Factory Functions ### `create_controller(controller_type, config=None, gains=None)` **Primary factory function for creating controller instances.** #### Signature

```python
def create_controller( controller_type: str, config: Optional[Any] = None, gains: Optional[Union[List[float], np.ndarray]] = None
) -> Any
``` #### Parameters | Parameter | Type | Description | Required |

|-----------|------|-------------|----------|
| `controller_type` | `str` | Controller type identifier | ✓ |
| `config` | `Optional[Any]` | Configuration object | ✗ |
| `gains` | `Optional[Union[List[float], np.ndarray]]` | Controller gains array | ✗ | #### Supported Controller Types | Controller Type | Aliases | Gain Count | Description |
|----------------|---------|------------|-------------|
| `'classical_smc'` | `'classic_smc'`, `'smc_classical'`, `'smc_v1'` | 6 | Classical sliding mode controller |
| `'sta_smc'` | `'super_twisting'`, `'sta'` | 6 | Super-twisting sliding mode controller |
| `'adaptive_smc'` | `'adaptive'` | 5 | Adaptive sliding mode controller |
| `'hybrid_adaptive_sta_smc'` | `'hybrid'`, `'hybrid_sta'` | 4 | Hybrid adaptive-STA controller |
| `'mpc_controller'` | - | 0 | Model predictive controller (if available) | #### Returns
Controller instance implementing the `ControllerProtocol` #### Raises
- `ValueError`: Invalid controller type or parameters
- `ImportError`: Missing required dependencies #### Examples ```python
# example-metadata:

# runnable: false # Basic controller creation

controller = create_controller( 'classical_smc', gains=[20.0, 15.0, 12.0, 8.0, 35.0, 5.0]
) # With configuration object
from src.config import load_config
config = load_config("config.yaml")
controller = create_controller('adaptive_smc', config=config) # Using controller type aliases
controller = create_controller('classic_smc', gains=[...]) # Alias for classical_smc
``` ### `list_available_controllers()` **Returns list of available controller types.** #### Signature
```python
# example-metadata:

# runnable: false def list_available_controllers() -> List[str]

``` #### Returns
List of available controller type strings #### Example
```python

available = list_available_controllers()
print(available)
# Output: ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']

``` ### `get_default_gains(controller_type)` **Returns default gains for a controller type.** #### Signature
```python
# example-metadata:

# runnable: false def get_default_gains(controller_type: str) -> List[float]

``` #### Parameters
| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `controller_type` | `str` | Controller type identifier | ✓ | #### Returns
List of default gain values #### Raises
- `ValueError`: Unknown controller type #### Example
```python

defaults = get_default_gains('classical_smc')
print(defaults)
# Output: [20.0, 15.0, 12.0, 8.0, 35.0, 5.0]

``` ## Type Definitions and Protocols ### `ControllerProtocol` **Protocol defining the standard controller interface.** ```python
# example-metadata:
# runnable: false class ControllerProtocol(Protocol): def compute_control( self, state: StateVector, last_control: float, history: ConfigDict ) -> ControlOutput: """Compute control output for given state.""" ... def reset(self) -> None: """Reset controller internal state.""" ... @property def gains(self) -> List[float]: """Return controller gains.""" ...
``` ### Type Aliases ```python

StateVector = NDArray[np.float64] # 6-element state vector [θ₁, θ₂, x, θ̇₁, θ̇₂, ẋ]
ControlOutput = Union[float, NDArray[np.float64]] # Scalar or array control output
GainsArray = Union[List[float], NDArray[np.float64]] # Controller gains
ConfigDict = Dict[str, Any] # Configuration dictionary
``` ## Controller-Specific APIs ### Classical SMC Configuration #### Required Parameters
```python

classical_params = { 'gains': List[float], # [k1, k2, λ1, λ2, K, kd] - 6 elements 'max_force': float, # Maximum control force [N] 'boundary_layer': float, # Boundary layer thickness 'dt': float # Time step [s]
}
``` #### Mathematical Foundation
- **Gains**: `[k1, k2, λ1, λ2, K, kd]` - `k1, k2`: Proportional gains for pendulum 1 and 2 - `λ1, λ2`: Sliding surface coefficients - `K`: Switching gain magnitude - `kd`: Derivative gain for chattering reduction - **Sliding Surface**: `s = λ₁e₁ + λ₂e₂ + ė₁ + ė₂`
- **Control Law**: `u = -K·sign(s) + u_eq` #### Example
```python

controller = create_controller( 'classical_smc', gains=[20.0, 15.0, 12.0, 8.0, 35.0, 5.0], max_force=150.0, boundary_layer=0.02, dt=0.001
)
``` ### Super-Twisting SMC Configuration #### Required Parameters
```python

sta_params = { 'gains': List[float], # [K1, K2, k1, k2, λ1, λ2] - 6 elements 'max_force': float, # Maximum control force [N] 'dt': float, # Time step [s] 'power_exponent': float, # Super-twisting power (typically 0.5) 'regularization': float, # Numerical regularization 'boundary_layer': float, # Boundary layer thickness 'switch_method': str # Switching function ('tanh', 'sign', 'linear')
}
``` #### Mathematical Foundation
- **Gains**: `[K1, K2, k1, k2, λ1, λ2]` - `K1, K2`: Super-twisting algorithmic gains - `k1, k2`: Surface proportional gains - `λ1, λ2`: Sliding surface coefficients - **Super-Twisting Algorithm**: ``` u̇ = -K₂·sign(s) u = -K₁·|s|^α·sign(s) + ∫u̇dt ``` #### Example
```python

controller = create_controller( 'sta_smc', gains=[25.0, 15.0, 20.0, 12.0, 8.0, 6.0], max_force=150.0, dt=0.001, power_exponent=0.5, regularization=1e-6, switch_method='tanh'
)
``` ### Adaptive SMC Configuration #### Required Parameters
```python
# example-metadata:

# runnable: false adaptive_params = { 'gains': List[float], # [k1, k2, λ1, λ2, γ] - 5 elements 'max_force': float, # Maximum control force [N] 'dt': float, # Time step [s] 'leak_rate': float, # Adaptation leak rate 'adapt_rate_limit': float, # Maximum adaptation rate 'K_min': float, # Minimum switching gain 'K_max': float, # Maximum switching gain 'K_init': float, # Initial switching gain 'alpha': float, # Adaptation law parameter 'boundary_layer': float, # Boundary layer thickness 'smooth_switch': bool # smooth switching

}
``` #### Mathematical Foundation
- **Gains**: `[k1, k2, λ1, λ2, γ]` - `k1, k2`: Proportional gains for pendulum 1 and 2 - `λ1, λ2`: Sliding surface coefficients - `γ`: Adaptation rate - **Adaptation Law**: `K̇ = γ·|s| - σ·K` (with leak rate σ)
- **Control Law**: `u = -K(t)·sign(s) + u_eq` #### Example
```python
# example-metadata:

# runnable: false controller = create_controller( 'adaptive_smc', gains=[25.0, 18.0, 15.0, 10.0, 4.0], max_force=150.0, dt=0.001, leak_rate=0.01, adapt_rate_limit=10.0, K_min=0.1, K_max=100.0, alpha=0.5

)
``` ### Hybrid Adaptive-STA SMC Configuration #### Required Parameters
```python

hybrid_params = { 'gains': List[float], # [k1, k2, λ1, λ2] - 4 surface gains 'hybrid_mode': HybridMode, # Hybrid mode enumeration 'max_force': float, # Maximum control force [N] 'dt': float, # Time step [s] 'classical_config': ClassicalSMCConfig, # Sub-controller configuration 'adaptive_config': AdaptiveSMCConfig # Sub-controller configuration
}
``` #### Mathematical Foundation
- **Surface Gains**: `[k1, k2, λ1, λ2]` - unified sliding surface
- **Hybrid Modes**: `CLASSICAL_ADAPTIVE`, `STA_ADAPTIVE`, `FULL_HYBRID`
- **Mode Switching**: Performance-based or error-threshold switching #### Example
```python

from src.controllers.smc.algorithms.hybrid.config import HybridMode controller = create_controller( 'hybrid_adaptive_sta_smc', gains=[18.0, 12.0, 10.0, 8.0], hybrid_mode=HybridMode.CLASSICAL_ADAPTIVE, max_force=150.0, dt=0.001
)
``` ## PSO Integration APIs ### `create_pso_controller_factory(smc_type, **kwargs)` **Creates PSO-optimized controller factory function.** #### Signature
```python

def create_pso_controller_factory( smc_type: SMCType, plant_config: Optional[Any] = None, **kwargs: Any
) -> Callable[[Union[List[float], np.ndarray]], Any]
``` #### Parameters
| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `smc_type` | `SMCType` | SMC controller type enum | ✓ |
| `plant_config` | `Optional[Any]` | Plant configuration | ✗ |
| `**kwargs` | `Any` | Additional controller parameters | ✗ | #### Returns
Factory function compatible with PSO optimization #### Example
```python

from src.controllers.factory import SMCType, create_pso_controller_factory # Create PSO factory for classical SMC
factory_func = create_pso_controller_factory( SMCType.CLASSICAL, max_force=150.0, boundary_layer=0.02
) # Use in PSO optimization
optimized_gains = pso_optimizer.optimize(factory_func)
``` ### `get_gain_bounds_for_pso(smc_type)` **Returns PSO optimization bounds for controller type.** #### Signature
```python
# example-metadata:

# runnable: false def get_gain_bounds_for_pso(smc_type: SMCType) -> Tuple[List[float], List[float]]

``` #### Parameters
| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `smc_type` | `SMCType` | SMC controller type enum | ✓ | #### Returns
Tuple of `(lower_bounds, upper_bounds)` lists #### Controller-Specific Bounds | Controller | Lower Bounds | Upper Bounds |
|-----------|--------------|--------------|
| Classical | `[1.0, 1.0, 1.0, 1.0, 5.0, 0.1]` | `[30.0, 30.0, 20.0, 20.0, 50.0, 10.0]` |
| Adaptive | `[2.0, 2.0, 1.0, 1.0, 0.5]` | `[40.0, 40.0, 25.0, 25.0, 10.0]` |
| Super-Twisting | `[3.0, 2.0, 2.0, 2.0, 0.5, 0.5]` | `[50.0, 30.0, 30.0, 30.0, 20.0, 20.0]` |
| Hybrid | `[2.0, 2.0, 1.0, 1.0]` | `[30.0, 30.0, 20.0, 20.0]` | #### Example
```python

from src.controllers.factory import SMCType, get_gain_bounds_for_pso bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)
lower, upper = bounds
print(f"Lower bounds: {lower}")
print(f"Upper bounds: {upper}")
``` ### `validate_smc_gains(smc_type, gains)` **Validates gains for controller type.** #### Signature
```python
# example-metadata:

# runnable: false def validate_smc_gains(smc_type: SMCType, gains: Union[List[float], np.ndarray]) -> bool

``` #### Parameters
| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `smc_type` | `SMCType` | SMC controller type enum | ✓ |
| `gains` | `Union[List[float], np.ndarray]` | Gains to validate | ✓ | #### Returns
`True` if gains are valid, `False` otherwise #### Validation Criteria
1. **Length validation**: Correct number of gains for controller type
2. **Type validation**: All gains must be numeric
3. **Range validation**: All gains must be positive
4. **Stability validation**: Controller-specific stability constraints #### Example
```python

from src.controllers.factory import SMCType, validate_smc_gains gains = [20.0, 15.0, 12.0, 8.0, 35.0, 5.0]
is_valid = validate_smc_gains(SMCType.CLASSICAL, gains)
print(f"Gains valid: {is_valid}")
``` ## SMC Enumeration Types ### `SMCType` **Enumeration of SMC controller types.** ```python
class SMCType(Enum): CLASSICAL = "classical_smc" ADAPTIVE = "adaptive_smc" SUPER_TWISTING = "sta_smc" HYBRID = "hybrid_adaptive_sta_smc"
``` #### Usage

```python
from src.controllers.factory import SMCType # Type-safe controller specification
controller_type = SMCType.CLASSICAL
factory_func = create_pso_controller_factory(controller_type)
``` ## Configuration Classes ### `SMCConfig` **General SMC configuration dataclass.** ```python

@dataclass
class SMCConfig: gains: List[float] max_force: float = 150.0 dt: float = 0.001 **kwargs: Any
``` #### Example
```python

from src.controllers.factory import SMCConfig config = SMCConfig( gains=[20.0, 15.0, 12.0, 8.0, 35.0, 5.0], max_force=150.0, boundary_layer=0.02
)
``` ## Deprecation Management APIs ### `check_deprecated_config(controller_type, config_params)` **Checks and migrates deprecated configuration parameters.** #### Signature
```python

def check_deprecated_config( controller_type: str, config_params: Dict[str, Any]
) -> Dict[str, Any]
``` #### Parameters
| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `controller_type` | `str` | Controller type identifier | ✓ |
| `config_params` | `Dict[str, Any]` | Configuration parameters | ✓ | #### Returns
Updated configuration with deprecated parameters migrated #### Example
```python

from src.controllers.factory.deprecation import check_deprecated_config old_config = { 'switch_function': 'sign', # Old parameter name 'gamma': 0.1 # Invalid for classical SMC
} migrated_config = check_deprecated_config('classical_smc', old_config)
# Result: {'switch_method': 'sign'}

# Warning: Removed invalid 'gamma' parameter

``` ### `get_controller_migration_guide(controller_type)` **Returns migration guide for controller type.** #### Signature
```python
# example-metadata:

# runnable: false def get_controller_migration_guide(controller_type: str) -> List[str]

``` #### Parameters
| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `controller_type` | `str` | Controller type identifier | ✓ | #### Returns
List of migration guidance strings #### Example
```python

from src.controllers.factory.deprecation import get_controller_migration_guide guide = get_controller_migration_guide('classical_smc')
for instruction in guide: print(f"- {instruction}")
``` ## Thread Safety ### Thread Safety Guarantees The factory system provides thread safety: 1. **Reentrant Locks**: All factory operations use `threading.RLock()`
2. **Timeout Protection**: 10-second timeout on lock acquisition
3. **Immutable Registry**: Controller registry is read-only after initialization
4. **Instance Isolation**: Each controller instance is independent ### Thread-Safe Usage Patterns ```python
import threading
from src.controllers.factory import create_controller def worker_thread(thread_id): """Thread-safe controller creation.""" controller = create_controller( 'classical_smc', gains=[20.0, 15.0, 12.0, 8.0, 35.0, 5.0] ) # Each thread gets independent controller instance return controller # Safe concurrent execution
threads = []
for i in range(10): thread = threading.Thread(target=worker_thread, args=(i,)) threads.append(thread) thread.start() for thread in threads: thread.join()
``` ## Error Handling ### Exception Hierarchy ```python
# example-metadata:

# runnable: false # Factory-specific exceptions

ValueError: ├── Unknown controller type ├── Invalid parameter count ├── Invalid parameter values └── Configuration validation errors ImportError: ├── Missing controller dependencies └── Optional feature unavailable TimeoutError: └── Thread lock acquisition timeout
``` ### Error Recovery Patterns ```python
from src.controllers.factory import create_controller, get_default_gains

def robust_controller_creation(controller_type, gains=None):
    """Robust controller creation with error recovery."""

    try:
        return create_controller(controller_type, gains=gains) except ValueError as e: if "gains" in str(e): # Use default gains on validation error default_gains = get_default_gains(controller_type) return create_controller(controller_type, gains=default_gains) else: raise except ImportError: # Fallback to basic controller type return create_controller('classical_smc', gains=gains)
``` ## Performance Considerations ### Factory Performance Metrics | Operation | Typical Time | Memory Usage | Thread Safety |

|-----------|--------------|--------------|---------------|
| `create_controller()` | ~1-5ms | ~50-100KB | ✓ Full |
| `list_available_controllers()` | ~0.1ms | ~1KB | ✓ Read-only |
| `get_default_gains()` | ~0.1ms | ~1KB | ✓ Read-only |
| `validate_smc_gains()` | ~0.5ms | ~10KB | ✓ Stateless | ### Optimization Strategies 1. **Controller Reuse**: Cache controller instances when parameters don't change
2. **Batch Creation**: Use thread pools for creating multiple controllers
3. **Lazy Loading**: Only create controllers when needed
4. **Parameter Validation**: Validate before expensive operations ```python
# Optimized batch controller creation

import concurrent.futures
from src.controllers.factory import create_controller def create_controllers_optimized(controller_specs): """Optimized parallel controller creation.""" with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor: futures = { executor.submit(create_controller, **spec): name for name, spec in controller_specs.items() } controllers = {} for future in concurrent.futures.as_completed(futures): name = futures[future] try: controllers[name] = future.result(timeout=30) except Exception as e: print(f"Failed to create {name}: {e}") return controllers
``` ## API Evolution and Versioning ### Backward Compatibility Policy 1. **Legacy Functions**: Deprecated functions remain available with warnings
2. **Parameter Migration**: Automatic migration of deprecated parameters
3. **Interface Stability**: Core interfaces maintain backward compatibility
4. **Deprecation Timeline**: 3-version deprecation cycle before removal ### Version History | Version | Changes | Compatibility |
|---------|---------|---------------|
| 2.0.0 | GitHub Issue #6 resolution | ✓ Full backward compatibility |
| 1.x.x | Legacy factory system | ✓ Supported via compatibility layer | ### Future API Changes Planned enhancements maintain backward compatibility:
- Enhanced type safety with generic types
- Additional controller types
- Improved PSO integration
- Advanced validation features ## Usage Examples ### Complete Workflow Example ```python
from src.controllers.factory import ( create_controller, SMCType, get_gain_bounds_for_pso, create_pso_controller_factory
)
from src.optimizer.pso_optimizer import PSOTuner # 1. Create initial controller
controller = create_controller( 'classical_smc', gains=[20.0, 15.0, 12.0, 8.0, 35.0, 5.0]
) # 2. Set up PSO optimization
bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)
factory_func = create_pso_controller_factory(SMCType.CLASSICAL) tuner = PSOTuner( controller_factory=factory_func, bounds=bounds, n_particles=20, max_iterations=200
) # 3. Optimize controller gains
optimized_gains, best_cost = tuner.optimize() # 4. Create optimized controller
optimized_controller = create_controller( 'classical_smc', gains=optimized_gains
) print(f"Optimization improved cost from {initial_cost} to {best_cost}")
``` This API reference provides documentation for the enhanced factory system, enabling efficient and reliable controller creation for advanced control systems research.