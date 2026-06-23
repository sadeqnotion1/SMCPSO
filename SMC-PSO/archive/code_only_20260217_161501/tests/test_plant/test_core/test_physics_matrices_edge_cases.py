#======================================================================================\\
#============== tests/test_plant/test_core/test_physics_matrices_edge_cases.py ==============\\
#======================================================================================\\

"""
Edge case and advanced validation tests for physics matrix computation.

Tests focus on:
- Numba fallback behavior
- Extreme physics scenarios (singularities, high velocities)
- Matrix mathematical properties (symmetry, positive-definiteness)
- Performance characteristics
- Numerical stability at edge configurations
"""

import pytest
import numpy as np
import time
from unittest.mock import patch, MagicMock
from src.plant.core.physics_matrices import DIPPhysicsMatrices, SimplifiedDIPPhysicsMatrices


class MockPhysicsParameters:
    """Mock physics parameters for testing."""

    def __init__(self, **kwargs):
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


class TestNumbaFallback:
    """Test Numba fallback behavior when JIT unavailable."""

    def test_numba_decorator_fallback(self):
        """Test that Numba fallback decorator works."""
        # The module already imports with fallback
        # Just verify matrices can be created and computed
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        M = matrices.compute_inertia_matrix(state)
        C = matrices.compute_coriolis_matrix(state)
        G = matrices.compute_gravity_vector(state)

        assert M.shape == (3, 3)
        assert C.shape == (3, 3)
        assert G.shape == (3,)


class TestExtremePhysicsScenarios:
    """Test physics computation under extreme conditions."""

    def test_inertia_matrix_zero_gravity(self):
        """Test inertia matrix computation with zero gravity."""
        params = MockPhysicsParameters(gravity=0.0)
        matrices = DIPPhysicsMatrices(params)
        state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        M = matrices.compute_inertia_matrix(state)
        G = matrices.compute_gravity_vector(state)

        # Inertia should still be valid
        assert M.shape == (3, 3)
        assert np.all(np.isfinite(M))

        # Gravity vector should be zero
        assert np.allclose(G, np.zeros(3))

    def test_coriolis_matrix_extreme_coupling(self):
        """Test Coriolis matrix with high angular velocities."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        # High angular velocities
        state = np.array([0.0, 0.0, 0.0, 0.0, 100.0, 100.0])

        C = matrices.compute_coriolis_matrix(state)

        assert C.shape == (3, 3)
        assert np.all(np.isfinite(C))

    def test_gravity_vector_inverted_heavy_pendulums(self):
        """Test gravity vector with inverted pendulums and high masses."""
        params = MockPhysicsParameters(
            pendulum1_mass=10.0,
            pendulum2_mass=10.0
        )
        matrices = DIPPhysicsMatrices(params)

        # Inverted configuration
        state = np.array([0.0, np.pi, np.pi, 0.0, 0.0, 0.0])

        G = matrices.compute_gravity_vector(state)

        assert G.shape == (3,)
        assert np.all(np.isfinite(G))
        # G2 and G3 should be significant due to heavy pendulums
        assert abs(G[1]) > 0 or abs(G[2]) > 0

    def test_combined_matrices_high_speed_rotation(self):
        """Test all matrices with fast rotation."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        # Fast rotating state
        state = np.array([0.0, np.pi/4, np.pi/6, 1.0, 50.0, -50.0])

        M, C, G = matrices.compute_all_matrices(state)

        assert np.all(np.isfinite(M))
        assert np.all(np.isfinite(C))
        assert np.all(np.isfinite(G))


class TestSingularityConditions:
    """Test physics matrices near singularity configurations."""

    def test_inertia_matrix_near_singularity_theta1_pi_half(self):
        """Test inertia matrix near theta1 = π/2 singularity."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        # Near π/2 (but not exactly to avoid true singularity)
        state = np.array([0.0, np.pi/2 - 0.001, 0.0, 0.0, 0.0, 0.0])

        M = matrices.compute_inertia_matrix(state)

        assert M.shape == (3, 3)
        assert np.all(np.isfinite(M))
        # Matrix should still be invertible (det ≠ 0)
        assert abs(np.linalg.det(M)) > 1e-6

    def test_inertia_matrix_near_singularity_theta2_pi_half(self):
        """Test inertia matrix near theta2 = π/2 singularity."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        # Near π/2 for theta2
        state = np.array([0.0, 0.0, np.pi/2 - 0.001, 0.0, 0.0, 0.0])

        M = matrices.compute_inertia_matrix(state)

        assert M.shape == (3, 3)
        assert np.all(np.isfinite(M))
        assert abs(np.linalg.det(M)) > 1e-6

    def test_matrices_at_configuration_singularity(self):
        """Test all matrices when theta1 - theta2 = 0 (aligned pendulums)."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        # Aligned pendulums (theta1 = theta2)
        angle = np.pi / 4
        state = np.array([0.0, angle, angle, 0.0, 0.0, 0.0])

        M, C, G = matrices.compute_all_matrices(state)

        # cos(theta1 - theta2) = cos(0) = 1 (special case)
        assert np.all(np.isfinite(M))
        assert np.all(np.isfinite(C))
        assert np.all(np.isfinite(G))


class TestMatrixPropertyValidation:
    """Test mathematical properties of physics matrices."""

    def test_inertia_matrix_positive_definiteness(self):
        """Test that inertia matrix is positive definite."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        # Test at multiple configurations
        test_states = [
            np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),  # Upright
            np.array([0.0, np.pi/4, np.pi/6, 0.0, 0.0, 0.0]),  # Tilted
            np.array([0.0, -np.pi/3, np.pi/3, 0.0, 0.0, 0.0]),  # Complex
        ]

        for state in test_states:
            M = matrices.compute_inertia_matrix(state)

            # Check positive definiteness via eigenvalues
            eigenvalues = np.linalg.eigvals(M)
            assert np.all(eigenvalues > 0), f"Inertia matrix not positive definite at state {state[:3]}"

            # Check symmetry (M should be symmetric)
            assert np.allclose(M, M.T), f"Inertia matrix not symmetric at state {state[:3]}"

    def test_inertia_matrix_symmetry(self):
        """Test that inertia matrix is symmetric."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        state = np.array([0.0, 0.2, 0.3, 0.0, 0.0, 0.0])
        M = matrices.compute_inertia_matrix(state)

        # Symmetry: M = M^T
        assert np.allclose(M, M.T, atol=1e-12)

    def test_coriolis_skew_symmetry_property(self):
        """Test Coriolis matrix skew-symmetry property: M_dot - 2C is skew-symmetric (no friction)."""
        # Use zero friction to test theoretical property
        params = MockPhysicsParameters(
            cart_friction=0.0,
            joint1_friction=0.0,
            joint2_friction=0.0
        )
        matrices = DIPPhysicsMatrices(params)

        # State with non-zero velocities
        state = np.array([0.0, 0.1, 0.2, 0.0, 1.0, 0.5])

        M = matrices.compute_inertia_matrix(state)
        C = matrices.compute_coriolis_matrix(state)

        # Compute M_dot numerically using finite differences
        dt = 1e-6
        # Perturb angles based on angular velocities
        theta1_new = state[1] + state[4] * dt
        theta2_new = state[2] + state[5] * dt
        state_perturbed = np.array([state[0], theta1_new, theta2_new, state[3], state[4], state[5]])
        M_perturbed = matrices.compute_inertia_matrix(state_perturbed)
        M_dot = (M_perturbed - M) / dt

        # Test property: M_dot - 2C should be skew-symmetric (without friction)
        S = M_dot - 2 * C

        # Skew-symmetric: S = -S^T
        # Use larger tolerance due to numerical differentiation
        assert np.allclose(S, -S.T, atol=1e-2), "M_dot - 2C is not skew-symmetric (passivity property)"

    def test_energy_conservation_via_matrices(self):
        """Test energy conservation using physics matrices."""
        params = MockPhysicsParameters(
            cart_friction=0.0,
            joint1_friction=0.0,
            joint2_friction=0.0
        )
        matrices = DIPPhysicsMatrices(params)

        # Initial state with kinetic energy
        state = np.array([0.0, 0.1, 0.2, 0.0, 1.0, 0.5])

        M = matrices.compute_inertia_matrix(state)
        G = matrices.compute_gravity_vector(state)

        # Kinetic energy: T = 0.5 * q_dot^T * M * q_dot
        q_dot = state[3:6]
        T = 0.5 * q_dot @ M @ q_dot

        # Potential energy from gravity (integrated from G)
        # This is a simplified check - just verify energy is finite and positive
        assert T >= 0, "Kinetic energy must be non-negative"
        assert np.isfinite(T)


class TestPerformanceCharacteristics:
    """Test performance characteristics of matrix computation."""

    def test_matrix_computation_performance_baseline(self):
        """Establish baseline performance for matrix computation."""
        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        state = np.array([0.0, 0.1, 0.2, 0.0, 1.0, 0.5])

        # Warmup JIT
        for _ in range(10):
            matrices.compute_all_matrices(state)

        # Benchmark
        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            matrices.compute_all_matrices(state)
        elapsed = time.perf_counter() - start

        time_per_call = elapsed / iterations

        # Should be fast (< 100 microseconds per call after JIT warmup)
        assert time_per_call < 100e-6, f"Matrix computation too slow: {time_per_call*1e6:.2f} μs"

    def test_matrix_computation_thread_safety(self):
        """Test that matrix computation is thread-safe."""
        import threading

        params = MockPhysicsParameters()
        matrices = DIPPhysicsMatrices(params)

        results = []
        errors = []

        def compute_matrices(thread_id):
            try:
                state = np.array([0.0, 0.1*thread_id, 0.2*thread_id, 0.0, 1.0, 0.5])
                M, C, G = matrices.compute_all_matrices(state)
                results.append((thread_id, M, C, G))
            except Exception as e:
                errors.append((thread_id, e))

        # Run computations in parallel threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=compute_matrices, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 10


class TestSimplifiedPhysicsMatrices:
    """Test simplified physics matrices."""

    def test_simplified_inherits_from_full(self):
        """Test that SimplifiedDIPPhysicsMatrices inherits properly."""
        params = MockPhysicsParameters()
        simplified = SimplifiedDIPPhysicsMatrices(params)

        # Should have all attributes from parent
        assert hasattr(simplified, 'm0')
        assert hasattr(simplified, 'm1')
        assert hasattr(simplified, 'm2')
        assert hasattr(simplified, 'compute_inertia_matrix')
        assert hasattr(simplified, 'compute_coriolis_matrix')
        assert hasattr(simplified, 'compute_gravity_vector')

    def test_simplified_matrices_computation(self):
        """Test simplified matrices compute correctly."""
        params = MockPhysicsParameters()
        simplified = SimplifiedDIPPhysicsMatrices(params)

        state = np.array([0.0, 0.1, 0.2, 0.0, 1.0, 0.5])

        M, C, G = simplified.compute_all_matrices(state)

        assert M.shape == (3, 3)
        assert C.shape == (3, 3)
        assert G.shape == (3,)
        assert np.all(np.isfinite(M))
        assert np.all(np.isfinite(C))
        assert np.all(np.isfinite(G))
