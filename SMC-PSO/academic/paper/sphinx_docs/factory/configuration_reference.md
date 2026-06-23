# Factory Configuration Reference ## Overview The SMC Controller Factory system provides a unified, type-safe interface for creating sliding mode controllers with parameter validation, deprecation management, and PSO optimization integration. This reference documents the factory configuration system implemented to resolve GitHub Issue #6. ## Factory Architecture ### Core Components ```

src/controllers/factory/
├── __init__.py # Main factory interface
├── smc_factory.py # Clean SMC-specific factory
├── deprecation.py # Deprecation management system
└── fallback_configs.py # Graceful degradation support
``` ### Thread Safety Implementation The factory implements thread-safe operations using `threading.RLock()`: ```python
# example-metadata:
# runnable: false # Thread-safe factory operations
_factory_lock = threading.RLock() def create_controller(controller_type: str, config: Optional[Any] = None, gains: Optional[Union[list, np.ndarray]] = None) -> Any: with _factory_lock: # Thread-safe controller creation ...
``` **Benefits:**

- Concurrent controller creation from multiple threads
- PSO optimization thread safety
- Prevention of race conditions in factory registry access ## Parameter Interface Specification ### Controller Registry Structure The factory maintains a controller registry with standardized metadata: ```python
# example-metadata:

# runnable: false CONTROLLER_REGISTRY = { 'classical_smc': { 'class': ModularClassicalSMC, 'config_class': ClassicalSMCConfig, 'default_gains': [8.0, 6.0, 4.0, 3.0, 15.0, 2.0], # [k1, k2, λ1, λ2, K, kd] 'gain_count': 6, 'description': 'Classical sliding mode controller with boundary layer', 'supports_dynamics': True, 'required_params': ['gains', 'max_force', 'boundary_layer'] }

}
``` ### Gain Resolution Hierarchy The factory resolves controller gains using a hierarchical approach: 1. **Explicit gains** (highest priority)
2. **Configuration-embedded gains**
3. **Default registry gains** (fallback) ```python
def _resolve_controller_gains( gains: Optional[Union[List[float], np.ndarray]], config: Optional[Any], controller_type: str, controller_info: Dict[str, Any]
) -> List[float]: """Resolve controller gains from multiple sources with fallback."""
``` ### Parameter Validation Framework #### Gain Validation ```python
# example-metadata:

# runnable: false def _validate_controller_gains( gains: List[float], controller_info: Dict[str, Any]

) -> None: """Validate controller gains for stability and correctness.""" # Length validation expected_count = controller_info['gain_count'] if len(gains) != expected_count: raise ValueError(f"Controller requires {expected_count} gains, got {len(gains)}") # Numerical validation if not all(isinstance(g, (int, float)) and np.isfinite(g) for g in gains): raise ValueError("All gains must be finite numbers") # Stability validation (SMC requirement) if any(g <= 0 for g in gains): raise ValueError("All gains must be positive")
``` ### Controller-Specific Parameter Handling #### Classical SMC Configuration ```python
# Classical SMC parameters with boundary layer chattering reduction
config_params = { 'gains': controller_gains, # [k1, k2, λ1, λ2, K, kd] 'max_force': 150.0, # Control saturation limit 'dt': 0.001, # Sampling time 'boundary_layer': 0.02, # Required for chattering reduction 'dynamics_model': dynamics_model # Optional plant model
}
``` #### Adaptive SMC Configuration ```python
# example-metadata:

# runnable: false # Adaptive SMC with parameter estimation

config_params = { 'gains': controller_gains, # [k1, k2, λ1, λ2, γ] 'max_force': 150.0, 'dt': 0.001, 'leak_rate': 0.01, # Parameter estimation leak 'adapt_rate_limit': 10.0, # Adaptation rate bounds 'K_min': 0.1, 'K_max': 100.0, # Adaptive gain bounds 'K_init': 10.0, # Initial adaptive gain 'alpha': 0.5, # Adaptation law exponent 'boundary_layer': 0.01, # Smooth switching 'smooth_switch': True # smooth switching
}
``` #### Super-Twisting SMC Configuration ```python
# example-metadata:
# runnable: false # Super-Twisting Algorithm (STA) SMC
config_params = { 'gains': controller_gains, # [K1, K2, k1, k2, λ1, λ2] 'max_force': 150.0, 'dt': 0.001, 'power_exponent': 0.5, # STA convergence exponent 'regularization': 1e-6, # Numerical regularization 'boundary_layer': 0.01, # Chattering reduction 'switch_method': 'tanh', # Switching function type 'damping_gain': 0.0 # Additional damping
}
``` #### Hybrid Adaptive-STA SMC Configuration ```python
# example-metadata:

# runnable: false # Hybrid controller requires sub-configurations

classical_config = ClassicalSMCConfig( gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0], max_force=150.0, dt=0.001, boundary_layer=0.02
)
adaptive_config = AdaptiveSMCConfig( gains=[12.0, 10.0, 6.0, 5.0, 2.5], max_force=150.0, dt=0.001
) config_params = { 'hybrid_mode': HybridMode.CLASSICAL_ADAPTIVE, 'dt': 0.001, 'max_force': 150.0, 'classical_config': classical_config, 'adaptive_config': adaptive_config, 'dynamics_model': dynamics_model
}
``` ## Configuration Validation Rules ### Mandatory Parameters All controllers require:
- `gains`: Non-empty list of positive finite numbers
- `max_force`: Positive control saturation limit
- `dt`: Positive sampling time ### Controller-Specific Requirements | Controller Type | Required Parameters | Gain Count | Special Validation |
|----------------|--------------------|-----------:|-------------------|
| `classical_smc` | `boundary_layer` | 6 | Surface gains > 0 |
| `adaptive_smc` | `leak_rate`, `adapt_rate_limit` | 5 | Adaptation bounds |
| `sta_smc` | `power_exponent`, `regularization` | 6 | STA stability |
| `hybrid_adaptive_sta_smc` | `classical_config`, `adaptive_config` | 4 | Sub-config validity | ### Validation Workflow ```python
# example-metadata:
# runnable: false def validate_configuration(controller_type: str, config_params: Dict[str, Any]) -> None: """configuration validation.""" # 1. Check required parameters controller_info = _get_controller_info(controller_type) required_params = controller_info['required_params'] for param in required_params: if param not in config_params: raise ValueError(f"Missing required parameter: {param}") # 2. Validate gains gains = config_params.get('gains', []) _validate_controller_gains(gains, controller_info) # 3. Controller-specific validation if controller_type == 'classical_smc': if config_params.get('boundary_layer', 0) <= 0: raise ValueError("boundary_layer must be positive") # 4. Numerical validation for key, value in config_params.items(): if key in ['max_force', 'dt', 'boundary_layer']: if not (isinstance(value, (int, float)) and value > 0): raise ValueError(f"{key} must be positive number")
``` ## Error Handling and Graceful Degradation ### Configuration Fallback Mechanism ```python
# example-metadata:

# runnable: false try: # Attempt full configuration controller_config = config_class(**config_params)

except Exception as e: logger.warning(f"Could not create full config, using minimal config: {e}") # Fallback to minimal configuration fallback_params = { 'gains': controller_gains, 'max_force': 150.0, 'dt': 0.001 } # Add controller-specific required parameters if controller_type == 'classical_smc': fallback_params['boundary_layer'] = 0.02 controller_config = config_class(**fallback_params)
``` ### Import Error Handling ```python
# Graceful handling of missing dependencies
try: from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig CONFIG_CLASSES_AVAILABLE = True
except ImportError: CONFIG_CLASSES_AVAILABLE = False # Use fallback minimal config classes from src.controllers.factory.fallback_configs import ClassicalSMCConfig
``` ### Runtime Error Recovery ```python
# example-metadata:

# runnable: false def create_controller_with_recovery(controller_type: str, config: Any, gains: Any) -> Any: """Create controller with automatic error recovery.""" try: return create_controller(controller_type, config, gains) except Exception as primary_error: logger.warning(f"Primary creation failed: {primary_error}") # Attempt recovery with minimal configuration try: minimal_config = create_minimal_config(controller_type, gains) return create_controller(controller_type, minimal_config, None) except Exception as recovery_error: logger.error(f"Recovery failed: {recovery_error}") raise primary_error

``` ## Controller Aliasing and Normalization ### Backwards Compatibility Aliases ```python
# example-metadata:
# runnable: false CONTROLLER_ALIASES = { 'classic_smc': 'classical_smc', 'smc_classical': 'classical_smc', 'smc_v1': 'classical_smc', 'super_twisting': 'sta_smc', 'sta': 'sta_smc', 'adaptive': 'adaptive_smc', 'hybrid': 'hybrid_adaptive_sta_smc', 'hybrid_sta': 'hybrid_adaptive_sta_smc',
} def _canonicalize_controller_type(name: str) -> str: """Normalize controller type names for consistency.""" if not isinstance(name, str): return name key = name.strip().lower().replace('-', '_').replace(' ', '_') return CONTROLLER_ALIASES.get(key, key)
``` ## Dynamics Model Integration ### Optional Plant Model Support ```python
# example-metadata:

# runnable: false def _create_dynamics_model(config: Any) -> Optional[Any]: """Create dynamics model from configuration with fallback handling.""" # Priority order for dynamics model resolution if hasattr(config, 'dynamics_model'): return config.dynamics_model elif hasattr(config, 'physics'): return DIPDynamics(config.physics) elif hasattr(config, 'dip_params'): return DIPDynamics(config.dip_params) return None

``` ### Controller-Dynamics Compatibility ```python
# Only add dynamics_model for controllers that support it
if dynamics_model is not None and controller_type in ['classical_smc', 'sta_smc', 'adaptive_smc', 'mpc_controller']: config_params['dynamics_model'] = dynamics_model
``` ## Factory API Interface ### Primary Factory Function ```python

def create_controller( controller_type: str, config: Optional[Any] = None, gains: Optional[Union[list, np.ndarray]] = None
) -> Any: """ Create a controller instance with validation and error handling. Thread-safe and supports multiple calling patterns for flexibility. """
``` ### Legacy Compatibility Functions ```python
# Backwards compatibility wrappers
def create_classical_smc_controller(config=None, gains=None) -> Any: return create_controller('classical_smc', config, gains) def create_sta_smc_controller(config=None, gains=None) -> Any: return create_controller('sta_smc', config, gains) def create_adaptive_smc_controller(config=None, gains=None) -> Any: return create_controller('adaptive_smc', config, gains)
``` ### Utility Functions ```python

def list_available_controllers() -> List[str]: """Get list of available controller types.""" return list(CONTROLLER_REGISTRY.keys()) def get_default_gains(controller_type: str) -> List[float]: """Get default gains for a controller type.""" return CONTROLLER_REGISTRY[controller_type]['default_gains'].copy()
``` ## Quality Assurance Integration ### Testing Coverage - **Unit Tests**: Individual component validation
- **Integration Tests**: Controller-plant-factory interaction
- **Thread Safety Tests**: Concurrent operation validation
- **Performance Tests**: Real-time constraint verification
- **Robustness Tests**: Edge case and failure mode handling ### Continuous Integration Gates ```python
# Quality gates enforced by factory
assert coverage >= 0.95 # 95% test coverage for critical components
assert thread_safety_tests_pass == True
assert memory_leak_tests_pass == True
assert performance_constraints_met == True
``` This configuration reference provides the foundation for robust, maintainable SMC controller creation with validation, error handling, and quality assurance integration.