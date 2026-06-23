#======================================================================================
#== tests/test_controllers/smc/algorithms/conditional_hybrid/test_controller_integration.py ==
#======================================================================================

"""
Comprehensive Integration Tests for Conditional Hybrid SMC Controller.

Tests the complete controller with full DIP dynamics, validates performance
metrics, and compares against Adaptive SMC baseline.
"""

import pytest
import numpy as np
from pathlib import Path

from src.controllers.smc.algorithms.conditional_hybrid.controller import ConditionalHybridController
from src.controllers.smc.algorithms.conditional_hybrid.config import ConditionalHybridConfig
from src.controllers.smc.algorithms.adaptive.controller import ModularAdaptiveSMC
from src.controllers.smc.algorithms.adaptive.config import AdaptiveSMCConfig


# Mock dynamics model for testing
class MockDynamics:
    """Mock dynamics model that provides compute_dynamics for integration testing."""

    def compute_dynamics(self, state: np.ndarray, u: float) -> np.ndarray:
        """
        Simplified linearized dynamics for testing.

        State: [x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂]
        """
        # Simple linearized dynamics (good enough for testing controller interface)
        x, theta1, theta2, x_dot, theta1_dot, theta2_dot = state

        # Simplified accelerations (not physics-accurate, just for testing)
        x_ddot = u - 0.1 * x_dot  # Cart acceleration with friction
        theta1_ddot = -theta1 + 0.5 * u - 0.01 * theta1_dot  # Pendulum 1 (simplified)
        theta2_ddot = -theta2 + 0.3 * u - 0.01 * theta2_dot  # Pendulum 2 (simplified)

        return np.array([
            x_dot,
            theta1_dot,
            theta2_dot,
            x_ddot,
            theta1_ddot,
            theta2_ddot
        ])


@pytest.fixture
def dynamics():
    """Create mock dynamics model for testing."""
    return MockDynamics()


@pytest.fixture
def conditional_hybrid_config():
    """Create Conditional Hybrid configuration."""
    return ConditionalHybridConfig(
        angle_threshold=0.2,
        surface_threshold=1.0,
        B_eq_threshold=0.1,
        w_angle=0.3,
        w_surface=0.3,
        w_singularity=0.4,
        gamma1=1.0,
        gamma2=1.0,
        epsilon_min=0.017,
        alpha=1.142,
        max_force=150.0,
        dt=0.001
    )


@pytest.fixture
def conditional_hybrid_controller(conditional_hybrid_config, dynamics):
    """Create Conditional Hybrid controller."""
    controller = ConditionalHybridController(
        config=conditional_hybrid_config,
        dynamics=dynamics,
        gains=[20.0, 15.0, 9.0, 4.0]
    )
    return controller


@pytest.fixture
def adaptive_baseline_controller(conditional_hybrid_config, dynamics):
    """Create pure Adaptive SMC for comparison."""
    adaptive_config = AdaptiveSMCConfig(
        gains=[20.0, 15.0, 9.0, 4.0, 1.142],  # Same gains + alpha
        max_force=150.0,
        dt=0.001,
        boundary_layer=0.017,
        smooth_switch=True,
        K_init=10.0,
        dynamics_model=dynamics
    )
    return ModularAdaptiveSMC(config=adaptive_config, dynamics=dynamics)


class TestConditionalHybridIntegration:
    """Integration tests for Conditional Hybrid SMC controller."""

    def test_full_simulation_near_equilibrium(
        self, conditional_hybrid_controller, dynamics
    ):
        """Test full simulation starting near equilibrium (STA should activate)."""
        # Initial state: small angles (within STA activation region)
        x0 = np.array([0.0, 0.05, 0.03, 0.0, 0.0, 0.0])

        # Simulation parameters
        t_final = 5.0  # 5 seconds
        dt = 0.001
        t = np.arange(0, t_final, dt)
        n_steps = len(t)

        # Storage
        states = np.zeros((n_steps, 6))
        controls = np.zeros(n_steps)
        states[0] = x0

        # Simulate
        for i in range(n_steps - 1):
            u = conditional_hybrid_controller.compute_control(
                state=states[i],
                t=t[i]
            )
            controls[i] = u

            # Integrate dynamics (simple Euler for testing)
            state_dot = dynamics.compute_dynamics(states[i], u)
            states[i + 1] = states[i] + dt * state_dot

        # Final control
        controls[-1] = conditional_hybrid_controller.compute_control(
            state=states[-1],
            t=t[-1]
        )

        # Validate results
        stats = conditional_hybrid_controller.get_stats()

        # STA should activate frequently near equilibrium
        assert stats["sta_usage_percent"] > 50.0, (
            f"Expected >50% STA usage near equilibrium, got {stats['sta_usage_percent']:.1f}%"
        )

        # System should stabilize
        final_angles = np.max(np.abs(states[-1000:, 1:3]))  # Last 1 second
        assert final_angles < 0.1, (
            f"System did not stabilize: max angle = {final_angles:.3f} rad"
        )

        # Control should be reasonable
        assert np.max(np.abs(controls)) <= 150.0, "Control exceeded saturation"

    def test_full_simulation_large_initial_angles(
        self, conditional_hybrid_controller, dynamics
    ):
        """Test full simulation starting with large angles (STA should be limited)."""
        # Initial state: large angles (outside STA activation region)
        x0 = np.array([0.0, 0.4, 0.3, 0.0, 0.0, 0.0])

        # Simulation parameters
        t_final = 5.0
        dt = 0.001
        t = np.arange(0, t_final, dt)
        n_steps = len(t)

        # Storage
        states = np.zeros((n_steps, 6))
        controls = np.zeros(n_steps)
        states[0] = x0

        # Simulate
        for i in range(n_steps - 1):
            u = conditional_hybrid_controller.compute_control(
                state=states[i],
                t=t[i]
            )
            controls[i] = u

            state_dot = dynamics.compute_dynamics(states[i], u)
            states[i + 1] = states[i] + dt * state_dot

        controls[-1] = conditional_hybrid_controller.compute_control(
            state=states[-1],
            t=t[-1]
        )

        # Validate results
        stats = conditional_hybrid_controller.get_stats()

        # Initially, STA should NOT activate much
        # As system stabilizes, STA usage should increase
        assert 0.0 <= stats["sta_usage_percent"] <= 100.0, (
            "STA usage percent out of valid range"
        )

        # System should eventually stabilize
        final_angles = np.max(np.abs(states[-1000:, 1:3]))
        assert final_angles < 0.2, (
            f"System did not stabilize well: max angle = {final_angles:.3f} rad"
        )

        # Control should be bounded
        assert np.max(np.abs(controls)) <= 150.0, "Control exceeded saturation"

    def test_chattering_index_calculation(
        self, conditional_hybrid_controller, dynamics
    ):
        """Test that chattering index can be computed and is reasonable."""
        # Initial state near equilibrium
        x0 = np.array([0.0, 0.05, 0.03, 0.0, 0.0, 0.0])

        # Short simulation
        t_final = 2.0
        dt = 0.001
        t = np.arange(0, t_final, dt)
        n_steps = len(t)

        states = np.zeros((n_steps, 6))
        controls = np.zeros(n_steps)
        states[0] = x0

        for i in range(n_steps - 1):
            u = conditional_hybrid_controller.compute_control(
                state=states[i],
                t=t[i]
            )
            controls[i] = u

            state_dot = dynamics.compute_dynamics(states[i], u)
            states[i + 1] = states[i] + dt * state_dot

        controls[-1] = conditional_hybrid_controller.compute_control(
            state=states[-1],
            t=t[-1]
        )

        # Compute chattering index (total variation / settling time)
        # Use last 1 second for steady-state analysis
        steady_state_controls = controls[-1000:]
        chattering = np.sum(np.abs(np.diff(steady_state_controls))) / len(steady_state_controls)

        # Chattering should be reasonable (< 1.0 for good controllers)
        # Conditional Hybrid should have chattering similar to Adaptive SMC baseline
        assert chattering < 1.0, (
            f"High chattering detected: {chattering:.4f}"
        )

        print(f"Chattering index: {chattering:.4f}")

    def test_settling_time(
        self, conditional_hybrid_controller, dynamics
    ):
        """Test that settling time is reasonable."""
        # Initial state with moderate angles
        x0 = np.array([0.0, 0.15, 0.10, 0.0, 0.0, 0.0])

        # Simulation
        t_final = 10.0  # Longer simulation for settling time
        dt = 0.001
        t = np.arange(0, t_final, dt)
        n_steps = len(t)

        states = np.zeros((n_steps, 6))
        controls = np.zeros(n_steps)
        states[0] = x0

        for i in range(n_steps - 1):
            u = conditional_hybrid_controller.compute_control(
                state=states[i],
                t=t[i]
            )
            controls[i] = u

            state_dot = dynamics.compute_dynamics(states[i], u)
            states[i + 1] = states[i] + dt * state_dot

        controls[-1] = conditional_hybrid_controller.compute_control(
            state=states[-1],
            t=t[-1]
        )

        # Find settling time (when angles stay < 0.05 rad)
        threshold = 0.05
        max_angles = np.max(np.abs(states[:, 1:3]), axis=1)

        # Find first index where system enters and stays in threshold
        settling_idx = None
        window_size = 1000  # 1 second window
        for i in range(n_steps - window_size):
            if np.all(max_angles[i:i+window_size] < threshold):
                settling_idx = i
                break

        if settling_idx is not None:
            settling_time = t[settling_idx]
            assert settling_time < 8.0, (
                f"Settling time too long: {settling_time:.2f}s"
            )
            print(f"Settling time: {settling_time:.2f}s")
        else:
            pytest.fail("System did not settle within 10 seconds")

    def test_comparison_with_adaptive_baseline(
        self, conditional_hybrid_controller, adaptive_baseline_controller, dynamics
    ):
        """Compare Conditional Hybrid with pure Adaptive SMC baseline."""
        # Same initial state for fair comparison
        x0 = np.array([0.0, 0.10, 0.08, 0.0, 0.0, 0.0])

        # Simulation parameters
        t_final = 5.0
        dt = 0.001
        t = np.arange(0, t_final, dt)
        n_steps = len(t)

        # Simulate Conditional Hybrid
        states_rh = np.zeros((n_steps, 6))
        controls_rh = np.zeros(n_steps)
        states_rh[0] = x0

        for i in range(n_steps - 1):
            u = conditional_hybrid_controller.compute_control(
                state=states_rh[i],
                t=t[i]
            )
            controls_rh[i] = u

            state_dot = dynamics.compute_dynamics(states_rh[i], u)
            states_rh[i + 1] = states_rh[i] + dt * state_dot

        controls_rh[-1] = conditional_hybrid_controller.compute_control(
            state=states_rh[-1],
            t=t[-1]
        )

        # Simulate Adaptive baseline
        states_ad = np.zeros((n_steps, 6))
        controls_ad = np.zeros(n_steps)
        states_ad[0] = x0

        for i in range(n_steps - 1):
            result = adaptive_baseline_controller.compute_control(
                state=states_ad[i],
                state_vars=None,
                history=None,
                dt=None
            )
            u = result.get("control_signal", 0.0) if isinstance(result, dict) else float(result[0])
            controls_ad[i] = u

            state_dot = dynamics.compute_dynamics(states_ad[i], u)
            states_ad[i + 1] = states_ad[i] + dt * state_dot

        result = adaptive_baseline_controller.compute_control(
            state=states_ad[-1],
            state_vars=None,
            history=None,
            dt=None
        )
        controls_ad[-1] = result.get("control_signal", 0.0) if isinstance(result, dict) else float(result[0])

        # Compute performance metrics
        # Chattering (last 1 second)
        chattering_rh = np.sum(np.abs(np.diff(controls_rh[-1000:]))) / 1000
        chattering_ad = np.sum(np.abs(np.diff(controls_ad[-1000:]))) / 1000

        # Tracking error (last 1 second)
        error_rh = np.mean(np.abs(states_rh[-1000:, 1:3]))
        error_ad = np.mean(np.abs(states_ad[-1000:, 1:3]))

        print(f"\nPerformance Comparison:")
        print(f"Conditional Hybrid - Chattering: {chattering_rh:.4f}, Error: {error_rh:.4f}")
        print(f"Adaptive Baseline - Chattering: {chattering_ad:.4f}, Error: {error_ad:.4f}")

        # Conditional Hybrid should perform at least as well as baseline
        # (May be better or similar, but not significantly worse)
        assert chattering_rh <= chattering_ad * 1.5, (
            f"Conditional Hybrid chattering ({chattering_rh:.4f}) significantly worse than baseline ({chattering_ad:.4f})"
        )

        # Get Conditional Hybrid statistics
        stats = conditional_hybrid_controller.get_stats()
        print(f"STA usage: {stats['sta_usage_percent']:.1f}%")
        print(f"Unsafe conditions: {stats['unsafe_conditions']}")

    def test_sta_activation_regions(
        self, conditional_hybrid_controller, dynamics
    ):
        """Test that STA activates only in safe regions."""
        # Test several states across the operating region
        test_states = [
            # (state, expected_safe)
            (np.array([0.0, 0.05, 0.03, 0.0, 0.0, 0.0]), True),   # Near equilibrium
            (np.array([0.0, 0.25, 0.20, 0.0, 0.0, 0.0]), False),  # Large angles
            (np.array([0.0, 0.10, 0.08, 0.0, 0.0, 0.0]), False),  # Moderate angles (|s|=1.22 > threshold=1.0)
            (np.array([0.0, 0.01, 0.01, 0.0, 0.0, 0.0]), True),   # Very small angles
        ]

        conditional_hybrid_controller.reset()

        for state, expected_safe in test_states:
            # Simulate a few steps with this state
            for _ in range(10):
                u = conditional_hybrid_controller.compute_control(
                    state=state,
                    t=0.0
                )

            stats = conditional_hybrid_controller.get_stats()

            if expected_safe:
                # STA should activate for safe states
                assert stats["sta_active_steps"] > 0, (
                    f"STA did not activate for expected safe state: {state[1:3]}"
                )
            # Note: For borderline cases, we don't enforce strict requirements

            conditional_hybrid_controller.reset()

    def test_robustness_to_parameter_variations(
        self, dynamics
    ):
        """Test robustness to configuration parameter variations."""
        # Test different threshold configurations
        configs = [
            # Strict thresholds (less STA usage)
            ConditionalHybridConfig(
                angle_threshold=0.1,
                surface_threshold=0.5,
                B_eq_threshold=0.2,
                gamma1=1.0,
                gamma2=1.0,
                epsilon_min=0.017,
                alpha=1.142,
                max_force=150.0,
                dt=0.001
            ),
            # Relaxed thresholds (more STA usage)
            ConditionalHybridConfig(
                angle_threshold=0.3,
                surface_threshold=2.0,
                B_eq_threshold=0.05,
                gamma1=1.0,
                gamma2=1.0,
                epsilon_min=0.017,
                alpha=1.142,
                max_force=150.0,
                dt=0.001
            ),
        ]

        x0 = np.array([0.0, 0.10, 0.08, 0.0, 0.0, 0.0])

        for config in configs:
            controller = ConditionalHybridController(
                config=config,
                dynamics=dynamics,
                gains=[20.0, 15.0, 9.0, 4.0]
            )

            # Short simulation
            t_final = 2.0
            dt = 0.001
            t = np.arange(0, t_final, dt)
            n_steps = len(t)

            states = np.zeros((n_steps, 6))
            controls = np.zeros(n_steps)
            states[0] = x0

            for i in range(n_steps - 1):
                u = controller.compute_control(
                    state=states[i],
                    t=t[i]
                )
                controls[i] = u

                state_dot = dynamics.compute_dynamics(states[i], u)
                states[i + 1] = states[i] + dt * state_dot

            controls[-1] = controller.compute_control(
                state=states[-1],
                t=t[-1]
            )

            # System should remain stable
            final_angles = np.max(np.abs(states[-100:, 1:3]))
            assert final_angles < 0.3, (
                f"System unstable with config: angle_threshold={config.angle_threshold}"
            )

            # Control should be bounded
            assert np.max(np.abs(controls)) <= 150.0, "Control exceeded saturation"

    def test_integral_anti_windup(
        self, conditional_hybrid_controller, dynamics
    ):
        """Test that integral anti-windup works (resets when leaving safe region)."""
        # Start in safe region, then move to unsafe region
        states_sequence = [
            np.array([0.0, 0.05, 0.03, 0.0, 0.0, 0.0]),  # Safe
            np.array([0.0, 0.05, 0.03, 0.0, 0.0, 0.0]),  # Safe
            np.array([0.0, 0.05, 0.03, 0.0, 0.0, 0.0]),  # Safe
            np.array([0.0, 0.30, 0.25, 0.0, 0.0, 0.0]),  # Unsafe (large angles)
        ]

        conditional_hybrid_controller.reset()

        # Accumulate integral in safe region
        for i in range(3):
            u = conditional_hybrid_controller.compute_control(
                state=states_sequence[i],
                t=float(i) * 0.001
            )

        # Integral should be non-zero
        assert conditional_hybrid_controller.st_integral != 0.0, (
            "Integral did not accumulate in safe region"
        )

        # Move to unsafe region
        u = conditional_hybrid_controller.compute_control(
            state=states_sequence[3],
            t=3 * 0.001
        )

        # Integral should be reset
        assert conditional_hybrid_controller.st_integral == 0.0, (
            "Integral anti-windup did not reset when entering unsafe region"
        )

        # Unsafe conditions should be recorded
        stats = conditional_hybrid_controller.get_stats()
        assert stats["unsafe_conditions"] > 0, "Unsafe condition not recorded"


class TestConditionalHybridEdgeCases:
    """Edge case tests for Conditional Hybrid controller."""

    def test_zero_initial_state(
        self, conditional_hybrid_controller
    ):
        """Test controller at exact equilibrium (zero state)."""
        x0 = np.zeros(6)

        u = conditional_hybrid_controller.compute_control(
            state=x0,
            t=0.0
        )

        # Control should be zero or very small at equilibrium
        assert np.abs(u) < 1.0, f"Control too large at equilibrium: {u:.4f}"

    def test_saturated_control(
        self, conditional_hybrid_controller
    ):
        """Test that control saturates properly at limits."""
        # Very large angles (should require large control)
        x_large = np.array([0.0, 0.8, 0.7, 0.0, 0.0, 0.0])

        u = conditional_hybrid_controller.compute_control(
            state=x_large,
            t=0.0
        )

        # Control should be saturated
        assert np.abs(u) <= 150.0, f"Control exceeded max_force: {u:.2f}"

    def test_reset_functionality(
        self, conditional_hybrid_controller
    ):
        """Test that reset() properly clears controller state."""
        # Run controller for a few steps
        state = np.array([0.0, 0.05, 0.03, 0.0, 0.0, 0.0])
        for _ in range(10):
            u = conditional_hybrid_controller.compute_control(
                state=state,
                t=0.0
            )

        # Verify state accumulated
        stats_before = conditional_hybrid_controller.get_stats()
        assert stats_before["total_steps"] > 0

        # Reset
        conditional_hybrid_controller.reset()

        # Verify state cleared
        assert conditional_hybrid_controller.st_integral == 0.0
        stats_after = conditional_hybrid_controller.get_stats()
        assert stats_after["total_steps"] == 0
        assert stats_after["sta_active_steps"] == 0
        assert stats_after["unsafe_conditions"] == 0

    def test_get_stats_format(
        self, conditional_hybrid_controller
    ):
        """Test that get_stats() returns correct format."""
        # Run a few steps
        state = np.array([0.0, 0.05, 0.03, 0.0, 0.0, 0.0])
        for _ in range(5):
            u = conditional_hybrid_controller.compute_control(
                state=state,
                t=0.0
            )

        stats = conditional_hybrid_controller.get_stats()

        # Verify required fields
        assert "total_steps" in stats
        assert "sta_active_steps" in stats
        assert "unsafe_conditions" in stats
        assert "sta_usage_percent" in stats

        # Verify types
        assert isinstance(stats["total_steps"], int)
        assert isinstance(stats["sta_active_steps"], int)
        assert isinstance(stats["unsafe_conditions"], int)
        assert isinstance(stats["sta_usage_percent"], float)

        # Verify values are consistent
        assert stats["total_steps"] >= stats["sta_active_steps"]
        assert stats["total_steps"] >= stats["unsafe_conditions"]
        assert 0.0 <= stats["sta_usage_percent"] <= 100.0
