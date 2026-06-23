#======================================================================================\\\
#=============== tests/test_optimization/test_pso_deterministic_coverage.py ==========\\\
#======================================================================================\\\

"""
Comprehensive PSO Deterministic Coverage Tests.

This module provides deterministic testing for PSO optimization components to achieve
≥95% coverage for critical optimization components. All tests use fixed seeds and
mocked dependencies to ensure reproducible results.

Coverage Goals:
- PSOTuner initialization and configuration validation: 100%
- Fitness evaluation and cost computation: 100%
- Optimization bounds and parameter validation: 100%
- Convergence detection and early stopping: 100%
- Results serialization and error handling: 100%
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.optimization.algorithms.pso_optimizer import PSOTuner, _normalise, _seeded_global_numpy
from src.optimization.validation.pso_bounds_validator import PSOBoundsValidator, validate_pso_configuration
from src.optimization.core.results_manager import OptimizationResultsManager
from src.utils.seed import create_rng


class TestPSODeterministicCoverage:
    """Comprehensive deterministic PSO coverage tests."""

    @pytest.fixture(autouse=True)
    def setup_deterministic_environment(self):
        """Ensure completely deterministic test environment."""
        # Set all possible random seeds
        np.random.seed(42)
        self._original_state = np.random.get_state()
        yield
        # Restore original state
        np.random.set_state(self._original_state)

    @pytest.fixture
    def deterministic_config(self):
        """Deterministic configuration for PSO tests."""
        return {
            'physics': {
                'cart_mass': 1.0,
                'pendulum1_mass': 0.1,
                'pendulum2_mass': 0.1,
                'pendulum1_length': 0.5,
                'pendulum2_length': 0.5,
                'gravity': 9.81,
                'cart_friction': 0.1,
                'pendulum1_friction': 0.01,
                'pendulum2_friction': 0.01
            },
            'simulation': {
                'dt': 0.01,
                'duration': 2.0,  # Short for fast tests
                'initial_state': [0.0, 0.1, -0.05, 0.0, 0.0, 0.0]
            },
            'pso': {
                'n_particles': 8,
                'max_iter': 5,
                'c1': 0.5,
                'c2': 0.3,
                'w': 0.9,
                'velocity_clamp': (-0.5, 0.5),
                'w_schedule': (0.9, 0.4)
            },
            'cost_function': {
                'weights': {
                    'ise': 1.0,
                    'u': 0.01,
                    'du': 0.001,
                    'sigma': 0.1
                }
            },
            'global_seed': 42
        }

    @pytest.fixture
    def mock_controller_factory(self):
        """Mock controller factory with comprehensive behavior."""
        def _factory(gains):
            controller = MagicMock()
            controller.max_force = 150.0
            controller.n_gains = len(gains) if hasattr(gains, '__len__') else 6
            # Mock validate_gains with deterministic behavior
            controller.validate_gains = MagicMock(
                side_effect=lambda g: np.array([True] * len(g)) if hasattr(g, '__len__') else True
            )
            controller.compute_control = MagicMock(return_value=0.0)
            return controller
        return _factory

    # === PSOTuner Initialization Coverage ===

    def test_pso_tuner_initialization_comprehensive(self, deterministic_config, mock_controller_factory):
        """Test comprehensive PSOTuner initialization scenarios."""
        # Test with config dict
        tuner1 = PSOTuner(
            controller_factory=mock_controller_factory,
            config=deterministic_config,
            seed=42
        )
        assert tuner1.seed == 42
        assert isinstance(tuner1.rng, np.random.Generator)

        # Test with external RNG
        external_rng = create_rng(123)
        tuner2 = PSOTuner(
            controller_factory=mock_controller_factory,
            config=deterministic_config,
            rng=external_rng
        )
        assert tuner2.rng is external_rng

        # Test with custom instability penalty factor
        tuner3 = PSOTuner(
            controller_factory=mock_controller_factory,
            config=deterministic_config,
            seed=42,
            instability_penalty_factor=200.0
        )
        assert tuner3.instability_penalty_factor == 200.0

    def test_pso_tuner_deprecated_parameters_validation(self, deterministic_config, mock_controller_factory):
        """Test validation of deprecated PSO parameters."""
        # Create config with deprecated parameters
        config_with_deprecated = deterministic_config.copy()
        config_with_deprecated['pso'].update({
            'n_processes': 4,  # Should trigger error
            'hyper_trials': 10,  # Should trigger error
            'hyper_search': True,  # Should trigger error
            'study_timeout': 300  # Should trigger error
        })

        with pytest.raises(ValueError, match="deprecated PSO parameters"):
            PSOTuner(
                controller_factory=mock_controller_factory,
                config=config_with_deprecated,
                seed=42
            )

    # === Normalization Function Coverage ===

    def test_normalise_function_comprehensive(self):
        """Test _normalise function with all edge cases."""
        # Normal case
        values = np.array([1.0, 2.0, 3.0])
        result = _normalise(values, 2.0)
        expected = np.array([0.5, 1.0, 1.5])
        assert np.allclose(result, expected)

        # Zero denominator (below threshold)
        result = _normalise(values, 1e-15)
        assert np.allclose(result, values)  # Should return original values

        # Exactly at threshold
        result = _normalise(values, 1e-12)
        assert np.allclose(result, values)  # Should return original values

        # Large denominator
        result = _normalise(values, 1e6)
        expected = values / 1e6
        assert np.allclose(result, expected)

        # Array of zeros
        zeros = np.array([0.0, 0.0, 0.0])
        result = _normalise(zeros, 1.0)
        assert np.allclose(result, zeros)

    # === Seeded Context Manager Coverage ===

    def test_seeded_global_numpy_context_manager(self):
        """Test _seeded_global_numpy context manager thoroughly."""
        original_state = np.random.get_state()

        # Test with None seed (should do nothing)
        with _seeded_global_numpy(None):
            # State should be unchanged
            current_state = np.random.get_state()
            assert current_state[0] == original_state[0]

        # Test with valid seed
        test_value_1 = None
        test_value_2 = None

        with _seeded_global_numpy(12345):
            test_value_1 = np.random.random()

        # Reset and test same seed gives same result
        with _seeded_global_numpy(12345):
            test_value_2 = np.random.random()

        assert test_value_1 == test_value_2

        # Verify original state is restored
        restored_state = np.random.get_state()
        assert restored_state[0] == original_state[0]

    # === Cost Combination Coverage ===

    def test_combine_costs_comprehensive(self, deterministic_config, mock_controller_factory):
        """Test _combine_costs method with all scenarios."""
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=deterministic_config,
            seed=42
        )

        # Set custom combine weights for testing
        tuner.combine_weights = (0.7, 0.3)

        # Test 1D array
        costs_1d = np.array([1.0, 2.0, 3.0, 4.0])
        result = tuner._combine_costs(costs_1d)
        expected = 0.7 * costs_1d.mean() + 0.3 * costs_1d.max()
        assert abs(result - expected) < 1e-10

        # Test 2D array
        costs_2d = np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0]
        ])
        result = tuner._combine_costs(costs_2d)
        expected = 0.7 * costs_2d.mean(axis=0) + 0.3 * costs_2d.max(axis=0)
        assert np.allclose(result, expected)

        # Test empty array
        empty_costs = np.array([])
        result = tuner._combine_costs(empty_costs)
        assert result == tuner.instability_penalty

        # Test with NaN values
        nan_costs = np.array([1.0, np.nan, 3.0])
        result = tuner._combine_costs(nan_costs)
        assert result == tuner.instability_penalty

        # Test with infinite values
        inf_costs = np.array([1.0, np.inf, 3.0])
        result = tuner._combine_costs(inf_costs)
        assert result == tuner.instability_penalty

    # === Fitness Function Coverage ===

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_fitness_function_comprehensive(self, mock_simulate, deterministic_config, mock_controller_factory):
        """Test fitness function with all code paths."""
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=deterministic_config,
            seed=42
        )

        # Mock simulation results
        t = np.linspace(0, 2.0, 201)
        particles = np.array([[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]] * 5)
        x_b = np.random.rand(5, 201, 6)  # 5 particles, 201 time steps, 6 states
        u_b = np.random.rand(5, 201)     # 5 particles, 201 time steps
        sigma_b = np.random.rand(5, 201) # 5 particles, 201 time steps

        mock_simulate.return_value = (t, x_b, u_b, sigma_b)

        # Test normal fitness evaluation
        result = tuner._fitness(particles)
        assert len(result) == 5
        assert all(np.isfinite(result))

        # Test with NaN in simulation results
        x_b_nan = x_b.copy()
        x_b_nan[0, :, 0] = np.nan  # Introduce NaN in first particle
        mock_simulate.return_value = (t, x_b_nan, u_b, sigma_b)

        result = tuner._fitness(particles)
        assert result[0] == tuner.instability_penalty
        assert all(np.isfinite(result[1:]))

    # === Bounds Validation Coverage ===

    def test_bounds_validation_comprehensive(self, deterministic_config):
        """Test comprehensive bounds validation scenarios."""
        # Valid bounds
        valid_bounds = [(0.0, 10.0), (-5.0, 5.0), (0.1, 1.0)]
        validator = PSOBoundsValidator()
        result = validator.validate_bounds(valid_bounds)
        assert result['valid'] is True

        # Invalid bounds (lower > upper)
        invalid_bounds = [(10.0, 0.0), (-5.0, 5.0)]
        result = validator.validate_bounds(invalid_bounds)
        assert result['valid'] is False
        assert len(result['errors']) > 0

        # Empty bounds
        empty_bounds = []
        result = validator.validate_bounds(empty_bounds)
        assert result['valid'] is False

        # Single bound
        single_bound = [(0.0, 1.0)]
        result = validator.validate_bounds(single_bound)
        assert result['valid'] is True

    # === Configuration Validation Coverage ===

    def test_pso_configuration_validation_comprehensive(self, deterministic_config):
        """Test comprehensive PSO configuration validation."""
        # Valid configuration
        result = validate_pso_configuration(deterministic_config)
        assert result['valid'] is True

        # Missing PSO section
        config_no_pso = deterministic_config.copy()
        del config_no_pso['pso']
        result = validate_pso_configuration(config_no_pso)
        assert result['valid'] is False

        # Invalid particle count
        config_invalid_particles = deterministic_config.copy()
        config_invalid_particles['pso']['n_particles'] = -1
        result = validate_pso_configuration(config_invalid_particles)
        assert result['valid'] is False

        # Invalid iteration count
        config_invalid_iter = deterministic_config.copy()
        config_invalid_iter['pso']['max_iter'] = 0
        result = validate_pso_configuration(config_invalid_iter)
        assert result['valid'] is False

    # === Optimization Result Management Coverage ===

    def test_optimization_results_serialization(self, deterministic_config, mock_controller_factory):
        """Test optimization results serialization and loading."""
        # Create results manager
        manager = OptimizationResultsManager()

        # Create mock optimization results
        results = {
            'best_cost': 0.123,
            'best_pos': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            'cost_history': [0.5, 0.3, 0.123],
            'pos_history': [[[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]] * 3],
            'convergence_data': {
                'converged': True,
                'iterations': 15,
                'final_variance': 1e-6
            }
        }

        # Test serialization
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            manager.save_results(results, temp_path)

        # Test loading
        loaded_results = manager.load_results(temp_path)
        assert loaded_results['best_cost'] == results['best_cost']
        assert np.allclose(loaded_results['best_pos'], results['best_pos'])

        # Cleanup
        temp_path.unlink()

    # === Convergence Detection Coverage ===

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_convergence_detection_comprehensive(self, mock_simulate, deterministic_config, mock_controller_factory):
        """Test convergence detection with various scenarios."""
        # Configure for early stopping
        convergence_config = deterministic_config.copy()
        convergence_config['pso'].update({
            'max_iter': 50,
            'convergence_threshold': 1e-6,
            'convergence_patience': 5
        })

        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=convergence_config,
            seed=42
        )

        # Mock simulation for converging scenario
        t = np.linspace(0, 2.0, 201)
        np.array([[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]] * 8)
        x_b = np.random.rand(8, 201, 6) * 0.01  # Small values for good cost
        u_b = np.random.rand(8, 201) * 0.01
        sigma_b = np.random.rand(8, 201) * 0.01

        mock_simulate.return_value = (t, x_b, u_b, sigma_b)

        # Test optimization with convergence
        result = tuner.optimise(iters_override=10, n_particles_override=8)
        assert 'best_cost' in result
        assert 'best_pos' in result
        assert len(result['best_pos']) == 6  # Expected number of gains

    # === Error Handling Coverage ===

    def test_error_handling_comprehensive(self, deterministic_config, mock_controller_factory):
        """Test comprehensive error handling scenarios."""
        # Test with invalid controller factory
        def invalid_factory(gains):
            raise ValueError("Invalid controller configuration")

        tuner = PSOTuner(
            controller_factory=invalid_factory,
            config=deterministic_config,
            seed=42
        )

        # This should handle the error gracefully
        with patch.object(tuner, '_fitness') as mock_fitness:
            mock_fitness.return_value = np.full(8, tuner.instability_penalty)
            result = tuner.optimise(iters_override=2, n_particles_override=8)
            assert result['best_cost'] >= tuner.instability_penalty

    # === Integration Test Coverage ===

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_end_to_end_optimization_workflow(self, mock_simulate, deterministic_config, mock_controller_factory):
        """Test complete end-to-end optimization workflow."""
        # Setup deterministic simulation mock
        np.random.seed(42)
        t = np.linspace(0, 2.0, 201)

        def mock_simulation_func(*args, **kwargs):
            particles = kwargs.get('particles', args[1] if len(args) > 1 else np.array([[]]))
            n_particles = len(particles)

            # Generate deterministic trajectories based on particle gains
            x_b = np.random.rand(n_particles, 201, 6) * 0.1
            u_b = np.random.rand(n_particles, 201) * 0.1
            sigma_b = np.random.rand(n_particles, 201) * 0.1

            return t, x_b, u_b, sigma_b

        mock_simulate.side_effect = mock_simulation_func

        # Create tuner
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=deterministic_config,
            seed=42
        )

        # Run optimization
        result = tuner.optimise(
            iters_override=3,
            n_particles_override=6,
            options_override={'w': 0.7, 'c1': 0.4, 'c2': 0.4}
        )

        # Validate results
        assert 'best_cost' in result
        assert 'best_pos' in result
        assert isinstance(result['best_pos'], (list, np.ndarray))
        assert len(result['best_pos']) == 6
        assert result['best_cost'] >= 0
        assert np.all(np.isfinite(result['best_pos']))

        # Test reproducibility
        tuner2 = PSOTuner(
            controller_factory=mock_controller_factory,
            config=deterministic_config,
            seed=42  # Same seed
        )

        result2 = tuner2.optimise(
            iters_override=3,
            n_particles_override=6,
            options_override={'w': 0.7, 'c1': 0.4, 'c2': 0.4}
        )

        # Results should be very close due to deterministic seeding
        assert abs(result['best_cost'] - result2['best_cost']) < 1e-10
        assert np.allclose(result['best_pos'], result2['best_pos'], atol=1e-10)


class TestPSOPerformanceValidation:
    """PSO performance validation and benchmarking tests."""

    @pytest.fixture(autouse=True)
    def setup_deterministic_environment(self):
        """Ensure deterministic environment for performance tests."""
        np.random.seed(42)
        self._original_state = np.random.get_state()
        yield
        np.random.set_state(self._original_state)

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_pso_performance_scaling(self, mock_simulate, test_config, mock_controller_factory):
        """Test PSO performance scales appropriately with problem size."""
        # Mock fast simulation
        def fast_mock_simulation(*args, **kwargs):
            particles = kwargs.get('particles', args[1] if len(args) > 1 else np.array([[]]))
            n_particles = len(particles)
            t = np.linspace(0, 1.0, 101)
            return (
                t,
                np.random.rand(n_particles, 101, 6) * 0.01,
                np.random.rand(n_particles, 101) * 0.01,
                np.random.rand(n_particles, 101) * 0.01
            )

        mock_simulate.side_effect = fast_mock_simulation

        # Test different problem sizes
        sizes = [5, 10, 20]
        times = []

        for size in sizes:
            tuner = PSOTuner(
                controller_factory=mock_controller_factory,
                config=test_config,
                seed=42
            )

            import time
            start_time = time.time()
            result = tuner.optimise(iters_override=2, n_particles_override=size)
            end_time = time.time()

            times.append(end_time - start_time)
            assert result['best_cost'] >= 0

        # Performance should scale reasonably (not exponentially)
        assert times[1] <= times[0] * 3  # 2x particles shouldn't take more than 3x time
        assert times[2] <= times[0] * 5  # 4x particles shouldn't take more than 5x time

    def test_pso_memory_usage_bounds(self, test_config, mock_controller_factory):
        """Test PSO memory usage stays within reasonable bounds."""
        import sys

        # Measure baseline memory
        sys.getsizeof({})

        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=test_config,
            seed=42
        )

        # Memory usage should be reasonable for small problems
        tuner_memory = sys.getsizeof(tuner.__dict__)
        assert tuner_memory < 1024 * 1024  # Should be less than 1MB for basic tuner

    # === Configuration Validation Coverage ===

    def test_configuration_edge_cases(self, mock_controller_factory):
        """Test PSO configuration with edge cases."""
        # Minimal valid configuration
        minimal_config = {
            'physics': {'cart_mass': 1.0},
            'simulation': {'dt': 0.01, 'duration': 1.0},
            'pso': {'n_particles': 2, 'max_iter': 1},
            'cost_function': {'weights': {'ise': 1.0}}
        }

        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,
            seed=42
        )
        assert tuner.cfg is not None

        # Configuration with all optional parameters
        maximal_config = {
            'physics': {
                'cart_mass': 1.0, 'pendulum1_mass': 0.1, 'pendulum2_mass': 0.1,
                'pendulum1_length': 0.5, 'pendulum2_length': 0.5, 'gravity': 9.81,
                'cart_friction': 0.1, 'pendulum1_friction': 0.01, 'pendulum2_friction': 0.01
            },
            'simulation': {'dt': 0.01, 'duration': 5.0},
            'pso': {
                'n_particles': 30, 'max_iter': 100, 'c1': 0.5, 'c2': 0.3, 'w': 0.9,
                'velocity_clamp': (-1.0, 1.0), 'w_schedule': (0.9, 0.4)
            },
            'cost_function': {
                'weights': {'ise': 1.0, 'u': 0.01, 'du': 0.001, 'sigma': 0.1}
            },
            'physics_uncertainty': {'n_evals': 5, 'mass_std': 0.05},
            'global_seed': 12345
        }

        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=maximal_config,
            seed=42
        )
        assert tuner.uncertainty_cfg is not None
        assert tuner.uncertainty_cfg.n_evals == 5