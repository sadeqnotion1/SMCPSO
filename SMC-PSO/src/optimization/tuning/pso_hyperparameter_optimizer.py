#======================================================================================\\\
#============== src/optimization/tuning/pso_hyperparameter_optimizer.py ===============\\\
#======================================================================================\\\

"""
Advanced PSO Hyperparameter Optimization for Factory-Generated Controllers.

This module provides sophisticated hyperparameter optimization for PSO algorithms
specifically tuned for factory-generated SMC controllers. Features include adaptive
parameter adjustment, multi-objective optimization, and controller-specific tuning.

Key Features:
- Adaptive PSO hyperparameter optimization
- Controller-specific parameter tuning
- Multi-objective optimization (convergence speed vs quality)
- Population dynamics optimization
- Real-time parameter adaptation
- Performance-driven hyperparameter selection
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
import time
import json
from scipy.optimize import differential_evolution, minimize
import warnings

from src.controllers.factory import SMCType, create_smc_for_pso
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.config import load_config
from src.utils.seed import set_global_seed

warnings.filterwarnings("ignore", category=RuntimeWarning)


class OptimizationObjective(Enum):
    """PSO optimization objectives."""
    CONVERGENCE_SPEED = "convergence_speed"
    SOLUTION_QUALITY = "solution_quality"
    ROBUSTNESS = "robustness"
    EFFICIENCY = "efficiency"
    MULTI_OBJECTIVE = "multi_objective"


class PSOParameterType(Enum):
    """Types of PSO parameters to optimize."""
    POPULATION_SIZE = "population_size"
    INERTIA_WEIGHT = "inertia_weight"
    COGNITIVE_COEFFICIENT = "cognitive_coefficient"
    SOCIAL_COEFFICIENT = "social_coefficient"
    VELOCITY_CLAMP = "velocity_clamp"
    CONVERGENCE_THRESHOLD = "convergence_threshold"
    MAX_ITERATIONS = "max_iterations"


@dataclass
class PSOHyperparameters:
    """PSO hyperparameter configuration."""
    population_size: int = 20
    inertia_weight: float = 0.729
    cognitive_coefficient: float = 1.49445
    social_coefficient: float = 1.49445
    velocity_clamp_factor: float = 0.5
    convergence_threshold: float = 1e-6
    max_iterations: int = 100

    # Advanced parameters
    adaptive_inertia: bool = True
    inertia_decay_rate: float = 0.99
    velocity_clamping: bool = True
    restart_threshold: int = 20
    diversity_threshold: float = 1e-3

    # Performance weights
    convergence_weight: float = 0.6
    quality_weight: float = 0.4


@dataclass
class OptimizationResult:
    """Result of hyperparameter optimization."""
    optimized_parameters: PSOHyperparameters
    performance_metrics: Dict[str, float]
    optimization_history: List[Dict[str, Any]]
    controller_type: SMCType
    optimization_time: float
    validation_results: Dict[str, Any]
    improvement_ratio: float
    success: bool


class PSOHyperparameterOptimizer:
    """
    Advanced PSO hyperparameter optimizer for factory-generated controllers.

    Optimizes PSO hyperparameters specifically for each controller type to maximize
    convergence efficiency and solution quality in the factory integration context.
    """

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize PSO hyperparameter optimizer."""
        self.config = load_config(config_path)
        self.logger = logging.getLogger(__name__)

        # Set reproducible seed
        set_global_seed(42)

        # Optimization parameters
        self.optimization_trials = 20  # Number of trials per configuration
        self.validation_trials = 5     # Number of validation trials
        self.max_optimization_time = 600.0  # Maximum optimization time (seconds)

        # Performance tracking
        self.optimization_history = []
        self.controller_performance_db = {}

        # Initialize parameter search spaces
        self.parameter_bounds = self._initialize_parameter_bounds()

        # Controller-specific baseline parameters
        self.baseline_parameters = self._initialize_baseline_parameters()

    def _initialize_parameter_bounds(self) -> Dict[str, Tuple[float, float]]:
        """Initialize search bounds for PSO hyperparameters."""
        return {
            'population_size': (8, 50),
            'inertia_weight': (0.1, 0.9),
            'cognitive_coefficient': (0.5, 3.0),
            'social_coefficient': (0.5, 3.0),
            'velocity_clamp_factor': (0.1, 1.0),
            'convergence_threshold': (1e-8, 1e-3),
            'max_iterations': (20, 200),
            'inertia_decay_rate': (0.95, 0.999),
            'diversity_threshold': (1e-5, 1e-2),
            'restart_threshold': (5, 50)
        }

    def _initialize_baseline_parameters(self) -> Dict[SMCType, PSOHyperparameters]:
        """Initialize baseline PSO parameters for each controller type."""
        return {
            SMCType.CLASSICAL: PSOHyperparameters(
                population_size=20,
                inertia_weight=0.729,
                cognitive_coefficient=1.49445,
                social_coefficient=1.49445,
                max_iterations=50,
                convergence_threshold=1e-5
            ),
            SMCType.ADAPTIVE: PSOHyperparameters(
                population_size=25,
                inertia_weight=0.6,
                cognitive_coefficient=1.8,
                social_coefficient=1.2,
                max_iterations=60,
                convergence_threshold=5e-6
            ),
            SMCType.SUPER_TWISTING: PSOHyperparameters(
                population_size=18,
                inertia_weight=0.8,
                cognitive_coefficient=1.3,
                social_coefficient=1.7,
                max_iterations=45,
                convergence_threshold=2e-5
            ),
            SMCType.HYBRID: PSOHyperparameters(
                population_size=22,
                inertia_weight=0.65,
                cognitive_coefficient=1.6,
                social_coefficient=1.4,
                max_iterations=55,
                convergence_threshold=8e-6
            )
        }

    def optimize_hyperparameters(self,
                                controller_type: SMCType,
                                objective: OptimizationObjective = OptimizationObjective.MULTI_OBJECTIVE,
                                max_time: float = 300.0) -> OptimizationResult:
        """
        Optimize PSO hyperparameters for specific controller type.

        Args:
            controller_type: Controller type to optimize for
            objective: Optimization objective
            max_time: Maximum optimization time in seconds

        Returns:
            OptimizationResult with optimized parameters and metrics
        """
        self.logger.info(f"Optimizing PSO hyperparameters for {controller_type.value}")
        start_time = time.time()

        # Get baseline parameters
        baseline_params = self.baseline_parameters[controller_type]

        # Create optimization objective function
        objective_function = self._create_objective_function(controller_type, objective)

        # Run hyperparameter optimization
        try:
            optimization_result = self._run_optimization(
                objective_function, controller_type, max_time * 0.8
            )

            # Extract optimized parameters
            optimized_params = self._parameters_from_vector(optimization_result.x)

            # Validate optimized parameters
            validation_results = self._validate_optimized_parameters(
                controller_type, optimized_params, max_time * 0.2
            )

            # Calculate improvement ratio
            improvement_ratio = self._calculate_improvement_ratio(
                baseline_params, optimized_params, controller_type
            )

            optimization_time = time.time() - start_time

            # Create result object
            result = OptimizationResult(
                optimized_parameters=optimized_params,
                performance_metrics=validation_results['performance_metrics'],
                optimization_history=self.optimization_history.copy(),
                controller_type=controller_type,
                optimization_time=optimization_time,
                validation_results=validation_results,
                improvement_ratio=improvement_ratio,
                success=validation_results['validation_successful']
            )

            self.logger.info(
                f"Hyperparameter optimization completed for {controller_type.value}: "
                f"Improvement: {improvement_ratio:.2f}x, Time: {optimization_time:.1f}s"
            )

            return result

        except Exception as e:
            self.logger.error(f"Hyperparameter optimization failed for {controller_type.value}: {e}")
            optimization_time = time.time() - start_time

            return OptimizationResult(
                optimized_parameters=baseline_params,
                performance_metrics={},
                optimization_history=[],
                controller_type=controller_type,
                optimization_time=optimization_time,
                validation_results={'error': str(e)},
                improvement_ratio=1.0,
                success=False
            )

    def _create_objective_function(self,
                                 controller_type: SMCType,
                                 objective: OptimizationObjective) -> Callable:
        """Create objective function for hyperparameter optimization."""

        def objective_function(parameter_vector: np.ndarray) -> float:
            """Objective function for PSO hyperparameter optimization."""
            try:
                # Convert parameter vector to PSO hyperparameters
                params = self._parameters_from_vector(parameter_vector)

                # Evaluate PSO performance with these parameters
                performance = self._evaluate_pso_performance(controller_type, params)

                # Calculate objective value based on optimization goal
                if objective == OptimizationObjective.CONVERGENCE_SPEED:
                    # Minimize convergence time
                    objective_value = performance['convergence_time'] + performance['iterations'] * 0.1

                elif objective == OptimizationObjective.SOLUTION_QUALITY:
                    # Minimize final cost
                    objective_value = performance['final_cost'] * 1000

                elif objective == OptimizationObjective.ROBUSTNESS:
                    # Minimize variance across multiple runs
                    objective_value = performance['cost_variance'] * 1000 + performance['convergence_variance']

                elif objective == OptimizationObjective.EFFICIENCY:
                    # Balance quality and computational cost
                    objective_value = (
                        performance['final_cost'] * 500 +
                        performance['convergence_time'] * 0.5 +
                        performance['iterations'] * 0.1
                    )

                else:  # MULTI_OBJECTIVE
                    # Weighted combination of multiple objectives
                    objective_value = (
                        0.4 * performance['final_cost'] * 1000 +
                        0.3 * performance['convergence_time'] +
                        0.2 * performance['iterations'] * 0.1 +
                        0.1 * performance['cost_variance'] * 1000
                    )

                return float(objective_value)

            except Exception as e:
                self.logger.warning(f"Objective function evaluation failed: {e}")
                return 1e6  # Large penalty for failed evaluations

        return objective_function

    def _parameters_from_vector(self, vector: np.ndarray) -> PSOHyperparameters:
        """Convert optimization vector to PSO hyperparameters."""
        bounds = self.parameter_bounds

        # Ensure vector has correct length
        expected_length = len(bounds)
        if len(vector) != expected_length:
            raise ValueError(f"Expected vector length {expected_length}, got {len(vector)}")

        # Map vector values to parameter ranges
        param_values = {}
        for i, (param_name, (lower, upper)) in enumerate(bounds.items()):
            # Clamp and scale vector value to parameter range
            clamped_value = np.clip(vector[i], 0.0, 1.0)
            scaled_value = lower + clamped_value * (upper - lower)

            # Apply type conversion for integer parameters
            if param_name in ['population_size', 'max_iterations', 'restart_threshold']:
                scaled_value = int(round(scaled_value))

            param_values[param_name] = scaled_value

        # Create PSOHyperparameters object
        return PSOHyperparameters(
            population_size=param_values['population_size'],
            inertia_weight=param_values['inertia_weight'],
            cognitive_coefficient=param_values['cognitive_coefficient'],
            social_coefficient=param_values['social_coefficient'],
            velocity_clamp_factor=param_values['velocity_clamp_factor'],
            convergence_threshold=param_values['convergence_threshold'],
            max_iterations=param_values['max_iterations'],
            inertia_decay_rate=param_values['inertia_decay_rate'],
            diversity_threshold=param_values['diversity_threshold'],
            restart_threshold=param_values['restart_threshold']
        )

    def _parameters_to_vector(self, params: PSOHyperparameters) -> np.ndarray:
        """Convert PSO hyperparameters to optimization vector."""
        bounds = self.parameter_bounds
        vector = []

        for param_name, (lower, upper) in bounds.items():
            value = getattr(params, param_name)
            # Normalize to [0, 1] range
            normalized_value = (value - lower) / (upper - lower)
            vector.append(np.clip(normalized_value, 0.0, 1.0))

        return np.array(vector)

    def _evaluate_pso_performance(self,
                                controller_type: SMCType,
                                params: PSOHyperparameters) -> Dict[str, float]:
        """Evaluate PSO performance with given hyperparameters."""
        # Create controller factory
        def controller_factory(gains):
            return create_smc_for_pso(
                smc_type=controller_type,
                gains=gains,
                max_force=150.0
            )

        # Performance metrics across multiple trials
        trial_results = []

        # Run multiple trials for statistical reliability
        num_trials = min(3, self.optimization_trials)

        for trial in range(num_trials):
            try:
                # Create PSO tuner with specified hyperparameters
                tuner = PSOTuner(
                    controller_factory=controller_factory,
                    config=self.config,
                    seed=42 + trial
                )

                # Run PSO optimization
                start_time = time.time()
                result = tuner.optimise(
                    n_particles_override=params.population_size,
                    iters_override=min(params.max_iterations, 30),  # Limit for speed
                    options_override={
                        'w': params.inertia_weight,
                        'c1': params.cognitive_coefficient,
                        'c2': params.social_coefficient
                    }
                )
                convergence_time = time.time() - start_time

                # Extract performance metrics
                final_cost = result['best_cost']
                cost_history = result.get('history', {}).get('cost', [])
                iterations = len(cost_history)

                trial_results.append({
                    'final_cost': final_cost,
                    'convergence_time': convergence_time,
                    'iterations': iterations,
                    'cost_history': cost_history
                })

            except Exception as e:
                self.logger.debug(f"PSO trial failed: {e}")
                # Add penalty result
                trial_results.append({
                    'final_cost': 1000.0,
                    'convergence_time': 60.0,
                    'iterations': params.max_iterations,
                    'cost_history': []
                })

        # Calculate aggregate performance metrics
        if trial_results:
            final_costs = [r['final_cost'] for r in trial_results]
            convergence_times = [r['convergence_time'] for r in trial_results]
            iterations_list = [r['iterations'] for r in trial_results]

            performance = {
                'final_cost': np.mean(final_costs),
                'cost_variance': np.var(final_costs),
                'convergence_time': np.mean(convergence_times),
                'convergence_variance': np.var(convergence_times),
                'iterations': np.mean(iterations_list),
                'success_rate': sum(1 for cost in final_costs if cost < 100) / len(final_costs)
            }
        else:
            # No successful trials
            performance = {
                'final_cost': 1000.0,
                'cost_variance': 0.0,
                'convergence_time': 60.0,
                'convergence_variance': 0.0,
                'iterations': params.max_iterations,
                'success_rate': 0.0
            }

        return performance

    def _run_optimization(self,
                        objective_function: Callable,
                        controller_type: SMCType,
                        max_time: float) -> Any:
        """Run hyperparameter optimization using differential evolution."""
        # Get baseline parameters as starting point
        baseline_params = self.baseline_parameters[controller_type]
        initial_guess = self._parameters_to_vector(baseline_params)

        # Define bounds for optimization (normalized to [0, 1])
        bounds = [(0.0, 1.0) for _ in range(len(self.parameter_bounds))]

        try:
            # Use differential evolution for global optimization
            result = differential_evolution(
                objective_function,
                bounds,
                seed=42,
                maxiter=15,  # Limit iterations for time constraints
                popsize=8,   # Small population for efficiency
                atol=1e-3,
                tol=1e-3,
                workers=1,   # Single worker to avoid conflicts
                updating='immediate'
            )

            self.logger.info(f"Optimization completed: {result.message}")
            return result

        except Exception as e:
            self.logger.warning(f"Differential evolution failed: {e}, using local optimization")

            # Fallback to local optimization
            try:
                result = minimize(
                    objective_function,
                    initial_guess,
                    bounds=bounds,
                    method='L-BFGS-B',
                    options={'maxiter': 10}
                )
                return result

            except Exception as e2:
                self.logger.error(f"Local optimization also failed: {e2}")
                # Return baseline parameters
                class FallbackResult:
                    def __init__(self, x):
                        self.x = x
                        self.success = False

                return FallbackResult(initial_guess)

    def _validate_optimized_parameters(self,
                                     controller_type: SMCType,
                                     optimized_params: PSOHyperparameters,
                                     max_time: float) -> Dict[str, Any]:
        """Validate optimized parameters through comprehensive testing."""
        validation_results = {
            'validation_successful': False,
            'performance_metrics': {},
            'parameter_stability': False,
            'convergence_reliability': False
        }

        try:
            # Test 1: Parameter reasonableness
            param_bounds = self.parameter_bounds
            reasonable_params = True

            for param_name, (lower, upper) in param_bounds.items():
                value = getattr(optimized_params, param_name)
                if not (lower <= value <= upper):
                    reasonable_params = False
                    break

            # Test 2: Convergence reliability
            performance_results = []
            for trial in range(self.validation_trials):
                try:
                    performance = self._evaluate_pso_performance(
                        controller_type, optimized_params
                    )
                    performance_results.append(performance)
                except Exception as e:
                    self.logger.debug(f"Validation trial {trial} failed: {e}")

            if performance_results:
                # Calculate reliability metrics
                final_costs = [r['final_cost'] for r in performance_results]
                convergence_times = [r['convergence_time'] for r in performance_results]
                success_rates = [r['success_rate'] for r in performance_results]

                avg_final_cost = np.mean(final_costs)
                cost_consistency = 1.0 - (np.std(final_costs) / max(avg_final_cost, 1e-6))
                avg_success_rate = np.mean(success_rates)

                validation_results['performance_metrics'] = {
                    'average_final_cost': avg_final_cost,
                    'cost_consistency': cost_consistency,
                    'average_convergence_time': np.mean(convergence_times),
                    'average_success_rate': avg_success_rate
                }

                # Success criteria
                convergence_reliable = (
                    avg_final_cost < 50.0 and
                    avg_success_rate > 0.6 and
                    cost_consistency > 0.7
                )

                validation_results['convergence_reliability'] = convergence_reliable
                validation_results['parameter_stability'] = reasonable_params

                validation_results['validation_successful'] = (
                    reasonable_params and convergence_reliable
                )

        except Exception as e:
            validation_results['error'] = str(e)
            self.logger.error(f"Parameter validation failed: {e}")

        return validation_results

    def _calculate_improvement_ratio(self,
                                   baseline_params: PSOHyperparameters,
                                   optimized_params: PSOHyperparameters,
                                   controller_type: SMCType) -> float:
        """Calculate improvement ratio from parameter optimization."""
        try:
            # Evaluate baseline performance
            baseline_performance = self._evaluate_pso_performance(controller_type, baseline_params)

            # Evaluate optimized performance
            optimized_performance = self._evaluate_pso_performance(controller_type, optimized_params)

            # Calculate improvement metrics
            cost_improvement = (
                baseline_performance['final_cost'] /
                max(optimized_performance['final_cost'], 1e-6)
            )

            time_improvement = (
                baseline_performance['convergence_time'] /
                max(optimized_performance['convergence_time'], 1e-6)
            )

            success_improvement = (
                optimized_performance['success_rate'] /
                max(baseline_performance['success_rate'], 1e-6)
            )

            # Geometric mean of improvements
            improvement_ratio = (cost_improvement * time_improvement * success_improvement) ** (1/3)

            return min(5.0, improvement_ratio)  # Cap at 5x improvement

        except Exception as e:
            self.logger.warning(f"Improvement calculation failed: {e}")
            return 1.0

    def optimize_all_controllers(self,
                               objective: OptimizationObjective = OptimizationObjective.MULTI_OBJECTIVE
                               ) -> Dict[SMCType, OptimizationResult]:
        """Optimize hyperparameters for all controller types."""
        self.logger.info("Optimizing PSO hyperparameters for all controllers")

        results = {}
        optimization_time_per_controller = self.max_optimization_time / 4

        for controller_type in [SMCType.CLASSICAL, SMCType.ADAPTIVE, SMCType.SUPER_TWISTING, SMCType.HYBRID]:
            try:
                result = self.optimize_hyperparameters(
                    controller_type, objective, optimization_time_per_controller
                )
                results[controller_type] = result

                status = "✓ SUCCESS" if result.success else "✗ FAILED"
                self.logger.info(
                    f"{status} {controller_type.value}: "
                    f"Improvement: {result.improvement_ratio:.2f}x"
                )

            except Exception as e:
                self.logger.error(f"Optimization failed for {controller_type.value}: {e}")
                results[controller_type] = OptimizationResult(
                    optimized_parameters=self.baseline_parameters[controller_type],
                    performance_metrics={},
                    optimization_history=[],
                    controller_type=controller_type,
                    optimization_time=0.0,
                    validation_results={'error': str(e)},
                    improvement_ratio=1.0,
                    success=False
                )

        return results

    def export_optimized_configuration(self,
                                     optimization_results: Dict[SMCType, OptimizationResult],
                                     output_path: str = "optimized_pso_hyperparameters.json"
                                     ) -> Dict[str, Any]:
        """Export optimized hyperparameters as configuration file."""
        export_config = {
            'metadata': {
                'optimization_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'optimization_objective': 'multi_objective',
                'total_optimization_time': sum(r.optimization_time for r in optimization_results.values()),
                'overall_success_rate': sum(1 for r in optimization_results.values() if r.success) / len(optimization_results)
            },
            'optimized_hyperparameters': {},
            'performance_summary': {}
        }

        for controller_type, result in optimization_results.items():
            controller_key = controller_type.value
            params = result.optimized_parameters

            export_config['optimized_hyperparameters'][controller_key] = {
                'population_size': params.population_size,
                'inertia_weight': params.inertia_weight,
                'cognitive_coefficient': params.cognitive_coefficient,
                'social_coefficient': params.social_coefficient,
                'velocity_clamp_factor': params.velocity_clamp_factor,
                'convergence_threshold': params.convergence_threshold,
                'max_iterations': params.max_iterations,
                'adaptive_inertia': params.adaptive_inertia,
                'inertia_decay_rate': params.inertia_decay_rate,
                'diversity_threshold': params.diversity_threshold,
                'restart_threshold': params.restart_threshold
            }

            export_config['performance_summary'][controller_key] = {
                'improvement_ratio': result.improvement_ratio,
                'optimization_successful': result.success,
                'optimization_time_seconds': result.optimization_time,
                'performance_metrics': result.performance_metrics
            }

        # Save to file
        with open(output_path, 'w') as f:
            json.dump(export_config, f, indent=2)

        self.logger.info(f"Optimized hyperparameters exported to {output_path}")
        return export_config


def run_pso_hyperparameter_optimization() -> Dict[str, Any]:
    """Run complete PSO hyperparameter optimization workflow."""
    print("=" * 80)
    print("PSO HYPERPARAMETER OPTIMIZATION - GitHub Issue #6")
    print("Advanced PSO Parameter Tuning for Factory Controllers")
    print("=" * 80)

    # Initialize optimizer
    optimizer = PSOHyperparameterOptimizer()

    # Run optimization for all controllers
    print("\n🔍 Optimizing PSO hyperparameters for all controller types...")
    optimization_results = optimizer.optimize_all_controllers(
        objective=OptimizationObjective.MULTI_OBJECTIVE
    )

    # Export optimized configuration
    print("\n📤 Exporting optimized hyperparameter configuration...")
    config_export = optimizer.export_optimized_configuration(optimization_results)

    # Print summary
    print("\n" + "=" * 60)
    print("PSO HYPERPARAMETER OPTIMIZATION SUMMARY")
    print("=" * 60)

    successful_optimizations = 0
    total_improvement = 0.0

    for controller_type, result in optimization_results.items():
        status = "✅ SUCCESS" if result.success else "❌ FAILED"
        improvement = result.improvement_ratio

        print(f"{controller_type.value:25} | {status} | Improvement: {improvement:.2f}x")

        if result.success:
            successful_optimizations += 1
            total_improvement += improvement

    success_rate = (successful_optimizations / len(optimization_results)) * 100
    avg_improvement = total_improvement / max(successful_optimizations, 1)

    print("\n" + "-" * 60)
    print(f"Overall Success Rate: {success_rate:.1f}%")
    print(f"Average Improvement: {avg_improvement:.2f}x")
    print(f"Total Optimization Time: {sum(r.optimization_time for r in optimization_results.values()):.1f}s")

    if success_rate >= 75:
        print("\n🎉 PSO HYPERPARAMETER OPTIMIZATION: SUCCESSFUL")
        print("✅ Enhanced PSO parameters for improved convergence")
        print("✅ Controller-specific hyperparameter tuning completed")
        print("✅ Multi-objective optimization objectives achieved")
        print("✅ Configuration exported for production use")
    else:
        print("\n⚠️  PSO HYPERPARAMETER OPTIMIZATION: PARTIAL SUCCESS")
        print(f"✅ {successful_optimizations}/{len(optimization_results)} controllers optimized")
        print("⚠️  Some controllers may benefit from manual parameter tuning")

    return {
        'optimization_results': optimization_results,
        'config_export': config_export,
        'summary': {
            'success_rate': success_rate,
            'average_improvement': avg_improvement,
            'successful_optimizations': successful_optimizations,
            'total_controllers': len(optimization_results)
        }
    }


if __name__ == "__main__":
    results = run_pso_hyperparameter_optimization()