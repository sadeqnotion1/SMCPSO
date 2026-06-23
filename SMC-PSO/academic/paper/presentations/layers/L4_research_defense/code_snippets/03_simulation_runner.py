# ============================================================================
# Simulation Runner: Core Control Loop
# ============================================================================
# Demonstrates the main simulation loop integrating controller + dynamics

import numpy as np
from scipy.integrate import solve_ivp


def run_simulation(controller, dynamics, initial_state, dt=0.01, duration=10.0):
    """
    Run closed-loop simulation of double-inverted pendulum.

    Parameters:
        controller: Controller object with compute_control() method
        dynamics: Dynamics object with compute_derivatives() method
        initial_state: [theta1, theta1_dot, theta2, theta2_dot] initial angles/velocities
        dt: Time step for control updates (seconds)
        duration: Total simulation time (seconds)

    Returns:
        times: Array of time points
        states: Array of states at each time point (N x 4)
        controls: Array of control forces at each time point
    """
    # Time array
    t_eval = np.arange(0, duration, dt)
    n_steps = len(t_eval)

    # Preallocate storage
    states = np.zeros((n_steps, 4))
    controls = np.zeros(n_steps)

    # Initial conditions
    states[0] = initial_state
    last_control = 0.0

    # Simulation loop
    for i in range(n_steps - 1):
        t_current = t_eval[i]
        state_current = states[i]

        # Compute control force from controller
        u = controller.compute_control(
            state=state_current,
            last_control=last_control,
            history=None  # Optional history for adaptive controllers
        )
        controls[i] = u

        # Integrate dynamics forward one time step using RK4
        def dynamics_func(t, x):
            return dynamics.compute_derivatives(x, u)

        sol = solve_ivp(
            dynamics_func,
            t_span=(t_current, t_current + dt),
            y0=state_current,
            method='RK45',
            dense_output=False
        )

        # Store next state
        states[i + 1] = sol.y[:, -1]
        last_control = u

    # Compute final control
    controls[-1] = controller.compute_control(
        state=states[-1],
        last_control=controls[-2],
        history=None
    )

    return t_eval, states, controls


# Example usage
if __name__ == "__main__":
    from src.controllers.factory import create_controller
    from src.plant.dynamics import FullDynamics

    # Create controller
    controller = create_controller(
        'classical_smc',
        gains=[10.0, 5.0, 8.0, 3.0, 15.0, 0.05]
    )

    # Create dynamics model
    dynamics = FullDynamics()

    # Initial state: small perturbation
    initial_state = np.array([0.1, 0.0, 0.05, 0.0])

    # Run simulation
    print("[INFO] Running simulation...")
    times, states, controls = run_simulation(
        controller,
        dynamics,
        initial_state,
        dt=0.01,
        duration=5.0
    )

    # Analyze results
    final_error = np.linalg.norm(states[-1])
    max_control = np.max(np.abs(controls))

    print(f"[OK] Simulation complete!")
    print(f"Final tracking error: {final_error:.6f} rad")
    print(f"Maximum control effort: {max_control:.3f} N")
