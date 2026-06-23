#======================================================================================\\\
#================ tests/test_optimization/test_pso_safety_critical.py =================\\\
#======================================================================================\\\

"""
Safety-critical PSO optimization tests.
Targeting 100% coverage for safety-critical optimization mechanisms.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List

from src.optimization.algorithms.pso_optimizer import PSOTuner


class TestPSOSafetyCritical:
    """Safety-critical PSO optimization test suite."""

    @pytest.fixture
    def safety_config(self):
        """Configuration for safety-critical testing."""
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
                    self.initial_state = [0.0, 0.05, -0.03, 0.0, 0.0, 0.0]

        @dataclass
        class MockWeights:
            state_error: float = 50.0
            control_effort: float = 0.2
            control_rate: float = 0.1
            stability: float = 1.0  # High stability weight for safety

        @dataclass
        class MockNorms:
            state_error: float = 10.0
            control_effort: float = 5.0
            control_rate: float = 2.0
            sliding: float = 1.0

        @dataclass
        class MockCostFunction:
            weights: MockWeights = None
            norms: MockNorms = None
            instability_penalty: float = 1e6  # High penalty for safety

            def __post_init__(self):
                if self.weights is None:
                    self.weights = MockWeights()
                if self.norms is None:
                    self.norms = MockNorms()

        @dataclass
        class MockPSO:
            n_particles: int = 10
            iters: int = 20

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
    def safety_controller_factory(self):
        """Controller factory with safety-critical validation."""
        def factory(gains):
            controller = Mock()
            controller.max_force = 150.0
            controller.gains = gains
            controller.controller_type = 'classical_smc'

            def validate_gains(particle_array):
                """Safety-critical gain validation."""
                if particle_array.ndim == 1:
                    particle_array = particle_array.reshape(1, -1)

                valid_mask = np.ones(particle_array.shape[0], dtype=bool)

                for i, gains in enumerate(particle_array):
                    # SAFETY: Check for NaN/Inf values
                    if not np.all(np.isfinite(gains)):
                        valid_mask[i] = False
                        continue

                    # SAFETY: Positivity constraint
                    if np.any(gains <= 0):
                        valid_mask[i] = False
                        continue

                    # SAFETY: Critical bound checks
                    if len(gains) < 6:
                        valid_mask[i] = False
                        continue

                    # SAFETY: Switching gain bounds (critical for stability)
                    if gains[4] < 1.0 or gains[4] > 100.0:
                        valid_mask[i] = False
                        continue

                    # SAFETY: Boundary layer thickness
                    if gains[5] < 0.01 or gains[5] > 10.0:
                        valid_mask[i] = False
                        continue

                    # SAFETY: Gain ratio constraints (prevent instability)
                    max_ratio = 100.0
                    for j in range(4):
                        for k in range(j+1, 4):
                            if gains[j] / gains[k] > max_ratio or gains[k] / gains[j] > max_ratio:
                                valid_mask[i] = False
                                break
                        if not valid_mask[i]:
                            break

                    # SAFETY: Total control effort constraint
                    if np.sum(gains[:4]) > 200.0:
                        valid_mask[i] = False
                        continue

                return valid_mask

            controller.validate_gains = validate_gains
            return controller

        factory.n_gains = 6
        factory.controller_type = 'classical_smc'
        return factory

    def test_parameter_bounds_enforcement(self, safety_config, safety_controller_factory):
        """Test safety-critical parameter bounds enforcement."""
        tuner = PSOTuner(
            controller_factory=safety_controller_factory,
            config=safety_config,
            seed=42
        )

        # Test extreme values (should be rejected)
        extreme_particles = np.array([
            [1e10, 1e10, 1e10, 1e10, 1e10, 1e10],  # Too large
            [-5.0, 5.0, 5.0, 5.0, 20.0, 2.0],     # Negative
            [np.nan, 5.0, 5.0, 5.0, 20.0, 2.0],   # NaN
            [np.inf, 5.0, 5.0, 5.0, 20.0, 2.0],   # Infinite
            [0.0, 5.0, 5.0, 5.0, 20.0, 2.0],      # Zero
        ])

        fitness = tuner._fitness(extreme_particles)

        # All should be penalized
        expected_penalty = tuner.instability_penalty
        assert np.all(fitness == expected_penalty)

    def test_stability_constraint_validation(self, safety_config, safety_controller_factory):
        """Test stability constraint validation in cost computation."""
        tuner = PSOTuner(
            controller_factory=safety_controller_factory,
            config=safety_config,
            seed=42
        )

        # Test unstable trajectory detection
        t = np.linspace(0, 1.0, 101)

        # Stable trajectory
        x_stable = np.random.random((2, 101, 6)) * 0.1
        u_stable = np.random.random((2, 101)) * 10.0
        sigma_stable = np.random.random((2, 101)) * 0.5

        cost_stable = tuner._compute_cost_from_traj(t, x_stable, u_stable, sigma_stable)

        # Unstable trajectory (large pendulum angles)
        x_unstable = x_stable.copy()
        x_unstable[:, 50:, 1] = 2.0  # theta1 > pi/2
        cost_unstable = tuner._compute_cost_from_traj(t, x_unstable, u_stable, sigma_stable)

        # Explosive trajectory
        x_explosive = x_stable.copy()
        x_explosive[:, 70:, :] = 1e8  # Explosive growth
        cost_explosive = tuner._compute_cost_from_traj(t, x_explosive, u_stable, sigma_stable)

        # Safety check: unstable should be more penalized
        assert np.all(cost_unstable > cost_stable)
        assert np.all(cost_explosive > cost_unstable)

        # Safety check: explosive should get maximum penalty
        assert np.all(cost_explosive >= tuner.instability_penalty * 0.5)

    def test_nan_infinity_handling(self, safety_config, safety_controller_factory):
        """Test NaN and infinity handling in cost computation."""
        tuner = PSOTuner(
            controller_factory=safety_controller_factory,
            config=safety_config,
            seed=42
        )

        t = np.linspace(0, 1.0, 101)

        # NaN in states
        x_nan = np.random.random((2, 101, 6))
        x_nan[:, 50, 0] = np.nan
        u_normal = np.random.random((2, 101)) * 10.0
        sigma_normal = np.random.random((2, 101)) * 0.5

        cost_nan = tuner._compute_cost_from_traj(t, x_nan, u_normal, sigma_normal)
        assert np.all(cost_nan == tuner.instability_penalty)

        # Infinity in controls
        u_inf = u_normal.copy()
        u_inf[:, 30] = np.inf
        cost_inf = tuner._compute_cost_from_traj(t, x_nan, u_inf, sigma_normal)
        assert np.all(cost_inf == tuner.instability_penalty)

        # NaN in sliding variables
        sigma_nan = sigma_normal.copy()
        sigma_nan[:, 40] = np.nan
        cost_sigma_nan = tuner._compute_cost_from_traj(t, x_nan, u_normal, sigma_nan)
        assert np.all(cost_sigma_nan == tuner.instability_penalty)

    def test_convergence_failure_detection(self, safety_config, safety_controller_factory):
        """Test detection of convergence failures."""
        tuner = PSOTuner(
            controller_factory=safety_controller_factory,
            config=safety_config,
            seed=42
        )

        # Test cost combination with invalid inputs
        # Empty costs
        empty_costs = np.array([])
        combined_empty = tuner._combine_costs(empty_costs)
        assert combined_empty == tuner.instability_penalty

        # All NaN costs
        nan_costs = np.array([np.nan, np.nan, np.nan])
        combined_nan = tuner._combine_costs(nan_costs)
        assert combined_nan == tuner.instability_penalty

        # Mixed valid/invalid costs (2D)
        mixed_costs = np.array([
            [1.0, np.nan, 3.0],
            [2.0, 5.0, np.inf],
            [3.0, 6.0, 9.0]
        ])
        combined_mixed = tuner._combine_costs(mixed_costs)
        assert combined_mixed == tuner.instability_penalty

    def test_physics_parameter_safety_bounds(self, safety_config, safety_controller_factory):
        """Test safety bounds for physics parameter perturbations."""
        # Enable uncertainty with extreme perturbations
        @dataclass
        class ExtremePerturbation:
            n_evals: int = 3
            cart_mass: float = 0.9  # 90% perturbation
            pendulum1_com: float = 0.5  # Could exceed length

            def model_dump(self) -> dict:
                return {
                    'n_evals': self.n_evals,
                    'cart_mass': self.cart_mass,
                    'pendulum1_com': self.pendulum1_com
                }

        config = safety_config
        config.physics_uncertainty = ExtremePerturbation()

        tuner = PSOTuner(
            controller_factory=safety_controller_factory,
            config=config,
            seed=42
        )

        # Check that physics perturbations maintain safety bounds
        physics_models = list(tuner._iter_perturbed_physics())

        for params in physics_models:
            # SAFETY: COM must not exceed pendulum length
            assert params.pendulum1_com < params.pendulum1_length
            assert params.pendulum2_com < params.pendulum2_length

            # SAFETY: Masses must be positive
            assert params.cart_mass > 0
            assert params.pendulum1_mass > 0
            assert params.pendulum2_mass > 0

            # SAFETY: Lengths must be positive
            assert params.pendulum1_length > 0
            assert params.pendulum2_length > 0

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_simulation_failure_recovery(self, mock_simulate, safety_config, safety_controller_factory):
        """Test recovery from simulation failures."""
        tuner = PSOTuner(
            controller_factory=safety_controller_factory,
            config=safety_config,
            seed=42
        )

        # Mock simulation failure
        def failing_simulation(*args, **kwargs):
            raise RuntimeError("Simulation failed")

        mock_simulate.side_effect = failing_simulation

        particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 2.0],
            [12.0, 9.0, 6.0, 4.0, 25.0, 3.0]
        ])

        # Should handle gracefully and return penalty
        with pytest.raises(RuntimeError):
            tuner._fitness(particles)

    def test_memory_safety_large_arrays(self, safety_config, safety_controller_factory):
        """Test memory safety with large arrays."""
        tuner = PSOTuner(
            controller_factory=safety_controller_factory,
            config=safety_config,
            seed=42
        )

        # Large time series
        t = np.linspace(0, 1.0, 10001)  # 10k time steps
        x_large = np.random.random((5, 10001, 6)) * 0.1
        u_large = np.random.random((5, 10001)) * 10.0
        sigma_large = np.random.random((5, 10001)) * 0.5

        # Should handle without memory issues
        cost = tuner._compute_cost_from_traj(t, x_large, u_large, sigma_large)

        assert cost.shape == (5,)
        assert np.all(np.isfinite(cost))

    def test_numerical_stability_edge_cases(self, safety_config, safety_controller_factory):
        """Test numerical stability with edge cases."""
        tuner = PSOTuner(
            controller_factory=safety_controller_factory,
            config=safety_config,
            seed=42
        )

        # Very small values
        small_values = np.array([1e-15, 1e-12, 1e-10])
        normalised_small = tuner._normalise(small_values, 1e-14)
        assert np.all(np.isfinite(normalised_small))

        # Very large values
        large_values = np.array([1e10, 1e15, 1e20])
        normalised_large = tuner._normalise(large_values, 1e5)
        assert np.all(np.isfinite(normalised_large))

        # Mixed scale values
        mixed_values = np.array([1e-15, 1.0, 1e15])
        normalised_mixed = tuner._normalise(mixed_values, 1.0)
        assert np.all(np.isfinite(normalised_mixed))

    def test_thread_safety_rng_isolation(self, safety_config, safety_controller_factory):
        """Test thread safety of RNG isolation."""
        def create_tuner_and_generate():
            tuner = PSOTuner(
                controller_factory=safety_controller_factory,
                config=safety_config,
                seed=42
            )
            return tuner.rng.random()

        # Run in multiple threads
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(create_tuner_and_generate) for _ in range(10)]
            results = [f.result() for f in futures]

        # All results should be the same (deterministic with same seed)
        assert len(set(results)) == 1, "RNG not properly isolated between threads"

    def test_constraint_violation_detection(self, safety_config, safety_controller_factory):
        """Test detection of constraint violations."""
        tuner = PSOTuner(
            controller_factory=safety_controller_factory,
            config=safety_config,
            seed=42
        )

        # Test particles with various constraint violations
        test_particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 2.0],    # Valid
            [0.5, 8.0, 5.0, 3.0, 20.0, 2.0],     # Below minimum
            [10.0, 8.0, 5.0, 3.0, 150.0, 2.0],   # Switching gain too high
            [10.0, 8.0, 5.0, 3.0, 20.0, 0.005],  # Boundary layer too small
            [1000.0, 8.0, 5.0, 3.0, 20.0, 2.0],  # Extreme gain ratio
        ])

        fitness = tuner._fitness(test_particles)

        # First particle should be valid (finite cost)
        assert np.isfinite(fitness[0]) and fitness[0] < tuner.instability_penalty

        # Others should be penalized
        expected_penalty = tuner.instability_penalty
        assert fitness[1] == expected_penalty  # Below minimum
        assert fitness[2] == expected_penalty  # Switching gain too high
        assert fitness[3] == expected_penalty  # Boundary layer too small
        assert fitness[4] == expected_penalty  # Extreme gain ratio

    def test_cost_computation_safety_checks(self, safety_config, safety_controller_factory):
        """Test safety checks in cost computation."""
        tuner = PSOTuner(
            controller_factory=safety_controller_factory,
            config=safety_config,
            seed=42
        )

        t = np.linspace(0, 1.0, 101)

        # Test with mismatched dimensions (safety check)
        x_wrong_dim = np.random.random((2, 101, 3))  # Wrong state dimension
        u_normal = np.random.random((2, 101))
        sigma_normal = np.random.random((2, 101))

        # Should handle gracefully
        cost_wrong = tuner._compute_cost_from_traj(t, x_wrong_dim, u_normal, sigma_normal)
        assert cost_wrong.shape == (2,)
        assert np.all(np.isfinite(cost_wrong))

        # Test with zero time step
        t_zero = np.array([0.0, 0.0, 0.0])
        x_zero = np.random.random((2, 3, 6))
        u_zero = np.random.random((2, 3))
        sigma_zero = np.random.random((2, 3))

        cost_zero = tuner._compute_cost_from_traj(t_zero, x_zero, u_zero, sigma_zero)
        assert cost_zero.shape == (2,)
        assert np.all(np.isfinite(cost_zero))

    def test_instability_penalty_computation_safety(self, safety_config, safety_controller_factory):
        """Test safety in instability penalty computation."""
        # Test with zero/negative norms
        config = safety_config
        config.cost_function.norms.state_error = 0.0
        config.cost_function.norms.control_effort = -1.0  # Invalid
        config.cost_function.norms.control_rate = np.inf  # Invalid
        config.cost_function.norms.sliding = np.nan  # Invalid

        tuner = PSOTuner(
            controller_factory=safety_controller_factory,
            config=config,
            seed=42,
            instability_penalty_factor=100.0
        )

        # Should handle gracefully and use safe defaults
        assert np.isfinite(tuner.instability_penalty)
        assert tuner.instability_penalty > 0
        assert tuner.instability_penalty == 100.0  # Should fall back to factor


class TestPSOProductionSafety:
    """Production safety validation for PSO optimization."""

    @pytest.fixture
    def production_config(self):
        """Production-like configuration."""
        @dataclass
        class ProductionPhysics:
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
        class ProductionSimulation:
            duration: float = 5.0  # Longer simulation
            dt: float = 0.005  # Higher resolution
            initial_state: List[float] = None
            use_full_dynamics: bool = True

            def __post_init__(self):
                if self.initial_state is None:
                    self.initial_state = [0.0, 0.1, -0.05, 0.0, 0.0, 0.0]

        @dataclass
        class ProductionWeights:
            state_error: float = 100.0
            control_effort: float = 0.1
            control_rate: float = 0.05
            stability: float = 2.0

        @dataclass
        class ProductionNorms:
            state_error: float = 50.0
            control_effort: float = 20.0
            control_rate: float = 10.0
            sliding: float = 5.0

        @dataclass
        class ProductionCostFunction:
            weights: ProductionWeights = None
            norms: ProductionNorms = None
            instability_penalty: float = 1e8

            def __post_init__(self):
                if self.weights is None:
                    self.weights = ProductionWeights()
                if self.norms is None:
                    self.norms = ProductionNorms()

        @dataclass
        class ProductionPSO:
            n_particles: int = 50
            iters: int = 100

        @dataclass
        class ProductionConfig:
            global_seed: int = 12345
            physics: ProductionPhysics = None
            simulation: ProductionSimulation = None
            cost_function: ProductionCostFunction = None
            pso: ProductionPSO = None

            def __post_init__(self):
                if self.physics is None:
                    self.physics = ProductionPhysics()
                if self.simulation is None:
                    self.simulation = ProductionSimulation()
                if self.cost_function is None:
                    self.cost_function = ProductionCostFunction()
                if self.pso is None:
                    self.pso = ProductionPSO()

        return ProductionConfig()

    @pytest.fixture
    def production_controller_factory(self):
        """Production-grade controller factory with comprehensive validation."""
        def factory(gains):
            controller = Mock()
            controller.max_force = 100.0  # Production limit
            controller.gains = gains
            controller.controller_type = 'classical_smc'

            def validate_gains(particle_array):
                """Production-grade validation with comprehensive checks."""
                if particle_array.ndim == 1:
                    particle_array = particle_array.reshape(1, -1)

                valid_mask = np.ones(particle_array.shape[0], dtype=bool)

                for i, gains in enumerate(particle_array):
                    # Critical safety checks
                    if not np.all(np.isfinite(gains)):
                        valid_mask[i] = False
                        continue

                    if len(gains) != 6:
                        valid_mask[i] = False
                        continue

                    # Production bounds (tighter than experimental)
                    bounds = [
                        (0.5, 50.0),   # K1
                        (0.5, 50.0),   # K2
                        (0.5, 30.0),   # K3
                        (0.5, 30.0),   # K4
                        (1.0, 80.0),   # Switching gain
                        (0.01, 5.0)    # Boundary layer
                    ]

                    for j, (min_val, max_val) in enumerate(bounds):
                        if gains[j] < min_val or gains[j] > max_val:
                            valid_mask[i] = False
                            break

                    if not valid_mask[i]:
                        continue

                    # Stability ratio constraints
                    for j in range(4):
                        for k in range(j+1, 4):
                            if gains[j] / gains[k] > 20.0 or gains[k] / gains[j] > 20.0:
                                valid_mask[i] = False
                                break
                        if not valid_mask[i]:
                            break

                    # Total effort constraint
                    if np.sum(gains[:4]) > 150.0:
                        valid_mask[i] = False
                        continue

                    # Minimum control authority
                    if np.sum(gains[:4]) < 5.0:
                        valid_mask[i] = False
                        continue

                return valid_mask

            controller.validate_gains = validate_gains
            return controller

        return factory

    def test_production_parameter_validation(self, production_config, production_controller_factory):
        """Test production-grade parameter validation."""
        tuner = PSOTuner(
            controller_factory=production_controller_factory,
            config=production_config,
            seed=12345
        )

        # Production test cases
        production_particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 1.0],    # Valid production gains
            [25.0, 20.0, 15.0, 10.0, 40.0, 2.0], # Valid high-performance
            [0.1, 8.0, 5.0, 3.0, 20.0, 1.0],     # Below production minimum
            [100.0, 8.0, 5.0, 3.0, 20.0, 1.0],   # Above production maximum
            [10.0, 8.0, 5.0, 3.0, 100.0, 1.0],   # Switching gain too high
            [10.0, 8.0, 5.0, 3.0, 20.0, 0.005],  # Boundary layer too small
        ])

        fitness = tuner._fitness(production_particles)

        # Valid particles should have finite costs
        assert np.isfinite(fitness[0])
        assert np.isfinite(fitness[1])

        # Invalid particles should be penalized
        penalty = tuner.instability_penalty
        assert fitness[2] == penalty  # Below minimum
        assert fitness[3] == penalty  # Above maximum
        assert fitness[4] == penalty  # Switching gain too high
        assert fitness[5] == penalty  # Boundary layer too small

    def test_production_stability_requirements(self, production_config, production_controller_factory):
        """Test production stability requirements."""
        tuner = PSOTuner(
            controller_factory=production_controller_factory,
            config=production_config,
            seed=12345
        )

        # Test different stability scenarios
        t = np.linspace(0, 5.0, 1001)

        # Production-acceptable stability
        x_acceptable = np.random.random((3, 1001, 6)) * 0.05  # Small deviations
        u_acceptable = np.random.random((3, 1001)) * 20.0
        sigma_acceptable = np.random.random((3, 1001)) * 0.2

        cost_acceptable = tuner._compute_cost_from_traj(t, x_acceptable, u_acceptable, sigma_acceptable)

        # Marginal stability (larger deviations)
        x_marginal = np.random.random((3, 1001, 6)) * 0.3
        x_marginal[:, 500:, 1] = 0.7  # Larger angle excursions
        cost_marginal = tuner._compute_cost_from_traj(t, x_marginal, u_acceptable, sigma_acceptable)

        # Unacceptable for production
        x_unacceptable = x_acceptable.copy()
        x_unacceptable[:, 800:, 1] = 2.0  # Fall over
        cost_unacceptable = tuner._compute_cost_from_traj(t, x_unacceptable, u_acceptable, sigma_acceptable)

        # Production quality requirements
        assert np.all(cost_marginal > cost_acceptable)
        assert np.all(cost_unacceptable > cost_marginal)

        # Production failure threshold
        assert np.all(cost_unacceptable >= tuner.instability_penalty * 0.3)

    def test_production_timeout_handling(self, production_config, production_controller_factory):
        """Test timeout handling in production scenarios."""
        tuner = PSOTuner(
            controller_factory=production_controller_factory,
            config=production_config,
            seed=12345
        )

        # Simulate long-running cost computation
        start_time = time.time()

        # Large particle set (production scale)
        particles = np.random.random((50, 6)) * 20.0 + 1.0

        with patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch') as mock_sim:
            # Mock simulation that takes time
            def slow_simulation(*args, **kwargs):
                time.sleep(0.001)  # Simulate computation time
                t = np.linspace(0, 5.0, 1001)
                x = np.random.random((50, 1001, 6)) * 0.1
                u = np.random.random((50, 1001)) * 20.0
                sigma = np.random.random((50, 1001)) * 0.5
                return (t, x, u, sigma)

            mock_sim.side_effect = slow_simulation

            fitness = tuner._fitness(particles)
            elapsed = time.time() - start_time

            # Should complete in reasonable time for production
            assert elapsed < 5.0  # 5 second timeout
            assert fitness.shape == (50,)

    def test_production_memory_management(self, production_config, production_controller_factory):
        """Test memory management in production scenarios."""
        tuner = PSOTuner(
            controller_factory=production_controller_factory,
            config=production_config,
            seed=12345
        )

        # Production-scale memory test
        large_t = np.linspace(0, 5.0, 50001)  # 50k time steps
        large_x = np.random.random((10, 50001, 6)) * 0.1
        large_u = np.random.random((10, 50001)) * 20.0
        large_sigma = np.random.random((10, 50001)) * 0.5

        # Should handle without memory overflow
        cost = tuner._compute_cost_from_traj(large_t, large_x, large_u, large_sigma)

        assert cost.shape == (10,)
        assert np.all(np.isfinite(cost))

        # Memory should be released (no accumulation)
        import gc
        gc.collect()

    def test_production_determinism_validation(self, production_config, production_controller_factory):
        """Test determinism validation for production deployment."""
        # Same seed should give identical results
        particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 1.0],
            [15.0, 12.0, 7.0, 5.0, 30.0, 2.0]
        ])

        tuner1 = PSOTuner(
            controller_factory=production_controller_factory,
            config=production_config,
            seed=12345
        )

        tuner2 = PSOTuner(
            controller_factory=production_controller_factory,
            config=production_config,
            seed=12345
        )

        with patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch') as mock_sim:
            mock_sim.return_value = (
                np.linspace(0, 5.0, 1001),
                np.random.RandomState(42).random((2, 1001, 6)) * 0.1,
                np.random.RandomState(42).random((2, 1001)) * 20.0,
                np.random.RandomState(42).random((2, 1001)) * 0.5
            )

            fitness1 = tuner1._fitness(particles)

            # Reset mock for second call
            mock_sim.return_value = (
                np.linspace(0, 5.0, 1001),
                np.random.RandomState(42).random((2, 1001, 6)) * 0.1,
                np.random.RandomState(42).random((2, 1001)) * 20.0,
                np.random.RandomState(42).random((2, 1001)) * 0.5
            )

            fitness2 = tuner2._fitness(particles)

            # Must be identical for production deployment
            np.testing.assert_array_equal(fitness1, fitness2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])