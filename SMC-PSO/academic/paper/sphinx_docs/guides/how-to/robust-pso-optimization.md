# Robust PSO Optimization Guide

## Overview

Robust PSO is an advanced optimization mode that trains controller gains across multiple diverse scenarios to prevent overfitting. Standard PSO optimizes for a single nominal initial condition, which can lead to poor generalization when the system starts from significantly different states.

**Problem Solved:**
- MT-7 Issue: Standard PSO shows 50-150x chattering degradation when tested on realistic conditions (±0.3 rad) vs training conditions (±0.05 rad)
- Overfitting: Gains optimized for narrow conditions perform poorly outside that range
- Real-world robustness: Controllers must handle diverse initial conditions in practice

**Solution:**
- Train across 15 diverse scenarios (20% nominal, 30% moderate, 50% large disturbances)
- Robust fitness function: J_robust = mean(costs) + α × max(costs)
- Validates controller performance across the full operational envelope

## Quick Start

### Basic Usage

```bash
# Train with robust PSO (recommended for production)
python simulate.py --controller classical_smc --run-pso --robust-pso --seed 42 --save gains_robust.json

# Compare with standard PSO
python simulate.py --controller classical_smc --run-pso --seed 42 --save gains_standard.json

# Validate robustness improvement
python scripts/benchmarks/validate_mt7_robust_pso.py \
  --controller classical_smc \
  --standard-gains gains_standard.json \
  --robust-gains gains_robust.json \
  --n-runs 500
```

### Quick Test (50 runs)

```bash
python scripts/benchmarks/validate_mt7_robust_pso.py \
  --controller classical_smc \
  --quick-test \
  --standard-gains gains_standard.json \
  --robust-gains gains_robust.json
```

## Configuration

### YAML Configuration

Add to `config.yaml`:

```yaml
pso:
  # Standard PSO parameters
  swarm_size: 30
  max_iters: 200
  c1: 2.0              # Cognitive coefficient
  c2: 2.0              # Social coefficient
  w: 0.7               # Inertia weight

  # Robust PSO configuration
  robustness:
    enabled: false     # Enable via --robust-pso CLI flag

    # Scenario distribution (must sum to 1.0)
    scenario_weights:
      nominal: 0.20    # 20% ±0.05 rad (training conditions)
      moderate: 0.30   # 30% ±0.15 rad (moderate disturbances)
      large: 0.50      # 50% ±0.30 rad (large disturbances)

    # Angle ranges for each scenario type
    nominal_angle_range: 0.05    # ±0.05 rad (~±3°)
    moderate_angle_range: 0.15   # ±0.15 rad (~±9°)
    large_angle_range: 0.30      # ±0.30 rad (~±17°)

    # Robust fitness function
    robustness_alpha: 0.3        # Weight for worst-case cost
                                  # J = mean + α × max

    random_seed: null            # Reproducible scenarios (null = random)
```

### Scenario Distribution

The default configuration evaluates each gain set on 15 scenarios:
- **3 nominal** (20%): ±0.05 rad initial angles
- **4 moderate** (30%): ±0.15 rad initial angles
- **8 large** (50%): ±0.30 rad initial angles

This distribution emphasizes robustness to large disturbances while maintaining nominal performance.

### Fitness Function

```python
# Standard PSO: Single scenario
J_standard = cost(gains, nominal_IC)

# Robust PSO: Multiple scenarios
costs = [cost(gains, IC) for IC in scenarios]
J_robust = mean(costs) + α × max(costs)
```

The `robustness_alpha` parameter controls the trade-off:
- **α = 0.0**: Pure average (equal weight to all scenarios)
- **α = 0.3**: Balanced (default, 30% weight on worst case)
- **α = 1.0**: Conservative (worst case dominates)

## Validation Methodology

### MT-7 Validation Script

The `validate_mt7_robust_pso.py` script compares standard vs robust PSO across 4 test conditions:

1. **Standard PSO on Nominal** (±0.05 rad): Training condition performance
2. **Standard PSO on Realistic** (±0.3 rad): Generalization test (expect degradation)
3. **Robust PSO on Nominal** (±0.05 rad): Baseline performance
4. **Robust PSO on Realistic** (±0.3 rad): Generalization test (target <5x degradation)

### Metrics

**Chattering Index:** Variance of control rate (du/dt)
- Primary metric for MT-7 validation
- Quantifies high-frequency oscillations in control signal
- Lower is better (smoother control)

**Degradation Ratio:**
```
degradation = chattering_realistic / chattering_nominal
```

**Target:**
- Standard PSO: Typically 50-150x degradation (overfitting)
- Robust PSO: <5x degradation (good generalization)

**Improvement Factor:**
```
improvement = standard_degradation / robust_degradation
```
Target: >10x improvement (robust PSO reduces overfitting by 10x)

## Example Results

### Validation Report (500 runs per condition, 2000 total)

```
================================================================================
MT-7 VALIDATION REPORT: classical_smc
================================================================================
Total Simulations: 2000 (500 per condition)

STANDARD PSO (trained on ±0.05 rad)
--------------------------------------------------------------------------------
Nominal (±0.05 rad):
  Chattering: 797.34 ± 4821.01
  Success Rate: 0.0%
Realistic (±0.3 rad):
  Chattering: 115,291.24 ± 206,713.76
  Success Rate: 0.0%
DEGRADATION: 144.59x

ROBUST PSO (trained on diverse scenarios)
--------------------------------------------------------------------------------
Nominal (±0.05 rad):
  Chattering: 359.78 ± 1771.79
  Success Rate: 0.0%
Realistic (±0.3 rad):
  Chattering: 6,937.89 ± 15,557.16
  Success Rate: 0.0%
DEGRADATION: 19.28x

SUMMARY
--------------------------------------------------------------------------------
Improvement Factor: 7.50x
  (Standard degradation / Robust degradation)
Target (<5x degradation): FAIL (19.28x > 5x)
MT-7 Issue Partially Resolved: 7.5x improvement, needs parameter tuning
================================================================================
```

### Interpretation

**Positive Results:**
- Robust PSO shows 7.5x less overfitting than standard PSO
- Chattering reduced from 115,291 to 6,938 (94% reduction) on realistic conditions
- Infrastructure operational and producing reproducible results

**Areas for Improvement:**
- Absolute degradation (19.28x) still exceeds <5x target
- Both controllers show 0% success rate (stability issues)
- Suggests need for:
  - Parameter tuning (increase α, adjust scenario weights)
  - Different controller architectures
  - Hybrid optimization strategies

## API Reference

### Command-Line Interface

```bash
# Enable robust PSO
python simulate.py --controller <name> --run-pso --robust-pso [OPTIONS]

Options:
  --robust-pso          Enable robust PSO (multi-scenario optimization)
  --seed INT           Random seed for reproducibility (default: 42)
  --save PATH          Save optimized gains to JSON file
  --config PATH        Custom config file (default: config.yaml)
```

### Validation Script

```bash
python scripts/benchmarks/validate_mt7_robust_pso.py [OPTIONS]

Options:
  --controller {classical_smc,sta_smc}
                       Controller type to test (default: classical_smc)
  --n-runs INT        Number of runs per condition (default: 500)
  --quick-test        Quick mode: 50 runs per condition (200 total)
  --standard-gains PATH
                       Path to standard PSO gains JSON
  --robust-gains PATH
                       Path to robust PSO gains JSON (REQUIRED)
  --output-dir PATH   Output directory (default: .artifacts/mt7_validation)
  --seed INT          Random seed (default: 42)
```

### Python API

```python
from src.optimization.pso.robust_tuner import RobustPSOTuner
from src.optimization.core.robust_cost_evaluator import RobustCostEvaluator
from src.config import load_config

# Load configuration
config = load_config("config.yaml")

# Create robust PSO tuner
tuner = RobustPSOTuner(
    controller_name="classical_smc",
    config=config,
    seed=42
)

# Run optimization
best_gains, best_cost = tuner.optimize()

# Save results
tuner.save_gains("gains_robust.json")

print(f"Best gains: {best_gains}")
print(f"Best robust cost: {best_cost:.4f}")
```

### Direct Cost Evaluator Usage

```python
from src.optimization.core.robust_cost_evaluator import RobustCostEvaluator
import numpy as np

# Create evaluator
evaluator = RobustCostEvaluator(
    controller_factory=lambda gains: create_controller("classical_smc", config, gains),
    sim_cfg=config.simulation,
    cost_cfg=config.pso.cost_function,
    robustness_cfg=config.pso.robustness,
    u_max=150.0,
    seed=42
)

# Evaluate gain set
test_gains = np.array([20.0, 15.0, 10.0, 5.0, 8.0, 3.0])
cost = evaluator.compute_cost(test_gains)

print(f"Robust cost: {cost:.4f}")
print(f"Evaluated on {evaluator.n_scenarios} scenarios")
```

## Troubleshooting

### High Training Time

**Symptom:** Robust PSO takes 15-30x longer than standard PSO

**Solution:**
- Expected behavior: 15 scenarios vs 1 scenario
- Reduce `pso.max_iters` for quick tests (e.g., 50 iterations)
- Use vectorized simulation (`simulate_system_batch`)
- Pre-filter infeasible particles before scenario evaluation

### Target Not Met

**Symptom:** Degradation >5x despite robust PSO

**Possible Causes:**
1. Insufficient scenario diversity: Increase `large_angle_range` to ±0.5 rad
2. Low worst-case weight: Increase `robustness_alpha` to 0.5-1.0
3. Controller architecture limitations: Try STA-SMC or hybrid controllers
4. Insufficient PSO iterations: Increase `max_iters` to 500+

**Debugging:**
```bash
# Check scenario distribution
python -c "
from src.optimization.core.robust_cost_evaluator import RobustCostEvaluator
from src.config import load_config
config = load_config('config.yaml')
# Print scenario ICs
evaluator = RobustCostEvaluator(...)
for i, ic in enumerate(evaluator.scenario_ics):
    print(f'Scenario {i}: angles = {ic[1:3]}')
"

# Visualize gain evolution
# (PSO history logging not yet implemented - future work)
```

### Zero Success Rate

**Symptom:** All simulations fail to stabilize (0% success)

**Possible Causes:**
1. Gain bounds too restrictive: Check `bounds_lower` and `bounds_upper`
2. Cost function penalizes stability: Review `cost_function` weights
3. Controller saturation: Increase `u_max` (e.g., 200N vs 150N)
4. Numerical instability: Reduce `dt` time step

**Solution:**
```yaml
pso:
  # Widen gain search space
  bounds_lower: [1.0, 1.0, 1.0, 0.1, 1.0, 0.1]
  bounds_upper: [100.0, 50.0, 30.0, 10.0, 50.0, 10.0]

  # Adjust cost weights
  cost_function:
    settling_time_weight: 10.0    # Increase stability importance
    overshoot_weight: 3.0
    steady_state_error_weight: 5.0
```

## Best Practices

### Recommended Workflow

1. **Baseline:** Train standard PSO first for comparison
   ```bash
   python simulate.py --ctrl classical_smc --run-pso --save gains_standard.json
   ```

2. **Robust Training:** Train robust PSO with default config
   ```bash
   python simulate.py --ctrl classical_smc --run-pso --robust-pso --save gains_robust.json
   ```

3. **Quick Validation:** Test with 50 runs to verify improvement
   ```bash
   python scripts/benchmarks/validate_mt7_robust_pso.py --quick-test \
     --standard-gains gains_standard.json --robust-gains gains_robust.json
   ```

4. **Full Validation:** Run 500 runs for publication-quality results
   ```bash
   python scripts/benchmarks/validate_mt7_robust_pso.py \
     --standard-gains gains_standard.json --robust-gains gains_robust.json
   ```

5. **Parameter Tuning:** If target not met, adjust `robustness_alpha` and `scenario_weights`

6. **Production Deployment:** Use robust gains for real hardware (HIL testing recommended)

### Configuration Tips

**For Maximum Robustness (Conservative):**
```yaml
pso:
  robustness:
    robustness_alpha: 1.0          # Worst-case dominates
    scenario_weights:
      nominal: 0.10                # Focus on disturbances
      moderate: 0.20
      large: 0.70
    large_angle_range: 0.5         # Very large disturbances
```

**For Balanced Performance (Default):**
```yaml
pso:
  robustness:
    robustness_alpha: 0.3          # 30% worst-case weight
    scenario_weights:
      nominal: 0.20                # Maintain nominal perf
      moderate: 0.30
      large: 0.50
    large_angle_range: 0.3
```

**For Computational Efficiency (Quick Tests):**
```yaml
pso:
  max_iters: 100                   # Reduce iterations
  robustness:
    scenario_weights:
      nominal: 0.33                # Fewer scenarios (9 total)
      moderate: 0.33
      large: 0.34
```

## Related Documentation

- [Tutorial 03: PSO Optimization](../tutorials/tutorial-03-pso-optimization.md)
- [PSO Optimization Workflow](../workflows/pso-optimization-workflow.md)
- [MT-7 Issue Tracking](.project/ai/planning/phase5/MT-7_ROBUST_PSO_IMPLEMENTATION.md)
- [API Reference: RobustPSOTuner](../../api/optimization_module_api_reference.md)
- [Chattering Analysis](../../analysis/chattering_analysis.md)

## Citation

If you use robust PSO in your research, please cite:

```bibtex
@software{dip_smc_robust_pso_2025,
  title={Robust PSO for Sliding Mode Control: Multi-Scenario Gain Optimization},
  author={[Your Name]},
  year={2025},
  url={https://github.com/theSadeQ/dip-smc-pso}
}
```

## Changelog

### v1.0.0 (November 2025)
- Initial release of robust PSO feature
- Multi-scenario cost evaluator with 15 diverse scenarios
- MT-7 validation script for overfitting comparison
- CLI integration via `--robust-pso` flag
- Configuration via `config.yaml` robustness section
- Validation results: 7.5x improvement over standard PSO

### Future Work
- Adaptive scenario selection based on convergence
- Hybrid PSO + gradient-based local refinement
- Multi-objective optimization (chattering vs settling time)
- Online learning: Update scenarios during optimization
- Hardware-in-the-loop (HIL) validation with real pendulum

---

**Last Updated:** November 7, 2025
**Status:** Operational | MT-7 Partially Resolved (7.5x improvement, needs tuning)
