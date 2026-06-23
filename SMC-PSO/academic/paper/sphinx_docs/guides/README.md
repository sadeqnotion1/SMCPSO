# User Guides & Tutorials Welcome to the DIP SMC PSO framework documentation! This guide covers help you navigate the documentation and find what you need.

## 🎮 NEW: Interactive 3D Visualization

**Revolutionary Feature: World's First 3D Pendulum in Technical Documentation**

Experience real-time physics simulation with WebGL rendering, directly in your browser:

- [**🎮 3D Interactive Pendulum Demo**](interactive/3d-pendulum-demo.md) - Adjust controller gains, set initial conditions, watch physics unfold in real-time with cinematic 3D graphics

**Features:**
- GPU-accelerated WebGL rendering with Three.js
- Real-time physics at 60 FPS
- Interactive parameter sliders (controller gains K₁-K₆, initial angles θ₁, θ₂)
- Orbit camera controls (zoom, pan, rotate)
- Visual trail showing pendulum tip path
- Realistic materials with shadows and lighting

**Zero installation required** - runs entirely in your browser!

---

## Quick Navigation ### 🚀 Getting Started

**Start here if you're new to the framework** - [**Getting Started Guide**](getting-started.md) Complete setup and first simulation in 10 minutes ### 📘 User Guide
**reference for daily usage** - [**User Guide**](user-guide.md) Core workflows, configuration, PSO optimization, result analysis ### 📚 Tutorial Series
**Step-by-step learning path** 1. [**Tutorial 01: Your First Simulation**](tutorials/tutorial-01-first-simulation.md) Learn DIP system, run classical SMC, interpret results (30-45 min) 2. [**Tutorial 02: Controller Comparison**](tutorials/tutorial-02-controller-comparison.md) Compare 4 core SMC controllers, understand tradeoffs, select optimal controller (45-60 min) 3. [**Tutorial 03: PSO Optimization**](tutorials/tutorial-03-pso-optimization.md) Automatic gain tuning, convergence analysis, custom cost functions (60-90 min) 4. [**Tutorial 04: Custom Controller Development**](tutorials/tutorial-04-custom-controller.md) Implement Terminal SMC from scratch, factory integration, testing (90-120 min) 5. [**Tutorial 05: Research Workflow**](tutorials/tutorial-05-research-workflow.md) End-to-end research project, statistical analysis, publication workflow (120+ min) ### 🔧 How-To Guides
**Task-oriented recipes for specific workflows** - [**Running Simulations**](how-to/running-simulations.md) CLI usage, Streamlit dashboard, programmatic API, batch processing - [**Result Analysis**](how-to/result-analysis.md) Metrics interpretation, statistical analysis, visualization, data export - [**Optimization Workflows**](how-to/optimization-workflows.md) PSO tuning, custom cost functions, convergence diagnostics, parallel execution - [**Testing & Validation**](how-to/testing-validation.md) Test suite, unit testing, performance benchmarking, coverage analysis ### 📖 API Reference Guides
**Module-by-module technical reference with examples** - [**API Index**](api/README.md) Overview and navigation for all API guides - [**Controllers API**](api/controllers.md) Factory system, SMC types, gain bounds, custom controllers (726 lines) - [**Simulation API**](api/simulation.md) SimulationRunner, dynamics models, batch processing, performance (517 lines) - [**Optimization API**](api/optimization.md) PSOTuner, cost functions, gain bounds, convergence monitoring (543 lines) - [**Configuration API**](api/configuration.md) Loading config, validation, programmatic configuration (438 lines) - [**Plant Models API**](api/plant-models.md) Physics models, parameter configuration, custom dynamics (424 lines) - [**Utilities API**](api/utilities.md) Validation, control primitives, monitoring, analysis tools (434 lines) ### 📐 Theory & Explanation
**Understanding-oriented guides that explain the "why" behind the framework** - [**Theory Index**](theory/README.md) Overview and navigation for all theory guides - [**Sliding Mode Control Theory**](theory/smc-theory.md) SMC fundamentals, Lyapunov stability, chattering analysis, super-twisting mathematics (619 lines) - [**PSO Algorithm Theory**](theory/pso-theory.md) Swarm intelligence principles, convergence theory, parameter selection, benchmarks (438 lines) - [**Double-Inverted Pendulum Dynamics**](theory/dip-dynamics.md) Lagrangian derivation, equations of motion, linearization, controllability (501 lines) ### ✨ Documentation Features
**Special features built into this documentation site** - [**Features Index**](features/README.md) Overview of all documentation features - [**Collapsible Code Blocks**](features/code-collapse/user-guide.md) Collapse/expand code examples with state persistence (v1.0.0)

---

## Documentation Structure ```

docs/guides/
├── README.md # This file (navigation)
├── getting-started.md # Quick setup (523 lines)
├── user-guide.md # reference (826 lines)
├── QUICK_REFERENCE.md # Command cheat sheet
├── how-to/ # Task-oriented guides
│ ├── running-simulations.md (619 lines)
│ ├── result-analysis.md (589 lines)
│ ├── optimization-workflows.md (724 lines)
│ └── testing-validation.md (611 lines)
├── api/ # API reference guides
│ ├── README.md (203 lines)
│ ├── controllers.md (726 lines)
│ ├── simulation.md (517 lines)
│ ├── optimization.md (543 lines)
│ ├── configuration.md (438 lines)
│ ├── plant-models.md (424 lines)
│ └── utilities.md (434 lines)
├── theory/ # Theory & explanation guides
│ ├── README.md (104 lines)
│ ├── smc-theory.md (619 lines)
│ ├── pso-theory.md (438 lines)
│ └── dip-dynamics.md (501 lines)
├── features/ # Documentation features
│ ├── README.md (overview)
│ └── code-collapse/ # Collapsible code blocks
│ ├── user-guide.md
│ ├── integration-guide.md
│ ├── configuration-reference.md
│ ├── troubleshooting.md
│ ├── technical-reference.md
│ ├── maintenance-guide.md
│ └── changelog.md
└── tutorials/ # Tutorial series ├── tutorial-01-first-simulation.md (600 lines) ├── tutorial-02-controller-comparison.md (797 lines) ├── tutorial-03-pso-optimization.md (865 lines) ├── tutorial-04-custom-controller.md (784 lines) └── tutorial-05-research-workflow.md (640 lines)
``` **Total: 12,525 lines of user documentation** (up from 10,863 after adding theory guides)

---

## Learning Paths ### Path 1: Quick Start (1-2 hours)
Perfect for: First-time users, quick prototyping 1. [Getting Started](getting-started.md) → Install & run first simulation
2. [Tutorial 01](tutorials/tutorial-01-first-simulation.md) → Understand DIP & SMC basics
3. [How-To: Running Simulations](how-to/running-simulations.md) → Explore CLI and Streamlit options ### Path 2: Controller Expert (4-6 hours)
Perfect for: Control systems researchers, comparative studies 1. [Getting Started](getting-started.md) → Setup
2. [Tutorial 01](tutorials/tutorial-01-first-simulation.md) → Basics
3. [Tutorial 02](tutorials/tutorial-02-controller-comparison.md) → Compare controllers
4. [Tutorial 03](tutorials/tutorial-03-pso-optimization.md) → Optimize gains
5. [How-To: Optimization Workflows](how-to/optimization-workflows.md) → Advanced PSO tuning ### Path 3: Custom Development (8-12 hours)
Perfect for: Implementing novel SMC algorithms 1. [Getting Started](getting-started.md) → Setup
2. [Tutorial 01-02](tutorials/) → Learn framework basics
3. [Tutorial 04](tutorials/tutorial-04-custom-controller.md) → Implement custom controller
4. [Tutorial 03](tutorials/tutorial-03-pso-optimization.md) → Optimize custom controller
5. [How-To: Testing & Validation](how-to/testing-validation.md) → testing ### Path 4: Research Publication (12+ hours)
Perfect for: Graduate students, researchers 1. Complete Paths 1-2 (understand framework & controllers)
2. [Tutorial 05](tutorials/tutorial-05-research-workflow.md) → End-to-end research project
3. [How-To: Result Analysis](how-to/result-analysis.md) → Statistical validation and visualization
4. [User Guide - Batch Processing](user-guide.md#batch-processing) → Monte Carlo studies

---

## Quick Reference ### Most Common Commands ```bash
# Run simulation
python simulate.py --ctrl classical_smc --plot # Optimize gains
python simulate.py --ctrl classical_smc --run-pso --save gains.json # Test optimized gains
python simulate.py --load gains.json --plot # Web interface
streamlit run streamlit_app.py # Run tests
python run_tests.py
``` See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for full command reference.

---

## Controllers Overview | Controller | Best For | Computational Cost | Chattering |

|------------|----------|-------------------|------------|
| **Classical SMC** | Prototyping, known systems | Low | Moderate |
| **Super-Twisting SMC** | Chattering-sensitive apps | Medium | None |
| **Adaptive SMC** | Uncertain/varying systems | Medium-High | Low |
| **Hybrid Adaptive STA** | High-performance control | High | None | **Decision Tree:**
- Need smooth control? → Super-Twisting or Hybrid
- Parameter uncertainty? → Adaptive or Hybrid
- Simplicity priority? → Classical
- Best overall? → Hybrid Adaptive STA ### Interactive Performance Comparison Visual comparison of controller performance across key metrics: ```{eval-rst}
.. chartjs:: :type: bar :data: ../visualization/performance_charts/settling_time_comparison.json :height: 350 :responsive: :title: Settling Time Comparison with 95% Confidence Intervals
``` **Key Performance Metrics:** - **Settling Time:** Classical SMC leads with fastest convergence (lowest settling time)
- **Computational Efficiency:** All controllers achieve real-time performance (<10ms per timestep)
- **Stability:** Hybrid Adaptive-STA provides best robustness to disturbances
- **Overshoot:** STA-SMC and Classical SMC show superior tracking performance ```{eval-rst}
.. chartjs:: :type: radar :data: ../visualization/performance_charts/stability_scores.json :height: 350 :responsive: :title: Multi-Dimensional Controller Comparison
``` **Interactive Dashboards:** For detailed performance analysis with all 6 chart types, see:

- [📊 Full Interactive Dashboard](../visualization/interactive_dashboard.html) - 6-chart performance overview
- [📈 Individual Chart Pages](../visualization/) - Focused single-chart visualizations

---

## Key Concepts ### System

- **DIP (Double-Inverted Pendulum):** Two pendulums on a cart, 6-state system
- **Underactuated:** 3 DOF, 1 control input (cart force)
- **Unstable equilibrium:** Both pendulums vertical ### Control
- **SMC (Sliding Mode Control):** Nonlinear control with sliding surface
- **Sliding Surface:** `s = k₁θ₁ + k₂dθ₁ + λ₁θ₂ + λ₂dθ₂`
- **Chattering:** High-frequency oscillations from discontinuous switching ### Optimization
- **PSO (Particle Swarm Optimization):** Bio-inspired algorithm for gain tuning
- **Swarm:** Collection of candidate approaches (particles)
- **Convergence:** Process of finding optimal gains (typically 50-100 iterations) ### Metrics
- **ISE:** Integral Squared Error (tracking accuracy)
- **ITAE:** Integral Time-Absolute Error (convergence speed)
- **Settling Time:** Time to reach ±5% of setpoint
- **Overshoot:** Peak deviation beyond setpoint

---

## Troubleshooting ### Simulation Won't Run

1. Check Python version: `python --version` (need ≥3.9)
2. Verify installation: `pip list | findstr numpy`
3. Check working directory: Must be project root ### PSO Not Converging
1. Increase iterations: `--override "pso.iters=200"`
2. Widen bounds in `config.yaml`
3. Try different random seed: `--seed 123` ### Performance Issues
1. Use simplified dynamics: `--override "use_full_dynamics=false"`
2. Reduce simulation duration: `--override "simulation.duration=3.0"`
3. Increase timestep: `--override "simulation.dt=0.02"` (test stability) See [User Guide - Troubleshooting](user-guide.md#troubleshooting) for complete guide.

---

## Contributing Found an issue or have a suggestion?

- Open an issue: https://github.com/theSadeQ/dip-smc-pso/issues
- Discuss improvements in [User Guide](user-guide.md)

---

## License & Citation This framework is open-source. If you use it in research, please cite: ```bibtex

@software{dip_smc_pso_2025, title={DIP SMC PSO: Double-Inverted Pendulum Sliding Mode Control with PSO Optimization}, author={...}, year={2025}, url={https://github.com/theSadeQ/dip-smc-pso}
}
```

---

**Happy Experimenting!** 🚀 For questions, consult the [User Guide](user-guide.md) or open an issue on GitHub.
