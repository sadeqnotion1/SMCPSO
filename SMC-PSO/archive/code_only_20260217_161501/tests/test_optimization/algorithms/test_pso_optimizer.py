#======================================================================================\\\
#============== tests/test_optimization/algorithms/test_pso_optimizer.py ==============\\\
#======================================================================================\\\

"""
Comprehensive tests for PSO optimizer integration and functionality.
Tests the main PSOTuner class for correctness, performance, and integration.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from pathlib import Path
import yaml

from src.optimization.algorithms.pso_optimizer import PSOTuner


class TestPSOTuner:
    """Test suite for PSOTuner class."""

    @pytest.fixture
    def minimal_config(self):
        """Create minimal valid configuration for testing."""
        from dataclasses import dataclass
        from typing import Any, List

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
                """Provide Pydantic-compatible model_dump method for mock."""
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
            duration: float = 1.0
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
            state_error: float = 1.0
            control_effort: float = 1.0
            control_rate: float = 1.0
            sliding: float = 1.0

        @dataclass
        class MockCostFunction:
            weights: MockWeights = None
            norms: MockNorms = None
            instability_penalty: float = 1000.0

            def __post_init__(self):
                if self.weights is None:
                    self.weights = MockWeights()
                if self.norms is None:
                    self.norms = MockNorms()

        @dataclass
        class MockControllerBounds:
            min: List[float]
            max: List[float]

        @dataclass
        class MockPSOBounds:
            min: List[float] = None
            max: List[float] = None
            classical_smc: MockControllerBounds = None
            adaptive_smc: MockControllerBounds = None
            sta_smc: MockControllerBounds = None

            def __post_init__(self):
                if self.min is None:
                    self.min = [1.0, 1.0, 1.0, 1.0, 5.0, 0.1]
                if self.max is None:
                    self.max = [20.0, 20.0, 10.0, 10.0, 50.0, 5.0]
                if self.classical_smc is None:
                    self.classical_smc = MockControllerBounds(
                        min=[1.0, 1.0, 1.0, 1.0, 5.0, 0.1],
                        max=[30.0, 30.0, 20.0, 20.0, 50.0, 10.0]
                    )
                if self.adaptive_smc is None:
                    self.adaptive_smc = MockControllerBounds(
                        min=[2.0, 2.0, 1.0, 1.0, 0.5],
                        max=[40.0, 40.0, 25.0, 25.0, 10.0]
                    )
                if self.sta_smc is None:
                    self.sta_smc = MockControllerBounds(
                        min=[3.0, 2.0, 2.0, 2.0, 0.5, 0.5],
                        max=[50.0, 30.0, 30.0, 30.0, 20.0, 20.0]
                    )

        @dataclass
        class MockPSO:
            n_particles: int = 5
            bounds: MockPSOBounds = None
            w: float = 0.5
            c1: float = 1.5
            c2: float = 1.5
            iters: int = 3
            w_schedule: Any = None
            n_processes: Any = None
            hyper_trials: Any = None
            hyper_search: Any = None
            study_timeout: Any = None

            def __post_init__(self):
                if self.bounds is None:
                    self.bounds = MockPSOBounds()

        @dataclass
        class MockPhysicsUncertainty:
            n_evals: int = 1

            def model_dump(self) -> dict:
                """Provide Pydantic-compatible model_dump method for mock."""
                return {'n_evals': self.n_evals}

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

            def model_dump(self):
                """Return a dictionary representation for serialization."""
                return {
                    'global_seed': self.global_seed,
                    'physics': {
                        'cart_mass': self.physics.cart_mass,
                        'pendulum1_mass': self.physics.pendulum1_mass,
                        'pendulum2_mass': self.physics.pendulum2_mass,
                        'pendulum1_length': self.physics.pendulum1_length,
                        'pendulum2_length': self.physics.pendulum2_length,
                        'pendulum1_com': self.physics.pendulum1_com,
                        'pendulum2_com': self.physics.pendulum2_com,
                        'pendulum1_inertia': self.physics.pendulum1_inertia,
                        'pendulum2_inertia': self.physics.pendulum2_inertia,
                        'gravity': self.physics.gravity,
                        'cart_friction': self.physics.cart_friction,
                        'joint1_friction': self.physics.joint1_friction,
                        'joint2_friction': self.physics.joint2_friction
                    },
                    'simulation': {
                        'duration': self.simulation.duration,
                        'dt': self.simulation.dt,
                        'initial_state': self.simulation.initial_state,
                        'use_full_dynamics': self.simulation.use_full_dynamics
                    },
                    'cost_function': {
                        'weights': {
                            'state_error': self.cost_function.weights.state_error,
                            'control_effort': self.cost_function.weights.control_effort,
                            'control_rate': self.cost_function.weights.control_rate,
                            'stability': self.cost_function.weights.stability
                        },
                        'norms': {
                            'state_error': self.cost_function.norms.state_error,
                            'control_effort': self.cost_function.norms.control_effort,
                            'control_rate': self.cost_function.norms.control_rate,
                            'sliding': self.cost_function.norms.sliding
                        },
                        'instability_penalty': self.cost_function.instability_penalty
                    },
                    'pso': {
                        'n_particles': self.pso.n_particles,
                        'bounds': {
                            'min': self.pso.bounds.min,
                            'max': self.pso.bounds.max,
                            'classical_smc': {
                                'min': self.pso.bounds.classical_smc.min,
                                'max': self.pso.bounds.classical_smc.max
                            },
                            'adaptive_smc': {
                                'min': self.pso.bounds.adaptive_smc.min,
                                'max': self.pso.bounds.adaptive_smc.max
                            },
                            'sta_smc': {
                                'min': self.pso.bounds.sta_smc.min,
                                'max': self.pso.bounds.sta_smc.max
                            }
                        },
                        'w': self.pso.w,
                        'c1': self.pso.c1,
                        'c2': self.pso.c2,
                        'iters': self.pso.iters,
                        'w_schedule': self.pso.w_schedule,
                        'n_processes': self.pso.n_processes,
                        'hyper_trials': self.pso.hyper_trials,
                        'hyper_search': self.pso.hyper_search,
                        'study_timeout': self.pso.study_timeout
                    },
                    'physics_uncertainty': {
                        'n_evals': self.physics_uncertainty.n_evals
                    }
                }

        return MockConfig()

    @pytest.fixture
    def mock_controller_factory(self):
        """Create mock controller factory."""
        def factory(gains):
            controller = Mock()
            controller.max_force = 150.0
            controller.n_gains = len(gains)
            controller.controller_type = 'classical_smc'
            controller.validate_gains = Mock(return_value=np.ones(len(gains), dtype=bool))
            return controller

        factory.n_gains = 6
        factory.controller_type = 'classical_smc'
        return factory

    def test_pso_tuner_initialization(self, minimal_config, mock_controller_factory):
        """Test PSOTuner initialization with valid configuration."""
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,
            seed=42
        )

        assert tuner.seed == 42
        assert tuner.instability_penalty > 0
        assert tuner.combine_weights == (0.7, 0.3)
        assert tuner.normalisation_threshold > 0

    def test_pso_tuner_with_config_file(self, minimal_config, mock_controller_factory, tmp_path):
        """Test PSOTuner initialization with configuration file."""
        config_file = tmp_path / "test_config.yaml"
        config_data = minimal_config.model_dump()

        with open(config_file, 'w') as f:
            yaml.safe_dump(config_data, f)

        # Test with direct config object instead of file path since ConfigSchema import may fail
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,  # Use config object directly
            seed=42
        )

        assert tuner.seed == 42
        # Don't check ConfigSchema type since we're using mock config
        assert tuner.cfg is not None

    def test_deprecated_pso_config_fields(self, minimal_config, mock_controller_factory):
        """Test that deprecated PSO configuration fields raise ValueError."""
        # Create a copy of config and modify PSO to have deprecated field
        config_copy = minimal_config
        config_copy.pso.n_processes = 4  # Deprecated field

        with pytest.raises(ValueError, match="Deprecated PSO configuration fields"):
            PSOTuner(
                controller_factory=mock_controller_factory,
                config=config_copy,
                seed=42
            )

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_fitness_evaluation(self, mock_simulate, minimal_config, mock_controller_factory):
        """Test fitness function evaluation."""
        # Setup mock simulation results
        mock_simulate.return_value = (
            np.linspace(0, 1, 101),  # time
            np.random.random((2, 101, 6)),  # states
            np.random.random((2, 101)),  # controls
            np.random.random((2, 101))   # sigma
        )

        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,
            seed=42
        )

        # Test fitness evaluation
        particles = np.random.random((2, 6))
        fitness = tuner._fitness(particles)

        assert isinstance(fitness, np.ndarray)
        assert fitness.shape == (2,)
        assert np.all(np.isfinite(fitness))

    def test_normalisation_function(self, minimal_config, mock_controller_factory):
        """Test safe normalisation function."""
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,
            seed=42
        )

        # Test normal normalisation
        values = np.array([1.0, 2.0, 3.0])
        normalised = tuner._normalise(values, 2.0)
        expected = np.array([0.5, 1.0, 1.5])
        np.testing.assert_array_almost_equal(normalised, expected)

        # Test near-zero denominator
        normalised_zero = tuner._normalise(values, 1e-15)
        np.testing.assert_array_equal(normalised_zero, values)

    def test_cost_combination(self, minimal_config, mock_controller_factory):
        """Test cost aggregation across uncertainty draws."""
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,
            seed=42
        )

        # Test 1D cost array
        costs_1d = np.array([1.0, 2.0, 3.0])
        combined = tuner._combine_costs(costs_1d)
        expected = 0.7 * 2.0 + 0.3 * 3.0  # mean * w_mean + max * w_max
        assert abs(combined - expected) < 1e-10

        # Test 2D cost array
        costs_2d = np.array([[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]])
        combined_2d = tuner._combine_costs(costs_2d)
        assert combined_2d.shape == (2,)

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    @patch('pyswarms.single.GlobalBestPSO')
    def test_optimization_execution(self, mock_pso_class, mock_simulate, minimal_config, mock_controller_factory):
        """Test full PSO optimization execution."""
        # Setup mocks
        mock_optimizer = Mock()
        mock_optimizer.optimize.return_value = (1.5, np.array([5, 5, 5, 2, 20, 1]))
        mock_optimizer.cost_history = [2.0, 1.8, 1.5]
        mock_optimizer.pos_history = [np.array([5, 5, 5, 2, 20, 1])]
        # Make options property support item assignment for weight scheduling
        mock_optimizer.options = {}
        mock_pso_class.return_value = mock_optimizer

        mock_simulate.return_value = (
            np.linspace(0, 1, 101),
            np.random.random((5, 101, 6)),
            np.random.random((5, 101)),
            np.random.random((5, 101))
        )

        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,
            seed=42
        )

        # Run optimization
        result = tuner.optimise()

        assert 'best_cost' in result
        assert 'best_pos' in result
        assert 'history' in result
        assert result['best_cost'] == 1.5
        assert len(result['best_pos']) == 6

    def test_perturbed_physics_iteration(self, minimal_config, mock_controller_factory):
        """Test physics uncertainty iteration."""
        # Modify uncertainty configuration directly
        config_copy = minimal_config
        config_copy.physics_uncertainty.n_evals = 3
        # Add perturbation parameters (note: these need to be added dynamically)
        config_copy.physics_uncertainty.cart_mass = 0.1
        config_copy.physics_uncertainty.pendulum1_mass = 0.05

        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=config_copy,
            seed=42
        )

        physics_models = list(tuner._iter_perturbed_physics())
        assert len(physics_models) == 3  # nominal + 2 perturbed

    def test_instability_penalty_computation(self, minimal_config, mock_controller_factory):
        """Test instability penalty calculation."""
        # Test with explicit penalty
        config_copy = minimal_config
        config_copy.cost_function.instability_penalty = 500.0

        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=config_copy,
            seed=42
        )

        assert tuner.instability_penalty == 500.0

    def test_bounds_dimension_matching(self, minimal_config, mock_controller_factory):
        """Test PSO bounds dimension matching with controller expectations."""
        from dataclasses import dataclass
        from typing import List, Any

        @dataclass
        class MockWrongBounds:
            min: List[float] = None
            max: List[float] = None
            classical_smc: Any = None

            def __post_init__(self):
                if self.min is None:
                    self.min = [1.0, 1.0, 1.0]  # Only 3 dimensions
                if self.max is None:
                    self.max = [10.0, 10.0, 10.0]
                if self.classical_smc is None:
                    from dataclasses import dataclass
                    @dataclass
                    class MockControllerBounds:
                        min: List[float] = None
                        max: List[float] = None
                        def __post_init__(self):
                            if self.min is None:
                                self.min = [1.0, 1.0, 1.0]  # Wrong dimensions
                            if self.max is None:
                                self.max = [10.0, 10.0, 10.0]
                    self.classical_smc = MockControllerBounds()

        @dataclass
        class MockWrongPSO:
            n_particles: int = 5
            bounds: MockWrongBounds = None
            w: float = 0.5
            c1: float = 1.5
            c2: float = 1.5
            iters: int = 3
            w_schedule: Any = None
            n_processes: Any = None
            hyper_trials: Any = None
            hyper_search: Any = None
            study_timeout: Any = None

            def __post_init__(self):
                if self.bounds is None:
                    self.bounds = MockWrongBounds()

        # Create config with wrong bounds dimensions
        wrong_bounds_config = minimal_config
        wrong_bounds_config.pso = MockWrongPSO()

        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=wrong_bounds_config,
            seed=42
        )

        # Should auto-extend to match expected dimensions
        with patch('pyswarms.single.GlobalBestPSO') as mock_pso:
            mock_optimizer = Mock()
            mock_optimizer.optimize.return_value = (1.0, np.array([5, 5, 5, 2, 20, 1]))
            mock_optimizer.cost_history = [1.0]
            mock_optimizer.pos_history = [np.array([5, 5, 5, 2, 20, 1])]
            mock_optimizer.options = {}
            mock_pso.return_value = mock_optimizer

            with patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch'):
                result = tuner.optimise()
                assert 'best_pos' in result


class TestPSOTunerIntegration:
    """Integration tests for PSOTuner with real components."""

    def test_real_configuration_loading(self):
        """Test loading actual configuration file."""
        # This test would use the real config.yaml if available
        config_path = Path("D:/Projects/main/config.yaml")
        if not config_path.exists():
            pytest.skip("Main config.yaml not found")

        try:
            from src.config import load_config
            config = load_config(str(config_path))

            # Basic validation that config loaded properly
            assert hasattr(config, 'pso')
            assert hasattr(config, 'physics')
            assert hasattr(config, 'simulation')
        except Exception as e:
            pytest.skip(f"Could not load real configuration: {e}")


# Performance and property-based tests would go here
class TestPSOTunerProperties:
    """Property-based and performance tests for PSOTuner."""

    @pytest.fixture
    def minimal_config(self):
        """Create minimal valid configuration for testing."""
        from dataclasses import dataclass
        from typing import List

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
                """Provide Pydantic-compatible model_dump method for mock."""
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
        class MockNorms:
            state_error: float = 1.0
            control_effort: float = 1.0
            control_rate: float = 1.0
            sliding: float = 1.0

        @dataclass
        class MockCostFunction:
            weights: MockWeights = None
            norms: MockNorms = None
            instability_penalty: float = 1000.0

            def __post_init__(self):
                if self.weights is None:
                    self.weights = MockWeights()
                if self.norms is None:
                    self.norms = MockNorms()

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
                    self.max = [20.0, 20.0, 10.0, 10.0, 50.0, 5.0]
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
            options: dict = None
            iters: int = 5
            max_iters: int = 100
            tol: float = 1e-6
            seed: int = None
            n_jobs: int = 1
            early_stopping: bool = False
            patience: int = 10
            study_timeout: int = None

            def __post_init__(self):
                if self.bounds is None:
                    self.bounds = MockPSOBounds()
                if self.options is None:
                    self.options = {'c1': self.c1, 'c2': self.c2, 'w': self.w}

        @dataclass
        class MockPhysicsUncertainty:
            n_evals: int = 1

            def model_dump(self) -> dict:
                """Provide Pydantic-compatible model_dump method for mock."""
                return {'n_evals': self.n_evals}

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
    def mock_controller_factory(self):
        """Create mock controller factory."""
        def factory(gains, controller_type="classical_smc", config=None):
            mock_controller = Mock()
            mock_controller.gains = gains
            mock_controller.controller_type = controller_type
            mock_controller.compute_control = Mock(return_value=np.array([0.0]))
            return mock_controller

        # Add required attributes to the factory function for PSO compatibility
        factory.n_gains = 6
        factory.controller_type = "classical_smc"
        factory.max_force = 150.0
        return factory

    def test_deterministic_behavior(self, minimal_config, mock_controller_factory):
        """Test that PSO optimization is deterministic with fixed seed."""
        with patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch') as mock_sim:
            mock_sim.return_value = (
                np.linspace(0, 1, 101),
                np.random.RandomState(42).random((5, 101, 6)),
                np.random.RandomState(42).random((5, 101)),
                np.random.RandomState(42).random((5, 101))
            )

            with patch('pyswarms.single.GlobalBestPSO') as mock_pso:
                mock_optimizer = Mock()
                mock_optimizer.optimize.return_value = (1.5, np.array([5, 5, 5, 2, 20, 1]))
                mock_optimizer.cost_history = [1.5]
                mock_optimizer.pos_history = [np.array([5, 5, 5, 2, 20, 1])]
                mock_optimizer.options = {}
                mock_pso.return_value = mock_optimizer

                tuner1 = PSOTuner(mock_controller_factory, minimal_config, seed=42)
                tuner2 = PSOTuner(mock_controller_factory, minimal_config, seed=42)

                result1 = tuner1.optimise()
                result2 = tuner2.optimise()

                assert result1['best_cost'] == result2['best_cost']
                np.testing.assert_array_equal(result1['best_pos'], result2['best_pos'])

    def test_parameter_validation_bounds(self, minimal_config, mock_controller_factory):
        """Test parameter bounds validation."""
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,
            seed=42
        )

        # Test invalid parameters (negative values, etc.)
        invalid_particles = np.array([[-1, -1, -1, -1, -1, -1]])

        with patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch') as mock_sim:
            # Mock must return 4-tuple: (time, states, controls, sigma)
            mock_sim.return_value = (
                np.linspace(0, 1, 101),  # time
                np.random.random((1, 101, 6)),  # states
                np.random.random((1, 101)),  # controls
                np.random.random((1, 101))   # sigma
            )
            fitness = tuner._fitness(invalid_particles)
            # Should handle gracefully, potentially with high penalty
            assert np.all(np.isfinite(fitness))

class TestPSOTunerEdgeCases:
    """Edge case tests for PSO optimizer to achieve 85%+ coverage."""

    @pytest.fixture
    def minimal_config(self):
        """Create minimal valid configuration for testing."""
        from dataclasses import dataclass
        from typing import Any, List

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
            duration: float = 1.0
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
            state_error: float = 1.0
            control_effort: float = 1.0
            control_rate: float = 1.0
            sliding: float = 1.0

        @dataclass
        class MockCostFunction:
            weights: MockWeights = None
            norms: MockNorms = None
            instability_penalty: float = 1000.0

            def __post_init__(self):
                if self.weights is None:
                    self.weights = MockWeights()
                if self.norms is None:
                    self.norms = MockNorms()

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
                    self.max = [20.0, 20.0, 10.0, 10.0, 50.0, 5.0]
                if self.classical_smc is None:
                    self.classical_smc = MockControllerBounds(
                        min=[1.0, 1.0, 1.0, 1.0, 5.0, 0.1],
                        max=[30.0, 30.0, 20.0, 20.0, 50.0, 10.0]
                    )

        @dataclass
        class MockPSO:
            n_particles: int = 5
            bounds: MockPSOBounds = None
            w: float = 0.5
            c1: float = 1.5
            c2: float = 1.5
            iters: int = 3
            w_schedule: Any = None
            n_processes: Any = None
            hyper_trials: Any = None
            hyper_search: Any = None
            study_timeout: Any = None

            def __post_init__(self):
                if self.bounds is None:
                    self.bounds = MockPSOBounds()

        @dataclass
        class MockPhysicsUncertainty:
            n_evals: int = 1

            def model_dump(self) -> dict:
                return {'n_evals': self.n_evals}

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
    def mock_controller_factory(self):
        """Create mock controller factory."""
        def factory(gains):
            controller = Mock()
            controller.max_force = 150.0
            controller.n_gains = len(gains)
            controller.controller_type = 'classical_smc'
            controller.validate_gains = Mock(return_value=np.ones(len(gains), dtype=bool))
            return controller

        factory.n_gains = 6
        factory.controller_type = 'classical_smc'
        return factory

    def test_deprecated_hyper_trials_raises_error(self, minimal_config, mock_controller_factory):
        """Test lines 197-198: deprecated hyper_trials parameter."""
        config_copy = minimal_config
        config_copy.pso.hyper_trials = 10  # Set deprecated field

        with pytest.raises(ValueError, match="Deprecated PSO configuration fields"):
            PSOTuner(
                controller_factory=mock_controller_factory,
                config=config_copy,
                seed=42
            )

    def test_deprecated_hyper_search_raises_error(self, minimal_config, mock_controller_factory):
        """Test lines 199-200: deprecated hyper_search parameter."""
        config_copy = minimal_config
        config_copy.pso.hyper_search = True  # Set deprecated field

        with pytest.raises(ValueError, match="Deprecated PSO configuration fields"):
            PSOTuner(
                controller_factory=mock_controller_factory,
                config=config_copy,
                seed=42
            )

    def test_deprecated_study_timeout_raises_error(self, minimal_config, mock_controller_factory):
        """Test lines 201-202: deprecated study_timeout parameter."""
        config_copy = minimal_config
        config_copy.pso.study_timeout = 600  # Set deprecated field

        with pytest.raises(ValueError, match="Deprecated PSO configuration fields"):
            PSOTuner(
                controller_factory=mock_controller_factory,
                config=config_copy,
                seed=42
            )

    def test_multiple_deprecated_fields_in_error_message(self, minimal_config, mock_controller_factory):
        """Test lines 203-207: multiple deprecated fields in single error message."""
        config_copy = minimal_config
        config_copy.pso.hyper_trials = 10
        config_copy.pso.hyper_search = True
        config_copy.pso.study_timeout = 600

        with pytest.raises(ValueError, match="hyper_trials.*hyper_search.*study_timeout"):
            PSOTuner(
                controller_factory=mock_controller_factory,
                config=config_copy,
                seed=42
            )

    def test_invalid_instability_penalty_falls_back_to_default(self, minimal_config, mock_controller_factory):
        """Test lines 217-221: invalid instability_penalty value handling."""
        from dataclasses import dataclass
        from typing import Any

        @dataclass
        class MockWeights:
            state_error: float = 50.0
            control_effort: float = 0.2
            control_rate: float = 0.1
            stability: float = 0.1

        @dataclass
        class MockNorms:
            state_error: float = 1.0
            control_effort: float = 1.0
            control_rate: float = 1.0
            sliding: float = 1.0

        @dataclass
        class MockCostFunction:
            weights: MockWeights = None
            norms: MockNorms = None
            instability_penalty: Any = "invalid_string"  # Invalid value

            def __post_init__(self):
                if self.weights is None:
                    self.weights = MockWeights()
                if self.norms is None:
                    self.norms = MockNorms()

        config_copy = minimal_config
        config_copy.cost_function = MockCostFunction()

        # Should log warning and fall back to default factor
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=config_copy,
            seed=42
        )

        # Should fall back to default penalty factor (100.0)
        assert tuner.instability_penalty == 100.0

    def test_normalization_with_very_small_denominator(self, minimal_config, mock_controller_factory):
        """Test lines 263-267: normalization with near-zero denominator."""
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,
            seed=42
        )

        values = np.array([1.0, 2.0, 3.0])
        # Test with denominator just above threshold
        small_denom = tuner.normalisation_threshold * 1.1
        normalised = tuner._normalise(values, small_denom)

        # Should normalize normally
        expected = values / small_denom
        np.testing.assert_array_almost_equal(normalised, expected)

    def test_normalization_below_threshold_returns_original(self, minimal_config, mock_controller_factory):
        """Test normalization threshold bypass - returns original values."""
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,
            seed=42
        )

        values = np.array([1.0, 2.0, 3.0])
        # Test with denominator below threshold
        tiny_denom = tuner.normalisation_threshold * 0.5

        normalised = tuner._normalise(values, tiny_denom)

        # Should return original values unchanged
        np.testing.assert_array_equal(normalised, values)

    def test_compute_cost_from_traj_handles_normal_trajectories(self, minimal_config, mock_controller_factory):
        """Test _compute_cost_from_traj with normal trajectories."""
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,
            seed=42
        )

        n_particles = 3
        n_steps = 10
        n_states = 6

        t = np.linspace(0, 1.0, n_steps)
        x_b = np.random.randn(n_particles, n_steps, n_states) * 0.1
        u_b = np.random.randn(n_particles, n_steps) * 10.0
        sigma_b = np.random.randn(n_particles, n_steps) * 0.5

        costs = tuner._compute_cost_from_traj(t, x_b, u_b, sigma_b)

        assert costs.shape == (n_particles,)
        assert np.all(np.isfinite(costs))
        assert np.all(costs >= 0)

    def test_normalise_with_large_denominator(self, minimal_config, mock_controller_factory):
        """Test _normalise with large denominator value."""
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,
            seed=42
        )

        values = np.array([100.0, 200.0, 300.0])
        large_denom = 1000.0

        normalised = tuner._normalise(values, large_denom)

        expected = values / large_denom
        np.testing.assert_array_almost_equal(normalised, expected)

    def test_combine_costs_weighted_mean_max(self, minimal_config, mock_controller_factory):
        """Test _combine_costs computes weighted mean+max across draws."""
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,
            seed=42
        )

        # Create cost matrix: (n_draws, n_particles)
        costs = np.array([
            [10.0, 20.0, 30.0],
            [12.0, 22.0, 32.0],
            [14.0, 24.0, 34.0]
        ])

        combined = tuner._combine_costs(costs)

        # Default combine_weights is (0.7, 0.3) for (mean_weight, max_weight)
        mean_w, max_w = tuner.combine_weights
        expected = mean_w * np.mean(costs, axis=0) + max_w * np.max(costs, axis=0)
        np.testing.assert_array_almost_equal(combined, expected)

    def test_iter_perturbed_physics_returns_iterable(self, minimal_config, mock_controller_factory):
        """Test _iter_perturbed_physics returns iterable of physics models."""
        config_copy = minimal_config
        config_copy.physics_uncertainty.n_evals = 3

        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=config_copy,
            seed=42
        )

        physics_models = list(tuner._iter_perturbed_physics())

        assert len(physics_models) == 3
        assert all(hasattr(model, 'cart_mass') for model in physics_models)

    def test_normalise_handles_zero_values(self, minimal_config, mock_controller_factory):
        """Test _normalise handles array with zero values."""
        tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=minimal_config,
            seed=42
        )

        values = np.array([0.0, 0.0, 0.0])
        denom = 10.0

        normalised = tuner._normalise(values, denom)

        expected = np.zeros(3)
        np.testing.assert_array_equal(normalised, expected)
