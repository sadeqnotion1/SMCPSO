# Controller Factory Integration Technical Documentation ## Overview This document provides technical documentation for the controller factory pattern implementation in the double-inverted pendulum sliding mode control (DIP-SMC) system. The factory pattern serves as the primary instantiation mechanism for all SMC variants, ensuring consistent interfaces, robust error handling, and integration with optimization algorithms. ## Table of Contents 1. [Factory Pattern Architecture](#factory-pattern-architecture)

2. [Controller Registry System](#controller-registry-system)
3. [Configuration Management](#configuration-management)
4. [Integration Protocols](#integration-protocols)
5. [Error Handling & Recovery](#error-handling--recovery)
6. [PSO Integration Workflows](#pso-integration-workflows)
7. [Performance Requirements](#performance-requirements)
8. [Mathematical Foundations](#mathematical-foundations)

---

## Factory Pattern Architecture ### Design Principles The controller factory implements a robust factory pattern with the following core principles: 1. **Type Safety**: All controller instantiation uses strict type checking

2. **Configuration Validation**: parameter validation before instantiation
3. **Error Resilience**: Graceful fallback mechanisms for configuration failures
4. **Interface Consistency**: Uniform API across all controller types
5. **Extensibility**: Support for adding new controller types without breaking existing code ### Core Factory Interface ```python
def create_controller( controller_type: str, config: Optional[Any] = None, gains: Optional[Union[list, np.ndarray]] = None
) -> Any
``` **Parameters:**
- `controller_type`: String identifier for controller type (supports aliases)
- `config`: Optional configuration object with system parameters
- `gains`: Optional gain vector override **Returns:**
- Fully configured controller instance ready for control computation ### Factory Pattern Implementation ```mermaid
graph TD A[create_controller] --> B[_canonicalize_controller_type] B --> C[Registry Lookup] C --> D[Configuration Creation] D --> E[Controller Instantiation] E --> F[Return Controller] C --> G{Type Found?} G -->|No| H[ValueError] G -->|Yes| D D --> I{Config Valid?} I -->|No| J[Fallback Config] I -->|Yes| E J --> E
```

---

## Controller Registry System ### Registry Structure The `CONTROLLER_REGISTRY` provides a centralized mapping of controller types to their implementations: ```python

# example-metadata:

# runnable: false CONTROLLER_REGISTRY = { 'classical_smc': { 'class': ModularClassicalSMC, 'config_class': ClassicalSMCConfig, 'default_gains': [5.0, 5.0, 5.0, 0.5, 0.5, 0.5] }, 'sta_smc': { 'class': ModularSuperTwistingSMC, 'config_class': STASMCConfig, 'default_gains': [5.0, 3.0, 4.0, 4.0, 0.4, 0.4] }, 'adaptive_smc': { 'class': ModularAdaptiveSMC, 'config_class': AdaptiveSMCConfig, 'default_gains': [10.0, 8.0, 5.0, 4.0, 1.0] }, 'hybrid_adaptive_sta_smc': { 'class': ModularHybridSMC, 'config_class': HybridAdaptiveSTASMCConfig, 'default_gains': [5.0, 5.0, 5.0, 0.5] }

}
``` ### Alias Management The factory supports multiple naming conventions through the `ALIAS_MAP`: ```python
# example-metadata:
# runnable: false ALIAS_MAP = { 'classic_smc': 'classical_smc', 'smc_classical': 'classical_smc', 'smc_v1': 'classical_smc', 'super_twisting': 'sta_smc', 'sta': 'sta_smc', 'adaptive': 'adaptive_smc', 'hybrid': 'hybrid_adaptive_sta_smc', 'hybrid_sta': 'hybrid_adaptive_sta_smc',
}
``` ### Controller Type Canonicalization ```python

def _canonicalize_controller_type(name: str) -> str: """Normalize and alias controller type names.""" if not isinstance(name, str): return name key = name.strip().lower().replace('-', '_').replace(' ', '_') return ALIAS_MAP.get(key, key)
```

---

## Configuration Management ### Configuration Hierarchy The factory implements a sophisticated configuration resolution hierarchy: 1. **Direct Gains Parameter** (highest priority)
2. **Config Object Gains** (from passed configuration)
3. **Default Registry Gains** (fallback) ### Type-Safe Configuration Classes Each controller type has a dedicated configuration class with validation: #### Classical SMC Configuration ```python
@dataclass(frozen=True)
class ClassicalSMCConfig: gains: List[float] # [k1, k2, λ1, λ2, K, kd] max_force: float boundary_layer: float dt: float = 0.01 switch_method: Literal["tanh", "linear", "sign"] = "tanh" regularization: float = 1e-10 dynamics_model: Optional[object] = None
``` **Validation Rules:**

- Surface gains [k1, k2, λ1, λ2] must be positive for Hurwitz stability
- Switching gain K must be positive for reaching condition
- Boundary layer must be positive to prevent division by zero
- Numerical bounds: gains ∈ [1e-12, 1e5] for numerical stability #### Super-Twisting SMC Configuration ```python
@dataclass(frozen=True)
class STASMCConfig: gains: List[float] # [K1, K2, c1, λ1, c2, λ2] max_force: float dt: float = 0.001 K1: float = 4.0 # First-order gain K2: float = 0.4 # Second-order gain power_exponent: float = 0.5 # Finite-time convergence exponent regularization: float = 1e-6
``` **Validation Rules:**
- K1 > K2 > 0 for finite-time stability
- Power exponent ∈ (0, 1) for finite-time convergence
- Surface gains must satisfy Lyapunov conditions ### Configuration Resolution Algorithm ```python
# example-metadata:
# runnable: false def resolve_configuration(controller_type, config, gains): """Resolve configuration with fallback mechanisms.""" # 1. Resolve gains if gains is not None: controller_gains = gains elif config and hasattr(config, 'controllers'): controller_gains = extract_gains_from_config(config, controller_type) else: controller_gains = get_default_gains(controller_type) # 2. Create configuration object try: return create_validated_config(controller_type, controller_gains, config) except ValidationError: return create_fallback_config(controller_type, controller_gains)
```

---

## Integration Protocols ### Cross-Domain Integration Architecture The factory provides integration between multiple system domains: ```mermaid

graph LR A[Factory] --> B[Controllers] A --> C[Plant Models] A --> D[Optimization] A --> E[Simulation] B --> F[SMC Variants] C --> G[Dynamics Models] D --> H[PSO Tuning] E --> I[Batch Simulation]
``` ### Plant Model Integration The factory automatically resolves dynamics models: ```python
def resolve_dynamics_model(config): """Resolve dynamics model from configuration.""" if hasattr(config, 'dynamics_model'): return config.dynamics_model elif hasattr(config, 'physics'): return DoubleInvertedPendulum(config.physics) elif hasattr(config, 'dip_params'): return DoubleInvertedPendulum(config.dip_params) return None
``` ### Controller Interface Specification All factory-created controllers implement the unified interface: ```python

class ControllerInterface: def compute_control( self, state: np.ndarray, last_control: Any, history: dict ) -> ControlResult: """Compute control action for given state.""" pass
``` **Control Result Structure:**
```python

@dataclass
class ControlResult: u: float # Control action sliding_surface: float # Current sliding surface value equivalent_control: float # Equivalent control component switching_control: float # Switching control component controller_state: dict # Internal controller state
```

---

## Error Handling & Recovery ### Multi-Level Error Handling The factory implements error handling at multiple levels: #### 1. Input Validation ```python
# example-metadata:
# runnable: false def validate_inputs(controller_type, config, gains): """Validate factory inputs before processing.""" # Controller type validation if not isinstance(controller_type, str): raise TypeError("controller_type must be string") # Gains validation if gains is not None: if not isinstance(gains, (list, np.ndarray)): raise TypeError("gains must be list or numpy array") if not all(isinstance(g, (int, float)) for g in gains): raise ValueError("gains must contain numeric values") if any(not np.isfinite(g) for g in gains): raise ValueError("gains contain NaN or infinite values")
``` #### 2. Configuration Validation ```python

def validate_configuration(config_obj): """Validate configuration object after creation.""" try: # Use config class validation config_obj._validate_gains() config_obj._validate_parameters() except ValidationError as e: logger.warning(f"Configuration validation failed: {e}") raise ConfigurationError(f"Invalid configuration: {e}")
``` #### 3. Graceful Fallback Mechanisms ```python
# example-metadata:
# runnable: false def create_fallback_configuration(controller_type, gains): """Create minimal working configuration when full config fails.""" fallback_params = { 'gains': gains, 'max_force': 150.0, # Safe default 'dt': 0.001, # Standard timestep } # Add controller-specific required parameters if controller_type == 'classical_smc': fallback_params['boundary_layer'] = 0.02 elif controller_type == 'sta_smc': fallback_params['K1'] = 4.0 fallback_params['K2'] = 0.4 return controller_info['config_class'](**fallback_params)
``` #### 4. Controller Instantiation Error Recovery ```python
# example-metadata:

# runnable: false def safe_controller_creation(controller_class, config): """Create controller with error recovery.""" try: return controller_class(config) except Exception as e: logger.error(f"Controller instantiation failed: {e}") # Try with minimal configuration minimal_config = create_minimal_config(config) try: return controller_class(minimal_config) except Exception as e2: logger.error(f"Minimal controller creation failed: {e2}") raise FactoryError(f"Cannot create controller: {e}, {e2}")

``` ### Error Classification The factory defines specific error types for better error handling: ```python
# example-metadata:
# runnable: false class FactoryError(Exception): """Base factory error.""" pass class ConfigurationError(FactoryError): """Configuration validation error.""" pass class ControllerTypeError(FactoryError): """Unknown controller type error.""" pass class GainValidationError(FactoryError): """Gain validation error.""" pass
```

---

## PSO Integration Workflows ### PSO-Compatible Interface The factory provides specialized PSO integration through wrapper classes: #### PSOControllerWrapper ```python

# example-metadata:

# runnable: false class PSOControllerWrapper: """Wrapper for SMC controllers to provide PSO-compatible interface.""" def __init__(self, controller, n_gains: int, controller_type: str): self.controller = controller self.n_gains = n_gains self.controller_type = controller_type self.max_force = getattr(controller, 'max_force', 150.0) def compute_control(self, state: np.ndarray) -> np.ndarray: """PSO-compatible control computation interface.""" result = self.controller.compute_control(state, (), {}) # Extract and normalize control value if hasattr(result, 'u'): u = result.u elif isinstance(result, dict) and 'u' in result: u = result['u'] else: u = result return np.array([u]) if isinstance(u, (int, float)) else u

``` ### PSO Factory Function ```python
# example-metadata:
# runnable: false def create_pso_controller_factory( smc_type: SMCType, plant_config: Optional[Any] = None, max_force: float = 150.0, dt: float = 0.001, **kwargs
) -> Callable: """Create a PSO-optimized controller factory function.""" def controller_factory(gains: Union[list, np.ndarray]) -> Any: """Controller factory function optimized for PSO.""" return create_smc_for_pso(smc_type, gains, plant_config, max_force, dt, **kwargs) # Add PSO-required attributes controller_factory.n_gains = get_expected_gain_count(smc_type) controller_factory.controller_type = smc_type.value return controller_factory
``` ### Gain Bounds Specification ```python
# example-metadata:

# runnable: false def get_gain_bounds_for_pso(smc_type: SMCType) -> Tuple[List[float], List[float]]: """Get PSO gain bounds based on control theory constraints.""" bounds_map = { SMCType.CLASSICAL: { 'lower': [0.1, 0.1, 0.1, 0.1, 1.0, 0.0], # [c1, λ1, c2, λ2, K, kd] 'upper': [50.0, 50.0, 50.0, 50.0, 200.0, 50.0] }, SMCType.SUPER_TWISTING: { 'lower': [1.0, 1.0, 0.1, 0.1, 0.1, 0.1], # [K1, K2, c1, λ1, c2, λ2] 'upper': [100.0, 100.0, 50.0, 50.0, 50.0, 50.0] } } return bounds_map.get(smc_type, default_bounds)

``` ### PSO Optimization Workflow ```mermaid
graph TD A[PSO Request] --> B[Create Factory Function] B --> C[Define Gain Bounds] C --> D[Initialize PSO Algorithm] D --> E[For Each Particle] E --> F[Create Controller via Factory] F --> G[Evaluate Performance] G --> H[Update Particle Position] H --> I{Convergence?} I -->|No| E I -->|Yes| J[Return Optimal Gains]
```

---

## Performance Requirements ### Real-Time Performance Specifications #### Instantiation Performance - **Target**: Controller creation < 10ms

- **Maximum**: Controller creation < 50ms for complex configurations
- **Memory**: Peak instantiation memory < 50MB #### Control Computation Performance - **Target**: Control computation < 1ms per call
- **Maximum**: Control computation < 5ms per call
- **Throughput**: Support > 1000 Hz control loops ### Memory Efficiency Requirements #### Controller Memory Footprint - **Classical SMC**: < 1MB per instance
- **Super-Twisting SMC**: < 2MB per instance
- **Adaptive SMC**: < 5MB per instance (includes adaptation history)
- **Hybrid SMC**: < 3MB per instance #### Factory Memory Management ```python
# example-metadata:

# runnable: false class ControllerPool: """Memory-efficient controller instance pool.""" def __init__(self, max_instances: int = 100): self._pool = {} self._usage_count = {} self._max_instances = max_instances def get_controller(self, controller_type: str, config_hash: str): """Get controller from pool or create new one.""" key = f"{controller_type}_{config_hash}" if key in self._pool: self._usage_count[key] += 1 return self._pool[key] if len(self._pool) >= self._max_instances: self._evict_least_used() controller = create_controller(controller_type, config) self._pool[key] = controller self._usage_count[key] = 1 return controller

``` ### Validation Procedures #### Performance Benchmarking ```python
# example-metadata:
# runnable: false def benchmark_factory_performance(): """Benchmark factory instantiation performance.""" controller_types = ['classical_smc', 'sta_smc', 'adaptive_smc'] results = {} for controller_type in controller_types: times = [] for _ in range(100): start = time.perf_counter() controller = create_controller(controller_type) end = time.perf_counter() times.append(end - start) results[controller_type] = { 'mean': np.mean(times), 'std': np.std(times), 'max': np.max(times), 'p95': np.percentile(times, 95) } return results
``` #### Memory Usage Validation ```python

def validate_memory_usage(): """Validate factory memory usage patterns.""" import psutil import gc # Baseline memory gc.collect() baseline = psutil.Process().memory_info().rss # Create multiple controllers controllers = [] for i in range(100): controller = create_controller('classical_smc') controllers.append(controller) if i % 10 == 0: current = psutil.Process().memory_info().rss memory_per_controller = (current - baseline) / (i + 1) assert memory_per_controller < 1_000_000 # < 1MB per controller
```

---

## Mathematical Foundations ### Stability Analysis for Factory-Created Controllers The factory ensures that all created controllers satisfy fundamental stability requirements: #### Classical SMC Stability Conditions For classical SMC controllers created by the factory, the following stability conditions are verified: **Sliding Surface Design:**
```latex

s = c₁e₁ + λ₁ė₁ + c₂e₂ + λ₂ė₂
``` where:
- e₁, e₂: position errors for pendulum 1 and 2
- ė₁, ė₂: velocity errors for pendulum 1 and 2
- c₁, c₂, λ₁, λ₂: surface gains (must be positive) **Reaching Condition:**
```latex

s·ṡ ≤ -η|s|, η > 0
``` The factory validates that switching gain K satisfies:
```latex

K ≥ η + ||F|| + ||ΔF||
``` where F represents system uncertainties and ΔF represents unmodeled dynamics. #### Super-Twisting SMC Finite-Time Stability For super-twisting controllers, the factory ensures finite-time convergence conditions: **Control Law:**
```latex

u = -K₁|s|^(1/2)sign(s) - K₂∫sign(s)dt
``` **Stability Conditions:**
```latex

K₁ > K₂ > 0
K₁² > 2α
``` where α is the Lipschitz constant of the uncertainty. #### Lyapunov Function Validation The factory can optionally validate Lyapunov stability for created controllers: ```python
# example-metadata:
# runnable: false def validate_lyapunov_stability(controller, test_states): """Validate Lyapunov stability for controller.""" for state in test_states: # Compute Lyapunov function V = compute_lyapunov_function(state, controller.config) # Compute time derivative dV_dt = compute_lyapunov_derivative(state, controller) # Verify stability condition if dV_dt > 0: logger.warning(f"Lyapunov condition violated at state {state}") return False return True
``` ### Gain Sensitivity Analysis The factory provides mathematical tools for analyzing gain sensitivity: #### Sensitivity Matrix Computation ```python
# example-metadata:

# runnable: false def compute_gain_sensitivity_matrix(controller_type, nominal_gains, test_states): """Compute sensitivity of control performance to gain variations.""" n_gains = len(nominal_gains) n_states = len(test_states) sensitivity_matrix = np.zeros((n_states, n_gains)) delta = 0.01 # 1% perturbation for i, state in enumerate(test_states): for j, gain in enumerate(nominal_gains): # Perturb gain perturbed_gains = nominal_gains.copy() perturbed_gains[j] *= (1 + delta) # Create controllers nominal_controller = create_controller(controller_type, gains=nominal_gains) perturbed_controller = create_controller(controller_type, gains=perturbed_gains) # Compute control actions u_nominal = nominal_controller.compute_control(state, (), {}).u u_perturbed = perturbed_controller.compute_control(state, (), {}).u # Compute sensitivity sensitivity_matrix[i, j] = (u_perturbed - u_nominal) / (delta * gain) return sensitivity_matrix

``` #### Robustness Analysis ```python
# example-metadata:
# runnable: false def analyze_controller_robustness(controller_type, gains, uncertainty_bounds): """Analyze controller robustness to parameter uncertainties.""" # Create nominal controller controller = create_controller(controller_type, gains=gains) # Monte Carlo robustness analysis n_samples = 1000 stability_count = 0 for _ in range(n_samples): # Generate random uncertainties uncertainties = generate_random_uncertainties(uncertainty_bounds) # Test stability with uncertainties if test_stability_with_uncertainties(controller, uncertainties): stability_count += 1 robustness_probability = stability_count / n_samples return robustness_probability
``` ### Performance Comparison Methodologies #### Statistical Performance Metrics ```python
# example-metadata:

# runnable: false def compare_controller_performance(controller_types, test_scenarios): """Statistically compare performance of different controller types.""" results = {} for controller_type in controller_types: controller = create_controller(controller_type) # Collect performance metrics settling_times = [] overshoots = [] steady_state_errors = [] for scenario in test_scenarios: metrics = simulate_control_scenario(controller, scenario) settling_times.append(metrics['settling_time']) overshoots.append(metrics['overshoot']) steady_state_errors.append(metrics['steady_state_error']) results[controller_type] = { 'settling_time': { 'mean': np.mean(settling_times), 'std': np.std(settling_times), 'confidence_interval': compute_confidence_interval(settling_times) }, 'overshoot': { 'mean': np.mean(overshoots), 'std': np.std(overshoots), 'confidence_interval': compute_confidence_interval(overshoots) }, 'steady_state_error': { 'mean': np.mean(steady_state_errors), 'std': np.std(steady_state_errors), 'confidence_interval': compute_confidence_interval(steady_state_errors) } } return results

``` #### Statistical Significance Testing ```python
def test_performance_significance(results_A, results_B, metric='settling_time'): """Test statistical significance of performance differences.""" from scipy import stats data_A = results_A[metric]['samples'] data_B = results_B[metric]['samples'] # Perform Welch's t-test (unequal variances) t_stat, p_value = stats.ttest_ind(data_A, data_B, equal_var=False) # Compute effect size (Cohen's d) pooled_std = np.sqrt((np.var(data_A) + np.var(data_B)) / 2) cohens_d = (np.mean(data_A) - np.mean(data_B)) / pooled_std return { 't_statistic': t_stat, 'p_value': p_value, 'effect_size': cohens_d, 'significant': p_value < 0.05 }
```

---

## Conclusion The controller factory integration provides a robust, type-safe, and performance-optimized foundation for the DIP-SMC control system. Through error handling, mathematical validation, and PSO integration, the factory ensures reliable controller instantiation while maintaining the theoretical foundations required for stable control performance. The modular design enables easy extension with new controller types while preserving backward compatibility and performance requirements. The integration with the broader system architecture provides a solid foundation for research and practical applications in sliding mode control.