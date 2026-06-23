import numpy as np
import yaml
from pathlib import Path
from src.core.simulation_context import SimulationContext
from src.core.simulation_runner import run_simulation
from src.utils.analysis.chattering_metrics import compute_chattering_metrics

def check_hybrid_chattering():
    config_path = "config.yaml"
    ctx = SimulationContext(config_path)
    
    dynamics = ctx.get_dynamics_model()
    from src.controllers.factory import get_default_gains
    default_gains = get_default_gains("hybrid_adaptive_sta_smc")
    print(f"Using default gains: {default_gains}")
    controller = ctx.create_controller("hybrid_adaptive_sta_smc", gains=default_gains)
    if hasattr(controller, 'controllers'):
        for sub_ctrl in controller.controllers.values():
            if hasattr(sub_ctrl, '_equivalent'):
                sub_ctrl._equivalent.dynamics_model = None
    
    cfg = ctx.get_config()
    duration = cfg.simulation.duration
    dt = cfg.simulation.dt
    initial_state = np.array(cfg.simulation.initial_state)
    
    # Run simulation manually to see progress
    dt = cfg.simulation.dt
    current_state = initial_state
    
    state_vars = controller.initialize_state() if hasattr(controller, 'initialize_state') else ()
    history = controller.initialize_history() if hasattr(controller, 'initialize_history') else {}
    
    states = [current_state]
    controls = []
    times = [0.0]
    
    for i in range(int(duration/dt)):
        control_result = controller.compute_control(current_state, state_vars, history)
        if isinstance(control_result, dict):
            u = control_result.get('u', 0.0)
            state_vars = control_result.get('state_vars', state_vars)
        else:
            u = control_result[0]
            
        control_input = np.array([u])
        result = dynamics.compute_dynamics(current_state, control_input)
        if not result.success:
            print(f"Simulation failed at step {i}")
            break
            
        current_state = current_state + dt * result.state_derivative
        states.append(current_state)
        controls.append(u)
        times.append((i+1)*dt)
        
        if i % 100 == 0:
            print(f"Step {i}: t={i*dt:.2f}s, th1={current_state[1]:.4f}, th2={current_state[2]:.4f}, s={control_result.get('surface_value', 0):.4f}")
            
    t = np.array(times)
    x = np.array(states)
    u = np.array(controls)
    
    print(f"Simulation completed with {len(t)} steps.")
    
    # Plot results
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    
    axes[0].plot(t, x[:, 1], label='Theta 1')
    axes[0].plot(t, x[:, 2], label='Theta 2')
    axes[0].set_title('Pendulum Angles')
    axes[0].legend()
    axes[0].grid(True)
    
    axes[1].plot(t[:-1], u, label='Control (u)')
    axes[1].set_title('Control Input')
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    plt.savefig('chattering_diag.png')
    print("\nSaved diagnostic plot to 'chattering_diag.png'")
    
    # Calculate chattering metrics
    # We use the control array 'u'
    metrics = compute_chattering_metrics(u, dt, transient_time=1.0)
    
    print("\nChattering Metrics (after 1s transient):")
    for key, value in metrics.items():
        print(f"  {key}: {value:.6f}")
        
    if metrics['chattering_index'] < 0.1:
        print("\nSUCCESS: Chattering index is below 0.1!")
    elif metrics['chattering_index'] < 2.0:
        print("\nPARTIAL SUCCESS: Chattering index is below 2.0 (standard target).")
    else:
        print(f"\nFAILURE: Chattering index is {metrics['chattering_index']:.2f} (Target < 0.1)")

if __name__ == "__main__":
    check_hybrid_chattering()
