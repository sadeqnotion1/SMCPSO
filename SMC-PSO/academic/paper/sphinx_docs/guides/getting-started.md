# Getting Started

Welcome to the DIP SMC PSO framework!

This guide covers help you get up and running with your first simulation in under 10 minutes.

## What is the DIP SMC PSO Framework?

This framework provides a complete research and development environment for:

- **Controlling a Double-Inverted Pendulum (DIP):** A challenging control problem with two pendulums stacked on a cart

- **Sliding Mode Control (SMC):** Advanced nonlinear control techniques with 4 controller variants
- **Particle Swarm Optimization (PSO):** Automated gain tuning for optimal performance
- **Scientific Computing:** High-fidelity simulations, analysis, and visualization ## Who Should Use This Framework? This framework is designed for: - **Control Systems Researchers:** Testing advanced SMC algorithms and optimization techniques
- **Graduate Students:** Learning control theory through hands-on experimentation
- **Engineers:** Prototyping control systems for underactuated mechanical systems
- **Educators:** Teaching nonlinear control and optimization concepts ## Prerequisites Before you begin, ensure you have: - ![check](../_static/icons/status/check.svg) **Python 3.9 or newer** (Python 3.11 recommended)
- ![check](../_static/icons/status/check.svg) **pip** package manager
- ![check](../_static/icons/status/check.svg) **Git** for cloning the repository
- ![check](../_static/icons/status/check.svg) **10 GB free disk space** (for virtual environment and dependencies)
- ![check](../_static/icons/status/check.svg) **Basic Python knowledge** (variables, functions, imports)
- ![info](../_static/icons/status/info.svg) **Optional:** CUDA-capable GPU for accelerated batch simulations ## What You'll Learn By the end of this guide, you will be able to: 1. Install and verify the framework
2. Run your first simulation with a classical SMC controller
3. Understand simulation outputs and visualizations
4. Explore different controller types
5. Know where to go next for advanced topics

---

## Installation ### Step 1: Verify Python Version Open a terminal and check your Python version: ```bash

python --version
# OR on some systems:

python3 --version
``` **Expected output:** `Python 3.9.x` or higher (e.g., `Python 3.11.5`) **Troubleshooting:**
- **"python: command not found"** → Install Python from [python.org](https://www.python.org/downloads/)
- **Python 2.x.x shown** → Use `python3` instead of `python` throughout this guide
- **Python 3.8 or older** → Upgrade to Python 3.9+ for compatibility ### Step 2: Clone the Repository Clone the project to your local machine: ```bash
# Clone repository
git clone https://github.com/theSadeQ/dip-smc-pso.git # Navigate to project directory
cd dip-smc-pso # Verify you're in the correct directory
ls
# You should see: simulate.py, config.yaml, src/, tests/, docs/, etc.
``` **Troubleshooting:**

- **"git: command not found"** → Install Git from [git-scm.com](https://git-scm.com/downloads)
- **Permission denied** → Check your SSH keys or use HTTPS URL instead
- **Slow clone** → Large repository (~100 MB), be patient on slow connections ### Step 3: Create Virtual Environment (Recommended) A virtual environment isolates project dependencies: ```bash
# Create virtual environment

python -m venv venv # Activate virtual environment
# On Linux/Mac:

source venv/bin/activate # On Windows (Command Prompt):
venv\Scripts\activate.bat # On Windows (PowerShell):
venv\Scripts\Activate.ps1
``` **Expected result:** Your terminal prompt should now show `(venv)` prefix **Troubleshooting:**
- **"venv: command not found"** → Install python3-venv: `sudo apt install python3-venv` (Linux)
- **PowerShell execution policy error** → Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Activation doesn't change prompt** → Try using full path to activate script ### Step 4: Install Dependencies Install all required Python packages: ```bash
# Ensure pip is up to date
pip install --upgrade pip # Install project dependencies
pip install -r requirements.txt
``` **This will install (~50 packages, ~500 MB):**

- NumPy, SciPy (numerical computing)
- Matplotlib (visualization)
- PyYAML (configuration)
- Numba (performance acceleration)
- PySwarms (PSO optimization)
- Pytest (testing)
- Streamlit (web interface) **Installation takes:** 2-5 minutes depending on internet speed **Troubleshooting:**
- **Compiler errors (Windows)** → Install Visual C++ Build Tools
- **NumPy version conflicts** → Use: `pip install --upgrade numpy`
- **Permission errors** → Ensure virtual environment is activated, or use `pip install --user`
- **Slow download** → Use mirror: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple` ### Step 5: Verify Installation Test that everything is installed correctly: ```bash
# Check simulate.py is accessible

python simulate.py --help
``` **Expected output:**
```

usage: simulate.py [-h] [--config CONFIG] [--controller CONTROLLER] [--save-gains PATH] [--load-gains PATH] [--duration DURATION] [--dt DT] [--plot] [--print-config] [--plot-fdi] [--run-hil] [--run-pso] [--seed SEED] CLI for PSO-tuned Sliding-Mode Control and HIL for a double-inverted pendulum. options: -h, --help show this help message and exit --config CONFIG Path to config file (default: config.yaml) --controller CONTROLLER Controller type to use (classical_smc, sta_smc, adaptive_smc, hybrid_adaptive_sta_smc) --save-gains PATH Save gains to JSON file --load-gains PATH Load gains from JSON file --duration DURATION Override simulation duration (s) --dt DT Override simulation timestep (s) --plot Display plots after simulation --print-config Print current configuration and exit --plot-fdi Show FDI residual plots (requires FDI enabled) --run-hil Run hardware-in-the-loop simulation --run-pso Run PSO optimization for controller gains --seed SEED Random seed for reproducibility
``` **Installation Complete!** You're now ready to run your first simulation.

---

## Your First Simulation

### Run the Classical SMC Controller

Execute your first simulation with the classical sliding mode controller:

```bash
python simulate.py --controller classical_smc --plot
```

**What happens:**

1. Framework loads configuration from `config.yaml`
2. Creates a classical SMC controller with default gains
3. Initializes the double-inverted pendulum dynamics model
4. Runs a 5-second simulation with 0.001s timesteps (5,000 steps)
5. Generates performance metrics
6. Displays visualization plots **Expected terminal output:**
```
INFO:root:Provenance configured: commit=<hash>, cfg_hash=<hash>, seed=0
D:\Projects\main\src\plant\core\state_validation.py:171: UserWarning: State vector was modified during sanitization warnings.warn("State vector was modified during sanitization", UserWarning)
``` **Note:** The simulation runs with minimal terminal output. The provenance line confirms the simulation configuration is tracked for reproducibility. The state sanitization warning is normal and indicates the simulator is ensuring numerical stability. **⏱️ Simulation takes:** 10-15 seconds on modern hardware (includes initialization and plotting) ### Understanding the Output #### Plot Window 1: State Trajectories You'll see a plot with 6 subplots showing: 1. **Cart Position (x):** Should stabilize near initial displacement (~0.1 m)

2. **Cart Velocity (dx):** Should converge to 0 m/s
3. **First Pendulum Angle (θ₁):** Should converge to 0 rad (upright)
4. **First Pendulum Velocity (dθ₁):** Should converge to 0 rad/s
5. **Second Pendulum Angle (θ₂):** Should converge to 0 rad (upright)
6. **Second Pendulum Velocity (dθ₂):** Should converge to 0 rad/s **Key observations:**
- **Transient response:** Initial oscillations as pendulums stabilize (0-3 seconds)
- **Steady state:** Final values after settling (3-5 seconds)
- **Coupling effects:** Notice how cart motion affects pendulum angles #### Plot Window 2: Control Input Shows the force applied to the cart over time: - **Initial spike:** Large force to counteract initial perturbation
- **Oscillations:** Controller actively stabilizing during transient
- **Steady-state control:** Small forces for regulation and disturbance rejection
- **Saturation:** Control is limited to ±150 N (actuator limit) #### Performance Metrics Explained **Settling Time (2.45s):**
- Time until all state variables stay within 2% of final value
- Indicates how quickly the controller stabilizes the system
- Lower is better (faster response) **Max Overshoot (3.2%):**
- Maximum deviation beyond setpoint during transient
- Indicates damping quality
- Target: <5% for well-tuned controllers **Steady-State Error (0.008 rad ≈ 0.46°):**
- Final tracking error after settling
- Indicates long-term accuracy
- Caused by model mismatch, friction, discretization **RMS Control Effort (12.4 N):**
- Root-mean-square of control input
- Indicates energy consumption and actuator wear
- Must stay below saturation limit (150 N) ### What Just Happened? break down the simulation process: 1. **Controller Initialization** - Classical SMC with default gains: `[k₁=5, k₂=5, λ₁=5, λ₂=0.5, K=0.5, ε=0.5]` - Sliding surface: `s = k₁·θ₁ + k₂·dθ₁ + λ₁·θ₂ + λ₂·dθ₂` - Control law: `u = -K·tanh(s/ε)` (smooth approximation to reduce chattering) 2. **Dynamics Model Selection** - Simplified nonlinear model (faster computation) - 6-state system: `[x, dx, θ₁, dθ₁, θ₂, dθ₂]` - Includes gravity, inertia, Coriolis effects - Discretized with fixed-step integration (Euler or RK4) 3. **Integration Process** - Time loop: 0 → 5 seconds with 0.001s timestep - At each step: - Controller computes force `u` based on current state - Dynamics model predicts next state using `u` - State updated and logged - Total: 5,000 integration steps 4. **Visualization Generation** - State trajectories plotted from logged data - Control input history displayed - Performance metrics computed from final results ### Modifying Initial Conditions The initial state of the system is defined in `config.yaml`: ```yaml
simulation: initial_state: [0.1, 0.0, 0.0, 0.0, 0.0, 0.0] # [x, dx, θ₁, dθ₁, θ₂, dθ₂]
``` **Current setup:**
- Cart displaced 0.1 m to the right
- Both pendulums upright
- All velocities zero **Experiment:** Try different initial conditions: ```yaml
# Example 1: Perturb first pendulum
initial_state: [0.0, 0.0, 0.15, 0.0, 0.0, 0.0] # θ₁ = 0.15 rad ≈ 8.6° # Example 2: Perturb second pendulum
initial_state: [0.0, 0.0, 0.0, 0.0, -0.10, 0.0] # θ₂ = -0.10 rad ≈ -5.7° # Example 3: Both pendulums perturbed
initial_state: [0.0, 0.0, 0.10, 0.0, -0.08, 0.0] # Example 4: Moving cart
initial_state: [0.0, 0.5, 0.05, 0.0, -0.05, 0.0] # Cart velocity = 0.5 m/s
``` After editing `config.yaml`, re-run:

```bash
python simulate.py --controller classical_smc --plot
``` Observe how the controller responds to different perturbations!

---

## Exploring Other Controllers The framework includes 4 SMC controller variants. Each has unique strengths: ### 1. Super-Twisting SMC (STA) Smooth, continuous control with reduced chattering: ```bash

python simulate.py --controller sta_smc --plot
``` **Characteristics:**
- Second-order sliding mode (higher-order derivative compensation)
- Finite-time convergence guarantee
- Continuous control signal (no switching)
- Better for systems sensitive to chattering ### 2. Adaptive SMC Automatically tunes gains online for uncertain systems: ```bash
python simulate.py --controller adaptive_smc --plot
``` **Characteristics:**

- Adaptation law adjusts gains based on tracking error
- Robust to parameter variations and disturbances
- Slower initial response but learns over time
- Good for systems with unknown dynamics ### 3. Hybrid Adaptive STA-SMC Combines adaptation with super-twisting for maximum performance: ```bash
python simulate.py --controller hybrid_adaptive_sta_smc --plot
``` **Characteristics:**
- Best overall performance (fastest + smoothest)
- Most complex configuration
- Recommended for research applications
- Requires understanding of advanced SMC theory **Note:** You may see a warning about "Large adaptation rate may cause instability" - this is advisory only and the default configuration has been validated for stability. ### Quick Comparison | Controller | Chattering | Speed | Complexity | Best For |
|-----------|-----------|-------|-----------|----------|
| **Classical** | Moderate | Good | Low | Learning, baseline |
| **STA** | Low | Good | Medium | Smooth control |
| **Adaptive** | Moderate | Slower | Medium | Uncertain systems |
| **Hybrid** | Very Low | Fast | High | Research, max performance |

---

## Next Steps ### Learn More: Tutorials Progress through our tutorial series: 1. **[Tutorial 01: First Simulation](tutorials/tutorial-01-first-simulation.md)** - Deep dive into the DIP system - Detailed explanation of simulation outputs - Parameter experimentation guide 2. **[Tutorial 02: Controller Comparison](tutorials/tutorial-02-controller-comparison.md)** - Side-by-side comparison of all 4 controllers - Quantitative performance analysis - How to choose the right controller 3. **[Tutorial 03: PSO Optimization](tutorials/tutorial-03-pso-optimization.md)** - Automated gain tuning workflow - Understanding PSO parameters - Case study: Overshoot reduction 4. **[Tutorial 04: Custom Controller](tutorials/tutorial-04-custom-controller.md)** - Implement your own controller - Integrate with factory pattern - Register for PSO optimization 5. **[Tutorial 05: Research Workflow](tutorials/tutorial-05-research-workflow.md)** - Reproducible experiments - Monte Carlo validation - Publication-quality plots ### How-To Guides Task-oriented recipes for specific workflows: - **[Running Simulations](how-to/running-simulations.md):** CLI, Streamlit, programmatic usage
- **[Optimization Workflows](how-to/optimization-workflows.md):** PSO tuning, convergence analysis
- **[Result Analysis](how-to/result-analysis.md):** Metrics interpretation, visualization
- **[Testing & Validation](how-to/testing-validation.md):** Test suite, validation, benchmarks ### Advanced Topics Ready for more? Explore: - **PSO Gain Tuning:** Automatically find optimal controller gains ```bash python simulate.py --controller classical_smc --run-pso --save-gains tuned_gains.json ``` - **Streamlit Dashboard:** Interactive parameter adjustment and real-time visualization ```bash streamlit run streamlit_app.py ``` - **Hardware-in-the-Loop (HIL):** Connect to real hardware ```bash python simulate.py --run-hil --plot ``` - **Batch Simulations:** Monte Carlo validation for robustness analysis ### API Reference Guides module-by-module technical reference with practical examples: - **[Controllers API Guide](api/controllers.md)** - Factory system, SMC types, custom controllers
- **[Simulation API Guide](api/simulation.md)** - SimulationRunner, dynamics models, batch processing
- **[Optimization API Guide](api/optimization.md)** - PSOTuner, cost functions, convergence monitoring
- **[Configuration API Guide](api/configuration.md)** - Loading config, validation, programmatic setup
- **[Plant Models API Guide](api/plant-models.md)** - Physics models, parameter configuration
- **[Utilities API Guide](api/utilities.md)** - Validation, monitoring, analysis tools For auto-generated technical reference, see: [docs/reference/](../reference/index.md)

---

## Troubleshooting Common Issues

### Simulation Runs But No Plots Appear

**Cause:** Matplotlib backend issue

**Solution:**

```bash
# Linux: Install Tkinter

sudo apt-get install python3-tk # macOS: Use different backend
export MPLBACKEND=MacOSX # Windows: Reinstall matplotlib
pip uninstall matplotlib
pip install matplotlib
``` ### "NumericalInstabilityError" During Simulation **Cause:** Controller gains too aggressive or timestep too large **Solution:**
- Reduce controller gains (edit `config.yaml`)
- Decrease timestep: `dt: 0.0005` (in `config.yaml`)
- Use full dynamics model for better accuracy ### PSO Optimization Very Slow **Cause:** Default settings evaluate 1,500 simulations (30 particles × 50 iterations) **Solution:**
```yaml
# config.yaml - Reduce PSO iterations for faster testing

pso: iters: 20 # Reduced from 50 n_particles: 20 # Reduced from 30
``` ### Import Errors After Installation **Cause:** Virtual environment not activated or wrong Python interpreter **Solution:**
```bash
# Ensure virtual environment is activated

source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows # Verify correct Python
which python # Should show path inside venv/
python -c "import src.config; print('OK')"
``` ### "State vector was modified during sanitization" Warning **Cause:** Normal operation - the simulator ensures numerical stability by sanitizing input states **What it means:** This is an informational warning, not an error. The simulation is working correctly and automatically correcting any potential numerical issues with the initial state. **Solution:** No action required. This warning confirms the safety mechanisms are active. You can safely ignore it.

---

## Get Help - **Documentation:** [https://dip-smc-pso.readthedocs.io/](https://dip-smc-pso.readthedocs.io/)
- **GitHub Issues:** [https://github.com/theSadeQ/dip-smc-pso/issues](https://github.com/theSadeQ/dip-smc-pso/issues)
- **Discussions:** [https://github.com/theSadeQ/dip-smc-pso/discussions](https://github.com/theSadeQ/dip-smc-pso/discussions)

---

**Congratulations! You've completed the getting started guide.** 🎉 You now have a working DIP SMC PSO installation and have run your first simulation. Continue with [Tutorial 01](tutorials/tutorial-01-first-simulation.md) for a deeper understanding.
