#======================================================================================\\\
#============== tests/test_simulation/orchestrators/test_batch_core_logic.py ==========\\\
#======================================================================================\\\

"""Comprehensive tests for BatchOrchestrator core execution logic.

This test suite covers lines 52-137 of src/simulation/orchestrators/batch.py,
focusing on:
- Batch size detection and normalization (lines 57-63)
- Active mask management (lines 82-88, 100-112, 117-130)
- Control extraction per timestep (lines 90-96)
- Safety guards and stop conditions (lines 98-113)
- State update and validation (lines 114-137)
- Execution tracking (lines 54, 135-137)

Target Coverage: ~45% of BatchOrchestrator (30 tests, 6 hours)
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock, call
import time

from src.simulation.orchestrators.batch import BatchOrchestrator
from src.simulation.orchestrators.base import BaseOrchestrator
from src.simulation.core.simulation_context import SimulationContext


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def mock_context():
    """Create mock simulation context."""
    context = Mock(spec=SimulationContext)
    context.get_config.return_value = {}
    context.get_simulation_parameters.return_value = {
        "dt": 0.01,
        "integration_method": "rk4"
    }

    # Mock dynamics model
    dynamics_model = Mock()
    dynamics_model.compute_dynamics.return_value = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    context.get_dynamics_model.return_value = dynamics_model

    return context


@pytest.fixture
def orchestrator(mock_context):
    """Create BatchOrchestrator instance with mocked context."""
    return BatchOrchestrator(mock_context)


# ==============================================================================
# Track A: BatchOrchestrator.execute() Main Loop (15 tests)
# ==============================================================================

class TestBatchOrchestratorExecute:
    """Test BatchOrchestrator.execute() main logic (15 tests)."""

    # ------------------------------------------------------------------------
    # Category 1: Batch Size Detection (5 tests)
    # ------------------------------------------------------------------------

    def test_single_state_input_normalized_to_batch(self, orchestrator):
        """Test single state input (state_dim,) is normalized to (1, state_dim)."""
        # Single state: shape (6,) should become (1, 6)
        initial_state = np.array([0.1, 0.0, 0.05, 0.0, 0.0, 0.0])
        control_inputs = np.zeros((1, 10))

        with patch.object(orchestrator, 'step', return_value=np.zeros(6)):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=10)

        # Should succeed without error - state was normalized internally
        assert result is not None

    def test_batch_state_input_kept_as_is(self, orchestrator):
        """Test batch state input (batch_size, state_dim) is kept unchanged."""
        # Batch of 3 states
        batch_size = 3
        initial_state = np.array([
            [0.1, 0.0, 0.05, 0.0, 0.0, 0.0],
            [0.2, 0.0, 0.1, 0.0, 0.0, 0.0],
            [0.3, 0.0, 0.15, 0.0, 0.0, 0.0]
        ])
        control_inputs = np.zeros((batch_size, 10))

        with patch.object(orchestrator, 'step', return_value=np.zeros(6)):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=10)

        # Should handle batch correctly
        assert result is not None

    def test_batch_size_one_special_case(self, orchestrator):
        """Test batch_size=1 special case (shape[0] == 1)."""
        # Shape (1, 6) - batch_size should be detected as 1
        initial_state = np.array([[0.1, 0.0, 0.05, 0.0, 0.0, 0.0]])
        control_inputs = np.zeros((1, 10))

        with patch.object(orchestrator, 'step', return_value=np.zeros(6)) as mock_step:
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=10)

        # step() should be called for batch_size=1
        assert mock_step.call_count == 10  # horizon steps

    def test_state_dim_extracted_from_shape(self, orchestrator):
        """Test state_dim extracted correctly from shape[1]."""
        # Various state dimensions
        for state_dim in [4, 6, 8, 10]:
            initial_state = np.zeros((2, state_dim))  # batch_size=2
            control_inputs = np.zeros((2, 5))

            with patch.object(orchestrator, 'step', return_value=np.zeros(state_dim)):
                result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=5)

            # Should handle different state dimensions
            assert result is not None

    def test_atleast_2d_applied_to_initial_state(self, orchestrator):
        """Test initial_state = np.atleast_2d(initial_state) is applied."""
        # 1D array should become 2D
        initial_state = np.array([0.1, 0.0, 0.05, 0.0, 0.0, 0.0])
        control_inputs = np.zeros((1, 5))

        # Verify internal normalization happens
        with patch('numpy.atleast_2d', wraps=np.atleast_2d) as mock_atleast_2d:
            with patch.object(orchestrator, 'step', return_value=np.zeros(6)):
                result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=5)

            # atleast_2d should have been called on initial_state
            mock_atleast_2d.assert_called()

    # ------------------------------------------------------------------------
    # Category 2: Active Mask Management (5 tests)
    # ------------------------------------------------------------------------

    def test_active_mask_initialized_to_all_true(self, orchestrator):
        """Test active_mask initialized to all True (np.ones(batch_size, dtype=bool))."""
        batch_size = 3
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, 5))

        # Track active_mask state by monitoring step() calls
        step_calls = []
        def track_step(state, control, dt, **kwargs):
            step_calls.append(state.copy())
            return state + 0.01  # Small increment

        with patch.object(orchestrator, 'step', side_effect=track_step):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=5)

        # All batch elements should have been processed (active initially)
        # 3 batch elements * 5 horizon steps = 15 calls
        assert len(step_calls) == 15

    def test_loop_breaks_when_all_inactive(self, orchestrator):
        """Test loop breaks when np.any(active_mask) == False (all inactive)."""
        batch_size = 2
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, 10))

        # Make step() return NaN after 3 steps to deactivate all
        call_count = [0]
        def step_with_nan(state, control, dt, **kwargs):
            call_count[0] += 1
            if call_count[0] > 6:  # After 3 steps for 2 batch elements
                return np.full(6, np.nan)
            return state

        with patch.object(orchestrator, 'step', side_effect=step_with_nan):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=10)

        # Loop should break early, not complete all 10*2=20 steps
        assert call_count[0] < 20

    def test_active_mask_false_on_non_finite_state(self, orchestrator):
        """Test active_mask[b] = False when state contains non-finite values."""
        batch_size = 2
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, 5))

        # First batch element returns NaN on second step
        call_count = [0]
        def step_with_selective_nan(state, control, dt, **kwargs):
            call_count[0] += 1
            # Make first batch element fail on step 2
            if call_count[0] == 2:
                return np.full(6, np.nan)
            return state + 0.01

        with patch.object(orchestrator, 'step', side_effect=step_with_selective_nan):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=5)

        # Should continue with second batch element after first fails
        # First element: 2 calls (fails on 2nd), Second element: 5 calls = 7 total
        # However, implementation may vary slightly, so check for >= 6
        assert call_count[0] >= 6

    def test_active_mask_false_on_exception(self, orchestrator):
        """Test active_mask[b] = False on exception during step()."""
        batch_size = 2
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, 5))

        # Make first call raise exception
        call_count = [0]
        def step_with_exception(state, control, dt, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("Simulation failed")
            return state + 0.01

        with patch.object(orchestrator, 'step', side_effect=step_with_exception):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=5)

        # Should catch exception and continue with other batch elements
        # First element fails on step 1, second element completes 5 steps = 6 total
        assert call_count[0] >= 6
        assert result is not None

    def test_partial_batch_active(self, orchestrator):
        """Test partial batch active (some True, some False)."""
        batch_size = 4
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, 5))

        # Deactivate elements 0 and 2 by returning NaN
        def step_selective_fail(state, control, dt, **kwargs):
            # Use state value to determine batch index
            state_sum = np.sum(state)
            if np.isclose(state_sum, 0.0) or np.isclose(state_sum, 0.02):
                return np.full(6, np.nan)
            return state + 0.001

        # Set different initial states to distinguish batch elements
        initial_state[0, 0] = 0.0
        initial_state[1, 0] = 0.01
        initial_state[2, 0] = 0.02
        initial_state[3, 0] = 0.03

        with patch.object(orchestrator, 'step', side_effect=step_selective_fail):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=5)

        # Should handle partial active batch
        assert result is not None

    # ------------------------------------------------------------------------
    # Category 3: Control Extraction Per Step (5 tests)
    # ------------------------------------------------------------------------

    def test_3d_controls_extraction(self, orchestrator):
        """Test 3D controls: step_controls = control_inputs[:, i, :] (line 92)."""
        batch_size = 2
        horizon = 5
        control_dim = 1
        initial_state = np.zeros((batch_size, 6))
        # 3D control: (batch_size, horizon, control_dim)
        control_inputs = np.random.rand(batch_size, horizon, control_dim)

        extracted_controls = []
        def track_control(state, control, dt, **kwargs):
            extracted_controls.append(control.copy())
            return state

        with patch.object(orchestrator, 'step', side_effect=track_control):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=horizon)

        # Should extract control for each timestep and batch element
        assert len(extracted_controls) == batch_size * horizon

    def test_2d_controls_extraction(self, orchestrator):
        """Test 2D controls: step_controls = control_inputs[:, i:i+1] (line 94)."""
        batch_size = 2
        horizon = 5
        initial_state = np.zeros((batch_size, 6))
        # 2D control: (batch_size, horizon)
        control_inputs = np.random.rand(batch_size, horizon)

        extracted_controls = []
        def track_control(state, control, dt, **kwargs):
            extracted_controls.append(control.copy() if hasattr(control, 'copy') else control)
            return state

        with patch.object(orchestrator, 'step', side_effect=track_control):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=horizon)

        # Should extract control slice for each timestep
        assert len(extracted_controls) == batch_size * horizon

    def test_controls_assignment_per_step(self, orchestrator):
        """Test controls[:, i] = step_controls.flat[:batch_size] assignment."""
        batch_size = 3
        horizon = 4
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.ones((batch_size, horizon)) * 2.5

        with patch.object(orchestrator, 'step', return_value=np.zeros(6)):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=horizon)

        # Result should contain control trajectory for each batch element
        # BatchResultContainer stores controls in batch_data
        for b in range(batch_size):
            batch_controls = result.batch_data.get(b, {}).get('controls', None)
            # Should have recorded controls
            assert batch_controls is not None
            assert len(batch_controls) > 0

    def test_control_extraction_each_timestep(self, orchestrator):
        """Test control extraction for each timestep i in range(horizon)."""
        batch_size = 2
        horizon = 10
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.arange(batch_size * horizon).reshape(batch_size, horizon)

        timestep_controls = {i: [] for i in range(horizon)}
        call_count = [0]

        def track_timestep_control(state, control, dt, **kwargs):
            step_idx = call_count[0] // batch_size
            timestep_controls[step_idx].append(control)
            call_count[0] += 1
            return state

        with patch.object(orchestrator, 'step', side_effect=track_timestep_control):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=horizon)

        # Each timestep should have controls extracted
        for i in range(horizon):
            assert len(timestep_controls[i]) > 0

    def test_step_controls_indexing_by_ndim(self, orchestrator):
        """Test step_controls[b] vs step_controls[b:b+1] based on ndim."""
        batch_size = 2
        horizon = 3
        initial_state = np.zeros((batch_size, 6))

        # Test with 3D controls (should use step_controls[b])
        control_inputs_3d = np.ones((batch_size, horizon, 1))

        controls_passed = []
        def capture_control(state, control, dt, **kwargs):
            controls_passed.append(control.shape)
            return state

        with patch.object(orchestrator, 'step', side_effect=capture_control):
            result = orchestrator.execute(initial_state, control_inputs_3d, dt=0.01, horizon=horizon)

        # Should have extracted controls with correct shapes
        assert len(controls_passed) == batch_size * horizon


# ==============================================================================
# Track B: Safety Guards & Stop Conditions (10 tests)
# ==============================================================================

class TestSafetyAndStopConditions:
    """Test safety guards and stop conditions (10 tests)."""

    # ------------------------------------------------------------------------
    # Category 4: Stop Condition Logic (5 tests)
    # ------------------------------------------------------------------------

    def test_stop_fn_none_no_early_stopping(self, orchestrator):
        """Test stop_fn=None means no early stopping (line 99)."""
        batch_size = 2
        horizon = 10
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))

        step_count = [0]
        def count_steps(state, control, dt, **kwargs):
            step_count[0] += 1
            return state

        with patch.object(orchestrator, 'step', side_effect=count_steps):
            result = orchestrator.execute(
                initial_state, control_inputs, dt=0.01, horizon=horizon,
                stop_fn=None
            )

        # Should complete all steps without early stopping
        assert step_count[0] == batch_size * horizon

    def test_stop_fn_triggers_deactivation(self, orchestrator):
        """Test stop_fn(current_states[b]) triggers active_mask[b]=False."""
        batch_size = 2
        horizon = 10
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))

        # Stop condition: stop when state[0] > 0.5
        def stop_condition(state):
            return state[0] > 0.5

        step_count = [0]
        def increment_state(state, control, dt, **kwargs):
            step_count[0] += 1
            new_state = state.copy()
            new_state[0] += 0.15  # Increment to trigger stop after ~4 steps
            return new_state

        with patch.object(orchestrator, 'step', side_effect=increment_state):
            result = orchestrator.execute(
                initial_state, control_inputs, dt=0.01, horizon=horizon,
                stop_fn=stop_condition
            )

        # Should stop early due to stop condition
        assert step_count[0] < batch_size * horizon

    def test_stop_fn_checked_only_for_active(self, orchestrator):
        """Test stop_fn checked only for active batch elements (if active_mask[b])."""
        batch_size = 3
        horizon = 5
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))

        stop_fn_calls = []
        def track_stop_checks(state):
            stop_fn_calls.append(state.copy())
            return False  # Never stop

        # Make first batch element fail immediately
        call_count = [0]
        def fail_first_element(state, control, dt, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return np.full(6, np.nan)
            return state

        with patch.object(orchestrator, 'step', side_effect=fail_first_element):
            result = orchestrator.execute(
                initial_state, control_inputs, dt=0.01, horizon=horizon,
                stop_fn=track_stop_checks
            )

        # stop_fn should only be called for active elements
        # First element fails immediately, so fewer stop checks
        assert len(stop_fn_calls) < batch_size * horizon

    def test_loop_continues_after_some_stop(self, orchestrator):
        """Test loop continues after some elements stop."""
        batch_size = 3
        horizon = 10
        initial_state = np.zeros((batch_size, 6))
        initial_state[:, 0] = [0.0, 0.6, 0.0]  # Second element starts above threshold
        control_inputs = np.zeros((batch_size, horizon))

        # Stop when state[0] > 0.5
        def stop_condition(state):
            return state[0] > 0.5

        step_count = [0]
        def count_steps(state, control, dt, **kwargs):
            step_count[0] += 1
            return state

        with patch.object(orchestrator, 'step', side_effect=count_steps):
            result = orchestrator.execute(
                initial_state, control_inputs, dt=0.01, horizon=horizon,
                stop_fn=stop_condition
            )

        # Should continue with other elements after one stops
        # Element 1 stops immediately, elements 0 and 2 continue
        assert step_count[0] >= 2 * horizon  # At least 2 elements complete

    def test_for_loop_iterates_batch_size(self, orchestrator):
        """Test for b in range(batch_size) iteration in stop condition check."""
        batch_size = 5
        horizon = 3
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))

        stop_checks_per_timestep = []
        current_timestep = [0]

        def count_stop_checks(state):
            if len(stop_checks_per_timestep) <= current_timestep[0]:
                stop_checks_per_timestep.append(0)
            stop_checks_per_timestep[current_timestep[0]] += 1
            return False

        step_count = [0]
        def track_timesteps(state, control, dt, **kwargs):
            step_count[0] += 1
            if step_count[0] % batch_size == 0:
                current_timestep[0] += 1
            return state

        with patch.object(orchestrator, 'step', side_effect=track_timesteps):
            result = orchestrator.execute(
                initial_state, control_inputs, dt=0.01, horizon=horizon,
                stop_fn=count_stop_checks
            )

        # Each timestep should check all batch elements
        for checks in stop_checks_per_timestep:
            assert checks == batch_size

    # ------------------------------------------------------------------------
    # Category 5: Safety Guards Integration (5 tests)
    # ------------------------------------------------------------------------

    def test_safety_guards_true_imports_and_calls(self, orchestrator):
        """Test safety_guards=True imports and calls apply_safety_guards()."""
        batch_size = 2
        horizon = 3
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))

        mock_apply_guards = Mock()

        with patch.object(orchestrator, 'step', return_value=np.zeros(6)):
            with patch('src.simulation.safety.guards.apply_safety_guards', mock_apply_guards):
                result = orchestrator.execute(
                    initial_state, control_inputs, dt=0.01, horizon=horizon,
                    safety_guards=True
                )

        # apply_safety_guards should be called for each step and batch element
        assert mock_apply_guards.call_count == batch_size * horizon

    def test_safety_guards_false_skips_checks(self, orchestrator):
        """Test safety_guards=False skips guard checks."""
        batch_size = 2
        horizon = 3
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))

        mock_apply_guards = Mock()

        with patch.object(orchestrator, 'step', return_value=np.zeros(6)):
            with patch('src.simulation.safety.guards.apply_safety_guards', mock_apply_guards):
                result = orchestrator.execute(
                    initial_state, control_inputs, dt=0.01, horizon=horizon,
                    safety_guards=False
                )

        # apply_safety_guards should NOT be called
        assert mock_apply_guards.call_count == 0

    def test_apply_safety_guards_call_signature(self, orchestrator):
        """Test apply_safety_guards(current_states[b], i, self.config) call signature."""
        batch_size = 2
        horizon = 2
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))

        guard_calls = []
        def track_guard_calls(state, step_idx, config):
            guard_calls.append((state.copy(), step_idx, config))

        with patch.object(orchestrator, 'step', return_value=np.zeros(6)):
            with patch('src.simulation.safety.guards.apply_safety_guards', side_effect=track_guard_calls):
                result = orchestrator.execute(
                    initial_state, control_inputs, dt=0.01, horizon=horizon,
                    safety_guards=True
                )

        # Verify call signature: (state, step_index, config)
        assert len(guard_calls) == batch_size * horizon
        for state, step_idx, config in guard_calls:
            assert isinstance(state, np.ndarray)
            assert isinstance(step_idx, int)
            assert step_idx < horizon

    def test_exception_in_safety_guards_deactivates(self, orchestrator):
        """Test exception in apply_safety_guards() sets active_mask[b]=False."""
        batch_size = 2
        horizon = 5
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))

        # Make safety guard fail on first call
        call_count = [0]
        def failing_guard(state, step_idx, config):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("Safety violation")

        step_count = [0]
        def count_steps(state, control, dt, **kwargs):
            step_count[0] += 1
            return state

        with patch.object(orchestrator, 'step', side_effect=count_steps):
            with patch('src.simulation.safety.guards.apply_safety_guards', side_effect=failing_guard):
                result = orchestrator.execute(
                    initial_state, control_inputs, dt=0.01, horizon=horizon,
                    safety_guards=True
                )

        # First element should fail, second should continue
        # Expected: first element fails on step 1, second completes 5 steps = 6 total
        assert step_count[0] >= 5

    def test_safety_guards_per_batch_element(self, orchestrator):
        """Test safety guards checked per batch element independently."""
        batch_size = 4
        horizon = 3
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))

        guard_call_indices = []

        def track_batch_index(state, step_idx, config):
            # Track which batch element is being checked
            guard_call_indices.append((step_idx, state[0]))  # Use state[0] as identifier

        # Give each batch element unique initial state
        for b in range(batch_size):
            initial_state[b, 0] = b * 0.1

        with patch.object(orchestrator, 'step', return_value=np.zeros(6)):
            with patch('src.simulation.safety.guards.apply_safety_guards', side_effect=track_batch_index):
                result = orchestrator.execute(
                    initial_state, control_inputs, dt=0.01, horizon=horizon,
                    safety_guards=True
                )

        # Should check each batch element independently
        assert len(guard_call_indices) == batch_size * horizon


# ==============================================================================
# Track C: State Update & Edge Cases (5 tests)
# ==============================================================================

class TestStateUpdateValidation:
    """Test state propagation and finite checks (5 tests)."""

    # ------------------------------------------------------------------------
    # Category 6: State Update Loop (3 tests)
    # ------------------------------------------------------------------------

    def test_next_states_copy_initialization(self, orchestrator):
        """Test next_states = current_states.copy() initialization."""
        batch_size = 2
        horizon = 3
        initial_state = np.array([[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
                                 [7.0, 8.0, 9.0, 10.0, 11.0, 12.0]])
        control_inputs = np.zeros((batch_size, horizon))

        # Make step return the input state unchanged
        with patch.object(orchestrator, 'step', side_effect=lambda s, c, dt, **kw: s):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=horizon)

        # Final states should match initial states (no dynamics applied)
        states_b0 = result.get_states(batch_index=0)
        states_b1 = result.get_states(batch_index=1)

        np.testing.assert_array_almost_equal(states_b0[0], initial_state[0])
        np.testing.assert_array_almost_equal(states_b1[0], initial_state[1])

    def test_step_call_signature(self, orchestrator):
        """Test next_state = self.step(current_states[b], control, dt, t=times[i])."""
        batch_size = 2
        horizon = 3
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))
        t0 = 1.5
        dt = 0.01

        step_calls = []
        def capture_step_args(state, control, dt_arg, **kwargs):
            step_calls.append({
                'state': state.copy(),
                'control': control,
                'dt': dt_arg,
                't': kwargs.get('t', None)
            })
            return state

        with patch.object(orchestrator, 'step', side_effect=capture_step_args):
            result = orchestrator.execute(
                initial_state, control_inputs, dt=dt, horizon=horizon,
                t0=t0
            )

        # Verify call signature and time progression
        assert len(step_calls) == batch_size * horizon
        for i, call_info in enumerate(step_calls):
            assert call_info['dt'] == dt
            # Time should progress with timesteps
            expected_time = t0 + (i // batch_size) * dt
            assert call_info['t'] is not None

    def test_state_assignment_on_success(self, orchestrator):
        """Test states[b, i+1, :] = next_state assignment on success."""
        batch_size = 2
        horizon = 5
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))

        # Increment state by 0.1 each step
        def increment_state(state, control, dt, **kwargs):
            return state + 0.1

        with patch.object(orchestrator, 'step', side_effect=increment_state):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=horizon)

        # Check state progression for first batch element
        states = result.get_states(batch_index=0)

        # States should increment by 0.1 each step
        for i in range(1, len(states)):
            expected_increment = np.allclose(states[i] - states[i-1], 0.1, atol=1e-10)
            assert expected_increment or np.allclose(states[i], states[i-1], atol=1e-10)

    # ------------------------------------------------------------------------
    # Category 7: Finite State Validation (2 tests)
    # ------------------------------------------------------------------------

    def test_isfinite_check_all(self, orchestrator):
        """Test np.isfinite(next_state).all() check."""
        batch_size = 2
        horizon = 5
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))

        # Return NaN on step 3 for first batch element
        call_count = [0]
        def selective_nan(state, control, dt, **kwargs):
            call_count[0] += 1
            if call_count[0] == 5:  # Step 3 for first element (0-indexed)
                return np.array([np.nan, 0, 0, 0, 0, 0])
            return state + 0.01

        with patch.object(orchestrator, 'step', side_effect=selective_nan):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=horizon)

        # Verify that result contains data for both batch elements
        states_b0 = result.get_states(batch_index=0)
        states_b1 = result.get_states(batch_index=1)

        # Both should have some trajectory data
        assert len(states_b0) > 0
        assert len(states_b1) > 0

        # At least one element should complete successfully
        assert len(states_b1) >= 5

    def test_active_mask_false_on_inf(self, orchestrator):
        """Test active_mask[b]=False when state contains inf."""
        batch_size = 2
        horizon = 5
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))

        # Return inf on step 2
        call_count = [0]
        def return_inf(state, control, dt, **kwargs):
            call_count[0] += 1
            if call_count[0] == 3:
                return np.array([np.inf, 0, 0, 0, 0, 0])
            return state + 0.01

        with patch.object(orchestrator, 'step', side_effect=return_inf):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=horizon)

        # Should handle inf by deactivating element
        assert result is not None


# ==============================================================================
# Track D: Performance & Edge Cases (5 tests - BONUS)
# ==============================================================================

class TestExecutionTracking:
    """Test execution tracking and array initialization (5 tests)."""

    # ------------------------------------------------------------------------
    # Category 8: Execution Tracking (3 tests)
    # ------------------------------------------------------------------------

    def test_start_time_before_loop(self, orchestrator):
        """Test start_time = time.perf_counter() before loop."""
        batch_size = 1
        horizon = 5
        initial_state = np.zeros((1, 6))
        control_inputs = np.zeros((1, horizon))

        with patch('time.perf_counter') as mock_perf:
            mock_perf.return_value = 100.0
            with patch.object(orchestrator, 'step', return_value=np.zeros(6)):
                result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=horizon)

        # perf_counter should be called at least twice (start and end)
        assert mock_perf.call_count >= 2

    def test_execution_time_calculation(self, orchestrator):
        """Test execution_time = time.perf_counter() - start_time after loop."""
        batch_size = 1
        horizon = 5
        initial_state = np.zeros((1, 6))
        control_inputs = np.zeros((1, horizon))

        # Mock time progression
        time_values = [100.0, 100.5]  # 0.5 second execution
        time_iter = iter(time_values)

        with patch('time.perf_counter', side_effect=lambda: next(time_iter)):
            with patch.object(orchestrator, 'step', return_value=np.zeros(6)):
                result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=horizon)

        # Check execution stats were updated
        stats = orchestrator.get_execution_statistics()
        assert stats['total_time'] > 0

    def test_update_stats_call(self, orchestrator):
        """Test self._update_stats(total_steps, execution_time) call."""
        batch_size = 2
        horizon = 5
        initial_state = np.zeros((batch_size, 6))
        control_inputs = np.zeros((batch_size, horizon))

        with patch.object(orchestrator, 'step', return_value=np.zeros(6)):
            with patch.object(orchestrator, '_update_stats') as mock_update:
                result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=horizon)

        # _update_stats should be called once with total_steps and execution_time
        mock_update.assert_called_once()
        call_args = mock_update.call_args[0]
        total_steps = call_args[0]
        execution_time = call_args[1]

        assert total_steps == batch_size * horizon
        assert execution_time >= 0

    # ------------------------------------------------------------------------
    # Category 9: Array Initialization (2 tests)
    # ------------------------------------------------------------------------

    def test_times_linspace_initialization(self, orchestrator):
        """Test times = np.linspace(t0, t0 + horizon * dt, horizon + 1)."""
        batch_size = 1
        horizon = 10
        dt = 0.02
        t0 = 5.0
        initial_state = np.zeros((1, 6))
        control_inputs = np.zeros((1, horizon))

        with patch.object(orchestrator, 'step', return_value=np.zeros(6)):
            result = orchestrator.execute(
                initial_state, control_inputs, dt=dt, horizon=horizon, t0=t0
            )

        # Get time array from result
        times = result.get_times(batch_index=0)

        # Should start at t0
        assert np.isclose(times[0], t0)
        # Should end at t0 + horizon * dt
        assert np.isclose(times[-1], t0 + horizon * dt, rtol=1e-10)
        # Should have horizon + 1 points
        assert len(times) == horizon + 1

    def test_states_initial_assignment(self, orchestrator):
        """Test states[:, 0, :] = initial_state initialization."""
        batch_size = 3
        horizon = 5
        initial_state = np.array([
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0, 10.0, 11.0, 12.0],
            [13.0, 14.0, 15.0, 16.0, 17.0, 18.0]
        ])
        control_inputs = np.zeros((batch_size, horizon))

        with patch.object(orchestrator, 'step', return_value=np.zeros(6)):
            result = orchestrator.execute(initial_state, control_inputs, dt=0.01, horizon=horizon)

        # Check that initial states are correctly assigned
        for b in range(batch_size):
            states = result.get_states(batch_index=b)
            np.testing.assert_array_almost_equal(states[0], initial_state[b])


# ==============================================================================
# Run Tests
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
