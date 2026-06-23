#======================================================================================\\\
#============================ test_overshoot_comparison.py ============================\\\
#======================================================================================\\\

"""
Direct overshoot comparison test for Issue #2 STA-SMC parameter optimization.
Bypasses complex configuration and directly tests old vs new parameters.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_overshoot_comparison():
    """Compare overshoot between original and optimized STA-SMC parameters."""

    try:
        # Import necessary components
        from src.controllers.smc.sta_smc import SuperTwistingSMC
        from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics
        from src.plant.models.simplified.config import SimplifiedDIPConfig

        print("Testing STA-SMC Overshoot Comparison")
        print("="*60)

        # Configure simplified physics (bypass validation issues)
        physics_config = {
            'cart_mass': 1.5,
            'pendulum1_mass': 0.2,
            'pendulum2_mass': 0.15,
            'pendulum1_length': 0.4,
            'pendulum2_length': 0.3,
            'pendulum1_com': 0.2,
            'pendulum2_com': 0.15,
            'pendulum1_inertia': 0.0081,  # Increased to meet validation
            'pendulum2_inertia': 0.0035,  # Increased to meet validation
            'gravity': 9.81,
            'cart_friction': 0.1,
            'joint1_friction': 0.001,
            'joint2_friction': 0.001
        }

        # Create dynamics model
        dip_config = SimplifiedDIPConfig.from_dict(physics_config)
        dynamics = SimplifiedDIPDynamics(dip_config)

        # Test parameters
        dt = 0.01
        duration = 5.0
        time_steps = int(duration / dt)
        initial_state = np.array([0.0, 0.1, 0.05, 0.0, 0.0, 0.0])  # Small disturbance

        # Original problematic parameters
        original_gains = [15.0, 8.0, 12.0, 6.0, 20.0, 4.0]
        original_boundary = 0.01

        # New optimized parameters
        optimized_gains = [8.0, 4.0, 12.0, 6.0, 1.2, 0.8]
        optimized_boundary = 0.05

        print(f"Original gains:  {original_gains}")
        print(f"Optimized gains: {optimized_gains}")
        print(f"Original boundary layer: {original_boundary}")
        print(f"Optimized boundary layer: {optimized_boundary}")
        print()

        # Test both configurations
        results = {}

        for name, gains, boundary in [
            ('original', original_gains, original_boundary),
            ('optimized', optimized_gains, optimized_boundary)
        ]:
            print(f"Testing {name} configuration...")

            # Create controller
            controller = SuperTwistingSMC(
                gains=gains,
                dt=dt,
                max_force=150.0,
                damping_gain=0.0,
                boundary_layer=boundary,
                dynamics_model=dynamics
            )

            # Initialize simulation
            state = initial_state.copy()
            controller_state = controller.initialize_state()
            history = controller.initialize_history()

            # Storage arrays
            time_array = np.linspace(0, duration, time_steps)
            states = np.zeros((time_steps, 6))
            controls = np.zeros(time_steps)

            # Simulation loop
            for i in range(time_steps):
                states[i] = state

                # Compute control
                result = controller.compute_control(state, controller_state, history)
                control = result.u
                controller_state = result.state
                controls[i] = control

                # Integrate dynamics (simple Euler for now)
                control_array = np.array([control])  # Convert to array
                dynamics_result = dynamics.compute_dynamics(state, control_array)
                # Extract the state derivative (first element is usually the derivative)
                if hasattr(dynamics_result, '__iter__') and len(dynamics_result) > 0:
                    state_dot = dynamics_result[0] if isinstance(dynamics_result[0], np.ndarray) else np.array(dynamics_result[0])
                else:
                    state_dot = np.array(dynamics_result)
                state = state + state_dot * dt

            # Analyze results
            theta1 = states[:, 1]  # Pendulum 1 angle
            theta2 = states[:, 2]  # Pendulum 2 angle

            # Find peaks and overshoot
            theta1_peak = np.max(np.abs(theta1))
            theta2_peak = np.max(np.abs(theta2))

            # Settling time (when |theta| < 0.02 and stays there)
            settling_tolerance = 0.02
            combined_angle = np.sqrt(theta1**2 + theta2**2)
            settled_indices = np.where(combined_angle < settling_tolerance)[0]

            if len(settled_indices) > 0:
                # Find the last time it exceeded tolerance and add buffer
                last_excursion = 0
                for i in range(len(combined_angle)-1):
                    if combined_angle[i] >= settling_tolerance:
                        last_excursion = i

                # Look for continuous settling after last excursion
                settling_time = duration  # Default if never settles
                for i in range(last_excursion, len(combined_angle)-10):
                    if np.all(combined_angle[i:i+10] < settling_tolerance):
                        settling_time = time_array[i]
                        break
            else:
                settling_time = duration

            # Overshoot percentage (relative to initial disturbance)
            initial_theta1 = abs(initial_state[1])
            initial_theta2 = abs(initial_state[2])
            overshoot1_pct = ((theta1_peak - initial_theta1) / initial_theta1) * 100 if initial_theta1 > 0 else 0
            overshoot2_pct = ((theta2_peak - initial_theta2) / initial_theta2) * 100 if initial_theta2 > 0 else 0

            # RMS control effort
            rms_control = np.sqrt(np.mean(controls**2))

            results[name] = {
                'theta1_peak': theta1_peak,
                'theta2_peak': theta2_peak,
                'overshoot1_pct': overshoot1_pct,
                'overshoot2_pct': overshoot2_pct,
                'settling_time': settling_time,
                'rms_control': rms_control,
                'time': time_array,
                'theta1': theta1,
                'theta2': theta2,
                'control': controls
            }

            print(f"  Peak |θ1|: {theta1_peak:.4f} rad ({theta1_peak*180/np.pi:.2f} deg)")
            print(f"  Peak |θ2|: {theta2_peak:.4f} rad ({theta2_peak*180/np.pi:.2f} deg)")
            print(f"  Overshoot θ1: {overshoot1_pct:.1f}%")
            print(f"  Overshoot θ2: {overshoot2_pct:.1f}%")
            print(f"  Settling time: {settling_time:.2f} s")
            print(f"  RMS control: {rms_control:.2f} N")
            print()

        # Generate comparison report
        print("OVERSHOOT COMPARISON RESULTS")
        print("="*60)

        orig = results['original']
        opt = results['optimized']

        print("Metric                Original    Optimized    Improvement")
        print("-" * 55)
        print(f"Peak θ1 (deg)        {orig['theta1_peak']*180/np.pi:8.2f}    {opt['theta1_peak']*180/np.pi:8.2f}    {((orig['theta1_peak']-opt['theta1_peak'])/orig['theta1_peak']*100):6.1f}%")
        print(f"Peak θ2 (deg)        {orig['theta2_peak']*180/np.pi:8.2f}    {opt['theta2_peak']*180/np.pi:8.2f}    {((orig['theta2_peak']-opt['theta2_peak'])/orig['theta2_peak']*100):6.1f}%")
        print(f"Overshoot θ1 (%)     {orig['overshoot1_pct']:8.1f}    {opt['overshoot1_pct']:8.1f}    {orig['overshoot1_pct']-opt['overshoot1_pct']:6.1f}pp")
        print(f"Overshoot θ2 (%)     {orig['overshoot2_pct']:8.1f}    {opt['overshoot2_pct']:8.1f}    {orig['overshoot2_pct']-opt['overshoot2_pct']:6.1f}pp")
        print(f"Settling time (s)    {orig['settling_time']:8.2f}    {opt['settling_time']:8.2f}    {((orig['settling_time']-opt['settling_time'])/orig['settling_time']*100):6.1f}%")
        print(f"RMS control (N)      {orig['rms_control']:8.2f}    {opt['rms_control']:8.2f}    {((orig['rms_control']-opt['rms_control'])/orig['rms_control']*100):6.1f}%")

        # Create plots
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('STA-SMC Parameter Optimization Results - Issue #2')

        # Pendulum angles
        axes[0,0].plot(orig['time'], orig['theta1']*180/np.pi, 'r-', label='Original θ1', linewidth=2)
        axes[0,0].plot(opt['time'], opt['theta1']*180/np.pi, 'b-', label='Optimized θ1', linewidth=2)
        axes[0,0].set_ylabel('Pendulum 1 Angle (deg)')
        axes[0,0].grid(True)
        axes[0,0].legend()

        axes[0,1].plot(orig['time'], orig['theta2']*180/np.pi, 'r-', label='Original θ2', linewidth=2)
        axes[0,1].plot(opt['time'], opt['theta2']*180/np.pi, 'b-', label='Optimized θ2', linewidth=2)
        axes[0,1].set_ylabel('Pendulum 2 Angle (deg)')
        axes[0,1].grid(True)
        axes[0,1].legend()

        # Control signals
        axes[1,0].plot(orig['time'], orig['control'], 'r-', label='Original', linewidth=2)
        axes[1,0].plot(opt['time'], opt['control'], 'b-', label='Optimized', linewidth=2)
        axes[1,0].set_xlabel('Time (s)')
        axes[1,0].set_ylabel('Control Force (N)')
        axes[1,0].grid(True)
        axes[1,0].legend()

        # Combined angle magnitude
        orig_combined = np.sqrt(orig['theta1']**2 + orig['theta2']**2) * 180/np.pi
        opt_combined = np.sqrt(opt['theta1']**2 + opt['theta2']**2) * 180/np.pi

        axes[1,1].plot(orig['time'], orig_combined, 'r-', label='Original ||θ||', linewidth=2)
        axes[1,1].plot(opt['time'], opt_combined, 'b-', label='Optimized ||θ||', linewidth=2)
        axes[1,1].axhline(y=settling_tolerance*180/np.pi, color='k', linestyle='--', alpha=0.5, label='Settling threshold')
        axes[1,1].set_xlabel('Time (s)')
        axes[1,1].set_ylabel('Combined Angle Magnitude (deg)')
        axes[1,1].grid(True)
        axes[1,1].legend()

        plt.tight_layout()
        plt.savefig('sta_smc_overshoot_comparison.png', dpi=150, bbox_inches='tight')
        plt.show()

        # Success assessment
        overshoot_reduction = orig['overshoot1_pct'] - opt['overshoot1_pct']
        settling_improvement = (orig['settling_time'] - opt['settling_time']) / orig['settling_time'] * 100

        print("\nISSUE #2 RESOLUTION ASSESSMENT:")
        print("="*60)
        if overshoot_reduction > 5:
            print(f"✅ OVERSHOOT SIGNIFICANTLY REDUCED: {overshoot_reduction:.1f} percentage points")
        elif overshoot_reduction > 0:
            print(f"✅ OVERSHOOT REDUCED: {overshoot_reduction:.1f} percentage points")
        else:
            print(f"❌ OVERSHOOT NOT REDUCED: {overshoot_reduction:.1f} percentage points")

        if settling_improvement > 5:
            print(f"✅ SETTLING TIME IMPROVED: {settling_improvement:.1f}%")
        elif settling_improvement > 0:
            print(f"✅ SETTLING TIME SLIGHTLY IMPROVED: {settling_improvement:.1f}%")
        else:
            print(f"⚠️  SETTLING TIME WORSENED: {settling_improvement:.1f}%")

        return True, results

    except Exception as e:
        print(f"ERROR: Error in overshoot comparison: {e}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    success, results = test_overshoot_comparison()
    if not success:
        sys.exit(1)