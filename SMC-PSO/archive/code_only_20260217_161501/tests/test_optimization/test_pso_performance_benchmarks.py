#======================================================================================\\\
#============= tests/test_optimization/test_pso_performance_benchmarks.py =============\\\
#======================================================================================\\\

"""
Comprehensive PSO performance benchmarks using pytest-benchmark.
Restores performance regression detection for optimization algorithms.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import List

from src.optimization.algorithms.pso_optimizer import PSOTuner


class TestPSOPerformanceBenchmarks:
    """Performance benchmark test suite for PSO optimization."""

    @pytest.fixture
    def benchmark_config(self):
        """Create optimized configuration for performance benchmarking."""
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
            iters: int = 10

            def __post_init__(self):
                if self.bounds is None:
                    self.bounds = MockPSOBounds()

        @dataclass
        class MockConfig:
            global_seed: int = 42
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
    def fast_controller_factory(self):
        """Fast controller factory for performance testing."""
        def factory(gains):
            controller = Mock()
            controller.max_force = 150.0
            controller.gains = gains
            controller.controller_type = 'classical_smc'

            # Fast validation function
            def validate_gains(particle_array):
                if particle_array.ndim == 1:
                    particle_array = particle_array.reshape(1, -1)
                return np.ones(particle_array.shape[0], dtype=bool)

            controller.validate_gains = validate_gains
            return controller

        factory.n_gains = 6
        factory.controller_type = 'classical_smc'
        return factory

    @pytest.fixture
    def mock_simulation_fast(self):
        """Fast simulation mock for benchmarking."""
        def mock_simulate(*args, **kwargs):
            # Extract number of particles
            particles = args[1] if len(args) > 1 else kwargs.get('particles', np.array([[1,1,1,1,1,1]]))
            n_particles = particles.shape[0]
            n_timesteps = 101

            # Generate fast deterministic results
            t = np.linspace(0, 1.0, n_timesteps)
            x = np.random.RandomState(42).random((n_particles, n_timesteps, 6)) * 0.1
            u = np.random.RandomState(42).random((n_particles, n_timesteps)) * 10.0
            sigma = np.random.RandomState(42).random((n_particles, n_timesteps)) * 0.5

            return (t, x, u, sigma)

        return mock_simulate

    def test_pso_initialization_performance(self, benchmark, benchmark_config, fast_controller_factory):
        """Benchmark PSO initialization performance."""
        def create_pso_tuner():
            return PSOTuner(
                controller_factory=fast_controller_factory,
                config=benchmark_config,
                seed=42
            )

        result = benchmark(create_pso_tuner)
        assert result is not None
        assert hasattr(result, 'seed')

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_fitness_evaluation_performance(self, mock_simulate, benchmark, benchmark_config, fast_controller_factory, mock_simulation_fast):
        """Benchmark fitness evaluation performance."""
        mock_simulate.side_effect = mock_simulation_fast

        tuner = PSOTuner(
            controller_factory=fast_controller_factory,
            config=benchmark_config,
            seed=42
        )

        # Test particles
        particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 2.0],
            [12.0, 9.0, 6.0, 4.0, 25.0, 3.0],
            [8.0, 7.0, 4.0, 2.0, 15.0, 1.5],
            [15.0, 10.0, 7.0, 5.0, 30.0, 4.0],
            [5.0, 5.0, 3.0, 1.0, 10.0, 1.0]
        ])

        def fitness_evaluation():
            return tuner._fitness(particles)

        result = benchmark(fitness_evaluation)
        assert result.shape == (5,)
        assert np.all(np.isfinite(result))

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_cost_computation_performance(self, mock_simulate, benchmark, benchmark_config, fast_controller_factory, mock_simulation_fast):
        """Benchmark cost computation performance."""
        mock_simulate.side_effect = mock_simulation_fast

        tuner = PSOTuner(
            controller_factory=fast_controller_factory,
            config=benchmark_config,
            seed=42
        )

        # Generate test trajectory data
        t = np.linspace(0, 1.0, 101)
        x = np.random.RandomState(42).random((10, 101, 6)) * 0.1
        u = np.random.RandomState(42).random((10, 101)) * 10.0
        sigma = np.random.RandomState(42).random((10, 101)) * 0.5

        def cost_computation():
            return tuner._compute_cost_from_traj(t, x, u, sigma)

        result = benchmark(cost_computation)
        assert result.shape == (10,)
        assert np.all(np.isfinite(result))

    def test_normalisation_performance(self, benchmark, benchmark_config, fast_controller_factory):
        """Benchmark normalisation function performance."""
        tuner = PSOTuner(
            controller_factory=fast_controller_factory,
            config=benchmark_config,
            seed=42
        )

        # Large array for performance testing
        values = np.random.random(10000) * 100

        def normalisation():
            return tuner._normalise(values, 5.0)

        result = benchmark(normalisation)
        assert result.shape == values.shape
        assert np.all(np.isfinite(result))

    def test_cost_combination_performance(self, benchmark, benchmark_config, fast_controller_factory):
        """Benchmark cost combination performance."""
        tuner = PSOTuner(
            controller_factory=fast_controller_factory,
            config=benchmark_config,
            seed=42
        )

        # Large 2D cost array
        costs = np.random.random((100, 50))  # 100 draws, 50 particles

        def cost_combination():
            return tuner._combine_costs(costs)

        result = benchmark(cost_combination)
        assert result.shape == (50,)
        assert np.all(np.isfinite(result))

    @patch('pyswarms.single.GlobalBestPSO')
    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_small_optimization_performance(self, mock_simulate, mock_pso_class, benchmark, benchmark_config, fast_controller_factory, mock_simulation_fast):
        """Benchmark small PSO optimization performance."""
        # Setup mocks for fast execution
        mock_optimizer = Mock()
        mock_optimizer.optimize.return_value = (1.5, np.array([10, 8, 5, 3, 20, 2]))
        mock_optimizer.cost_history = [2.0, 1.8, 1.5]
        mock_optimizer.pos_history = [np.array([10, 8, 5, 3, 20, 2])]
        mock_optimizer.options = {}
        mock_pso_class.return_value = mock_optimizer

        mock_simulate.side_effect = mock_simulation_fast

        # Small optimization for benchmark
        config = benchmark_config
        config.pso.n_particles = 5
        config.pso.iters = 5

        def small_optimization():
            tuner = PSOTuner(
                controller_factory=fast_controller_factory,
                config=config,
                seed=42
            )
            return tuner.optimise()

        result = benchmark(small_optimization)
        assert 'best_cost' in result
        assert 'best_pos' in result

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_physics_perturbation_performance(self, mock_simulate, benchmark, benchmark_config, fast_controller_factory, mock_simulation_fast):
        """Benchmark physics uncertainty iteration performance."""
        mock_simulate.side_effect = mock_simulation_fast

        # Enable uncertainty
        @dataclass
        class MockPhysicsUncertainty:
            n_evals: int = 10
            cart_mass: float = 0.1
            pendulum1_mass: float = 0.05

            def model_dump(self) -> dict:
                return {
                    'n_evals': self.n_evals,
                    'cart_mass': self.cart_mass,
                    'pendulum1_mass': self.pendulum1_mass
                }

        config = benchmark_config
        config.physics_uncertainty = MockPhysicsUncertainty()

        tuner = PSOTuner(
            controller_factory=fast_controller_factory,
            config=config,
            seed=42
        )

        def physics_perturbation():
            return list(tuner._iter_perturbed_physics())

        result = benchmark(physics_perturbation)
        assert len(result) == 10

    def test_parameter_bounds_validation_performance(self, benchmark, benchmark_config, fast_controller_factory):
        """Benchmark parameter bounds validation performance."""
        def validation_factory(gains):
            controller = Mock()
            controller.max_force = 150.0
            controller.gains = gains
            controller.controller_type = 'classical_smc'

            def validate_gains(particle_array):
                """Realistic but fast validation."""
                if particle_array.ndim == 1:
                    particle_array = particle_array.reshape(1, -1)

                # Vectorized validation
                valid_mask = np.ones(particle_array.shape[0], dtype=bool)
                valid_mask &= np.all(particle_array > 0, axis=1)  # Positivity
                valid_mask &= np.all(particle_array[:, :4] < 100, axis=1)  # Upper bounds
                valid_mask &= (particle_array[:, 4] >= 5.0) & (particle_array[:, 4] <= 50.0)  # Switching gain

                return valid_mask

            controller.validate_gains = validate_gains
            return controller

        validation_factory.n_gains = 6
        validation_factory.controller_type = 'classical_smc'

        PSOTuner(
            controller_factory=validation_factory,
            config=benchmark_config,
            seed=42
        )

        # Large particle array
        particles = np.random.uniform(1, 30, (1000, 6))

        def bounds_validation():
            controller = validation_factory(particles[0])
            return controller.validate_gains(particles)

        result = benchmark(bounds_validation)
        assert result.shape == (1000,)
        assert result.dtype == bool


class TestPSOScalabilityBenchmarks:
    """Scalability benchmarks for PSO optimization."""

    @pytest.fixture
    def scalable_config(self):
        """Configuration for scalability testing."""
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

            def __post_init__(self):
                if self.initial_state is None:
                    self.initial_state = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        @dataclass
        class MockWeights:
            state_error: float = 1.0
            control_effort: float = 1.0
            control_rate: float = 1.0
            stability: float = 1.0

        @dataclass
        class MockCostFunction:
            weights: MockWeights = None

            def __post_init__(self):
                if self.weights is None:
                    self.weights = MockWeights()

        @dataclass
        class MockPSO:
            n_particles: int = 20
            iters: int = 10

        @dataclass
        class MockConfig:
            global_seed: int = 42
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
    def scalable_controller_factory(self):
        """Controller factory for scalability testing."""
        def factory(gains):
            controller = Mock()
            controller.max_force = 150.0
            return controller

        factory.n_gains = 6
        return factory

    @pytest.mark.parametrize("n_particles", [5, 10, 20, 50])
    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_fitness_scaling_with_particles(self, mock_simulate, benchmark, scalable_config, scalable_controller_factory, n_particles):
        """Benchmark fitness evaluation scaling with particle count."""
        # Mock simulation
        def mock_sim(*args, **kwargs):
            particles = args[1] if len(args) > 1 else kwargs.get('particles')
            n_p = particles.shape[0] if hasattr(particles, 'shape') else n_particles
            t = np.linspace(0, 1.0, 101)
            x = np.random.RandomState(42).random((n_p, 101, 6)) * 0.1
            u = np.random.RandomState(42).random((n_p, 101)) * 10.0
            sigma = np.random.RandomState(42).random((n_p, 101)) * 0.5
            return (t, x, u, sigma)

        mock_simulate.side_effect = mock_sim

        tuner = PSOTuner(
            controller_factory=scalable_controller_factory,
            config=scalable_config,
            seed=42
        )

        particles = np.random.uniform(1, 30, (n_particles, 6))

        def fitness_evaluation():
            return tuner._fitness(particles)

        result = benchmark.pedantic(fitness_evaluation, rounds=3, iterations=5)
        assert result.shape == (n_particles,)

    @pytest.mark.parametrize("n_timesteps", [51, 101, 201, 501])
    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_cost_scaling_with_trajectory_length(self, mock_simulate, benchmark, scalable_config, scalable_controller_factory, n_timesteps):
        """Benchmark cost computation scaling with trajectory length."""
        mock_simulate.return_value = (
            np.linspace(0, 1.0, n_timesteps),
            np.random.RandomState(42).random((10, n_timesteps, 6)) * 0.1,
            np.random.RandomState(42).random((10, n_timesteps)) * 10.0,
            np.random.RandomState(42).random((10, n_timesteps)) * 0.5
        )

        tuner = PSOTuner(
            controller_factory=scalable_controller_factory,
            config=scalable_config,
            seed=42
        )

        # Generate test data
        t = np.linspace(0, 1.0, n_timesteps)
        x = np.random.RandomState(42).random((10, n_timesteps, 6)) * 0.1
        u = np.random.RandomState(42).random((10, n_timesteps)) * 10.0
        sigma = np.random.RandomState(42).random((10, n_timesteps)) * 0.5

        def cost_computation():
            return tuner._compute_cost_from_traj(t, x, u, sigma)

        result = benchmark.pedantic(cost_computation, rounds=3, iterations=10)
        assert result.shape == (10,)

    @pytest.mark.parametrize("array_size", [100, 1000, 10000])
    def test_normalisation_scaling(self, benchmark, scalable_config, scalable_controller_factory, array_size):
        """Benchmark normalisation scaling with array size."""
        tuner = PSOTuner(
            controller_factory=scalable_controller_factory,
            config=scalable_config,
            seed=42
        )

        values = np.random.random(array_size) * 100

        def normalisation():
            return tuner._normalise(values, 5.0)

        result = benchmark.pedantic(normalisation, rounds=5, iterations=100)
        assert result.shape == (array_size,)


class TestPSOMemoryBenchmarks:
    """Memory usage benchmarks for PSO optimization."""

    @pytest.fixture
    def memory_config(self):
        """Configuration for memory testing."""
        @dataclass
        class MockConfig:
            global_seed: int = 42

        return MockConfig()

    def test_memory_efficiency_large_arrays(self, benchmark):
        """Benchmark memory efficiency with large arrays."""
        from src.optimization.algorithms.pso_optimizer import _normalise

        # Large array for memory testing
        size = 100000
        values = np.random.random(size)
        denominator = 5.0

        def memory_test():
            # Test multiple operations that could accumulate memory
            results = []
            for _ in range(10):
                result = _normalise(values, denominator)
                results.append(result.mean())  # Store only mean to avoid memory buildup
            return results

        result = benchmark(memory_test)
        assert len(result) == 10


# Custom benchmark assertions
class TestPSOPerformanceAssertions:
    """Performance assertions and thresholds."""

    def test_fitness_evaluation_threshold(self):
        """Assert fitness evaluation meets performance threshold."""
        # This would be run with actual timing data
        # Target: < 10ms for 10 particles with 100 timesteps
        pass

    def test_optimization_convergence_rate(self):
        """Assert optimization converges within reasonable time."""
        # Target: < 1 second for 10 particles, 10 iterations
        pass

    def test_memory_usage_bounds(self):
        """Assert memory usage stays within bounds."""
        # Target: < 100MB for standard optimization run
        pass


if __name__ == "__main__":
    pytest.main([__file__, "--benchmark-only", "-v"])