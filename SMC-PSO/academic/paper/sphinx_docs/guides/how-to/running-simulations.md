# How-To: Running Simulations **Type:** Task-Oriented Guide

**Level:** Beginner to Advanced
**Prerequisites:** [Getting Started Guide](../getting-started.md)

---

## Overview This guide provides practical recipes for running simulations in the DIP SMC PSO framework. Choose the approach that best fits your needs: - **Quick simulation:** CLI with default settings

- **Custom parameters:** CLI with overrides
- **Interactive tuning:** Streamlit dashboard
- **Batch processing:** Python API for Monte Carlo studies
- **Notebooks:** Jupyter integration for exploration

---

## Table of Contents - [CLI Usage](#cli-usage)

- [Programmatic Usage](#programmatic-usage)
- [Streamlit Dashboard](#streamlit-dashboard)
- [Advanced Patterns](#advanced-patterns)

---

## CLI Usage ### Basic Commands ```bash

# Minimal simulation (default controller, no plots)

python simulate.py # Classical SMC with plots
python simulate.py --ctrl classical_smc --plot # Save results to file
python simulate.py --ctrl classical_smc --plot --save results.json
``` ### All CLI Options ```bash
# View help
python simulate.py --help # Print current configuration
python simulate.py --print-config # Use custom configuration file
python simulate.py --config my_config.yaml --ctrl classical_smc --plot # Load pre-tuned gains
python simulate.py --load optimized_gains.json --plot # Run PSO optimization
python simulate.py --ctrl classical_smc --run-pso --save gains.json # Run Hardware-in-the-Loop simulation
python simulate.py --run-hil --plot # Set random seed for reproducibility
python simulate.py --ctrl classical_smc --seed 42 --plot
``` ### Parameter Overrides **Override single parameter:**

```bash
python simulate.py --ctrl classical_smc \ --override "max_force=150.0" \ --plot
``` **Override multiple parameters:**

```bash
python simulate.py --ctrl classical_smc \ --override "gains=[12,9,18,14,60,6]" \ --override "max_force=120.0" \ --override "boundary_layer=0.05" \ --plot
``` **Override nested configuration:**

```bash
# Change simulation duration
python simulate.py --ctrl classical_smc \ --override "simulation.duration=10.0" \ --plot # Change timestep
python simulate.py --ctrl classical_smc \ --override "simulation.dt=0.005" \ --plot # Change initial conditions
python simulate.py --ctrl classical_smc \ --override "simulation.initial_conditions=[0,0,0.2,0,0.3,0]" \ --plot # Change physics parameters
python simulate.py --ctrl classical_smc \ --override "dip_params.m0=1.5" \ --plot
``` **Combine multiple overrides:**

```bash
python simulate.py --ctrl classical_smc \ --override "simulation.duration=8.0" \ --override "simulation.dt=0.005" \ --override "dip_params.m0=1.2" \ --override "max_force=120.0" \ --plot \ --save robustness_test.json
``` ### Working with Saved Results **Save simulation:**

```bash
python simulate.py --ctrl classical_smc --plot --save baseline.json
``` **Load and inspect results (Python):**

```python
import json # Load results
with open('baseline.json') as f: data = json.load(f) # Access metrics
print(f"ISE: {data['metrics']['ise']:.4f}")
print(f"Settling Time: {data['metrics']['settling_time']:.2f}s") # Access controller type
print(f"Controller: {data['controller_type']}") # Access gains used
print(f"Gains: {data['gains']}")
``` **Load and compare results (bash):**

```bash
# Quick comparison using jq (if installed)
jq '.metrics' baseline.json
jq '.metrics' optimized.json # Or using Python one-liner
python -c "import json; print(json.load(open('baseline.json'))['metrics'])"
``` ### Reproducibility **Set seed for deterministic results:**

```bash
# Same seed = same PSO initialization + same random noise (if any)
python simulate.py --ctrl classical_smc --run-pso --seed 42 --save run1.json
python simulate.py --ctrl classical_smc --run-pso --seed 42 --save run2.json # Verify identical results
python -c "
import json
r1 = json.load(open('run1.json'))
r2 = json.load(open('run2.json'))
print('Identical:', r1['pso_cost'] == r2['pso_cost'])
"
```

---

## Programmatic Usage ### Basic Python API ```python

from src.controllers.factory import create_controller
from src.core.simulation_runner import SimulationRunner
from src.config import load_config # Load configuration
config = load_config('config.yaml') # Create controller
controller = create_controller( 'classical_smc', config=config.controllers.classical_smc
) # Initialize simulation runner
runner = SimulationRunner(config) # Run simulation
result = runner.run(controller) # Access results
print(f"ISE: {result['metrics']['ise']:.4f}")
print(f"Settling Time: {result['metrics']['settling_time']:.2f}s") # Access trajectories
import numpy as np
time = np.array(result['time'])
state = np.array(result['state'])
control = np.array(result['control']) # Extract specific states
theta1 = state[:, 2] # First pendulum angle
theta2 = state[:, 4] # Second pendulum angle
``` ### Custom Simulation Loop ```python
from src.controllers import create_smc_for_pso, SMCType
from src.plant.models.dynamics import DoubleInvertedPendulum
import numpy as np # Initialize system
dt = 0.01
duration = 5.0
steps = int(duration / dt) # Create dynamics model
dynamics = DoubleInvertedPendulum( m0=1.0, m1=0.1, m2=0.1, l1=0.5, l2=0.5, g=9.81
) # Create controller
controller = create_smc_for_pso( SMCType.CLASSICAL, gains=[10, 8, 15, 12, 50, 5], max_force=100.0
) # Initialize state
state = np.array([0.0, 0.0, 0.1, 0.0, 0.15, 0.0])
state_vars = {}
history = controller.initialize_history() # Storage
time_log = []
state_log = []
control_log = [] # Simulation loop
for i in range(steps): # Compute control u, state_vars, history = controller.compute_control( state, state_vars, history ) # Apply dynamics (using RK4 or Euler) state = dynamics.step(state, u, dt) # Your integration method # Log data time_log.append(i * dt) state_log.append(state.copy()) control_log.append(u) # Convert to arrays
time_array = np.array(time_log)
state_array = np.array(state_log)
control_array = np.array(control_log) print(f"Final state: {state_array[-1]}")
``` ### Batch Simulations ```python

import multiprocessing as mp
from functools import partial def run_single_simulation(ic, controller_gains): """Run simulation with specific initial condition.""" config = load_config('config.yaml') config.simulation.initial_conditions = ic controller = create_controller( 'classical_smc', config=config.controllers.classical_smc, gains=controller_gains ) runner = SimulationRunner(config) result = runner.run(controller) return result['metrics']['ise'] # Define initial conditions
initial_conditions = [ [0, 0, 0.1, 0, 0.15, 0], [0, 0, 0.2, 0, 0.25, 0], [0, 0, 0.3, 0, 0.35, 0],
] # Define gains
gains = [10, 8, 15, 12, 50, 5] # Run in parallel
with mp.Pool(4) as pool: run_func = partial(run_single_simulation, controller_gains=gains) ise_results = pool.map(run_func, initial_conditions) print(f"Mean ISE: {np.mean(ise_results):.4f}")
print(f"Std ISE: {np.std(ise_results):.4f}")
``` ### Jupyter Notebook Integration ```python
# In Jupyter notebook
%matplotlib inline
import matplotlib.pyplot as plt
from src.controllers.factory import create_controller
from src.core.simulation_runner import SimulationRunner
from src.config import load_config # Load config
config = load_config('config.yaml') # Run simulation
controller = create_controller('classical_smc', config=config.controllers.classical_smc)
runner = SimulationRunner(config)
result = runner.run(controller) # Plot results inline
fig, axes = plt.subplots(3, 1, figsize=(12, 8)) time = result['time']
state = np.array(result['state'])
control = result['control'] # Pendulum angles
axes[0].plot(time, state[:, 2], label='θ₁')
axes[0].plot(time, state[:, 4], label='θ₂')
axes[0].set_ylabel('Angle (rad)')
axes[0].legend()
axes[0].grid() # Angular velocities
axes[1].plot(time, state[:, 3], label='dθ₁')
axes[1].plot(time, state[:, 5], label='dθ₂')
axes[1].set_ylabel('Angular Velocity (rad/s)')
axes[1].legend()
axes[1].grid() # Control signal
axes[2].plot(time, control)
axes[2].set_xlabel('Time (s)')
axes[2].set_ylabel('Control Force (N)')
axes[2].grid() plt.tight_layout()
plt.show() # Display metrics
print(f"ISE: {result['metrics']['ise']:.4f}")
print(f"Settling Time: {result['metrics']['settling_time']:.2f}s")
```

---

## Streamlit Dashboard ### Launching the Dashboard ```bash

# Basic launch

streamlit run streamlit_app.py # Custom port
streamlit run streamlit_app.py --server.port 8080 # Network accessible (other devices on LAN)
streamlit run streamlit_app.py --server.address 0.0.0.0
``` Access at: `http://localhost:8501` ### Dashboard Features **1. Controller Selection**
- Dropdown menu with all 4 core controllers
- Dynamic parameter UI based on controller type **2. Parameter Tuning**
- Interactive sliders for gains
- Real-time validation (bounds checking)
- Max force adjustment
- Boundary layer control (classical SMC) **3. Initial Conditions**
- Sliders for all 6 state variables
- Presets for common scenarios: - Small perturbation - Large disturbance - Cart displacement - Non-zero velocities **4. Simulation Execution**
- "Run Simulation" button
- Live progress indicator
- Estimated time remaining **5. Visualization**
- Real-time state trajectories
- Control signal plot
- Phase portraits (optional)
- Zoomable, pannable plots **6. Performance Metrics**
- ISE, ITAE, settling time
- Peak overshoot
- Control effort
- Chattering index (for classical SMC) **7. Configuration Export**
- Download current parameters as JSON
- Load previously saved configurations
- Export plots as PNG/PDF ### Typical Workflow 1. **Select controller** (e.g., Classical SMC)
2. **Adjust gains** using sliders
3. **Set initial conditions** (e.g., θ₁=0.2, θ₂=0.3)
4. **Run simulation**
5. **Observe convergence** in plots
6. **Check metrics** (ISE, settling time)
7. **Refine parameters** and re-run
8. **Export configuration** when satisfied ### Tips for Dashboard Usage **Performance:**
- Keep simulation duration ≤10s for responsiveness
- Use coarser timestep (0.01-0.02) for real-time interaction
- "Simplified Dynamics" for faster iterations **Parameter Tuning:**
- Start with default gains
- Adjust one parameter at a time
- Watch for instability (unbounded states)
- Use PSO button for automatic optimization **Comparison:**
- Run multiple controllers sequentially
- Take screenshots for comparison
- Export metrics to CSV for analysis

---

## Advanced Patterns ### Long-Duration Simulations ```bash
# 60-second simulation with fine timestep
python simulate.py --ctrl classical_smc \ --override "simulation.duration=60.0" \ --override "simulation.dt=0.001" \ --plot \ --save long_run.json # Monitor memory usage (Linux/Mac)
/usr/bin/time -v python simulate.py --ctrl classical_smc \ --override "simulation.duration=60.0" \ --plot
``` **Memory management tip:**

For very long simulations, consider downsampling stored data: ```python
# In custom loop

if i % 10 == 0: # Store every 10th sample time_log.append(i * dt) state_log.append(state.copy()) control_log.append(u)
``` ### Parallel Simulations (Multiprocessing) ```python
import multiprocessing as mp
import subprocess def run_simulation(params): """Run simulation with specific parameters.""" ctrl, ic_idx, ic = params cmd = [ 'python', 'simulate.py', '--ctrl', ctrl, '--override', f'simulation.initial_conditions={ic}', '--save', f'results_{ctrl}_ic{ic_idx}.json' ] subprocess.run(cmd, check=True) return f'results_{ctrl}_ic{ic_idx}.json' # Define parameter combinations
controllers = ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']
initial_conditions = [ [0, 0, 0.1, 0, 0.15, 0], [0, 0, 0.2, 0, 0.25, 0],
] # Create all combinations
experiments = [ (ctrl, i, ic) for ctrl in controllers for i, ic in enumerate(initial_conditions)
] # Run in parallel (4 processes)
with mp.Pool(4) as pool: result_files = pool.map(run_simulation, experiments) print(f"Generated {len(result_files)} result files")
``` ### Custom Integration Methods ```python

from scipy.integrate import solve_ivp def dip_dynamics(t, state, controller, state_vars, history): """Dynamics function for scipy ODE solver.""" u, state_vars, history = controller.compute_control(state, state_vars, history) # Compute state derivatives (use your dynamics model) dstate = dynamics.compute_derivatives(state, u) return dstate # Solve using RK45 (adaptive)
solution = solve_ivp( lambda t, s: dip_dynamics(t, s, controller, state_vars, history), t_span=(0, 5.0), y0=initial_state, method='RK45', rtol=1e-6, atol=1e-9
) time = solution.t
state = solution.y.T
```

---

## Troubleshooting ### Simulation Diverges **Symptoms:** State values grow unbounded, NaN errors **Solutions:**
```bash
# Reduce timestep

python simulate.py --ctrl classical_smc --override "simulation.dt=0.005" --plot # Reduce initial perturbation
python simulate.py --ctrl classical_smc \ --override "simulation.initial_conditions=[0,0,0.05,0,0.08,0]" \ --plot # Increase max force limit
python simulate.py --ctrl classical_smc --override "max_force=150.0" --plot
``` ### Slow Performance **Solutions:**
```bash
# Use simplified dynamics

python simulate.py --ctrl classical_smc \ --override "simulation.use_full_dynamics=false" \ --plot # Reduce duration
python simulate.py --ctrl classical_smc --override "simulation.duration=3.0" --plot # Increase timestep (check stability)
python simulate.py --ctrl classical_smc --override "simulation.dt=0.02" --plot
``` ### Import Errors ```bash
# Verify working directory
pwd # Should be project root # Check Python path
python -c "import sys; print('\n'.join(sys.path))" # Reinstall dependencies
pip install -r requirements.txt
```

---

## Next Steps - [How-To: Result Analysis](result-analysis.md): Interpret simulation outputs

- [How-To: Optimization Workflows](optimization-workflows.md): Tune gains with PSO
- [Tutorial 01](../tutorials/tutorial-01-first-simulation.md): walkthrough
- [User Guide](../user-guide.md): Complete reference

---

**Last Updated:** October 2025
