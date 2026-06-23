#======================================================================================\\\
#================ tests/test_optimization/test_algorithm_comparison.py ================\\\
#======================================================================================\\\

"""
Algorithm comparison framework for PSO vs GA vs DE optimization.
Statistical benchmarking and performance comparison tests.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import List
from scipy import stats



class TestAlgorithmComparison:
    """Comprehensive algorithm comparison framework."""

    @pytest.fixture
    def comparison_config(self):
        """Configuration for algorithm comparison."""
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
                    self.initial_state = [0.0, 0.05, -0.03, 0.0, 0.0, 0.0]

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
            n_particles: int = 20
            iters: int = 50

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
    def comparison_controller_factory(self):
        """Controller factory for algorithm comparison."""
        def factory(gains):
            controller = Mock()
            controller.max_force = 150.0
            controller.gains = gains
            controller.controller_type = 'classical_smc'
            return controller

        factory.n_gains = 6
        factory.controller_type = 'classical_smc'
        return factory

    def create_benchmark_functions(self):
        """Create standard benchmark functions for optimization comparison."""

        def sphere_function(x):
            """Sphere function: f(x) = sum(x_i^2)"""
            return np.sum(x**2)

        def rosenbrock_function(x):
            """Rosenbrock function: f(x) = sum(100*(x[i+1] - x[i]^2)^2 + (1 - x[i])^2)"""
            if len(x) < 2:
                return 0.0
            total = 0.0
            for i in range(len(x) - 1):
                total += 100 * (x[i+1] - x[i]**2)**2 + (1 - x[i])**2
            return total

        def rastrigin_function(x):
            """Rastrigin function: f(x) = A*n + sum(x[i]^2 - A*cos(2*pi*x[i]))"""
            A = 10.0
            n = len(x)
            return A * n + np.sum(x**2 - A * np.cos(2 * np.pi * x))

        def ackley_function(x):
            """Ackley function: multimodal function with many local minima"""
            if len(x) == 0:
                return 0.0

            a = 20.0
            b = 0.2
            c = 2 * np.pi

            sum1 = np.sum(x**2)
            sum2 = np.sum(np.cos(c * x))

            term1 = -a * np.exp(-b * np.sqrt(sum1 / len(x)))
            term2 = -np.exp(sum2 / len(x))

            return term1 + term2 + a + np.exp(1)

        return {
            'sphere': {'func': sphere_function, 'bounds': [(-5.12, 5.12)] * 6, 'optimum': 0.0},
            'rosenbrock': {'func': rosenbrock_function, 'bounds': [(-2.048, 2.048)] * 6, 'optimum': 0.0},
            'rastrigin': {'func': rastrigin_function, 'bounds': [(-5.12, 5.12)] * 6, 'optimum': 0.0},
            'ackley': {'func': ackley_function, 'bounds': [(-32.768, 32.768)] * 6, 'optimum': 0.0}
        }

    def test_benchmark_function_validation(self):
        """Test validation of benchmark functions."""
        benchmark_functions = self.create_benchmark_functions()

        # Test sphere function
        sphere_func = benchmark_functions['sphere']['func']
        assert sphere_func(np.zeros(6)) == 0.0  # Global optimum
        assert sphere_func(np.ones(6)) == 6.0   # All ones

        # Test Rosenbrock function
        rosenbrock_func = benchmark_functions['rosenbrock']['func']
        assert rosenbrock_func(np.ones(6)) == 0.0  # Global optimum

        # Test Rastrigin function
        rastrigin_func = benchmark_functions['rastrigin']['func']
        assert rastrigin_func(np.zeros(6)) == 0.0  # Global optimum

        # Test Ackley function
        ackley_func = benchmark_functions['ackley']['func']
        result = ackley_func(np.zeros(6))
        assert abs(result) < 1e-10  # Should be very close to 0

    def create_genetic_algorithm_mock(self):
        """Create mock genetic algorithm for comparison."""
        class MockGeneticAlgorithm:
            def __init__(self, bounds, population_size=20, generations=50, mutation_rate=0.1, crossover_rate=0.8):
                self.bounds = bounds
                self.population_size = population_size
                self.generations = generations
                self.mutation_rate = mutation_rate
                self.crossover_rate = crossover_rate
                self.best_fitness = None
                self.best_solution = None
                self.convergence_history = []

            def optimize(self, fitness_function, seed=42):
                """Mock genetic algorithm optimization."""
                np.random.seed(seed)

                # Initialize population
                n_dimensions = len(self.bounds)
                population = np.random.uniform(
                    low=[b[0] for b in self.bounds],
                    high=[b[1] for b in self.bounds],
                    size=(self.population_size, n_dimensions)
                )

                best_fitness = float('inf')
                best_solution = None

                for generation in range(self.generations):
                    # Evaluate fitness
                    fitness_values = np.array([fitness_function(ind) for ind in population])

                    # Track best
                    current_best_idx = np.argmin(fitness_values)
                    current_best_fitness = fitness_values[current_best_idx]

                    if current_best_fitness < best_fitness:
                        best_fitness = current_best_fitness
                        best_solution = population[current_best_idx].copy()

                    self.convergence_history.append(best_fitness)

                    # Simple evolution simulation
                    # Select parents (tournament selection)
                    new_population = []
                    for _ in range(self.population_size):
                        # Tournament selection
                        tournament_size = 3
                        tournament_indices = np.random.choice(self.population_size, tournament_size)
                        winner_idx = tournament_indices[np.argmin(fitness_values[tournament_indices])]
                        new_population.append(population[winner_idx].copy())

                    population = np.array(new_population)

                    # Apply crossover and mutation
                    for i in range(0, self.population_size - 1, 2):
                        if np.random.random() < self.crossover_rate:
                            # Simple crossover
                            crossover_point = np.random.randint(1, n_dimensions)
                            temp = population[i, crossover_point:].copy()
                            population[i, crossover_point:] = population[i+1, crossover_point:]
                            population[i+1, crossover_point:] = temp

                    # Mutation
                    for i in range(self.population_size):
                        if np.random.random() < self.mutation_rate:
                            mutation_point = np.random.randint(n_dimensions)
                            population[i, mutation_point] += np.random.normal(0, 0.1)
                            # Ensure bounds
                            population[i, mutation_point] = np.clip(
                                population[i, mutation_point],
                                self.bounds[mutation_point][0],
                                self.bounds[mutation_point][1]
                            )

                self.best_fitness = best_fitness
                self.best_solution = best_solution

                return {
                    'best_fitness': best_fitness,
                    'best_solution': best_solution,
                    'convergence_history': self.convergence_history
                }

        return MockGeneticAlgorithm

    def create_differential_evolution_mock(self):
        """Create mock differential evolution algorithm for comparison."""
        class MockDifferentialEvolution:
            def __init__(self, bounds, population_size=20, generations=50, F=0.5, CR=0.7):
                self.bounds = bounds
                self.population_size = population_size
                self.generations = generations
                self.F = F  # Differential weight
                self.CR = CR  # Crossover probability
                self.best_fitness = None
                self.best_solution = None
                self.convergence_history = []

            def optimize(self, fitness_function, seed=42):
                """Mock differential evolution optimization."""
                np.random.seed(seed)

                # Initialize population
                n_dimensions = len(self.bounds)
                population = np.random.uniform(
                    low=[b[0] for b in self.bounds],
                    high=[b[1] for b in self.bounds],
                    size=(self.population_size, n_dimensions)
                )

                # Evaluate initial population
                fitness_values = np.array([fitness_function(ind) for ind in population])
                best_idx = np.argmin(fitness_values)
                best_fitness = fitness_values[best_idx]
                best_solution = population[best_idx].copy()

                for generation in range(self.generations):
                    for i in range(self.population_size):
                        # Select three random individuals different from current
                        candidates = [j for j in range(self.population_size) if j != i]
                        a, b, c = np.random.choice(candidates, 3, replace=False)

                        # Create mutant vector
                        mutant = population[a] + self.F * (population[b] - population[c])

                        # Ensure bounds
                        for j in range(n_dimensions):
                            mutant[j] = np.clip(mutant[j], self.bounds[j][0], self.bounds[j][1])

                        # Crossover
                        trial = population[i].copy()
                        R = np.random.randint(n_dimensions)  # Ensure at least one parameter from mutant

                        for j in range(n_dimensions):
                            if np.random.random() < self.CR or j == R:
                                trial[j] = mutant[j]

                        # Selection
                        trial_fitness = fitness_function(trial)
                        if trial_fitness < fitness_values[i]:
                            population[i] = trial
                            fitness_values[i] = trial_fitness

                            if trial_fitness < best_fitness:
                                best_fitness = trial_fitness
                                best_solution = trial.copy()

                    self.convergence_history.append(best_fitness)

                self.best_fitness = best_fitness
                self.best_solution = best_solution

                return {
                    'best_fitness': best_fitness,
                    'best_solution': best_solution,
                    'convergence_history': self.convergence_history
                }

        return MockDifferentialEvolution

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_algorithm_performance_comparison(self, mock_simulate, comparison_config, comparison_controller_factory):
        """Test performance comparison between PSO, GA, and DE."""
        # Mock simulation for PSO
        def mock_sim(*args, **kwargs):
            particles = args[1] if len(args) > 1 else kwargs.get('particles')
            n_particles = particles.shape[0]
            t = np.linspace(0, 1.0, 101)
            x = np.random.RandomState(42).random((n_particles, 101, 6)) * 0.1
            u = np.random.RandomState(42).random((n_particles, 101)) * 10.0
            sigma = np.random.RandomState(42).random((n_particles, 101)) * 0.5
            return (t, x, u, sigma)

        mock_simulate.side_effect = mock_sim

        # Get benchmark functions
        benchmark_functions = self.create_benchmark_functions()

        # Test on sphere function (simple benchmark)
        sphere_func = benchmark_functions['sphere']['func']
        bounds = benchmark_functions['sphere']['bounds']

        # Initialize algorithms
        GA = self.create_genetic_algorithm_mock()
        DE = self.create_differential_evolution_mock()

        ga_optimizer = GA(bounds, population_size=20, generations=50)
        de_optimizer = DE(bounds, population_size=20, generations=50)

        # Run comparison
        algorithms = {
            'GA': ga_optimizer,
            'DE': de_optimizer
        }

        results = {}
        n_runs = 5  # Multiple runs for statistical significance

        for alg_name, optimizer in algorithms.items():
            run_results = []

            for run in range(n_runs):
                result = optimizer.optimize(sphere_func, seed=42 + run)
                run_results.append({
                    'best_fitness': result['best_fitness'],
                    'convergence_history': result['convergence_history'],
                    'runtime': 0.1  # Mock runtime
                })

            # Calculate statistics
            best_fitnesses = [r['best_fitness'] for r in run_results]
            results[alg_name] = {
                'mean_fitness': np.mean(best_fitnesses),
                'std_fitness': np.std(best_fitnesses),
                'best_fitness': np.min(best_fitnesses),
                'worst_fitness': np.max(best_fitnesses),
                'success_rate': sum(1 for f in best_fitnesses if f < 1e-6) / n_runs,
                'convergence_histories': [r['convergence_history'] for r in run_results],
                'mean_runtime': np.mean([r['runtime'] for r in run_results])
            }

        # Validate results structure
        for alg_name, alg_results in results.items():
            assert 'mean_fitness' in alg_results
            assert 'std_fitness' in alg_results
            assert 'success_rate' in alg_results
            assert len(alg_results['convergence_histories']) == n_runs

    def test_statistical_significance_testing(self):
        """Test statistical significance of algorithm comparison results."""

        def perform_statistical_tests(results_a, results_b, alpha=0.05):
            """Perform statistical tests between two algorithm results."""

            # Wilcoxon rank-sum test (Mann-Whitney U test)
            try:
                statistic, p_value = stats.mannwhitneyu(results_a, results_b, alternative='two-sided')
                mann_whitney_significant = p_value < alpha
            except ValueError:
                statistic, p_value = 0, 1.0
                mann_whitney_significant = False

            # Two-sample t-test
            try:
                t_statistic, t_p_value = stats.ttest_ind(results_a, results_b)
                t_test_significant = t_p_value < alpha
            except ValueError:
                t_statistic, t_p_value = 0, 1.0
                t_test_significant = False

            # Effect size (Cohen's d)
            pooled_std = np.sqrt(((len(results_a) - 1) * np.var(results_a) +
                                 (len(results_b) - 1) * np.var(results_b)) /
                                (len(results_a) + len(results_b) - 2))

            if pooled_std > 0:
                cohens_d = abs(np.mean(results_a) - np.mean(results_b)) / pooled_std
            else:
                cohens_d = 0.0

            # Effect size interpretation
            if cohens_d < 0.2:
                effect_size = 'negligible'
            elif cohens_d < 0.5:
                effect_size = 'small'
            elif cohens_d < 0.8:
                effect_size = 'medium'
            else:
                effect_size = 'large'

            return {
                'mann_whitney': {
                    'statistic': statistic,
                    'p_value': p_value,
                    'significant': mann_whitney_significant
                },
                't_test': {
                    'statistic': t_statistic,
                    'p_value': t_p_value,
                    'significant': t_test_significant
                },
                'effect_size': {
                    'cohens_d': cohens_d,
                    'interpretation': effect_size
                }
            }

        # Test with mock data
        # Algorithm A (better performance)
        results_a = np.random.normal(loc=1.0, scale=0.5, size=30)

        # Algorithm B (worse performance)
        results_b = np.random.normal(loc=2.0, scale=0.5, size=30)

        statistical_results = perform_statistical_tests(results_a, results_b)

        # Validate statistical test structure
        assert 'mann_whitney' in statistical_results
        assert 't_test' in statistical_results
        assert 'effect_size' in statistical_results

        # Check effect size calculation
        assert statistical_results['effect_size']['cohens_d'] >= 0
        assert statistical_results['effect_size']['interpretation'] in [
            'negligible', 'small', 'medium', 'large'
        ]

        # Test with identical distributions (should not be significant)
        identical_a = np.random.normal(loc=1.0, scale=0.1, size=30)
        identical_b = np.random.normal(loc=1.0, scale=0.1, size=30)

        identical_results = perform_statistical_tests(identical_a, identical_b)

        # Should have small effect size
        assert identical_results['effect_size']['cohens_d'] < 0.5

    def test_convergence_analysis_comparison(self):
        """Test convergence analysis across different algorithms."""

        def analyze_convergence_characteristics(convergence_history):
            """Analyze convergence characteristics of an optimization run."""

            if len(convergence_history) == 0:
                return {'converged': False, 'convergence_rate': 0.0}

            # Initial and final fitness
            initial_fitness = convergence_history[0]
            final_fitness = convergence_history[-1]

            # Total improvement
            total_improvement = initial_fitness - final_fitness

            # Convergence rate (improvement per iteration)
            convergence_rate = total_improvement / len(convergence_history)

            # Detect convergence point (when improvement becomes negligible)
            convergence_threshold = 0.001 * abs(initial_fitness)
            convergence_detected = False
            convergence_iteration = len(convergence_history)

            for i in range(1, len(convergence_history)):
                improvement = convergence_history[i-1] - convergence_history[i]
                if improvement < convergence_threshold:
                    # Check if improvement stays low
                    remaining_improvements = [
                        convergence_history[j-1] - convergence_history[j]
                        for j in range(i+1, min(i+10, len(convergence_history)))
                    ]
                    if all(imp < convergence_threshold for imp in remaining_improvements):
                        convergence_detected = True
                        convergence_iteration = i
                        break

            # Convergence speed (iterations to reach 90% of final improvement)
            target_fitness = initial_fitness - 0.9 * total_improvement
            convergence_speed = len(convergence_history)

            for i, fitness in enumerate(convergence_history):
                if fitness <= target_fitness:
                    convergence_speed = i
                    break

            # Stability of final solution (variance in last 10% of iterations)
            final_portion_size = max(1, len(convergence_history) // 10)
            final_portion = convergence_history[-final_portion_size:]
            final_stability = 1.0 / (1.0 + np.var(final_portion))

            return {
                'converged': convergence_detected,
                'convergence_iteration': convergence_iteration,
                'convergence_rate': convergence_rate,
                'convergence_speed': convergence_speed,
                'total_improvement': total_improvement,
                'final_stability': final_stability,
                'iterations': len(convergence_history)
            }

        # Test with different convergence patterns

        # Fast convergence
        fast_convergence = [10.0 * np.exp(-i/5) + 0.1 for i in range(50)]
        fast_analysis = analyze_convergence_characteristics(fast_convergence)

        assert fast_analysis['convergence_speed'] < 25  # Should converge quickly
        assert fast_analysis['converged']

        # Slow convergence
        slow_convergence = [10.0 * np.exp(-i/30) + 0.1 for i in range(50)]
        slow_analysis = analyze_convergence_characteristics(slow_convergence)

        assert slow_analysis['convergence_speed'] > fast_analysis['convergence_speed']

        # No convergence (stagnant)
        stagnant = [5.0 + 0.1 * np.random.random() for _ in range(50)]
        stagnant_analysis = analyze_convergence_characteristics(stagnant)

        assert stagnant_analysis['total_improvement'] < 1.0  # Minimal improvement

    def test_multi_objective_algorithm_comparison(self):
        """Test comparison of algorithms on multi-objective problems."""

        def zdt1_objectives(x):
            """ZDT1 multi-objective test function."""
            f1 = x[0]

            g = 1 + 9 * np.sum(x[1:]) / (len(x) - 1)
            h = 1 - np.sqrt(f1 / g)
            f2 = g * h

            return np.array([f1, f2])

        def dtlz2_objectives(x):
            """DTLZ2 multi-objective test function."""
            len(x) - 2  # Number of position variables

            # Calculate g function
            g = np.sum((x[2:] - 0.5)**2)

            # Calculate objectives
            f1 = (1 + g) * np.cos(x[0] * np.pi / 2) * np.cos(x[1] * np.pi / 2)
            f2 = (1 + g) * np.cos(x[0] * np.pi / 2) * np.sin(x[1] * np.pi / 2)
            f3 = (1 + g) * np.sin(x[0] * np.pi / 2)

            return np.array([f1, f2, f3])

        def evaluate_pareto_quality(pareto_front, reference_front=None):
            """Evaluate quality of Pareto front."""
            if len(pareto_front) == 0:
                return {'hypervolume': 0.0, 'spacing': float('inf'), 'coverage': 0.0}

            # Hypervolume calculation (simplified 2D version)
            if pareto_front.shape[1] == 2:
                sorted_front = pareto_front[np.argsort(pareto_front[:, 0])]
                reference_point = np.max(pareto_front, axis=0) + 1.0

                hypervolume = 0.0
                prev_x = 0.0

                for point in sorted_front:
                    if point[0] < reference_point[0] and point[1] < reference_point[1]:
                        width = point[0] - prev_x
                        height = reference_point[1] - point[1]
                        hypervolume += max(0, width * height)
                        prev_x = point[0]
            else:
                hypervolume = 0.0  # Simplified for higher dimensions

            # Spacing metric (diversity measure)
            if len(pareto_front) > 1:
                distances = []
                for i, point in enumerate(pareto_front):
                    min_dist = float('inf')
                    for j, other_point in enumerate(pareto_front):
                        if i != j:
                            dist = np.linalg.norm(point - other_point)
                            min_dist = min(min_dist, dist)
                    distances.append(min_dist)

                mean_distance = np.mean(distances)
                spacing = np.sqrt(np.mean([(d - mean_distance)**2 for d in distances]))
            else:
                spacing = 0.0

            # Coverage metric (if reference front is provided)
            coverage = 0.0
            if reference_front is not None and len(reference_front) > 0:
                covered_points = 0
                for ref_point in reference_front:
                    for front_point in pareto_front:
                        if np.all(front_point <= ref_point):
                            covered_points += 1
                            break
                coverage = covered_points / len(reference_front)

            return {
                'hypervolume': hypervolume,
                'spacing': spacing,
                'coverage': coverage,
                'size': len(pareto_front)
            }

        # Test ZDT1 function
        test_points = np.random.uniform(0, 1, (10, 6))
        zdt1_results = [zdt1_objectives(point) for point in test_points]
        zdt1_front = np.array(zdt1_results)

        zdt1_quality = evaluate_pareto_quality(zdt1_front)

        assert 'hypervolume' in zdt1_quality
        assert 'spacing' in zdt1_quality
        assert zdt1_quality['size'] == 10

        # Test DTLZ2 function
        dtlz2_results = [dtlz2_objectives(point) for point in test_points]
        dtlz2_front = np.array(dtlz2_results)

        dtlz2_quality = evaluate_pareto_quality(dtlz2_front)

        assert dtlz2_quality['size'] == 10
        assert dtlz2_quality['spacing'] >= 0

    def test_algorithm_recommendation_system(self):
        """Test algorithm recommendation based on problem characteristics."""

        def recommend_algorithm(problem_characteristics):
            """Recommend optimization algorithm based on problem characteristics."""

            # Problem characteristics:
            # - dimensionality: low (<10), medium (10-50), high (>50)
            # - modality: unimodal, multimodal
            # - separability: separable, non-separable
            # - noise_level: low, medium, high
            # - constraints: none, linear, nonlinear
            # - objectives: single, multi

            recommendations = []

            # PSO recommendations
            if problem_characteristics.get('modality') == 'multimodal':
                recommendations.append({
                    'algorithm': 'PSO',
                    'reason': 'Good for multimodal optimization',
                    'confidence': 0.8
                })

            if problem_characteristics.get('dimensionality') == 'medium':
                recommendations.append({
                    'algorithm': 'PSO',
                    'reason': 'Effective for medium-dimensional problems',
                    'confidence': 0.7
                })

            # GA recommendations
            if problem_characteristics.get('constraints') in ['linear', 'nonlinear']:
                recommendations.append({
                    'algorithm': 'GA',
                    'reason': 'Good constraint handling capabilities',
                    'confidence': 0.75
                })

            if problem_characteristics.get('objectives') == 'multi':
                recommendations.append({
                    'algorithm': 'GA',
                    'reason': 'Excellent for multi-objective optimization',
                    'confidence': 0.9
                })

            # DE recommendations
            if problem_characteristics.get('noise_level') == 'low':
                recommendations.append({
                    'algorithm': 'DE',
                    'reason': 'Robust and reliable for low-noise problems',
                    'confidence': 0.8
                })

            if problem_characteristics.get('separability') == 'non-separable':
                recommendations.append({
                    'algorithm': 'DE',
                    'reason': 'Good for non-separable functions',
                    'confidence': 0.7
                })

            # Sort by confidence
            recommendations.sort(key=lambda x: x['confidence'], reverse=True)

            return recommendations[:3]  # Top 3 recommendations

        # Test different problem scenarios

        # Scenario 1: Multimodal, medium-dimensional, single-objective
        scenario1 = {
            'dimensionality': 'medium',
            'modality': 'multimodal',
            'separability': 'separable',
            'noise_level': 'low',
            'constraints': 'none',
            'objectives': 'single'
        }

        recs1 = recommend_algorithm(scenario1)
        assert len(recs1) > 0
        assert 'PSO' in [rec['algorithm'] for rec in recs1]

        # Scenario 2: Multi-objective with constraints
        scenario2 = {
            'dimensionality': 'low',
            'modality': 'unimodal',
            'separability': 'separable',
            'noise_level': 'medium',
            'constraints': 'nonlinear',
            'objectives': 'multi'
        }

        recs2 = recommend_algorithm(scenario2)
        assert len(recs2) > 0
        assert 'GA' in [rec['algorithm'] for rec in recs2]

        # Scenario 3: High-noise, non-separable
        scenario3 = {
            'dimensionality': 'high',
            'modality': 'multimodal',
            'separability': 'non-separable',
            'noise_level': 'low',
            'constraints': 'none',
            'objectives': 'single'
        }

        recs3 = recommend_algorithm(scenario3)
        assert len(recs3) > 0

    def test_performance_profiling_comparison(self):
        """Test performance profiling across algorithms."""

        def profile_algorithm_performance(algorithm_function, problem_size):
            """Profile algorithm performance characteristics."""

            # Memory usage simulation
            base_memory = 10.0  # MB
            memory_per_individual = 0.1  # MB per individual
            memory_per_dimension = 0.05  # MB per dimension

            estimated_memory = (base_memory +
                               memory_per_individual * problem_size['population'] +
                               memory_per_dimension * problem_size['dimensions'])

            # Runtime estimation
            base_runtime = 0.1  # seconds
            runtime_per_evaluation = 0.001  # seconds per evaluation
            runtime_per_iteration = 0.01  # seconds per iteration

            total_evaluations = problem_size['population'] * problem_size['iterations']
            estimated_runtime = (base_runtime +
                                runtime_per_evaluation * total_evaluations +
                                runtime_per_iteration * problem_size['iterations'])

            # Scalability analysis
            scalability_factor = problem_size['dimensions'] * problem_size['population']

            return {
                'estimated_memory_mb': estimated_memory,
                'estimated_runtime_seconds': estimated_runtime,
                'scalability_factor': scalability_factor,
                'evaluations_per_second': total_evaluations / estimated_runtime if estimated_runtime > 0 else 0,
                'memory_efficiency': scalability_factor / estimated_memory if estimated_memory > 0 else 0
            }

        # Test performance profiling for different problem sizes
        small_problem = {'population': 20, 'iterations': 50, 'dimensions': 6}
        medium_problem = {'population': 50, 'iterations': 100, 'dimensions': 20}
        large_problem = {'population': 100, 'iterations': 200, 'dimensions': 50}

        # Mock algorithm functions
        def mock_pso(problem_size):
            return f"PSO with {problem_size}"

        def mock_ga(problem_size):
            return f"GA with {problem_size}"

        def mock_de(problem_size):
            return f"DE with {problem_size}"

        algorithms = {'PSO': mock_pso, 'GA': mock_ga, 'DE': mock_de}
        problem_sizes = {'small': small_problem, 'medium': medium_problem, 'large': large_problem}

        performance_results = {}

        for alg_name, alg_func in algorithms.items():
            performance_results[alg_name] = {}

            for size_name, size_config in problem_sizes.items():
                profile = profile_algorithm_performance(alg_func, size_config)
                performance_results[alg_name][size_name] = profile

        # Validate performance profiling results
        for alg_name, alg_results in performance_results.items():
            for size_name, size_results in alg_results.items():
                assert 'estimated_memory_mb' in size_results
                assert 'estimated_runtime_seconds' in size_results
                assert 'evaluations_per_second' in size_results
                assert size_results['estimated_memory_mb'] > 0
                assert size_results['estimated_runtime_seconds'] > 0

        # Check scalability trends
        for alg_name in algorithms:
            small_memory = performance_results[alg_name]['small']['estimated_memory_mb']
            large_memory = performance_results[alg_name]['large']['estimated_memory_mb']
            assert large_memory > small_memory  # Memory should increase with problem size


if __name__ == "__main__":
    pytest.main([__file__, "-v"])