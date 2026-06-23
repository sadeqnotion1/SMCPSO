# Monte Carlo Validation Quick Start Guide

**Companion to Tutorial 05: Research Workflow** **Version:** 1.0
**Date:** 2025-10-07
**Status:** Practical quick-start examples for statistical validation

---

## Purpose This guide provides **working code examples** for Monte Carlo validation and statistical analysis to complement [Tutorial 05: Research Workflow](../tutorials/tutorial-05-research-workflow.md). While Tutorial 05 provides the research methodology, this guide focuses on **practical implementation**. **Use this guide for:**

- Quick Monte Carlo validation (10-20 trials for testing)
- Statistical analysis templates with real code
- Confidence interval calculation
- Hypothesis testing examples
- Effect size measurement

---

## Quick Monte Carlo Example (10 Trials) ### Minimal Working Example ```python

# example-metadata:

# runnable: false #!/usr/bin/env python

"""Quick Monte Carlo validation: 10 trials × 2 controllers × 1 scenario.""" import numpy as np
import subprocess
import json
from pathlib import Path # Configuration
N_TRIALS = 10 # Quick test (use 50+ for publication)
CONTROLLERS = ['classical_smc', 'sta_smc']
DURATION = 5.0 # Seconds
RESULTS_DIR = Path('monte_carlo_quick_test')
RESULTS_DIR.mkdir(exist_ok=True) # Run trials
results = []
for controller in CONTROLLERS: print(f"\\nRunning {controller}...") for trial in range(N_TRIALS): seed = 1000 + trial # Reproducible seeds # Run simulation cmd = [ 'python', 'simulate.py', '--controller', controller, '--duration', str(DURATION), '--seed', str(seed), '--no-plot' # Suppress plotting for batch runs ] try: result = subprocess.run(cmd, capture_output=True, text=True, check=True) # Parse output (example - adjust to actual output format) # Assuming simulate.py prints metrics in JSON format # In practice, you'd capture metrics from simulation results results.append({ 'controller': controller, 'trial': trial, 'seed': seed, # Placeholder metrics - replace with actual parsing 'ise': np.random.uniform(0.1, 0.5), # Example 'settling_time': np.random.uniform(2.0, 4.0), # Example }) print(f" Trial {trial+1}/{N_TRIALS} complete") except subprocess.CalledProcessError as e: print(f" Trial {trial} failed: {e}") continue # Save results
import pandas as pd
df = pd.DataFrame(results)
df.to_csv(RESULTS_DIR / 'results.csv', index=False)
print(f"\\nResults saved to: {RESULTS_DIR / 'results.csv'}")
print(df.groupby('controller')[['ise', 'settling_time']].describe())
``` **Expected Runtime:** ~2-5 minutes (depending on simulation speed)

---

## Statistical Analysis Templates ### 1. Descriptive Statistics with Confidence Intervals ```python
import pandas as pd
import numpy as np
from scipy import stats # Load results
df = pd.read_csv('monte_carlo_quick_test/results.csv') def compute_statistics(data, metric='ise', confidence=0.95): """Compute mean, std, and confidence interval.""" mean = data[metric].mean() std = data[metric].std() n = len(data) se = std / np.sqrt(n) # Standard error # Confidence interval (t-distribution) alpha = 1 - confidence t_critical = stats.t.ppf(1 - alpha/2, df=n-1) ci_lower = mean - t_critical * se ci_upper = mean + t_critical * se return { 'mean': mean, 'std': std, 'se': se, 'ci_lower': ci_lower, 'ci_upper': ci_upper, 'n': n } # Compute for each controller
for controller in df['controller'].unique(): data = df[df['controller'] == controller] stats_ise = compute_statistics(data, metric='ise') print(f"\\n{controller}:") print(f" ISE: {stats_ise['mean']:.4f} ± {stats_ise['std']:.4f}") print(f" 95% CI: [{stats_ise['ci_lower']:.4f}, {stats_ise['ci_upper']:.4f}]") print(f" Samples: {stats_ise['n']}")
``` **Example Output:**

```
classical_smc: ISE: 0.2842 ± 0.1123 95% CI: [0.2038, 0.3646] Samples: 10 sta_smc: ISE: 0.2134 ± 0.0867 95% CI: [0.1512, 0.2756] Samples: 10
``` ### 2. Hypothesis Testing (Welch's t-test) ```python

from scipy.stats import ttest_ind # Load data
df = pd.read_csv('monte_carlo_quick_test/results.csv') classical = df[df['controller'] == 'classical_smc']['ise'].values
sta = df[df['controller'] == 'sta_smc']['ise'].values # Welch's t-test (unequal variances)
t_stat, p_value = ttest_ind(classical, sta, equal_var=False) # Effect size (Cohen's d)
pooled_std = np.sqrt((classical.std()**2 + sta.std()**2) / 2)
cohens_d = (classical.mean() - sta.mean()) / pooled_std # Interpret results
alpha = 0.05
significant = p_value < alpha print("\\nHypothesis Test Results:")
print(f" H₀: No difference between controllers")
print(f" H₁: Controllers have different performance")
print(f" \\n t-statistic: {t_stat:.4f}")
print(f" p-value: {p_value:.4f}")
print(f" Significance level (α): {alpha}")
print(f" Result: {'REJECT H₀' if significant else 'FAIL TO REJECT H₀'} (p {'<' if significant else '>='} {alpha})")
print(f" \\n Effect size (Cohen's d): {cohens_d:.4f}")
print(f" Interpretation: {interpret_cohens_d(cohens_d)}") def interpret_cohens_d(d): """Interpret Cohen's d effect size.""" abs_d = abs(d) if abs_d < 0.2: return "Negligible" elif abs_d < 0.5: return "Small" elif abs_d < 0.8: return "Medium" else: return "Large"
``` **Example Output:**
```

Hypothesis Test Results: H₀: No difference between controllers H₁: Controllers have different performance t-statistic: 1.4325 p-value: 0.1702 Significance level (α): 0.05 Result: FAIL TO REJECT H₀ (p >= 0.05) Effect size (Cohen's d): 0.6812 Interpretation: Medium
``` **Interpretation:**
- p = 0.17 > 0.05: Not statistically significant (with N=10)
- Cohen's d = 0.68: Medium practical effect size
- **Action**: Increase sample size to N=50 for adequate statistical power ### 3. Power Analysis ```python
from statsmodels.stats.power import ttest_power # Calculate required sample size for desired power
effect_size = 0.68 # From Cohen's d above
alpha = 0.05
power = 0.80 # Desired power (80%) # Compute required sample size per group
from statsmodels.stats.power import tt_solve_power required_n = tt_solve_power( effect_size=effect_size, alpha=alpha, power=power, alternative='two-sided'
) print(f"\\nPower Analysis:")
print(f" Effect size (d): {effect_size}")
print(f" Significance level (α): {alpha}")
print(f" Desired power: {power}")
print(f" Required sample size per group: {np.ceil(required_n):.0f}")
print(f" \\n Current sample size: 10")
print(f" Recommendation: Increase to {np.ceil(required_n):.0f} trials per controller")
``` **Example Output:**

```
Power Analysis: Effect size (d): 0.68 Significance level (α): 0.05 Desired power: 0.80 Required sample size per group: 36 Current sample size: 10 Recommendation: Increase to 36 trials per controller
```

---

## Confidence Interval Visualization ```python

import matplotlib.pyplot as plt
import numpy as np # Load data
df = pd.read_csv('monte_carlo_quick_test/results.csv') # Compute statistics for each controller
controllers = df['controller'].unique()
stats_data = [] for ctrl in controllers: data = df[df['controller'] == ctrl]['ise'].values mean = data.mean() ci = stats.t.interval(0.95, len(data)-1, loc=mean, scale=stats.sem(data)) stats_data.append({ 'controller': ctrl, 'mean': mean, 'ci_lower': ci[0], 'ci_upper': ci[1] }) stats_df = pd.DataFrame(stats_data) # Plot
fig, ax = plt.subplots(figsize=(8, 6)) x = np.arange(len(controllers))
means = stats_df['mean'].values
ci_errors = np.array([stats_df['mean'] - stats_df['ci_lower'], stats_df['ci_upper'] - stats_df['mean']]) ax.bar(x, means, alpha=0.7, color=['blue', 'orange'])
ax.errorbar(x, means, yerr=ci_errors, fmt='none', ecolor='black', capsize=5, capthick=2, label='95% CI') ax.set_xlabel('Controller')
ax.set_ylabel('ISE (Integral Squared Error)')
ax.set_title('Controller Performance Comparison\\n(N=10 trials, 95% confidence intervals)')
ax.set_xticks(x)
ax.set_xticklabels(controllers, rotation=15)
ax.legend()
ax.grid(axis='y', alpha=0.3) plt.tight_layout()
plt.savefig('monte_carlo_quick_test/performance_comparison.png', dpi=150)
print("\\nPlot saved: monte_carlo_quick_test/performance_comparison.png")
```

---

## Practical Guidelines ### Sample Size Recommendations | Study Type | Minimum N | Recommended N | Notes |
|------------|-----------|---------------|-------|
| **Quick validation** | 10 | 20 | Check for obvious issues |
| **Preliminary study** | 20 | 30 | Initial effect size estimate |
| **Standard validation** | 30 | 50 | Adequate statistical power |
| **Publication-quality** | 50 | 100 | High confidence results |
| **High-stakes decisions** | 100 | 500+ | Minimize risk | ### Statistical Power Guidelines **For medium effect size (d=0.5):**
- N=10: Power ≈ 0.25 (25% chance of detecting effect)
- N=20: Power ≈ 0.45 (45%)
- N=30: Power ≈ 0.60 (60%)
- N=50: Power ≈ 0.82 (82%) ✅ Adequate
- N=100: Power ≈ 0.97 (97%) **Recommendation**: Aim for power ≥ 0.80 (80%) ### When to Use Which Test **Welch's t-test (recommended default):**
- Comparing two controllers
- Don't assume equal variances
- Robust to violations **Mann-Whitney U test (non-parametric):**
- Non-normal distributions
- Small sample sizes (N<30)
- Outliers present **ANOVA (Analysis of Variance):**
- Comparing 3+ controllers
- Follow up with post-hoc tests (Tukey HSD) **Kruskal-Wallis (non-parametric ANOVA):**
- Non-normal distributions
- 3+ groups
- Small samples

---

## Complete Workflow Example ```python
#!/usr/bin/env python
"""Complete Monte Carlo validation workflow with statistical analysis.""" import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt # Step 1: Run Monte Carlo (assume already completed)
# Results in: monte_carlo_quick_test/results.csv # Step 2: Load and validate data
df = pd.read_csv('monte_carlo_quick_test/results.csv')
print(f"Loaded {len(df)} trials")
print(f"Controllers: {df['controller'].unique()}")
print(f"Metrics: {[col for col in df.columns if col not in ['controller', 'trial', 'seed']]}") # Step 3: Descriptive statistics
print("\\n" + "="*60)
print("DESCRIPTIVE STATISTICS")
print("="*60)
print(df.groupby('controller').agg({ 'ise': ['count', 'mean', 'std', 'min', 'max']
}).round(4)) # Step 4: Hypothesis testing
print("\\n" + "="*60)
print("HYPOTHESIS TESTING")
print("="*60) classical = df[df['controller'] == 'classical_smc']['ise'].values
sta = df[df['controller'] == 'sta_smc']['ise'].values t_stat, p_value = stats.ttest_ind(classical, sta, equal_var=False)
print(f"Welch's t-test:")
print(f" t = {t_stat:.4f}, p = {p_value:.4f}")
print(f" Result: {'Significant' if p_value < 0.05 else 'Not significant'} at α=0.05") # Step 5: Effect size
pooled_std = np.sqrt((classical.std()**2 + sta.std()**2) / 2)
cohens_d = abs(classical.mean() - sta.mean()) / pooled_std
print(f"\\nCohen's d: {cohens_d:.4f} ({interpret_cohens_d(cohens_d)})") # Step 6: Confidence intervals
for ctrl in df['controller'].unique(): data = df[df['controller'] == ctrl]['ise'] ci = stats.t.interval(0.95, len(data)-1, loc=data.mean(), scale=stats.sem(data)) print(f"\\n{ctrl}:") print(f" Mean: {data.mean():.4f}") print(f" 95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]") # Step 7: Visualization
fig, axes = plt.subplots(1, 2, figsize=(12, 5)) # Box plot
df.boxplot(column='ise', by='controller', ax=axes[0])
axes[0].set_title('ISE Distribution by Controller')
axes[0].set_xlabel('Controller')
axes[0].set_ylabel('ISE') # Bar plot with CI
controllers = df['controller'].unique()
means = [df[df['controller'] == c]['ise'].mean() for c in controllers]
cis = [stats.t.interval(0.95, len(df[df['controller'] == c])-1, loc=df[df['controller'] == c]['ise'].mean(), scale=stats.sem(df[df['controller'] == c]['ise'])) for c in controllers]
ci_errors = np.array([[m - ci[0], ci[1] - m] for m, ci in zip(means, cis)]).T x = np.arange(len(controllers))
axes[1].bar(x, means, alpha=0.7)
axes[1].errorbar(x, means, yerr=ci_errors, fmt='none', ecolor='black', capsize=5)
axes[1].set_xlabel('Controller')
axes[1].set_ylabel('Mean ISE')
axes[1].set_title('Mean ISE with 95% CI')
axes[1].set_xticks(x)
axes[1].set_xticklabels(controllers)
axes[1].grid(axis='y', alpha=0.3) plt.tight_layout()
plt.savefig('monte_carlo_quick_test/analysis_summary.png', dpi=150)
print("\\nPlot saved: monte_carlo_quick_test/analysis_summary.png") def interpret_cohens_d(d): abs_d = abs(d) if abs_d < 0.2: return "Negligible" elif abs_d < 0.5: return "Small" elif abs_d < 0.8: return "Medium" else: return "Large"
```

---

## Troubleshooting ### Issue 1: Not Enough Samples for Statistical Power **Symptom:** p-value > 0.05 despite apparent difference in means **Solution:**

1. Calculate required sample size with power analysis
2. Re-run with larger N
3. Consider practical significance (effect size) alongside statistical significance ### Issue 2: High Variance Obscures Differences **Symptom:** Large confidence intervals, unstable means **Solution:**
1. Increase sample size (reduces standard error)
2. Control experimental conditions more tightly
3. Use stratified sampling (block by initial conditions) ### Issue 3: Non-Normal Distributions **Symptom:** Shapiro-Wilk test fails (p < 0.05) **Solution:**
1. Use non-parametric tests (Mann-Whitney instead of t-test)
2. Transform data (log, sqrt) if appropriate
3. Bootstrap confidence intervals

---

## Next Steps **After Quick Validation:**

1. ✅ Verify Monte Carlo workflow works
2. ✅ Check statistical analysis pipeline
3. ➡️ Scale up to N=50 trials for full study
4. ➡️ Add additional scenarios (parameter variations)
5. ➡️ Document results in research paper format **For Full Research Study:**
➡️ Return to [Tutorial 05: Research Workflow](../tutorials/tutorial-05-research-workflow.md)
➡️ Follow complete experimental design (50+ trials, multiple scenarios)
➡️ Prepare publication-quality figures and tables

---

**Document Status:** ✅ Practical Templates
**Last Updated:** 2025-10-07
**Validation Method:** Code templates based on scipy/statsmodels APIs
**Recommended Use:** Quick validation before full-scale studies
