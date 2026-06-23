# Simulation Validation Guide

**Purpose:** Ensure simulation results are physically plausible, statistically robust, and reproducible.

## Why Validate Simulations?

Validation is critical for:
- **Reproducibility:** Independent researchers can replicate results
- **Correctness:** Control algorithms behave as theoretically predicted
- **Benchmarking:** Fair comparison between different controllers
- **Academic Integrity:** Results meet peer-review standards

## Validation Philosophy

This project employs a **4-stage validation workflow**:

1. **Setup Validation** - Verify initial conditions, parameters, and constraints before execution
2. **Runtime Validation** - Monitor state bounds, physics consistency, and numerical stability during simulation
3. **Post-Processing Validation** - Apply statistical tests, confidence intervals, and convergence analysis after completion
4. **Benchmark Comparison** - Compare against established baselines using standardized metrics

Each stage catches different classes of errors, from configuration mistakes (stage 1) to subtle numerical issues (stage 2) to statistical anomalies (stage 3).

## Quick Links to Detailed Guides

### Practical Implementations
- **[Validation Examples](validation_examples.md)** - Concrete validation patterns with code
- **[Validation Workflow](validation_workflow.md)** - Step-by-step validation procedures

### API References
- **[Simulation Validation](../reference/simulation/validation___init__.md)** - Core validation classes and methods
- **[Statistical Validation](../reference/analysis/validation_statistics.md)** - Confidence intervals, hypothesis tests

### Specialized Workflows
- **[Monte Carlo Validation](../guides/workflows/monte-carlo-validation-quickstart.md)** - Robustness testing via randomized trials
- **[Benchmarking Guide](../testing/benchmarking_framework_technical_guide.md)** - Performance comparison methodology

## Simulation Validation Workflow

### 1. Setup Validation
**Goal:** Catch configuration errors before expensive computation

- Validate initial conditions (e.g., theta in [-pi, pi], velocities finite)
- Check parameter ranges (masses > 0, lengths > 0, friction >= 0)
- Verify simulation settings (dt > 0, T > dt, numerical method valid)

**Tools:** `src.plant.core.state_validation`, `src.utils.validation`

### 2. Runtime Validation
**Goal:** Detect instabilities and constraint violations during execution

- Monitor state bounds (prevent divergence, NaN, Inf)
- Check physics consistency (energy conservation, momentum balance)
- Track numerical stability (integration error, chattering)

**Tools:** `src.reference.simulation.safety_monitors`, `src.utils.monitoring.stability`

### 3. Post-Processing Validation
**Goal:** Ensure statistical rigor and reproducibility

- Compute confidence intervals (95% CI for all metrics)
- Run hypothesis tests (Welch's t-test for comparisons, ANOVA for multi-group)
- Verify convergence (PSO optimization, Monte Carlo sampling)

**Tools:** `src.utils.analysis.validation_statistics`, `scipy.stats`

### 4. Benchmark Comparison
**Goal:** Fair, standardized comparison across controllers

- Use common initial conditions (reproducible seeds)
- Apply identical metrics (settling time, overshoot, chattering, energy)
- Report statistical significance (p-values, effect sizes)

**Tools:** `src.utils.analysis.validation_benchmarking`

## Example: Validating a Controller Comparison

```python
# See validation_examples.md for complete implementation
from src.utils.validation import validate_simulation_config
from src.utils.analysis.validation_statistics import compute_confidence_interval

# 1. Setup validation
config = load_config("config.yaml")
validate_simulation_config(config)  # Raises ValueError if invalid

# 2. Runtime validation (automatic via SimulationRunner)
results = run_simulation(controller, dynamics, initial_state)

# 3. Post-processing validation
ci_settling = compute_confidence_interval(results['settling_times'], alpha=0.05)
print(f"Settling time: {ci_settling.mean:.2f} +/- {ci_settling.margin:.2f}s")

# 4. Benchmark comparison
compare_controllers([smc_results, sta_results], metrics=['settling', 'chattering'])
```

---

**Next Steps:**
- **New users:** Start with [Validation Examples](validation_examples.md) for hands-on code
- **API reference:** See [Simulation Validation](../reference/simulation/validation___init__.md) for class documentation
- **Advanced:** Explore [Monte Carlo Validation](../guides/workflows/monte-carlo-validation-quickstart.md) for robustness testing
