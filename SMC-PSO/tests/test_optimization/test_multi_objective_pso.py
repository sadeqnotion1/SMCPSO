#======================================================================================\\\
#================ tests/test_optimization/test_multi_objective_pso.py =================\\\
#======================================================================================\\\

"""
Multi-objective PSO optimization tests and Pareto front analysis.
Tests NSGA-II integration, Pareto dominance, and hypervolume calculation.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import List

from src.optimization.algorithms.pso_optimizer import PSOTuner


class TestMultiObjectivePSO:
    """Test multi-objective PSO optimization capabilities."""

    @pytest.fixture
    def multi_objective_config(self):
        """Configuration for multi-objective optimization testing."""
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
            duration: float = 2.0
            dt: float = 0.01
            initial_state: List[float] = None

            def __post_init__(self):
                if self.initial_state is None:
                    self.initial_state = [0.0, 0.05, -0.03, 0.0, 0.0, 0.0]

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
            iters: int = 30

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
    def multi_objective_controller_factory(self):
        """Controller factory for multi-objective optimization."""
        def factory(gains):
            controller = Mock()
            controller.max_force = 150.0
            controller.gains = gains
            controller.controller_type = 'classical_smc'
            return controller

        factory.n_gains = 6
        factory.controller_type = 'classical_smc'
        return factory

    def create_multi_objective_simulation_mock(self):
        """Create simulation mock for multi-objective testing."""
        def mock_simulate(*args, **kwargs):
            particles = args[1] if len(args) > 1 else kwargs.get('particles')
            particles.shape[0]
            n_timesteps = 201

            t = np.linspace(0, 2.0, n_timesteps)

            all_x, all_u, all_sigma = [], [], []

            for i, particle in enumerate(particles):
                # Generate trajectories with trade-offs
                # Performance vs efficiency trade-off based on gains
                performance_factor = np.mean(particle[:4])  # Position/velocity gains
                efficiency_factor = 1.0 / (1.0 + particle[4])  # Inverse switching gain

                # State trajectory
                x = np.zeros((n_timesteps, 6))
                x[0] = [0.0, 0.05, -0.03, 0.0, 0.0, 0.0]

                for t_idx in range(1, n_timesteps):
                    # Performance-efficiency trade-off
                    decay_rate = 0.01 + 0.02 * performance_factor / 20.0
                    noise_level = 0.001 * efficiency_factor

                    x[t_idx] = x[t_idx-1] * (1 - decay_rate) + \
                               np.random.normal(0, noise_level, 6)

                # Control trajectory
                u = np.zeros(n_timesteps)
                for t_idx in range(n_timesteps):
                    control_magnitude = performance_factor * np.linalg.norm(x[t_idx, 2:])
                    u[t_idx] = control_magnitude + 0.1 * np.random.normal()

                # Sliding variable
                sigma = np.zeros(n_timesteps)
                for t_idx in range(n_timesteps):
                    sigma[t_idx] = np.sum(particle[:2] * x[t_idx, 2:4]) + \
                                   np.sum(particle[2:4] * x[t_idx, 4:6])

                all_x.append(x)
                all_u.append(u)
                all_sigma.append(sigma)

            x_batch = np.array(all_x)
            u_batch = np.array(all_u)
            sigma_batch = np.array(all_sigma)

            return (t, x_batch, u_batch, sigma_batch)

        return mock_simulate

    def test_pareto_dominance_detection(self):
        """Test Pareto dominance relationship detection."""

        def pareto_dominates(obj_a, obj_b):
            """Test if objective vector a dominates vector b."""
            # a dominates b if: a_i <= b_i for all i, and a_j < b_j for at least one j
            better_or_equal = np.all(obj_a <= obj_b)
            strictly_better = np.any(obj_a < obj_b)
            return better_or_equal and strictly_better

        def find_non_dominated(objectives):
            """Find non-dominated solutions (Pareto front)."""
            n_solutions = objectives.shape[0]
            dominated = np.zeros(n_solutions, dtype=bool)

            for i in range(n_solutions):
                for j in range(n_solutions):
                    if i != j and pareto_dominates(objectives[j], objectives[i]):
                        dominated[i] = True
                        break

            return ~dominated

        # Test dominance relationships
        obj_a = np.array([1.0, 2.0])  # Better in both objectives
        obj_b = np.array([2.0, 3.0])
        assert pareto_dominates(obj_a, obj_b)
        assert not pareto_dominates(obj_b, obj_a)

        # Test non-dominated case
        obj_c = np.array([0.5, 4.0])  # Better in first, worse in second
        obj_d = np.array([2.0, 1.0])  # Worse in first, better in second
        assert not pareto_dominates(obj_c, obj_d)
        assert not pareto_dominates(obj_d, obj_c)

        # Test Pareto front identification
        objectives = np.array([
            [1.0, 4.0],  # Non-dominated
            [2.0, 3.0],  # Non-dominated
            [3.0, 2.0],  # Non-dominated
            [4.0, 1.0],  # Non-dominated
            [2.5, 3.5],  # Dominated by [2.0, 3.0]
            [1.5, 4.5],  # Dominated by [1.0, 4.0]
        ])

        non_dominated = find_non_dominated(objectives)
        expected_non_dominated = np.array([True, True, True, True, False, False])
        np.testing.assert_array_equal(non_dominated, expected_non_dominated)

    def test_crowding_distance_calculation(self):
        """Test crowding distance calculation for diversity preservation."""

        def calculate_crowding_distance(objectives):
            """Calculate crowding distance for objective vectors."""
            n_solutions, n_objectives = objectives.shape
            distances = np.zeros(n_solutions)

            for obj_idx in range(n_objectives):
                # Sort by objective value
                obj_values = objectives[:, obj_idx]
                sorted_indices = np.argsort(obj_values)

                # Boundary solutions get infinite distance
                distances[sorted_indices[0]] = float('inf')
                distances[sorted_indices[-1]] = float('inf')

                # Calculate normalized distances for intermediate solutions
                obj_range = obj_values.max() - obj_values.min()
                if obj_range > 0:
                    for i in range(1, n_solutions - 1):
                        idx = sorted_indices[i]
                        next_idx = sorted_indices[i + 1]
                        prev_idx = sorted_indices[i - 1]

                        distance = (obj_values[next_idx] - obj_values[prev_idx]) / obj_range
                        distances[idx] += distance

            return distances

        # Test crowding distance calculation
        objectives = np.array([
            [1.0, 4.0],
            [2.0, 3.0],
            [3.0, 2.0],
            [4.0, 1.0],
            [2.5, 2.5],  # Middle solution
        ])

        distances = calculate_crowding_distance(objectives)

        # Boundary solutions should have infinite distance
        assert distances[0] == float('inf')  # [1.0, 4.0]
        assert distances[3] == float('inf')  # [4.0, 1.0]

        # Middle solutions should have finite distances
        assert np.isfinite(distances[1])
        assert np.isfinite(distances[2])
        assert np.isfinite(distances[4])

        # Test with identical objectives
        identical_objectives = np.array([
            [2.0, 2.0],
            [2.0, 2.0],
            [2.0, 2.0],
        ])

        identical_distances = calculate_crowding_distance(identical_objectives)
        # Should handle gracefully (no division by zero)
        assert np.all(np.isfinite(identical_distances))

    def test_hypervolume_calculation(self):
        """Test hypervolume calculation for Pareto front quality assessment."""

        def calculate_hypervolume_2d(pareto_front, reference_point):
            """Calculate 2D hypervolume of Pareto front."""
            if len(pareto_front) == 0:
                return 0.0

            # Sort by first objective
            sorted_front = pareto_front[np.argsort(pareto_front[:, 0])]

            hypervolume = 0.0
            prev_x = reference_point[0]

            for point in sorted_front:
                if point[0] < reference_point[0] and point[1] < reference_point[1]:
                    width = point[0] - prev_x
                    height = reference_point[1] - point[1]
                    hypervolume += width * height
                    prev_x = point[0]

            return hypervolume

        # Test hypervolume calculation
        pareto_front = np.array([
            [1.0, 4.0],
            [2.0, 3.0],
            [3.0, 2.0],
            [4.0, 1.0],
        ])

        reference_point = np.array([5.0, 5.0])
        hypervolume = calculate_hypervolume_2d(pareto_front, reference_point)

        # Should be positive for valid Pareto front
        assert hypervolume > 0

        # Test with single point
        single_point = np.array([[2.0, 3.0]])
        single_hv = calculate_hypervolume_2d(single_point, reference_point)
        (2.0 - 5.0) * (5.0 - 3.0)  # Should be negative area
        assert single_hv >= 0  # Implementation should handle this case

        # Test with empty front
        empty_front = np.array([]).reshape(0, 2)
        empty_hv = calculate_hypervolume_2d(empty_front, reference_point)
        assert empty_hv == 0.0

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_multi_objective_fitness_evaluation(self, mock_simulate, multi_objective_config, multi_objective_controller_factory):
        """Test multi-objective fitness evaluation."""
        mock_simulate.side_effect = self.create_multi_objective_simulation_mock()

        # Create multi-objective PSO tuner
        tuner = PSOTuner(
            controller_factory=multi_objective_controller_factory,
            config=multi_objective_config,
            seed=42
        )

        # Define multiple objectives
        def objective_1_stability(t, x, u, sigma):
            """Stability objective (minimize state error)."""
            dt = np.diff(t)
            dt_b = dt[None, :]
            return np.sum((x[:, :-1, :] ** 2 * dt_b[:, :, None]), axis=(1, 2))

        def objective_2_efficiency(t, x, u, sigma):
            """Efficiency objective (minimize control effort)."""
            dt = np.diff(t)
            dt_b = dt[None, :]
            return np.sum((u[:, :-1] ** 2 * dt_b), axis=1)

        def objective_3_robustness(t, x, u, sigma):
            """Robustness objective (minimize sliding variable)."""
            dt = np.diff(t)
            dt_b = dt[None, :]
            return np.sum((sigma[:, :-1] ** 2 * dt_b), axis=1)

        # Test particles
        particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 2.0],   # Balanced
            [15.0, 12.0, 8.0, 6.0, 30.0, 3.0],  # High performance
            [5.0, 4.0, 2.0, 1.0, 10.0, 1.0],    # Low control effort
            [8.0, 6.0, 4.0, 2.0, 40.0, 4.0],    # High robustness
        ])

        # Evaluate fitness for multi-objective scenario
        # (This would be modified version of _fitness method)
        fitness_values = tuner._fitness(particles)

        assert fitness_values.shape == (4,)
        assert np.all(np.isfinite(fitness_values))

        # For actual multi-objective, we would need separate objective values
        # Here we simulate the computation
        t = np.linspace(0, 2.0, 201)
        x_sim = np.random.random((4, 201, 6)) * 0.1
        u_sim = np.random.random((4, 201)) * 10.0
        sigma_sim = np.random.random((4, 201)) * 0.5

        obj1_values = objective_1_stability(t, x_sim, u_sim, sigma_sim)
        obj2_values = objective_2_efficiency(t, x_sim, u_sim, sigma_sim)
        obj3_values = objective_3_robustness(t, x_sim, u_sim, sigma_sim)

        # Combine objectives into matrix
        objectives = np.column_stack([obj1_values, obj2_values, obj3_values])

        assert objectives.shape == (4, 3)
        assert np.all(np.isfinite(objectives))
        assert np.all(objectives >= 0)  # All objectives should be positive

    def test_nsga_ii_selection(self):
        """Test NSGA-II selection mechanism."""

        def non_dominated_sort(objectives):
            """Perform non-dominated sorting."""
            n_solutions = objectives.shape[0]
            domination_count = np.zeros(n_solutions)
            dominated_solutions = [[] for _ in range(n_solutions)]
            fronts = [[]]

            # Calculate domination relationships
            for i in range(n_solutions):
                for j in range(n_solutions):
                    if i != j:
                        if self.dominates(objectives[i], objectives[j]):
                            dominated_solutions[i].append(j)
                        elif self.dominates(objectives[j], objectives[i]):
                            domination_count[i] += 1

                if domination_count[i] == 0:
                    fronts[0].append(i)

            # Build subsequent fronts
            i = 0
            while len(fronts[i]) > 0:
                next_front = []
                for p in fronts[i]:
                    for q in dominated_solutions[p]:
                        domination_count[q] -= 1
                        if domination_count[q] == 0:
                            next_front.append(q)
                i += 1
                fronts.append(next_front)

            return fronts[:-1]  # Remove empty last front

        def dominates(obj_a, obj_b):
            """Check if obj_a dominates obj_b."""
            return np.all(obj_a <= obj_b) and np.any(obj_a < obj_b)

        self.dominates = dominates  # Store for use in method

        # Test NSGA-II sorting
        objectives = np.array([
            [1.0, 4.0, 3.0],  # Front 0
            [2.0, 3.0, 3.0],  # Front 0
            [3.0, 2.0, 3.0],  # Front 0
            [4.0, 1.0, 3.0],  # Front 0
            [2.5, 3.5, 3.5],  # Front 1 (dominated by [2.0, 3.0, 3.0])
            [1.5, 4.5, 3.5],  # Front 1 (dominated by [1.0, 4.0, 3.0])
            [3.5, 3.5, 4.0],  # Front 2
        ])

        fronts = non_dominated_sort(objectives)

        # Verify front structure
        assert len(fronts) >= 2
        assert len(fronts[0]) == 4  # First front should have 4 solutions
        assert len(fronts[1]) >= 1  # Second front should have solutions

        # Verify no solution in front 0 is dominated by any other
        front_0_indices = fronts[0]
        for i in front_0_indices:
            for j in front_0_indices:
                if i != j:
                    assert not dominates(objectives[j], objectives[i])

    def test_multi_objective_optimization_integration(self):
        """Test integration of multi-objective optimization components."""

        class MultiObjectivePSOTuner(PSOTuner):
            """Extended PSO tuner with multi-objective capabilities."""

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.archive = []  # Pareto archive

            def evaluate_multi_objectives(self, particles):
                """Evaluate multiple objectives for particles."""
                # This would interface with the simulation to get multiple objectives
                n_particles = particles.shape[0]

                # Simulate three objectives: stability, efficiency, robustness
                objectives = np.zeros((n_particles, 3))

                for i, particle in enumerate(particles):
                    # Stability (minimize state error) - favor higher gains
                    objectives[i, 0] = 10.0 / (1.0 + np.mean(particle[:4]))

                    # Efficiency (minimize control effort) - favor lower switching gain
                    objectives[i, 1] = particle[4] / 10.0

                    # Robustness (minimize sensitivity) - favor balanced gains
                    gain_variance = np.var(particle[:4])
                    objectives[i, 2] = 1.0 + gain_variance

                return objectives

            def update_archive(self, particles, objectives):
                """Update Pareto archive with non-dominated solutions."""
                # Combine current archive with new solutions
                if len(self.archive) == 0:
                    for i, (particle, obj) in enumerate(zip(particles, objectives)):
                        self.archive.append({'position': particle, 'objectives': obj})
                else:
                    # Add new solutions and remove dominated ones
                    for i, (particle, obj) in enumerate(zip(particles, objectives)):
                        is_dominated = False
                        solutions_to_remove = []

                        for j, archived in enumerate(self.archive):
                            if self.dominates(archived['objectives'], obj):
                                is_dominated = True
                                break
                            elif self.dominates(obj, archived['objectives']):
                                solutions_to_remove.append(j)

                        # Remove dominated solutions from archive
                        for idx in sorted(solutions_to_remove, reverse=True):
                            del self.archive[idx]

                        # Add non-dominated solution
                        if not is_dominated:
                            self.archive.append({'position': particle, 'objectives': obj})

            def dominates(self, obj_a, obj_b):
                """Check if obj_a dominates obj_b."""
                return np.all(obj_a <= obj_b) and np.any(obj_a < obj_b)

        # Test multi-objective integration
        from dataclasses import dataclass

        @dataclass
        class MinimalConfig:
            global_seed: int = 42

        config = MinimalConfig()

        def minimal_factory(gains):
            controller = Mock()
            controller.max_force = 150.0
            return controller

        # Create multi-objective tuner
        mo_tuner = MultiObjectivePSOTuner(
            controller_factory=minimal_factory,
            config=config,
            seed=42
        )

        # Test multi-objective evaluation
        particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 2.0],
            [15.0, 12.0, 8.0, 6.0, 10.0, 3.0],
            [5.0, 4.0, 2.0, 1.0, 30.0, 1.0],
            [8.0, 6.0, 4.0, 2.0, 25.0, 4.0],
        ])

        objectives = mo_tuner.evaluate_multi_objectives(particles)
        assert objectives.shape == (4, 3)

        # Test archive update
        mo_tuner.update_archive(particles, objectives)
        assert len(mo_tuner.archive) > 0

        # Extract Pareto front
        pareto_objectives = np.array([sol['objectives'] for sol in mo_tuner.archive])
        pareto_positions = np.array([sol['position'] for sol in mo_tuner.archive])

        assert pareto_objectives.shape[1] == 3
        assert pareto_positions.shape[1] == 6

        # Verify no solution dominates another in the archive
        for i in range(len(mo_tuner.archive)):
            for j in range(len(mo_tuner.archive)):
                if i != j:
                    assert not mo_tuner.dominates(
                        mo_tuner.archive[j]['objectives'],
                        mo_tuner.archive[i]['objectives']
                    )

    def test_pareto_front_quality_metrics(self):
        """Test quality metrics for Pareto front assessment."""

        def calculate_spread_metric(pareto_front):
            """Calculate spread metric for Pareto front diversity."""
            if len(pareto_front) < 2:
                return 0.0

            # Calculate distances between consecutive solutions
            sorted_front = pareto_front[np.argsort(pareto_front[:, 0])]
            distances = []

            for i in range(len(sorted_front) - 1):
                dist = np.linalg.norm(sorted_front[i+1] - sorted_front[i])
                distances.append(dist)

            # Spread metric is coefficient of variation of distances
            if len(distances) > 1:
                return np.std(distances) / np.mean(distances)
            else:
                return 0.0

        def calculate_convergence_metric(pareto_front, reference_front):
            """Calculate convergence metric compared to reference front."""
            if len(pareto_front) == 0 or len(reference_front) == 0:
                return float('inf')

            # Average distance from each point to nearest point in reference
            distances = []
            for point in pareto_front:
                min_dist = min(np.linalg.norm(point - ref_point)
                              for ref_point in reference_front)
                distances.append(min_dist)

            return np.mean(distances)

        # Test with well-distributed Pareto front
        good_front = np.array([
            [1.0, 4.0],
            [2.0, 3.0],
            [3.0, 2.0],
            [4.0, 1.0],
        ])

        good_spread = calculate_spread_metric(good_front)
        assert good_spread >= 0

        # Test with poorly distributed front
        poor_front = np.array([
            [1.0, 4.0],
            [1.1, 3.9],
            [1.2, 3.8],
            [4.0, 1.0],
        ])

        poor_spread = calculate_spread_metric(poor_front)
        assert poor_spread > good_spread  # Poor distribution should have higher spread

        # Test convergence metric
        reference_front = np.array([
            [0.5, 4.5],
            [1.5, 3.5],
            [2.5, 2.5],
            [3.5, 1.5],
        ])

        convergence = calculate_convergence_metric(good_front, reference_front)
        assert convergence >= 0

        # Test with identical fronts
        identical_convergence = calculate_convergence_metric(good_front, good_front)
        assert identical_convergence == 0.0

    def test_multi_objective_constraint_handling(self):
        """Test constraint handling in multi-objective optimization."""

        def apply_constraint_penalties(objectives, constraints_violated):
            """Apply penalties for constraint violations."""
            penalized_objectives = objectives.copy()

            for i, violated in enumerate(constraints_violated):
                if violated:
                    # Add penalty to all objectives
                    penalty_factor = 1000.0
                    penalized_objectives[i] += penalty_factor

            return penalized_objectives

        def check_stability_constraints(particles):
            """Check stability constraints for particles."""
            constraints = np.ones(particles.shape[0], dtype=bool)

            # Check switching gain bounds
            constraints &= (particles[:, 4] >= 5.0) & (particles[:, 4] <= 50.0)

            # Check gain ratios
            for i in range(particles.shape[0]):
                if particles[i, 0] / particles[i, 1] > 10.0:
                    constraints[i] = False
                if particles[i, 1] / particles[i, 0] > 10.0:
                    constraints[i] = False

            return ~constraints  # Return violations

        # Test constraint checking
        particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 2.0],  # Valid
            [100.0, 1.0, 5.0, 3.0, 20.0, 2.0], # Invalid ratio
            [10.0, 8.0, 5.0, 3.0, 60.0, 2.0],  # Invalid switching gain
            [5.0, 5.0, 3.0, 2.0, 15.0, 1.0],   # Valid
        ])

        violations = check_stability_constraints(particles)
        expected_violations = np.array([False, True, True, False])
        np.testing.assert_array_equal(violations, expected_violations)

        # Test penalty application
        objectives = np.array([
            [1.0, 2.0, 3.0],
            [1.5, 2.5, 3.5],
            [2.0, 3.0, 4.0],
            [0.8, 1.8, 2.8],
        ])

        penalized = apply_constraint_penalties(objectives, violations)

        # Valid particles should remain unchanged
        np.testing.assert_array_equal(penalized[0], objectives[0])
        np.testing.assert_array_equal(penalized[3], objectives[3])

        # Invalid particles should have penalties
        assert np.all(penalized[1] > objectives[1])
        assert np.all(penalized[2] > objectives[2])


class TestMultiObjectiveVisualization:
    """Test visualization and analysis tools for multi-objective optimization."""

    def test_pareto_front_plotting_data(self):
        """Test generation of data for Pareto front plotting."""

        def prepare_pareto_plot_data(pareto_front, objective_names):
            """Prepare data for Pareto front visualization."""
            plot_data = {
                'objectives': pareto_front,
                'names': objective_names,
                'n_objectives': len(objective_names),
                'n_solutions': len(pareto_front)
            }

            # Calculate bounds for plotting
            if len(pareto_front) > 0:
                plot_data['bounds'] = {
                    'min': np.min(pareto_front, axis=0),
                    'max': np.max(pareto_front, axis=0),
                    'range': np.max(pareto_front, axis=0) - np.min(pareto_front, axis=0)
                }

                # Normalize objectives for comparison
                plot_data['normalized'] = (pareto_front - plot_data['bounds']['min']) / \
                                        (plot_data['bounds']['range'] + 1e-10)

            return plot_data

        # Test with 2D Pareto front
        pareto_front_2d = np.array([
            [1.0, 4.0],
            [2.0, 3.0],
            [3.0, 2.0],
            [4.0, 1.0],
        ])

        objective_names_2d = ['Stability Error', 'Control Effort']
        plot_data_2d = prepare_pareto_plot_data(pareto_front_2d, objective_names_2d)

        assert plot_data_2d['n_objectives'] == 2
        assert plot_data_2d['n_solutions'] == 4
        assert 'bounds' in plot_data_2d
        assert 'normalized' in plot_data_2d

        # Test normalization
        normalized = plot_data_2d['normalized']
        assert np.all(normalized >= 0)
        assert np.all(normalized <= 1)

        # Test with 3D Pareto front
        pareto_front_3d = np.array([
            [1.0, 4.0, 2.0],
            [2.0, 3.0, 3.0],
            [3.0, 2.0, 1.0],
            [4.0, 1.0, 4.0],
        ])

        objective_names_3d = ['Stability', 'Efficiency', 'Robustness']
        plot_data_3d = prepare_pareto_plot_data(pareto_front_3d, objective_names_3d)

        assert plot_data_3d['n_objectives'] == 3
        assert plot_data_3d['n_solutions'] == 4

    def test_trade_off_analysis(self):
        """Test trade-off analysis between objectives."""

        def analyze_trade_offs(pareto_front, objective_names):
            """Analyze trade-offs between objectives."""
            n_objectives = pareto_front.shape[1]
            trade_offs = {}

            # Pairwise trade-off analysis
            for i in range(n_objectives):
                for j in range(i + 1, n_objectives):
                    obj1_name = objective_names[i]
                    obj2_name = objective_names[j]

                    # Calculate correlation coefficient
                    correlation = np.corrcoef(pareto_front[:, i], pareto_front[:, j])[0, 1]

                    # Calculate trade-off strength
                    # Negative correlation indicates trade-off
                    trade_off_strength = max(0, -correlation)

                    trade_offs[f"{obj1_name}_vs_{obj2_name}"] = {
                        'correlation': correlation,
                        'trade_off_strength': trade_off_strength,
                        'relationship': 'trade_off' if correlation < -0.5 else
                                     'synergy' if correlation > 0.5 else 'independent'
                    }

            return trade_offs

        # Test with clear trade-off
        trade_off_front = np.array([
            [1.0, 4.0, 2.5],
            [2.0, 3.0, 2.0],
            [3.0, 2.0, 1.5],
            [4.0, 1.0, 1.0],
        ])

        objective_names = ['Performance', 'Efficiency', 'Robustness']
        trade_offs = analyze_trade_offs(trade_off_front, objective_names)

        # Should detect trade-off between Performance and Efficiency
        perf_eff_trade_off = trade_offs['Performance_vs_Efficiency']
        assert perf_eff_trade_off['relationship'] == 'trade_off'
        assert perf_eff_trade_off['correlation'] < 0

    def test_solution_ranking(self):
        """Test ranking of solutions in multi-objective space."""

        def rank_solutions(pareto_front, weights=None):
            """Rank solutions using weighted sum or other methods."""
            if weights is None:
                weights = np.ones(pareto_front.shape[1]) / pareto_front.shape[1]

            # Normalize objectives (assuming minimization)
            normalized_front = pareto_front.copy()
            for i in range(pareto_front.shape[1]):
                obj_range = pareto_front[:, i].max() - pareto_front[:, i].min()
                if obj_range > 0:
                    normalized_front[:, i] = (pareto_front[:, i] - pareto_front[:, i].min()) / obj_range

            # Calculate weighted sum
            weighted_scores = np.sum(normalized_front * weights, axis=1)

            # Rank solutions (lower score is better for minimization)
            rankings = np.argsort(weighted_scores)

            return rankings, weighted_scores

        # Test solution ranking
        pareto_front = np.array([
            [1.0, 4.0],  # Good in obj1, poor in obj2
            [2.0, 3.0],  # Balanced
            [3.0, 2.0],  # Balanced
            [4.0, 1.0],  # Poor in obj1, good in obj2
        ])

        # Equal weights
        rankings_equal, scores_equal = rank_solutions(pareto_front)
        assert len(rankings_equal) == 4
        assert len(scores_equal) == 4

        # Preference for first objective
        weights_obj1 = np.array([0.8, 0.2])
        rankings_obj1, scores_obj1 = rank_solutions(pareto_front, weights_obj1)

        # Solution with best obj1 should rank higher with obj1 preference
        best_obj1_idx = np.argmin(pareto_front[:, 0])
        assert rankings_obj1[0] == best_obj1_idx

        # Preference for second objective
        weights_obj2 = np.array([0.2, 0.8])
        rankings_obj2, scores_obj2 = rank_solutions(pareto_front, weights_obj2)

        # Solution with best obj2 should rank higher with obj2 preference
        best_obj2_idx = np.argmin(pareto_front[:, 1])
        assert rankings_obj2[0] == best_obj2_idx


if __name__ == "__main__":
    pytest.main([__file__, "-v"])