import numpy as np
import logging
import sys
import os
from pathlib import Path
from dataclasses import asdict

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.controllers.factory import create_controller
from src.simulation.engines.vector_sim import simulate_system_batch
from src.core.dynamics import DIPParams
from src.config import load_config
from src.utils.disturbances import DisturbanceGenerator, create_step_scenario

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResetAnalyzer")

class DisturbedControllerWrapper:
    """Wraps a controller to inject external disturbances into the control signal."""
    def __init__(self, controller, disturbance_gen):
        self.controller = controller
        self.disturbance_gen = disturbance_gen
        self.time = 0.0
        
        # Proxy attributes
        if hasattr(controller, 'dynamics_model'):
            self.dynamics_model = controller.dynamics_model
        if hasattr(controller, 'max_force'):
            self.max_force = controller.max_force
        else:
            self.max_force = 150.0 # Default
            
    def compute_control(self, state, *args, **kwargs):
        # Update internal time estimate (approximate)
        # Note: vector_sim passes time to ctrl(t, x) but compute_control usually takes (x, state, history)
        # We need to know 't'. 
        # But simulate_system_batch doesn't pass 't' to compute_control!
        # It updates controller internal state if available.
        # Let's rely on the controller's internal clock if it has one, or approximate.
        # Actually, ModularHybridSMC has self.simulation_time.
        
        # Get nominal control
        result = self.controller.compute_control(state, *args, **kwargs)
        
        # Get time from controller if possible
        t = getattr(self.controller, 'simulation_time', self.time)
        
        # Get disturbance
        d_force = self.disturbance_gen.get_disturbance_force_only(t)
        
        # Add to control (simulating matched disturbance on input channel)
        # Result can be dict or array or float
        if isinstance(result, dict):
            result['u'] += d_force
            # Re-saturate
            result['u'] = np.clip(result['u'], -self.max_force, self.max_force)
        elif isinstance(result, np.ndarray):
            result[0] += d_force
            result[0] = np.clip(result[0], -self.max_force, self.max_force)
        else:
            result += d_force
            result = np.clip(result, -self.max_force, self.max_force)
            
        # Update local time tracking (fallback)
        # Assuming dt=0.001 from config
        self.time += 0.001 
        
        return result

    def initialize_state(self):
        if hasattr(self.controller, 'initialize_state'):
            return self.controller.initialize_state()
        return None

    def initialize_history(self):
        if hasattr(self.controller, 'initialize_history'):
            return self.controller.initialize_history()
        return None

def params_to_dict(p):
    return {
        'cart_mass': p.masses.cart,
        'pendulum1_mass': p.masses.pendulum1,
        'pendulum2_mass': p.masses.pendulum2,
        'pendulum1_length': p.lengths.pendulum1,
        'pendulum2_length': p.lengths.pendulum2,
        'pendulum1_com': p.lengths.pendulum1_com,
        'pendulum2_com': p.lengths.pendulum2_com,
        'pendulum1_inertia': p.inertias.pendulum1,
        'pendulum2_inertia': p.inertias.pendulum2,
        'gravity': p.physics.gravity,
        'cart_damping': p.damping.cart,
        'pendulum1_damping': p.damping.pendulum1,
        'pendulum2_damping': p.damping.pendulum2,
    }

def analyze_resets():
    print("Running Stress Test with DISTURBANCES for Hybrid Adaptive STA-SMC...")
    
    # 1. Configuration Setup (Set 3 Parameters)
    surface_gains = [23.67, 14.29, 8.87, 3.55] 
    
    config_path = Path("config.yaml")
    base_config = load_config(config_path)
    base_params = DIPParams.from_physics_config(base_config.physics)
    
    rng = np.random.default_rng(42)
    
    # Disturbance Scenarios to Test
    # 10N is the standard benchmark. We test 10N, 20N, 30N.
    disturbance_magnitudes = [10.0, 20.0, 30.0, 40.0, 50.0]
    runs_per_case = 20
    
    print(f"{'Disturbance (N)':<20} | {'Saturation':<15} | {'Fall':<15} | {'Divergence':<15} | {'Success':<15}")
    print("-" * 90)
    
    for mag in disturbance_magnitudes:
        sat_count = 0
        fall_count = 0
        div_count = 0
        success_count = 0
        
        # Create Step Disturbance Scenario
        # Step at t=2.0s
        dist_gen_template = create_step_scenario(magnitude=mag, start_time=2.0)
        
        for i in range(runs_per_case):
            # A. Perturb Physics
            p_dict = params_to_dict(base_params)
            for key in ['cart_mass', 'pendulum1_mass', 'pendulum2_mass', 'pendulum1_length', 'pendulum2_length']:
                 if key in p_dict:
                     p_dict[key] *= rng.uniform(0.9, 1.1)
            perturbed_params = DIPParams(**p_dict)
            
            # B. Nominal Initial State (Small perturbation)
            # We focus on disturbance rejection, so start near equilibrium
            state = np.array([0.0, 0.05, -0.03, 0.0, 0.0, 0.0])
            
            # C. Factory with Wrapper
            def specific_factory(gains):
                ctrl = create_controller(
                    'hybrid_adaptive_sta_smc', 
                    config=base_config, 
                    gains=surface_gains
                )
                # Inject physics
                if hasattr(ctrl, 'dynamics_model'):
                     try: ctrl.dynamics_model = perturbed_params
                     except: pass
                if hasattr(ctrl, 'controllers'):
                     for c in ctrl.controllers.values():
                         if hasattr(c, 'dynamics_model'):
                             try: c.dynamics_model = perturbed_params
                             except: pass
                             
                # Wrap with Disturbance
                # We need a fresh generator for each run if it had state, but it's stateless config usually
                # But best to be safe.
                # create_step_scenario returns a new generator
                dist_gen = create_step_scenario(magnitude=mag, start_time=2.0)
                
                return DisturbedControllerWrapper(ctrl, dist_gen)
            
            # D. Run
            dummy_particles = np.zeros((1, 4))
            try:
                results = simulate_system_batch(
                    controller_factory=specific_factory,
                    particles=dummy_particles,
                    sim_time=5.0, # Enough time to see disturbance effect (starts at 2.0)
                    dt=0.001,
                    u_max=150.0,
                    initial_state=state
                )
                
                t, x, u, sigma = results
                x_run = x[0]
                u_run = u[0]
                sigma_run = sigma[0]
                
                # Check Failures
                # 1. Fall
                theta1 = x_run[:, 1]
                theta2 = x_run[:, 2]
                if np.any(np.abs(theta1) > np.pi/2) or np.any(np.abs(theta2) > np.pi/2):
                    fall_count += 1
                    continue
                
                # 2. Divergence
                if np.any(np.abs(sigma_run) > 50.0):
                    div_count += 1
                    continue
                    
                # 3. Saturation
                if np.any(np.abs(u_run) >= 149.9):
                    sat_count += 1
                    # Don't skip, just count.
                
                success_count += 1
                
            except Exception as e:
                # logger.error(f"Error: {e}")
                fall_count += 1
                
        print(f"{mag:<20.1f} | {sat_count:<15} | {fall_count:<15} | {div_count:<15} | {success_count:<15}")

if __name__ == "__main__":
    analyze_resets()