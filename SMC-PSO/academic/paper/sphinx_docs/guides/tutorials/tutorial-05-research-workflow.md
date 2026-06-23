# Tutorial 05: End-to-End Research Workflow

**What This Tutorial Covers:**
This advanced tutorial guides you through a complete research workflow from formulating a hypothesis to publication-quality results. You'll conduct a rigorous comparison study (Classical SMC vs Hybrid Adaptive STA-SMC) using statistical validation, Monte Carlo analysis, and reproducible research practices suitable for academic publication.

**Who This Is For:**
- Graduate students preparing research papers on control systems
- Researchers new to rigorous experimental methodology
- Engineers validating controller improvements for publication
- Anyone wanting to conduct defensible, reproducible benchmarking studies

**What You'll Learn:**
- How to formulate testable research questions with statistical hypotheses
- Designing experiments with proper controls and statistical power
- Executing Monte Carlo studies with confidence intervals
- Analyzing results using t-tests, effect sizes, and ANOVA
- Creating publication-quality figures (matplotlib, LaTeX equations)
- Ensuring full reproducibility (random seeds, environment captures, data archiving)

**Level:** Advanced | **Duration:** 120+ minutes (spread across multiple sessions)

**Prerequisites:**
- All previous tutorials completed
- Understanding of research methodology
- Familiarity with statistical analysis

## Learning Objectives

By the end of this tutorial, you will:
- [ ] Formulate a research question for control systems
- [ ] Design rigorous experiments with statistical validation
- [ ] Execute benchmarking studies
- [ ] Analyze results and draw defensible conclusions
- [ ] Create publication-quality figures and tables
- [ ] Ensure reproducibility and open science best practices

---

## Case Study: Robustness Comparison **Research Question:**

*"Does hybrid adaptive STA-SMC provide statistically significant improvements in robustness to mass parameter uncertainty compared to classical SMC?"*

---

## Phase 1: Problem Formulation ### Step 1: Define Research Objectives **Primary Objective:**

Quantify performance degradation of classical vs hybrid SMC under ±30% cart mass variation **Secondary Objectives:**
- Compare convergence speed across parameter ranges
- Analyze control effort trade-offs
- Identify operating regimes where adaptive advantage is maximized **Success Criteria:**
- p-value < 0.05 for statistical significance
- Effect size > 20% for practical significance
- Reproducible across 50+ Monte Carlo trials ### Step 2: Literature Review **Baseline Controllers:**
- Classical SMC (Utkin, 1977)
- Hybrid Adaptive STA-SMC (Recent development, this framework) **Performance Metrics:**
- ISE (Integral Squared Error): Tracking accuracy
- Settling Time: Convergence speed
- Control Effort: Energy efficiency
- Robustness Index: Performance variance across parameter range **Hypothesis:**
H₀: No significant difference in robustness (null hypothesis)
H₁: Hybrid SMC has lower performance variance under parameter uncertainty (alternative hypothesis)

---

## Phase 2: Experimental Design ### Step 1: Define Test Scenarios Create `experiments/robustness_study/scenarios.yaml`: ```yaml

# Experimental scenarios for robustness study

scenarios: nominal: name: "Nominal System" parameters: m0: 1.0 # Cart mass (kg) m1: 0.1 m2: 0.1 initial_conditions: [0, 0, 0.1, 0, 0.15, 0] light_cart: name: "Light Cart (-30%)" parameters: m0: 0.7 # 30% lighter m1: 0.1 m2: 0.1 initial_conditions: [0, 0, 0.1, 0, 0.15, 0] heavy_cart: name: "Heavy Cart (+30%)" parameters: m0: 1.3 # 30% heavier m1: 0.1 m2: 0.1 initial_conditions: [0, 0, 0.1, 0, 0.15, 0] light_pendulums: name: "Light Pendulums (-20%)" parameters: m0: 1.0 m1: 0.08 # 20% lighter m2: 0.08 initial_conditions: [0, 0, 0.1, 0, 0.15, 0] heavy_pendulums: name: "Heavy Pendulums (+20%)" parameters: m0: 1.0 m1: 0.12 # 20% heavier m2: 0.12 initial_conditions: [0, 0, 0.1, 0, 0.15, 0]
``` ### Step 2: Monte Carlo Experimental Script Create `experiments/robustness_study/run_monte_carlo.py`: ```python
#!/usr/bin/env python
"""
Monte Carlo robustness study: Classical vs Hybrid Adaptive STA-SMC. Runs N trials for each controller × scenario combination with random seeds.
""" import numpy as np
import subprocess
import json
import yaml
from pathlib import Path
from tqdm import tqdm
import pandas as pd # Configuration
N_TRIALS = 50 # Monte Carlo sample size
CONTROLLERS = ['classical_smc', 'hybrid_adaptive_sta_smc']
SCENARIOS_FILE = 'experiments/robustness_study/scenarios.yaml'
RESULTS_DIR = Path('experiments/robustness_study/results')
RESULTS_DIR.mkdir(parents=True, exist_ok=True) # Load scenarios
with open(SCENARIOS_FILE) as f: scenarios_config = yaml.safe_load(f)
scenarios = scenarios_config['scenarios'] # Main experiment loop
results = [] for controller in CONTROLLERS: print(f"\n{'='*60}") print(f"Running trials for {controller}") print(f"{'='*60}") for scenario_name, scenario in scenarios.items(): print(f"\nScenario: {scenario['name']}") for trial in tqdm(range(N_TRIALS), desc="Trials"): # Unique seed for reproducibility seed = hash((controller, scenario_name, trial)) % (2**31) # Construct simulation command cmd = [ 'python', 'simulate.py', '--ctrl', controller, '--seed', str(seed), '--override', f"dip_params.m0={scenario['parameters']['m0']}", '--override', f"dip_params.m1={scenario['parameters']['m1']}", '--override', f"dip_params.m2={scenario['parameters']['m2']}", '--override', f"simulation.initial_conditions={scenario['initial_conditions']}", '--save', f"{RESULTS_DIR}/{controller}_{scenario_name}_{trial}.json" ] # Run simulation try: subprocess.run(cmd, check=True, capture_output=True) # Load results result_file = f"{RESULTS_DIR}/{controller}_{scenario_name}_{trial}.json" with open(result_file) as f: data = json.load(f) # Extract metrics results.append({ 'controller': controller, 'scenario': scenario_name, 'trial': trial, 'seed': seed, 'ise': data['metrics']['ise'], 'itae': data['metrics']['itae'], 'settling_time': data['metrics']['settling_time'], 'overshoot': data['metrics']['overshoot'], 'control_effort': data['metrics']['control_effort'], 'm0': scenario['parameters']['m0'], 'm1': scenario['parameters']['m1'], 'm2': scenario['parameters']['m2'], }) except subprocess.CalledProcessError as e: print(f"ERROR in trial {trial}: {e}") continue # Save raw results
df = pd.DataFrame(results)
df.to_csv(f"{RESULTS_DIR}/monte_carlo_results.csv", index=False) print(f"\n{'='*60}")
print(f"Experiment complete!")
print(f"Total trials: {len(results)}")
print(f"Results saved to: {RESULTS_DIR}/monte_carlo_results.csv")
print(f"{'='*60}")
``` ### Step 3: Run Experiment ```bash
# Install tqdm for progress bar if needed

pip install tqdm pandas # Run Monte Carlo study (takes ~2-3 hours for 50 trials × 2 controllers × 5 scenarios)
python experiments/robustness_study/run_monte_carlo.py
```

---

## Phase 3: Statistical Analysis ### Step 1: Compute Summary Statistics Create `experiments/robustness_study/analyze_results.py`: ```python
#!/usr/bin/env python
"""Analyze Monte Carlo results with statistical rigor.""" import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns # Load results
df = pd.read_csv('experiments/robustness_study/results/monte_carlo_results.csv') # Compute summary statistics per controller × scenario
summary = df.groupby(['controller', 'scenario']).agg({ 'ise': ['mean', 'std', 'min', 'max'], 'settling_time': ['mean', 'std'], 'control_effort': ['mean', 'std']
}).round(4) print("Summary Statistics:")
print(summary)
print("\n") # Compute robustness index (coefficient of variation across scenarios)
robustness = df.groupby(['controller', 'trial']).agg({ 'ise': 'std' # Standard deviation across scenarios (lower = more robust)
}) robustness_summary = robustness.groupby('controller').agg({ 'ise': ['mean', 'std']
}) print("Robustness Index (ISE std dev across scenarios):")
print(robustness_summary)
print("\n") # Statistical hypothesis testing: Welch's t-test (unequal variances)
classical_robustness = robustness.loc['classical_smc']['ise'].values
hybrid_robustness = robustness.loc['hybrid_adaptive_sta_smc']['ise'].values t_stat, p_value = stats.ttest_ind(classical_robustness, hybrid_robustness, equal_var=False) print(f"Welch's t-test:")
print(f" H₀: No difference in robustness")
print(f" t-statistic: {t_stat:.4f}")
print(f" p-value: {p_value:.6f}")
print(f" Significant (α=0.05): {'YES' if p_value < 0.05 else 'NO'}")
print("\n") # Effect size (Cohen's d)
pooled_std = np.sqrt((classical_robustness.std()**2 + hybrid_robustness.std()**2) / 2)
cohens_d = (classical_robustness.mean() - hybrid_robustness.mean()) / pooled_std print(f"Effect Size (Cohen's d): {cohens_d:.4f}")
print(f" Interpretation: ", end="")
if abs(cohens_d) < 0.2: print("Small effect")
elif abs(cohens_d) < 0.5: print("Medium effect")
else: print("Large effect")
print("\n") # 95% Confidence intervals
ci_classical = stats.t.interval(0.95, len(classical_robustness)-1, loc=classical_robustness.mean(), scale=classical_robustness.std()/np.sqrt(len(classical_robustness)))
ci_hybrid = stats.t.interval(0.95, len(hybrid_robustness)-1, loc=hybrid_robustness.mean(), scale=hybrid_robustness.std()/np.sqrt(len(hybrid_robustness))) print(f"95% Confidence Intervals (Robustness Index):")
print(f" Classical SMC: [{ci_classical[0]:.4f}, {ci_classical[1]:.4f}]")
print(f" Hybrid SMC: [{ci_hybrid[0]:.4f}, {ci_hybrid[1]:.4f}]")
``` **Run analysis:**

```bash
python experiments/robustness_study/analyze_results.py
``` **Expected Output:**

```
Welch's t-test: H₀: No difference in robustness t-statistic: 8.3421 p-value: 0.000003 Significant (α=0.05): YES Effect Size (Cohen's d): 1.24 Interpretation: Large effect 95% Confidence Intervals (Robustness Index): Classical SMC: [0.1234, 0.1567] Hybrid SMC: [0.0523, 0.0712]
``` **Interpretation:**

✅ p < 0.05: Hybrid SMC is statistically significantly more robust
✅ Cohen's d = 1.24: Large practical effect size
✅ Non-overlapping CIs: Strong evidence for difference ### Step 2: Publication-Quality Visualizations Create `experiments/robustness_study/plot_results.py`: ```python
#!/usr/bin/env python
"""Generate publication-quality figures.""" import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns # Set publication style
sns.set_context("paper", font_scale=1.5)
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.family'] = 'serif' # Load data
df = pd.read_csv('experiments/robustness_study/results/monte_carlo_results.csv') # Figure 1: Box plots - ISE across scenarios
fig, ax = plt.subplots()
df_pivot = df.pivot_table(values='ise', index='scenario', columns='controller') df_pivot.plot(kind='bar', ax=ax, color=['tab:blue', 'tab:orange'])
ax.set_ylabel('ISE')
ax.set_xlabel('Parameter Scenario')
ax.set_title('Controller Performance Under Parameter Uncertainty')
ax.legend(['Classical SMC', 'Hybrid Adaptive STA-SMC'])
ax.grid(axis='y')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('experiments/robustness_study/figures/fig1_ise_comparison.pdf', dpi=300)
plt.savefig('experiments/robustness_study/figures/fig1_ise_comparison.png', dpi=300)
print("Saved: fig1_ise_comparison.pdf") # Figure 2: Violin plots - Distribution comparison
fig, ax = plt.subplots()
sns.violinplot(data=df, x='scenario', y='ise', hue='controller', split=True, ax=ax)
ax.set_ylabel('ISE')
ax.set_xlabel('Parameter Scenario')
ax.set_title('ISE Distribution Comparison')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('experiments/robustness_study/figures/fig2_distribution.pdf', dpi=300)
print("Saved: fig2_distribution.pdf") # Figure 3: Robustness index comparison
robustness = df.groupby(['controller', 'trial']).agg({'ise': 'std'}).reset_index() fig, ax = plt.subplots()
sns.boxplot(data=robustness, x='controller', y='ise', ax=ax)
ax.set_ylabel('Robustness Index\n(ISE std dev across scenarios)')
ax.set_xlabel('Controller Type')
ax.set_title('Robustness Comparison (Lower is Better)')
ax.set_xticklabels(['Classical SMC', 'Hybrid Adaptive STA-SMC'])
plt.tight_layout()
plt.savefig('experiments/robustness_study/figures/fig3_robustness_index.pdf', dpi=300)
print("Saved: fig3_robustness_index.pdf") print("\nAll figures saved to: experiments/robustness_study/figures/")
``` **Run visualization:**
```bash

python experiments/robustness_study/plot_results.py
```

---

## Phase 4: Documentation & Reproducibility ### Step 1: Create Experimental Metadata Create `experiments/robustness_study/metadata.yaml`: ```yaml
# Experimental Metadata for Robustness Study
study: title: "Robustness Comparison of SMC Controllers Under Parameter Uncertainty" authors: ["Your Name"] date: "2025-10-05" version: "1.0" methods: controllers: - name: "Classical SMC" implementation: "src/controllers/smc/classic_smc.py" gains: [10.0, 8.0, 15.0, 12.0, 50.0, 5.0] tuning_method: "PSO optimized" - name: "Hybrid Adaptive STA-SMC" implementation: "src/controllers/smc/hybrid_adaptive_sta_smc.py" gains: [15.0, 12.0, 18.0, 15.0] tuning_method: "PSO optimized with auto-tuned STA gains" scenarios: parameter_variations: - "Cart mass: -30% to +30%" - "Pendulum masses: -20% to +20%" initial_conditions: [0, 0, 0.1, 0, 0.15, 0] monte_carlo: n_trials: 50 seed_generation: "hash(controller, scenario, trial)" metrics: primary: "Robustness Index (ISE std dev across scenarios)" secondary: ["ISE mean", "Settling Time", "Control Effort"] statistical_analysis: hypothesis_test: "Welch's t-test (two-tailed)" significance_level: 0.05 effect_size: "Cohen's d" confidence_intervals: 0.95 reproducibility: framework_version: "1.0.0" python_version: "3.9.7" dependencies: "requirements.txt (SHA256: ...)" random_seed_tracking: true data_availability: "experiments/robustness_study/results/"
``` ### Step 2: Generate Research Report Create `experiments/robustness_study/generate_report.py`: ```python
# example-metadata:

# runnable: false #!/usr/bin/env python

"""Generate automated research report.""" import pandas as pd
import yaml # Load results and metadata
df = pd.read_csv('experiments/robustness_study/results/monte_carlo_results.csv')
with open('experiments/robustness_study/metadata.yaml') as f: metadata = yaml.safe_load(f) # Generate markdown report
report = f"""
# {metadata['study']['title']} **Authors:** {', '.join(metadata['study']['authors'])}

**Date:** {metadata['study']['date']}
**Version:** {metadata['study']['version']}

---

## Abstract This study compares the robustness of Classical SMC and Hybrid Adaptive STA-SMC

controllers under mass parameter uncertainty for a double-inverted pendulum system.
Monte Carlo simulations (N={metadata['methods']['monte_carlo']['n_trials']}) were
conducted across 5 parameter variation scenarios. Results indicate Hybrid Adaptive
STA-SMC achieves {improvement:.1f}% better robustness (p < 0.001, Cohen's d = {cohens_d:.2f}). ## Methodology ### Controllers Tested
{chr(10).join(f"- **{c['name']}**: {c['implementation']}" for c in metadata['methods']['controllers'])} ### Experimental Scenarios
{chr(10).join(f"- {var}" for var in metadata['methods']['scenarios']['parameter_variations'])} ### Statistical Analysis
- Hypothesis Test: {metadata['statistical_analysis']['hypothesis_test']}
- Significance Level: α = {metadata['statistical_analysis']['significance_level']}
- Effect Size Metric: {metadata['statistical_analysis']['effect_size']} ## Results ### Summary Statistics
{{summary_table}} ### Hypothesis Test Results
{{hypothesis_results}} ## Conclusions {{conclusions}} ## Reproducibility
All code, data, and configurations are available in `experiments/robustness_study/`.
Random seeds logged for each trial. Framework version: {metadata['reproducibility']['framework_version']}. ---
""" # Fill in results (placeholder for actual computation)
# ... (run analysis and populate results) # Save report

with open('experiments/robustness_study/REPORT.md', 'w') as f: f.write(report) print("Report generated: experiments/robustness_study/REPORT.md")
```

---

## Phase 5: Archiving & Publication ### Step 1: Create Zenodo Archive ```bash
# Package experiment for archiving
cd experiments/robustness_study
tar -czf robustness_study_archive.tar.gz \ scenarios.yaml \ metadata.yaml \ results/ \ figures/ \ REPORT.md \ *.py # Upload to Zenodo.org for DOI and permanent archival
# (Follow Zenodo web interface)
``` ### Step 2: Create GitHub Release ```bash
# Tag release

git tag -a v1.0-robustness-study -m "Robustness comparison study results"
git push origin v1.0-robustness-study # Create release on GitHub with:
# - PDF figures

# - CSV results

# - Metadata YAML

# - README with instructions

```

---

## Best Practices Checklist **Before Starting:**
- [ ] Clear research question formulated
- [ ] Literature review completed (baselines identified)
- [ ] Success criteria defined (statistical + practical significance)
- [ ] Computational budget estimated **During Experiment:**
- [ ] Random seeds logged for reproducibility
- [ ] Intermediate results saved (checkpoints every 10 trials)
- [ ] Progress monitoring (tqdm, logging)
- [ ] Error handling (failed trials logged, not ignored) **Analysis:**
- [ ] Multiple statistical tests (t-test, Mann-Whitney, ANOVA if >2 groups)
- [ ] Effect size reported (Cohen's d, η²)
- [ ] Confidence intervals calculated
- [ ] Assumptions verified (normality, homogeneity of variance) **Documentation:**
- [ ] Metadata file with all experimental parameters
- [ ] Automated report generation
- [ ] Publication-quality figures (PDF + PNG)
- [ ] Code commented and organized **Reproducibility:**
- [ ] Dependency versions locked (requirements.txt)
- [ ] Random seed strategy documented
- [ ] Data and code publicly archived (Zenodo/GitHub)
- [ ] Instructions for replication provided

---

## Summary **Complete Research Workflow:** 1. **Formulation:** Define question, hypotheses, success criteria
2. **Design:** Create scenarios, metrics, statistical plan
3. **Execution:** Run Monte Carlo trials with seed tracking
4. **Analysis:** Compute statistics, test hypotheses, visualize
5. **Documentation:** Generate reports, archive data
6. **Publication:** Share code, data, figures **Key Takeaways:**
- **Rigor:** Use Monte Carlo (N ≥ 30-50) for statistical power
- **Statistics:** Report p-values, effect sizes, confidence intervals
- **Reproducibility:** Log seeds, versions, configurations
- **Automation:** Script everything for easy replication **When to Use This Workflow:** ✅ Comparing controllers scientifically
✅ Publishing research papers
✅ Validating novel algorithms
✅ Industry benchmarking studies

---

## Next Steps **Related Guides:**
- [Result Analysis How-To](../how-to/result-analysis.md): Advanced statistical analysis techniques
- [Optimization Workflows How-To](../how-to/optimization-workflows.md): PSO tuning for research studies
- [Testing & Validation How-To](../how-to/testing-validation.md): testing frameworks **Theory & Foundations (Essential for Publications):**
- [DIP Dynamics Theory](../theory/dip-dynamics.md): Cite the mathematical model - Lagrangian derivation - Linearization validity - Controllability analysis
- [SMC Theory Guide](../theory/smc-theory.md): Reference control design principles - Lyapunov stability proofs - Chattering analysis - Super-twisting mathematics
- [PSO Algorithm Theory](../theory/pso-theory.md): Document optimization methodology - Convergence guarantees - Parameter selection rationale - Benchmark comparisons **Advanced Topics:**
- **Extend Study:** Add more controllers, scenarios, or metrics
- **Real Hardware:** Validate simulation results on physical system
- **Publications:** Submit to IEEE TCST, Automatica, or control conferences
- **Open Science:** Share reproducible code on GitHub, datasets on Zenodo, preprints on arXiv **Congratulations!** You have completed a full end-to-end research project with publication-quality results and reproducibility.
