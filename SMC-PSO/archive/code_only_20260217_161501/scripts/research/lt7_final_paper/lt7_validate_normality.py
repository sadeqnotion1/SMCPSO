#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LT-7 RESEARCH PAPER - TASK B.1: NORMALITY VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose:
  Validate that chattering distributions are approximately normal
  (assumption for parametric tests like Welch's t-test)

Methods:
  1. Shapiro-Wilk test (H0: data is normal, reject if p < 0.05)
  2. Q-Q plots (visual normality check)

Data Sources:
  - benchmarks/MT6_fixed_baseline.csv (Fixed boundary, n=30)
  - benchmarks/MT6_adaptive_validation.csv (Adaptive boundary, n=30)

Output:
  - Statistical report (console + markdown)
  - Figure VI-1-normality.pdf (2-panel Q-Q plot)

Author: Claude Code
Date: 2025-10-20 (Phase 2, Category B)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

# Data paths
FIXED_CSV = Path("benchmarks/MT6_fixed_baseline.csv")
ADAPTIVE_CSV = Path("benchmarks/MT6_adaptive_validation.csv")

# Output paths
OUTPUT_DIR = Path(".artifacts/LT7_research_paper/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_PATH = OUTPUT_DIR / "figure_vi_1_normality_validation.pdf"
REPORT_PATH = OUTPUT_DIR.parent / "reports" / "B1_normality_validation_report.md"
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Statistical parameters
ALPHA = 0.05  # Significance level for Shapiro-Wilk

# ═══════════════════════════════════════════════════════════════════════════════
# Load Data
# ═══════════════════════════════════════════════════════════════════════════════

print("[LOAD] Loading MT-6 chattering data...")
df_fixed = pd.read_csv(FIXED_CSV)
df_adaptive = pd.read_csv(ADAPTIVE_CSV)

chattering_fixed = df_fixed['chattering_index'].values
chattering_adaptive = df_adaptive['chattering_index'].values

print(f"  Fixed boundary: n={len(chattering_fixed)}, mean={chattering_fixed.mean():.2f}")
print(f"  Adaptive boundary: n={len(chattering_adaptive)}, mean={chattering_adaptive.mean():.2f}")

# ═══════════════════════════════════════════════════════════════════════════════
# Shapiro-Wilk Test
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[TEST] Running Shapiro-Wilk normality test...")
stat_fixed, p_fixed = stats.shapiro(chattering_fixed)
stat_adaptive, p_adaptive = stats.shapiro(chattering_adaptive)

print(f"  Fixed boundary: W={stat_fixed:.4f}, p={p_fixed:.4f}")
print(f"    -> {'NORMAL' if p_fixed > ALPHA else 'NOT NORMAL'} (alpha={ALPHA})")

print(f"  Adaptive boundary: W={stat_adaptive:.4f}, p={p_adaptive:.4f}")
print(f"    -> {'NORMAL' if p_adaptive > ALPHA else 'NOT NORMAL'} (alpha={ALPHA})")

# ═══════════════════════════════════════════════════════════════════════════════
# Q-Q Plots (Visual Normality Check)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[PLOT] Generating Q-Q plots...")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Fixed boundary Q-Q plot
(osm_fixed, osr_fixed), (slope_fixed, intercept_fixed, r_fixed) = stats.probplot(
    chattering_fixed, dist="norm", plot=None
)
axes[0].scatter(osm_fixed, osr_fixed, alpha=0.6, edgecolors='k', s=50, label='Data')
axes[0].plot(osm_fixed, slope_fixed * osm_fixed + intercept_fixed, 'r--', linewidth=2, label='Fit')
axes[0].set_xlabel('Theoretical Quantiles', fontsize=12)
axes[0].set_ylabel('Sample Quantiles', fontsize=12)
axes[0].set_title(f'Fixed Boundary (W={stat_fixed:.3f}, p={p_fixed:.3f})', fontsize=13, fontweight='bold')
axes[0].legend(fontsize=10)
axes[0].grid(True, alpha=0.3)

# Adaptive boundary Q-Q plot
(osm_adaptive, osr_adaptive), (slope_adaptive, intercept_adaptive, r_adaptive) = stats.probplot(
    chattering_adaptive, dist="norm", plot=None
)
axes[1].scatter(osm_adaptive, osr_adaptive, alpha=0.6, edgecolors='k', s=50, label='Data', color='tab:orange')
axes[1].plot(osm_adaptive, slope_adaptive * osm_adaptive + intercept_adaptive, 'r--', linewidth=2, label='Fit')
axes[1].set_xlabel('Theoretical Quantiles', fontsize=12)
axes[1].set_ylabel('Sample Quantiles', fontsize=12)
axes[1].set_title(f'Adaptive Boundary (W={stat_adaptive:.3f}, p={p_adaptive:.3f})', fontsize=13, fontweight='bold')
axes[1].legend(fontsize=10)
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

report = f"""# Task B.1: Normality Validation Report

**Date:** 2025-10-20
**Phase:** LT-7 Phase 2, Category B
**Objective:** Validate normality assumption for parametric statistical tests

---

## 1. Data Summary

| Metric | Fixed Boundary | Adaptive Boundary |
|--------|----------------|-------------------|
| Sample Size (n) | {len(chattering_fixed)} | {len(chattering_adaptive)} |
| Mean | {chattering_fixed.mean():.4f} | {chattering_adaptive.mean():.4f} |
| Std Dev | {chattering_fixed.std(ddof=1):.4f} | {chattering_adaptive.std(ddof=1):.4f} |
| Min | {chattering_fixed.min():.4f} | {chattering_adaptive.min():.4f} |
| Max | {chattering_fixed.max():.4f} | {chattering_adaptive.max():.4f} |

**Data Sources:**
- Fixed: `benchmarks/MT6_fixed_baseline.csv`
- Adaptive: `benchmarks/MT6_adaptive_validation.csv`

---

## 2. Shapiro-Wilk Test Results

**Test Hypothesis:**
- H₀: Data is normally distributed
- H₁: Data is NOT normally distributed
- Significance level (α): {ALPHA}

**Results:**

| Distribution | W-statistic | p-value | Conclusion (α={ALPHA}) |
|--------------|-------------|---------|------------------------|
| **Fixed Boundary** | {stat_fixed:.4f} | {p_fixed:.4f} | {'✓ NORMAL' if p_fixed > ALPHA else '✗ NOT NORMAL'} |
| **Adaptive Boundary** | {stat_adaptive:.4f} | {p_adaptive:.4f} | {'✓ NORMAL' if p_adaptive > ALPHA else '✗ NOT NORMAL'} |

**Interpretation:**
- **Fixed Boundary:** {'p > α, fail to reject H₀ → data is approximately normal' if p_fixed > ALPHA else 'p ≤ α, reject H₀ → data deviates significantly from normality'}
- **Adaptive Boundary:** {'p > α, fail to reject H₀ → data is approximately normal' if p_adaptive > ALPHA else 'p ≤ α, reject H₀ → data deviates significantly from normality'}

---

## 3. Q-Q Plot Analysis

**Visual Inspection:**
- Q-Q plots show theoretical quantiles (normal distribution) vs. sample quantiles
- Points near the red dashed line indicate good fit to normal distribution
- Deviations in tails may indicate skewness or heavy tails

**Figure:** `{FIGURE_PATH.name}`

---

## 4. Validity of Parametric Tests

**Welch's t-test Assumption Check:**

The Welch's t-test used in Chapter 6 (Figure VI-1) assumes approximate normality of data.

**Validation Status:**
"""

# Add validation status based on test results
if p_fixed > ALPHA and p_adaptive > ALPHA:
    report += """
✓ **VALID:** Both distributions pass Shapiro-Wilk test (p > 0.05)
✓ Parametric tests (Welch's t-test) are appropriate for this data
✓ Reported confidence intervals and p-values are reliable
"""
elif p_fixed > ALPHA or p_adaptive > ALPHA:
    report += f"""
⚠ **PARTIAL:** One distribution passes, one fails normality test
- Fixed: {'PASS' if p_fixed > ALPHA else 'FAIL'} (p={p_fixed:.4f})
- Adaptive: {'PASS' if p_adaptive > ALPHA else 'FAIL'} (p={p_adaptive:.4f})

**Recommendation:** Use robust non-parametric tests (Mann-Whitney U) or bootstrap methods for validation
"""
else:
    report += f"""
✗ **INVALID:** Both distributions fail Shapiro-Wilk test (p ≤ 0.05)
- Fixed: p={p_fixed:.4f}
- Adaptive: p={p_adaptive:.4f}

**Recommendation:** Use non-parametric tests (Mann-Whitney U, Kruskal-Wallis) instead of t-tests
"""

report += f"""
---

## 5. Recommendations

"""

if p_fixed > ALPHA and p_adaptive > ALPHA:
    report += """
1. ✓ Continue using Welch's t-test for statistical comparisons
2. ✓ Confidence intervals computed via t-distribution are valid
3. ✓ No need to switch to non-parametric methods
"""
else:
    report += """
1. ⚠ Consider supplementing with Mann-Whitney U test (non-parametric alternative)
2. ⚠ Use bootstrap confidence intervals for robustness
3. ⚠ Report both parametric and non-parametric results for transparency
"""

report += f"""

---

**Generated:** 2025-10-20
**Script:** `scripts/lt7_validate_normality.py`
**Figure:** `{FIGURE_PATH}`
"""

# Save report
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"  [OK] Saved: {REPORT_PATH}")

# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("NORMALITY VALIDATION COMPLETE")
print("="*80)
print(f"Fixed boundary: W={stat_fixed:.4f}, p={p_fixed:.4f} -> {'NORMAL' if p_fixed > ALPHA else 'NOT NORMAL'}")
print(f"Adaptive boundary: W={stat_adaptive:.4f}, p={p_adaptive:.4f} -> {'NORMAL' if p_adaptive > ALPHA else 'NOT NORMAL'}")
print(f"\nFigure: {FIGURE_PATH}")
print(f"Report: {REPORT_PATH}")
print("="*80)
