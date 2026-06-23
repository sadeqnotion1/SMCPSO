#==========================================================================================\\\
#================= scripts/optimization/diagnose_classical_chattering.py =================\\\
#==========================================================================================\\\

"""
Diagnostic tool for classical SMC chattering investigation.
Analyzes why classical_smc has cost=533 while adaptive/sta have cost=1-2.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from scipy.fft import fft, fftfreq  # noqa: E402

from src.config import load_config  # noqa: E402
from src.controllers.factory import create_controller  # noqa: E402
from src.plant.models.dynamics import DoubleInvertedPendulum  # noqa: E402


def simulate_controller(controller_type: str, gains: list, dt: float = 0.01, t_sim: float = 15.0):
    """Simulate controller and return detailed diagnostics."""

    config = load_config('config.yaml', allow_unknown=False)

    # Update gains
    temp_config = config.model_copy(deep=True)
    if hasattr(temp_config.controller_defaults, controller_type):
        default_ctrl = getattr(temp_config.controller_defaults, controller_type)
        updated = default_ctrl.model_copy(update={'gains': gains})
        setattr(temp_config.controller_defaults, controller_type, updated)

    if hasattr(temp_config.controllers, controller_type):
        ctrl = getattr(temp_config.controllers, controller_type)
        updated = ctrl.model_copy(update={'gains': gains})
        setattr(temp_config.controllers, controller_type, updated)

    # Create controller and dynamics
    controller = create_controller(controller_type=controller_type, config=temp_config)
    dynamics = DoubleInvertedPendulum(config=config.physics)

    # Initialize
    state_vars = controller.initialize_state() if hasattr(controller, 'initialize_state') else ()
    history = controller.initialize_history() if hasattr(controller, 'initialize_history') else {}

    # Initial state (small disturbance)
    state = np.array([0.0, 0.02, 0.02, 0.0, 0.0, 0.0])

    n_steps = int(t_sim / dt)
    t_hist = np.zeros(n_steps)
    state_hist = np.zeros((n_steps, 6))
    control_hist = np.zeros(n_steps)

    # Simulate
    for i in range(n_steps):
        t_hist[i] = i * dt
        state_hist[i] = state

        # Compute control
        try:
            result = controller.compute_control(state, state_vars, history)

            if hasattr(result, 'u'):
                control_output = result.u
                state_vars = getattr(result, 'state', state_vars)
                history = getattr(result, 'history', history)
            elif isinstance(result, (int, float)):
                control_output = float(result)
            elif isinstance(result, tuple):
                control_output = float(result[0])
                if len(result) > 1:
                    state_vars = result[1]
                if len(result) > 2:
                    history = result[2]
            else:
                control_output = float(result)

        except Exception as e:
            print(f"Control failed at step {i}: {e}")
            break

        control_hist[i] = control_output

        # Update dynamics
        state = dynamics.sanitize_state(state)
        dyn_result = dynamics.compute_dynamics(state, np.array([control_output]))

        if dyn_result.success:
            state = state + dyn_result.state_derivative * dt
            if np.any(np.abs(state) > 1e3) or not np.all(np.isfinite(state)):
                print(f"Simulation diverged at step {i}")
                break
        else:
            print(f"Dynamics failed at step {i}")
            break

    return t_hist, state_hist, control_hist


def compute_chattering_metrics(t, control):
    """Compute detailed chattering metrics."""
    dt = t[1] - t[0]

    # Time domain: control derivative RMS
    control_deriv = np.gradient(control, dt)
    time_domain_index = np.sqrt(np.mean(control_deriv**2))

    # Frequency domain: high-frequency power
    spectrum = np.abs(fft(control))
    freqs = fftfreq(len(control), d=dt)
    hf_mask = np.abs(freqs) > 10.0
    hf_power = np.sum(spectrum[hf_mask]) if np.any(hf_mask) else 0.0
    total_power = np.sum(spectrum) + 1e-12
    freq_domain_index = hf_power / total_power

    # Combined chattering index
    chattering_index = 0.7 * time_domain_index + 0.3 * freq_domain_index

    # Total variation (control changes)
    total_variation = np.sum(np.abs(np.diff(control)))

    return {
        'chattering_index': chattering_index,
        'time_domain_index': time_domain_index,
        'freq_domain_index': freq_domain_index,
        'total_variation': total_variation,
        'control_deriv_max': np.max(np.abs(control_deriv)),
        'control_deriv_std': np.std(control_deriv)
    }


def main():
    print("="*80)
    print("CLASSICAL SMC CHATTERING DIAGNOSTIC")
    print("="*80)
    print()

    # PSO best gains for each controller
    controllers = {
        'classical_smc': [16.11, 2.79, 2.72, 4.52, 16.94, 2.96],
        'adaptive_smc': [3.39, 9.77, 7.01, 1.70, 0.78],  # Approximate from logs
        'sta_smc': [25.0, 15.0, 20.0, 12.0, 8.0, 6.0]     # Approximate from logs
    }

    results = {}

    for ctrl_name, gains in controllers.items():
        print(f"Simulating {ctrl_name}...")

        try:
            t, state, control = simulate_controller(ctrl_name, gains)
            metrics = compute_chattering_metrics(t, control)

            # Tracking error
            tracking_rms = np.sqrt(np.mean(state[:, 1:3]**2))

            results[ctrl_name] = {
                't': t,
                'state': state,
                'control': control,
                'metrics': metrics,
                'tracking_rms': tracking_rms
            }

            print(f"  Chattering index: {metrics['chattering_index']:.2f}")
            print(f"  Time domain: {metrics['time_domain_index']:.2f}")
            print(f"  Freq domain: {metrics['freq_domain_index']:.4f}")
            print(f"  Total variation: {metrics['total_variation']:.1f}")
            print(f"  Max control deriv: {metrics['control_deriv_max']:.1f}")
            print(f"  Tracking RMS: {tracking_rms:.4f}")
            print()

        except Exception as e:
            print(f"  ERROR: {e}")
            print()

    # Generate comparison plots
    if len(results) >= 2:
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))

        colors = {'classical_smc': '#e74c3c', 'adaptive_smc': '#2ecc71', 'sta_smc': '#3498db'}

        for ctrl_name, data in results.items():
            t = data['t']
            control = data['control']
            state = data['state']

            # Control signal
            axes[0].plot(t, control, label=f"{ctrl_name} (chat={data['metrics']['chattering_index']:.1f})",
                        color=colors.get(ctrl_name, 'gray'), linewidth=1.5)

            # Control derivative
            control_deriv = np.gradient(control, t[1]-t[0])
            axes[1].plot(t, control_deriv, label=ctrl_name, color=colors.get(ctrl_name, 'gray'), linewidth=1.5)

            # Pendulum angles
            axes[2].plot(t, state[:, 1], label=f"{ctrl_name} θ1", color=colors.get(ctrl_name, 'gray'),
                        linestyle='-', linewidth=1.5)
            axes[2].plot(t, state[:, 2], label=f"{ctrl_name} θ2", color=colors.get(ctrl_name, 'gray'),
                        linestyle='--', linewidth=1.5, alpha=0.7)

        axes[0].set_ylabel('Control Force (N)', fontweight='bold')
        axes[0].set_title('Control Signal Comparison', fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        axes[1].set_ylabel('Control Derivative (N/s)', fontweight='bold')
        axes[1].set_title('Control Derivative (Chattering Indicator)', fontweight='bold')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        axes[2].set_xlabel('Time (s)', fontweight='bold')
        axes[2].set_ylabel('Angle (rad)', fontweight='bold')
        axes[2].set_title('Pendulum Angles', fontweight='bold')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        output_file = 'docs/analysis/classical_smc_chattering_diagnosis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"[OK] Saved diagnostic plot: {output_file}")
        plt.close()

    # Generate summary report
    print("="*80)
    print("DIAGNOSTIC SUMMARY")
    print("="*80)
    print()
    print("Key Findings:")
    print()

    if 'classical_smc' in results and 'adaptive_smc' in results:
        classical_chat = results['classical_smc']['metrics']['chattering_index']
        adaptive_chat = results['adaptive_smc']['metrics']['chattering_index']
        ratio = classical_chat / adaptive_chat if adaptive_chat > 0 else float('inf')

        print(f"1. Classical SMC chattering is {ratio:.1f}x higher than adaptive SMC")
        print(f"   - Classical: {classical_chat:.2f}")
        print(f"   - Adaptive: {adaptive_chat:.2f}")
        print()

        classical_deriv_std = results['classical_smc']['metrics']['control_deriv_std']
        adaptive_deriv_std = results['adaptive_smc']['metrics']['control_deriv_std']

        print("2. Control derivative STD comparison:")
        print(f"   - Classical: {classical_deriv_std:.2f} N/s")
        print(f"   - Adaptive: {adaptive_deriv_std:.2f} N/s")
        print()

        print("3. Likely causes:")
        print("   - Classical SMC with boundary layer still produces discrete switching")
        print("   - Adaptive SMC smoothly adjusts gains → smoother control")
        print("   - STA-SMC uses continuous higher-order sliding → reduced chattering")


if __name__ == '__main__':
    main()