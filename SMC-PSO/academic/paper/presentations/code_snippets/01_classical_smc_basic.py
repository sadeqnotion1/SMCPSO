# ============================================================================
# Classical SMC: Basic Control Law
# ============================================================================
# Demonstrates the core sliding mode control computation with boundary layer

import numpy as np

def compute_control_classical_smc(state, gains, epsilon=0.05, K=10.0):
    """
    Classical SMC control law with boundary layer.

    Parameters:
        state: [theta1, theta1_dot, theta2, theta2_dot] - Current state
        gains: [k1, k2, lambda1, lambda2] - Sliding surface gains
        epsilon: Boundary layer thickness (chattering reduction)
        K: Control gain (reaching speed)

    Returns:
        u: Control force
    """
    # Unpack state
    theta1, theta1_dot, theta2, theta2_dot = state
    k1, k2, lambda1, lambda2 = gains

    # Compute sliding surface
    s = k1 * theta1 + k2 * theta1_dot + lambda1 * theta2 + lambda2 * theta2_dot

    # Boundary layer control (continuous approximation of sign function)
    u = -K * np.tanh(s / epsilon)

    # Actuator saturation
    u_max = 20.0  # Maximum force (Newtons)
    u = np.clip(u, -u_max, u_max)

    return u


# Example usage
if __name__ == "__main__":
    # Initial state: small perturbation from upright equilibrium
    state = np.array([0.1, 0.0, 0.05, 0.0])  # [theta1, dot, theta2, dot] in radians

    # Sliding surface gains (tuned via PSO)
    gains = np.array([10.0, 5.0, 8.0, 3.0])

    # Compute control force
    u = compute_control_classical_smc(state, gains, epsilon=0.05, K=10.0)

    print(f"State: {state}")
    print(f"Control force: {u:.3f} N")
