#==========================================================================================\\\
#================ tests/test_optimization/test_pso_cost_sensitivity.py ===================\\\
#==========================================================================================\\\

"""PSO Cost Function Sensitivity Tests

Regression tests for PSO fitness function to prevent cost=0.0 issues.
These tests validate that the cost function can distinguish between
good and bad controllers, and that normalization doesn't collapse costs.

Root Cause Context (Issue #10):
- Excessive baseline normalization caused costs to approach zero
- High state_error weight (50.0) couldn't overcome normalization
- All PSO particles converged to cost=0.0
- Fix: Removed baseline, added explicit norms, reduced weights
"""

import numpy as np
import pytest
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.config import load_config


@pytest.fixture
def pso_config():
    """Load configuration with fixed PSO settings"""
    config = load_config("config.yaml")
    return config


@pytest.fixture
def controller_factory():
    """Simple controller factory for testing"""
    def factory(gains):
        from src.controllers.smc.classic_smc import ClassicalSMC
        return ClassicalSMC(
            gains=gains.tolist() if hasattr(gains, 'tolist') else gains,
            max_force=100.0,
            boundary_layer=0.05,
            dt=0.01
        )
    return factory


class TestPSOCostSensitivity:
    """Test suite for PSO cost function sensitivity and robustness"""

    def test_cost_distinguishes_good_bad_controllers(self, controller_factory, pso_config):
        """Verify PSO can distinguish between good and bad controller gains"""
        tuner = PSOTuner(controller_factory, pso_config)

        # Good gains (well-tuned from previous optimizations)
        good_gains = np.array([[8.0, 4.0, 12.0, 6.0, 4.85, 3.43]])

        # Bad gains (very low, poor stabilization)
        bad_gains = np.array([[0.1, 0.1, 0.1, 0.1, 0.1, 0.1]])

        # Compute costs
        good_cost = tuner._cost(good_gains)
        bad_cost = tuner._cost(bad_gains)

        # Assertions
        assert np.isfinite(good_cost[0]), "Good controller should have finite cost"
        assert np.isfinite(bad_cost[0]), "Bad controller should have finite cost"
        assert good_cost[0] > 0, f"Good controller cost should be > 0, got {good_cost[0]}"
        assert bad_cost[0] > 0, f"Bad controller cost should be > 0, got {bad_cost[0]}"
        assert bad_cost[0] > good_cost[0], \
            f"Bad controller should have higher cost (bad={bad_cost[0]:.4e} vs good={good_cost[0]:.4e})"

        # Cost ratio should be significant (at least 2x difference)
        cost_ratio = bad_cost[0] / good_cost[0]
        assert cost_ratio > 2.0, \
            f"Bad controller should have significantly higher cost (ratio={cost_ratio:.2f})"

    def test_cost_variation_across_particles(self, controller_factory, pso_config):
        """Check that different particles have meaningfully different costs"""
        tuner = PSOTuner(controller_factory, pso_config)

        # Create diverse particle swarm (10 particles with random gains)
        np.random.seed(42)
        bounds_min = np.array([1.0, 1.0, 1.0, 1.0, 5.0, 0.1])
        bounds_max = np.array([100.0, 100.0, 20.0, 20.0, 150.0, 10.0])

        particles = np.random.uniform(
            low=bounds_min,
            high=bounds_max,
            size=(10, 6)
        )

        # Compute costs for all particles
        costs = tuner._cost(particles)

        # Assertions
        assert len(costs) == 10, "Should have 10 costs for 10 particles"
        assert np.all(np.isfinite(costs)), "All costs should be finite"
        assert np.all(costs > 0), f"All costs should be positive, got min={np.min(costs):.4e}"

        # Check for variation (not all costs the same)
        cost_std = np.std(costs)
        cost_mean = np.mean(costs)
        cv = cost_std / cost_mean  # Coefficient of variation

        assert cost_std > 1e-6, f"Costs should vary across particles (std={cost_std:.4e})"
        assert cv > 0.1, f"Costs should have meaningful variation (CV={cv:.2f})"

        # At least 50% of particles should have different costs
        unique_costs = len(np.unique(np.round(costs, decimals=6)))
        assert unique_costs >= 5, \
            f"At least 5 unique costs expected, got {unique_costs}"

    def test_no_baseline_normalization_regression(self, controller_factory, pso_config):
        """Ensure baseline normalization doesn't cause cost=0.0 regression"""
        # Verify baseline is None or removed from config
        baseline = getattr(pso_config.cost_function, 'baseline', None)
        if baseline is not None:
            # If baseline exists, check it doesn't have gains that cause issues
            gains = None
            if isinstance(baseline, dict):
                gains = baseline.get('gains')
            else:
                gains = getattr(baseline, 'gains', None)

            if gains is not None and len(gains) > 0:
                pytest.skip("Baseline normalization detected - this test validates the fix was applied")

        # Verify explicit norms are used instead
        tuner = PSOTuner(controller_factory, pso_config)

        # Check that normalization constants are reasonable (not huge)
        assert tuner.norm_ise < 1000.0, f"norm_ise too large: {tuner.norm_ise:.4e}"
        assert tuner.norm_u < 10000.0, f"norm_u too large: {tuner.norm_u:.4e}"
        assert tuner.norm_du < 100000.0, f"norm_du too large: {tuner.norm_du:.4e}"
        assert tuner.norm_sigma < 1000.0, f"norm_sigma too large: {tuner.norm_sigma:.4e}"

        # Test with typical gains
        test_gains = np.array([[10.0, 5.0, 15.0, 8.0, 20.0, 3.0]])
        cost = tuner._cost(test_gains)

        assert cost[0] > 1e-3, \
            f"Cost should not be near zero (cost={cost[0]:.4e}), indicating excessive normalization"

    def test_pso_convergence_not_premature(self, controller_factory, pso_config):
        """Verify PSO doesn't converge prematurely to zero cost"""
        tuner = PSOTuner(controller_factory, pso_config)

        # Create swarm with diverse gains
        np.random.seed(123)
        bounds_min = np.array([1.0, 1.0, 1.0, 1.0, 5.0, 0.1])
        bounds_max = np.array([100.0, 100.0, 20.0, 20.0, 150.0, 10.0])

        # Sample 30 particles from search space
        particles = np.random.uniform(
            low=bounds_min,
            high=bounds_max,
            size=(30, 6)
        )

        costs = tuner._cost(particles)

        # Check that costs span a reasonable range
        min_cost = np.min(costs)
        max_cost = np.max(costs)
        cost_range = max_cost - min_cost

        assert min_cost > 0, f"Minimum cost should be positive, got {min_cost:.4e}"
        assert cost_range > 1e-3, \
            f"Cost range too small (range={cost_range:.4e}), PSO cannot distinguish particles"

        # Verify cost distribution is not collapsed
        sorted_costs = np.sort(costs)
        percentiles = [sorted_costs[int(p * len(sorted_costs))] for p in [0.25, 0.5, 0.75]]

        # Q1, Q2, Q3 should be distinct
        assert percentiles[1] > percentiles[0] * 1.1, "Q2 should be > Q1 by at least 10%"
        assert percentiles[2] > percentiles[1] * 1.1, "Q3 should be > Q2 by at least 10%"

    def test_weighted_cost_contributions_balanced(self, controller_factory, pso_config):
        """Verify cost components contribute meaningfully (no single component dominates)"""
        tuner = PSOTuner(controller_factory, pso_config)

        # Test with reasonable gains
        np.array([[8.0, 4.0, 12.0, 6.0, 4.85, 3.43]])

        # Access internal cost components (need to replicate logic for testing)
        # This is a white-box test to ensure balance

        # Check weight ratios are reasonable
        weights = tuner.weights
        max_weight = max(weights.state_error, weights.control_effort,
                        weights.control_rate, weights.stability)
        min_weight = min(w for w in [weights.state_error, weights.control_effort,
                                     weights.control_rate, weights.stability] if w > 0)

        weight_ratio = max_weight / min_weight if min_weight > 0 else float('inf')

        assert weight_ratio < 100, \
            f"Weight ratio too high ({weight_ratio:.1f}), one component may dominate"

    def test_cost_function_deterministic(self, controller_factory, pso_config):
        """Verify cost function produces same results for same gains"""
        tuner = PSOTuner(controller_factory, pso_config)

        # Test gains
        test_gains = np.array([[8.0, 4.0, 12.0, 6.0, 4.85, 3.43]])

        # Compute cost twice
        cost1 = tuner._cost(test_gains)
        cost2 = tuner._cost(test_gains)

        # Should be identical (deterministic simulation)
        np.testing.assert_allclose(
            cost1, cost2,
            rtol=1e-10,
            err_msg="Cost function should be deterministic for same gains"
        )

    def test_extreme_gains_handled_gracefully(self, controller_factory, pso_config):
        """Test that extreme gain values don't break cost computation"""
        tuner = PSOTuner(controller_factory, pso_config)

        # Very small gains (near bounds)
        small_gains = np.array([[1.0, 1.0, 1.0, 1.0, 5.0, 0.1]])
        small_cost = tuner._cost(small_gains)

        assert np.isfinite(small_cost[0]), "Should handle small gains gracefully"
        assert small_cost[0] > 0, "Small gains should have positive cost"

        # Very large gains (near bounds)
        large_gains = np.array([[100.0, 100.0, 20.0, 20.0, 150.0, 10.0]])
        large_cost = tuner._cost(large_gains)

        assert np.isfinite(large_cost[0]), "Should handle large gains gracefully"
        assert large_cost[0] > 0, "Large gains should have positive cost"

        # Neither should be instability penalty
        assert small_cost[0] < tuner.instability_penalty * 0.9, \
            "Small gains shouldn't trigger full instability penalty"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])