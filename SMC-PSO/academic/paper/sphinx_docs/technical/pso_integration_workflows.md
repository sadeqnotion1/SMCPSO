# PSO Integration Workflows - Factory Integration ## PSO-Factory Integration Documentation **Document Version:** 2.0

**Last Updated:** November 2024
**Related Issue:** GitHub Issue #6 - Factory Integration Fixes

---

## Table of Contents 1. [PSO Integration Overview](#pso-integration-overview)

2. [Enhanced PSO Factory Architecture](#enhanced-pso-factory-architecture)
3. [Basic PSO Workflows](#basic-pso-workflows)
4. [Advanced PSO Configuration](#advanced-pso-configuration)
5. [Multi-Scenario Fitness Evaluation](#multi-scenario-fitness-evaluation)
6. [Optimization Diagnostics and Monitoring](#optimization-diagnostics-and-monitoring)
7. [Performance Analysis Tools](#performance-analysis-tools)
8. [Production PSO Workflows](#production-pso-workflows)
9. [Integration Examples](#integration-examples)
10. [Best Practices and Guidelines](#best-practices-and-guidelines)

---

## PSO Integration Overview The enhanced factory system provides integration between Particle Swarm Optimization (PSO) and the controller factory pattern. This integration addresses fitness evaluation issues, parameter validation, and convergence diagnostics identified in GitHub Issue #6. ### Key Integration Features - **✅ Robust Fitness Evaluation**: Multi-scenario controller testing with automatic error recovery

- **✅ Parameter Validation**: Real-time gain validation based on SMC theory constraints
- **✅ Convergence Monitoring**: Advanced convergence detection and stagnation analysis
- **✅ Performance Analytics**: optimization result analysis
- **✅ Error Recovery**: Graceful handling of simulation failures and controller instabilities ### Architecture Components ```
PSO Integration Architecture
├── Enhanced PSO Factory (pso_factory_bridge.py)
│ ├── Configuration Management
│ ├── Controller Factory Integration
│ ├── Multi-Scenario Fitness Evaluation
│ └── Performance Analytics
├── Controller Factory Integration
│ ├── Type-Safe Controller Creation
│ ├── Parameter Validation
│ └── Error Recovery Systems
└── Optimization Diagnostics ├── Convergence Analysis ├── Performance Metrics └── Validation Reports
```

---

## Enhanced PSO Factory Architecture ### Core Components #### 1. Enhanced PSO Factory (`EnhancedPSOFactory`) The central component providing advanced PSO-factory integration: ```python
from src.optimization.integration.pso_factory_bridge import ( EnhancedPSOFactory, PSOFactoryConfig, ControllerType
) class EnhancedPSOFactory: """Enhanced PSO-Factory integration with advanced optimization capabilities.""" def __init__(self, config: PSOFactoryConfig, global_config_path: str = "config.yaml") def create_enhanced_controller_factory(self) -> Callable def create_enhanced_fitness_function(self, controller_factory: Callable) -> Callable def optimize_controller(self) -> Dict[str, Any] def get_optimization_diagnostics(self) -> Dict[str, Any]
``` #### 2. PSO Factory Configuration (`PSOFactoryConfig`) Type-safe configuration for PSO optimization parameters: ```python
# example-metadata:

# runnable: false @dataclass

class PSOFactoryConfig: """Configuration for PSO-Factory integration.""" controller_type: ControllerType # Controller to optimize population_size: int = 20 # PSO swarm size max_iterations: int = 50 # Maximum iterations convergence_threshold: float = 1e-6 # Convergence criteria max_stagnation_iterations: int = 10 # Early stopping enable_adaptive_bounds: bool = True # Dynamic bounds enable_gradient_guidance: bool = False # Gradient hints fitness_timeout: float = 10.0 # Evaluation timeout [s] use_robust_evaluation: bool = True # Error recovery
``` #### 3. Controller Type Enumeration ```python
class ControllerType(Enum): """Controller types for PSO optimization.""" CLASSICAL_SMC = "classical_smc" ADAPTIVE_SMC = "adaptive_smc" STA_SMC = "sta_smc" HYBRID_SMC = "hybrid_adaptive_sta_smc"
```

---

## Basic PSO Workflows ### 1. Simple Controller Optimization #### Classical SMC Optimization ```python

from src.optimization.integration.pso_factory_bridge import ( EnhancedPSOFactory, PSOFactoryConfig, ControllerType
) # Configure PSO optimization
pso_config = PSOFactoryConfig( controller_type=ControllerType.CLASSICAL_SMC, population_size=20, max_iterations=50
) # Create PSO factory and optimize
pso_factory = EnhancedPSOFactory(pso_config, "config.yaml")
optimization_result = pso_factory.optimize_controller() # Extract results
if optimization_result['success']: optimized_controller = optimization_result['controller'] best_gains = optimization_result['best_gains'] best_cost = optimization_result['best_cost'] print(f"Optimization successful!") print(f"Best gains: {best_gains}") print(f"Best cost: {best_cost:.6f}") # Use optimized controller immediately test_state = [0.0, 0.1, 0.05, 0.0, 0.0, 0.0] control_output = optimized_controller.compute_control(test_state) print(f"Test control output: {control_output}")
else: print(f"Optimization failed: {optimization_result['error']}")
``` #### Super-Twisting SMC Optimization ```python
# example-metadata:
# runnable: false # Optimize STA-SMC with Issue #2 considerations
pso_config = PSOFactoryConfig( controller_type=ControllerType.STA_SMC, population_size=25, # Larger population for better exploration max_iterations=75 # More iterations for convergence
) pso_factory = EnhancedPSOFactory(pso_config)
result = pso_factory.optimize_controller() if result['success']: # Verify reduced overshoot (Issue #2 resolution) performance = result['performance_analysis'] print(f"Converged: {performance['converged']}") print(f"Improvement ratio: {performance['improvement_ratio']:.3f}") # Check optimized surface coefficients gains = result['best_gains'] lambda1, lambda2 = gains[4], gains[5] # λ₁, λ₂ coefficients print(f"Optimized surface coefficients: λ₁={lambda1:.3f}, λ₂={lambda2:.3f}")
``` ### 2. One-Line Optimization Functions For quick optimization, use the convenience functions: ```python
# example-metadata:

# runnable: false from src.optimization.integration.pso_factory_bridge import ( optimize_classical_smc, optimize_adaptive_smc, optimize_sta_smc

) # Quick optimization for each controller type
print("Optimizing controllers...") classical_factory, classical_result = optimize_classical_smc()
adaptive_factory, adaptive_result = optimize_adaptive_smc()
sta_factory, sta_result = optimize_sta_smc() # Compare optimization results
results = { 'Classical SMC': classical_result['best_cost'], 'Adaptive SMC': adaptive_result['best_cost'], 'STA SMC': sta_result['best_cost']
} print("\nOptimization Results:")
for controller, cost in results.items(): print(f" {controller}: {cost:.6f}") # Use optimized controllers
optimized_controllers = { 'classical': classical_factory(), 'adaptive': adaptive_factory(), 'sta': sta_factory()
}
``` ### 3. Custom PSO Configuration ```python
# example-metadata:
# runnable: false # Advanced PSO configuration example
custom_pso_config = PSOFactoryConfig( controller_type=ControllerType.ADAPTIVE_SMC, population_size=30, # Larger swarm for exploration max_iterations=100, # Extended optimization convergence_threshold=1e-5, # Strict convergence max_stagnation_iterations=15, # Patience for stagnation enable_adaptive_bounds=True, # Dynamic parameter bounds fitness_timeout=15.0, # Longer evaluation timeout use_robust_evaluation=True # Enhanced error handling
) pso_factory = EnhancedPSOFactory(custom_pso_config)
result = pso_factory.optimize_controller() # Detailed result analysis
if result['success']: print("=== Optimization Analysis ===") # Performance metrics perf = result['performance_analysis'] print(f"Converged: {perf['converged']}") print(f"Final cost: {perf['final_cost']:.6f}") print(f"Initial cost: {perf['initial_cost']:.6f}") print(f"Improvement: {perf['improvement_ratio']:.1%}") print(f"Iterations: {perf['iterations_completed']}") # Validation results validation = result['validation_results'] print(f"\nValidation Status:") print(f" Gains valid: {validation['gains_valid']}") print(f" Controller stable: {validation['controller_stable']}") print(f" Performance acceptable: {validation['performance_acceptable']}") if validation['validation_errors']: print(f" Warnings: {validation['validation_errors']}")
```

---

## Advanced PSO Configuration ### 1. Multi-Objective Optimization ```python

# example-metadata:

# runnable: false # Configure PSO for multi-objective optimization

multi_objective_config = PSOFactoryConfig( controller_type=ControllerType.CLASSICAL_SMC, population_size=40, # Larger population for Pareto front max_iterations=150, # Extended search convergence_threshold=1e-6, # High precision enable_adaptive_bounds=True, # Dynamic exploration fitness_timeout=20.0 # Longer evaluations
) pso_factory = EnhancedPSOFactory(multi_objective_config) # The enhanced fitness function automatically considers:
# - State regulation performance

# - Control effort minimization

# - Control smoothness

# - Stability margins

# - Robustness to disturbances result = pso_factory.optimize_controller()

``` ### 2. Constraint-Based Optimization ```python
from src.controllers.factory import get_gain_bounds_for_pso, SMCType # Get controller-specific bounds
smc_type = SMCType.CLASSICAL
bounds = get_gain_bounds_for_pso(smc_type)
lower_bounds, upper_bounds = bounds print(f"Classical SMC optimization bounds:")
print(f" Lower: {lower_bounds}")
print(f" Upper: {upper_bounds}") # Configure PSO with custom bounds
constrained_config = PSOFactoryConfig( controller_type=ControllerType.CLASSICAL_SMC, population_size=25, max_iterations=60, enable_adaptive_bounds=False # Use fixed bounds
) pso_factory = EnhancedPSOFactory(constrained_config) # Factory automatically applies controller-specific bounds:
# Classical SMC: [k1, k2, λ1, λ2, K, kd] bounds
# - Position gains: [1.0, 30.0]
# - Surface coefficients: [1.0, 20.0]
# - Switching gain: [5.0, 50.0]
# - Derivative gain: [0.1, 10.0] result = pso_factory.optimize_controller()
``` ### 3. Adaptive PSO Parameters ```python
# example-metadata:

# runnable: false # PSO with adaptive parameters

adaptive_config = PSOFactoryConfig( controller_type=ControllerType.STA_SMC, population_size=20, max_iterations=80, convergence_threshold=1e-5, max_stagnation_iterations=12, enable_adaptive_bounds=True, # Key feature enable_gradient_guidance=False, # Pure PSO use_robust_evaluation=True
) pso_factory = EnhancedPSOFactory(adaptive_config) # Adaptive bounds automatically:
# - Narrow search ranges during convergence

# - Expand ranges during stagnation

# - Adjust based on swarm diversity result = pso_factory.optimize_controller() # Monitor adaptive behavior

diagnostics = pso_factory.get_optimization_diagnostics()
print(f"Adaptive bounds enabled: {diagnostics['configuration']['enable_adaptive_bounds']}")
```

---

## Multi-Scenario Fitness Evaluation ### 1. Automatic Test Scenarios The enhanced PSO factory evaluates controllers across multiple test scenarios: ```python
# example-metadata:
# runnable: false # Automatic test scenarios (built into enhanced fitness function):
test_scenarios = [ { 'initial_state': [0.0, 0.1, 0.05, 0.0, 0.0, 0.0], # Small disturbance 'sim_time': 2.0, 'weight': 1.0, 'description': 'small_disturbance' }, { 'initial_state': [0.0, 0.5, 0.3, 0.0, 0.0, 0.0], # Large angles 'sim_time': 3.0, 'weight': 1.5, # Higher weight for challenging scenario 'description': 'large_angles' }, { 'initial_state': [0.0, 0.2, 0.1, 0.0, 1.0, 0.5], # High velocity 'sim_time': 2.5, 'weight': 1.2, 'description': 'high_velocity' }
]
``` ### 2. Fitness Function Components The enhanced fitness function computes weighted costs: ```python
# example-metadata:

# runnable: false def _evaluate_controller_performance(self, controller, gains): """Multi-scenario performance evaluation.""" # For each test scenario: for scenario in test_scenarios: # Simulate controller performance cost = self._simulate_scenario(controller, scenario) total_cost += cost * scenario['weight'] # Cost components: # - Position error: 10.0 * ∫|state_error|²dt # - Control effort: 0.1 * ∫|u|²dt # - Control rate: 0.05 * ∫|du/dt|²dt # - Stability penalty: penalties for instability return total_cost / total_weight

``` ### 3. Robustness Evaluation ```python
# example-metadata:
# runnable: false # Configure PSO for robustness optimization
robust_config = PSOFactoryConfig( controller_type=ControllerType.ADAPTIVE_SMC, population_size=35, max_iterations=120, fitness_timeout=25.0, # Longer timeout for robust evaluation use_robust_evaluation=True
) pso_factory = EnhancedPSOFactory(robust_config) # Robust evaluation automatically includes:
# - Multiple initial conditions
# - Different simulation durations
# - Varying disturbance levels
# - Parameter uncertainty scenarios result = pso_factory.optimize_controller() if result['success']: # Analyze robustness metrics validation = result['validation_results'] print(f"Robustness Analysis:") print(f" All scenarios passed: {validation['performance_acceptable']}") print(f" Controller stability: {validation['controller_stable']}")
```

---

## Optimization Diagnostics and Monitoring ### 1. Real-Time Monitoring ```python

# example-metadata:

# runnable: false from src.optimization.integration.pso_factory_bridge import EnhancedPSOFactory # Create PSO factory with monitoring

pso_factory = EnhancedPSOFactory(pso_config) # Start optimization
print("Starting optimization with real-time monitoring...")
result = pso_factory.optimize_controller() # Access monitoring statistics
stats = pso_factory.validation_stats
print(f"\nOptimization Statistics:")
print(f" Total fitness evaluations: {stats['fitness_evaluations']}")
print(f" Failed evaluations: {stats['failed_evaluations']}")
print(f" Parameter violations: {stats['parameter_violations']}")
print(f" Convergence checks: {stats['convergence_checks']}") # Calculate success metrics
success_rate = 1.0 - (stats['failed_evaluations'] / max(stats['fitness_evaluations'], 1))
print(f" Evaluation success rate: {success_rate:.1%}")
``` ### 2. Convergence Analysis ```python
# example-metadata:
# runnable: false def analyze_convergence(optimization_result): """Analyze PSO convergence characteristics.""" if not optimization_result['success']: print("Optimization failed - no convergence analysis available") return # Extract convergence data performance = optimization_result['performance_analysis'] print("=== Convergence Analysis ===") print(f"Converged: {performance['converged']}") print(f"Convergence rate: {performance['convergence_rate']:.2e}") print(f"Improvement ratio: {performance['improvement_ratio']:.1%}") print(f"Cost reduction: {performance['cost_reduction']:.6f}") print(f"Iterations completed: {performance['iterations_completed']}") # Convergence quality assessment if performance['converged']: if performance['convergence_rate'] < 1e-6: quality = "Excellent" elif performance['convergence_rate'] < 1e-4: quality = "Good" elif performance['convergence_rate'] < 1e-2: quality = "Fair" else: quality = "Poor" print(f"Convergence quality: {quality}") else: print("Warning: Optimization did not converge") # Suggest improvements if performance['iterations_completed'] >= 100: print(" Suggestion: Increase convergence threshold") else: print(" Suggestion: Increase max_iterations") # Example usage
result = pso_factory.optimize_controller()
analyze_convergence(result)
``` ### 3. Performance Diagnostics ```python
# example-metadata:

# runnable: false def comprehensive_diagnostics(pso_factory, optimization_result): """Generate optimization diagnostics.""" print("=== PSO Diagnostics ===") # 1. Configuration summary diagnostics = pso_factory.get_optimization_diagnostics() config = diagnostics['configuration'] print(f"\nConfiguration:") print(f" Controller type: {config['controller_type']}") print(f" Population size: {config['population_size']}") print(f" Max iterations: {config['max_iterations']}") print(f" Convergence threshold: {config['convergence_threshold']}") # 2. Controller specifications specs = diagnostics['controller_specs'] print(f"\nController Specifications:") print(f" Expected gains: {specs['n_gains']}") print(f" Bounds: {specs['bounds']}") print(f" Default gains: {specs['default_gains']}") # 3. Validation statistics stats = diagnostics['validation_statistics'] print(f"\nValidation Statistics:") print(f" Fitness evaluations: {stats['fitness_evaluations']}") print(f" Failed evaluations: {stats['failed_evaluations']}") print(f" Parameter violations: {stats['parameter_violations']}") # 4. Optimization outcome if optimization_result['success']: print(f"\nOptimization Outcome:") print(f" Status: SUCCESS") print(f" Best cost: {optimization_result['best_cost']:.6f}") print(f" Best gains: {optimization_result['best_gains']}") # Performance analysis perf = optimization_result['performance_analysis'] print(f" Converged: {perf['converged']}") print(f" Improvement: {perf['improvement_ratio']:.1%}") # Validation results validation = optimization_result['validation_results'] print(f" Gains valid: {validation['gains_valid']}") print(f" Controller stable: {validation['controller_stable']}") else: print(f"\nOptimization Outcome:") print(f" Status: FAILED") print(f" Error: {optimization_result.get('error', 'Unknown')}") # Usage example

pso_factory = EnhancedPSOFactory(pso_config)
result = pso_factory.optimize_controller()
comprehensive_diagnostics(pso_factory, result)
```

---

## Performance Analysis Tools ### 1. Optimization History Analysis ```python
def analyze_optimization_history(optimization_result): """Analyze optimization history and performance trends.""" if not optimization_result['success']: return history = optimization_result.get('convergence_history', {}) cost_history = history.get('cost', []) if len(cost_history) == 0: print("No history available for analysis") return import numpy as np import matplotlib.pyplot as plt costs = np.array(cost_history) iterations = np.arange(len(costs)) # Plot convergence history plt.figure(figsize=(12, 8)) plt.subplot(2, 2, 1) plt.plot(iterations, costs, 'b-', linewidth=2) plt.xlabel('Iteration') plt.ylabel('Best Cost') plt.title('PSO Convergence History') plt.grid(True) # Plot improvement rate plt.subplot(2, 2, 2) if len(costs) > 1: improvement = np.diff(costs) plt.plot(iterations[1:], improvement, 'r-', linewidth=1) plt.xlabel('Iteration') plt.ylabel('Cost Improvement') plt.title('Cost Improvement Rate') plt.grid(True) # Plot convergence rate plt.subplot(2, 2, 3) window_size = min(10, len(costs) // 4) if window_size > 1: convergence_rate = np.array([ np.std(costs[max(0, i-window_size):i+1]) / max(np.mean(costs[max(0, i-window_size):i+1]), 1e-6) for i in range(window_size, len(costs)) ]) plt.plot(iterations[window_size:], convergence_rate, 'g-', linewidth=2) plt.xlabel('Iteration') plt.ylabel('Convergence Rate') plt.title('Convergence Rate (std/mean)') plt.yscale('log') plt.grid(True) # Summary statistics plt.subplot(2, 2, 4) final_cost = costs[-1] initial_cost = costs[0] improvement_ratio = (initial_cost - final_cost) / max(initial_cost, 1e-6) stats_text = f""" Initial Cost: {initial_cost:.6f} Final Cost: {final_cost:.6f} Improvement: {improvement_ratio:.1%} Iterations: {len(costs)} """ plt.text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center') plt.axis('off') plt.title('Optimization Summary') plt.tight_layout() plt.savefig('pso_convergence_analysis.png', dpi=300, bbox_inches='tight') plt.show() return { 'initial_cost': float(initial_cost), 'final_cost': float(final_cost), 'improvement_ratio': float(improvement_ratio), 'iterations': len(costs) } # Usage example
result = pso_factory.optimize_controller()
history_analysis = analyze_optimization_history(result)
``` ### 2. Controller Performance Comparison ```python
# example-metadata:

# runnable: false def compare_controller_performance(): """Compare optimized controllers across different types.""" # Optimize all controller types controller_types = [ ControllerType.CLASSICAL_SMC, ControllerType.STA_SMC, ControllerType.ADAPTIVE_SMC ] results = {} for controller_type in controller_types: print(f"Optimizing {controller_type.value}...") pso_config = PSOFactoryConfig( controller_type=controller_type, population_size=20, max_iterations=50 ) pso_factory = EnhancedPSOFactory(pso_config) result = pso_factory.optimize_controller() results[controller_type.value] = result # Performance comparison print("\n=== Controller Performance Comparison ===") print(f"{'Controller':<20} {'Best Cost':<12} {'Converged':<10} {'Improvement':<12}") print("-" * 60) for controller_name, result in results.items(): if result['success']: best_cost = result['best_cost'] converged = result['performance_analysis']['converged'] improvement = result['performance_analysis']['improvement_ratio'] print(f"{controller_name:<20} {best_cost:<12.6f} {str(converged):<10} {improvement:<12.1%}") else: print(f"{controller_name:<20} {'FAILED':<12} {'-':<10} {'-':<12}") return results # Run comparison

comparison_results = compare_controller_performance()
```

---

## Production PSO Workflows ### 1. Production-Ready Optimization Pipeline ```python
def production_optimization_pipeline(controller_type: str, config_path: str = "config.yaml", output_path: str = "optimized_gains.json"): """Production-ready PSO optimization pipeline.""" import json import logging from datetime import datetime # Setup logging logging.basicConfig( level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' ) logger = logging.getLogger(__name__) # Map string to enum controller_type_map = { 'classical_smc': ControllerType.CLASSICAL_SMC, 'sta_smc': ControllerType.STA_SMC, 'adaptive_smc': ControllerType.ADAPTIVE_SMC, 'hybrid_adaptive_sta_smc': ControllerType.HYBRID_SMC } if controller_type not in controller_type_map: raise ValueError(f"Unknown controller type: {controller_type}") controller_enum = controller_type_map[controller_type] try: # Production PSO configuration pso_config = PSOFactoryConfig( controller_type=controller_enum, population_size=25, # Balanced exploration/exploitation max_iterations=100, # Sufficient for convergence convergence_threshold=1e-6, # High precision max_stagnation_iterations=15, # Prevent premature termination enable_adaptive_bounds=True, # Dynamic optimization fitness_timeout=20.0, # Generous timeout use_robust_evaluation=True # Production reliability ) logger.info(f"Starting production optimization for {controller_type}") logger.info(f"Configuration: {pso_config}") # Create factory and optimize pso_factory = EnhancedPSOFactory(pso_config, config_path) start_time = datetime.now() optimization_result = pso_factory.optimize_controller() end_time = datetime.now() optimization_time = (end_time - start_time).total_seconds() if optimization_result['success']: # Extract optimized parameters best_gains = optimization_result['best_gains'] best_cost = optimization_result['best_cost'] # Validation results validation = optimization_result['validation_results'] performance = optimization_result['performance_analysis'] # Production validation checks production_ready = ( validation['gains_valid'] and validation['controller_stable'] and validation['performance_acceptable'] and performance['converged'] ) # Prepare production data production_data = { 'controller_type': controller_type, 'optimization_timestamp': start_time.isoformat(), 'optimization_duration_seconds': optimization_time, 'optimized_gains': best_gains, 'optimization_cost': best_cost, 'convergence_analysis': performance, 'validation_results': validation, 'production_ready': production_ready, 'optimization_configuration': { 'population_size': pso_config.population_size, 'max_iterations': pso_config.max_iterations, 'convergence_threshold': pso_config.convergence_threshold } } # Save results with open(output_path, 'w') as f: json.dump(production_data, f, indent=2) logger.info(f"Optimization completed successfully") logger.info(f"Best cost: {best_cost:.6f}") logger.info(f"Optimized gains: {best_gains}") logger.info(f"Production ready: {production_ready}") logger.info(f"Results saved to: {output_path}") if not production_ready: logger.warning("Controller may not be production ready - review validation results") return optimization_result else: error_msg = optimization_result.get('error', 'Unknown error') logger.error(f"Optimization failed: {error_msg}") # Save failure information failure_data = { 'controller_type': controller_type, 'optimization_timestamp': start_time.isoformat(), 'optimization_duration_seconds': optimization_time, 'status': 'FAILED', 'error': error_msg, 'optimization_stats': optimization_result.get('optimization_stats', {}) } failure_path = output_path.replace('.json', '_failure.json') with open(failure_path, 'w') as f: json.dump(failure_data, f, indent=2) logger.info(f"Failure data saved to: {failure_path}") return None except Exception as e: logger.error(f"Production optimization pipeline failed: {e}") raise # Usage examples
classical_result = production_optimization_pipeline('classical_smc', output_path='classical_gains.json')
sta_result = production_optimization_pipeline('sta_smc', output_path='sta_gains.json')
adaptive_result = production_optimization_pipeline('adaptive_smc', output_path='adaptive_gains.json')
``` ### 2. Batch Optimization Workflow ```python
# example-metadata:

# runnable: false def batch_optimization_workflow(controller_types: List[str], optimization_configs: Dict[str, Dict] = None): """Batch optimization workflow for multiple controllers.""" import concurrent.futures import os from datetime import datetime if optimization_configs is None: optimization_configs = {} def optimize_single_controller(controller_type): """Optimize a single controller type.""" try: # Get custom config or use defaults custom_config = optimization_configs.get(controller_type, {}) # Default configuration default_config = { 'population_size': 25, 'max_iterations': 75, 'convergence_threshold': 1e-6, 'enable_adaptive_bounds': True, 'use_robust_evaluation': True } # Merge configurations config_params = {**default_config, **custom_config} controller_enum = { 'classical_smc': ControllerType.CLASSICAL_SMC, 'sta_smc': ControllerType.STA_SMC, 'adaptive_smc': ControllerType.ADAPTIVE_SMC, 'hybrid_adaptive_sta_smc': ControllerType.HYBRID_SMC }[controller_type] pso_config = PSOFactoryConfig( controller_type=controller_enum, **config_params ) pso_factory = EnhancedPSOFactory(pso_config) result = pso_factory.optimize_controller() return controller_type, result except Exception as e: return controller_type, {'success': False, 'error': str(e)} # Parallel optimization print(f"Starting batch optimization for {len(controller_types)} controllers...") results = {} with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor: # Submit optimization tasks future_to_controller = { executor.submit(optimize_single_controller, ct): ct for ct in controller_types } # Collect results for future in concurrent.futures.as_completed(future_to_controller): controller_type = future_to_controller[future] try: controller_name, optimization_result = future.result() results[controller_name] = optimization_result if optimization_result['success']: cost = optimization_result['best_cost'] print(f"✅ {controller_name}: {cost:.6f}") else: error = optimization_result.get('error', 'Unknown') print(f"❌ {controller_name}: {error}") except Exception as e: print(f"❌ {controller_type}: Exception - {e}") results[controller_type] = {'success': False, 'error': str(e)} # Save batch results timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") batch_results_path = f"batch_optimization_{timestamp}.json" with open(batch_results_path, 'w') as f: json.dump(results, f, indent=2, default=str) print(f"\nBatch optimization completed. Results saved to: {batch_results_path}") # Summary report successful = sum(1 for r in results.values() if r['success']) total = len(results) print(f"\nBatch Summary:") print(f" Total controllers: {total}") print(f" Successful optimizations: {successful}") print(f" Failed optimizations: {total - successful}") print(f" Success rate: {successful/total:.1%}") return results # Usage example

controllers_to_optimize = ['classical_smc', 'sta_smc', 'adaptive_smc'] # Custom configurations for specific controllers
custom_configs = { 'sta_smc': { 'population_size': 30, # Larger population for STA-SMC 'max_iterations': 100, # More iterations for Issue #2 resolution 'convergence_threshold': 1e-5 }, 'adaptive_smc': { 'population_size': 35, # Complex parameter space 'max_iterations': 120 }
} batch_results = batch_optimization_workflow(controllers_to_optimize, custom_configs)
```

---

## Integration Examples ### 1. Complete Research Workflow ```python
# example-metadata:
# runnable: false def complete_research_workflow(): """Complete research workflow demonstrating PSO-factory integration.""" print("=== Complete Research Workflow ===") # Step 1: Baseline controllers print("\n1. Creating baseline controllers...") from src.controllers.factory import create_controller baseline_controllers = { 'classical': create_controller('classical_smc', gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0]), 'sta': create_controller('sta_smc', gains=[8.0, 4.0, 12.0, 6.0, 4.85, 3.43]), 'adaptive': create_controller('adaptive_smc', gains=[12.0, 10.0, 6.0, 5.0, 2.5]) } print(f"Created {len(baseline_controllers)} baseline controllers") # Step 2: PSO optimization print("\n2. Running PSO optimization...") optimization_results = {} for controller_name in ['classical_smc', 'sta_smc', 'adaptive_smc']: controller_enum = { 'classical_smc': ControllerType.CLASSICAL_SMC, 'sta_smc': ControllerType.STA_SMC, 'adaptive_smc': ControllerType.ADAPTIVE_SMC }[controller_name] pso_config = PSOFactoryConfig( controller_type=controller_enum, population_size=20, max_iterations=60, use_robust_evaluation=True ) pso_factory = EnhancedPSOFactory(pso_config) result = pso_factory.optimize_controller() optimization_results[controller_name] = result if result['success']: cost = result['best_cost'] converged = result['performance_analysis']['converged'] print(f" {controller_name}: cost={cost:.6f}, converged={converged}") else: print(f" {controller_name}: FAILED - {result.get('error', 'Unknown')}") # Step 3: Performance comparison print("\n3. Performance comparison...") comparison_data = [] for controller_name, result in optimization_results.items(): if result['success']: comparison_data.append({ 'controller': controller_name, 'cost': result['best_cost'], 'gains': result['best_gains'], 'converged': result['performance_analysis']['converged'], 'improvement': result['performance_analysis']['improvement_ratio'] }) # Sort by cost (lower is better) comparison_data.sort(key=lambda x: x['cost']) print(f"{'Rank':<4} {'Controller':<15} {'Cost':<12} {'Converged':<10} {'Improvement':<12}") print("-" * 55) for i, data in enumerate(comparison_data, 1): print(f"{i:<4} {data['controller']:<15} {data['cost']:<12.6f} " f"{str(data['converged']):<10} {data['improvement']:<12.1%}") # Step 4: Best controller analysis if comparison_data: best_controller = comparison_data[0] print(f"\n4. Best controller analysis:") print(f" Controller: {best_controller['controller']}") print(f" Cost: {best_controller['cost']:.6f}") print(f" Gains: {best_controller['gains']}") print(f" Converged: {best_controller['converged']}") print(f" Improvement: {best_controller['improvement']:.1%}") # Create optimized controller best_name = best_controller['controller'] best_gains = best_controller['gains'] optimized_controller = create_controller(best_name, gains=best_gains) print(f" Optimized controller ready for deployment") return { 'baseline_controllers': baseline_controllers, 'optimization_results': optimization_results, 'best_controller': optimized_controller, 'comparison_data': comparison_data } else: print("No successful optimizations") return None # Run complete workflow
workflow_results = complete_research_workflow()
``` ### 2. Real-Time Optimization Integration ```python
# example-metadata:

# runnable: false def real_time_optimization_integration(): """Demonstrate real-time optimization with live feedback.""" import time import threading from queue import Queue class OptimizationMonitor: """Real-time optimization monitoring.""" def __init__(self): self.progress_queue = Queue() self.current_iteration = 0 self.current_best_cost = float('inf') self.is_running = False def update_progress(self, iteration, best_cost): """Update optimization progress.""" self.current_iteration = iteration self.current_best_cost = best_cost self.progress_queue.put((iteration, best_cost)) def start_monitoring(self): """Start monitoring thread.""" self.is_running = True monitor_thread = threading.Thread(target=self._monitor_loop) monitor_thread.daemon = True monitor_thread.start() def stop_monitoring(self): """Stop monitoring.""" self.is_running = False def _monitor_loop(self): """Monitoring loop.""" while self.is_running: try: if not self.progress_queue.empty(): iteration, cost = self.progress_queue.get(timeout=0.1) print(f"\rIteration {iteration}: Best cost = {cost:.6f}", end='', flush=True) time.sleep(0.1) except: continue # Create monitor monitor = OptimizationMonitor() # Configure PSO with monitoring integration pso_config = PSOFactoryConfig( controller_type=ControllerType.CLASSICAL_SMC, population_size=20, max_iterations=50, use_robust_evaluation=True ) print("Starting real-time PSO optimization...") # Start monitoring monitor.start_monitoring() try: # Create factory and optimize pso_factory = EnhancedPSOFactory(pso_config) # Note: In a real implementation, you would integrate the monitor # with the PSO algorithm's iteration callback result = pso_factory.optimize_controller() print("\n") # New line after progress updates if result['success']: print(f"Optimization completed successfully!") print(f"Final cost: {result['best_cost']:.6f}") print(f"Optimized gains: {result['best_gains']}") # Real-time validation optimized_controller = result['controller'] print("\nPerforming real-time validation...") test_states = [ [0.0, 0.1, 0.05, 0.0, 0.0, 0.0], [0.0, 0.2, 0.1, 0.0, 0.0, 0.0], [0.0, 0.3, 0.15, 0.0, 0.0, 0.0] ] for i, state in enumerate(test_states): control_output = optimized_controller.compute_control(state) if hasattr(control_output, 'u'): u = control_output.u else: u = control_output print(f" Test {i+1}: state={state[:3]}, control={u:.3f}") print("Real-time validation completed") else: print(f"Optimization failed: {result.get('error', 'Unknown')}") finally: monitor.stop_monitoring() return result # Run real-time optimization

real_time_result = real_time_optimization_integration()
```

---

## Best Practices and Guidelines ### 1. PSO Configuration Guidelines #### Population Size Selection
```python
# example-metadata:

# runnable: false # Guidelines for population size selection:

population_guidelines = { 'small_problems': { 'gains_count': '≤ 4', 'recommended_size': '15-20', 'reasoning': 'Sufficient diversity for low-dimensional search' }, 'medium_problems': { 'gains_count': '5-6', 'recommended_size': '20-30', 'reasoning': 'Balanced exploration/exploitation' }, 'large_problems': { 'gains_count': '> 6', 'recommended_size': '30-50', 'reasoning': 'Increased diversity for complex landscapes' }
} def get_recommended_population_size(controller_type: ControllerType) -> int: """Get recommended population size for controller type.""" gain_counts = { ControllerType.CLASSICAL_SMC: 6, ControllerType.STA_SMC: 6, ControllerType.ADAPTIVE_SMC: 5, ControllerType.HYBRID_SMC: 4 } n_gains = gain_counts.get(controller_type, 6) if n_gains <= 4: return 20 elif n_gains <= 6: return 25 else: return 35
``` #### Convergence Criteria ```python
# example-metadata:
# runnable: false def configure_convergence_criteria(controller_type: ControllerType, optimization_goal: str) -> PSOFactoryConfig: """Configure convergence criteria based on optimization goals.""" criteria_map = { 'fast_prototyping': { 'max_iterations': 30, 'convergence_threshold': 1e-4, 'max_stagnation_iterations': 8 }, 'research_quality': { 'max_iterations': 75, 'convergence_threshold': 1e-5, 'max_stagnation_iterations': 12 }, 'production_grade': { 'max_iterations': 100, 'convergence_threshold': 1e-6, 'max_stagnation_iterations': 15 } } criteria = criteria_map.get(optimization_goal, criteria_map['research_quality']) population_size = get_recommended_population_size(controller_type) return PSOFactoryConfig( controller_type=controller_type, population_size=population_size, **criteria, use_robust_evaluation=True, enable_adaptive_bounds=True ) # Usage examples
fast_config = configure_convergence_criteria(ControllerType.CLASSICAL_SMC, 'fast_prototyping')
research_config = configure_convergence_criteria(ControllerType.STA_SMC, 'research_quality')
production_config = configure_convergence_criteria(ControllerType.ADAPTIVE_SMC, 'production_grade')
``` ### 2. Error Handling Best Practices ```python
# example-metadata:

# runnable: false def robust_pso_optimization(controller_type: ControllerType, max_retries: int = 3) -> Dict[str, Any]: """Robust PSO optimization with automatic retry logic.""" for attempt in range(max_retries): try: # Adjust configuration based on attempt population_size = 20 + (attempt * 5) # Increase diversity on retries max_iterations = 50 + (attempt * 25) # More patience on retries pso_config = PSOFactoryConfig( controller_type=controller_type, population_size=population_size, max_iterations=max_iterations, convergence_threshold=1e-5, use_robust_evaluation=True, fitness_timeout=15.0 + (attempt * 5.0) # Longer timeout on retries ) pso_factory = EnhancedPSOFactory(pso_config) result = pso_factory.optimize_controller() if result['success']: # Validate result quality performance = result['performance_analysis'] validation = result['validation_results'] quality_checks = [ performance['converged'], validation['gains_valid'], validation['controller_stable'], result['best_cost'] < 1000.0 # Reasonable cost threshold ] if all(quality_checks): print(f"Optimization successful on attempt {attempt + 1}") return result else: print(f"Attempt {attempt + 1}: Poor quality result, retrying...") continue else: print(f"Attempt {attempt + 1} failed: {result.get('error', 'Unknown')}") continue except Exception as e: print(f"Attempt {attempt + 1} exception: {e}") continue # All attempts failed return { 'success': False, 'error': f'Optimization failed after {max_retries} attempts', 'controller_type': controller_type.value } # Usage

robust_result = robust_pso_optimization(ControllerType.CLASSICAL_SMC, max_retries=3)
``` ### 3. Performance Optimization Guidelines ```python
def performance_optimized_workflow(controller_types: List[ControllerType], parallel_execution: bool = True) -> Dict[str, Any]: """Performance-optimized PSO workflow.""" import concurrent.futures import multiprocessing def optimize_with_caching(controller_type: ControllerType) -> Tuple[ControllerType, Dict]: """Optimize with result caching.""" # Check for cached results cache_key = f"{controller_type.value}_optimized" # Configure for performance pso_config = PSOFactoryConfig( controller_type=controller_type, population_size=20, # Balanced size max_iterations=60, # Reasonable iterations convergence_threshold=1e-5, # Good precision fitness_timeout=10.0, # Efficient timeout use_robust_evaluation=True ) pso_factory = EnhancedPSOFactory(pso_config) result = pso_factory.optimize_controller() return controller_type, result results = {} if parallel_execution and len(controller_types) > 1: # Parallel execution max_workers = min(len(controller_types), multiprocessing.cpu_count()) with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor: future_to_type = { executor.submit(optimize_with_caching, ct): ct for ct in controller_types } for future in concurrent.futures.as_completed(future_to_type): controller_type, result = future.result() results[controller_type.value] = result else: # Sequential execution for controller_type in controller_types: controller_type_result, result = optimize_with_caching(controller_type) results[controller_type.value] = result return results # Usage
controller_types = [ControllerType.CLASSICAL_SMC, ControllerType.STA_SMC, ControllerType.ADAPTIVE_SMC]
performance_results = performance_optimized_workflow(controller_types, parallel_execution=True)
``` ### 4. Validation and Quality Assurance ```python
# example-metadata:

# runnable: false def comprehensive_validation_workflow(optimization_result: Dict[str, Any]) -> Dict[str, Any]: """validation workflow for optimized controllers.""" if not optimization_result['success']: return {'validation_status': 'FAILED', 'reason': 'Optimization failed'} validation_report = { 'validation_status': 'PENDING', 'checks_performed': [], 'issues_found': [], 'recommendations': [] } # 1. Basic validation checks validation_report['checks_performed'].append('basic_validation') basic_validation = optimization_result['validation_results'] if not basic_validation['gains_valid']: validation_report['issues_found'].append('Invalid gains detected') if not basic_validation['controller_stable']: validation_report['issues_found'].append('Controller stability issues') if not basic_validation['performance_acceptable']: validation_report['issues_found'].append('Performance below acceptable threshold') # 2. Convergence analysis validation_report['checks_performed'].append('convergence_analysis') performance = optimization_result['performance_analysis'] if not performance['converged']: validation_report['issues_found'].append('PSO did not converge') validation_report['recommendations'].append('Increase max_iterations or relax convergence_threshold') if performance['improvement_ratio'] < 0.1: validation_report['issues_found'].append('Low improvement ratio') validation_report['recommendations'].append('Review optimization bounds or increase population size') # 3. Gain analysis validation_report['checks_performed'].append('gain_analysis') gains = optimization_result['best_gains'] # Check for extreme values if any(g > 100.0 for g in gains): validation_report['issues_found'].append('Extremely high gains detected') validation_report['recommendations'].append('Review optimization bounds') if any(g < 0.1 for g in gains): validation_report['issues_found'].append('Very low gains detected') validation_report['recommendations'].append('Check minimum bounds') # 4. Cost analysis validation_report['checks_performed'].append('cost_analysis') best_cost = optimization_result['best_cost'] if best_cost > 100.0: validation_report['issues_found'].append('High optimization cost') validation_report['recommendations'].append('Review controller performance or optimization scenarios') # 5. Determine overall status if len(validation_report['issues_found']) == 0: validation_report['validation_status'] = 'PASSED' elif len(validation_report['issues_found']) <= 2: validation_report['validation_status'] = 'WARNING' else: validation_report['validation_status'] = 'FAILED' # 6. Generate summary validation_report['summary'] = { 'total_checks': len(validation_report['checks_performed']), 'issues_count': len(validation_report['issues_found']), 'recommendations_count': len(validation_report['recommendations']), 'overall_status': validation_report['validation_status'] } return validation_report # Usage example

pso_config = PSOFactoryConfig(controller_type=ControllerType.CLASSICAL_SMC)
pso_factory = EnhancedPSOFactory(pso_config)
result = pso_factory.optimize_controller() validation_report = comprehensive_validation_workflow(result)
print(f"Validation status: {validation_report['validation_status']}")
print(f"Issues found: {len(validation_report['issues_found'])}")
for issue in validation_report['issues_found']: print(f" - {issue}")
``` This PSO integration documentation provides complete workflows, advanced configuration options, performance analysis tools, and best practices for using the enhanced PSO-factory integration system. The workflows are designed to be production-ready with robust error handling, diagnostics, and quality assurance measures.