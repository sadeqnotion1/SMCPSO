#======================================================================================\\
#======================== tests/test_plant/test_core/test_physics_matrices.py ========================\\
#======================================================================================\\

"""Comprehensive tests for physics matrix computation."""

import pytest
import numpy as np
from unittest.mock import Mock
from src.plant.core.physics_matrices import DIPPhysicsMatrices, SimplifiedDIPPhysicsMatrices


class MockPhysicsParameters:
    """Mock physics parameters for testing."""

    def __init__(self, **kwargs):
        # Set default parameter
        self.cart_mass = kwargs.get('cart_mass', 1.0)
        self.pendulum1_mass = kwargs.get('pendulum1_mass', 0.1)
        self.pendulum2_mass = kwargs.get('pendulum2_mass', 0.1)
        self.pendulum1_length = kwargs.get('pendulum1_length', 0.5)
        self.pendulum2_length = kwargs.get('pendulum2_length', 0.5)
        self.pendulum1_com = kwargs.get('pendulum1_com', 0.25)
        self.pendulum2_com = kwargs.get('pendulum2_com', 0.25)
        self.pendulum1_inertia = kwargs.get('pendulum1_inertia', 0.01)
        self.pendulum2_inertia = kwargs.get('pendulum2_inertia', 0.01)
        self.gravity = kwargs.get('gravity', 9.81)
        self.cart_friction = kwargs.get('cart_friction', 0.1)
        self.joint1_friction = kwargs.get('joint1_friction', 0.01)
        self.joint2_friction = kwargs.get('joint2_friction', 0.01)


class TestDIPPhysicsMatricesInitialization:
    """Test DIPPhysicsMatrices initialization."""

    def test_init_with_default_parameters(self):
        """Test initialization with default parameters."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        assert matrices.m0 == 1.0
        assert matrices.m1 == 0.1
        assert matrices.m2 == 0.1
        assert matrices.L1 == 0.5
        assert matrices.L2 == 0.5
        assert matrices.g == 9.81

    def test_init_stores_parameters(self):
        """Test that initialization stores parameters."""
        params = MockPhysicsParameters(cart_mass=2.0, gravity=10.0)
        matrices = DIPPhysicsMatrices(params)

        assert matrices.m0 == 2.0
        assert matrices.g == 10.0
        assert matrices.params is params

    def test_init_friction_coefficients(self):
        """Test friction coefficient storage."""
        params = MockPhysicsParameters(
            cart_friction=0.2,
            joint1_friction=0.02,
            joint2_friction=0.03
        )
        matrices = DIPPhysicsMatrices(params)

        assert matrices.c0 == 0.2
        assert matrices.c1 == 0.02
        assert matrices.c2 == 0.03

    def test_init_inertia_properties(self):
        """Test inertia property storage."""
        params = MockPhysicsParameters(
            pendulum1_inertia=0.05,
            pendulum2_inertia=0.06
        )
        matrices = DIPPhysicsMatrices(params)

        assert matrices.I1 == 0.05
        assert matrices.I2 == 0.06

    def test_init_center_of_mass(self):
        """Test center of mass property storage."""
        params = MockPhysicsParameters(
            pendulum1_com=0.3,
            pendulum2_com=0.4
        )
        matrices = DIPPhysicsMatrices(params)

        assert matrices.Lc1 == 0.3
        assert matrices.Lc2 == 0.4


class TestInertiaMatrixComputation:
    """Test inertia matrix computation."""

    def test_compute_inertia_zero_angles(self):
        """Test inertia matrix at zero angles."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        M = matrices.compute_inertia_matrix(state)

        assert M.shape == (3, 3)
        assert isinstance(M, np.ndarray)
        # At zero angles, M should be symmetric
        assert np.allclose(M, M.T)

    def test_compute_inertia_non_zero_angles(self):
        """Test inertia matrix at non-zero angles."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.0, 0.1, 0.2, 0.0, 0.0, 0.0])

        M = matrices.compute_inertia_matrix(state)

        assert M.shape == (3, 3)
        # Inertia should still be symmetric
        assert np.allclose(M, M.T)
        # Diagonal elements should be positive
        assert np.all(np.diag(M) > 0)

    def test_compute_inertia_large_angles(self):
        """Test inertia matrix with large angles."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.0, np.pi/2, np.pi/4, 0.0, 0.0, 0.0])

        M = matrices.compute_inertia_matrix(state)

        assert M.shape == (3, 3)
        assert np.allclose(M, M.T)
        assert np.all(np.diag(M) > 0)

    def test_compute_inertia_with_position(self):
        """Test that cart position doesn't affect inertia matrix."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        state1 = np.array([0.0, 0.1, 0.2, 0.0, 0.0, 0.0])
        state2 = np.array([1.0, 0.1, 0.2, 0.0, 0.0, 0.0])

        M1 = matrices.compute_inertia_matrix(state1)
        M2 = matrices.compute_inertia_matrix(state2)

        # Cart position should not affect inertia matrix
        assert np.allclose(M1, M2)

    def test_compute_inertia_different_parameters(self):
        """Test inertia matrix with different parameters."""
        params1 = MockPhysicsParameters(cart_mass=1.0)
        params2 = MockPhysicsParameters(cart_mass=2.0)

        matrices1 = DIPPhysicsMatrices(params1)
        matrices2 = DIPPhysicsMatrices(params2)

        state = np.array([0.0, 0.1, 0.2, 0.0, 0.0, 0.0])

        M1 = matrices1.compute_inertia_matrix(state)
        M2 = matrices2.compute_inertia_matrix(state)

        # Different cart mass should affect inertia
        assert not np.allclose(M1, M2)


class TestCoriolisMatrixComputation:
    """Test Coriolis matrix computation."""

    def test_compute_coriolis_zero_state(self):
        """Test Coriolis matrix at zero state."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        C = matrices.compute_coriolis_matrix(state)

        assert C.shape == (3, 3)
        assert isinstance(C, np.ndarray)
        # At zero velocities, Coriolis should have only friction terms
        assert np.allclose(C[0, 0], params.cart_friction)
        assert np.allclose(C[1, 1], params.joint1_friction)
        assert np.allclose(C[2, 2], params.joint2_friction)

    def test_compute_coriolis_with_velocity(self):
        """Test Coriolis matrix with non-zero velocities."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.0, 0.1, 0.2, 0.0, 1.0, 0.5])

        C = matrices.compute_coriolis_matrix(state)

        assert C.shape == (3, 3)
        # Diagonal should contain friction terms (approximately)
        assert np.isclose(C[0, 0], params.cart_friction)
        assert np.isclose(C[1, 1], params.joint1_friction, atol=0.01)
        assert np.isclose(C[2, 2], params.joint2_friction, atol=0.01)

    def test_compute_coriolis_zero_velocity(self):
        """Test Coriolis matrix structure at zero velocity."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.0, np.pi/4, np.pi/6, 0.0, 0.0, 0.0])

        C = matrices.compute_coriolis_matrix(state)

        assert C.shape == (3, 3)
        # Off-diagonal C[0,1:] and C[0,2:] should be zero at zero velocity
        assert np.allclose(C[0, 1:], 0.0)

    def test_compute_coriolis_velocity_dependence(self):
        """Test that Coriolis matrix depends on velocity."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        state1 = np.array([0.0, 0.1, 0.2, 0.0, 0.0, 0.0])
        state2 = np.array([0.0, 0.1, 0.2, 0.0, 2.0, 1.0])

        C1 = matrices.compute_coriolis_matrix(state1)
        C2 = matrices.compute_coriolis_matrix(state2)

        # Different velocities should generally affect some Coriolis terms
        # Check that at least some off-diagonal terms differ
        assert not np.allclose(C1[0, 1:], C2[0, 1:], atol=0.001)


class TestGravityVectorComputation:
    """Test gravity vector computation."""

    def test_compute_gravity_zero_angles(self):
        """Test gravity vector at zero angles."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        G = matrices.compute_gravity_vector(state)

        assert G.shape == (3,)
        # At zero angles (upright), gravity on pendulums should be zero
        # Cart gravity term is zero (no vertical component)
        assert np.allclose(G[0], 0.0)
        assert np.allclose(G[1], 0.0)
        assert np.allclose(G[2], 0.0)

    def test_compute_gravity_horizontal(self):
        """Test gravity vector at horizontal angles (pi/2)."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.0, np.pi/2, 0.0, 0.0, 0.0, 0.0])

        G = matrices.compute_gravity_vector(state)

        assert G.shape == (3,)
        # At pi/2, sin(pi/2) = 1, so gravity should be maximum
        assert G[0] == 0.0  # Cart has no gravity term
        assert G[1] < 0.0  # Gravity effect on link 1
        assert G[2] == 0.0  # Link 2 not affected

    def test_compute_gravity_inverted(self):
        """Test gravity vector at inverted angles (pi)."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.0, np.pi, 0.0, 0.0, 0.0, 0.0])

        G = matrices.compute_gravity_vector(state)

        assert G.shape == (3,)
        # At pi, sin(pi) = 0, so gravity should be zero
        assert np.allclose(G, 0.0, atol=1e-10)

    def test_compute_gravity_different_gravity(self):
        """Test gravity vector with different gravity values."""
        params1 = MockPhysicsParameters(gravity=9.81)
        params2 = MockPhysicsParameters(gravity=10.0)

        matrices1 = DIPPhysicsMatrices(params1)
        matrices2 = DIPPhysicsMatrices(params2)

        state = np.array([0.0, np.pi/4, np.pi/6, 0.0, 0.0, 0.0])

        G1 = matrices1.compute_gravity_vector(state)
        G2 = matrices2.compute_gravity_vector(state)

        # Different gravity should affect gravity vector proportionally
        assert not np.allclose(G1, G2)
        # Check that the scaling is approximately 10.0/9.81
        expected_ratio = 10.0 / 9.81
        # Compare non-zero elements
        for i in range(3):
            if np.abs(G1[i]) > 1e-10:
                actual_ratio = G2[i] / G1[i]
                assert np.isclose(actual_ratio, expected_ratio, rtol=0.01)


class TestComputeAllMatrices:
    """Test combined matrix computation."""

    def test_compute_all_matrices_zero_state(self):
        """Test computing all matrices at zero state."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        M, C, G = matrices.compute_all_matrices(state)

        assert M.shape == (3, 3)
        assert C.shape == (3, 3)
        assert G.shape == (3,)

    def test_compute_all_matrices_consistency(self):
        """Test that all_matrices returns same results as individual methods."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.1, 0.2, 0.3, 0.5, 0.6, 0.7])

        M1, C1, G1 = matrices.compute_all_matrices(state)
        M2 = matrices.compute_inertia_matrix(state)
        C2 = matrices.compute_coriolis_matrix(state)
        G2 = matrices.compute_gravity_vector(state)

        assert np.allclose(M1, M2)
        assert np.allclose(C1, C2)
        assert np.allclose(G1, G2)

    def test_compute_all_matrices_generic_state(self):
        """Test all matrices with arbitrary state."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.array([1.5, 0.5, -0.3, 0.2, 1.2, -0.8])

        M, C, G = matrices.compute_all_matrices(state)

        assert M.shape == (3, 3)
        assert C.shape == (3, 3)
        assert G.shape == (3,)
        assert np.allclose(M, M.T)  # M should be symmetric


class TestSimplifiedDIPPhysicsMatrices:
    """Test SimplifiedDIPPhysicsMatrices."""

    def test_simplified_init(self):
        """Test simplified matrices initialization."""
        params = MockPhysicsParameters()
        matrices = SimplifiedDIPPhysicsMatrices(params)

        assert matrices.m0 == 1.0
        assert matrices.m1 == 0.1
        assert matrices.m2 == 0.1

    def test_simplified_inertia_computation(self):
        """Test simplified inertia matrix computation."""
        params = MockPhysicsParameters()
        matrices = SimplifiedDIPPhysicsMatrices(params)
        state = np.array([0.0, 0.1, 0.2, 0.0, 0.0, 0.0])

        M = matrices.compute_inertia_matrix(state)

        assert M.shape == (3, 3)
        assert np.allclose(M, M.T)
        assert np.all(np.diag(M) > 0)

    def test_simplified_vs_full_inertia(self):
        """Test difference between simplified and full inertia matrices."""
        params = MockPhysicsParameters()
        full_matrices = DIPPhysicsMatrices(params)
        simplified_matrices = SimplifiedDIPPhysicsMatrices(params)
        state = np.array([0.0, 0.5, 0.3, 0.0, 0.0, 0.0])

        M_full = full_matrices.compute_inertia_matrix(state)
        M_simplified = simplified_matrices.compute_inertia_matrix(state)

        # Simplified should approximate full (not equal due to approximations)
        assert not np.allclose(M_full, M_simplified)
        # First and last diagonal terms should be very similar
        assert np.isclose(M_full[0, 0], M_simplified[0, 0])
        assert np.isclose(M_full[2, 2], M_simplified[2, 2])

    def test_simplified_inherits_coriolis(self):
        """Test that simplified class inherits Coriolis computation."""
        params = MockPhysicsParameters()
        matrices = SimplifiedDIPPhysicsMatrices(params)
        state = np.array([0.0, 0.1, 0.2, 0.0, 1.0, 0.5])

        C = matrices.compute_coriolis_matrix(state)

        assert C.shape == (3, 3)
        # Should use parent class Coriolis computation
        assert C[0, 0] == params.cart_friction

    def test_simplified_inherits_gravity(self):
        """Test that simplified class inherits gravity computation."""
        params = MockPhysicsParameters()
        matrices = SimplifiedDIPPhysicsMatrices(params)
        state = np.array([0.0, np.pi/4, np.pi/6, 0.0, 0.0, 0.0])

        G = matrices.compute_gravity_vector(state)

        assert G.shape == (3,)


class TestNumericalProperties:
    """Test numerical properties of physics matrices."""

    def test_inertia_positive_definiteness(self):
        """Test that inertia matrix is positive semi-definite."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        # Test at multiple angles
        for theta1 in [0, np.pi/6, np.pi/4, np.pi/2]:
            for theta2 in [0, np.pi/6, np.pi/4]:
                state = np.array([0.0, theta1, theta2, 0.0, 0.0, 0.0])
                M = matrices.compute_inertia_matrix(state)

                # Check eigenvalues are non-negative
                eigenvalues = np.linalg.eigvalsh(M)
                assert np.all(eigenvalues >= -1e-10)  # Allow small numerical errors

    def test_inertia_symmetry(self):
        """Test that inertia matrix is symmetric."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        for _ in range(10):
            state = np.random.randn(6)
            M = matrices.compute_inertia_matrix(state)
            assert np.allclose(M, M.T)

    def test_gravity_magnitude_bounds(self):
        """Test that gravity vector magnitude is bounded."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        for _ in range(20):
            state = np.random.randn(6) * 2 * np.pi
            G = matrices.compute_gravity_vector(state)

            # Gravity magnitude should be bounded by maximum possible
            max_gravity = 2 * params.gravity * (
                params.pendulum1_mass * params.pendulum1_com +
                params.pendulum2_mass * params.pendulum1_length +
                params.pendulum2_mass * params.pendulum2_com
            )
            assert np.linalg.norm(G) <= max_gravity * 1.1  # 10% margin for numerical error

    def test_matrix_dimensions(self):
        """Test that all matrices have correct dimensions."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.random.randn(6)

        M = matrices.compute_inertia_matrix(state)
        C = matrices.compute_coriolis_matrix(state)
        G = matrices.compute_gravity_vector(state)

        assert M.shape == (3, 3)
        assert C.shape == (3, 3)
        assert G.shape == (3,)

    def test_matrix_values_not_nan(self):
        """Test that matrix values are not NaN or Inf."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        for _ in range(20):
            state = np.random.randn(6)
            M = matrices.compute_inertia_matrix(state)
            C = matrices.compute_coriolis_matrix(state)
            G = matrices.compute_gravity_vector(state)

            assert np.all(np.isfinite(M))
            assert np.all(np.isfinite(C))
            assert np.all(np.isfinite(G))


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_small_masses(self):
        """Test with very small masses."""
        params = MockPhysicsParameters(
            cart_mass=0.001,
            pendulum1_mass=0.0001,
            pendulum2_mass=0.0001
        )
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.0, 0.1, 0.2, 0.0, 0.0, 0.0])

        M = matrices.compute_inertia_matrix(state)
        assert np.all(np.isfinite(M))

    def test_large_angles(self):
        """Test with very large angles."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        state = np.array([0.0, 10.0, 20.0, 0.0, 0.0, 0.0])

        M = matrices.compute_inertia_matrix(state)
        C = matrices.compute_coriolis_matrix(state)
        G = matrices.compute_gravity_vector(state)

        assert np.all(np.isfinite(M))
        assert np.all(np.isfinite(C))
        assert np.all(np.isfinite(G))

    def test_high_velocities(self):
        """Test with very high velocities."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        state = np.array([0.0, 0.1, 0.2, 100.0, 100.0, 100.0])

        C = matrices.compute_coriolis_matrix(state)
        assert np.all(np.isfinite(C))

    def test_negative_angles(self):
        """Test with negative angles."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        state = np.array([0.0, -0.5, -0.3, 0.0, 0.0, 0.0])

        M = matrices.compute_inertia_matrix(state)
        G = matrices.compute_gravity_vector(state)

        assert np.all(np.isfinite(M))
        assert np.all(np.isfinite(G))
        # Verify symmetry
        assert np.allclose(M, M.T)
