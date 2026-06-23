#======================================================================================\\\
#=============== tests/test_optimization/test_optimization_framework.py ===============\\\
#======================================================================================\\\

"""
Comprehensive optimization algorithm testing framework and benchmarking.
Covers multi-objective optimization, constraint handling, and algorithm comparison.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
import time
from dataclasses import dataclass
from typing import List, Optional
import json
import tempfile
from pathlib import Path

from src.optimization.algorithms.pso_optimizer import PSOTuner


class TestOptimizationFramework:
    """Comprehensive optimization framework testing."""

    @pytest.fixture
    def framework_config(self):
        """Configuration for optimization framework testing."""
        @dataclass
        class FrameworkPhysics:
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
        class FrameworkSimulation:
            duration: float = 3.0
            dt: float = 0.01
            initial_state: List[float] = None
            use_full_dynamics: bool = False

            def __post_init__(self):
                if self.initial_state is None:
                    self.initial_state = [0.0, 0.1, -0.05, 0.0, 0.0, 0.0]

        @dataclass
        class FrameworkWeights:
            state_error: float = 100.0
            control_effort: float = 0.1
            control_rate: float = 0.05
            stability: float = 1.0

        @dataclass
        class FrameworkNorms:
            state_error: float = 20.0
            control_effort: float = 10.0
            control_rate: float = 5.0
            sliding: float = 2.0

        @dataclass
        class FrameworkCombineWeights:
            mean: float = 0.6
            max: float = 0.4

        @dataclass
        class FrameworkCostFunction:
            weights: FrameworkWeights = None
            norms: FrameworkNorms = None
            instability_penalty: float = 5e5
            combine_weights: FrameworkCombineWeights = None
            normalization_threshold: float = 1e-10

            def __post_init__(self):
                if self.weights is None:
                    self.weights = FrameworkWeights()
                if self.norms is None:
                    self.norms = FrameworkNorms()
                if self.combine_weights is None:
                    self.combine_weights = FrameworkCombineWeights()

        @dataclass
        class FrameworkPSO:
            n_particles: int = 20
            iters: int = 30
            w: float = 0.6
            c1: float = 1.8
            c2: float = 1.8
            velocity_clamp: Optional[List[float]] = None
            w_schedule: Optional[List[float]] = None

        @dataclass
        class FrameworkUncertainty:
            n_evals: int = 5
            cart_mass: float = 0.15
            pendulum1_mass: float = 0.1
            pendulum2_mass: float = 0.1
            gravity: float = 0.05

            def model_dump(self) -> dict:
                return {
                    'n_evals': self.n_evals,
                    'cart_mass': self.cart_mass,
                    'pendulum1_mass': self.pendulum1_mass,
                    'pendulum2_mass': self.pendulum2_mass,
                    'gravity': self.gravity
                }

        @dataclass
        class FrameworkConfig:
            global_seed: int = 12345
            physics: FrameworkPhysics = None
            simulation: FrameworkSimulation = None
            cost_function: FrameworkCostFunction = None
            pso: FrameworkPSO = None
            physics_uncertainty: FrameworkUncertainty = None

            def __post_init__(self):
                if self.physics is None:
                    self.physics = FrameworkPhysics()
                if self.simulation is None:
                    self.simulation = FrameworkSimulation()
                if self.cost_function is None:
                    self.cost_function = FrameworkCostFunction()
                if self.pso is None:
                    self.pso = FrameworkPSO()
                if self.physics_uncertainty is None:
                    self.physics_uncertainty = FrameworkUncertainty()

        return FrameworkConfig()

    @pytest.fixture
    def multi_controller_factory(self):
        """Factory supporting multiple controller types."""
        def factory(gains, controller_type="classical_smc"):
            controller = Mock()
            controller.gains = gains
            controller.controller_type = controller_type

            # Controller-specific configurations
            if controller_type == "classical_smc":
                controller.max_force = 150.0
                controller.n_gains = 6
                bounds = [(0.5, 50.0)] * 4 + [(1.0, 100.0), (0.01, 10.0)]
            elif controller_type == "adaptive_smc":
                controller.max_force = 120.0
                controller.n_gains = 5
                bounds = [(1.0, 80.0)] * 4 + [(0.1, 20.0)]
            elif controller_type == "sta_smc":
                controller.max_force = 180.0
                controller.n_gains = 6
                bounds = [(2.0, 100.0)] * 4 + [(0.5, 150.0), (0.01, 15.0)]
            else:
                raise ValueError(f"Unknown controller type: {controller_type}")

            def validate_gains(particle_array):
                if particle_array.ndim == 1:
                    particle_array = particle_array.reshape(1, -1)

                valid_mask = np.ones(particle_array.shape[0], dtype=bool)

                for i, gains in enumerate(particle_array):
                    if not np.all(np.isfinite(gains)):
                        valid_mask[i] = False
                        continue

                    if len(gains) != controller.n_gains:
                        valid_mask[i] = False
                        continue

                    # Check bounds
                    for j, (min_val, max_val) in enumerate(bounds):
                        if j >= len(gains):
                            break
                        if gains[j] < min_val or gains[j] > max_val:
                            valid_mask[i] = False
                            break

                return valid_mask

            controller.validate_gains = validate_gains
            return controller

        factory.controller_types = ["classical_smc", "adaptive_smc", "sta_smc"]
        return factory

    def test_multi_controller_optimization(self, framework_config, multi_controller_factory):
        """Test optimization across multiple controller types."""
        results = {}

        for controller_type in multi_controller_factory.controller_types:
            # Create controller-specific factory
            def type_specific_factory(gains):
                return multi_controller_factory(gains, controller_type)

            tuner = PSOTuner(
                controller_factory=type_specific_factory,
                config=framework_config,
                seed=12345
            )

            # Test fitness evaluation for each controller type
            if controller_type == "classical_smc":
                test_particles = np.array([
                    [10.0, 8.0, 5.0, 3.0, 20.0, 1.0],
                    [15.0, 12.0, 7.0, 5.0, 30.0, 2.0]
                ])
            elif controller_type == "adaptive_smc":
                test_particles = np.array([
                    [20.0, 15.0, 10.0, 8.0, 5.0],
                    [30.0, 25.0, 15.0, 12.0, 8.0]
                ])
            else:  # sta_smc
                test_particles = np.array([
                    [25.0, 20.0, 15.0, 10.0, 40.0, 3.0],
                    [35.0, 30.0, 20.0, 15.0, 60.0, 5.0]
                ])

            with patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch') as mock_sim:
                mock_sim.return_value = (
                    np.linspace(0, 3.0, 301),
                    np.random.RandomState(42).random((len(test_particles), 301, 6)) * 0.1,
                    np.random.RandomState(42).random((len(test_particles), 301)) * 20.0,
                    np.random.RandomState(42).random((len(test_particles), 301)) * 0.5
                )

                fitness = tuner._fitness(test_particles)
                results[controller_type] = {
                    'fitness': fitness,
                    'n_particles': len(test_particles),
                    'n_gains': test_particles.shape[1]
                }

        # Validate results for all controller types
        assert len(results) == 3
        for controller_type, result in results.items():
            assert result['fitness'].shape == (result['n_particles'],)
            assert np.all(np.isfinite(result['fitness']))

    def test_uncertainty_robustness_analysis(self, framework_config, multi_controller_factory):
        """Test optimization robustness under uncertainty."""
        # Create controller factory
        def controller_factory(gains):
            return multi_controller_factory(gains, "classical_smc")

        tuner = PSOTuner(
            controller_factory=controller_factory,
            config=framework_config,
            seed=12345
        )

        # Test with uncertainty evaluation
        test_particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 1.0],
            [15.0, 12.0, 7.0, 5.0, 30.0, 2.0],
            [8.0, 6.0, 4.0, 2.0, 15.0, 0.5]
        ])

        # Mock multiple uncertainty draws
        def uncertainty_simulation(*args, **kwargs):
            n_draws = 5
            results = []
            for draw in range(n_draws):
                t = np.linspace(0, 3.0, 301)
                # Different results for each uncertainty draw
                x = np.random.RandomState(42 + draw).random((3, 301, 6)) * (0.1 + 0.02 * draw)
                u = np.random.RandomState(42 + draw).random((3, 301)) * (20.0 + 2.0 * draw)
                sigma = np.random.RandomState(42 + draw).random((3, 301)) * (0.5 + 0.1 * draw)
                results.append((t, x, u, sigma))
            return results

        with patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch') as mock_sim:
            mock_sim.side_effect = uncertainty_simulation

            fitness = tuner._fitness(test_particles)

            # Should handle uncertainty properly
            assert fitness.shape == (3,)
            assert np.all(np.isfinite(fitness))

            # Fitness should reflect worst-case + mean combination
            assert np.all(fitness > 0)

    def test_optimization_algorithm_benchmarking(self, framework_config, multi_controller_factory):
        """Test algorithm benchmarking and comparison framework."""
        def controller_factory(gains):
            return multi_controller_factory(gains, "classical_smc")

        # Test different PSO configurations
        pso_configs = [
            {"w": 0.4, "c1": 1.5, "c2": 1.5, "name": "Conservative"},
            {"w": 0.8, "c1": 2.0, "c2": 2.0, "name": "Aggressive"},
            {"w": 0.6, "c1": 1.8, "c2": 1.2, "name": "Balanced"}
        ]

        benchmark_results = {}

        for config in pso_configs:
            # Modify PSO parameters
            test_config = framework_config
            test_config.pso.w = config["w"]
            test_config.pso.c1 = config["c1"]
            test_config.pso.c2 = config["c2"]

            tuner = PSOTuner(
                controller_factory=controller_factory,
                config=test_config,
                seed=12345
            )

            # Benchmark fitness evaluation
            test_particles = np.random.RandomState(12345).random((10, 6)) * 20.0 + 1.0

            with patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch') as mock_sim:
                mock_sim.return_value = (
                    np.linspace(0, 3.0, 301),
                    np.random.RandomState(42).random((10, 301, 6)) * 0.1,
                    np.random.RandomState(42).random((10, 301)) * 20.0,
                    np.random.RandomState(42).random((10, 301)) * 0.5
                )

                start_time = time.time()
                fitness = tuner._fitness(test_particles)
                elapsed = time.time() - start_time

                benchmark_results[config["name"]] = {
                    'fitness_mean': np.mean(fitness),
                    'fitness_std': np.std(fitness),
                    'elapsed_time': elapsed,
                    'config': {k: v for k, v in config.items() if k != 'name'}
                }

        # Validate benchmark results
        assert len(benchmark_results) == 3
        for name, result in benchmark_results.items():
            assert 'fitness_mean' in result
            assert 'fitness_std' in result
            assert 'elapsed_time' in result
            assert result['elapsed_time'] < 5.0  # Performance requirement

    @patch('pyswarms.single.GlobalBestPSO')
    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_optimization_convergence_analysis(self, mock_simulate, mock_pso_class, framework_config, multi_controller_factory):
        """Test optimization convergence analysis and monitoring."""
        def controller_factory(gains):
            return multi_controller_factory(gains, "classical_smc")

        # Setup convergence simulation
        mock_optimizer = Mock()

        # Simulate convergence behavior
        convergence_history = [5.0, 3.0, 2.2, 1.8, 1.5, 1.4, 1.35, 1.3, 1.29, 1.28]
        best_positions = [np.array([10+i, 8+i*0.1, 5+i*0.05, 3+i*0.02, 20+i*0.5, 1+i*0.01])
                         for i in range(len(convergence_history))]

        mock_optimizer.optimize.return_value = (convergence_history[-1], best_positions[-1])
        mock_optimizer.cost_history = convergence_history
        mock_optimizer.pos_history = best_positions
        mock_optimizer.options = {}
        mock_pso_class.return_value = mock_optimizer

        mock_simulate.return_value = (
            np.linspace(0, 3.0, 301),
            np.random.random((20, 301, 6)) * 0.1,
            np.random.random((20, 301)) * 20.0,
            np.random.random((20, 301)) * 0.5
        )

        tuner = PSOTuner(
            controller_factory=controller_factory,
            config=framework_config,
            seed=12345
        )

        result = tuner.optimise()

        # Analyze convergence
        assert 'history' in result
        convergence_data = result['history']

        # Check convergence properties
        costs = [entry['cost'] for entry in convergence_data]
        assert len(costs) > 5  # Sufficient iterations
        assert costs[0] >= costs[-1]  # Should improve

        # Convergence rate analysis
        improvements = [costs[i] - costs[i+1] for i in range(len(costs)-1)]
        initial_improvement = np.mean(improvements[:3])
        final_improvement = np.mean(improvements[-3:]) if len(improvements) >= 3 else improvements[-1]

        # Should show decreasing improvement (convergence)
        assert initial_improvement >= 0  # Should improve initially
        assert final_improvement < initial_improvement  # Should slow down

    def test_constraint_handling_comprehensive(self, framework_config, multi_controller_factory):
        """Test comprehensive constraint handling mechanisms."""
        def controller_factory(gains):
            return multi_controller_factory(gains, "classical_smc")

        tuner = PSOTuner(
            controller_factory=controller_factory,
            config=framework_config,
            seed=12345
        )

        # Test various constraint violations
        constraint_test_particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 1.0],    # Valid
            [0.0, 8.0, 5.0, 3.0, 20.0, 1.0],     # Zero gain
            [-5.0, 8.0, 5.0, 3.0, 20.0, 1.0],    # Negative gain
            [np.inf, 8.0, 5.0, 3.0, 20.0, 1.0],  # Infinite gain
            [np.nan, 8.0, 5.0, 3.0, 20.0, 1.0],  # NaN gain
            [100.0, 8.0, 5.0, 3.0, 20.0, 1.0],   # Exceeds bounds
            [10.0, 8.0, 5.0, 3.0, 0.5, 1.0],     # Below switching gain minimum
            [10.0, 8.0, 5.0, 3.0, 150.0, 1.0],   # Above switching gain maximum
            [10.0, 8.0, 5.0, 3.0, 20.0, 0.001],  # Boundary layer too small
            [10.0, 8.0, 5.0, 3.0, 20.0, 15.0],   # Boundary layer too large
        ])

        fitness = tuner._fitness(constraint_test_particles)

        # Check constraint enforcement
        penalty = tuner.instability_penalty

        # Valid particle should have finite cost
        assert np.isfinite(fitness[0]) and fitness[0] < penalty

        # Invalid particles should be penalized
        for i in range(1, len(constraint_test_particles)):
            assert fitness[i] == penalty, f"Particle {i} should be penalized but got fitness {fitness[i]}"

    def test_multi_objective_optimization_framework(self, framework_config, multi_controller_factory):
        """Test multi-objective optimization capabilities."""
        def controller_factory(gains):
            return multi_controller_factory(gains, "classical_smc")

        # Test with modified cost function for multi-objective
        config = framework_config
        config.cost_function.weights.state_error = 50.0
        config.cost_function.weights.control_effort = 1.0
        config.cost_function.weights.control_rate = 0.5
        config.cost_function.weights.stability = 2.0

        tuner = PSOTuner(
            controller_factory=controller_factory,
            config=config,
            seed=12345
        )

        # Test particles with different trade-offs
        trade_off_particles = np.array([
            [5.0, 4.0, 3.0, 2.0, 10.0, 0.5],    # Low control effort
            [20.0, 18.0, 15.0, 12.0, 40.0, 3.0], # High control effort, better performance
            [10.0, 8.0, 6.0, 4.0, 25.0, 1.5],   # Balanced
        ])

        with patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch') as mock_sim:
            # Simulate different performance characteristics
            def multi_objective_sim(*args, **kwargs):
                t = np.linspace(0, 3.0, 301)

                # Low effort: higher state error, lower control
                x_low = np.random.random((3, 301, 6)) * 0.2
                u_low = np.random.random((3, 301)) * 8.0
                sigma_low = np.random.random((3, 301)) * 0.8

                # Assign different characteristics to each particle
                x = np.zeros((3, 301, 6))
                u = np.zeros((3, 301))
                sigma = np.zeros((3, 301))

                # Particle 0: Low effort, higher error
                x[0] = x_low[0] * 1.5
                u[0] = u_low[0] * 0.6
                sigma[0] = sigma_low[0] * 1.2

                # Particle 1: High effort, lower error
                x[1] = x_low[1] * 0.5
                u[1] = u_low[1] * 2.0
                sigma[1] = sigma_low[1] * 0.4

                # Particle 2: Balanced
                x[2] = x_low[2]
                u[2] = u_low[2]
                sigma[2] = sigma_low[2]

                return (t, x, u, sigma)

            mock_sim.side_effect = multi_objective_sim

            fitness = tuner._fitness(trade_off_particles)

            # Should reflect trade-offs
            assert fitness.shape == (3,)
            assert np.all(np.isfinite(fitness))

            # Check that different objectives create different fitness values
            assert not np.allclose(fitness, fitness[0])  # Should have different values

    def test_optimization_result_serialization(self, framework_config, multi_controller_factory):
        """Test optimization result serialization and deserialization."""
        def controller_factory(gains):
            return multi_controller_factory(gains, "classical_smc")

        tuner = PSOTuner(
            controller_factory=controller_factory,
            config=framework_config,
            seed=12345
        )

        with patch('pyswarms.single.GlobalBestPSO') as mock_pso:
            mock_optimizer = Mock()

            # Create realistic optimization result
            best_gains = np.array([12.5, 9.3, 6.7, 4.2, 28.1, 1.8])
            best_cost = 1.234
            convergence_history = [5.0, 3.2, 2.1, 1.7, 1.4, 1.234]

            mock_optimizer.optimize.return_value = (best_cost, best_gains)
            mock_optimizer.cost_history = convergence_history
            mock_optimizer.pos_history = [best_gains]
            mock_optimizer.options = {}
            mock_pso.return_value = mock_optimizer

            with patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch'):
                result = tuner.optimise()

            # Test serialization
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump({
                    'best_cost': float(result['best_cost']),
                    'best_pos': result['best_pos'].tolist(),
                    'convergence': [float(x) for x in convergence_history],
                    'config': {
                        'n_particles': framework_config.pso.n_particles,
                        'iterations': framework_config.pso.iters,
                        'seed': framework_config.global_seed
                    }
                }, f)
                temp_path = f.name

            # Test deserialization
            with open(temp_path, 'r') as f:
                loaded_result = json.load(f)

            # Validate serialized data
            assert loaded_result['best_cost'] == result['best_cost']
            np.testing.assert_array_almost_equal(loaded_result['best_pos'], result['best_pos'])
            assert loaded_result['config']['seed'] == framework_config.global_seed

            # Cleanup
            Path(temp_path).unlink()

    def test_optimization_performance_profiling(self, framework_config, multi_controller_factory):
        """Test optimization performance profiling and bottleneck analysis."""
        def controller_factory(gains):
            return multi_controller_factory(gains, "classical_smc")

        tuner = PSOTuner(
            controller_factory=controller_factory,
            config=framework_config,
            seed=12345
        )

        # Profile fitness evaluation
        test_particles = np.random.RandomState(12345).random((50, 6)) * 20.0 + 1.0

        performance_metrics = {}

        with patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch') as mock_sim:
            def timed_simulation(*args, **kwargs):
                start = time.time()
                result = (
                    np.linspace(0, 3.0, 301),
                    np.random.random((50, 301, 6)) * 0.1,
                    np.random.random((50, 301)) * 20.0,
                    np.random.random((50, 301)) * 0.5
                )
                elapsed = time.time() - start
                performance_metrics['simulation_time'] = elapsed
                return result

            mock_sim.side_effect = timed_simulation

            # Profile total fitness evaluation
            start_time = time.time()
            tuner._fitness(test_particles)
            total_time = time.time() - start_time

            performance_metrics.update({
                'total_time': total_time,
                'time_per_particle': total_time / len(test_particles),
                'particles_per_second': len(test_particles) / total_time
            })

        # Validate performance
        assert performance_metrics['total_time'] < 10.0  # Should complete within 10 seconds
        assert performance_metrics['time_per_particle'] < 0.2  # Max 200ms per particle
        assert performance_metrics['particles_per_second'] > 5.0  # Min 5 particles/second

    def test_optimization_error_recovery(self, framework_config, multi_controller_factory):
        """Test optimization error recovery and resilience."""
        def controller_factory(gains):
            return multi_controller_factory(gains, "classical_smc")

        tuner = PSOTuner(
            controller_factory=controller_factory,
            config=framework_config,
            seed=12345
        )

        # Test recovery from various error conditions
        test_particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 1.0],
            [15.0, 12.0, 7.0, 5.0, 30.0, 2.0]
        ])

        # Test simulation failure recovery
        call_count = [0]
        def failing_then_succeeding_simulation(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("Temporary simulation failure")
            else:
                return (
                    np.linspace(0, 3.0, 301),
                    np.random.random((2, 301, 6)) * 0.1,
                    np.random.random((2, 301)) * 20.0,
                    np.random.random((2, 301)) * 0.5
                )

        with patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch') as mock_sim:
            mock_sim.side_effect = failing_then_succeeding_simulation

            # First call should fail
            with pytest.raises(RuntimeError):
                tuner._fitness(test_particles)

            # Reset for second call
            call_count[0] = 1  # Will succeed on next call
            fitness = tuner._fitness(test_particles)
            assert fitness.shape == (2,)
            assert np.all(np.isfinite(fitness))

    def test_optimization_memory_efficiency(self, framework_config, multi_controller_factory):
        """Test optimization memory efficiency with large problems."""
        def controller_factory(gains):
            return multi_controller_factory(gains, "classical_smc")

        tuner = PSOTuner(
            controller_factory=controller_factory,
            config=framework_config,
            seed=12345
        )

        # Test with large particle sets
        large_particles = np.random.RandomState(12345).random((200, 6)) * 20.0 + 1.0

        with patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch') as mock_sim:
            # Simulate memory-efficient batch processing
            def batch_simulation(*args, **kwargs):
                particles = kwargs.get('particles', args[1])
                batch_size = len(particles)

                # Process in smaller batches to simulate memory efficiency
                if batch_size > 100:
                    # Split into smaller batches
                    results = []
                    for i in range(0, batch_size, 50):
                        batch_end = min(i + 50, batch_size)
                        batch_particles = particles[i:batch_end]

                        t = np.linspace(0, 3.0, 301)
                        x = np.random.random((len(batch_particles), 301, 6)) * 0.1
                        u = np.random.random((len(batch_particles), 301)) * 20.0
                        sigma = np.random.random((len(batch_particles), 301)) * 0.5

                        results.append((t, x, u, sigma))

                    # Combine results
                    t = results[0][0]
                    x_combined = np.concatenate([r[1] for r in results], axis=0)
                    u_combined = np.concatenate([r[2] for r in results], axis=0)
                    sigma_combined = np.concatenate([r[3] for r in results], axis=0)

                    return (t, x_combined, u_combined, sigma_combined)
                else:
                    t = np.linspace(0, 3.0, 301)
                    x = np.random.random((batch_size, 301, 6)) * 0.1
                    u = np.random.random((batch_size, 301)) * 20.0
                    sigma = np.random.random((batch_size, 301)) * 0.5
                    return (t, x, u, sigma)

            mock_sim.side_effect = batch_simulation

            # Should handle large particle sets efficiently
            fitness = tuner._fitness(large_particles)

            assert fitness.shape == (200,)
            assert np.all(np.isfinite(fitness))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])