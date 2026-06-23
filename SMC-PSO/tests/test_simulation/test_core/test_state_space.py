"""
Unit tests for state-space utilities (src/simulation/core/state_space.py).

Tests cover:
- StateSpaceUtilities.validate_state_dimensions
- StateSpaceUtilities.normalize_state_batch
- StateSpaceUtilities.extract_state_components
- StateSpaceUtilities.compute_state_bounds
- StateSpaceUtilities.compute_energy
- StateSpaceUtilities.linearize_about_equilibrium
"""

import numpy as np
import pytest

from src.simulation.core.state_space import StateSpaceUtilities


# ======================================================================================
# validate_state_dimensions Tests
# ======================================================================================

class TestValidateStateDimensions:
    """Test validate_state_dimensions method."""

    def test_1d_array_correct_dimension(self):
        """Should return True for 1D array with correct dimension."""
        state = np.array([1.0, 2.0, 3.0])
        assert StateSpaceUtilities.validate_state_dimensions(state, 3) == True

    def test_1d_array_incorrect_dimension(self):
        """Should return False for 1D array with incorrect dimension."""
        state = np.array([1.0, 2.0, 3.0])
        assert StateSpaceUtilities.validate_state_dimensions(state, 4) == False

    def test_2d_array_correct_dimension(self):
        """Should return True for 2D array with correct last dimension."""
        state = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        assert StateSpaceUtilities.validate_state_dimensions(state, 3) == True

    def test_2d_array_incorrect_dimension(self):
        """Should return False for 2D array with incorrect last dimension."""
        state = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        assert StateSpaceUtilities.validate_state_dimensions(state, 2) == False

    def test_3d_array_returns_false(self):
        """Should return False for 3D arrays (not supported)."""
        state = np.random.rand(2, 3, 4)
        assert StateSpaceUtilities.validate_state_dimensions(state, 4) == False

    def test_empty_1d_array(self):
        """Should handle empty 1D array."""
        state = np.array([])
        assert StateSpaceUtilities.validate_state_dimensions(state, 0) == True


# ======================================================================================
# normalize_state_batch Tests
# ======================================================================================

class TestNormalizeStateBatch:
    """Test normalize_state_batch method."""

    def test_1d_state_to_batch(self):
        """Should convert 1D state to (1, 1, state_dim) format."""
        state = np.array([1.0, 2.0, 3.0])
        result = StateSpaceUtilities.normalize_state_batch(state)

        assert result.shape == (1, 1, 3)
        np.testing.assert_array_equal(result[0, 0, :], state)

    def test_2d_state_to_batch(self):
        """Should convert 2D state to (1, time_steps, state_dim) format."""
        states = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        result = StateSpaceUtilities.normalize_state_batch(states)

        assert result.shape == (1, 3, 2)
        np.testing.assert_array_equal(result[0, :, :], states)

    def test_3d_state_passthrough(self):
        """Should return 3D state unchanged (already in batch format)."""
        states = np.random.rand(2, 5, 3)
        result = StateSpaceUtilities.normalize_state_batch(states)

        np.testing.assert_array_equal(result, states)

    def test_4d_state_raises_error(self):
        """Should raise ValueError for 4D arrays."""
        states = np.random.rand(2, 3, 4, 5)
        with pytest.raises(ValueError, match="Unsupported state array dimensionality: 4"):
            StateSpaceUtilities.normalize_state_batch(states)


# ======================================================================================
# extract_state_components Tests
# ======================================================================================

class TestExtractStateComponents:
    """Test extract_state_components method."""

    def test_extract_single_index(self):
        """Should extract single component using int index."""
        state = np.array([1.0, 2.0, 3.0, 4.0])
        indices = {"x": 0, "y": 2}

        components = StateSpaceUtilities.extract_state_components(state, indices)

        assert components["x"] == 1.0
        assert components["y"] == 3.0

    def test_extract_slice(self):
        """Should extract component slice."""
        state = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        indices = {"positions": slice(0, 3), "velocities": slice(3, 6)}

        components = StateSpaceUtilities.extract_state_components(state, indices)

        np.testing.assert_array_equal(components["positions"], [1.0, 2.0, 3.0])
        np.testing.assert_array_equal(components["velocities"], [4.0, 5.0, 6.0])

    def test_extract_list_indices(self):
        """Should extract multiple indices using list."""
        state = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        indices = {"selected": [0, 2, 4]}

        components = StateSpaceUtilities.extract_state_components(state, indices)

        np.testing.assert_array_equal(components["selected"], [1.0, 3.0, 5.0])

    def test_extract_from_batch(self):
        """Should extract components from batch (2D array)."""
        states = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        indices = {"first": 0, "last": 2}

        components = StateSpaceUtilities.extract_state_components(states, indices)

        np.testing.assert_array_equal(components["first"], [1.0, 4.0])
        np.testing.assert_array_equal(components["last"], [3.0, 6.0])

    def test_invalid_index_type_raises_error(self):
        """Should raise ValueError for unsupported index type."""
        state = np.array([1.0, 2.0, 3.0])
        indices = {"bad": "invalid"}

        with pytest.raises(ValueError, match="Unsupported index type"):
            StateSpaceUtilities.extract_state_components(state, indices)


# ======================================================================================
# compute_state_bounds Tests
# ======================================================================================

class TestComputeStateBounds:
    """Test compute_state_bounds method."""

    def test_2d_trajectory_default_percentile(self):
        """Should compute 95th percentile bounds for 2D trajectory."""
        states = np.array([
            [1.0, 2.0],
            [2.0, 3.0],
            [3.0, 4.0],
            [4.0, 5.0],
            [5.0, 6.0]
        ])

        lower, upper = StateSpaceUtilities.compute_state_bounds(states)

        # 95th percentile: 2.5th to 97.5th percentile
        assert lower.shape == (2,)
        assert upper.shape == (2,)
        assert np.all(lower <= upper)

    def test_3d_batch_trajectory(self):
        """Should compute bounds for 3D batch trajectory."""
        states = np.random.rand(3, 10, 4)  # 3 batches, 10 timesteps, 4 states

        lower, upper = StateSpaceUtilities.compute_state_bounds(states)

        assert lower.shape == (4,)
        assert upper.shape == (4,)
        assert np.all(lower <= upper)

    def test_custom_percentile(self):
        """Should compute bounds with custom percentile."""
        states = np.array([[i, i*2] for i in range(100)])

        lower_90, upper_90 = StateSpaceUtilities.compute_state_bounds(states, percentile=90.0)
        lower_50, upper_50 = StateSpaceUtilities.compute_state_bounds(states, percentile=50.0)

        # 90th percentile should be wider than 50th
        assert np.all(lower_90 <= lower_50)
        assert np.all(upper_90 >= upper_50)

    def test_single_sample(self):
        """Should handle single sample trajectory."""
        states = np.array([[1.0, 2.0, 3.0]])

        lower, upper = StateSpaceUtilities.compute_state_bounds(states)

        # Single sample: bounds should equal the sample
        np.testing.assert_array_almost_equal(lower, [1.0, 2.0, 3.0])
        np.testing.assert_array_almost_equal(upper, [1.0, 2.0, 3.0])


# ======================================================================================
# compute_energy Tests
# ======================================================================================

class TestComputeEnergy:
    """Test compute_energy method."""

    def test_unit_mass_1d_state(self):
        """Should compute kinetic energy with unit mass for 1D state."""
        state = np.array([1.0, 2.0, 3.0, 4.0])  # [pos1, pos2, vel1, vel2]

        energy = StateSpaceUtilities.compute_energy(state)

        # KE = 0.5 * (3^2 + 4^2) = 0.5 * 25 = 12.5
        assert energy == pytest.approx(12.5, abs=1e-10)

    def test_unit_mass_batch_states(self):
        """Should compute energy for batch of states."""
        states = np.array([
            [1.0, 2.0, 3.0, 4.0],  # velocities: 3, 4
            [0.0, 0.0, 1.0, 1.0]   # velocities: 1, 1
        ])

        energies = StateSpaceUtilities.compute_energy(states)

        np.testing.assert_array_almost_equal(energies, [12.5, 1.0], decimal=10)

    def test_custom_mass_matrix_1d_state(self):
        """Should compute energy with custom mass matrix for 1D state."""
        state = np.array([0.0, 0.0, 2.0, 0.0])  # velocity [2, 0]
        mass_matrix = np.array([[2.0, 0.0], [0.0, 3.0]])

        energy = StateSpaceUtilities.compute_energy(state, mass_matrix)

        # KE = 0.5 * v^T M v = 0.5 * [2, 0]^T [[2, 0], [0, 3]] [2, 0]
        #    = 0.5 * [2, 0]^T [4, 0] = 0.5 * 8 = 4.0
        assert energy == pytest.approx(4.0, abs=1e-10)

    def test_custom_mass_matrix_batch_states(self):
        """Should compute energy with custom mass matrix for batch."""
        states = np.array([
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])
        mass_matrix = np.array([[2.0, 0.0], [0.0, 3.0]])

        energies = StateSpaceUtilities.compute_energy(states, mass_matrix)

        # First state: velocity [1, 0], KE = 0.5 * 2 * 1^2 = 1.0
        # Second state: velocity [0, 1], KE = 0.5 * 3 * 1^2 = 1.5
        np.testing.assert_array_almost_equal(energies, [1.0, 1.5], decimal=10)

    def test_zero_velocity(self):
        """Should return zero energy for zero velocity."""
        state = np.array([1.0, 2.0, 0.0, 0.0])

        energy = StateSpaceUtilities.compute_energy(state)

        assert energy == pytest.approx(0.0, abs=1e-10)


# ======================================================================================
# linearize_about_equilibrium Tests
# ======================================================================================

class TestLinearizeAboutEquilibrium:
    """Test linearize_about_equilibrium method."""

    def test_simple_linear_dynamics(self):
        """Should linearize simple linear dynamics correctly."""
        # Linear dynamics: dx/dt = A*x + B*u
        A_true = np.array([[0.0, 1.0], [-2.0, -3.0]])
        B_true = np.array([[0.0], [1.0]])

        def linear_dynamics(x, u):
            return A_true @ x + B_true @ u

        x_eq = np.array([0.0, 0.0])
        u_eq = np.array([0.0])

        A, B = StateSpaceUtilities.linearize_about_equilibrium(
            linear_dynamics, x_eq, u_eq, epsilon=1e-6
        )

        np.testing.assert_array_almost_equal(A, A_true, decimal=5)
        np.testing.assert_array_almost_equal(B, B_true, decimal=5)

    def test_nonlinear_dynamics(self):
        """Should linearize nonlinear dynamics using finite differences."""
        # Nonlinear: dx1/dt = x2, dx2/dt = -sin(x1) + u
        def nonlinear_dynamics(x, u):
            return np.array([x[1], -np.sin(x[0]) + u[0]])

        # Equilibrium at x=[0, 0], u=[0]
        x_eq = np.array([0.0, 0.0])
        u_eq = np.array([0.0])

        A, B = StateSpaceUtilities.linearize_about_equilibrium(
            nonlinear_dynamics, x_eq, u_eq, epsilon=1e-6
        )

        # Expected: A = [[0, 1], [-cos(0), 0]] = [[0, 1], [-1, 0]]
        A_expected = np.array([[0.0, 1.0], [-1.0, 0.0]])
        B_expected = np.array([[0.0], [1.0]])

        np.testing.assert_array_almost_equal(A, A_expected, decimal=5)
        np.testing.assert_array_almost_equal(B, B_expected, decimal=5)

    def test_matrix_dimensions(self):
        """Should produce correctly sized A and B matrices."""
        def dynamics(x, u):
            # 3 states, 2 controls
            return np.array([x[1], x[2], u[0] + u[1]])

        x_eq = np.zeros(3)
        u_eq = np.zeros(2)

        A, B = StateSpaceUtilities.linearize_about_equilibrium(
            dynamics, x_eq, u_eq
        )

        assert A.shape == (3, 3)
        assert B.shape == (3, 2)

    def test_non_zero_equilibrium(self):
        """Should linearize about non-zero equilibrium point."""
        # Simple dynamics: dx/dt = x^2 + u
        def dynamics(x, u):
            return np.array([x[0]**2 + u[0]])

        # Equilibrium at x=[2], u=[-4] (so 2^2 - 4 = 0)
        x_eq = np.array([2.0])
        u_eq = np.array([-4.0])

        A, B = StateSpaceUtilities.linearize_about_equilibrium(
            dynamics, x_eq, u_eq, epsilon=1e-6
        )

        # ∂f/∂x = 2x = 4 at x=2
        # ∂f/∂u = 1
        assert A[0, 0] == pytest.approx(4.0, abs=1e-4)
        assert B[0, 0] == pytest.approx(1.0, abs=1e-4)
