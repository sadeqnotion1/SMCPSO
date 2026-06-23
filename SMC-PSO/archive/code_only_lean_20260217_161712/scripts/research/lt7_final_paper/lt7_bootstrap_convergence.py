#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LT-7 RESEARCH PAPER - TASK B.2: BOOTSTRAP CONVERGENCE ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose:
  Validate that 10,000 bootstrap iterations used in MT-6 analysis were sufficient
  by testing convergence of confidence interval widths.

Methods:
  1. Run bootstrap with B = 1,000, 5,000, 10,000, 20,000 iterations
  2. Compute 95% CI for mean chattering (Fixed + Adaptive)
  3. Track CI width vs. B
  4. Check if CI width stabilizes at B=10,000 (change < 5% from 10K to 20K)

Data Sources:
  - benchmarks/MT6_fixed_baseline.csv
  - benchmarks/MT6_adaptive_validation.csv

Output:
  - Convergence plot (CI width vs. B)
  - Statistical report (markdown)

Author: Claude Code
Date: 2025-10-20 (Phase 2, Category B)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from pathlib import Path
import time

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

# Data paths
FIXED_CSV = Path("benchmarks/MT6_fixed_baseline.csv")
ADAPTIVE_CSV = Path("benchmarks/MT6_adaptive_validation.csv")

# Output paths
OUTPUT_DIR = Path(".artifacts/LT7_research_paper/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_PATH = OUTPUT_DIR / "figure_vi_1_bootstrap_convergence.pdf"
REPORT_PATH = OUTPUT_DIR.parent / "reports" / "B2_bootstrap_convergence_report.md"
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Bootstrap parameters
BOOTSTRAP_ITERATIONS = [1000, 5000, 10000, 20000]
CONFIDENCE_LEVEL = 0.95
RANDOM_SEED = 42
CONVERGENCE_THRESHOLD = 0.05  # 5% change threshold

# ═══════════════════════════════════════════════════════════════════════════════
# Load Data
# ═══════════════════════════════════════════════════════════════════════════════

print("[LOAD] Loading MT-6 chattering data...")
df_fixed = pd.read_csv(FIXED_CSV)
df_adaptive = pd.read_csv(ADAPTIVE_CSV)

chattering_fixed = df_fixed['chattering_index'].values
chattering_adaptive = df_adaptive['chattering_index'].values

print(f"  Fixed boundary: n={len(chattering_fixed)}, mean={chattering_fixed.mean():.4f}")
print(f"  Adaptive boundary: n={len(chattering_adaptive)}, mean={chattering_adaptive.mean():.4f}")

# ═══════════════════════════════════════════════════════════════════════════════
# Bootstrap Function
# ═══════════════════════════════════════════════════════════════════════════════

def bootstrap_ci(data, n_bootstrap, confidence=0.95, seed=42):
    """
    Compute bootstrap confidence interval for the mean.

    Parameters:
    -----------
    data : array-like
        Sample data
    n_bootstrap : int
        Number of bootstrap iterations
    confidence : float
        Confidence level (default: 0.95)
    seed : int
        Random seed for reproducibility

    Returns:
    --------
    ci_lower : float
        Lower bound of CI
    ci_upper : float
        Upper bound of CI
    ci_width : float
        Width of CI (upper - lower)
    elapsed : float
        Computation time (seconds)
    """
    np.random.seed(seed)
    n = len(data)

    start_time = time.time()

    # Generate bootstrap samples
    bootstrap_means = np.zeros(n_bootstrap)
    for i in range(n_bootstrap):
        sample = np.random.choice(data, size=n, replace=True)
        bootstrap_means[i] = np.mean(sample)

    # Compute percentile CI
    alpha = 1 - confidence
    ci_lower = np.percentile(bootstrap_means, 100 * alpha / 2)
    ci_upper = np.percentile(bootstrap_means, 100 * (1 - alpha / 2))
    ci_width = ci_upper - ci_lower

    elapsed = time.time() - start_time

    return ci_lower, ci_upper, ci_width, elapsed

# ═══════════════════════════════════════════════════════════════════════════════
# Run Bootstrap Convergence Analysis
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n[BOOTSTRAP] Running convergence analysis (B={BOOTSTRAP_ITERATIONS})...")
print("This may take a few minutes...\n")

results_fixed = []
results_adaptive = []

for B in BOOTSTRAP_ITERATIONS:
    print(f"  B={B:,}...")

    # Fixed boundary
    ci_lower_f, ci_upper_f, ci_width_f, elapsed_f = bootstrap_ci(
        chattering_fixed, B, CONFIDENCE_LEVEL, RANDOM_SEED
    )
    results_fixed.append({
        'B': B,
        'ci_lower': ci_lower_f,
        'ci_upper': ci_upper_f,
        'ci_width': ci_width_f,
        'elapsed': elapsed_f
    })
    print(f"    Fixed: CI=[{ci_lower_f:.4f}, {ci_upper_f:.4f}], width={ci_width_f:.4f}, time={elapsed_f:.2f}s")

    # Adaptive boundary
    ci_lower_a, ci_upper_a, ci_width_a, elapsed_a = bootstrap_ci(
        chattering_adaptive, B, CONFIDENCE_LEVEL, RANDOM_SEED
    )
    results_adaptive.append({
        'B': B,
        'ci_lower': ci_lower_a,
        'ci_upper': ci_upper_a,
        'ci_width': ci_width_a,
        'elapsed': elapsed_a
    })
    print(f"    Adaptive: CI=[{ci_lower_a:.4f}, {ci_upper_a:.4f}], width={ci_width_a:.4f}, time={elapsed_a:.2f}s")

# Convert to DataFrames
df_results_fixed = pd.DataFrame(results_fixed)
df_results_adaptive = pd.DataFrame(results_adaptive)

# ═══════════════════════════════════════════════════════════════════════════════
# Check Convergence (10K to 20K)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[CONVERGENCE] Checking CI width stability (10K to 20K)...")

width_10k_fixed = df_results_fixed[df_results_fixed['B'] == 10000]['ci_width'].values[0]
width_20k_fixed = df_results_fixed[df_results_fixed['B'] == 20000]['ci_width'].values[0]
change_fixed = abs(width_20k_fixed - width_10k_fixed) / width_10k_fixed

width_10k_adaptive = df_results_adaptive[df_results_adaptive['B'] == 10000]['ci_width'].values[0]
width_20k_adaptive = df_results_adaptive[df_results_adaptive['B'] == 20000]['ci_width'].values[0]
change_adaptive = abs(width_20k_adaptive - width_10k_adaptive) / width_10k_adaptive

print(f"  Fixed: {width_10k_fixed:.4f} (10K) -> {width_20k_fixed:.4f} (20K), change={change_fixed*100:.2f}%")
print(f"  Adaptive: {width_10k_adaptive:.4f} (10K) -> {width_20k_adaptive:.4f} (20K), change={change_adaptive*100:.2f}%")

converged_fixed = change_fixed < CONVERGENCE_THRESHOLD
converged_adaptive = change_adaptive < CONVERGENCE_THRESHOLD

print(f"\n  Fixed: {'CONVERGED' if converged_fixed else 'NOT CONVERGED'} (threshold={CONVERGENCE_THRESHOLD*100:.0f}%)")
print(f"  Adaptive: {'CONVERGED' if converged_adaptive else 'NOT CONVERGED'} (threshold={CONVERGENCE_THRESHOLD*100:.0f}%)")

# ═══════════════════════════════════════════════════════════════════════════════
# Plot Convergence
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[PLOT] Generating convergence plot...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Fixed boundary convergence
axes[0].plot(df_results_fixed['B'], df_results_fixed['ci_width'], 'o-', linewidth=2, markersize=8, label='CI Width')
axes[0].axhline(y=width_10k_fixed, color='r', linestyle='--', linewidth=1.5, label=f'B=10K baseline ({width_10k_fixed:.4f})')
axes[0].axhline(y=width_10k_fixed * (1 + CONVERGENCE_THRESHOLD), color='gray', linestyle=':', linewidth=1, label=f'+{CONVERGENCE_THRESHOLD*100:.0f}% threshold')
axes[0].axhline(y=width_10k_fixed * (1 - CONVERGENCE_THRESHOLD), color='gray', linestyle=':', linewidth=1, label=f'-{CONVERGENCE_THRESHOLD*100:.0f}% threshold')
axes[0].set_xlabel('Bootstrap Iterations (B)', fontsize=12)
axes[0].set_ylabel('95% CI Width', fontsize=12)
axes[0].set_title(f'Fixed Boundary (Converged: {converged_fixed})', fontsize=13, fontweight='bold')
axes[0].set_xscale('log')
axes[0].legend(fontsize=9)
axes[0].grid(True, alpha=0.3)

# Adaptive boundary convergence
axes[1].plot(df_results_adaptive['B'], df_results_adaptive['ci_width'], 'o-', linewidth=2, markersize=8, color='tab:orange', label='CI Width')
axes[1].axhline(y=width_10k_adaptive, color='r', linestyle='--', linewidth=1.5, label=f'B=10K baseline ({width_10k_adaptive:.4f})')
axes[1].axhline(y=width_10k_adaptive * (1 + CONVERGENCE_THRESHOLD), color='gray', linestyle=':', linewidth=1, label=f'+{CONVERGENCE_THRESHOLD*100:.0f}% threshold')
axes[1].axhline(y=width_10k_adaptive * (1 - CONVERGENCE_THRESHOLD), color='gray', linestyle=':', linewidth=1, label=f'-{CONVERGENCE_THRESHOLD*100:.0f}% threshold')
axes[1].set_xlabel('Bootstrap Iterations (B)', fontsize=12)
axes[1].set_ylabel('95% CI Width', fontsize=12)
axes[1].set_title(f'Adaptive Boundary (Converged: {converged_adaptive})', fontsize=13, fontweight='bold')
axes[1].set_xscale('log')
axes[1].legend(fontsize=9)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(FIGURE_PATH, dpi=300, bbox_inches='tight')
plt.savefig(FIGURE_PATH.with_suffix('.png'), dpi=150, bbox_inches='tight')
print(f"  [OK] Saved: {FIGURE_PATH}")
print(f"  [OK] Saved: {FIGURE_PATH.with_suffix('.png')}")

# ═══════════════════════════════════════════════════════════════════════════════
# Generate Report
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[REPORT] Generating markdown report...")

report = f"""# Task B.2: Bootstrap Convergence Analysis Report

**Date:** 2025-10-20
**Phase:** LT-7 Phase 2, Category B
**Objective:** Validate that B=10,000 iterations used in MT-6 analysis were sufficient

---

## 1. Data Summary

| Metric | Fixed Boundary | Adaptive Boundary |
|--------|----------------|-------------------|
| Sample Size (n) | {len(chattering_fixed)} | {len(chattering_adaptive)} |
| Mean | {chattering_fixed.mean():.4f} | {chattering_adaptive.mean():.4f} |
| Std Dev | {chattering_fixed.std(ddof=1):.4f} | {chattering_adaptive.std(ddof=1):.4f} |

---

## 2. Bootstrap Convergence Results

### Fixed Boundary

| B (iterations) | CI Lower | CI Upper | CI Width | Computation Time |
|----------------|----------|----------|----------|------------------|
"""

for _, row in df_results_fixed.iterrows():
    report += f"| {row['B']:,} | {row['ci_lower']:.4f} | {row['ci_upper']:.4f} | {row['ci_width']:.4f} | {row['elapsed']:.2f}s |\n"

report += f"""
### Adaptive Boundary

| B (iterations) | CI Lower | CI Upper | CI Width | Computation Time |
|----------------|----------|----------|----------|------------------|
"""

for _, row in df_results_adaptive.iterrows():
    report += f"| {row['B']:,} | {row['ci_lower']:.4f} | {row['ci_upper']:.4f} | {row['ci_width']:.4f} | {row['elapsed']:.2f}s |\n"

report += f"""
---

## 3. Convergence Analysis (10K to 20K)

**Convergence Criterion:** CI width change < {CONVERGENCE_THRESHOLD*100:.0f}%

### Fixed Boundary
- **B=10,000:** CI width = {width_10k_fixed:.4f}
- **B=20,000:** CI width = {width_20k_fixed:.4f}
- **Change:** {change_fixed*100:.2f}%
- **Status:** {'✓ CONVERGED' if converged_fixed else '✗ NOT CONVERGED'}

### Adaptive Boundary
- **B=10,000:** CI width = {width_10k_adaptive:.4f}
- **B=20,000:** CI width = {width_20k_adaptive:.4f}
- **Change:** {change_adaptive*100:.2f}%
- **Status:** {'✓ CONVERGED' if converged_adaptive else '✗ NOT CONVERGED'}

---

## 4. Conclusion

"""

if converged_fixed and converged_adaptive:
    report += """
✓ **VALIDATION SUCCESSFUL:** Both distributions show convergence at B=10,000

**Implications:**
- The 10,000 bootstrap iterations used in MT-6 analysis were **sufficient**
- Confidence intervals reported in Chapter 6 are **stable and reliable**
- Increasing to B=20,000 produces negligible improvement (<5% change)
- Current bootstrap methodology is **computationally efficient** without sacrificing accuracy

**Recommendation:** Continue using B=10,000 for future bootstrap analyses in this project.
"""
else:
    report += f"""
⚠ **PARTIAL CONVERGENCE:** At least one distribution did not converge at B=10,000

**Details:**
- Fixed: {'CONVERGED' if converged_fixed else f'NOT CONVERGED ({change_fixed*100:.2f}% change)'}
- Adaptive: {'CONVERGED' if converged_adaptive else f'NOT CONVERGED ({change_adaptive*100:.2f}% change)'}

**Recommendation:** Consider increasing to B=20,000 for improved stability, especially for the non-converged distribution.
"""

report += f"""

---

## 5. Computational Efficiency

**Total Bootstrap Time (all tests):**
- Fixed: {df_results_fixed['elapsed'].sum():.2f}s
- Adaptive: {df_results_adaptive['elapsed'].sum():.2f}s
- **Combined:** {(df_results_fixed['elapsed'].sum() + df_results_adaptive['elapsed'].sum()):.2f}s

**Time per iteration (B=10,000):**
- Fixed: {df_results_fixed[df_results_fixed['B'] == 10000]['elapsed'].values[0] / 10000 * 1000:.4f} ms/iter
- Adaptive: {df_results_adaptive[df_results_adaptive['B'] == 10000]['elapsed'].values[0] / 10000 * 1000:.4f} ms/iter

---

**Figure:** `{FIGURE_PATH.name}`
**Generated:** 2025-10-20
**Script:** `scripts/lt7_bootstrap_convergence.py`
"""

# Save report
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"  [OK] Saved: {REPORT_PATH}")

# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("BOOTSTRAP CONVERGENCE ANALYSIS COMPLETE")
print("="*80)
print(f"Fixed: {change_fixed*100:.2f}% change (10K->20K) -> {'CONVERGED' if converged_fixed else 'NOT CONVERGED'}")
print(f"Adaptive: {change_adaptive*100:.2f}% change (10K->20K) -> {'CONVERGED' if converged_adaptive else 'NOT CONVERGED'}")
print(f"\nFigure: {FIGURE_PATH}")
print(f"Report: {REPORT_PATH}")
print("="*80)
