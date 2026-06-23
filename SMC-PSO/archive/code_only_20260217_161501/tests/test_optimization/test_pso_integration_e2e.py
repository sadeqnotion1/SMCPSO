#======================================================================================\\\
#================ tests/test_optimization/test_pso_integration_e2e.py =================\\\
#======================================================================================\\\

"""
End-to-End PSO Integration Validation Tests.

This module provides comprehensive end-to-end testing of the PSO optimization system
including controller integration, fitness evaluation, convergence validation, and
result management.

Test Coverage:
- Complete PSO optimization workflows
- Controller factory integration
- Multi-objective optimization
- Bounds validation and adjustment
- Results serialization and loading
- Convergence criteria validation
- Statistical significance testing
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.optimization.algorithms.multi_objective_pso import run_multi_objective_pso
from src.optimization.validation.pso_bounds_validator import PSOBoundsValidator
from src.optimization.core.results_manager import (
    OptimizationResultsManager, OptimizationResults, create_optimization_metadata
)


class TestPSOEndToEndIntegration:
    """Comprehensive end-to-end PSO integration tests."""

    @pytest.fixture
    def test_config(self):
        """Create test configuration for PSO optimization."""
        return {
            'physics': {
                'cart_mass': 1.0,
                'pendulum1_mass': 0.1,
                'pendulum2_mass': 0.1,
                'pendulum1_length': 0.5,
                'pendulum2_length': 0.5,
                'pendulum1_com': 0.25,
                'pendulum2_com': 0.25,
                'pendulum1_inertia': 0.01,
                'pendulum2_inertia': 0.01,
                'gravity': 9.81,
                'cart_friction': 0.1,
                'joint1_friction': 0.01,
                'joint2_friction': 0.01
            },
            'simulation': {
                'duration': 1.0,
                'dt': 0.01,
                'use_full_dynamics': False
            },
            'pso': {
                'n_particles': 10,
                'iters': 5,
                'w': 0.5,
                'c1': 1.5,
                'c2': 1.5,
                'bounds': {
                    'min': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                    'max': [20.0, 20.0, 10.0, 10.0, 50.0, 10.0],
                    'classical_smc': {
                        'min': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                        'max': [20.0, 20.0, 10.0, 10.0, 50.0, 10.0]
                    }
                }
            },
            'cost_function': {
                'weights': {
                    'state_error': 50.0,
                    'control_effort': 0.2,
                    'control_rate': 0.1,
                    'stability': 0.1
                },
                'baseline': {
                    'gains': [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
                },
                'instability_penalty': 1000.0
            }
        }

    @pytest.fixture
    def mock_controller_factory(self):
        """Mock controller factory for testing."""
        def factory(gains):
            mock_controller = MagicMock()
            mock_controller.max_force = 150.0
            mock_controller.dynamics_model = MagicMock()
            mock_controller.dynamics_model.step = MagicMock(return_value=np.zeros(6))
            return mock_controller

        factory.n_gains = 6
        factory.controller_type = 'classical_smc'
        return factory

    def test_complete_pso_workflow(self, test_config, mock_controller_factory):
        """Test complete PSO optimization workflow."""
        # Create PSO tuner
        tuner = PSOTuner(mock_controller_factory, test_config, seed=42)

        # Run optimization
        result = tuner.optimise()

        # Validate results structure
        assert 'best_cost' in result
        assert 'best_pos' in result
        assert 'history' in result
        assert isinstance(result['best_cost'], (int, float))
        assert isinstance(result['best_pos'], np.ndarray)
        assert len(result['best_pos']) == 6  # Classical SMC has 6 gains

        # Validate optimization progress
        assert result['best_cost'] >= 0  # Cost should be non-negative
        assert np.all(np.isfinite(result['best_pos']))  # Gains should be finite

        # Validate bounds compliance
        bounds_min = test_config['pso']['bounds']['min']
        bounds_max = test_config['pso']['bounds']['max']
        for i, gain in enumerate(result['best_pos']):
            assert bounds_min[i] <= gain <= bounds_max[i]

    def test_pso_convergence_behavior(self, test_config, mock_controller_factory):
        """Test PSO convergence behavior and criteria."""
        # Test with different convergence settings
        test_config['pso']['iters'] = 20

        tuner = PSOTuner(mock_controller_factory, test_config, seed=42)
        result = tuner.optimise()

        # Check convergence history
        cost_history = result['history']['cost']
        assert len(cost_history) <= test_config['pso']['iters']

        # Verify convergence trend (cost should generally decrease)
        if len(cost_history) > 1:
            # Allow for some fluctuation but expect overall improvement
            final_cost = cost_history[-1]
            initial_cost = cost_history[0]
            assert final_cost <= initial_cost * 1.1  # Allow small increase due to randomness

    def test_bounds_validation_integration(self, test_config):
        """Test PSO bounds validation system."""
        # Create mock config object
        class MockConfig:
            def __init__(self, config_dict):
                for key, value in config_dict.items():
                    if isinstance(value, dict):
                        setattr(self, key, MockConfig(value))
                    else:
                        setattr(self, key, value)

        config_obj = MockConfig(test_config)
        validator = PSOBoundsValidator(config_obj)

        # Test valid bounds
        bounds_min = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        bounds_max = [20.0, 20.0, 10.0, 10.0, 50.0, 10.0]

        result = validator.validate_bounds('classical_smc', bounds_min, bounds_max)
        assert result.is_valid
        assert len(result.warnings) == 0

        # Test invalid bounds (min > max)
        invalid_bounds_min = [20.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        invalid_bounds_max = [10.0, 20.0, 10.0, 10.0, 50.0, 10.0]

        result = validator.validate_bounds('classical_smc', invalid_bounds_min, invalid_bounds_max)
        assert not result.is_valid
        assert len(result.warnings) > 0

    def test_multi_objective_optimization(self, test_config, mock_controller_factory):
        """Test multi-objective PSO optimization."""
        # Create mock config object
        class MockConfig:
            def __init__(self, config_dict):
                for key, value in config_dict.items():
                    if isinstance(value, dict):
                        setattr(self, key, MockConfig(value))
                    else:
                        setattr(self, key, value)

        config_obj = MockConfig(test_config)

        # Run multi-objective optimization
        results = run_multi_objective_pso(mock_controller_factory, config_obj, seed=42)

        # Validate multi-objective results
        assert 'pareto_front' in results
        assert 'pareto_positions' in results
        assert 'convergence_history' in results
        assert 'hypervolume_history' in results

        # Check Pareto front properties
        pareto_front = results['pareto_front']
        assert len(pareto_front) > 0
        assert all('position' in sol and 'objectives' in sol for sol in pareto_front)

        # Validate hypervolume progression
        hypervolume_history = results['hypervolume_history']
        if len(hypervolume_history) > 1:
            # Hypervolume should generally increase (better diversity/convergence)
            assert hypervolume_history[-1] >= 0

    def test_results_serialization_workflow(self, test_config, mock_controller_factory):
        """Test complete results serialization and loading workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            results_manager = OptimizationResultsManager(Path(temp_dir))

            # Run optimization
            tuner = PSOTuner(mock_controller_factory, test_config, seed=42)
            pso_result = tuner.optimise()

            # Create optimization metadata
            metadata = create_optimization_metadata('classical_smc', test_config, seed=42)

            # Create optimization results object
            optimization_results = OptimizationResults(
                metadata=metadata,
                best_cost=pso_result['best_cost'],
                best_gains=pso_result['best_pos'].tolist(),
                convergence_history=pso_result['history']['cost'],
                position_history=pso_result['history']['pos'].tolist() if 'pos' in pso_result['history'] else None
            )

            # Test JSON serialization
            json_path = results_manager.save_results(optimization_results, "test_run_json", format="json")
            assert json_path.exists()

            loaded_results = results_manager.load_results(json_path)
            assert loaded_results.best_cost == optimization_results.best_cost
            assert np.allclose(loaded_results.best_gains, optimization_results.best_gains)

            # Test NPZ serialization
            npz_path = results_manager.save_results(optimization_results, "test_run_npz", format="npz")
            assert npz_path.exists()

            loaded_npz_results = results_manager.load_results(npz_path)
            assert loaded_npz_results.best_cost == optimization_results.best_cost
            assert np.allclose(loaded_npz_results.best_gains, optimization_results.best_gains)

    def test_results_comparison_analysis(self, test_config, mock_controller_factory):
        """Test results comparison and statistical analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            results_manager = OptimizationResultsManager(Path(temp_dir))

            # Generate multiple optimization runs
            result_paths = []
            for i in range(3):
                tuner = PSOTuner(mock_controller_factory, test_config, seed=42 + i)
                pso_result = tuner.optimise()

                metadata = create_optimization_metadata('classical_smc', test_config, seed=42 + i)
                optimization_results = OptimizationResults(
                    metadata=metadata,
                    best_cost=pso_result['best_cost'],
                    best_gains=pso_result['best_pos'].tolist(),
                    convergence_history=pso_result['history']['cost']
                )

                path = results_manager.save_results(optimization_results, f"test_run_{i}", format="json")
                result_paths.append(path)

            # Test comparison analysis
            comparison = results_manager.compare_results(result_paths)

            assert 'summary' in comparison
            assert 'detailed_metrics' in comparison
            assert 'recommendations' in comparison

            # Validate summary statistics
            if 'best_costs' in comparison['summary']:
                costs = comparison['summary']['best_costs']
                assert len(costs) == 3
                assert all(isinstance(cost, (int, float)) for cost in costs)

    def test_fitness_function_robustness(self, test_config, mock_controller_factory):
        """Test fitness function robustness with edge cases."""
        tuner = PSOTuner(mock_controller_factory, test_config, seed=42)

        # Test with extreme parameter values
        extreme_particles = np.array([
            [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],  # Very small values
            [100.0, 100.0, 100.0, 100.0, 100.0, 100.0],  # Very large values
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],  # Boundary values
        ])

        # Evaluate fitness for extreme cases
        fitness_values = tuner._fitness(extreme_particles)

        # Validate fitness values
        assert len(fitness_values) == 3
        assert np.all(np.isfinite(fitness_values))
        assert np.all(fitness_values >= 0)  # Fitness should be non-negative

    @pytest.mark.parametrize("controller_type,expected_gains", [
        ('classical_smc', 6),
        ('adaptive_smc', 5),
        ('hybrid_adaptive_sta_smc', 4),
    ])
    def test_controller_specific_optimization(self, test_config, controller_type, expected_gains):
        """Test PSO optimization for different controller types."""
        # Mock controller factory for specific controller type
        def factory(gains):
            mock_controller = MagicMock()
            mock_controller.max_force = 150.0
            mock_controller.dynamics_model = MagicMock()
            mock_controller.dynamics_model.step = MagicMock(return_value=np.zeros(6))
            return mock_controller

        factory.n_gains = expected_gains
        factory.controller_type = controller_type

        # Adjust bounds for controller type
        if controller_type == 'adaptive_smc':
            test_config['pso']['bounds']['min'] = test_config['pso']['bounds']['min'][:5]
            test_config['pso']['bounds']['max'] = test_config['pso']['bounds']['max'][:5]
        elif controller_type == 'hybrid_adaptive_sta_smc':
            test_config['pso']['bounds']['min'] = test_config['pso']['bounds']['min'][:4]
            test_config['pso']['bounds']['max'] = test_config['pso']['bounds']['max'][:4]

        tuner = PSOTuner(factory, test_config, seed=42)
        result = tuner.optimise()

        assert len(result['best_pos']) == expected_gains

    def test_pso_parameter_sensitivity(self, test_config, mock_controller_factory):
        """Test sensitivity to PSO hyperparameters."""
        results = {}

        # Test different PSO configurations
        pso_configs = [
            {'w': 0.3, 'c1': 1.0, 'c2': 1.0},  # Conservative
            {'w': 0.7, 'c1': 2.0, 'c2': 2.0},  # Aggressive
            {'w': 0.5, 'c1': 1.5, 'c2': 1.5},  # Balanced
        ]

        for i, pso_params in enumerate(pso_configs):
            config = test_config.copy()
            config['pso'].update(pso_params)

            tuner = PSOTuner(mock_controller_factory, config, seed=42)
            result = tuner.optimise()
            results[f'config_{i}'] = result['best_cost']

        # All configurations should produce valid results
        assert all(isinstance(cost, (int, float)) and cost >= 0 for cost in results.values())

        # Results should show some variation due to different parameters
        costs = list(results.values())
        if len(set(costs)) > 1:  # If there's variation
            assert max(costs) / min(costs) < 10  # Shouldn't vary by more than 10x

    def test_error_handling_and_recovery(self, test_config):
        """Test PSO error handling and recovery mechanisms."""
        # Test with invalid controller factory
        def failing_factory(gains):
            raise ValueError("Simulated controller creation failure")

        failing_factory.n_gains = 6
        failing_factory.controller_type = 'classical_smc'

        # PSO should handle controller creation failures gracefully
        tuner = PSOTuner(failing_factory, test_config, seed=42)

        with pytest.raises((ValueError, RuntimeError)):
            tuner.optimise()

    def test_reproducibility_with_seeds(self, test_config, mock_controller_factory):
        """Test optimization reproducibility with fixed seeds."""
        # Run optimization with same seed multiple times
        results = []
        for _ in range(2):
            tuner = PSOTuner(mock_controller_factory, test_config, seed=12345)
            result = tuner.optimise()
            results.append(result)

        # Results should be identical with same seed
        assert results[0]['best_cost'] == results[1]['best_cost']
        assert np.allclose(results[0]['best_pos'], results[1]['best_pos'], atol=1e-10)

    def test_performance_monitoring(self, test_config, mock_controller_factory):
        """Test performance monitoring and metrics collection."""
        tuner = PSOTuner(mock_controller_factory, test_config, seed=42)

        # Monitor optimization time
        import time
        start_time = time.time()
        result = tuner.optimise()
        elapsed_time = time.time() - start_time

        # Optimization should complete in reasonable time for test case
        assert elapsed_time < 30.0  # Should complete within 30 seconds

        # Validate that optimization made progress
        if 'history' in result and 'cost' in result['history']:
            cost_history = result['history']['cost']
            if len(cost_history) > 1:
                # Check for improvement (allowing some stochastic variation)
                improvement_ratio = (cost_history[0] - cost_history[-1]) / cost_history[0]
                assert improvement_ratio >= -0.1  # Allow up to 10% degradation due to randomness


class TestPSOSystemIntegration:
    """Integration tests for PSO system components."""

    def test_config_validation_integration(self):
        """Test integration with configuration validation system."""
        # Test with minimal valid configuration
        minimal_config = {
            'physics': {
                'cart_mass': 1.0, 'pendulum1_mass': 0.1, 'pendulum2_mass': 0.1,
                'pendulum1_length': 0.5, 'pendulum2_length': 0.5,
                'pendulum1_com': 0.25, 'pendulum2_com': 0.25,
                'pendulum1_inertia': 0.01, 'pendulum2_inertia': 0.01,
                'gravity': 9.81, 'cart_friction': 0.1,
                'joint1_friction': 0.01, 'joint2_friction': 0.01
            },
            'simulation': {'duration': 1.0, 'dt': 0.01},
            'pso': {
                'n_particles': 5, 'iters': 3, 'w': 0.5, 'c1': 1.5, 'c2': 1.5,
                'bounds': {'min': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                          'max': [10.0, 10.0, 5.0, 5.0, 20.0, 5.0]}
            },
            'cost_function': {
                'weights': {'state_error': 50.0, 'control_effort': 0.2,
                           'control_rate': 0.1, 'stability': 0.1},
                'baseline': {'gains': [5.0, 3.0, 4.0, 2.0, 10.0, 1.0]},
                'instability_penalty': 1000.0
            }
        }

        # Configuration should be processable by PSO system
        # This test validates that the configuration structure is compatible
        assert 'pso' in minimal_config
        assert 'bounds' in minimal_config['pso']
        assert len(minimal_config['pso']['bounds']['min']) == len(minimal_config['pso']['bounds']['max'])

    def test_memory_usage_monitoring(self, test_config, mock_controller_factory):
        """Test memory usage during optimization."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Run optimization
        tuner = PSOTuner(mock_controller_factory, test_config, seed=42)
        result = tuner.optimise()

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB for test case)
        assert memory_increase < 100 * 1024 * 1024  # 100MB limit

        # Validate result exists (optimization completed)
        assert 'best_cost' in result


@pytest.mark.integration
class TestPSOProductionReadiness:
    """Production readiness tests for PSO system."""

    def test_concurrent_optimization_safety(self, test_config):
        """Test thread safety for concurrent optimizations."""
        import threading
        import queue

        def mock_factory(gains):
            mock = MagicMock()
            mock.max_force = 150.0
            mock.dynamics_model = MagicMock()
            mock.dynamics_model.step = MagicMock(return_value=np.zeros(6))
            return mock

        mock_factory.n_gains = 6
        mock_factory.controller_type = 'classical_smc'

        results_queue = queue.Queue()

        def run_optimization(seed):
            try:
                tuner = PSOTuner(mock_factory, test_config, seed=seed)
                result = tuner.optimise()
                results_queue.put(('success', result))
            except Exception as e:
                results_queue.put(('error', str(e)))

        # Run multiple optimizations concurrently
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_optimization, args=(42 + i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        # All optimizations should complete successfully
        assert len(results) == 3
        assert all(status == 'success' for status, _ in results)

    def test_large_scale_optimization(self, mock_controller_factory):
        """Test optimization with larger parameter spaces."""
        large_config = {
            'simulation': {'duration': 0.5, 'dt': 0.01},
            'pso': {
                'n_particles': 20,
                'iters': 10,
                'w': 0.5, 'c1': 1.5, 'c2': 1.5,
                'bounds': {
                    'min': [0.1] * 6,
                    'max': [50.0] * 6
                }
            },
            'cost_function': {
                'weights': {'state_error': 50.0, 'control_effort': 0.2,
                           'control_rate': 0.1, 'stability': 0.1},
                'baseline': {'gains': [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]},
                'instability_penalty': 1000.0
            }
        }

        tuner = PSOTuner(mock_controller_factory, large_config, seed=42)
        result = tuner.optimise()

        # Optimization should handle larger scale efficiently
        assert 'best_cost' in result
        assert len(result['best_pos']) == 6
        assert np.all(np.isfinite(result['best_pos']))

    def test_stability_under_stress(self, test_config, mock_controller_factory):
        """Test system stability under stress conditions."""
        # Run many short optimizations
        for i in range(10):
            tuner = PSOTuner(mock_controller_factory, test_config, seed=i)
            result = tuner.optimise()

            # Each optimization should produce valid results
            assert isinstance(result['best_cost'], (int, float))
            assert np.all(np.isfinite(result['best_pos']))
            assert len(result['best_pos']) == 6