#======================================================================================\\\
#======= tests/test_analysis/performance/test_lyapunov_stability_verification.py =====\\\
#======================================================================================\\\

"""
Test suite for robust Lyapunov stability verification.

Validates GitHub Issue #11 resolution:
- Robust numerical stability for Lyapunov solver
- Integration with numerical_stability.py infrastructure
- Positive definiteness validation
- Handling of ill-conditioned matrices
"""

import pytest
import numpy as np
import warnings

from src.analysis.performance.stability_analysis import StabilityAnalyzer, StabilityAnalysisConfig


class TestLyapunovStabilityVerification:
    """Test robust Lyapunov solver implementation."""

    @pytest.fixture
    def analyzer(self):
        """Create stability analyzer with tight tolerance."""
        config = StabilityAnalysisConfig(eigenvalue_tolerance=1e-10)
        return StabilityAnalyzer(config=config)

    def test_stable_system_basic(self, analyzer):
        """Test Lyapunov analysis on a simple stable system."""
        # Stable system matrix (all eigenvalues have negative real parts)
        A = np.array([
            [-1.0, 0.5, 0.0],
            [0.0, -2.0, 1.0],
            [0.0, 0.0, -1.5]
        ])

        # Verify system is stable (eigenvalues have negative real parts)
        eigenvals = np.linalg.eigvals(A)
        assert np.all(np.real(eigenvals) < 0), "Test system should be stable"

        # Run Lyapunov analysis
        result = analyzer._analyze_analytical_lyapunov(A)

        # Validate results
        assert 'error' not in result, f"Lyapunov analysis failed: {result.get('error')}"
        assert result['is_positive_definite'], "P matrix should be positive definite"
        assert result['is_stable'], "System should be classified as stable"

        # Verify P eigenvalues are all positive (within tolerance)
        P_eigenvals = np.array(result['P_eigenvalues'])
        assert np.all(P_eigenvals > -1e-10), \
            f"P eigenvalues should be positive, got min: {np.min(P_eigenvals):.2e}"

        # Verify Lyapunov equation residual is small
        assert result['residual_relative'] < 1e-6, \
            f"Lyapunov residual too large: {result['residual_relative']:.2e}"

    def test_ill_conditioned_stable_system(self, analyzer):
        """Test Lyapunov solver with ill-conditioned but stable system."""
        # Create ill-conditioned stable system
        # Small eigenvalue spread causes high condition number
        A = np.array([
            [-1.0, 0.0, 0.0],
            [0.0, -0.01, 0.0],  # Much smaller eigenvalue
            [0.0, 0.0, -0.001]  # Even smaller
        ])

        cond_A = np.linalg.cond(A)
        print(f"\nCondition number of A: {cond_A:.2e}")

        # System should still be stable
        eigenvals = np.linalg.eigvals(A)
        assert np.all(np.real(eigenvals) < 0), "System should be stable"

        # Run Lyapunov analysis (should handle ill-conditioning gracefully)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = analyzer._analyze_analytical_lyapunov(A)

        # Validate results
        assert 'error' not in result, f"Analysis failed: {result.get('error')}"
        assert result['is_positive_definite'], "P should be positive definite despite ill-conditioning"

        # Check if regularization was applied (expected for high condition numbers)
        if cond_A > 1e12:
            assert result.get('regularization_applied', False), \
                "Regularization should be applied for extremely ill-conditioned systems"

    def test_unstable_system(self, analyzer):
        """Test that unstable systems are correctly identified."""
        # Unstable system (at least one positive eigenvalue)
        A = np.array([
            [1.0, 0.5, 0.0],   # Positive eigenvalue
            [0.0, -1.0, 0.0],
            [0.0, 0.0, -2.0]
        ])

        eigenvals = np.linalg.eigvals(A)
        assert np.any(np.real(eigenvals) > 0), "Test system should be unstable"

        # Run Lyapunov analysis
        result = analyzer._analyze_analytical_lyapunov(A)

        # For unstable systems, Lyapunov equation may not have positive definite solution
        # The solver should handle this gracefully
        if 'error' not in result:
            # If solver succeeded, it should identify instability
            assert not result['is_stable'] or not result['is_positive_definite'], \
                "Unstable system should not yield stable Lyapunov analysis"

    def test_marginally_stable_system(self, analyzer):
        """Test system on stability boundary (zero eigenvalue)."""
        # Marginally stable system (has zero eigenvalue)
        A = np.array([
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, -1.0]
        ])

        eigenvals = np.linalg.eigvals(A)
        assert np.any(np.abs(np.real(eigenvals)) < 1e-10), "Should have eigenvalue near zero"

        # Run Lyapunov analysis
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = analyzer._analyze_analytical_lyapunov(A)

        # Marginally stable systems may fail or produce borderline results
        # The key is that the solver doesn't crash
        if 'error' not in result:
            # Should handle gracefully, possibly with warnings
            print(f"Marginally stable system analysis: is_stable={result.get('is_stable')}")

    def test_lyapunov_derivative_negative(self, analyzer):
        """Test that Lyapunov derivative dV/dt < 0 for stable systems.

        This is the CORE validation for Issue #11:
        All Lyapunov derivatives must be negative (within tolerance 1e-10).
        """
        # Create a stable linear system
        A_stable = np.array([
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1],
            [-2, -1, 0, -1, 0, 0],
            [0, -3, -1, 0, -1, 0],
            [0, 0, -2, 0, 0, -1]
        ])

        # Verify stability
        eigenvals = np.linalg.eigvals(A_stable)
        assert np.all(np.real(eigenvals) < 0), "System must be stable"

        # Solve Lyapunov equation
        result = analyzer._analyze_analytical_lyapunov(A_stable)
        assert 'error' not in result, f"Lyapunov solver failed: {result.get('error')}"
        assert result['is_positive_definite'], "P must be positive definite"

        # Extract P matrix
        P = np.array(result['lyapunov_matrix_P'])

        # Compute Lyapunov derivative: dV/dt = x^T (A^T P + P A) x
        # For stability: A^T P + P A = -Q must be negative definite
        # This means A^T P + P A should have all negative eigenvalues
        M = A_stable.T @ P + P @ A_stable

        # M should be negative definite (all eigenvalues < 0)
        eigenvals_M = np.linalg.eigvals(M)
        real_parts_M = np.real(eigenvals_M)

        print(f"\nLyapunov derivative matrix eigenvalues: {real_parts_M}")

        # CRITICAL ASSERTION (Issue #11 core requirement)
        # All eigenvalues of M must be negative (within tolerance)
        tolerance = 1e-10
        max_eigenval = np.max(real_parts_M)

        assert max_eigenval < tolerance, \
            f"Lyapunov derivative has positive eigenvalue: {max_eigenval:.2e} (tolerance: {tolerance:.2e})"

        # Verify that most eigenvalues are significantly negative
        num_negative = np.sum(real_parts_M < -tolerance)
        assert num_negative >= len(real_parts_M) - 1, \
            "Most eigenvalues should be significantly negative"

    def test_large_system_performance(self, analyzer):
        """Test performance on larger systems."""
        # Create a 10x10 stable system
        n = 10
        np.random.seed(42)

        # Generate random stable matrix
        A = np.random.randn(n, n)
        # Make it stable by ensuring negative real eigenvalues
        A = A - np.eye(n) * (np.max(np.real(np.linalg.eigvals(A))) + 2.0)

        # Verify stability
        eigenvals = np.linalg.eigvals(A)
        assert np.all(np.real(eigenvals) < 0), "System should be stable"

        # Time the analysis
        import time
        start = time.perf_counter()
        result = analyzer._analyze_analytical_lyapunov(A)
        elapsed = time.perf_counter() - start

        print(f"\nLarge system ({n}x{n}) analysis time: {elapsed:.4f}s")

        # Validate results
        assert 'error' not in result, f"Large system analysis failed: {result.get('error')}"
        assert result['is_positive_definite'], "P should be positive definite"

        # Performance requirement: Should complete in reasonable time
        assert elapsed < 1.0, f"Analysis too slow: {elapsed:.4f}s (target: <1.0s)"

    def test_cholesky_decomposition_success(self, analyzer):
        """Test that Cholesky decomposition succeeds for stable systems."""
        # Stable system with good conditioning
        A = np.array([
            [-2.0, 1.0, 0.0],
            [0.0, -1.5, 0.5],
            [0.0, 0.0, -1.0]
        ])

        result = analyzer._analyze_analytical_lyapunov(A)
        assert 'error' not in result, f"Analysis failed: {result.get('error')}"
        assert result['is_positive_definite'], "P should be positive definite"

        # Manually verify Cholesky succeeds
        P = np.array(result['lyapunov_matrix_P'])
        P_sym = 0.5 * (P + P.T)  # Symmetrize

        try:
            np.linalg.cholesky(P_sym)
            cholesky_succeeded = True
        except np.linalg.LinAlgError:
            cholesky_succeeded = False

        assert cholesky_succeeded, "Cholesky decomposition should succeed for stable system"

    def test_svd_fallback_mechanism(self, analyzer):
        """Test that SVD fallback works for difficult cases."""
        # Create a system that might challenge the direct solver
        A = np.array([
            [-1.0, 1e-6, 0.0],
            [1e-6, -1.0, 1e-6],
            [0.0, 1e-6, -1.0]
        ])

        # Force fallback by creating conditions where direct solver might struggle
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = analyzer._analyze_analytical_lyapunov(A)

        # Should succeed even if fallback is triggered
        assert 'error' not in result, f"SVD fallback failed: {result.get('error')}"
        assert result['is_positive_definite'], "Should achieve positive definite solution"

    def test_residual_validation(self, analyzer):
        """Test that Lyapunov equation residual is properly validated."""
        A = np.array([
            [-1.0, 0.0, 0.0],
            [0.0, -2.0, 0.0],
            [0.0, 0.0, -3.0]
        ])

        result = analyzer._analyze_analytical_lyapunov(A)
        assert 'error' not in result

        # Check residual fields exist
        assert 'residual_norm' in result
        assert 'residual_relative' in result

        # Residual should be small
        assert result['residual_norm'] < 1e-6, \
            f"Residual norm too large: {result['residual_norm']:.2e}"
        assert result['residual_relative'] < 1e-6, \
            f"Relative residual too large: {result['residual_relative']:.2e}"

        # Manually verify residual calculation
        P = np.array(result['lyapunov_matrix_P'])
        Q = np.eye(A.shape[0])
        residual = A.T @ P + P @ A + Q
        manual_residual_norm = np.linalg.norm(residual, ord='fro')

        assert np.abs(manual_residual_norm - result['residual_norm']) < 1e-10, \
            "Residual calculation mismatch"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])