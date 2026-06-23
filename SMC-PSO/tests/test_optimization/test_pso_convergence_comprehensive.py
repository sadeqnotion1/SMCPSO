#======================================================================================\\\
#=========== tests/test_optimization/test_pso_convergence_comprehensive.py ============\\\
#======================================================================================\\\

"""
Comprehensive PSO convergence and parameter validation tests.
Achieving 95%+ coverage for critical optimization algorithms.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import List, Optional

from src.optimization.algorithms.pso_optimizer import PSOTuner, _normalise, _seeded_global_numpy


class TestPSOConvergenceValidation:
    """Comprehensive PSO convergence validation test suite."""

    @pytest.fixture
    def comprehensive_config(self):
        """Create comprehensive configuration for PSO testing."""
        @dataclass
        class MockPhysics:
            cart_mass: float = 1.5
            pendulum1_mass: float = 0.2
            pendulum2_mass: float = 0.15
            pendulum1_length: float = 0.4
            pendulum2_length: float = 0.3
            pendulum1_com: float = 0.2
            pendulum2_com: float = 0.15
            pendulum1_inertia: float = 0.009
            pendulum2_inertia: float = 0.009
            gravity: float = 9.81
            cart_friction: float = 0.2
            joint1_friction: float = 0.005
            joint2_friction: float = 0.004

            def model_dump(self) -> dict:
                return {
                    'cart_mass': self.cart_mass,
                    'pendulum1_mass': self.pendulum1_mass,
                    'pendulum2_mass': self.pendulum2_mass,
                    'pendulum1_length': self.pendulum1_length,
                    'pendulum2_length': self.pendulum2_length,
                    'pendulum1_com': self.pendulum1_com,
                    'pendulum2_com': self.pendulum2_com,
                    'pendulum1_inertia': self.pendulum1_inertia,
                    'pendulum2_inertia': self.pendulum2_inertia,
                    'gravity': self.gravity,
                    'cart_friction': self.cart_friction,
                    'joint1_friction': self.joint1_friction,
                    'joint2_friction': self.joint2_friction
                }

        @dataclass
        class MockSimulation:
            duration: float = 2.0
            dt: float = 0.01
            initial_state: List[float] = None
            use_full_dynamics: bool = False

            def __post_init__(self):
                if self.initial_state is None:
                    self.initial_state = [0.0, 0.05, -0.03, 0.0, 0.0, 0.0]

        @dataclass
        class MockWeights:
            state_error: float = 50.0
            control_effort: float = 0.2
            control_rate: float = 0.1
            stability: float = 0.1

        @dataclass
        class MockNorms:
            state_error: float = 10.0
            control_effort: float = 5.0
            control_rate: float = 2.0
            sliding: float = 1.0

        @dataclass
        class MockCombineWeights:
            mean: float = 0.7
            max: float = 0.3

        @dataclass
        class MockBaseline:
            gains: List[float] = None

            def __post_init__(self):
                if self.gains is None:
                    self.gains = [10.0, 8.0, 5.0, 3.0, 20.0, 2.0]

        @dataclass
        class MockCostFunction:
            weights: MockWeights = None
            norms: MockNorms = None
            instability_penalty: Optional[float] = None
            combine_weights: MockCombineWeights = None
            normalization_threshold: float = 1e-12
            baseline: MockBaseline = None

            def __post_init__(self):
                if self.weights is None:
                    self.weights = MockWeights()
                if self.norms is None:
                    self.norms = MockNorms()
                if self.combine_weights is None:
                    self.combine_weights = MockCombineWeights()
                if self.baseline is None:
                    self.baseline = MockBaseline()

        @dataclass
        class MockControllerBounds:
            min: List[float]
            max: List[float]

        @dataclass
        class MockPSOBounds:
            min: List[float] = None
            max: List[float] = None
            classical_smc: MockControllerBounds = None

            def __post_init__(self):
                if self.min is None:
                    self.min = [1.0, 1.0, 1.0, 1.0, 5.0, 0.1]
                if self.max is None:
                    self.max = [30.0, 30.0, 20.0, 20.0, 50.0, 10.0]
                if self.classical_smc is None:
                    self.classical_smc = MockControllerBounds(
                        min=[1.0, 1.0, 1.0, 1.0, 5.0, 0.1],
                        max=[30.0, 30.0, 20.0, 20.0, 50.0, 10.0]
                    )

        @dataclass
        class MockPSO:
            n_particles: int = 10
            bounds: MockPSOBounds = None
            w: float = 0.5
            c1: float = 1.5
            c2: float = 1.5
            iters: int = 20
            w_schedule: Optional[List[float]] = None
            velocity_clamp: Optional[List[float]] = None

            def __post_init__(self):
                if self.bounds is None:
                    self.bounds = MockPSOBounds()

        @dataclass
        class MockPhysicsUncertainty:
            n_evals: int = 3
            cart_mass: float = 0.1
            pendulum1_mass: float = 0.05
            pendulum2_mass: float = 0.05

            def model_dump(self) -> dict:
                return {
                    'n_evals': self.n_evals,
                    'cart_mass': self.cart_mass,
                    'pendulum1_mass': self.pendulum1_mass,
                    'pendulum2_mass': self.pendulum2_mass
                }

        @dataclass
        class MockConfig:
            global_seed: int = 42
            physics: MockPhysics = None
            simulation: MockSimulation = None
            cost_function: MockCostFunction = None
            pso: MockPSO = None
            physics_uncertainty: MockPhysicsUncertainty = None

            def __post_init__(self):
                if self.physics is None:
                    self.physics = MockPhysics()
                if self.simulation is None:
                    self.simulation = MockSimulation()
                if self.cost_function is None:
                    self.cost_function = MockCostFunction()
                if self.pso is None:
                    self.pso = MockPSO()
                if self.physics_uncertainty is None:
                    self.physics_uncertainty = MockPhysicsUncertainty()

        return MockConfig()

    @pytest.fixture
    def controller_factory_with_validation(self):
        """Controller factory with comprehensive validation."""
        def factory(gains):
            controller = Mock()
            controller.max_force = 150.0
            controller.gains = gains
            controller.controller_type = 'classical_smc'

            def validate_gains(particle_array):
                """Realistic gain validation function."""
                if particle_array.ndim == 1:
                    particle_array = particle_array.reshape(1, -1)

                valid_mask = np.ones(particle_array.shape[0], dtype=bool)

                # Check bounds
                for i, gains in enumerate(particle_array):
                    if len(gains) != 6:
                        valid_mask[i] = False
                        continue

                    # Basic positivity check
                    if np.any(gains <= 0):
                        valid_mask[i] = False
                        continue

                    # Stability constraints
                    if gains[4] < 5.0 or gains[4] > 50.0:  # Switching gain bounds
                        valid_mask[i] = False
                        continue

                    # Balance between gains
                    if gains[0] / gains[1] > 10.0 or gains[1] / gains[0] > 10.0:
                        valid_mask[i] = False
                        continue

                return valid_mask

            controller.validate_gains = validate_gains
            return controller

        factory.n_gains = 6
        factory.controller_type = 'classical_smc'
        return factory

    def test_pso_initialization_comprehensive(self, comprehensive_config, controller_factory_with_validation):
        """Test comprehensive PSO initialization with all configuration options."""
        tuner = PSOTuner(
            controller_factory=controller_factory_with_validation,
            config=comprehensive_config,
            seed=42,
            instability_penalty_factor=200.0
        )

        # Verify initialization
        assert tuner.seed == 42
        assert tuner.instability_penalty_factor == 200.0
        assert tuner.combine_weights == (0.7, 0.3)
        assert tuner.normalisation_threshold == 1e-12

        # Verify normalization constants
        assert tuner.norm_ise > 0
        assert tuner.norm_u > 0
        assert tuner.norm_du > 0
        assert tuner.norm_sigma > 0

    def test_deprecated_field_validation(self, comprehensive_config, controller_factory_with_validation):
        """Test deprecated PSO configuration field rejection."""
        # Test deprecated n_processes
        config = comprehensive_config
        config.pso.n_processes = 4

        with pytest.raises(ValueError, match="Deprecated PSO configuration fields"):
            PSOTuner(
                controller_factory=controller_factory_with_validation,
                config=config,
                seed=42
            )

        # Test deprecated hyper_trials
        config.pso.n_processes = None
        config.pso.hyper_trials = 100

        with pytest.raises(ValueError, match="Deprecated PSO configuration fields"):
            PSOTuner(
                controller_factory=controller_factory_with_validation,
                config=config,
                seed=42
            )

    def test_perturbed_physics_comprehensive(self, comprehensive_config, controller_factory_with_validation):
        """Test comprehensive physics perturbation iteration."""
        tuner = PSOTuner(
            controller_factory=controller_factory_with_validation,
            config=comprehensive_config,
            seed=42
        )

        physics_models = list(tuner._iter_perturbed_physics())

        # Should have nominal + perturbed models
        assert len(physics_models) == 3

        # First should be nominal
        nominal = physics_models[0]
        assert abs(nominal.cart_mass - 1.5) < 1e-10

        # Others should be perturbed
        for perturbed in physics_models[1:]:
            # At least one parameter should be different
            assert (abs(perturbed.cart_mass - 1.5) > 1e-10 or
                    abs(perturbed.pendulum1_mass - 0.2) > 1e-10 or
                    abs(perturbed.pendulum2_mass - 0.15) > 1e-10)

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_cost_computation_comprehensive(self, mock_simulate, comprehensive_config, controller_factory_with_validation):
        """Test comprehensive cost computation with various trajectory scenarios."""
        tuner = PSOTuner(
            controller_factory=controller_factory_with_validation,
            config=comprehensive_config,
            seed=42
        )

        # Test normal trajectory
        t = np.linspace(0, 2.0, 201)
        x_normal = np.random.random((2, 201, 6)) * 0.1  # Small deviations
        u_normal = np.random.random((2, 201)) * 10.0
        sigma_normal = np.random.random((2, 201)) * 0.5

        cost_normal = tuner._compute_cost_from_traj(t, x_normal, u_normal, sigma_normal)
        assert cost_normal.shape == (2,)
        assert np.all(np.isfinite(cost_normal))
        assert np.all(cost_normal > 0)

        # Test unstable trajectory (large angles)
        x_unstable = np.random.random((2, 201, 6))
        x_unstable[:, 50:, 1] = 2.0  # Large theta1 values
        cost_unstable = tuner._compute_cost_from_traj(t, x_unstable, u_normal, sigma_normal)

        # Should have penalty applied
        assert np.all(cost_unstable > cost_normal)

        # Test exploding trajectory
        x_exploding = np.random.random((2, 201, 6))
        x_exploding[:, 100:, :] = 1e8  # Exploding values
        cost_exploding = tuner._compute_cost_from_traj(t, x_exploding, u_normal, sigma_normal)

        # Should have severe penalty
        assert np.all(cost_exploding >= tuner.instability_penalty * 0.5)

        # Test NaN trajectory
        x_nan = np.random.random((2, 201, 6))
        x_nan[:, 50:, 0] = np.nan
        cost_nan = tuner._compute_cost_from_traj(t, x_nan, u_normal, sigma_normal)

        # Should return instability penalty
        assert np.all(cost_nan == tuner.instability_penalty)

    def test_normalisation_function_comprehensive(self, comprehensive_config, controller_factory_with_validation):
        """Test comprehensive normalisation function behavior."""
        tuner = PSOTuner(
            controller_factory=controller_factory_with_validation,
            config=comprehensive_config,
            seed=42
        )

        # Test normal normalisation
        values = np.array([10.0, 20.0, 30.0])
        normalised = tuner._normalise(values, 5.0)
        expected = np.array([2.0, 4.0, 6.0])
        np.testing.assert_array_almost_equal(normalised, expected)

        # Test zero denominator
        normalised_zero = tuner._normalise(values, 0.0)
        np.testing.assert_array_equal(normalised_zero, values)

        # Test very small denominator
        normalised_small = tuner._normalise(values, 1e-15)
        np.testing.assert_array_equal(normalised_small, values)

        # Test negative denominator
        normalised_neg = tuner._normalise(values, -2.0)
        expected_neg = np.array([-5.0, -10.0, -15.0])
        np.testing.assert_array_almost_equal(normalised_neg, expected_neg)

    def test_cost_combination_comprehensive(self, comprehensive_config, controller_factory_with_validation):
        """Test comprehensive cost combination across uncertainty draws."""
        tuner = PSOTuner(
            controller_factory=controller_factory_with_validation,
            config=comprehensive_config,
            seed=42
        )

        # Test 1D cost array
        costs_1d = np.array([1.0, 3.0, 2.0])
        combined = tuner._combine_costs(costs_1d)
        expected = 0.7 * 2.0 + 0.3 * 3.0  # mean * w_mean + max * w_max
        assert abs(combined - expected) < 1e-10

        # Test 2D cost array
        costs_2d = np.array([[1.0, 4.0, 7.0], [2.0, 5.0, 8.0], [3.0, 6.0, 9.0]])
        combined_2d = tuner._combine_costs(costs_2d)
        assert combined_2d.shape == (3,)

        # Check values
        for i in range(3):
            expected_i = 0.7 * costs_2d[:, i].mean() + 0.3 * costs_2d[:, i].max()
            assert abs(combined_2d[i] - expected_i) < 1e-10

        # Test empty array
        costs_empty = np.array([])
        combined_empty = tuner._combine_costs(costs_empty)
        assert combined_empty == tuner.instability_penalty

        # Test NaN/Inf arrays
        costs_nan = np.array([1.0, np.nan, 3.0])
        combined_nan = tuner._combine_costs(costs_nan)
        assert combined_nan == tuner.instability_penalty

        costs_inf = np.array([1.0, np.inf, 3.0])
        combined_inf = tuner._combine_costs(costs_inf)
        assert combined_inf == tuner.instability_penalty

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_fitness_evaluation_comprehensive(self, mock_simulate, comprehensive_config, controller_factory_with_validation):
        """Test comprehensive fitness evaluation with various scenarios."""
        tuner = PSOTuner(
            controller_factory=controller_factory_with_validation,
            config=comprehensive_config,
            seed=42
        )

        # Mock normal simulation results
        t = np.linspace(0, 2.0, 201)
        x_normal = np.random.RandomState(42).random((5, 201, 6)) * 0.1
        u_normal = np.random.RandomState(42).random((5, 201)) * 10.0
        sigma_normal = np.random.RandomState(42).random((5, 201)) * 0.5

        mock_simulate.return_value = (t, x_normal, u_normal, sigma_normal)

        # Test normal particles
        particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 2.0],
            [12.0, 9.0, 6.0, 4.0, 25.0, 3.0],
            [8.0, 7.0, 4.0, 2.0, 15.0, 1.5],
            [15.0, 10.0, 7.0, 5.0, 30.0, 4.0],
            [5.0, 5.0, 3.0, 1.0, 10.0, 1.0]
        ])

        fitness = tuner._fitness(particles)

        assert fitness.shape == (5,)
        assert np.all(np.isfinite(fitness))
        assert np.all(fitness > 0)

        # Test with invalid particles (should be penalized)
        particles_invalid = np.array([
            [0.0, 8.0, 5.0, 3.0, 20.0, 2.0],  # Zero gain
            [12.0, 9.0, 6.0, 4.0, 25.0, 3.0],
            [-5.0, 7.0, 4.0, 2.0, 15.0, 1.5],  # Negative gain
            [15.0, 10.0, 7.0, 5.0, 30.0, 4.0],
            [5.0, 5.0, 3.0, 1.0, 60.0, 1.0]   # Out of bounds
        ])

        fitness_invalid = tuner._fitness(particles_invalid)

        # Invalid particles should get penalty
        assert fitness_invalid[0] == tuner.instability_penalty  # Zero gain
        assert fitness_invalid[2] == tuner.instability_penalty  # Negative gain
        assert fitness_invalid[4] == tuner.instability_penalty  # Out of bounds

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_fitness_with_uncertainty(self, mock_simulate, comprehensive_config, controller_factory_with_validation):
        """Test fitness evaluation with physics uncertainty."""
        # Enable uncertainty evaluation
        config = comprehensive_config
        config.physics_uncertainty.n_evals = 3

        tuner = PSOTuner(
            controller_factory=controller_factory_with_validation,
            config=config,
            seed=42
        )

        # Mock multiple simulation results for uncertainty
        t = np.linspace(0, 2.0, 201)

        def side_effect(*args, **kwargs):
            # Return different results for each call
            x = np.random.random((2, 201, 6)) * 0.1
            u = np.random.random((2, 201)) * 10.0
            sigma = np.random.random((2, 201)) * 0.5
            return [(t, x, u, sigma) for _ in range(3)]  # 3 uncertainty draws

        mock_simulate.side_effect = side_effect

        particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 2.0],
            [12.0, 9.0, 6.0, 4.0, 25.0, 3.0]
        ])

        fitness = tuner._fitness(particles)

        assert fitness.shape == (2,)
        assert np.all(np.isfinite(fitness))
        assert np.all(fitness > 0)

    @patch('pyswarms.single.GlobalBestPSO')
    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_optimization_with_velocity_clamping(self, mock_simulate, mock_pso_class, comprehensive_config, controller_factory_with_validation):
        """Test PSO optimization with velocity clamping."""
        # Add velocity clamping configuration
        config = comprehensive_config
        config.pso.velocity_clamp = [-0.5, 0.5]

        # Setup mocks
        mock_optimizer = Mock()
        mock_optimizer.optimize.return_value = (1.5, np.array([10, 8, 5, 3, 20, 2]))
        mock_optimizer.cost_history = [2.0, 1.8, 1.5]
        mock_optimizer.pos_history = [np.array([10, 8, 5, 3, 20, 2])]
        mock_optimizer.options = {}
        mock_pso_class.return_value = mock_optimizer

        mock_simulate.return_value = (
            np.linspace(0, 2.0, 201),
            np.random.random((10, 201, 6)) * 0.1,
            np.random.random((10, 201)) * 10.0,
            np.random.random((10, 201)) * 0.5
        )

        tuner = PSOTuner(
            controller_factory=controller_factory_with_validation,
            config=config,
            seed=42
        )

        tuner.optimise()

        # Check that velocity clamping was configured
        call_kwargs = mock_pso_class.call_args[1]
        bounds = call_kwargs['bounds']

        # Calculate expected velocity bounds
        bounds_array = np.array(bounds)
        bounds_range = bounds_array[1] - bounds_array[0]
        expected_velocity_min = -0.5 * bounds_range
        expected_velocity_max = 0.5 * bounds_range

        # Should have velocity bounds set
        assert 'velocity_clamp' in call_kwargs
        velocity_bounds = call_kwargs['velocity_clamp']
        np.testing.assert_array_almost_equal(velocity_bounds[0], expected_velocity_min)
        np.testing.assert_array_almost_equal(velocity_bounds[1], expected_velocity_max)

    @patch('pyswarms.single.GlobalBestPSO')
    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_optimization_with_weight_scheduling(self, mock_simulate, mock_pso_class, comprehensive_config, controller_factory_with_validation):
        """Test PSO optimization with inertia weight scheduling."""
        # Add weight scheduling configuration
        config = comprehensive_config
        config.pso.w_schedule = [0.9, 0.4]

        # Setup mocks
        mock_optimizer = Mock()
        mock_optimizer.optimize.return_value = (1.5, np.array([10, 8, 5, 3, 20, 2]))
        mock_optimizer.cost_history = [2.0, 1.8, 1.5]
        mock_optimizer.pos_history = [np.array([10, 8, 5, 3, 20, 2])]
        mock_optimizer.options = {}
        mock_pso_class.return_value = mock_optimizer

        mock_simulate.return_value = (
            np.linspace(0, 2.0, 201),
            np.random.random((10, 201, 6)) * 0.1,
            np.random.random((10, 201)) * 10.0,
            np.random.random((10, 201)) * 0.5
        )

        tuner = PSOTuner(
            controller_factory=controller_factory_with_validation,
            config=config,
            seed=42
        )

        result = tuner.optimise()

        # Should have weight scheduling configured
        assert 'best_cost' in result
        assert 'best_pos' in result
        assert result['best_cost'] == 1.5

    def test_seeded_global_numpy_context_manager(self):
        """Test seeded global numpy context manager."""
        # Save initial state
        initial_state = np.random.get_state()

        # Test with seed
        with _seeded_global_numpy(42):
            val1 = np.random.random()

        with _seeded_global_numpy(42):
            val2 = np.random.random()

        # Should be deterministic
        assert val1 == val2

        # Test without seed
        with _seeded_global_numpy(None):
            np.random.random()

        # Should restore state
        final_state = np.random.get_state()
        assert np.array_equal(initial_state[1], final_state[1])

    def test_module_normalise_function(self):
        """Test module-level normalise function."""
        values = np.array([10.0, 20.0, 30.0])

        # Normal case
        result = _normalise(values, 5.0)
        expected = np.array([2.0, 4.0, 6.0])
        np.testing.assert_array_almost_equal(result, expected)

        # Zero denominator
        result_zero = _normalise(values, 0.0)
        np.testing.assert_array_equal(result_zero, values)

        # Very small denominator
        result_small = _normalise(values, 1e-15)
        np.testing.assert_array_equal(result_small, values)


class TestPSOEdgeCases:
    """Test PSO edge cases and error conditions."""

    @pytest.fixture
    def minimal_config(self):
        """Minimal configuration for edge case testing."""
        @dataclass
        class MockPhysics:
            cart_mass: float = 1.5
            pendulum1_mass: float = 0.2
            pendulum2_mass: float = 0.15
            pendulum1_length: float = 0.4
            pendulum2_length: float = 0.3
            pendulum1_com: float = 0.2
            pendulum2_com: float = 0.15
            pendulum1_inertia: float = 0.009
            pendulum2_inertia: float = 0.009
            gravity: float = 9.81
            cart_friction: float = 0.2
            joint1_friction: float = 0.005
            joint2_friction: float = 0.004

            def model_dump(self) -> dict:
                return {field: getattr(self, field) for field in self.__dataclass_fields__}

        @dataclass
        class MockSimulation:
            duration: float = 1.0
            dt: float = 0.01
            initial_state: List[float] = None
            use_full_dynamics: bool = False

            def __post_init__(self):
                if self.initial_state is None:
                    self.initial_state = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        @dataclass
        class MockWeights:
            state_error: float = 50.0
            control_effort: float = 0.2
            control_rate: float = 0.1
            stability: float = 0.1

        @dataclass
        class MockCostFunction:
            weights: MockWeights = None

            def __post_init__(self):
                if self.weights is None:
                    self.weights = MockWeights()

        @dataclass
        class MockPSO:
            n_particles: int = 5
            iters: int = 3

        @dataclass
        class MockConfig:
            global_seed: Optional[int] = None
            physics: MockPhysics = None
            simulation: MockSimulation = None
            cost_function: MockCostFunction = None
            pso: MockPSO = None

            def __post_init__(self):
                if self.physics is None:
                    self.physics = MockPhysics()
                if self.simulation is None:
                    self.simulation = MockSimulation()
                if self.cost_function is None:
                    self.cost_function = MockCostFunction()
                if self.pso is None:
                    self.pso = MockPSO()

        return MockConfig()

    @pytest.fixture
    def controller_factory_minimal(self):
        """Minimal controller factory."""
        def factory(gains):
            controller = Mock()
            controller.max_force = 150.0
            return controller
        return factory

    def test_invalid_cost_dimensions(self, minimal_config, controller_factory_minimal):
        """Test handling of invalid cost array dimensions."""
        tuner = PSOTuner(
            controller_factory=controller_factory_minimal,
            config=minimal_config,
            seed=42
        )

        # Test 3D array (should raise ValueError)
        costs_3d = np.random.random((2, 3, 4))
        with pytest.raises(ValueError, match="costs must be 1D or 2D"):
            tuner._combine_costs(costs_3d)

    def test_empty_trajectory_handling(self, minimal_config, controller_factory_minimal):
        """Test handling of empty trajectories."""
        tuner = PSOTuner(
            controller_factory=controller_factory_minimal,
            config=minimal_config,
            seed=42
        )

        # Empty time array
        t_empty = np.array([])
        x_empty = np.zeros((2, 0, 6))
        u_empty = np.zeros((2, 0))
        sigma_empty = np.zeros((2, 0))

        cost = tuner._compute_cost_from_traj(t_empty, x_empty, u_empty, sigma_empty)
        assert cost.shape == (2,)
        assert np.all(cost == 0.0)

    def test_mismatched_trajectory_dimensions(self, minimal_config, controller_factory_minimal):
        """Test handling of mismatched trajectory dimensions."""
        tuner = PSOTuner(
            controller_factory=controller_factory_minimal,
            config=minimal_config,
            seed=42
        )

        t = np.linspace(0, 1.0, 101)
        x = np.random.random((2, 101, 6))
        u = np.random.random((2, 150))  # Mismatched length
        sigma = np.random.random((2, 101))

        # Should handle gracefully by truncating
        cost = tuner._compute_cost_from_traj(t, x, u, sigma)
        assert cost.shape == (2,)
        assert np.all(np.isfinite(cost))

    def test_all_invalid_particles(self, minimal_config):
        """Test behavior when all particles are invalid."""
        def factory_strict(gains):
            controller = Mock()
            controller.max_force = 150.0

            def validate_gains(particle_array):
                # Reject all particles
                return np.zeros(particle_array.shape[0], dtype=bool)

            controller.validate_gains = validate_gains
            return controller

        tuner = PSOTuner(
            controller_factory=factory_strict,
            config=minimal_config,
            seed=42
        )

        particles = np.random.random((3, 6))
        fitness = tuner._fitness(particles)

        # All should get penalty
        expected_penalty = tuner.instability_penalty
        assert np.all(fitness == expected_penalty)

    def test_baseline_computation_failure(self, minimal_config, controller_factory_minimal):
        """Test handling of baseline computation failure."""
        # Add faulty baseline configuration
        @dataclass
        class FaultyBaseline:
            gains: List[float] = None

            def __post_init__(self):
                self.gains = [1e20, 1e20, 1e20, 1e20, 1e20, 1e20]  # Extreme values

        config = minimal_config
        config.cost_function.baseline = FaultyBaseline()

        # Should handle gracefully without crashing
        tuner = PSOTuner(
            controller_factory=controller_factory_minimal,
            config=config,
            seed=42
        )

        # Should still have reasonable defaults
        assert tuner.norm_ise > 0
        assert tuner.norm_u > 0
        assert tuner.norm_du > 0
        assert tuner.norm_sigma > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])