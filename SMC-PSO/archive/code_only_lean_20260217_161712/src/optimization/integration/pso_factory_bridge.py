#======================================================================================\\\
#================= src/optimization/integration/pso_factory_bridge.py =================\\\
#======================================================================================\\\

"""
Advanced PSO-Factory Integration Bridge.

This module provides robust integration between PSO optimization and the controller factory
pattern, addressing fitness evaluation issues, parameter validation, and convergence diagnostics.
"""

import numpy as np
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from src.controllers.factory import (
    SMCType, create_smc_for_pso, get_gain_bounds_for_pso,
    validate_smc_gains, get_expected_gain_count
)
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.config import load_config
from src.plant.configurations import ConfigurationFactory


class ControllerType(Enum):
    """Controller types for PSO optimization."""
    CLASSICAL_SMC = "classical_smc"
    ADAPTIVE_SMC = "adaptive_smc"
    STA_SMC = "sta_smc"
    HYBRID_SMC = "hybrid_adaptive_sta_smc"


@dataclass
class PSOFactoryConfig:
    """Configuration for PSO-Factory integration."""
    controller_type: ControllerType
    population_size: int = 20
    max_iterations: int = 50
    convergence_threshold: float = 1e-6
    max_stagnation_iterations: int = 10
    enable_adaptive_bounds: bool = True
    enable_gradient_guidance: bool = False
    fitness_timeout: float = 10.0  # seconds
    use_robust_evaluation: bool = True


class EnhancedPSOFactory:
    """Enhanced PSO-Factory integration with advanced optimization capabilities."""

    def __init__(self, config: PSOFactoryConfig, global_config_path: str = "config.yaml"):
        """Initialize enhanced PSO factory."""
        self.config = config
        self.global_config = load_config(global_config_path)
        self.logger = logging.getLogger(__name__)

        # Controller specifications
        self.controller_specs = self._get_controller_specifications()

        # Performance tracking
        self.optimization_history = []
        self.best_performers = {}

        # Validation metrics
        self.validation_stats = {
            'fitness_evaluations': 0,
            'failed_evaluations': 0,
            'convergence_checks': 0,
            'parameter_violations': 0
        }

    def _get_controller_specifications(self) -> Dict[str, Any]:
        """Get controller-specific optimization specifications."""
        smc_type_map = {
            ControllerType.CLASSICAL_SMC: SMCType.CLASSICAL,
            ControllerType.ADAPTIVE_SMC: SMCType.ADAPTIVE,
            ControllerType.STA_SMC: SMCType.SUPER_TWISTING,
            ControllerType.HYBRID_SMC: SMCType.HYBRID
        }

        smc_type = smc_type_map[self.config.controller_type]

        # Get PSO bounds and expected gain count
        lower_bounds, upper_bounds = get_gain_bounds_for_pso(smc_type)
        n_gains = get_expected_gain_count(smc_type)

        return {
            'smc_type': smc_type,
            'n_gains': n_gains,
            'bounds': (lower_bounds, upper_bounds),
            'parameter_ranges': list(zip(lower_bounds, upper_bounds)),
            'default_gains': self._get_default_gains(smc_type)
        }

    def _get_default_gains(self, smc_type: SMCType) -> List[float]:
        """Get robust default gains for controller type."""
        defaults = {
            SMCType.CLASSICAL: [15.0, 8.0, 12.0, 6.0, 25.0, 4.0],
            SMCType.ADAPTIVE: [15.0, 8.0, 12.0, 6.0, 3.0],
            SMCType.SUPER_TWISTING: [8.0, 4.0, 15.0, 8.0, 12.0, 6.0],
            SMCType.HYBRID: [12.0, 6.0, 10.0, 5.0]
        }
        return defaults.get(smc_type, [10.0] * 6)

    def create_enhanced_controller_factory(self) -> Callable:
        """Create an enhanced controller factory with robust error handling."""
        smc_type = self.controller_specs['smc_type']
        plant_config = ConfigurationFactory.create_default_config("simplified")

        def enhanced_factory(gains: Union[List[float], np.ndarray]) -> Any:
            """Enhanced controller factory with validation and error recovery."""
            try:
                # Validate gains
                gains_array = np.array(gains, dtype=float)
                if not validate_smc_gains(smc_type, gains_array):
                    raise ValueError(f"Invalid gains for {smc_type}: {gains}")

                # Create controller with robust configuration
                controller = create_smc_for_pso(
                    smc_type=smc_type,
                    gains=gains_array,
                    plant_config_or_model=plant_config,
                    max_force=150.0,
                    dt=0.001
                )

                # Add performance tracking attributes
                controller._factory_created = True
                controller._gain_validation_passed = True
                controller._creation_timestamp = np.datetime64('now')

                return controller

            except Exception as e:
                self.validation_stats['parameter_violations'] += 1
                self.logger.warning(f"Controller creation failed for gains {gains}: {e}")

                # Return fallback controller with safe gains
                safe_gains = self.controller_specs['default_gains']
                try:
                    return create_smc_for_pso(
                        smc_type=smc_type,
                        gains=safe_gains,
                        plant_config_or_model=plant_config,
                        max_force=150.0,
                        dt=0.001
                    )
                except Exception as fallback_error:
                    self.logger.error(f"Fallback controller creation failed: {fallback_error}")
                    raise

        # Add factory metadata
        enhanced_factory.controller_type = self.config.controller_type.value
        enhanced_factory.n_gains = self.controller_specs['n_gains']
        enhanced_factory.bounds = self.controller_specs['bounds']
        enhanced_factory.smc_type = smc_type

        return enhanced_factory

    def create_enhanced_fitness_function(self, controller_factory: Callable) -> Callable:
        """Create enhanced fitness function with proper simulation execution."""

        def enhanced_fitness(particles: np.ndarray) -> np.ndarray:
            """Enhanced fitness function with robust evaluation."""
            try:
                self.validation_stats['fitness_evaluations'] += 1

                # Validate particle dimensions
                if particles.shape[1] != self.controller_specs['n_gains']:
                    raise ValueError(
                        f"Expected {self.controller_specs['n_gains']} gains, "
                        f"got {particles.shape[1]}"
                    )

                fitness_values = np.zeros(particles.shape[0])

                for i, particle in enumerate(particles):
                    try:
                        # Create controller for this particle
                        controller = controller_factory(particle)

                        # Compute fitness using multiple test scenarios
                        fitness = self._evaluate_controller_performance(controller, particle)
                        fitness_values[i] = fitness

                    except Exception as e:
                        self.validation_stats['failed_evaluations'] += 1
                        self.logger.warning(f"Fitness evaluation failed for particle {i}: {e}")
                        # Assign high penalty for failed evaluations
                        fitness_values[i] = 1000.0

                return fitness_values

            except Exception as e:
                self.logger.error(f"Fitness function failed: {e}")
                # Return high penalty for all particles on critical failure
                return np.full(particles.shape[0], 1000.0)

        return enhanced_fitness

    def _evaluate_controller_performance(self, controller: Any, gains: np.ndarray) -> float:
        """Evaluate controller performance across multiple scenarios."""
        total_cost = 0.0
        scenario_count = 0

        # Test scenarios with different initial conditions
        test_scenarios = [
            # Scenario 1: Small disturbance
            {
                'initial_state': np.array([0.0, 0.1, 0.05, 0.0, 0.0, 0.0]),
                'sim_time': 2.0,
                'weight': 1.0,
                'description': 'small_disturbance'
            },
            # Scenario 2: Large angle deviation
            {
                'initial_state': np.array([0.0, 0.5, 0.3, 0.0, 0.0, 0.0]),
                'sim_time': 3.0,
                'weight': 1.5,
                'description': 'large_angles'
            },
            # Scenario 3: High velocity
            {
                'initial_state': np.array([0.0, 0.2, 0.1, 0.0, 1.0, 0.5]),
                'sim_time': 2.5,
                'weight': 1.2,
                'description': 'high_velocity'
            }
        ]

        for scenario in test_scenarios:
            try:
                cost = self._simulate_scenario(controller, scenario)
                total_cost += cost * scenario['weight']
                scenario_count += scenario['weight']

            except Exception as e:
                self.logger.warning(
                    f"Scenario {scenario['description']} failed for gains {gains}: {e}"
                )
                # Add penalty for scenario failure
                total_cost += 500.0 * scenario['weight']
                scenario_count += scenario['weight']

        # Return average weighted cost
        return total_cost / max(scenario_count, 1.0)

    def _simulate_scenario(self, controller: Any, scenario: Dict[str, Any]) -> float:
        """Simulate a specific control scenario and compute cost."""
        from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics

        # Create plant dynamics
        plant_config = ConfigurationFactory.create_default_config("simplified")
        dynamics = SimplifiedDIPDynamics(plant_config)

        # Simulation parameters
        dt = 0.01
        sim_time = scenario['sim_time']
        steps = int(sim_time / dt)

        # Initialize state
        state = scenario['initial_state'].copy()

        # Cost accumulators
        position_error_cost = 0.0
        control_effort_cost = 0.0
        control_rate_cost = 0.0
        stability_penalty = 0.0

        previous_control = 0.0

        for step in range(steps):
            try:
                # Compute control using PSO wrapper interface
                control_output = controller.compute_control(state)

                if isinstance(control_output, np.ndarray):
                    control = control_output[0] if control_output.size > 0 else 0.0
                else:
                    control = float(control_output)

                # Check for control saturation and stability
                if not np.isfinite(control):
                    stability_penalty += 100.0
                    control = 0.0

                control = np.clip(control, -150.0, 150.0)

                # Compute plant dynamics
                dynamics_result = dynamics.compute_dynamics(state, np.array([control]))

                if not dynamics_result.success or not np.all(np.isfinite(dynamics_result.state_derivative)):
                    stability_penalty += 50.0
                    break

                # Integrate dynamics (Euler method)
                state = state + dt * dynamics_result.state_derivative

                # Check for instability
                if np.any(np.abs(state[:3]) > 2.0) or np.any(np.abs(state[3:]) > 10.0):
                    stability_penalty += 200.0
                    break

                # Accumulate costs
                position_error_cost += dt * np.sum(state[:3] ** 2)
                control_effort_cost += dt * (control ** 2)

                control_rate = (control - previous_control) / dt
                control_rate_cost += dt * (control_rate ** 2)

                previous_control = control

            except Exception as e:
                self.logger.warning(f"Simulation step {step} failed: {e}")
                stability_penalty += 100.0
                break

        # Compute total cost with proper weighting
        total_cost = (
            10.0 * position_error_cost +  # State regulation
            0.1 * control_effort_cost +   # Control effort
            0.05 * control_rate_cost +    # Control smoothness
            stability_penalty             # Stability penalty
        )

        return float(total_cost)

    def optimize_controller(self) -> Dict[str, Any]:
        """Run enhanced PSO optimization with comprehensive monitoring."""
        self.logger.info(f"Starting PSO optimization for {self.config.controller_type.value}")

        # Create enhanced controller factory
        controller_factory = self.create_enhanced_controller_factory()

        # Create PSO tuner with enhanced configuration
        tuner = PSOTuner(
            controller_factory=controller_factory,
            config=self.global_config,
            seed=42
        )

        # Override fitness function with enhanced version
        enhanced_fitness = self.create_enhanced_fitness_function(controller_factory)
        tuner._fitness = enhanced_fitness

        try:
            # Run optimization with enhanced parameters
            result = tuner.optimise(
                n_particles_override=self.config.population_size,
                iters_override=self.config.max_iterations
            )

            # Validate optimization results
            optimized_gains = result['best_pos']
            best_cost = result['best_cost']

            # Create final controller with optimized gains
            final_controller = controller_factory(optimized_gains)

            # Comprehensive result analysis
            optimization_result = {
                'success': True,
                'best_gains': optimized_gains.tolist(),
                'best_cost': float(best_cost),
                'controller': final_controller,
                'convergence_history': result.get('history', {}),
                'controller_type': self.config.controller_type.value,
                'optimization_stats': self.validation_stats.copy(),
                'performance_analysis': self._analyze_optimization_performance(result),
                'validation_results': self._validate_optimized_controller(final_controller, optimized_gains)
            }

            self.logger.info(
                f"PSO optimization completed successfully. "
                f"Best cost: {best_cost:.6f}, Gains: {optimized_gains}"
            )

            return optimization_result

        except Exception as e:
            self.logger.error(f"PSO optimization failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'controller_type': self.config.controller_type.value,
                'optimization_stats': self.validation_stats.copy()
            }

    def _analyze_optimization_performance(self, pso_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PSO optimization performance and convergence."""
        history = pso_result.get('history', {})
        cost_history = history.get('cost', [])

        if len(cost_history) == 0:
            return {'convergence_analysis': 'No history available'}

        cost_array = np.array(cost_history)

        # Convergence analysis
        final_cost = cost_array[-1] if len(cost_array) > 0 else float('inf')
        initial_cost = cost_array[0] if len(cost_array) > 0 else float('inf')
        improvement_ratio = (initial_cost - final_cost) / max(initial_cost, 1e-6)

        # Detect convergence
        if len(cost_array) > 10:
            recent_costs = cost_array[-10:]
            convergence_rate = np.std(recent_costs) / max(np.mean(recent_costs), 1e-6)
            converged = convergence_rate < self.config.convergence_threshold
        else:
            convergence_rate = float('inf')
            converged = False

        return {
            'converged': converged,
            'convergence_rate': float(convergence_rate),
            'improvement_ratio': float(improvement_ratio),
            'final_cost': float(final_cost),
            'initial_cost': float(initial_cost),
            'iterations_completed': len(cost_array),
            'cost_reduction': float(initial_cost - final_cost)
        }

    def _validate_optimized_controller(self, controller: Any, gains: np.ndarray) -> Dict[str, Any]:
        """Validate the optimized controller performance."""
        validation_results = {
            'gains_valid': True,
            'controller_stable': True,
            'performance_acceptable': True,
            'validation_errors': []
        }

        try:
            # Validate gains are within bounds
            lower_bounds, upper_bounds = self.controller_specs['bounds']
            for i, (gain, lower, upper) in enumerate(zip(gains, lower_bounds, upper_bounds)):
                if not (lower <= gain <= upper):
                    validation_results['gains_valid'] = False
                    validation_results['validation_errors'].append(
                        f"Gain {i} ({gain:.3f}) outside bounds [{lower}, {upper}]"
                    )

            # Test controller stability with reference state
            test_state = np.array([0.0, 0.1, 0.05, 0.0, 0.0, 0.0])
            try:
                control_output = controller.compute_control(test_state)
                if not np.isfinite(control_output).all():
                    validation_results['controller_stable'] = False
                    validation_results['validation_errors'].append("Controller produces non-finite outputs")
            except Exception as e:
                validation_results['controller_stable'] = False
                validation_results['validation_errors'].append(f"Controller computation failed: {e}")

            # Performance acceptability test
            try:
                performance_cost = self._evaluate_controller_performance(controller, gains)
                if performance_cost > 100.0:  # Threshold for acceptable performance
                    validation_results['performance_acceptable'] = False
                    validation_results['validation_errors'].append(
                        f"Performance cost too high: {performance_cost:.3f}"
                    )
            except Exception as e:
                validation_results['performance_acceptable'] = False
                validation_results['validation_errors'].append(f"Performance evaluation failed: {e}")

        except Exception as e:
            validation_results['validation_errors'].append(f"Validation process failed: {e}")

        return validation_results

    def get_optimization_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive optimization diagnostics."""
        return {
            'controller_type': self.config.controller_type.value,
            'configuration': {
                'population_size': self.config.population_size,
                'max_iterations': self.config.max_iterations,
                'convergence_threshold': self.config.convergence_threshold
            },
            'controller_specs': self.controller_specs,
            'validation_statistics': self.validation_stats,
            'optimization_history': self.optimization_history
        }


def create_optimized_controller_factory(
    controller_type: ControllerType,
    optimization_config: Optional[PSOFactoryConfig] = None
) -> Tuple[Callable, Dict[str, Any]]:
    """Create an optimized controller factory using PSO with comprehensive results."""

    if optimization_config is None:
        optimization_config = PSOFactoryConfig(
            controller_type=controller_type,
            population_size=15,
            max_iterations=30
        )

    # Create PSO factory and run optimization
    pso_factory = EnhancedPSOFactory(optimization_config)
    optimization_result = pso_factory.optimize_controller()

    if not optimization_result['success']:
        raise RuntimeError(f"Controller optimization failed: {optimization_result.get('error', 'Unknown error')}")

    optimized_gains = optimization_result['best_gains']
    controller_type_str = controller_type.value

    def optimized_factory(gains: Optional[Union[List[float], np.ndarray]] = None) -> Any:
        """Factory that creates controllers with optimized or provided gains."""
        if gains is None:
            gains = optimized_gains

        return pso_factory.create_enhanced_controller_factory()(gains)

    # Add metadata
    optimized_factory.controller_type = controller_type_str
    optimized_factory.n_gains = len(optimized_gains)
    optimized_factory.optimized_gains = optimized_gains
    optimized_factory.optimization_result = optimization_result

    return optimized_factory, optimization_result


# Backwards compatibility functions
def optimize_classical_smc() -> Tuple[Callable, Dict[str, Any]]:
    """Optimize Classical SMC controller using PSO."""
    return create_optimized_controller_factory(ControllerType.CLASSICAL_SMC)


def optimize_adaptive_smc() -> Tuple[Callable, Dict[str, Any]]:
    """Optimize Adaptive SMC controller using PSO."""
    return create_optimized_controller_factory(ControllerType.ADAPTIVE_SMC)


def optimize_sta_smc() -> Tuple[Callable, Dict[str, Any]]:
    """Optimize Super-Twisting SMC controller using PSO."""
    return create_optimized_controller_factory(ControllerType.STA_SMC)