# Factory Usage Examples - Guide ## Advanced Controller Factory Usage Patterns This document provides practical examples for using the enhanced controller factory system after the GitHub Issue #6 resolution.

## Table of Contents 1. [Basic Usage Examples](#basic-usage-examples)

2. [Advanced Configuration Examples](#advanced-configuration-examples)
3. [PSO Integration Examples](#pso-integration-examples)
4. [Error Handling Examples](#error-handling-examples)
5. [Performance Optimization Examples](#performance-optimization-examples)

---

## Basic Usage Examples ### 1. Creating Controllers with Default Settings ```python

from src.controllers.factory import create_controller # Classical SMC with minimal configuration
classical_controller = create_controller( controller_type='classical_smc', gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0]
) # Super-Twisting SMC with optimized gains (Issue #2 resolution)
sta_controller = create_controller( controller_type='sta_smc', gains=[8.0, 4.0, 12.0, 6.0, 4.85, 3.43] # Reduced overshoot configuration
) # Adaptive SMC with standard gains
adaptive_controller = create_controller( controller_type='adaptive_smc', gains=[12.0, 10.0, 6.0, 5.0, 2.5]
) # Hybrid controller with surface gains only
hybrid_controller = create_controller( controller_type='hybrid_adaptive_sta_smc', gains=[8.0, 6.0, 4.0, 3.0]
)
``` ### 2. Using Controller Type Aliases ```python
# Multiple ways to create the same controller
controllers = [ create_controller('classical_smc', gains), create_controller('classic_smc', gains), # Alias create_controller('smc_classical', gains), # Alias create_controller('smc_v1', gains), # Alias
] # All create identical Classical SMC controllers
assert all(type(c) == type(controllers[0]) for c in controllers)
``` ### 3. Configuration from Global Config File ```python

from src.config import load_config
from src.controllers.factory import create_controller # Load global configuration
config = load_config("config.yaml") # Create controller using configuration defaults
controller = create_controller( controller_type='classical_smc', config=config # Gains automatically extracted from config
) # Override specific parameters while using config
controller_custom = create_controller( controller_type='classical_smc', config=config, gains=[10.0, 8.0, 6.0, 4.0, 20.0, 3.0] # Override config gains
)
```

---

## Advanced Configuration Examples ### 1. Type-Safe Configuration Classes ```python
from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig
from src.controllers.factory import create_controller # Create validated configuration
config = ClassicalSMCConfig( gains=[15.0, 12.0, 8.0, 6.0, 25.0, 4.0], max_force=150.0, boundary_layer=0.02, dt=0.001, switch_method="tanh", boundary_layer_slope=1.0, regularization=1e-8
) # Create controller with validated configuration
controller = create_controller('classical_smc', config=config)
``` ### 2. Super-Twisting SMC with Custom Parameters ```python

from src.controllers.smc.algorithms.super_twisting.config import SuperTwistingSMCConfig # Configuration for reduced overshoot (Issue #2 resolution)
sta_config = SuperTwistingSMCConfig( gains=[8.0, 4.0, 12.0, 6.0, 4.85, 3.43], # Optimized surface coefficients max_force=150.0, K1=8.0, # Proportional-like STA gain K2=4.0, # Integral-like STA gain (reduced for damping) power_exponent=0.5, # Standard STA exponent dt=0.001, damping_gain=0.0, regularization=1e-6
) controller = create_controller('sta_smc', config=sta_config) # Verify configuration properties
print(f"K1 gain: {sta_config.K1}")
print(f"Surface gains: {sta_config.get_surface_gains()}")
``` ### 3. Adaptive SMC with Parameter Estimation ```python
from src.controllers.smc.algorithms.adaptive.config import AdaptiveSMCConfig # Configuration for robust adaptation
adaptive_config = AdaptiveSMCConfig( gains=[15.0, 12.0, 8.0, 6.0, 3.0], # [k1, k2, λ1, λ2, γ] max_force=150.0, leak_rate=0.01, # Parameter drift prevention dead_zone=0.05, # Adaptation dead zone adapt_rate_limit=10.0, # Maximum adaptation rate K_min=0.1, # Minimum adaptive gain K_max=100.0, # Maximum adaptive gain gamma=2.0, # Adaptation rate boundary_layer=0.1, # Smooth switching layer smooth_switch=True, # smooth switching dt=0.001
) controller = create_controller('adaptive_smc', config=adaptive_config) # Access adaptation bounds
bounds = adaptive_config.get_adaptation_bounds()
print(f"Adaptation bounds: {bounds}")
``` ### 4. Hybrid Controller with Sub-Configurations ```python

from src.controllers.smc.algorithms.hybrid.config import HybridSMCConfig, HybridMode
from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig
from src.controllers.smc.algorithms.adaptive.config import AdaptiveSMCConfig # Create sub-configurations
classical_sub = ClassicalSMCConfig( gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0], max_force=150.0, dt=0.001, boundary_layer=0.02
) adaptive_sub = AdaptiveSMCConfig( gains=[12.0, 10.0, 6.0, 5.0, 2.5], max_force=150.0, dt=0.001, leak_rate=0.01, dead_zone=0.05
) # Create hybrid configuration
hybrid_config = HybridSMCConfig( hybrid_mode=HybridMode.CLASSICAL_ADAPTIVE, dt=0.001, max_force=150.0, classical_config=classical_sub, adaptive_config=adaptive_sub, k1_init=4.0, k2_init=0.4, gamma1=2.0, gamma2=0.5, dead_zone=0.05
) controller = create_controller('hybrid_adaptive_sta_smc', config=hybrid_config)
```

---

## PSO Integration Examples ### 1. Basic PSO Optimization ```python
from src.optimization.integration.pso_factory_bridge import ( EnhancedPSOFactory, PSOFactoryConfig, ControllerType
) # Configure PSO optimization
pso_config = PSOFactoryConfig( controller_type=ControllerType.CLASSICAL_SMC, population_size=20, max_iterations=50, convergence_threshold=1e-6
) # Create and run PSO optimization
pso_factory = EnhancedPSOFactory(pso_config, "config.yaml")
optimization_result = pso_factory.optimize_controller() if optimization_result['success']: optimized_controller = optimization_result['controller'] best_gains = optimization_result['best_gains'] best_cost = optimization_result['best_cost'] print(f"Optimization successful!") print(f"Best gains: {best_gains}") print(f"Best cost: {best_cost:.6f}")
else: print(f"Optimization failed: {optimization_result['error']}")
``` ### 2. Advanced PSO Configuration ```python
# example-metadata:

# runnable: false # Enhanced PSO configuration with robust evaluation

pso_config = PSOFactoryConfig( controller_type=ControllerType.STA_SMC, population_size=30, # Larger population for better exploration max_iterations=100, # More iterations for convergence convergence_threshold=1e-5, # Stricter convergence criteria max_stagnation_iterations=15, # Early stopping for stagnation enable_adaptive_bounds=True, # Dynamic bound adjustment enable_gradient_guidance=False, # Pure PSO without gradient hints fitness_timeout=15.0, # 15-second timeout per evaluation use_robust_evaluation=True # error recovery
) pso_factory = EnhancedPSOFactory(pso_config)
result = pso_factory.optimize_controller() # Analyze optimization performance
if result['success']: performance = result['performance_analysis'] validation = result['validation_results'] print(f"Converged: {performance['converged']}") print(f"Improvement ratio: {performance['improvement_ratio']:.3f}") print(f"Gains valid: {validation['gains_valid']}") print(f"Controller stable: {validation['controller_stable']}")
``` ### 3. One-Line Optimization Functions ```python
from src.optimization.integration.pso_factory_bridge import ( optimize_classical_smc, optimize_adaptive_smc, optimize_sta_smc
) # Quick optimization for each controller type
classical_factory, classical_result = optimize_classical_smc()
adaptive_factory, adaptive_result = optimize_adaptive_smc()
sta_factory, sta_result = optimize_sta_smc() # Use optimized controllers immediately
classical_controller = classical_factory() # Uses optimized gains
adaptive_controller = adaptive_factory()
sta_controller = sta_factory() # Access optimization results
print(f"Classical optimization cost: {classical_result['best_cost']:.6f}")
print(f"Adaptive optimization cost: {adaptive_result['best_cost']:.6f}")
print(f"STA optimization cost: {sta_result['best_cost']:.6f}")
``` ### 4. Custom PSO Bounds and Validation ```python

from src.controllers.factory import get_gain_bounds_for_pso, SMCType, validate_smc_gains # Get controller-specific bounds
bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)
lower_bounds, upper_bounds = bounds print(f"Classical SMC bounds:")
print(f" Lower: {lower_bounds}")
print(f" Upper: {upper_bounds}") # Validate gains before optimization
test_gains = [15.0, 12.0, 8.0, 6.0, 25.0, 4.0]
is_valid = validate_smc_gains(SMCType.CLASSICAL, test_gains) if is_valid: print("Gains are valid for Classical SMC") # Use gains in optimization or controller creation
else: print("Invalid gains - adjustment needed")
```

## Error Handling Examples

### 1. Robust Controller Creation

```python

from src.controllers.factory import create_controller
import logging # Configure logging to see factory warnings
logging.basicConfig(level=logging.INFO) # Factory automatically handles invalid gains
try: # These gains violate SMC stability requirements (negative gains) invalid_gains = [-1.0, 5.0, 3.0, 2.0, 10.0, 1.0] controller = create_controller( controller_type='classical_smc', gains=invalid_gains ) # Factory will: # 1. Detect invalid gains # 2. Log warning message # 3. Fall back to safe default gains # 4. Return working controller print("Controller created successfully with fallback gains") except Exception as e: print(f"Controller creation failed: {e}")
``` ### 2. Configuration Validation Examples ```python
from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig # Example 1: Invalid surface gains (negative values)
try: config = ClassicalSMCConfig( gains=[0.0, 5.0, 3.0, 2.0, 10.0, 1.0], # k1 = 0 violates stability max_force=150.0, boundary_layer=0.02 )
except ValueError as e: print(f"Configuration validation failed: {e}") # Output: "Surface gains [k1, k2, λ1, λ2] must be positive for stability" # Example 2: Invalid boundary layer (too small)
try: config = ClassicalSMCConfig( gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0], max_force=150.0, boundary_layer=1e-15 # Too small, causes division by zero )
except ValueError as e: print(f"Configuration validation failed: {e}") # Output: "boundary_layer is too small (minimum: 1e-12) which may cause division by zero" # Example 3: Valid configuration
config = ClassicalSMCConfig( gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0], max_force=150.0, boundary_layer=0.02
)
print("Configuration is valid")
``` ### 3. PSO Error Recovery ```python

from src.optimization.integration.pso_factory_bridge import EnhancedPSOFactory, PSOFactoryConfig, ControllerType # Configure PSO with robust evaluation
pso_config = PSOFactoryConfig( controller_type=ControllerType.CLASSICAL_SMC, use_robust_evaluation=True, # automatic error recovery fitness_timeout=10.0 # Timeout protection
) pso_factory = EnhancedPSOFactory(pso_config) # The enhanced factory automatically handles:
# - Controller creation failures

# - Simulation instabilities

# - Matrix singularities

# - Timeout conditions

# - Invalid parameter combinations result = pso_factory.optimize_controller() # Check optimization statistics

stats = pso_factory.validation_stats
print(f"Total fitness evaluations: {stats['fitness_evaluations']}")
print(f"Failed evaluations: {stats['failed_evaluations']}")
print(f"Parameter violations: {stats['parameter_violations']}") # Calculate success rate
success_rate = 1.0 - (stats['failed_evaluations'] / max(stats['fitness_evaluations'], 1))
print(f"Evaluation success rate: {success_rate:.1%}")
``` ### 4. Import Error Handling ```python
# The factory has robust import fallbacks for dynamics models
from src.controllers.factory import create_controller try: # Factory tries multiple import paths: # 1. src.core.dynamics.DIPDynamics (preferred) # 2. src.core.dynamics.DIPDynamics (alternative) # 3. src.plant.models.simplified.dynamics.SimplifiedDIPDynamics (fallback) controller = create_controller('classical_smc', gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0]) print("Controller created successfully") except ImportError as e: print(f"Import error: {e}") # This only happens if NO dynamics implementation is available
```

---

## Performance Optimization Examples ### 1. Configuration Reuse ```python

from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig
from src.controllers.factory import create_controller # Create configuration once
base_config = ClassicalSMCConfig( gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0], max_force=150.0, boundary_layer=0.02, dt=0.001
) # Reuse configuration for multiple controllers
controllers = []
for i in range(10): controller = create_controller('classical_smc', config=base_config) controllers.append(controller) print(f"Created {len(controllers)} controllers efficiently")
``` ### 2. Batch Controller Creation ```python
from src.controllers.factory import create_controller, get_default_gains # Efficient batch creation with different gain sets
controller_specs = [ ('classical_smc', [8.0, 6.0, 4.0, 3.0, 15.0, 2.0]), ('sta_smc', [8.0, 4.0, 12.0, 6.0, 4.85, 3.43]), ('adaptive_smc', [12.0, 10.0, 6.0, 5.0, 2.5]), ('hybrid_adaptive_sta_smc', [8.0, 6.0, 4.0, 3.0])
] controllers = {}
for controller_type, gains in controller_specs: controllers[controller_type] = create_controller(controller_type, gains=gains) print(f"Created {len(controllers)} different controller types")
``` ### 3. Lazy Loading Example ```python

from src.controllers.factory import create_controller # Controllers with dynamics models are created only when needed
def create_controller_lazily(controller_type, gains): """Create controller with lazy dynamics loading.""" # Dynamics model is only created when the controller needs it controller = create_controller( controller_type=controller_type, gains=gains # No explicit dynamics model - created automatically when needed ) return controller # Fast creation - dynamics loaded on first use
controller = create_controller_lazily('classical_smc', [8.0, 6.0, 4.0, 3.0, 15.0, 2.0])
``` ### 4. Memory-Efficient PSO ```python
from src.optimization.integration.pso_factory_bridge import EnhancedPSOFactory, PSOFactoryConfig, ControllerType # Configure PSO for memory efficiency
pso_config = PSOFactoryConfig( controller_type=ControllerType.CLASSICAL_SMC, population_size=15, # Smaller population for memory efficiency max_iterations=30, # Fewer iterations for speed convergence_threshold=1e-4, # Slightly relaxed convergence enable_adaptive_bounds=False, # Disable adaptive bounds for simplicity fitness_timeout=5.0 # Shorter timeout for speed
) pso_factory = EnhancedPSOFactory(pso_config) # Run efficient optimization
import time
start_time = time.time()
result = pso_factory.optimize_controller()
optimization_time = time.time() - start_time print(f"Optimization completed in {optimization_time:.2f} seconds")
print(f"Memory-efficient result: cost = {result['best_cost']:.6f}")
```

---

## Complete Workflow Examples ### 1. Research Workflow ```python

# example-metadata:

# runnable: false """Complete research workflow for controller comparison."""

from src.controllers.factory import create_controller
from src.optimization.integration.pso_factory_bridge import optimize_classical_smc, optimize_sta_smc # Step 1: Create baseline controllers
baseline_controllers = { 'classical': create_controller('classical_smc', gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0]), 'sta': create_controller('sta_smc', gains=[8.0, 4.0, 12.0, 6.0, 4.85, 3.43])
} # Step 2: Optimize controllers
print("Optimizing controllers...")
classical_factory, classical_result = optimize_classical_smc()
sta_factory, sta_result = optimize_sta_smc() optimized_controllers = { 'classical_opt': classical_factory(), 'sta_opt': sta_factory()
} # Step 3: Compare performance
print("\nPerformance Comparison:")
print(f"Classical baseline vs optimized:")
print(f" Optimized cost: {classical_result['best_cost']:.6f}")
print(f" Optimized gains: {classical_result['best_gains']}") print(f"\nSTA baseline vs optimized:")
print(f" Optimized cost: {sta_result['best_cost']:.6f}")
print(f" Optimized gains: {sta_result['best_gains']}")
``` ### 2. Production Deployment Workflow ```python
"""Production-ready controller deployment workflow."""
from src.controllers.factory import create_controller, list_available_controllers
from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig
from src.config import load_config
import logging # Step 1: Setup production logging
logging.basicConfig( level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) # Step 2: Load and validate configuration
config = load_config("config.yaml") # Step 3: Create production controller with validated configuration
production_config = ClassicalSMCConfig( gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0], # Validated stable gains max_force=150.0, # Hardware limit boundary_layer=0.02, # Tested boundary layer dt=0.001, # Control loop frequency switch_method="tanh", # Smooth switching regularization=1e-8 # Numerical stability
) # Step 4: Create controller with error handling
try: production_controller = create_controller( controller_type='classical_smc', config=production_config ) logging.info("Production controller created successfully") # Step 5: Validate controller operation test_state = [0.0, 0.1, 0.05, 0.0, 0.0, 0.0] control_output = production_controller.compute_control(test_state, (), {}) if hasattr(control_output, 'u'): control_value = control_output.u else: control_value = control_output logging.info(f"Controller validation successful: u = {control_value}") except Exception as e: logging.error(f"Production controller creation failed: {e}") raise print("Production deployment successful")
``` This guide demonstrates the full features of the enhanced factory system, providing practical examples for all major use cases from basic controller creation to advanced PSO optimization workflows.
