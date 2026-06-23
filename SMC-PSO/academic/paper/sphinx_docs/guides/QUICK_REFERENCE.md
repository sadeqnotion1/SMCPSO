# Quick Reference Guide Essential commands, patterns, and workflows for the DIP SMC PSO framework.

## Command Quick Reference 

### Basic Simulation 

```bash

# Minimal simulation (default controller, no plots)

python simulate.py # Classical SMC with plots
python simulate.py --ctrl classical_smc --plot # Super-Twisting SMC with plots
python simulate.py --ctrl sta_smc --plot # Adaptive SMC
python simulate.py --ctrl adaptive_smc --plot # Hybrid Adaptive STA-SMC
python simulate.py --ctrl hybrid_adaptive_sta_smc --plot
```

### PSO Optimization

```bash
# Optimize classical SMC gains
python simulate.py --ctrl classical_smc --run-pso --save optimized_gains.json # Optimize with specific seed (reproducibility)
python simulate.py --ctrl classical_smc --run-pso --seed 42 --save gains.json # Quick optimization (fewer iterations)
python simulate.py --ctrl classical_smc --run-pso \ --override "pso.iters=50" \ --override "pso.n_particles=15" \ --save quick_gains.json # Thorough optimization
python simulate.py --ctrl classical_smc --run-pso \ --override "pso.iters=200" \ --override "pso.n_particles=50" \ --save thorough_gains.json
```

### Loading Optimized Gains

```bash
# Use optimized gains

python simulate.py --load optimized_gains.json --plot # Load and override parameters
python simulate.py --load optimized_gains.json \ --override "max_force=150.0" \ --plot
```

### Configuration Overrides

```bash
# Override single parameter
python simulate.py --ctrl classical_smc \ --override "max_force=120.0" \ --plot # Override multiple parameters
python simulate.py --ctrl classical_smc \ --override "gains=[12,9,18,14,60,6]" \ --override "max_force=120.0" \ --override "boundary_layer=0.05" \ --plot # Override initial conditions
python simulate.py --ctrl classical_smc \ --override "simulation.initial_conditions=[0,0,0.2,0,0.3,0]" \ --plot # Override simulation duration and timestep
python simulate.py --ctrl classical_smc \ --override "simulation.duration=10.0" \ --override "simulation.dt=0.005" \ --plot
```

### Saving and Loading

```bash
# Save simulation results

python simulate.py --ctrl classical_smc --plot --save results.json # Load results for analysis
python -c "import json; data = json.load(open('results.json')); print(data['metrics'])" # Save configuration
python simulate.py --print-config > my_config.txt # Use custom configuration file
python simulate.py --config custom_config.yaml --ctrl classical_smc --plot
```

### Hardware-in-the-Loop (HIL)

```bash
# Run HIL simulation (automatic server + client)
python simulate.py --run-hil --plot # HIL with custom config
python simulate.py --config hil_config.yaml --run-hil --plot
```

### Web Interface

```bash
# Launch Streamlit dashboard

streamlit run streamlit_app.py # Custom port
streamlit run streamlit_app.py --server.port 8080 # Network accessible
streamlit run streamlit_app.py --server.address 0.0.0.0
```

### Testing

```bash
# Run all tests
python run_tests.py # Run specific test file
python -m pytest tests/test_controllers/test_classical_smc.py -v # Run with coverage
python -m pytest tests/ --cov=src --cov-report=html # Run benchmarks only
python -m pytest tests/test_benchmarks/ --benchmark-only
```

---

## Configuration Snippets 

### Gain Tuning 

```yaml

# config.yaml - Classical SMC

controllers: classical_smc: gains: [10.0, 8.0, 15.0, 12.0, 50.0, 5.0] # [k1, k2, λ1, λ2, K, ε] max_force: 100.0 boundary_layer: 0.01
```

### PSO Configuration

```yaml
# Quick PSO (prototyping)
pso: n_particles: 15 iters: 50 # Standard PSO (production)
pso: n_particles: 30 iters: 100 # Thorough PSO (research)
pso: n_particles: 50 iters: 200
```

### Cost Function Weights

```yaml
# Emphasize tracking accuracy

pso: cost_function: weights: ise: 0.6 itae: 0.2 control_effort: 0.1 overshoot: 0.1 # Emphasize energy efficiency
pso: cost_function: weights: ise: 0.2 itae: 0.2 control_effort: 0.5 overshoot: 0.1
```

---

## Python API Patterns 

### Basic Simulation 

```python
from src.controllers.factory import create_controller
from src.core.simulation_runner import SimulationRunner
from src.config import load_config # Load configuration
config = load_config('config.yaml') # Create controller
controller = create_controller( 'classical_smc', config=config.controllers.classical_smc
) # Run simulation
runner = SimulationRunner(config)
result = runner.run(controller) # Access results
print(f"ISE: {result['metrics']['ise']:.4f}")
print(f"Settling Time: {result['metrics']['settling_time']:.2f}s")
```

### PSO Optimization

```python

from src.optimizer.pso_optimizer import PSOTuner
from src.controllers import create_smc_for_pso, get_gain_bounds_for_pso, SMCType # Get bounds
bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL) # Create PSO tuner
tuner = PSOTuner( controller_type=SMCType.CLASSICAL, bounds=bounds, n_particles=30, iters=100
) # Optimize
best_gains, best_cost = tuner.optimize() print(f"Optimized gains: {best_gains}")
print(f"Final cost: {best_cost:.4f}")
```

### Batch Processing

```python
import numpy as np # Define initial conditions
initial_conditions = [ [0, 0, 0.1, 0, 0.15, 0], [0, 0, 0.2, 0, 0.25, 0], [0, 0, 0.3, 0, 0.35, 0],
] results = []
for ic in initial_conditions: config.simulation.initial_conditions = ic result = runner.run(controller) results.append(result['metrics']['ise']) print(f"Mean ISE: {np.mean(results):.4f}")
print(f"Std ISE: {np.std(results):.4f}")
```

---

## Performance Metrics Reference

### Primary Metrics

| Metric | Formula | Interpretation | Lower is Better |
|--------|---------|----------------|-----------------|
| **ISE** | ∫‖x‖² dt | Tracking accuracy (quadratic) | ![check](../_static/icons/status/check.svg) |
| **ITAE** | ∫t·‖x‖ dt | Time-weighted error (convergence) | ![check](../_static/icons/status/check.svg) |
| **Settling Time** | t when ‖x‖ < 5% | Convergence speed | ![check](../_static/icons/status/check.svg) |
| **Overshoot** | max(‖x‖) / setpoint | Peak deviation | ![check](../_static/icons/status/check.svg) |
| **Control Effort** | ∫‖u‖ dt | Energy consumption | ![check](../_static/icons/status/check.svg) |

### Controller-Specific Metrics

| Controller | Special Metrics |
|------------|-----------------|
| Classical SMC | Chattering index (du/dt variance) |
| Adaptive SMC | Adaptation trajectory, final gain |
| STA-SMC | Finite-time convergence, continuity |
| Hybrid | Adaptation + continuity |

---

## Troubleshooting Quick Fixes 

### Problem: Simulation diverges 

```bash

# Reduce timestep

python simulate.py --ctrl classical_smc --override "simulation.dt=0.005" --plot # Reduce initial perturbation
python simulate.py --ctrl classical_smc \ --override "simulation.initial_conditions=[0,0,0.05,0,0.08,0]" \ --plot
```

### Problem: PSO not converging

```bash
# Increase swarm size
python simulate.py --ctrl classical_smc --run-pso \ --override "pso.n_particles=50" \ --save gains.json # Widen bounds (edit config.yaml)
pso: bounds: - [0.1, 100.0] # Wider k1 range # ... etc
```

### Problem: Simulation too slow

```bash
# Use simplified dynamics

python simulate.py --ctrl classical_smc \ --override "simulation.use_full_dynamics=false" \ --plot # Reduce duration
python simulate.py --ctrl classical_smc \ --override "simulation.duration=3.0" \ --plot
```

### Problem: Import errors

```bash
# Verify working directory (must be project root)
cd /path/to/dip-smc-pso # Re-run simulation
python simulate.py --ctrl classical_smc --plot
```

---

## File Locations Reference ```

project_root/
├── simulate.py # Main CLI
├── streamlit_app.py # Web UI
├── config.yaml # Main configuration
├── requirements.txt # Dependencies
│
├── src/ # Source code
│ ├── controllers/ # Controller implementations
│ │ ├── factory/ # Factory system
│ │ ├── smc/ # 4 core SMC controllers
│ │ ├── specialized/ # Specialized controllers
│ │ └── mpc/ # MPC (experimental)
│ ├── core/ # Simulation engine
│ ├── optimizer/ # PSO implementation
│ └── utils/ # Utilities
│
├── tests/ # Test suite
│ ├── test_controllers/ # Controller tests
│ ├── test_core/ # Simulation tests
│ └── test_optimizer/ # PSO tests
│
├── docs/ # Documentation
│ └── guides/ # This directory
│
└── scripts/ # Utility scripts └── validate_documentation.py
```

---

## Common Workflows 

### Workflow 1: Baseline → Optimize → Validate 

```bash
# 1. Baseline
python simulate.py --ctrl classical_smc --plot --save baseline.json # 2. Optimize
python simulate.py --ctrl classical_smc --run-pso --save optimized.json # 3. Validate
python simulate.py --load optimized.json --plot --save validated.json # 4. Compare
python -c "
import json
b = json.load(open('baseline.json'))
v = json.load(open('validated.json'))
print(f'Improvement: {(1 - v[\"metrics\"][\"ise\"] / b[\"metrics\"][\"ise\"])*100:.1f}%')
"
```

### Workflow 2: Controller Comparison

```bash
# Run all 4 controllers

for ctrl in classical_smc sta_smc adaptive_smc hybrid_adaptive_sta_smc; do python simulate.py --ctrl $ctrl --plot --save results_${ctrl}.json
done # Compare
python -c "
import json
for ctrl in ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']: data = json.load(open(f'results_{ctrl}.json')) print(f'{ctrl:25s} ISE: {data[\"metrics\"][\"ise\"]:.4f}')
"
```

### Workflow 3: Monte Carlo Robustness Study

```bash
# Create batch script
cat > batch_study.sh << 'EOF'
for mass in 0.7 0.8 0.9 1.0 1.1 1.2 1.3; do for trial in {1..10}; do python simulate.py --ctrl classical_smc \ --override "dip_params.m0=${mass}" \ --seed $((mass * 100 + trial)) \ --save "results_m${mass}_t${trial}.json" done
done
EOF chmod +x batch_study.sh
./batch_study.sh
```

---

## Version Compatibility | Component | Required Version | Recommended |

|-----------|------------------|-------------|
| Python | ≥3.9 | 3.11 |
| NumPy | ≥1.21 | 2.0+ |
| SciPy | ≥1.7 | Latest |
| Matplotlib | ≥3.4 | Latest |
| PySwarms | ≥1.3 | Latest |
| Streamlit | ≥1.10 | Latest |

---

## Further Reading - [Getting Started](getting-started.md): Complete setup guide

- [User Guide](user-guide.md): reference
- [Tutorial Series](tutorials/): Step-by-step learning
- [How-To Guides](how-to/): Task-oriented recipes - [Running Simulations](how-to/running-simulations.md) - [Result Analysis](how-to/result-analysis.md) - [Optimization Workflows](how-to/optimization-workflows.md) - [Testing & Validation](how-to/testing-validation.md)
- [API Reference Guides](api/): Module-by-module technical reference - [Controllers API](api/controllers.md) - [Simulation API](api/simulation.md) - [Optimization API](api/optimization.md) - [Configuration API](api/configuration.md) - [Plant Models API](api/plant-models.md) - [Utilities API](api/utilities.md)
- [GitHub Issues](https://github.com/theSadeQ/dip-smc-pso/issues): Bug reports & features

---

**Last Updated:** October 2025
**Framework Version:** 1.0
