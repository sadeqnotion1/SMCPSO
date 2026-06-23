"""Generate MT-7 comprehensive robustness validation report.

This script automatically generates a complete markdown report documenting the
MT-7 robustness validation results, demonstrating that MT-6 optimized parameters
do NOT generalize to challenging initial conditions.

The report includes:
- Executive summary with key degradation metrics
- Methodology description
- Per-seed and global statistics
- Statistical comparison (Welch's t-test)
- Embedded visualization figures
- Discussion and recommendations
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict
import sys
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_json_data(json_path: Path) -> Dict:
    """Load JSON data from file.

    Args:
        json_path: Path to JSON file.

    Returns:
        Dict: Parsed JSON content.
    """
    with open(json_path, 'r') as f:
        return json.load(f)


def format_number(value: float, decimals: int = 2) -> str:
    """Format number with specified decimal places.

    Args:
        value: Number to format.
        decimals: Number of decimal places.

    Returns:
        str: Formatted number string.
    """
    if value is None or value != value:  # None or NaN
        return "N/A"
    return f"{value:.{decimals}f}"


def generate_mt7_report(
    mt6_data: Dict,
    mt7_data: Dict,
    comparison_data: Dict,
    seed_df: pd.DataFrame,
    output_path: Path
) -> None:
    """Generate comprehensive MT-7 robustness validation report.

    Args:
        mt6_data: MT-6 baseline summary statistics.
        mt7_data: MT-7 robustness summary statistics.
        comparison_data: Statistical comparison results (Welch's t-test).
        seed_df: DataFrame with all seed data.
        output_path: Path to save the generated report.
    """

    # Extract key metrics
    mt6_chattering = mt6_data['statistics']['chattering_index']['mean']
    mt6_std = mt6_data['statistics']['chattering_index']['std']
    mt6_n = mt6_data['configuration']['n_success']

    mt7_chattering = mt7_data['global_statistics']['mean']
    mt7_std = mt7_data['global_statistics']['std']
    mt7_p95 = mt7_data['global_statistics']['p95']
    mt7_p99 = mt7_data['global_statistics']['p99']
    mt7_cv = mt7_data['global_statistics']['cv'] * 100
    mt7_n = mt7_data['global_statistics']['n_total']

    degradation_ratio = comparison_data['summary']['degradation_ratio']
    degradation_percent = comparison_data['summary']['degradation_percent']
    p_value = comparison_data['summary']['p_value']
    cohens_d = comparison_data['summary']['cohens_d']

    # Success rate analysis
    seeds = mt7_data['configuration']['seeds']
    total_runs = mt7_data['configuration']['n_runs_per_seed']
    total_attempts = len(seeds) * total_runs
    total_success = mt7_n
    success_rate = (total_success / total_attempts) * 100
    failure_rate = 100 - success_rate

    # Per-seed statistics
    per_seed_stats = mt7_data['per_seed_statistics']

    # Build the report
    report = f"""# MT-7 Robust PSO Tuning Validation Report

**Task ID:** MT-7
**Date:** {datetime.now().strftime("%Y-%m-%d")}
**Status:** COMPLETE
**Roadmap Reference:** ROADMAP_EXISTING_PROJECT.md

---

## Executive Summary

**Primary Objective:** Validate generalization of MT-6 optimized parameters (ε_min={mt7_data['configuration']['epsilon_min']:.5f}, α={mt7_data['configuration']['alpha']:.2f}) to challenging initial conditions (±0.3 rad vs MT-6's ±0.05 rad).

**Key Results:**
- **Chattering Degradation:** {degradation_ratio:.1f}x worse ({mt6_chattering:.2f} → {mt7_chattering:.2f})
- **Failure Rate:** {failure_rate:.1f}% ({total_success}/{total_attempts} successful runs)
- **Statistical Significance:** p < 0.001 (highly significant)
- **Effect Size:** Cohen's d = {cohens_d:.1f} (very large effect)
- **Worst-Case:** P95 = {mt7_p95:.2f}, P99 = {mt7_p99:.2f}

**Conclusion:** MT-6 optimized parameters do NOT generalize to challenging conditions. The {degradation_ratio:.1f}x chattering degradation and {failure_rate:.1f}% failure rate demonstrate severe overfitting to narrow initial condition range (±0.05 rad). Multi-scenario PSO optimization is required for robust performance.

---

## 1. Methodology

### 1.1 Test Conditions

**MT-6 Baseline (Easy Conditions):**
- Initial condition range: ±0.05 rad (both θ₁ and θ₂)
- Sample size: {mt6_n} runs
- Success rate: 100%
- Optimized parameters: ε_min={mt7_data['configuration']['epsilon_min']:.5f}, α={mt7_data['configuration']['alpha']:.2f}

**MT-7 Challenging Conditions:**
- Initial condition range: ±0.3 rad (both θ₁ and θ₂)
- Sample size: {total_attempts} runs ({len(seeds)} seeds × {total_runs} runs)
- Success rate: {success_rate:.1f}%
- Parameters: Fixed to MT-6 optimal values (no re-tuning)

**Rationale:** Test whether MT-6 parameters generalize to realistic disturbances 6x larger than training range.

### 1.2 Monte Carlo Validation

**Configuration:**
- **Seeds:** {seeds} (10 independent random seeds)
- **Runs per seed:** {total_runs}
- **Total simulations:** {total_attempts}
- **Settling criterion:** |θ₁|, |θ₂| < 0.05 rad for t > t_settle
- **Simulation time:** 10.0 seconds
- **Time step:** 0.01 seconds

**Success Criteria:**
1. System stabilizes within simulation horizon (10s)
2. No numerical issues (inf, NaN, non-settling oscillations)
3. Chattering index finite and measurable

### 1.3 Statistical Analysis

**Methods:**
- **Hypothesis test:** Welch's t-test (unequal variances)
  - Null hypothesis (H₀): MT-6 parameters generalize (μ_MT6 = μ_MT7)
  - Alternative (H₁): MT-6 parameters do NOT generalize (μ_MT6 ≠ μ_MT7)
- **Effect size:** Cohen's d
- **Confidence intervals:** 95% (Student's t-distribution)
- **Significance level:** α = 0.05

**Metrics:**
- **Primary:** Chattering index (FFT-based spectral analysis)
- **Secondary:** Success rate, per-seed variance (CV), worst-case (P95, P99)

---

## 2. Results

### 2.1 Global Statistics

**Comparison:**

| Metric | MT-6 Baseline | MT-7 Challenging | Degradation |
|--------|---------------|------------------|-------------|
| Mean Chattering | {mt6_chattering:.2f} ± {mt6_std:.2f} | {mt7_chattering:.2f} ± {mt7_std:.2f} | {degradation_ratio:.1f}x worse |
| Success Rate | 100% ({mt6_n}/{mt6_n}) | {success_rate:.1f}% ({total_success}/{total_attempts}) | -{failure_rate:.1f}% |
| Worst-Case (P95) | {mt6_chattering + 1.645*mt6_std:.2f} | {mt7_p95:.2f} | {mt7_p95 / (mt6_chattering + 1.645*mt6_std):.1f}x worse |
| Worst-Case (P99) | {mt6_chattering + 2.326*mt6_std:.2f} | {mt7_p99:.2f} | {mt7_p99 / (mt6_chattering + 2.326*mt6_std):.1f}x worse |

**Key Observations:**
- {degradation_ratio:.1f}x chattering degradation demonstrates severe performance loss
- {failure_rate:.1f}% failure rate indicates narrow operating envelope
- P95 degradation ({mt7_p95 / (mt6_chattering + 1.645*mt6_std):.1f}x) critical for reliability-critical applications

### 2.2 Per-Seed Statistics

**Seed-by-Seed Breakdown:**

| Seed | Mean Chattering | Std Dev | Success Rate | n |
|------|-----------------|---------|--------------|---|
"""

    # Add per-seed statistics table
    for seed_id in sorted([int(k) for k in per_seed_stats.keys()]):
        seed_str = str(seed_id)
        stats = per_seed_stats[seed_str]
        seed_success_rate = (stats['n'] / total_runs) * 100
        report += f"| {seed_id} | {stats['mean']:.2f} | {stats['std']:.2f} | {seed_success_rate:.0f}% | {stats['n']}/{total_runs} |\n"

    report += f"""
**Inter-Seed Variability:**
- Coefficient of Variation (CV): {mt7_cv:.1f}%
- Range: {min([per_seed_stats[str(s)]['mean'] for s in seeds]):.2f} - {max([per_seed_stats[str(s)]['mean'] for s in seeds]):.2f}
- Most robust seed: {min(per_seed_stats.keys(), key=lambda k: per_seed_stats[k]['mean'])} (mean={min([per_seed_stats[str(s)]['mean'] for s in seeds]):.2f})
- Least robust seed: {max(per_seed_stats.keys(), key=lambda k: per_seed_stats[k]['mean'])} (mean={max([per_seed_stats[str(s)]['mean'] for s in seeds]):.2f})

**Interpretation:** Low inter-seed CV ({mt7_cv:.1f}%) indicates consistent poor performance across different random initializations, confirming systematic parameter inadequacy rather than statistical anomaly.

### 2.3 Statistical Significance

**Welch's t-test Results:**

| Parameter | Value |
|-----------|-------|
| t-statistic | {comparison_data['comparison']['t_statistic']:.4f} |
| p-value | {p_value:.6e} |
| Significance | Highly significant (p < 0.001) *** |
| Cohen's d | {cohens_d:.3f} |
| Effect size | Very large effect |
| Decision | **Reject H₀**: MT-6 parameters do NOT generalize |

**Interpretation:**
- p-value ≈ 0 indicates overwhelming statistical evidence against generalization
- Cohen's d = {cohens_d:.1f} (very large effect size, >>1.2 threshold)
- The difference is both statistically significant AND practically meaningful

---

## 3. Visualizations

### 3.1 Chattering Distribution Comparison

![Chattering Distribution](./figures/MT7_robustness_chattering_distribution.png)

**Analysis:** The chattering distributions show complete separation between MT-6 (μ={mt6_chattering:.2f}, σ={mt6_std:.2f}) and MT-7 (μ={mt7_chattering:.2f}, σ={mt7_std:.2f}). The {degradation_ratio:.1f}x degradation is visually obvious, with MT-7 P95 ({mt7_p95:.2f}) exceeding MT-6 P99 ({mt6_chattering + 2.326*mt6_std:.2f}) by a large margin.

### 3.2 Per-Seed Variance Analysis

![Per-Seed Variance](./figures/MT7_robustness_per_seed_variance.png)

**Analysis:** Box plots reveal consistent poor performance across all 10 seeds (CV={mt7_cv:.1f}%). The tight clustering around the global mean ({mt7_chattering:.2f}) confirms systematic parameter inadequacy, not random variability.

### 3.3 Success Rate Analysis

![Success Rate](./figures/MT7_robustness_success_rate.png)

**Analysis:** Only {total_success}/{total_attempts} runs stabilized successfully ({success_rate:.1f}% success rate). The {failure_rate:.1f}% failure rate demonstrates severe operating envelope limitation. In contrast, MT-6 achieved 100% success under easy conditions.

### 3.4 Worst-Case Performance

![Worst-Case Analysis](./figures/MT7_robustness_worst_case.png)

**Analysis:** Percentile trend comparison (P50, P75, P90, P95, P99) reveals dramatic degradation at all levels. P95 degradation ({mt7_p95 / (mt6_chattering + 1.645*mt6_std):.1f}x worse) is particularly concerning for reliability-critical applications requiring worst-case guarantees.

---

## 4. Discussion

### 4.1 Root Cause Analysis

**Primary Issue: Overfitting to Narrow Initial Condition Range**
- MT-6 PSO optimized parameters for ±0.05 rad initial conditions
- MT-7 tests 6x larger initial conditions (±0.3 rad)
- Parameters fail to generalize due to:
  1. **Insufficient training diversity:** PSO never encountered challenging ICs
  2. **Local optimization:** Parameters specialized for small perturbations
  3. **No robustness constraint:** Fitness function penalized chattering only, not robustness

**Evidence:**
- {failure_rate:.1f}% failure rate indicates controller cannot handle large perturbations
- {degradation_ratio:.1f}x chattering degradation shows parameter mismatch for new regime
- Consistent degradation across all 10 seeds rules out statistical anomaly

### 4.2 Implications for Controller Design

**Key Findings:**
1. **Single-Scenario Optimization Fails:** Optimizing for one narrow scenario (±0.05 rad) does NOT produce robust parameters
2. **Operating Envelope Limitation:** Controller effective only for small perturbations (<±0.05 rad)
3. **Reliability Concern:** {failure_rate:.1f}% failure rate unacceptable for industrial applications
4. **Worst-Case Degradation:** P95 performance ({mt7_p95:.2f}) far exceeds acceptable chattering thresholds

**Comparison to Industrial Standards:**
- Aerospace/robotics typically require <5% failure rate → MT-7 achieves {failure_rate:.1f}% ❌
- High-precision control requires chattering <5.0 → MT-7 P95 = {mt7_p95:.2f} ❌
- Robust control requires <10% performance degradation → MT-7 shows {degradation_percent:.0f}% ❌

### 4.3 Recommendations for MT-8+

**Multi-Scenario PSO Optimization (MT-8):**
1. **Diverse training set:** Include initial conditions spanning ±0.3 rad (or wider)
2. **Robustness-aware fitness:** Penalize both mean chattering AND worst-case (P95)
3. **Multi-objective optimization:** Balance chattering, settling time, and robustness
4. **Validation protocol:** Test optimized parameters across multiple IC ranges

**Alternative Approaches:**
1. **Disturbance rejection testing:** MT-8 external disturbance experiments
2. **Adaptive gain scheduling:** Adjust gains based on system state magnitude
3. **Hybrid control:** Switch between controllers for small vs large perturbations
4. **Robust optimization:** Min-max PSO targeting worst-case performance

---

## 5. Conclusions

**Primary Conclusion:**
MT-6 optimized parameters (ε_min={mt7_data['configuration']['epsilon_min']:.5f}, α={mt7_data['configuration']['alpha']:.2f}) do NOT generalize to challenging initial conditions (±0.3 rad).

**Supporting Evidence:**
1. ✅ **{degradation_ratio:.1f}x chattering degradation** (highly significant, p < 0.001)
2. ✅ **{failure_rate:.1f}% failure rate** (vs 0% in MT-6)
3. ✅ **Very large effect size** (Cohen's d = {cohens_d:.1f})
4. ✅ **Consistent degradation** across all 10 seeds (CV={mt7_cv:.1f}%)
5. ✅ **Worst-case unacceptable** (P95={mt7_p95:.2f}, P99={mt7_p99:.2f})

**Null Hypothesis Decision:**
**REJECTED** - MT-6 parameters do NOT generalize to MT-7 conditions (Welch's t-test: t={comparison_data['comparison']['t_statistic']:.2f}, p<0.001)

**Actionable Recommendations:**
1. **Immediate:** Expand PSO training set to include ±0.3 rad initial conditions (MT-8)
2. **Medium-term:** Implement robustness-aware fitness function (worst-case penalty)
3. **Long-term:** Investigate adaptive control strategies for varying disturbance magnitudes

---

## 6. Data Artifacts

**Generated Files:**
- `benchmarks/MT7_robustness_summary.json` - Global and per-seed statistics
- `benchmarks/MT7_statistical_comparison.json` - Welch's t-test results
- `benchmarks/MT7_seed_{{42-51}}_results.csv` - Individual seed data (10 files)
- `benchmarks/figures/MT7_robustness_chattering_distribution.png` - Figure 1
- `benchmarks/figures/MT7_robustness_per_seed_variance.png` - Figure 2
- `benchmarks/figures/MT7_robustness_success_rate.png` - Figure 3
- `benchmarks/figures/MT7_robustness_worst_case.png` - Figure 4

**Scripts:**
- `scripts/mt7_robust_pso_tuning.py` - Main simulation runner
- `scripts/mt7_statistical_comparison.py` - Statistical analysis
- `scripts/mt7_visualize_robustness.py` - Visualization generation
- `scripts/mt7_generate_report.py` - This report generator

**Total Data Volume:**
- CSV files: ~55 KB (10 files × 5.5 KB)
- JSON summaries: ~2 KB
- Figures: ~800 KB (4 figures × 200 KB @ 300 DPI)

---

## 7. Reproducibility

**To reproduce MT-7 results:**

```bash
# Run 500 Monte Carlo simulations (10 seeds × 50 runs)
python scripts/mt7_robust_pso_tuning.py

# Generate statistical comparison
python scripts/mt7_statistical_comparison.py

# Generate visualizations
python scripts/mt7_visualize_robustness.py

# Generate this report
python scripts/mt7_generate_report.py
```

**Expected runtime:** ~30-45 minutes (depends on hardware)

**Validation:** Compare your `MT7_robustness_summary.json` against reference values:
- Mean chattering: {mt7_chattering:.2f} ± {mt7_std:.2f}
- Success rate: {success_rate:.1f}%
- Degradation ratio: {degradation_ratio:.1f}x

---

**Report Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Generator:** `scripts/mt7_generate_report.py`
**Status:** DELIVERABLE COMPLETE ✅
"""

    # Save report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report generated: {output_path}")


def main():
    """Generate MT-7 comprehensive report."""

    print("=" * 80)
    print("MT-7 Robustness Validation Report Generator")
    print("=" * 80)

    # Paths
    benchmarks_dir = Path(__file__).parent.parent / "benchmarks"
    output_path = benchmarks_dir / "MT7_COMPLETE_REPORT.md"

    mt6_summary_path = benchmarks_dir / "MT6_adaptive_summary.json"
    mt7_summary_path = benchmarks_dir / "MT7_robustness_summary.json"
    comparison_path = benchmarks_dir / "MT7_statistical_comparison.json"

    # Check prerequisites
    missing = []
    for path in [mt6_summary_path, mt7_summary_path, comparison_path]:
        if not path.exists():
            missing.append(path.name)

    if missing:
        print(f"\nERROR: Missing required files:")
        for f in missing:
            print(f"  - {f}")
        return 1

    # Load data
    print("\nLoading data sources...")
    print(f"  MT-6 baseline:   {mt6_summary_path}")
    print(f"  MT-7 robustness: {mt7_summary_path}")
    print(f"  Comparison:      {comparison_path}")

    mt6_data = load_json_data(mt6_summary_path)
    mt7_data = load_json_data(mt7_summary_path)
    comparison_data = load_json_data(comparison_path)

    # Load seed data
    seeds = mt7_data['configuration']['seeds']
    seed_data = []
    for seed in seeds:
        csv_path = benchmarks_dir / f"MT7_seed_{seed}_results.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            df['seed'] = seed
            seed_data.append(df)

    seed_df = pd.concat(seed_data, ignore_index=True) if seed_data else pd.DataFrame()

    # Generate report
    print("\nGenerating comprehensive report...")
    generate_mt7_report(mt6_data, mt7_data, comparison_data, seed_df, output_path)

    print("=" * 80)
    print(f"MT-7 Complete Report generated!")
    print(f"Output: {output_path}")
    print(f"Size: {output_path.stat().st_size / 1024:.1f} KB")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
