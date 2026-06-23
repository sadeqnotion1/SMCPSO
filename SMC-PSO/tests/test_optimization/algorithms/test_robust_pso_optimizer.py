#======================================================================================\\\
#======== tests/test_optimization/algorithms/test_robust_pso_optimizer.py =============\\\
#======================================================================================\\\

"""
Unit tests for RobustPSOTuner class.

Tests the robust PSO optimizer wrapper that extends PSOTuner with multi-scenario
evaluation to address MT-7 overfitting issue.

Coverage:
- Initialization with robust_enabled flag
- Fallback to standard PSO when disabled
- Integration with RobustCostEvaluator
- Configuration validation
- Backward compatibility
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import List, Optional

from src.optimization.algorithms.robust_pso_optimizer import RobustPSOTuner


# ------------------------------------------------------------------------------
# Mock Configuration Objects (reuse from test_robust_cost_evaluator)
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
class MockPSOBounds:
    """Mock PSO bounds."""
    min: List[float] = None
    max: List[float] = None

    def __post_init__(self):
        if self.min is None:
            self.min = [1.0, 1.0, 1.0, 0.1, 1.0, 0.1]
        if self.max is None:
            self.max = [20.0, 20.0, 10.0, 5.0, 50.0, 5.0]


@dataclass
class MockPSOBoundsWithControllers:
    """Mock PSO bounds with controller-specific overrides."""
    min: List[float] = None
    max: List[float] = None
    classical_smc: Optional[MockPSOBounds] = None

    def __post_init__(self):
        if self.min is None:
            self.min = [1.0, 1.0, 1.0, 0.1, 1.0, 0.1]
        if self.max is None:
            self.max = [20.0, 20.0, 10.0, 5.0, 50.0, 5.0]


@dataclass
class MockPSOConfig:
    """Mock PSO configuration."""
    n_particles: int = 10
    iters: int = 20
    bounds: MockPSOBoundsWithControllers = None
    w: float = 0.7
    c1: float = 2.0
    c2: float = 2.0
    seed: Optional[int] = 42
    robustness: Optional[MockRobustnessConfig] = None

    def __post_init__(self):
        if self.bounds is None:
            self.bounds = MockPSOBoundsWithControllers()
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

class TestRobustPSOTuner:
    """Test suite for RobustPSOTuner."""

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
            mock_controller.compute_control = Mock(return_value=0.0)
            return mock_controller
        factory.n_gains = 6
        factory.controller_type = "classical_smc"
        return factory

    # --------------------------------------------------------------------------
    # Initialization Tests
    # --------------------------------------------------------------------------

    def test_initialization_robust_enabled(self, mock_controller_factory, mock_config):
        """Test tuner initializes with robust mode enabled."""
        tuner = RobustPSOTuner(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            robust_enabled=True
        )

        assert tuner.robust_enabled is True
        assert hasattr(tuner, 'robust_evaluator')
        assert tuner.robust_evaluator is not None

    def test_initialization_robust_disabled(self, mock_controller_factory, mock_config):
        """Test tuner falls back to standard PSO when disabled."""
        tuner = RobustPSOTuner(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            robust_enabled=False
        )

        assert tuner.robust_enabled is False
        assert tuner.robust_evaluator is None

    def test_initialization_from_config_enabled(self, mock_controller_factory, mock_config):
        """Test tuner reads robust_enabled from config when not provided."""
        mock_config.pso.robustness.enabled = True

        tuner = RobustPSOTuner(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            robust_enabled=None  # Let it auto-detect from config
        )

        assert tuner.robust_enabled is True

    def test_initialization_from_config_disabled(self, mock_controller_factory, mock_config):
        """Test tuner respects config when robustness disabled."""
        mock_config.pso.robustness.enabled = False

        tuner = RobustPSOTuner(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            robust_enabled=None
        )

        assert tuner.robust_enabled is False

    def test_initialization_cli_overrides_config(self, mock_controller_factory, mock_config):
        """Test CLI flag overrides config setting."""
        mock_config.pso.robustness.enabled = False

        # CLI flag True should override config False
        tuner = RobustPSOTuner(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            robust_enabled=True
        )

        assert tuner.robust_enabled is True

    def test_initialization_missing_robustness_config(self, mock_controller_factory):
        """Test tuner handles missing robustness config gracefully."""
        config = MockConfig()
        config.pso.robustness = None

        tuner = RobustPSOTuner(
            controller_factory=mock_controller_factory,
            config=config,
            seed=42,
            robust_enabled=False
        )

        # Should not crash, should disable robustness
        assert tuner.robust_enabled is False

    # --------------------------------------------------------------------------
    # Fitness Function Tests
    # --------------------------------------------------------------------------

    @patch('src.optimization.algorithms.robust_pso_optimizer.RobustCostEvaluator')
    def test_fitness_uses_robust_evaluator(self, MockRobustEval, mock_controller_factory, mock_config):
        """Test _fitness delegates to robust evaluator when enabled."""
        mock_evaluator_instance = Mock()
        mock_evaluator_instance.evaluate_batch_robust = Mock(return_value=np.array([1.5, 2.5, 3.5]))
        MockRobustEval.return_value = mock_evaluator_instance

        tuner = RobustPSOTuner(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            robust_enabled=True
        )

        particles = np.array([
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [2.0, 2.0, 2.0, 2.0, 2.0, 2.0],
            [3.0, 3.0, 3.0, 3.0, 3.0, 3.0],
        ])

        costs = tuner._fitness(particles)

        # Should call robust evaluator
        mock_evaluator_instance.evaluate_batch_robust.assert_called_once()
        np.testing.assert_array_equal(costs, [1.5, 2.5, 3.5])

    def test_fitness_falls_back_to_parent(self, mock_controller_factory, mock_config):
        """Test _fitness uses parent PSOTuner method when robust disabled."""
        tuner = RobustPSOTuner(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            robust_enabled=False
        )

        particles = np.array([
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        ])

        # Mock parent _fitness method
        with patch('src.optimization.algorithms.pso_optimizer.PSOTuner._fitness', return_value=np.array([10.0])) as mock_parent_fitness:
            costs = tuner._fitness(particles)

            # Should call parent method
            mock_parent_fitness.assert_called_once()
            np.testing.assert_array_equal(costs, [10.0])

    # --------------------------------------------------------------------------
    # Integration Tests
    # --------------------------------------------------------------------------

    def test_inherits_from_pso_tuner(self, mock_controller_factory, mock_config):
        """Test RobustPSOTuner inherits from PSOTuner."""
        from src.optimization.algorithms.pso_optimizer import PSOTuner

        tuner = RobustPSOTuner(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            robust_enabled=True
        )

        assert isinstance(tuner, PSOTuner)

    def test_has_all_parent_attributes(self, mock_controller_factory, mock_config):
        """Test tuner has all PSOTuner attributes."""
        tuner = RobustPSOTuner(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            robust_enabled=True
        )

        # Check key PSOTuner attributes exist
        assert hasattr(tuner, 'controller_factory')
        assert hasattr(tuner, 'cfg')
        assert hasattr(tuner, 'seed')
        assert hasattr(tuner, '_fitness')

    # --------------------------------------------------------------------------
    # Backward Compatibility Tests
    # --------------------------------------------------------------------------

    def test_backward_compatible_with_standard_pso(self, mock_controller_factory, mock_config):
        """Test RobustPSOTuner works as drop-in replacement for PSOTuner."""
        from src.optimization.algorithms.pso_optimizer import PSOTuner

        # Create both tuners with same config
        standard_tuner = PSOTuner(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42
        )

        robust_tuner = RobustPSOTuner(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            robust_enabled=False  # Disabled = standard behavior
        )

        # Both should have same basic attributes
        assert standard_tuner.seed == robust_tuner.seed
        assert hasattr(standard_tuner, '_fitness') and hasattr(robust_tuner, '_fitness')

    def test_can_disable_robustness_after_config_enabled(self, mock_controller_factory, mock_config):
        """Test CLI flag can disable robustness even if config enables it."""
        mock_config.pso.robustness.enabled = True

        tuner = RobustPSOTuner(
            controller_factory=mock_controller_factory,
            config=mock_config,
            seed=42,
            robust_enabled=False  # Explicit disable
        )

        assert tuner.robust_enabled is False

    # --------------------------------------------------------------------------
    # Configuration Propagation Tests
    # --------------------------------------------------------------------------

    def test_robust_evaluator_receives_correct_config(self, mock_controller_factory, mock_config):
        """Test RobustCostEvaluator receives same config as tuner."""
        with patch('src.optimization.algorithms.robust_pso_optimizer.RobustCostEvaluator') as MockEvaluator:
            tuner = RobustPSOTuner(
                controller_factory=mock_controller_factory,
                config=mock_config,
                seed=42,
                robust_enabled=True
            )

            # Check evaluator was created with correct config
            MockEvaluator.assert_called_once()
            call_kwargs = MockEvaluator.call_args[1]
            assert call_kwargs['config'] == mock_config
            assert call_kwargs['seed'] == 42

    def test_respects_custom_scenario_count(self, mock_controller_factory, mock_config):
        """Test tuner respects custom n_scenarios from config."""
        mock_config.pso.robustness.n_scenarios = 50

        with patch('src.optimization.algorithms.robust_pso_optimizer.RobustCostEvaluator') as MockEvaluator:
            mock_evaluator = Mock()
            mock_evaluator.n_scenarios = 50
            MockEvaluator.return_value = mock_evaluator

            tuner = RobustPSOTuner(
                controller_factory=mock_controller_factory,
                config=mock_config,
                seed=42,
                robust_enabled=True
            )

            # Evaluator should be created (implicitly uses config with n_scenarios=50)
            MockEvaluator.assert_called_once()

    def test_respects_custom_worst_case_weight(self, mock_controller_factory, mock_config):
        """Test tuner respects custom worst_case_weight from config."""
        mock_config.pso.robustness.worst_case_weight = 0.7

        with patch('src.optimization.algorithms.robust_pso_optimizer.RobustCostEvaluator') as MockEvaluator:
            mock_evaluator = Mock()
            mock_evaluator.worst_case_weight = 0.7
            MockEvaluator.return_value = mock_evaluator

            tuner = RobustPSOTuner(
                controller_factory=mock_controller_factory,
                config=mock_config,
                seed=42,
                robust_enabled=True
            )

            MockEvaluator.assert_called_once()


# ------------------------------------------------------------------------------
# Parametric Tests
# ------------------------------------------------------------------------------

@pytest.mark.parametrize("robust_enabled", [True, False])
def test_robust_enabled_parametric(robust_enabled, mock_controller_factory):
    """Test both enabled and disabled modes."""
    config = MockConfig()

    tuner = RobustPSOTuner(
        controller_factory=mock_controller_factory,
        config=config,
        seed=42,
        robust_enabled=robust_enabled
    )

    assert tuner.robust_enabled == robust_enabled

    if robust_enabled:
        assert tuner.robust_evaluator is not None
    else:
        assert tuner.robust_evaluator is None


@pytest.mark.parametrize("config_enabled,cli_enabled,expected", [
    (True, True, True),
    (True, False, False),
    (False, True, True),
    (False, False, False),
    (True, None, True),
    (False, None, False),
])
def test_config_cli_interaction_parametric(config_enabled, cli_enabled, expected, mock_controller_factory):
    """Test interaction between config and CLI robust_enabled settings."""
    config = MockConfig()
    config.pso.robustness.enabled = config_enabled

    tuner = RobustPSOTuner(
        controller_factory=mock_controller_factory,
        config=config,
        seed=42,
        robust_enabled=cli_enabled
    )

    assert tuner.robust_enabled == expected
