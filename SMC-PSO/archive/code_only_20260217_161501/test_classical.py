
import numpy as np
from src.core.simulation_context import SimulationContext
from src.core.simulation_runner import run_simulation

def check_classical():
    ctx = SimulationContext("config.yaml")
    dynamics = ctx.get_dynamics_model()
    controller = ctx.create_controller("classical_smc")
    
    cfg = ctx.get_config()
    t, x, u = run_simulation(
        controller=controller,
        dynamics_model=dynamics,
        sim_time=5.0,
        dt=0.01,
        initial_state=np.array(cfg.simulation.initial_state)
    )
    
    print(f"Classical simulation completed. Max theta1: {np.max(np.abs(x[:, 1])):.4f}")
    if np.max(np.abs(x[:, 1])) < 0.2:
        print("Classical SMC is STABLE")
    else:
        print("Classical SMC is UNSTABLE")

if __name__ == "__main__":
    check_classical()
