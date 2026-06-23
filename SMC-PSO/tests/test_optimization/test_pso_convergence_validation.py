#======================================================================================\\\
#============= tests/test_optimization/test_pso_convergence_validation.py =============\\\
#======================================================================================\\\

"""
Advanced PSO convergence criteria validation and monitoring.
Tests convergence detection, early stopping, and optimization quality metrics.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import List

from src.optimization.algorithms.pso_optimizer import PSOTuner


class TestPSOConvergenceDetection:
    """Test PSO convergence detection and criteria validation."""

    @pytest.fixture
    def convergence_config(self):
        """Configuration optimized for convergence testing."""
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
            n_particles: int = 20
            bounds: MockPSOBounds = None
            w: float = 0.5
            c1: float = 1.5
            c2: float = 1.5
            iters: int = 50
            tol: float = 1e-6
            early_stopping: bool = True
            patience: int = 10

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
    def convergence_controller_factory(self):
        """Controller factory with realistic convergence behavior."""
        def factory(gains):
            controller = Mock()
            controller.max_force = 150.0
            controller.gains = gains
            controller.controller_type = 'classical_smc'

            def validate_gains(particle_array):
                """Realistic gain validation with convergence constraints."""
                if particle_array.ndim == 1:
                    particle_array = particle_array.reshape(1, -1)

                valid_mask = np.ones(particle_array.shape[0], dtype=bool)

                # Basic feasibility
                valid_mask &= np.all(particle_array > 0, axis=1)
                valid_mask &= np.all(particle_array < 100, axis=1)

                # Stability constraints for convergence
                valid_mask &= (particle_array[:, 4] >= 5.0) & (particle_array[:, 4] <= 50.0)

                # Balance constraints to encourage convergence
                ratio_mask = (particle_array[:, 0] / particle_array[:, 1] < 5.0) & \
                           (particle_array[:, 1] / particle_array[:, 0] < 5.0)
                valid_mask &= ratio_mask

                return valid_mask

            controller.validate_gains = validate_gains
            return controller

        factory.n_gains = 6
        factory.controller_type = 'classical_smc'
        return factory

    def create_converging_simulation_mock(self):
        """Create simulation mock that shows converging behavior."""
        def mock_simulate(*args, **kwargs):
            particles = args[1] if len(args) > 1 else kwargs.get('particles')
            particles.shape[0]
            n_timesteps = 201

            t = np.linspace(0, 2.0, n_timesteps)

            # Create converging trajectories based on particle quality
            all_x, all_u, all_sigma = [], [], []

            for i, particle in enumerate(particles):
                # Better particles (closer to optimal) produce better trajectories
                optimal_gains = np.array([10.0, 8.0, 5.0, 3.0, 20.0, 2.0])
                gain_distance = np.linalg.norm(particle - optimal_gains)

                # Generate trajectory with decreasing error over time
                x = np.zeros((n_timesteps, 6))
                u = np.zeros(n_timesteps)
                sigma = np.zeros(n_timesteps)

                # Initial disturbance
                x[0] = [0.0, 0.05, -0.03, 0.0, 0.0, 0.0]

                for t_idx in range(1, n_timesteps):
                    # Exponential decay with gain-dependent rate
                    decay_rate = 0.02 + 0.01 / (1 + gain_distance)
                    noise_level = 0.001 * (1 + gain_distance)

                    # State evolution with convergence
                    x[t_idx] = x[t_idx-1] * (1 - decay_rate) + \
                               np.random.normal(0, noise_level, 6)

                    # Control effort
                    u[t_idx] = -np.sum(particle[:4] * x[t_idx, 2:6]) + \
                               np.random.normal(0, 0.1)

                    # Sliding variable
                    sigma[t_idx] = np.sum(particle[:2] * x[t_idx, 2:4]) + \
                                   np.sum(particle[2:4] * x[t_idx, 4:6])

                all_x.append(x)
                all_u.append(u)
                all_sigma.append(sigma)

            # Stack results
            x_batch = np.array(all_x)
            u_batch = np.array(all_u)
            sigma_batch = np.array(all_sigma)

            return (t, x_batch, u_batch, sigma_batch)

        return mock_simulate

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_convergence_trajectory_analysis(self, mock_simulate, convergence_config, convergence_controller_factory):
        """Test analysis of convergence trajectories."""
        mock_simulate.side_effect = self.create_converging_simulation_mock()

        tuner = PSOTuner(
            controller_factory=convergence_controller_factory,
            config=convergence_config,
            seed=42
        )

        # Test particles at different distances from optimum
        particles = np.array([
            [10.0, 8.0, 5.0, 3.0, 20.0, 2.0],    # Near optimal
            [15.0, 12.0, 8.0, 6.0, 30.0, 4.0],   # Moderate distance
            [5.0, 4.0, 2.0, 1.0, 10.0, 1.0],     # Far from optimal
            [25.0, 20.0, 15.0, 10.0, 40.0, 8.0], # Very far
        ])

        fitness = tuner._fitness(particles)

        # Verify convergence properties
        assert fitness.shape == (4,)
        assert np.all(np.isfinite(fitness))

        # Better particles should have lower cost
        assert fitness[0] < fitness[1] < fitness[2]

        # Test cost progression indicates convergence
        assert np.all(fitness > 0)

    @patch('pyswarms.single.GlobalBestPSO')
    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_optimization_convergence_detection(self, mock_simulate, mock_pso_class, convergence_config, convergence_controller_factory):
        """Test detection of optimization convergence."""
        mock_simulate.side_effect = self.create_converging_simulation_mock()

        # Create converging PSO mock
        class ConvergingPSOOptimizer:
            def __init__(self, *args, **kwargs):
                self.best_cost = 10.0
                self.best_pos = np.array([10.0, 8.0, 5.0, 3.0, 20.0, 2.0])
                self.cost_history = []
                self.pos_history = []
                self.options = {}

            def optimize(self, fitness_func, iters):
                """Simulate converging optimization."""
                self.cost_history = []
                self.pos_history = []

                current_cost = 10.0
                current_pos = np.random.uniform(5, 25, 6)

                for i in range(iters):
                    # Simulate convergence with noise
                    if i < 20:
                        # Fast initial convergence
                        improvement = 0.3 * np.exp(-i/10) + 0.01 * np.random.random()
                        current_cost = max(0.1, current_cost - improvement)
                    else:
                        # Slow final convergence
                        improvement = 0.01 * np.exp(-(i-20)/20) + 0.001 * np.random.random()
                        current_cost = max(0.05, current_cost - improvement)

                    # Update position towards optimum with noise
                    optimal = np.array([10.0, 8.0, 5.0, 3.0, 20.0, 2.0])
                    step_size = 0.1 * np.exp(-i/15)
                    current_pos += step_size * (optimal - current_pos) + \
                                   0.1 * np.random.normal(0, 1, 6)

                    self.cost_history.append(current_cost)
                    self.pos_history.append(current_pos.copy())

                self.best_cost = current_cost
                self.best_pos = current_pos.copy()

                return self.best_cost, self.best_pos

        mock_pso_class.return_value = ConvergingPSOOptimizer()

        tuner = PSOTuner(
            controller_factory=convergence_controller_factory,
            config=convergence_config,
            seed=42
        )

        result = tuner.optimise()

        # Analyze convergence
        cost_history = result['history']['cost']
        pos_history = result['history']['pos']

        # Test convergence criteria
        assert len(cost_history) > 0
        assert len(pos_history) > 0

        # Cost should generally decrease
        if len(cost_history) > 10:
            early_avg = np.mean(cost_history[:5])
            late_avg = np.mean(cost_history[-5:])
            assert late_avg < early_avg, "Cost should decrease over time"

        # Final cost should be reasonable
        assert result['best_cost'] < 5.0, "Should achieve reasonable final cost"

        # Position should be within reasonable bounds
        assert np.all(result['best_pos'] > 0), "Gains should be positive"
        assert np.all(result['best_pos'] < 100), "Gains should be reasonable"

    def test_convergence_metrics_calculation(self, convergence_config, convergence_controller_factory):
        """Test calculation of convergence quality metrics."""
        PSOTuner(
            controller_factory=convergence_controller_factory,
            config=convergence_config,
            seed=42
        )

        # Simulate convergence data
        cost_history = np.array([
            10.0, 8.5, 7.2, 6.1, 5.3, 4.8, 4.4, 4.1, 3.9, 3.8,
            3.7, 3.65, 3.62, 3.60, 3.59, 3.58, 3.58, 3.57, 3.57, 3.57
        ])

        # Test convergence rate calculation
        def calculate_convergence_rate(costs):
            """Calculate convergence rate."""
            if len(costs) < 2:
                return 0.0
            return (costs[0] - costs[-1]) / len(costs)

        conv_rate = calculate_convergence_rate(cost_history)
        assert conv_rate > 0, "Should have positive convergence rate"

        # Test plateau detection
        def detect_plateau(costs, window=5, threshold=0.01):
            """Detect convergence plateau."""
            if len(costs) < window:
                return False
            recent_costs = costs[-window:]
            return np.std(recent_costs) < threshold

        plateau_detected = detect_plateau(cost_history)
        assert plateau_detected, "Should detect convergence plateau"

        # Test relative improvement
        def calculate_relative_improvement(costs):
            """Calculate relative improvement."""
            if len(costs) < 2:
                return 0.0
            return (costs[0] - costs[-1]) / costs[0]

        rel_improvement = calculate_relative_improvement(cost_history)
        assert rel_improvement > 0.6, "Should show significant improvement"

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_early_stopping_criteria(self, mock_simulate, convergence_config, convergence_controller_factory):
        """Test early stopping criteria implementation."""
        mock_simulate.side_effect = self.create_converging_simulation_mock()

        class EarlyStoppingPSO:
            def __init__(self, *args, **kwargs):
                self.options = {}
                self.patience = 10
                self.tolerance = 1e-6

            def optimize(self, fitness_func, iters):
                """Simulate optimization with early stopping."""
                cost_history = []
                pos_history = []

                best_cost = float('inf')
                best_pos = np.random.uniform(5, 25, 6)
                no_improvement_count = 0

                for i in range(iters):
                    # Generate test particle
                    current_pos = best_pos + np.random.normal(0, 1, 6)
                    current_cost = best_cost * (0.95 + 0.1 * np.random.random())

                    if current_cost < best_cost - self.tolerance:
                        best_cost = current_cost
                        best_pos = current_pos.copy()
                        no_improvement_count = 0
                    else:
                        no_improvement_count += 1

                    cost_history.append(best_cost)
                    pos_history.append(best_pos.copy())

                    # Early stopping check
                    if no_improvement_count >= self.patience:
                        print(f"Early stopping at iteration {i}")
                        break

                self.cost_history = cost_history
                self.pos_history = pos_history
                return best_cost, best_pos

        # Enable early stopping in config
        config = convergence_config
        config.pso.early_stopping = True
        config.pso.patience = 5

        with patch('pyswarms.single.GlobalBestPSO', return_value=EarlyStoppingPSO()):
            tuner = PSOTuner(
                controller_factory=convergence_controller_factory,
                config=config,
                seed=42
            )

            result = tuner.optimise()

            # Should stop early if no improvement
            assert len(result['history']['cost']) <= config.pso.iters
            assert result['best_cost'] < float('inf')

    def test_convergence_quality_assessment(self, convergence_config, convergence_controller_factory):
        """Test assessment of convergence quality."""

        def assess_convergence_quality(cost_history, pos_history, target_cost=1.0):
            """Assess the quality of convergence."""
            metrics = {}

            if len(cost_history) == 0:
                return {'converged': False, 'quality': 'poor'}

            # Final cost quality
            final_cost = cost_history[-1]
            metrics['final_cost'] = final_cost
            metrics['target_achieved'] = final_cost <= target_cost

            # Convergence speed
            if len(cost_history) > 1:
                initial_cost = cost_history[0]
                metrics['improvement_ratio'] = (initial_cost - final_cost) / initial_cost
                metrics['convergence_speed'] = len(cost_history)
            else:
                metrics['improvement_ratio'] = 0.0
                metrics['convergence_speed'] = float('inf')

            # Stability of convergence
            if len(cost_history) >= 10:
                final_portion = cost_history[-10:]
                metrics['final_stability'] = 1.0 / (1.0 + np.std(final_portion))
            else:
                metrics['final_stability'] = 0.0

            # Overall quality score
            quality_score = (
                (1.0 if metrics['target_achieved'] else 0.5) *
                min(1.0, metrics['improvement_ratio']) *
                min(1.0, metrics['final_stability'])
            )

            if quality_score > 0.8:
                quality = 'excellent'
            elif quality_score > 0.6:
                quality = 'good'
            elif quality_score > 0.4:
                quality = 'fair'
            else:
                quality = 'poor'

            metrics['quality_score'] = quality_score
            metrics['quality'] = quality
            metrics['converged'] = quality_score > 0.5

            return metrics

        # Test with good convergence
        good_history = [10.0, 5.0, 2.0, 1.0, 0.8, 0.7, 0.65, 0.6, 0.58, 0.57]
        good_pos = [np.random.random(6) for _ in good_history]

        good_metrics = assess_convergence_quality(good_history, good_pos)
        assert good_metrics['converged']
        assert good_metrics['quality'] in ['good', 'excellent']

        # Test with poor convergence
        poor_history = [10.0, 9.5, 9.2, 9.1, 9.05, 9.0, 8.95, 8.9, 8.85, 8.8]
        poor_pos = [np.random.random(6) for _ in poor_history]

        poor_metrics = assess_convergence_quality(poor_history, poor_pos)
        assert poor_metrics['quality'] in ['poor', 'fair']

    @patch('src.optimization.algorithms.pso_optimizer.simulate_system_batch')
    def test_stagnation_detection(self, mock_simulate, convergence_config, convergence_controller_factory):
        """Test detection of optimization stagnation."""
        mock_simulate.side_effect = self.create_converging_simulation_mock()

        def detect_stagnation(cost_history, window=10, threshold=0.001):
            """Detect if optimization has stagnated."""
            if len(cost_history) < window:
                return False

            recent_costs = cost_history[-window:]
            cost_range = max(recent_costs) - min(recent_costs)
            mean_cost = np.mean(recent_costs)

            # Stagnation if relative change is very small
            return cost_range / mean_cost < threshold

        # Test with stagnating history
        stagnant_history = [5.0] + [5.0001 + 0.0001 * np.random.random() for _ in range(20)]
        assert detect_stagnation(stagnant_history)

        # Test with improving history
        improving_history = [10.0 - 0.2 * i for i in range(20)]
        assert not detect_stagnation(improving_history)

    def test_convergence_diagnostics(self, convergence_config, convergence_controller_factory):
        """Test comprehensive convergence diagnostics."""

        def run_convergence_diagnostics(cost_history, pos_history):
            """Run comprehensive convergence diagnostics."""
            diagnostics = {}

            if len(cost_history) == 0:
                return {'status': 'no_data'}

            # Basic statistics
            diagnostics['iterations'] = len(cost_history)
            diagnostics['initial_cost'] = cost_history[0]
            diagnostics['final_cost'] = cost_history[-1]
            diagnostics['best_cost'] = min(cost_history)

            # Convergence analysis
            if len(cost_history) > 1:
                # Rate of improvement
                total_improvement = cost_history[0] - cost_history[-1]
                diagnostics['total_improvement'] = total_improvement
                diagnostics['improvement_rate'] = total_improvement / len(cost_history)

                # Monotonicity
                decreasing_steps = sum(1 for i in range(1, len(cost_history))
                                     if cost_history[i] < cost_history[i-1])
                diagnostics['monotonicity'] = decreasing_steps / (len(cost_history) - 1)

                # Convergence speed (iterations to reach 90% of final improvement)
                if total_improvement > 0:
                    target_cost = cost_history[0] - 0.9 * total_improvement
                    conv_iter = next((i for i, cost in enumerate(cost_history)
                                    if cost <= target_cost), len(cost_history))
                    diagnostics['convergence_speed'] = conv_iter
                else:
                    diagnostics['convergence_speed'] = float('inf')

            # Stability analysis
            if len(cost_history) >= 10:
                final_portion = cost_history[-min(10, len(cost_history)):]
                diagnostics['final_stability'] = np.std(final_portion)
                diagnostics['final_mean'] = np.mean(final_portion)

            # Position analysis
            if len(pos_history) > 1:
                pos_array = np.array(pos_history)
                pos_changes = np.diff(pos_array, axis=0)
                diagnostics['position_stability'] = np.mean(np.linalg.norm(pos_changes, axis=1))

            # Overall assessment
            if diagnostics.get('total_improvement', 0) > 1.0 and \
               diagnostics.get('final_stability', float('inf')) < 0.1:
                diagnostics['status'] = 'converged'
            elif diagnostics.get('improvement_rate', 0) > 0.01:
                diagnostics['status'] = 'converging'
            else:
                diagnostics['status'] = 'stagnant'

            return diagnostics

        # Test with converged scenario
        converged_history = [10.0, 5.0, 2.0, 1.0, 0.5, 0.4, 0.35, 0.32, 0.31, 0.3]
        converged_pos = [np.array([10.0, 8.0, 5.0, 3.0, 20.0, 2.0]) + 0.1 * np.random.random(6)
                        for _ in converged_history]

        diag = run_convergence_diagnostics(converged_history, converged_pos)
        assert diag['status'] == 'converged'
        assert diag['total_improvement'] > 5.0
        assert diag['monotonicity'] > 0.8

        # Test with stagnant scenario
        stagnant_history = [5.0] * 10
        stagnant_pos = [np.array([5.0, 5.0, 5.0, 5.0, 15.0, 2.0])] * 10

        diag_stagnant = run_convergence_diagnostics(stagnant_history, stagnant_pos)
        assert diag_stagnant['status'] == 'stagnant'
        assert diag_stagnant['total_improvement'] == 0.0


class TestPSOParameterConvergence:
    """Test parameter-specific convergence behavior."""

    def test_gain_convergence_patterns(self):
        """Test convergence patterns for different gain types."""

        def analyze_gain_convergence(gain_history):
            """Analyze convergence patterns for each gain parameter."""
            gain_array = np.array(gain_history)
            n_gains = gain_array.shape[1]

            analysis = {}
            for i in range(n_gains):
                gain_values = gain_array[:, i]
                analysis[f'gain_{i}'] = {
                    'initial': gain_values[0],
                    'final': gain_values[-1],
                    'range': np.max(gain_values) - np.min(gain_values),
                    'stability': np.std(gain_values[-5:]) if len(gain_values) >= 5 else np.std(gain_values),
                    'trend': 'increasing' if gain_values[-1] > gain_values[0] else 'decreasing'
                }

            return analysis

        # Simulate converging gain history
        optimal_gains = np.array([10.0, 8.0, 5.0, 3.0, 20.0, 2.0])
        initial_gains = np.array([15.0, 12.0, 8.0, 6.0, 30.0, 4.0])

        gain_history = []
        current = initial_gains.copy()

        for i in range(20):
            # Move towards optimal with decreasing step size
            step_size = 0.1 * np.exp(-i/10)
            current = current + step_size * (optimal_gains - current) + \
                     0.05 * np.random.normal(0, 1, 6)
            gain_history.append(current.copy())

        analysis = analyze_gain_convergence(gain_history)

        # Verify convergence properties
        for i in range(6):
            gain_key = f'gain_{i}'
            assert analysis[gain_key]['stability'] < 1.0, f"Gain {i} should stabilize"
            final_diff = abs(analysis[gain_key]['final'] - optimal_gains[i])
            initial_diff = abs(analysis[gain_key]['initial'] - optimal_gains[i])
            assert final_diff < initial_diff, f"Gain {i} should move towards optimum"

    def test_controller_specific_convergence(self):
        """Test convergence behavior for different controller types."""

        def get_convergence_bounds(controller_type):
            """Get expected convergence bounds for different controllers."""
            bounds = {
                'classical_smc': {
                    'K1': (5.0, 15.0),     # Position gain
                    'K2': (4.0, 12.0),     # Velocity gain
                    'K3': (2.0, 8.0),      # Position gain 2
                    'K4': (1.0, 6.0),      # Velocity gain 2
                    'switching': (10.0, 30.0),  # Switching gain
                    'boundary': (1.0, 5.0)      # Boundary layer
                },
                'adaptive_smc': {
                    'K1': (8.0, 20.0),
                    'K2': (6.0, 16.0),
                    'K3': (3.0, 10.0),
                    'K4': (2.0, 8.0),
                    'adaptation': (0.5, 5.0)
                }
            }
            return bounds.get(controller_type, bounds['classical_smc'])

        def validate_convergence_bounds(final_gains, controller_type):
            """Validate that final gains are within expected convergence bounds."""
            bounds = get_convergence_bounds(controller_type)
            bound_names = list(bounds.keys())

            validation = {'within_bounds': True, 'violations': []}

            for i, gain_value in enumerate(final_gains):
                if i < len(bound_names):
                    bound_name = bound_names[i]
                    min_val, max_val = bounds[bound_name]

                    if not (min_val <= gain_value <= max_val):
                        validation['within_bounds'] = False
                        validation['violations'].append({
                            'parameter': bound_name,
                            'value': gain_value,
                            'expected_range': (min_val, max_val)
                        })

            return validation

        # Test classical SMC convergence
        classical_final = [10.0, 8.0, 5.0, 3.0, 20.0, 2.0]
        classical_validation = validate_convergence_bounds(classical_final, 'classical_smc')
        assert classical_validation['within_bounds'], f"Classical SMC bounds violated: {classical_validation['violations']}"

        # Test adaptive SMC convergence
        adaptive_final = [15.0, 12.0, 7.0, 5.0, 3.0]
        adaptive_validation = validate_convergence_bounds(adaptive_final, 'adaptive_smc')
        assert adaptive_validation['within_bounds'], f"Adaptive SMC bounds violated: {adaptive_validation['violations']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])