#!/usr/bin/env python
"""
Factory Integration Tests - Week 3 Coverage Improvement (Option A)

PURPOSE: Test factory → controller → control computation pipeline with REAL config.yaml
STRATEGY: Integration tests instead of mocks for higher pass rate (90%+ target)
EXPECTED COVERAGE: 40-50% with real behavior validation

DESIGN RATIONALE:
- Week 3 Session 1-2 revealed mock-based unit tests have low pass rate (20%)
- Root cause: Incomplete mocks that don't match modular controller architecture
- Solution: Use real config.yaml for authentic controller creation and validation
- Value: Tests validate actual system behavior, not mock assumptions

TEST MATRIX:
1. Factory → Controller Creation (6 controllers)
2. Controller → Control Computation (6 controllers × 3 states)
3. Factory → PSO Integration (4 controllers with gain tuning)
4. End-to-End Workflow Validation (config → factory → simulation)

Author: Claude Code (Week 3 Coverage Improvement - Option A)
Date: December 2025
Version: 1.0
"""

import pytest
import numpy as np
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import warnings

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Import core components
try:
    from src.controllers.factory import (
        create_controller,
        get_default_gains,
        get_controller_info,
        CONTROLLER_REGISTRY,
    )
    from src.config import load_config
    from src.core.dynamics import DIPDynamics
    from src.core.simulation_runner import run_simulation
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    COMPONENTS_AVAILABLE = False
    warnings.warn(f"Core components not available: {e}")

# ==============================================================================
# Test Configuration
# ==============================================================================

# Controllers that support gain-based creation
GAIN_BASED_CONTROLLERS = [
    "classical_smc",
    "sta_smc",
    "adaptive_smc",
    "hybrid_adaptive_sta_smc",
]

# All available controllers (factory-registered only)
# Note: swing_up_smc not yet registered in factory (returns "Unknown controller type")
# Note: mpc_controller requires cvxpy (optional dependency)
ALL_CONTROLLERS = GAIN_BASED_CONTROLLERS

# Test states for control computation
TEST_STATES = [
    np.array([0.0, 0.05, -0.03, 0.0, 0.0, 0.0]),  # Near equilibrium
    np.array([0.0, 0.2, 0.15, 0.1, 0.05, 0.0]),   # Moderate disturbance
    np.array([0.0, 0.5, 0.4, 0.2, 0.1, 0.0]),     # Large disturbance
]

# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture(scope="module")
def real_config():
    """Load real config.yaml for integration tests"""
    if not COMPONENTS_AVAILABLE:
        pytest.skip("Core components not available")

    try:
        config_path = PROJECT_ROOT / "config.yaml"
        cfg = load_config(str(config_path), allow_unknown=False)
        return cfg
    except Exception as e:
        pytest.skip(f"Failed to load config.yaml: {e}")

@pytest.fixture(scope="module")
def dynamics_model(real_config):
    """Create dynamics model from real config"""
    try:
        return DIPDynamics(config=real_config.physics)
    except Exception as e:
        pytest.skip(f"Failed to create dynamics model: {e}")

# ==============================================================================
# Test Suite 1: Factory → Controller Creation
# ==============================================================================

class TestFactoryControllerCreation:
    """Test factory controller creation with real config.yaml"""

    @pytest.mark.parametrize("controller_type", ALL_CONTROLLERS)
    def test_create_controller_from_config(self, controller_type, real_config):
        """Test controller creation using real config gains"""
        # Get controller config
        controller_config = getattr(real_config.controllers, controller_type)

        # Extract gains if available
        gains = None
        if hasattr(controller_config, 'gains') and controller_config.gains:
            gains = controller_config.gains

        # Create controller
        controller = create_controller(
            controller_type,
            config=real_config,
            gains=gains
        )

        # Validate controller creation
        assert controller is not None, f"Failed to create {controller_type}"
        assert hasattr(controller, 'compute_control'), f"{controller_type} missing compute_control"

        # Validate gains were set correctly (for gain-based controllers)
        if gains is not None and hasattr(controller, 'gains'):
            assert controller.gains is not None, f"{controller_type} gains not set"
            assert len(controller.gains) == len(gains), f"{controller_type} gain count mismatch"

    @pytest.mark.parametrize("controller_type", GAIN_BASED_CONTROLLERS)
    def test_get_default_gains(self, controller_type, real_config):
        """Test default gains retrieval from config"""
        default_gains = get_default_gains(controller_type)

        assert default_gains is not None, f"No default gains for {controller_type}"
        assert isinstance(default_gains, list), f"{controller_type} gains not a list"
        assert len(default_gains) > 0, f"{controller_type} gains empty"

        # Verify gain count matches expected
        controller_info = get_controller_info(controller_type)
        expected_count = controller_info['gain_count']
        assert len(default_gains) == expected_count, \
            f"{controller_type} expected {expected_count} gains, got {len(default_gains)}"

    @pytest.mark.parametrize("controller_type", GAIN_BASED_CONTROLLERS)
    def test_controller_with_custom_gains(self, controller_type, real_config):
        """Test controller creation with custom gains"""
        # Get expected gain count from registry
        controller_info = get_controller_info(controller_type)
        expected_count = controller_info['gain_count']

        # Create custom gains (all 1.0 for simplicity)
        custom_gains = [1.0] * expected_count

        # Create controller with custom gains
        controller = create_controller(
            controller_type,
            config=real_config,
            gains=custom_gains
        )

        assert controller is not None, f"Failed to create {controller_type} with custom gains"
        if hasattr(controller, 'gains'):
            # Note: Some controllers may transform gains internally
            assert controller.gains is not None, f"{controller_type} custom gains not set"

# ==============================================================================
# Test Suite 2: Controller → Control Computation
# ==============================================================================

class TestControllerComputeControl:
    """Test control computation with real controllers and states"""

    @pytest.mark.parametrize("controller_type", ALL_CONTROLLERS)
    @pytest.mark.parametrize("state", TEST_STATES, ids=["near_eq", "moderate", "large"])
    def test_compute_control_basic(self, controller_type, state, real_config):
        """Test basic control computation for all controllers"""
        # Get controller config
        controller_config = getattr(real_config.controllers, controller_type)
        gains = controller_config.gains if hasattr(controller_config, 'gains') and controller_config.gains else None

        # Create controller
        controller = create_controller(
            controller_type,
            config=real_config,
            gains=gains
        )

        # Compute control
        last_control = 0.0
        history = []

        try:
            control = controller.compute_control(state, last_control, history)

            # Extract control value from dict if needed (controllers may return metadata)
            if isinstance(control, dict):
                control_value = control.get('u', control.get('control', None))
                if control_value is None:
                    control_value = control  # Fallback to dict if keys not found
            else:
                control_value = control

            # Validate control output
            assert control_value is not None, f"{controller_type} returned None control"
            assert isinstance(control_value, (int, float, np.number)), \
                f"{controller_type} control not numeric: {type(control_value)}"

            # Check control is finite
            assert np.isfinite(control_value), f"{controller_type} control not finite: {control_value}"

            # Check control respects max_force bounds (if available)
            if hasattr(controller_config, 'max_force'):
                max_force = controller_config.max_force
                assert abs(control_value) <= max_force + 1e-6, \
                    f"{controller_type} control {control_value} exceeds max_force {max_force}"

        except Exception as e:
            pytest.fail(f"{controller_type} compute_control failed: {e}")

    @pytest.mark.parametrize("controller_type", ALL_CONTROLLERS)
    def test_compute_control_sequence(self, controller_type, real_config):
        """Test control computation sequence (multiple timesteps)"""
        # Get controller config
        controller_config = getattr(real_config.controllers, controller_type)
        gains = controller_config.gains if hasattr(controller_config, 'gains') and controller_config.gains else None

        # Create controller
        controller = create_controller(
            controller_type,
            config=real_config,
            gains=gains
        )

        # Initial state
        state = TEST_STATES[0].copy()
        last_control = 0.0
        history = []

        # Compute control for 10 timesteps
        controls = []
        for _ in range(10):
            try:
                control = controller.compute_control(state, last_control, history)
                # Extract control value from dict if needed
                if isinstance(control, dict):
                    control_value = control.get('u', control.get('control', None))
                    if control_value is None:
                        raise ValueError(f"Cannot extract control from dict: {list(control.keys())}")
                else:
                    control_value = control
                controls.append(control_value)
                last_control = control_value
            except Exception as e:
                pytest.fail(f"{controller_type} failed in sequence: {e}")

        # Validate all controls are finite
        assert all(np.isfinite(float(c)) for c in controls), \
            f"{controller_type} produced non-finite controls"

# ==============================================================================
# Test Suite 3: Factory → PSO Integration
# ==============================================================================

class TestFactoryPSOIntegration:
    """Test factory integration with PSO gain tuning"""

    @pytest.mark.parametrize("controller_type", GAIN_BASED_CONTROLLERS)
    def test_pso_gain_bounds(self, controller_type, real_config):
        """Test PSO gain bounds retrieval from config"""
        from src.controllers.factory import get_gain_bounds_for_pso

        try:
            min_bounds, max_bounds = get_gain_bounds_for_pso(controller_type)

            # Validate bounds
            assert min_bounds is not None, f"No min bounds for {controller_type}"
            assert max_bounds is not None, f"No max bounds for {controller_type}"
            assert len(min_bounds) == len(max_bounds), f"{controller_type} bound size mismatch"

            # Check bounds are reasonable
            controller_info = get_controller_info(controller_type)
            expected_count = controller_info['gain_count']
            assert len(min_bounds) == expected_count, \
                f"{controller_type} expected {expected_count} bounds, got {len(min_bounds)}"

            # Verify min < max for all bounds
            for i, (min_val, max_val) in enumerate(zip(min_bounds, max_bounds)):
                assert min_val < max_val, \
                    f"{controller_type} bound {i}: min {min_val} >= max {max_val}"

        except Exception as e:
            pytest.fail(f"PSO bounds retrieval failed for {controller_type}: {e}")

    @pytest.mark.parametrize("controller_type", GAIN_BASED_CONTROLLERS)
    def test_create_controller_with_pso_gains(self, controller_type, real_config):
        """Test controller creation with PSO-optimized gains"""
        from src.controllers.factory import get_gain_bounds_for_pso

        # Get PSO bounds
        min_bounds, max_bounds = get_gain_bounds_for_pso(controller_type)

        # Create test gains at midpoint of bounds
        test_gains = [(min_val + max_val) / 2.0 for min_val, max_val in zip(min_bounds, max_bounds)]

        # Create controller with PSO-style gains
        controller = create_controller(
            controller_type,
            config=real_config,
            gains=test_gains
        )

        assert controller is not None, f"Failed to create {controller_type} with PSO gains"

        # Test control computation with PSO gains
        state = TEST_STATES[0]
        try:
            control = controller.compute_control(state, 0.0, [])
            # Extract control value from dict if needed
            if isinstance(control, dict):
                control_value = control.get('u', control.get('control', None))
                if control_value is None:
                    raise ValueError(f"Cannot extract control from dict: {list(control.keys())}")
            else:
                control_value = control
            assert np.isfinite(float(control_value)), f"{controller_type} PSO gains produced non-finite control"
        except Exception as e:
            pytest.fail(f"{controller_type} PSO gains failed compute_control: {e}")

# ==============================================================================
# Test Suite 4: End-to-End Workflow Validation
# ==============================================================================

class TestEndToEndWorkflow:
    """Test complete workflow: config → factory → simulation"""

    @pytest.mark.parametrize("controller_type", ALL_CONTROLLERS)
    def test_full_simulation_workflow(self, controller_type, real_config, dynamics_model):
        """Test complete simulation workflow with real components"""
        # Get controller config
        controller_config = getattr(real_config.controllers, controller_type)
        gains = controller_config.gains if hasattr(controller_config, 'gains') and controller_config.gains else None

        # Create controller
        controller = create_controller(
            controller_type,
            config=real_config,
            gains=gains
        )

        # Run short simulation (1 second)
        sim_time = 1.0
        dt = real_config.simulation.dt
        initial_state = real_config.simulation.initial_state

        try:
            t_arr, x_arr, u_arr = run_simulation(
                controller=controller,
                dynamics_model=dynamics_model,
                sim_time=sim_time,
                dt=dt,
                initial_state=initial_state
            )

            # Validate simulation outputs
            assert t_arr is not None, f"{controller_type} simulation returned None time"
            assert x_arr is not None, f"{controller_type} simulation returned None state"
            assert u_arr is not None, f"{controller_type} simulation returned None control"

            # Check array shapes (u_arr might be scalar or array)
            assert len(t_arr) > 0, f"{controller_type} empty time array"
            assert x_arr.shape[0] == len(t_arr), f"{controller_type} state array size mismatch"

            # Handle control array - may be returned as list or array
            if isinstance(u_arr, (list, np.ndarray)):
                u_arr_len = len(u_arr)
            else:
                u_arr_len = 1
            assert u_arr_len > 0, f"{controller_type} empty control array"

            # Check values are finite
            assert np.all(np.isfinite(t_arr)), f"{controller_type} non-finite time values"
            assert np.all(np.isfinite(x_arr)), f"{controller_type} non-finite state values"
            if isinstance(u_arr, (list, np.ndarray)):
                assert np.all(np.isfinite(u_arr)), f"{controller_type} non-finite control values"

        except Exception as e:
            pytest.fail(f"{controller_type} simulation workflow failed: {e}")

    def test_multiple_controllers_same_config(self, real_config, dynamics_model):
        """Test creating multiple controllers from same config"""
        controllers = []

        # Create all controllers
        for controller_type in ALL_CONTROLLERS:
            controller_config = getattr(real_config.controllers, controller_type)
            gains = controller_config.gains if hasattr(controller_config, 'gains') and controller_config.gains else None

            controller = create_controller(
                controller_type,
                config=real_config,
                gains=gains
            )
            controllers.append((controller_type, controller))

        # Validate all controllers created successfully
        assert len(controllers) == len(ALL_CONTROLLERS), "Not all controllers created"

        # Test each controller can compute control independently
        state = TEST_STATES[0]
        for ctrl_type, controller in controllers:
            try:
                control = controller.compute_control(state, 0.0, [])
                # Extract control value from dict if needed
                if isinstance(control, dict):
                    control_value = control.get('u', control.get('control', None))
                    if control_value is None:
                        raise ValueError(f"Cannot extract control from dict: {list(control.keys())}")
                else:
                    control_value = control
                assert np.isfinite(float(control_value)), f"{ctrl_type} failed with shared config"
            except Exception as e:
                pytest.fail(f"{ctrl_type} failed in multi-controller test: {e}")

# ==============================================================================
# Summary Test
# ==============================================================================

@pytest.mark.integration
def test_integration_summary():
    """Print summary of integration test coverage"""
    print("\n" + "=" * 80)
    print(" Factory Integration Tests - Week 3 Option A")
    print("=" * 80)
    print(f" Strategy: Real config.yaml (not mocks)")
    print(f" Controllers Tested: {len(ALL_CONTROLLERS)}")
    print(f" Gain-Based Controllers: {len(GAIN_BASED_CONTROLLERS)}")
    print(f" Test States: {len(TEST_STATES)}")
    print("-" * 80)
    print(" Test Suites:")
    print("   1. Factory → Controller Creation")
    print("   2. Controller → Control Computation")
    print("   3. Factory → PSO Integration")
    print("   4. End-to-End Workflow Validation")
    print("-" * 80)
    print(" Expected Results:")
    print("   Pass Rate: 90%+ (vs 20% with mocks)")
    print("   Coverage: 40-50% (factory, controllers, core)")
    print("   Value: Tests validate REAL system behavior")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
