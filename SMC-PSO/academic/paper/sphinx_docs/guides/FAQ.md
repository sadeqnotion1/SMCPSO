# Frequently Asked Questions (FAQ)

**Last Updated:** November 12, 2025
**Version:** 1.0

This FAQ covers common questions about the DIP-SMC-PSO framework, from installation to advanced usage.

---

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Running Simulations](#running-simulations)
3. [PSO Optimization](#pso-optimization)
4. [Controllers](#controllers)
5. [HIL & Deployment](#hil--deployment)

---

## Installation & Setup

### Q1.1: What Python version is required?

**A:** Python 3.9 or higher is required. Python 3.10-3.11 are recommended for best performance.

**Verification:**
```bash
python --version  # Should show Python 3.9.x or higher
```

**See Also:** [Getting Started Guide](guides/getting-started.md)

---

### Q1.2: Why do I get "ModuleNotFoundError: No module named 'numpy'"?

**A:** Dependencies are not installed. Install all required packages:

```bash
pip install -r requirements.txt
```

**Common Causes:**
- Wrong virtual environment activated
- pip installed to different Python version
- Virtual environment not created

**Solution:** Create fresh virtual environment:
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

**See Also:** [Installation Guide](guides/installation.md)

---

### Q1.3: How do I run simulations on Windows vs Linux?

**A:** The framework is cross-platform. Key differences:

**Windows:**
- Use `python` (not `python3`)
- Path separator: backslash `\`
- Virtual env activation: `.venv\Scripts\activate`

**Linux/Mac:**
- Use `python3`
- Path separator: forward slash `/`
- Virtual env activation: `source .venv/bin/activate`

**See Also:** [Platform-Specific Installation](guides/getting-started.md#platform-specific-notes)

---

### Q1.4: What if I don't have a GPU? Can I still run simulations?

**A:** Yes! The framework runs on CPU-only systems. GPU is not required for any functionality.

**Performance:**
- Single simulation: <1 second (CPU sufficient)
- Monte Carlo (N=100): 30-60 seconds (CPU acceptable)
- PSO optimization: 5-10 minutes (CPU acceptable)

**See Also:** [Performance Guide](guides/performance.md)

---

### Q1.5: How do I check if installation was successful?

**A:** Run the test suite:

```bash
python -m pytest tests/ -v
```

**Expected:** All tests pass (2001+ tests). A few warnings are acceptable.

**See Also:** [Testing Guide](development/testing-guide.md)

---

## Running Simulations

### Q2.1: How do I run my first simulation?

**A:** Use the CLI with default settings:

```bash
python simulate.py --ctrl classical_smc --plot
```

**This will:**
1. Load default configuration from `config.yaml`
2. Create Classical SMC controller
3. Run 10-second simulation
4. Display plots (theta1, cart position, control input)

**See Also:** [Tutorial 01: First Simulation](guides/tutorials/tutorial-01-first-simulation.md)

---

### Q2.2: How do I interpret simulation plots?

**A:** Standard plots show:

**Plot 1 - Theta1 (Link 1 Angle):**
- Should converge to 0 (upright position)
- Settling time: Time to reach and stay within ±5% of equilibrium
- Overshoot: Maximum deviation from 0

**Plot 2 - Cart Position:**
- Should stay near 0 (cart doesn't drift)
- Large deviations indicate poor tuning

**Plot 3 - Control Input:**
- Should start large, then decrease as system stabilizes
- Chattering: High-frequency oscillations (undesirable but common in SMC)

**See Also:** [Understanding Results](guides/understanding-results.md)

---

### Q2.3: My simulation diverges (angles grow unbounded). What's wrong?

**A:** Common causes:

**Cause 1: Gains too low**
- **Solution:** Increase switching gain K (try 50, 100, 150)

**Cause 2: Initial conditions too extreme**
- **Solution:** Use smaller initial angles (default: 10 degrees)

**Cause 3: Time step too large**
- **Solution:** Decrease dt in `config.yaml` (try 0.005 or 0.001)

**Cause 4: Wrong controller type**
- **Solution:** Try STA or Adaptive SMC (more robust)

**See Also:** [Troubleshooting Guide](guides/troubleshooting.md)

---

### Q2.4: How do I save simulation results?

**A:** Use `--save` flag:

```bash
python simulate.py --ctrl classical_smc --save results.json
```

**Output format (JSON):**
```json
{
  "settling_time": 3.2,
  "max_theta1": 0.15,
  "control_effort": 250.5,
  "converged": true
}
```

**See Also:** [CLI Reference](guides/cli-reference.md)

---

### Q2.5: Can I run multiple simulations in parallel?

**A:** Yes, use the batch simulator:

```python
from src.core.vector_sim import run_batch_simulation

results = run_batch_simulation(
    controller, dynamics, initial_conditions,
    sim_params, n_cores=4
)
```

**Performance:** 4x speedup on 4-core CPU for Monte Carlo analysis.

**See Also:** [Batch Simulation Guide](guides/batch-simulation.md)

---

## PSO Optimization

### Q3.1: How long does PSO optimization take?

**A:** Depends on swarm size and iterations:

| Configuration | Time (CPU) | Quality |
|---------------|------------|---------|
| N=10, iters=20 | 2 minutes | Poor (quick test) |
| N=30, iters=50 | 8 minutes | Good (default) |
| N=50, iters=100 | 30 minutes | Excellent (publication) |

**Recommendation:** Start with N=30, iters=50 for initial tuning.

**See Also:** [Tutorial 03: PSO Optimization](guides/tutorials/tutorial-03-pso-optimization.md)

---

### Q3.2: My PSO converges to poor solution. How do I fix this?

**A:** Common issues and fixes:

**Issue 1: Premature convergence (diversity drops too fast)**
- **Solution:** Increase swarm size (N=50), use adaptive inertia

**Issue 2: Stuck in local minimum**
- **Solution:** Widen bounds, run PSO multiple times with different seeds

**Issue 3: Cost function poorly designed**
- **Solution:** Check normalization, balance objective weights

**See Also:** [Tutorial 07: Convergence Diagnostics](guides/tutorials/tutorial-07-multi-objective-pso.md#section-4)

---

### Q3.3: How do I customize the PSO cost function?

**A:** Modify `config.yaml` weights:

```yaml
pso:
  cost_function:
    weights:
      ise: 0.4          # Tracking error
      itae: 0.3         # Convergence speed
      control_effort: 0.2  # Energy
      overshoot: 0.1    # Peak deviation
```

**For advanced customization:** Implement custom cost function in Python.

**See Also:** [Tutorial 07: Custom Cost Functions](guides/tutorials/tutorial-07-multi-objective-pso.md#section-2)

---

### Q3.4: Can I optimize for multiple objectives (e.g., speed AND energy)?

**A:** Yes! Use weighted sum or generate Pareto frontier:

**Weighted Sum:**
```python
cost = w1 * (settling_time / 5.0) + w2 * (energy / 300.0)
```

**Pareto Frontier:** Sweep weights from 0 to 1, plot tradeoffs.

**See Also:** [Tutorial 07: Multi-Objective PSO](guides/tutorials/tutorial-07-multi-objective-pso.md)

---

### Q3.5: How do I know if PSO converged successfully?

**A:** Check convergence metrics:

**Good Convergence:**
- [OK] Cost decreases monotonically (never increases)
- [OK] Improvement rate <0.1% for last 20 iterations
- [OK] Diversity decreases gradually (not abruptly)
- [OK] Final cost significantly lower than initial (>50% reduction)

**Bad Convergence:**
- [ERROR] Cost plateaus at iteration 10-30 (premature)
- [ERROR] High cost variance throughout (not converging)
- [ERROR] Diversity drops to <1% early (loss of exploration)

**See Also:** [PSO Diagnostics Guide](guides/pso-diagnostics.md)

---

## Controllers

### Q4.1: Which controller should I use for my application?

**A:** Depends on requirements:

**High Performance (speed priority):**
- Use: STA SMC or Hybrid STA
- Tradeoff: Higher chattering

**High Robustness (uncertainty, disturbances):**
- Use: Adaptive SMC or Hybrid STA
- Tradeoff: Slower transients, higher computational cost

**Energy Efficiency (battery-powered):**
- Use: Classical SMC with optimized gains
- Tradeoff: Lower robustness

**Smoothness (low chattering):**
- Use: STA SMC or boundary layer Classical SMC
- Tradeoff: Slightly slower response

**See Also:** [Tutorial 06: Controller Selection](guides/tutorials/tutorial-06-robustness-analysis.md#section-5)

---

### Q4.2: How do I tune controller gains manually?

**A:** Use iterative tuning approach:

**Step 1: Start with default gains**
- k1=10, k2=8, lambda1=15, lambda2=12, K=50, epsilon=0.01

**Step 2: Adjust switching gain K**
- Too low: System diverges or oscillates
- Too high: Excessive chattering
- Target: K=30-100 for most applications

**Step 3: Adjust boundary layer epsilon (Classical SMC only)**
- Too low: Chattering
- Too high: Steady-state error
- Target: epsilon=0.01-0.1

**Step 4: Fine-tune surface gains (k1, k2, lambda1, lambda2)**
- Increase for faster response, decrease for smoothness

**See Also:** [Manual Tuning Guide](guides/manual-tuning.md)

---

### Q4.3: What's the difference between Classical SMC and STA?

**A:** Key differences:

| Aspect | Classical SMC | Super-Twisting (STA) |
|--------|---------------|----------------------|
| **Order** | 1st order | 2nd order |
| **Chattering** | Higher | Lower |
| **Robustness** | Good | Excellent |
| **Complexity** | Simple | Moderate |
| **Gains** | 6 gains | 6 gains |

**When to use STA:** Higher disturbances, smoothness required, research applications.

**See Also:** [SMC Theory](theory/smc-theory.md)

---

## HIL & Deployment

### Q5.1: How do I test controllers on real hardware?

**A:** Use Hardware-in-the-Loop (HIL) framework:

**Step 1: Start plant server** (on hardware computer)
```bash
python -m src.hil.plant_server --port 5555
```

**Step 2: Run controller client** (on control computer)
```bash
python simulate.py --run-hil --host 192.168.1.100 --port 5555
```

**See Also:** [HIL Quickstart Guide](guides/hil-quickstart.md)

---

### Q5.2: What safety protocols should I follow for real hardware?

**A:** Essential safety measures:

**Pre-Deployment:**
- [x] Test in simulation 100+ times (Monte Carlo)
- [x] Verify stability margins (Lyapunov analysis)
- [x] Implement emergency stop (hardware button)
- [x] Limit workspace (physical barriers)

**During Testing:**
- [x] Start with low gains (50% of optimized)
- [x] Monitor control input (saturate at safe limits)
- [x] Have kill switch within arm's reach
- [x] Test disturbance rejection gradually (start with 10N)

**See Also:** [Safety Protocol](guides/safety-protocol.md)

---

## Additional Resources

**Getting Help:**
- [GitHub Issues](https://github.com/theSadeQ/dip-smc-pso/issues): Bug reports, feature requests
- [GitHub Discussions](https://github.com/theSadeQ/dip-smc-pso/discussions): General questions
- [Documentation](https://theSadeQ.github.io/dip-smc-pso/): Complete documentation

**Learning Resources:**
- [Tutorial Series](guides/tutorials/): 5 tutorials (beginner to advanced)
- [Interactive Exercises](guides/exercises/): 5 hands-on exercises
- [Theory Documentation](theory/): SMC fundamentals, PSO theory

**Contributing:**
- [Contributing Guide](development/contributing.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

---

**FAQ Version:** 1.0
**Last Updated:** November 12, 2025
**Entries:** 22 (5 categories)
**Status:** Complete

---

**Can't find your question?** Open a [GitHub Discussion](https://github.com/theSadeQ/dip-smc-pso/discussions) or check the [complete documentation](docs/index.md).
