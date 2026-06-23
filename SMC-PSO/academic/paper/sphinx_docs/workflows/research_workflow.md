# Research Workflow Guide

**Complete workflow for conducting research with the DIP-SMC-PSO framework: from hypothesis to publication.**



## Table of Contents

- [Overview](#overview)
- [Phase 1: Experiment Design](#phase-1-experiment-design)
- [Phase 2: Implementation](#phase-2-implementation)
- [Phase 3: Data Collection](#phase-3-data-collection)
- [Phase 4: Analysis](#phase-4-analysis)
- [Phase 5: Validation](#phase-5-validation)
- [Phase 6: Documentation](#phase-6-documentation)
- [Phase 7: Publication](#phase-7-publication)
- [Reproducibility Checklist](#reproducibility-checklist)



## Overview

### Research Lifecycle

```
Hypothesis → Design → Implementation → Experiments → Analysis → Validation → Publication
     ↑                                                                          |
     └──────────────────────────── Iteration ────────────────────────────────┘
```

### Project Strengths for Research

- **Reproducibility**: Fixed random seeds, version-pinned dependencies
- **Validation**: Built-in Lyapunov stability verification
- **Benchmarking**: Performance metrics standardized across controllers
- **Scalability**: Batch simulations, PSO optimization, Monte Carlo analysis
- **Documentation**: Citation system, theorem validation, publication-ready exports



## Phase 1: Experiment Design

### 1.1 Define Research Question

**Examples:**
- "Does adaptive SMC outperform classical SMC under parameter uncertainty?"
- "What is the optimal PSO configuration for tuning hybrid controllers?"
- "How does chattering reduction impact control effort vs. tracking accuracy?"

### 1.2 Literature Review

**Use the project's citation system:**

```bash
# Search existing citations
grep -r "sliding mode control" docs/bib/*.bib

# View citation details
python scripts/docs/validate_citations.py --show-details FORMAL-THEOREM-001
```

**Key references in `docs/bib/`:**
- `smc_theory.bib` - SMC foundations (Utkin, Edwards & Spurgeon, Slotine & Li)
- `pso_optimization.bib` - PSO algorithms (Kennedy & Eberhart, Trelea)
- `adaptive_control.bib` - Adaptive control theory (Ioannou & Sun, Åström & Wittenmark)

## 1.3 Hypothesis Formulation

**Example:**

> **Hypothesis**: Hybrid Adaptive STA-SMC achieves 30% lower settling time than Classical SMC
> while maintaining comparable control effort, under ±20% mass uncertainty.
>
> **Null Hypothesis (H₀)**: No significant difference in settling time between controllers.
>
> **Alternative Hypothesis (H₁)**: Hybrid Adaptive STA-SMC has lower settling time (p < 0.05).

### 1.4 Experimental Design

**Define:**

1. **Independent variables**: Controller type, mass uncertainty level
2. **Dependent variables**: Settling time, control effort, steady-state error
3. **Control variables**: Initial conditions, simulation duration, time step
4. **Sample size**: N = 100 Monte Carlo runs per condition (statistical power ≥ 0.8)

**Configuration:**

```yaml
# experiments/adaptive_vs_classical/config.yaml
experiment:
  name: "Adaptive SMC vs Classical SMC - Parameter Uncertainty"
  hypothesis: "Hybrid adaptive achieves 30% lower settling time"

  controllers:
    - classical_smc
    - hybrid_adaptive_sta_smc

  perturbations:
    mass_uncertainty: [-20%, -10%, 0%, +10%, +20%]

  metrics:
    - settling_time
    - control_effort
    - steady_state_error

  monte_carlo:
    num_runs: 100
    seed: 42  # Reproducibility
    initial_conditions:
      distribution: "uniform"
      ranges:
        theta1: [-0.2, 0.2]  # radians
        theta2: [-0.2, 0.2]
```



## Phase 2: Implementation

### 2.1 Controller Implementation

**If testing existing controllers:**

```python
from src.controllers.factory import create_controller

controller = create_controller('hybrid_adaptive_sta_smc', config=config)
```

**If implementing new controller:**

```python
# src/controllers/my_novel_controller.py
from src.controllers.base import BaseController

class NovelController(BaseController):
    """
    Novel control algorithm for DIP.

    Based on: Smith et al. (2024), "Advanced Control Techniques"
    DOI: 10.1234/example
    """

    def __init__(self, gains, **kwargs):
        super().__init__(gains, **kwargs)
        # Implementation

    def compute_control(self, state, last_control, history):
        # Control law
        pass
```

**Register in factory:**

```python
# src/controllers/factory.py
from src.controllers.my_novel_controller import NovelController

CONTROLLER_REGISTRY = {
    # ... existing controllers ...
    'novel_controller': NovelController,
}
```

**Write tests:**

```python
# tests/test_controllers/test_novel_controller.py
import pytest
from src.controllers.my_novel_controller import NovelController

def test_novel_controller_initialization():
    controller = NovelController(gains=[...])
    assert controller is not None

def test_novel_controller_stability():
    """Verify Lyapunov stability."""
    # Implementation
    pass
```

### 2.2 Experiment Script

```python
# experiments/adaptive_vs_classical/run_experiment.py
import numpy as np
from pathlib import Path
from src.config import load_config
from src.controllers.factory import create_controller
from src.core.dynamics import SimplifiedDynamics
from src.core.simulation_runner import SimulationRunner

def run_single_trial(controller_name, config, seed, mass_perturbation):
    """Run single simulation trial."""
    np.random.seed(seed)

    # Perturb system parameters
    config.physics.m1 *= (1 + mass_perturbation)
    config.physics.m2 *= (1 + mass_perturbation)

    # Create components
    controller = create_controller(controller_name, config=config)
    dynamics = SimplifiedDynamics(config.physics)

    # Run simulation
    sim = SimulationRunner(controller, dynamics, config.simulation)
    result = sim.run()

    # Compute metrics
    metrics = compute_metrics(result)

    return {
        'controller': controller_name,
        'seed': seed,
        'mass_perturbation': mass_perturbation,
        **metrics
    }

def compute_metrics(result):
    """Extract performance metrics."""
    # Settling time (when angle < 1 degree and stays there)
    angle_error = np.abs(np.degrees(result.states[:, 2]))
    settled_idx = np.where(angle_error < 1.0)[0]
    settling_time = result.time[settled_idx[0]] if len(settled_idx) > 0 else np.nan

    # Control effort (integral of squared control)
    control_effort = np.trapz(result.controls**2, result.time)

    # Steady-state error (last 1 second average)
    steady_state_error = np.mean(np.abs(result.states[-100:, 2]))

    return {
        'settling_time': settling_time,
        'control_effort': control_effort,
        'steady_state_error': steady_state_error
    }

if __name__ == '__main__':
    config = load_config('experiments/adaptive_vs_classical/config.yaml')

    results = []
    for controller in config.experiment.controllers:
        for mass_pert in config.experiment.perturbations.mass_uncertainty:
            for run in range(config.experiment.monte_carlo.num_runs):
                seed = config.experiment.monte_carlo.seed + run
                result = run_single_trial(controller, config, seed, mass_pert)
                results.append(result)
                print(f"Completed: {controller}, pert={mass_pert:.1%}, run={run+1}/100")

    # Save results
    import pandas as pd
    df = pd.DataFrame(results)
    df.to_csv('experiments/adaptive_vs_classical/results.csv', index=False)
```



## Phase 3: Data Collection

### 3.1 Running Experiments

```bash
# Single experiment
python experiments/adaptive_vs_classical/run_experiment.py

# Parallel execution (4 processes)
python experiments/adaptive_vs_classical/run_experiment.py --parallel 4

# Resume interrupted experiment
python experiments/adaptive_vs_classical/run_experiment.py --resume results.csv
```

## 3.2 Progress Monitoring

```python
# experiments/adaptive_vs_classical/monitor.py
import pandas as pd
import time

while True:
    df = pd.read_csv('results.csv')
    total = 2 * 5 * 100  # 2 controllers × 5 perturbations × 100 runs = 1000 trials
    completed = len(df)
    progress = 100 * completed / total

    print(f"Progress: {completed}/{total} ({progress:.1f}%)")

    if completed >= total:
        print("✓ Experiment complete!")
        break

    time.sleep(60)  # Check every minute
```

## 3.3 Data Quality Checks

```python
# experiments/adaptive_vs_classical/validate_data.py
import pandas as pd
import numpy as np

df = pd.read_csv('results.csv')

# Check for missing data
missing = df.isnull().sum()
print(f"Missing values:\n{missing}")

# Check for outliers (IQR method)
Q1 = df['settling_time'].quantile(0.25)
Q3 = df['settling_time'].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df['settling_time'] < Q1 - 1.5*IQR) | (df['settling_time'] > Q3 + 1.5*IQR)]
print(f"Outliers detected: {len(outliers)}/{len(df)}")

# Check for failed simulations (NaN metrics)
failed = df[df['settling_time'].isna()]
print(f"Failed simulations: {len(failed)}/{len(df)}")

# Data integrity report
print(f"\n✓ Data quality check complete")
print(f"  Total trials: {len(df)}")
print(f"  Valid data: {len(df) - len(failed)} ({100*(1-len(failed)/len(df)):.1f}%)")
```



## Phase 4: Analysis

### 4.1 Statistical Analysis

```python
# experiments/adaptive_vs_classical/analyze.py
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('results.csv')

# Group by controller
classical = df[df['controller'] == 'classical_smc']
adaptive = df[df['controller'] == 'hybrid_adaptive_sta_smc']

# Descriptive statistics
print("=== Settling Time (seconds) ===")
print(f"Classical SMC: {classical['settling_time'].mean():.3f} ± {classical['settling_time'].std():.3f}")
print(f"Adaptive SMC:  {adaptive['settling_time'].mean():.3f} ± {adaptive['settling_time'].std():.3f}")

# Hypothesis testing (Welch's t-test, assumes unequal variances)
t_stat, p_value = stats.ttest_ind(
    classical['settling_time'].dropna(),
    adaptive['settling_time'].dropna(),
    equal_var=False
)
print(f"\nWelch's t-test:")
print(f"  t-statistic: {t_stat:.4f}")
print(f"  p-value: {p_value:.6f}")
print(f"  Significant (p<0.05): {'Yes' if p_value < 0.05 else 'No'}")

# Effect size (Cohen's d)
mean_diff = adaptive['settling_time'].mean() - classical['settling_time'].mean()
pooled_std = np.sqrt((classical['settling_time'].var() + adaptive['settling_time'].var()) / 2)
cohens_d = mean_diff / pooled_std
print(f"  Cohen's d: {cohens_d:.3f}")

# Interpret effect size
if abs(cohens_d) < 0.2:
    effect = "negligible"
elif abs(cohens_d) < 0.5:
    effect = "small"
elif abs(cohens_d) < 0.8:
    effect = "medium"
else:
    effect = "large"
print(f"  Effect size: {effect}")

# Confidence intervals (95%)
classical_ci = stats.t.interval(0.95, len(classical)-1,
                                 classical['settling_time'].mean(),
                                 stats.sem(classical['settling_time'].dropna()))
adaptive_ci = stats.t.interval(0.95, len(adaptive)-1,
                                adaptive['settling_time'].mean(),
                                stats.sem(adaptive['settling_time'].dropna()))
print(f"\n95% Confidence Intervals:")
print(f"  Classical: [{classical_ci[0]:.3f}, {classical_ci[1]:.3f}]")
print(f"  Adaptive:  [{adaptive_ci[0]:.3f}, {adaptive_ci[1]:.3f}]")
```

## 4.2 Visualization

```python
# Box plot comparison
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Settling time
sns.boxplot(data=df, x='controller', y='settling_time', ax=axes[0])
axes[0].set_title('Settling Time Comparison')
axes[0].set_ylabel('Settling Time (s)')

# Control effort
sns.boxplot(data=df, x='controller', y='control_effort', ax=axes[1])
axes[1].set_title('Control Effort Comparison')
axes[1].set_ylabel('Control Effort (N²·s)')

# Steady-state error
sns.boxplot(data=df, x='controller', y='steady_state_error', ax=axes[2])
axes[2].set_title('Steady-State Error Comparison')
axes[2].set_ylabel('Error (rad)')

plt.tight_layout()
plt.savefig('experiments/adaptive_vs_classical/figures/comparison.png', dpi=300)
plt.show()

# Performance vs perturbation
fig, ax = plt.subplots(figsize=(10, 6))
for controller in df['controller'].unique():
    data = df[df['controller'] == controller]
    grouped = data.groupby('mass_perturbation')['settling_time'].mean()
    ax.plot(grouped.index * 100, grouped.values, '-o', label=controller, linewidth=2, markersize=8)

ax.set_xlabel('Mass Perturbation (%)', fontsize=12)
ax.set_ylabel('Mean Settling Time (s)', fontsize=12)
ax.set_title('Robustness to Parameter Uncertainty', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.savefig('experiments/adaptive_vs_classical/figures/robustness.png', dpi=300)
plt.show()
```



## Phase 5: Validation

### 5.1 Reproducibility Check

```bash
# Re-run experiment with same seeds
python experiments/adaptive_vs_classical/run_experiment.py --seed 42

# Compare results
python experiments/adaptive_vs_classical/compare_runs.py \
  --original results.csv \
  --reproduction results_reproduced.csv
```

```python
# experiments/adaptive_vs_classical/compare_runs.py
import pandas as pd
import numpy as np

df1 = pd.read_csv('results.csv')
df2 = pd.read_csv('results_reproduced.csv')

# Check if results match
metrics = ['settling_time', 'control_effort', 'steady_state_error']
for metric in metrics:
    diff = np.abs(df1[metric] - df2[metric])
    max_diff = diff.max()
    mean_diff = diff.mean()

    print(f"{metric}:")
    print(f"  Max difference: {max_diff:.6f}")
    print(f"  Mean difference: {mean_diff:.6f}")

    if max_diff < 1e-10:
        print(f"  ✓ Perfect reproducibility")
    elif max_diff < 1e-6:
        print(f"  ✓ Excellent reproducibility (numerical precision)")
    else:
        print(f"  ⚠️  Reproducibility issue detected!")
```

## 5.2 Sensitivity Analysis

```python
# Test sensitivity to hyperparameters
config_variations = {
    'dt': [0.005, 0.01, 0.02],  # Time step
    'boundary_layer': [0.1, 0.3, 0.5],  # SMC parameter
    'duration': [5.0, 10.0, 15.0]  # Simulation length
}

for param, values in config_variations.items():
    results = []
    for value in values:
        # Run with modified config
        config_modified = config.copy()
        setattr(config_modified, param, value)
        result = run_experiment(config_modified)
        results.append((value, result))

    # Analyze sensitivity
    analyze_sensitivity(param, results)
```

### 5.3 Peer Review Simulation

```python
# Create reproducibility package for reviewers
# See: docs/for_reviewers/reproduction_guide.md

# Export experiment configuration
python experiments/adaptive_vs_classical/export_config.py

# Generate results summary
python experiments/adaptive_vs_classical/generate_report.py

# Create verification script for reviewers
python experiments/adaptive_vs_classical/create_verification_script.py
```



## Phase 6: Documentation

### 6.1 Results Documentation

Create `experiments/adaptive_vs_classical/README.md`:

```markdown
# Adaptive SMC vs Classical SMC Under Parameter Uncertainty

## Hypothesis
Hybrid Adaptive STA-SMC achieves 30% lower settling time than Classical SMC under ±20% mass uncertainty.

## Method
- **Controllers**: Classical SMC, Hybrid Adaptive STA-SMC
- **Perturbations**: Mass uncertainty ∈ [-20%, +20%]
- **Trials**: 100 Monte Carlo runs per condition
- **Metrics**: Settling time, control effort, steady-state error

## Results
| Controller | Mean Settling Time (s) | Control Effort (N²·s) | Steady-State Error (rad) |
|------------|------------------------|----------------------|-------------------------|
| Classical SMC | 3.42 ± 0.51 | 1250 ± 180 | 0.0042 ± 0.0008 |
| Hybrid Adaptive | **2.38 ± 0.32** | 1180 ± 150 | 0.0035 ± 0.0006 |

**Statistical Significance**: Welch's t-test, p = 0.0001 (p < 0.05), Cohen's d = 0.82 (large effect)

## Conclusion
✓ Hypothesis confirmed: Hybrid Adaptive STA-SMC reduces settling time by 30.4% (p < 0.001)
✓ No significant increase in control effort (p = 0.12)
✓ Robust to ±20% mass uncertainty

## Reproducibility
```bash

git clone https://github.com/theSadeQ/dip-smc-pso.git
cd dip-smc-pso
git checkout v1.0-publication-ready
python experiments/adaptive_vs_classical/run_experiment.py --seed 42
```
```

### 6.2 Citation Management

```bibtex
% experiments/adaptive_vs_classical/references.bib

@article{smith2024adaptive,
  title={Adaptive Sliding Mode Control for Robotic Systems},
  author={Smith, John and Doe, Jane},
  journal={IEEE Transactions on Control Systems Technology},
  year={2024},
  volume={32},
  pages={123--145},
  doi={10.1109/TCST.2024.1234567}
}

@inproceedings{your_work2025,
  title={Comparative Analysis of Adaptive SMC Variants for Double Inverted Pendulum},
  author={Your Name},
  booktitle={Proceedings of the 2025 American Control Conference},
  year={2025},
  note={Under review}
}
```



## Phase 7: Publication

### 7.1 Manuscript Preparation

**Structure:**

1. **Abstract**: 250 words, hypothesis + results + conclusion
2. **Introduction**: Motivation, literature review, research gap, contributions
3. **Methodology**: System model, controller design, experimental setup
4. **Results**: Statistical analysis, visualizations, tables
5. **Discussion**: Interpretation, limitations, future work
6. **Conclusion**: Summary of findings

**Use project's theorem validation:**

```bash
# Validate all mathematical claims in manuscript
python scripts/docs/validate_citations.py --check-theorems

# Generate LaTeX bibliography
python scripts/docs/export_citations.py --format bibtex
```

## 7.2 Supplementary Materials

**Create supplementary package:**

```
supplementary/
├── code/                       # Experiment scripts
│   ├── run_experiment.py
│   ├── analyze.py
│   └── requirements.txt
├── data/                       # Raw data (or link to Zenodo)
│   ├── results.csv
│   └── metadata.json
├── figures/                    # High-res figures (vector format)
│   ├── comparison.pdf
│   └── robustness.pdf
└── README.md                   # Instructions for reviewers
```

**Zenodo upload:**

```bash
# Create archive
tar -czf supplementary.tar.gz supplementary/

# Upload to Zenodo (get DOI for paper)
# https://zenodo.org/

# Cite in paper:
# "Supplementary materials available at https://doi.org/10.5281/zenodo.XXXXXXX"
```

## 7.3 Preprint

```bash
# Generate arXiv-compatible PDF
python scripts/publication/generate_arxiv_package.py

# Upload to arXiv
# https://arxiv.org/
```

## 7.4 Journal Submission

**Target journals** (for control systems research):
- IEEE Transactions on Automatic Control
- Automatica
- IEEE Control Systems Letters
- Control Engineering Practice
- International Journal of Robust and Nonlinear Control

**Submission checklist:**
- [ ] Manuscript (PDF + LaTeX source)
- [ ] Figures (high-resolution, vector format)
- [ ] Supplementary materials (code + data)
- [ ] Cover letter highlighting contributions
- [ ] Suggested reviewers (3-5 experts)
- [ ] ORCID iD and funding information



## Reproducibility Checklist

### Before Publication

- [ ] **Version control**: All code committed to git with tags
- [ ] **Dependencies**: Pinned versions in `requirements.txt`
- [ ] **Random seeds**: Fixed seeds documented
- [ ] **Configuration**: All hyperparameters in YAML configs
- [ ] **Data**: Raw data archived (Zenodo, Figshare)
- [ ] **Documentation**: README with reproduction instructions
- [ ] **Testing**: Reproduction verified on clean environment
- [ ] **Citation**: All external sources properly cited

### Reproducibility Package

```
reproduction/
├── README.md              # Step-by-step instructions
├── environment.yml        # Conda environment (Python 3.9)
├── requirements.txt       # Pip dependencies (pinned versions)
├── config.yaml            # Exact experiment configuration
├── run_reproduction.sh    # Automated reproduction script
├── verify_results.py      # Compare reproduction vs. published
└── expected_results.csv   # Ground truth results
```

**Example `README.md`:**

```markdown
# Reproduction Instructions

## Environment Setup
```bash

conda create -n dip-reproduce python=3.9
conda activate dip-reproduce
pip install -r requirements.txt
```

## Run Experiments
```bash

./run_reproduction.sh
```

Expected runtime: ~2 hours on 4-core CPU

## Verify Results
```bash

python verify_results.py --tolerance 1e-6
```

Should output: ✓ All results match within tolerance
```



## Additional Resources

- **Reproducibility Guide**: [FAIR Principles](https://www.go-fair.org/fair-principles/)
- **Statistical Power Analysis**: G*Power software
- **Data Repositories**: Zenodo, Figshare, Dryad
- **Preprint Servers**: arXiv, TechRxiv
- **Version Control**: Git, GitHub, GitLab
- **Citation Management**: Zotero, Mendeley, BibTeX



**Last Updated:** 2025-10-09
**Maintainer:** DIP-SMC-PSO Team
