# ==============================================================================
# tests/test_simulation/integrators/conftest.py
#
# Shared fixtures for integrator testing
#
# Provides standard test problems with analytical solutions for validating
# numerical integration accuracy and convergence order.
# ==============================================================================

import numpy as np
import pytest
from typing import Callable, Tuple


# ==============================================================================
# Standard Test Problems with Analytical Solutions
# ==============================================================================

@pytest.fixture
def linear_decay():
    """
    Linear ODE: dx/dt = -k*x with analytical solution x(t) = x0*exp(-k*t).

    Good for testing:
    - Order of accuracy (convergence studies)
    - Basic integration correctness
    - Simple non-stiff system

    Returns
    -------
    tuple[Callable, Callable]
        (dynamics_fn, analytical_solution)
    """
    k = 0.5  # Decay rate

    def dynamics(t: float, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        """Dynamics: dx/dt = -k*x"""
        return -k * x

    def solution(t: float, x0: np.ndarray) -> np.ndarray:
        """Analytical solution: x(t) = x0 * exp(-k*t)"""
        return x0 * np.exp(-k * t)

    return dynamics, solution


@pytest.fixture
def harmonic_oscillator():
    """
    Harmonic oscillator: dx/dt = [v; -x] with solution [cos(t), -sin(t)].

    Good for testing:
    - Energy conservation properties
    - Multi-dimensional systems
    - Oscillatory behavior
    - Long-term integration accuracy

    Returns
    -------
    tuple[Callable, Callable]
        (dynamics_fn, analytical_solution)
    """
    def dynamics(t: float, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        """
        Dynamics: [x_dot, v_dot] = [v, -x]
        Simple harmonic oscillator with omega = 1
        """
        return np.array([x[1], -x[0]])

    def solution(t: float, x0: np.ndarray) -> np.ndarray:
        """
        Analytical solution for [x0, v0] = [1, 0]:
        x(t) = x0*cos(t) + v0*sin(t)
        v(t) = -x0*sin(t) + v0*cos(t)
        """
        return np.array([
            x0[0] * np.cos(t) + x0[1] * np.sin(t),
            -x0[0] * np.sin(t) + x0[1] * np.cos(t)
        ])

    return dynamics, solution


@pytest.fixture
def exponential_growth():
    """
    Exponential growth: dx/dt = lambda*x with solution x(t) = x0*exp(lambda*t).

    Good for testing:
    - Unstable systems
    - Growth behavior
    - Adaptive step size control (for adaptive integrators)

    Returns
    -------
    tuple[Callable, Callable, float]
        (dynamics_fn, analytical_solution, lambda_value)
    """
    lambda_val = 2.0  # Growth rate

    def dynamics(t: float, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        """Dynamics: dx/dt = lambda*x"""
        return lambda_val * x

    def solution(t: float, x0: np.ndarray) -> np.ndarray:
        """Analytical solution: x(t) = x0 * exp(lambda*t)"""
        return x0 * np.exp(lambda_val * t)

    return dynamics, solution, lambda_val


@pytest.fixture
def stiff_system():
    """
    Stiff system: dx/dt = A*x with eigenvalues [-100, -1].

    Good for testing:
    - Implicit methods (BackwardEuler)
    - Adaptive step size control
    - Stability properties
    - Different time scales

    Returns
    -------
    tuple[Callable, Callable, np.ndarray]
        (dynamics_fn, analytical_solution, eigenvalues)
    """
    # System matrix with stiff eigenvalues
    A = np.array([[-100.0, 0.0],
                  [0.0, -1.0]])
    eigenvalues = np.array([-100.0, -1.0])

    def dynamics(t: float, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        """Dynamics: dx/dt = A*x"""
        return A @ x

    def solution(t: float, x0: np.ndarray) -> np.ndarray:
        """
        Analytical solution: x(t) = expm(A*t) @ x0
        For diagonal A: x_i(t) = x0_i * exp(lambda_i * t)
        """
        return np.array([
            x0[0] * np.exp(-100.0 * t),
            x0[1] * np.exp(-1.0 * t)
        ])

    return dynamics, solution, eigenvalues


@pytest.fixture
def controlled_system():
    """
    Simple controlled system: dx/dt = A*x + B*u.

    Good for testing:
    - Control input handling
    - Linear systems with inputs
    - Zero-order hold discretization

    Returns
    -------
    tuple[np.ndarray, np.ndarray, Callable]
        (A_matrix, B_matrix, dynamics_fn)
    """
    # Simple 2x2 system
    A = np.array([[0.0, 1.0],
                  [-2.0, -3.0]])
    B = np.array([[0.0],
                  [1.0]])

    def dynamics(t: float, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        """Dynamics: dx/dt = A*x + B*u"""
        u_val = u[0] if hasattr(u, '__len__') else u
        return A @ x + B.flatten() * u_val

    return A, B, dynamics


@pytest.fixture
def nonlinear_pendulum():
    """
    Nonlinear pendulum: dx/dt = [v; -sin(theta) - damping*v + u].

    Good for testing:
    - Nonlinear dynamics
    - Trigonometric functions
    - Damping effects
    - Control inputs

    Returns
    -------
    Callable
        dynamics_fn(t, x, u) -> dx/dt
    """
    damping = 0.1

    def dynamics(t: float, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        """
        Nonlinear pendulum dynamics
        x = [theta, theta_dot]
        dx/dt = [theta_dot, -sin(theta) - damping*theta_dot + u]
        """
        theta, theta_dot = x[0], x[1]
        u_val = u[0] if hasattr(u, '__len__') else u

        return np.array([
            theta_dot,
            -np.sin(theta) - damping * theta_dot + u_val
        ])

    return dynamics


# ==============================================================================
# Helper Functions for Testing
# ==============================================================================

def compute_convergence_order(dts: list, errors: list) -> float:
    """
    Compute numerical order of convergence from error vs timestep data.

    For an order-p method: error ~ dt^p
    So log(error) ~ p*log(dt), meaning slope of log-log plot gives order.

    Parameters
    ----------
    dts : list
        List of timesteps (must be sorted largest to smallest)
    errors : list
        List of corresponding errors

    Returns
    -------
    float
        Estimated convergence order
    """
    log_dts = np.log(dts)
    log_errors = np.log(errors)

    # Fit linear regression: log(error) = p*log(dt) + c
    # Slope gives order p
    slopes = []
    for i in range(len(dts) - 1):
        slope = (log_errors[i+1] - log_errors[i]) / (log_dts[i+1] - log_dts[i])
        slopes.append(slope)

    return np.mean(slopes)


def compute_global_error(integrator, dynamics, x0, t_final, dt, analytical_solution):
    """
    Compute global error by integrating to t_final and comparing to exact solution.

    Parameters
    ----------
    integrator : BaseIntegrator
        Integrator instance to test
    dynamics : Callable
        Dynamics function(t, x, u) -> dx/dt
    x0 : np.ndarray
        Initial state
    t_final : float
        Final time
    dt : float
        Timestep
    analytical_solution : Callable
        Function(t, x0) -> x(t)

    Returns
    -------
    float
        L2 norm of global error at t_final
    """
    state = x0.copy()
    t = 0.0
    control = np.array([0.0])

    num_steps = int(t_final / dt)

    for _ in range(num_steps):
        state = integrator.integrate(dynamics, state, control, dt)
        t += dt

    exact = analytical_solution(t_final, x0)
    error = np.linalg.norm(state - exact)

    return error


def integrate_trajectory(integrator, dynamics, x0, t_final, dt, u=None):
    """
    Integrate a full trajectory and return time/state arrays.

    Parameters
    ----------
    integrator : BaseIntegrator
        Integrator instance
    dynamics : Callable
        Dynamics function
    x0 : np.ndarray
        Initial state
    t_final : float
        Final time
    dt : float
        Timestep
    u : np.ndarray or float, optional
        Control input (default: 0)

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        (time_array, state_array)
    """
    if u is None:
        u = np.array([0.0])
    elif not isinstance(u, np.ndarray):
        u = np.array([u])

    num_steps = int(t_final / dt)
    times = np.linspace(0, t_final, num_steps + 1)
    states = np.zeros((num_steps + 1, len(x0)))

    states[0] = x0

    for i in range(num_steps):
        states[i+1] = integrator.integrate(dynamics, states[i], u, dt)

    return times, states


# ==============================================================================
# Test Data Generators
# ==============================================================================

@pytest.fixture
def convergence_test_timesteps():
    """Standard timesteps for convergence studies."""
    return [0.1, 0.05, 0.025, 0.0125, 0.00625]


@pytest.fixture
def test_initial_conditions():
    """Standard initial conditions for various test problems."""
    return {
        'scalar': np.array([1.0]),
        'vector_2d': np.array([1.0, 0.0]),
        'vector_4d': np.array([0.1, 0.0, 0.05, 0.0]),
        'oscillator': np.array([1.0, 0.0]),  # Position, velocity
        'stiff': np.array([1.0, 1.0]),  # For stiff system
    }


# ==============================================================================
# Tolerance Constants
# ==============================================================================

# Standard tolerances for adaptive integrators
RTOL_DEFAULT = 1e-6
ATOL_DEFAULT = 1e-9

# Tolerances for convergence testing
CONVERGENCE_RTOL = 0.3  # Allow 30% deviation in convergence order

# Tolerances for numerical comparisons
NUMERICAL_RTOL = 1e-10
NUMERICAL_ATOL = 1e-12
