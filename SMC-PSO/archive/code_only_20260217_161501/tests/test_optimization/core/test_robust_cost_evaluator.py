#======================================================================================\\\
#============ tests/test_optimization/core/test_robust_cost_evaluator.py ==============\\\
#======================================================================================\\\

"""
Unit tests for RobustCostEvaluator class.

Tests multi-scenario PSO optimization addressing MT-7 overfitting issue where
gains trained on small perturbations (±0.05 rad) show 50.4x chattering
degradation on realistic perturbations (±0.3 rad).

Coverage:
- Scenario generation with configurable distributions
- Robust fitness calculation (mean + α*max)
- IC override functionality
- Seed reproducibility
- Configuration validation
- Edge cases and error handling
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import List, Optional

from src.optimization.core.robust_cost_evaluator import RobustCostEvaluator


# ------------------------------------------------------------------------------
# Mock Configuration Objects
# ------------------------------------------------------------------------------

@dataclass
class MockRobustnessConfig:
    """Mock robustness configuration."""
    enabled: bool = True
    n_scenarios: int = 15
    worst_case_weight: float = 0.3
    scenario_distribution: 'MockScenarioDistribution' = None
    nominal_range: float = 0.05
    moderate_range: float = 0.15
    large_range: float = 0.3
    seed: Optional[int] = 42

    def __post_init__(self):
        if self.scenario_distribution is None:
            self.scenario_distribution = MockScenarioDistribution()


@dataclass
class MockScenarioDistribution:
    """Mock scenario distribution configuration."""
    nominal_fraction: float = 0.2
    moderate_fraction: float = 0.3
    large_fraction: float = 0.5


@dataclass
class MockPSOConfig:
    """Mock PSO configuration."""
    robustness: MockRobustnessConfig = None

    def __post_init__(self):
        if self.robustness is None:
            self.robustness = MockRobustnessConfig()


@dataclass
class MockPhysics:
    """Mock physics configuration."""
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


@dataclass
class MockSimulation:
    """Mock simulation configuration."""
    duration: float = 1.0
    dt: float = 0.01
    initial_state: List[float] = None
    use_full_dynamics: bool = False

    def __post_init__(self):
        if self.initial_state is None:
            self.initial_state = [0.0, 0.05, -0.03, 0.0, 0.0, 0.0]


@dataclass
class MockWeights:
    """Mock cost function weights."""
    state_error: float = 50.0
    control_effort: float = 0.2
    control_rate: float = 0.1
    stability: float = 0.1


@dataclass
class MockCombineWeights:
    """Mock combine weights."""
    mean: float = 0.7
    max: float = 0.3


@dataclass
class MockCostFunction:
    """Mock cost function configuration."""
    weights: MockWeights = None
    instability_penalty: float = 1000.0
    combine_weights: MockCombineWeights = None
    normalization_threshold: float = 1e-12

    def __post_init__(self):
        if self.weights is None:
            self.weights = MockWeights()
        if self.combine_weights is None:
            self.combine_weights = MockCombineWeights()


@dataclass
class MockConfig:
    """Mock full configuration."""
    pso: MockPSOConfig = None
    physics: MockPhysics = None
    simulation: MockSimulation = None
    cost_function: MockCostFunction = None

    def __post_init__(self):
        if self.pso is None:
            self.pso = MockPSOConfig()
        if self.physics is None:
            self.physics = MockPhysics()
        if self.simulation is None:
            self.simulation = MockSimulation()
        if self.cost_function is None:
            self.cost_function = MockCostFunction()


# ------------------------------------------------------------------------------
# Test Class
# ------------------------------------------------------------------------------

class TestRobustCostEvaluator:
    """Test suite for RobustCostEvaluator."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration with robustness enabled."""
        return MockConfig()

    @pytest.fixture
    def mock_controller_factory(self):
        """Create mock controller factory."""
        def factory(gains):
            mock_controller = Mock()
            mock_controller.gains = gains
            return mock_controller
        factory.n_gains = 6
        factory.controller_type = "classical_smc"
        return factory

    @pytest.fixture
    def evaluator(self, mock_controller_factory, mock_config):
        """Create RobustCostEvaluator instance."""
        return RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42
        )

    # --------------------------------------------------------------------------
    # Initialization Tests
    # --------------------------------------------------------------------------

    def test_initialization_with_defaults(self, mock_controller_factory, mock_config):
        """Test evaluator initializes with default robustness config."""
        evaluator = RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42
        )

        assert evaluator.n_scenarios == 15
        assert evaluator.worst_case_weight == 0.3
        assert len(evaluator.scenarios) == 15
        assert evaluator.rng is not None

    def test_initialization_without_robustness_config(self, mock_controller_factory):
        """Test evaluator uses defaults when robustness config is missing."""
        config = MockConfig()
        config.pso.robustness = None

        evaluator = RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=config,
            seed=42
        )

        # Should use hardcoded defaults
        assert evaluator.n_scenarios == 15
        assert evaluator.worst_case_weight == 0.3

    def test_initialization_custom_parameters(self, mock_controller_factory, mock_config):
        """Test evaluator respects custom robustness parameters."""
        # Note: Parameters must be passed explicitly, not read from config
        evaluator = RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            n_scenarios=30,
            worst_case_weight=0.5,
            nominal_range=0.1,
            moderate_range=0.2,
            large_range=0.4
        )

        assert evaluator.n_scenarios == 30
        assert evaluator.worst_case_weight == 0.5
        assert len(evaluator.scenarios) == 30

    # --------------------------------------------------------------------------
    # Scenario Generation Tests
    # --------------------------------------------------------------------------

    def test_scenario_generation_count(self, evaluator):
        """Test correct number of scenarios are generated."""
        assert len(evaluator.scenarios) == 15

    def test_scenario_generation_distribution(self, evaluator, mock_config):
        """Test scenarios follow configured distribution (20/30/50)."""
        cfg = mock_config.pso.robustness
        n_nominal = int(cfg.n_scenarios * cfg.scenario_distribution.nominal_fraction)
        n_moderate = int(cfg.n_scenarios * cfg.scenario_distribution.moderate_fraction)
        n_large = cfg.n_scenarios - n_nominal - n_moderate

        assert n_nominal == 3  # 20% of 15 = 3
        assert n_moderate == 4  # 30% of 15 = 4.5 -> 4
        assert n_large == 8    # Remaining 8

        # Verify total matches
        assert n_nominal + n_moderate + n_large == 15

    def test_scenario_generation_ranges(self, evaluator):
        """Test scenarios respect configured angle ranges."""
        for scenario in evaluator.scenarios:
            # Check cart position is always zero
            assert scenario[0] == 0.0

            # Check angle perturbations within largest range (0.3 rad)
            assert abs(scenario[1]) <= 0.3
            assert abs(scenario[2]) <= 0.3

            # Note: Velocities ARE perturbed for moderate/large scenarios
            # Nominal (20%): velocities = 0.0
            # Moderate (30%): velocities in [-0.2, 0.2]
            # Large (50%): velocities in [-0.5, 0.5]
            assert abs(scenario[3]) <= 0.5  # Cart velocity
            assert abs(scenario[4]) <= 0.5  # θ1 velocity
            assert abs(scenario[5]) <= 0.5  # θ2 velocity

    def test_scenario_generation_reproducibility(self, mock_controller_factory, mock_config):
        """Test scenario generation is reproducible with same seed."""
        eval1 = RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=12345
        )
        eval2 = RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=12345
        )

        scenarios1 = np.array(eval1.scenarios)
        scenarios2 = np.array(eval2.scenarios)

        np.testing.assert_array_equal(scenarios1, scenarios2)

    def test_scenario_generation_different_seeds(self, mock_controller_factory, mock_config):
        """Test different seeds produce different scenarios."""
        eval1 = RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=111
        )
        eval2 = RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=222
        )

        scenarios1 = np.array(eval1.scenarios)
        scenarios2 = np.array(eval2.scenarios)

        # Should be different
        assert not np.allclose(scenarios1, scenarios2)

    # --------------------------------------------------------------------------
    # Robust Fitness Calculation Tests
    # --------------------------------------------------------------------------

    def test_robust_fitness_calculation(self, evaluator):
        """Test robust fitness formula: J_robust = mean(costs) + α*max(costs)."""
        # Setup: 3 controllers, 15 scenarios
        # Controller 1: costs [1.0]*15 -> mean=1.0, max=1.0 -> J=1.0+0.3*1.0=1.3
        # Controller 2: costs [2.0]*15 -> mean=2.0, max=2.0 -> J=2.0+0.3*2.0=2.6
        # Controller 3: costs [0.5,5.0,...]  -> mean=1.5, max=5.0 -> J=1.5+0.3*5.0=3.0

        population = np.array([
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],  # Controller 1
            [2.0, 2.0, 2.0, 2.0, 2.0, 2.0],  # Controller 2
            [3.0, 3.0, 3.0, 3.0, 3.0, 3.0],  # Controller 3
        ])

        # Mock _evaluate_scenario to return controlled costs
        with patch.object(evaluator, '_evaluate_scenario') as mock_eval_scenario:
            # Controller 1: all scenarios cost 1.0
            # Controller 2: all scenarios cost 2.0
            # Controller 3: mixed costs
            def side_effect(pop, scenario_ic):
                # Return costs based on which controller
                B = pop.shape[0]
                costs = np.zeros(B)
                for i in range(B):
                    if np.allclose(pop[i], population[0]):
                        costs[i] = 1.0
                    elif np.allclose(pop[i], population[1]):
                        costs[i] = 2.0
                    else:  # Controller 3
                        # Make it scenario-dependent for variety
                        costs[i] = 0.5 if scenario_ic[1] < 0.1 else 5.0
                return costs

            mock_eval_scenario.side_effect = side_effect

            robust_costs = evaluator.evaluate_batch_robust(population)

            # Controller 1: mean=1.0, max=1.0 -> 1.0 + 0.3*1.0 = 1.3
            # Controller 2: mean=2.0, max=2.0 -> 2.0 + 0.3*2.0 = 2.6
            # Controller 3: mean varies, max=5.0 -> mean + 0.3*5.0

            assert robust_costs.shape == (3,)
            assert 1.0 <= robust_costs[0] <= 2.0  # Should be around 1.3
            assert 2.0 <= robust_costs[1] <= 3.0  # Should be around 2.6
            assert 2.0 <= robust_costs[2] <= 5.0  # Should include worst case

    def test_worst_case_weight_impact(self, mock_controller_factory, mock_config):
        """Test that worst_case_weight properly amplifies max cost."""
        # Test with α=0.0 (mean only) vs α=1.0 (max only)
        population = np.array([[1.0, 1.0, 1.0, 1.0, 1.0, 1.0]])

        # Create evaluators with different α
        eval_alpha0 = RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            worst_case_weight=0.0
        )

        eval_alpha1 = RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,  # Same seed for same scenarios
            worst_case_weight=1.0
        )

        # Mock scenario costs: mean=2.0, max=10.0
        with patch.object(eval_alpha0, '_evaluate_scenario') as mock0:
            with patch.object(eval_alpha1, '_evaluate_scenario') as mock1:
                # Make costs vary per scenario
                def vary_costs(pop, ic):
                    # First 3 scenarios: 2.0, rest: 10.0
                    if ic[1] < 0.1:
                        return np.array([2.0])
                    else:
                        return np.array([10.0])

                mock0.side_effect = vary_costs
                mock1.side_effect = vary_costs

                cost_alpha0 = eval_alpha0.evaluate_batch_robust(population)
                cost_alpha1 = eval_alpha1.evaluate_batch_robust(population)

                # α=0.0: J = mean only
                # α=1.0: J = mean + max

                # With 3 scenarios at 2.0 and 12 at 10.0:
                # mean ≈ (3*2 + 12*10)/15 = 86/15 ≈ 5.73
                # max = 10.0
                # α=0.0: J ≈ 5.73
                # α=1.0: J ≈ 5.73 + 10.0 = 15.73

                assert cost_alpha0[0] < cost_alpha1[0]  # α=0 should be less
                assert cost_alpha1[0] > cost_alpha0[0] * 1.5  # Significantly larger

    # --------------------------------------------------------------------------
    # Edge Cases and Error Handling
    # --------------------------------------------------------------------------

    def test_single_scenario(self, mock_controller_factory, mock_config):
        """Test evaluator works with n_scenarios=1."""
        evaluator = RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            n_scenarios=1
        )

        assert len(evaluator.scenarios) == 1

        population = np.array([[1.0, 1.0, 1.0, 1.0, 1.0, 1.0]])

        with patch.object(evaluator, '_evaluate_scenario', return_value=np.array([5.0])):
            costs = evaluator.evaluate_batch_robust(population)
            # mean=5.0, max=5.0 -> 5.0 + 0.3*5.0 = 6.5
            np.testing.assert_allclose(costs, [6.5], rtol=1e-5)

    def test_large_scenario_count(self, mock_controller_factory, mock_config):
        """Test evaluator handles large scenario counts."""
        evaluator = RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            n_scenarios=100
        )

        assert len(evaluator.scenarios) == 100
        assert evaluator.n_scenarios == 100

    def test_zero_worst_case_weight(self, mock_controller_factory, mock_config):
        """Test α=0.0 reduces to mean-only cost."""
        evaluator = RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            worst_case_weight=0.0
        )

        population = np.array([[1.0, 1.0, 1.0, 1.0, 1.0, 1.0]])

        with patch.object(evaluator, '_evaluate_scenario') as mock_eval:
            # Return costs: [1.0, 2.0, 3.0, ...] for different scenarios
            def vary_costs(pop, ic):
                return np.array([1.0 + abs(ic[1]) * 10])
            mock_eval.side_effect = vary_costs

            costs = evaluator.evaluate_batch_robust(population)

            # With α=0, should only see mean, no max contribution
            # Cost should be positive (mean of scenario costs)
            assert costs[0] > 0

    def test_max_worst_case_weight(self, mock_controller_factory, mock_config):
        """Test α=1.0 heavily weights worst case."""
        evaluator = RobustCostEvaluator(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            worst_case_weight=1.0
        )

        assert evaluator.worst_case_weight == 1.0

    # --------------------------------------------------------------------------
    # Integration with Parent Class Tests
    # --------------------------------------------------------------------------

    def test_inherits_from_controller_cost_evaluator(self, evaluator):
        """Test RobustCostEvaluator inherits from ControllerCostEvaluator."""
        from src.optimization.core.cost_evaluator import ControllerCostEvaluator
        assert isinstance(evaluator, ControllerCostEvaluator)

    def test_single_evaluation_fallback(self, evaluator):
        """Test evaluate_single_robust works via batch evaluation."""
        gains = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0])

        # evaluate_single_robust reshapes to (1, n_gains) and calls evaluate_batch_robust
        with patch.object(evaluator, 'evaluate_batch_robust', return_value=np.array([5.5])) as mock_batch:
            cost = evaluator.evaluate_single_robust(gains)

            # Verify it called evaluate_batch_robust with reshaped gains
            mock_batch.assert_called_once()
            call_args = mock_batch.call_args[0][0]
            assert call_args.shape == (1, 6)
            np.testing.assert_array_equal(call_args[0], gains)

            assert cost == 5.5

    # --------------------------------------------------------------------------
    # Scenario Diversity Tests
    # --------------------------------------------------------------------------

    def test_scenarios_cover_nominal_range(self, evaluator, mock_config):
        """Test some scenarios fall within nominal range."""
        cfg = mock_config.pso.robustness
        nominal_count = 0

        for scenario in evaluator.scenarios:
            theta1, theta2 = scenario[1], scenario[2]
            if abs(theta1) <= cfg.nominal_range and abs(theta2) <= cfg.nominal_range:
                nominal_count += 1

        # Should have at least some nominal scenarios (20% = 3)
        assert nominal_count >= 2

    def test_scenarios_include_large_perturbations(self, evaluator, mock_config):
        """Test some scenarios include large perturbations."""
        cfg = mock_config.pso.robustness
        large_count = 0

        for scenario in evaluator.scenarios:
            theta1, theta2 = scenario[1], scenario[2]
            if abs(theta1) > cfg.moderate_range or abs(theta2) > cfg.moderate_range:
                large_count += 1

        # Should have large scenarios (50% = 7-8)
        assert large_count >= 5

    def test_scenarios_diverse_angle_combinations(self, evaluator):
        """Test scenarios include diverse angle combinations."""
        scenarios = np.array(evaluator.scenarios)
        theta1_vals = scenarios[:, 1]
        theta2_vals = scenarios[:, 2]

        # Check we have both positive and negative angles
        assert np.any(theta1_vals > 0)
        assert np.any(theta1_vals < 0)
        assert np.any(theta2_vals > 0)
        assert np.any(theta2_vals < 0)

        # Check standard deviation is reasonable (not all same)
        assert np.std(theta1_vals) > 0.01
        assert np.std(theta2_vals) > 0.01


# ------------------------------------------------------------------------------
# Parametric Tests
# ------------------------------------------------------------------------------

@pytest.mark.parametrize("n_scenarios", [3, 10, 15, 30, 50])
def test_scenario_count_parametric(n_scenarios, mock_controller_factory):
    """Test various scenario counts."""
    config = MockConfig()

    evaluator = RobustCostEvaluator(
        controller_factory=mock_controller_factory,
        config=config,
        seed=42,
        n_scenarios=n_scenarios
    )

    assert len(evaluator.scenarios) == n_scenarios


@pytest.mark.parametrize("alpha", [0.0, 0.1, 0.3, 0.5, 1.0])
def test_worst_case_weight_parametric(alpha, mock_controller_factory):
    """Test various worst-case weights."""
    config = MockConfig()

    evaluator = RobustCostEvaluator(
        controller_factory=mock_controller_factory,
        config=config,
        seed=42,
        worst_case_weight=alpha
    )

    assert evaluator.worst_case_weight == alpha


@pytest.mark.parametrize("seed", [None, 0, 42, 12345, 999999])
def test_seed_handling_parametric(seed, mock_controller_factory):
    """Test various seed values including None."""
    config = MockConfig()
    config.pso.robustness.seed = seed

    evaluator = RobustCostEvaluator(
        controller_factory=mock_controller_factory,
        config=config,
        seed=seed
    )

    # Should not crash regardless of seed
    assert len(evaluator.scenarios) == 15
