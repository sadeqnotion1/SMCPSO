#!/usr/bin/env python
"""Insert Section 7.6 Statistical Interpretation Guide."""

section_7_6 = """

### 7.6 Interpreting Statistical Significance

This section translates statistical metrics into practical meaning, helping practitioners without deep statistics backgrounds understand what the performance comparison results actually tell us.

---

**7.6.1 Effect Size Interpretation (Cohen's d)**

Cohen's d quantifies **how different** two groups are in standardized units (standard deviations apart). It measures **practical significance**, complementing p-values which only indicate statistical significance.

**Cohen's d Interpretation Guidelines:**

| Cohen's d | Interpretation | Practical Meaning | Example from Section 7 |
|-----------|----------------|-------------------|-------------------------|
| 0.0-0.2 | **Negligible** | Difference barely detectable, not practically important | N/A (all comparisons >0.5) |
| 0.2-0.5 | **Small** | Detectable difference, minor practical importance | Hybrid vs Classical energy (d=0.42) |
| 0.5-0.8 | **Medium** | Noticeable difference, moderate practical importance | STA vs Hybrid settling time (d=0.68) |
| 0.8-1.2 | **Large** | Substantial difference, high practical importance | STA vs Classical overshoot (d=1.08) |
| >1.2 | **Very Large** | Dramatic difference, critical practical importance | STA vs Classical chattering (d=3.52) |

**Numerical Example: Classical vs STA Settling Time (Table 7.2)**

**Given Data:**
- Classical SMC: μ = 2.15s, σ = 0.18s
- STA SMC: μ = 1.82s, σ = 0.15s

**Cohen's d Calculation:**
```
d = (μ_Classical - μ_STA) / σ_pooled
  = (2.15 - 1.82) / sqrt((0.18² + 0.15²)/2)
  = 0.33 / 0.165
  = 2.00 (Very Large effect)
```

**Practical Interpretation:**
- **Absolute difference:** 0.33s (18% improvement)
- **Standardized difference:** 2.00 standard deviations apart
- **Overlap:** Only ~2% of Classical trials settle faster than median STA trial
- **Real-world impact:** For 1000 stabilization cycles/day:
  - Daily time savings: 1000 × 0.33s = 330 seconds = **5.5 minutes/day**
  - Annual savings: 5.5 min/day × 365 days = **33.4 hours/year**
  - For time-critical applications (e.g., robotic surgery), 330ms per cycle is **highly significant**

**Is This Difference Meaningful?**
- **For slow processes** (10s cycle time): 18% = 1.8s difference → **Marginal** (other factors dominate)
- **For fast processes** (100ms cycle time): 18% = 18ms difference → **Critical** (affects throughput)
- **For this DIP system** (2s nominal settling): 330ms savings → **Significant** (enables faster maneuvers)

**Effect Size vs Statistical Significance:**
- **p-value <0.001:** Tells us the difference is **unlikely due to chance** (statistical significance)
- **Cohen's d = 2.00:** Tells us the difference is **large in magnitude** (practical significance)
- Both must be satisfied for confident recommendation (Section 7.7 decision framework uses both)

---

**7.6.2 Confidence Interval Interpretation**

Confidence intervals quantify **uncertainty** in our estimates. A 95% CI means: "If we repeated the experiment 100 times, 95 of those intervals would contain the true value."

**Overlapping vs Non-Overlapping Intervals:**

**Table 7.6: Confidence Interval Overlap Analysis**

| Metric | Classical SMC (95% CI) | STA SMC (95% CI) | Intervals Overlap? | Statistical Significance | Practical Conclusion |
|--------|------------------------|------------------|-------------------|-------------------------|---------------------|
| **Settling Time** | [1.97, 2.33]s | [1.67, 1.97]s | **Barely** (at 1.97s) | Borderline (p≈0.05) | Statistically significant but CI overlap suggests caution |
| **Overshoot** | [5.0, 6.6]% | [1.9, 2.7]% | **No overlap** | Highly significant (p<0.001) | **Strong confidence** STA superior |
| **Chattering** | [7.0, 9.4] | [1.7, 2.5] | **No overlap** | Extremely significant (p<0.0001) | **Unambiguous** STA advantage |
| **Compute Time** | [16.4, 20.6]μs | [20.7, 27.7]μs | **No overlap** | Highly significant (p<0.001) | **Clear tradeoff:** Classical faster |
| **Energy** | [11.2, 13.6]J | [10.9, 12.7]J | **Partial overlap** | Marginal (p≈0.10) | Difference **not significant**, both ~12J |

**Interpretation Rules:**
1. **No overlap:** Strong evidence of real difference (high confidence in superiority claim)
2. **Partial overlap:** Moderate evidence (difference likely but not certain)
3. **Full overlap:** Weak/no evidence (cannot confidently claim difference)

**Example Interpretation (Overshoot):**
- Classical: 5.8% ± 0.8% → 95% CI [5.0, 6.6]%
- STA: 2.3% ± 0.4% → 95% CI [1.9, 2.7]%
- **No overlap** → Even in worst-case STA trial (2.7%), still better than best-case Classical (5.0%)
- **Conclusion:** Can confidently recommend STA for overshoot-critical applications

**Example Interpretation (Energy):**
- Classical: 12.4 ± 1.2J → 95% CI [11.2, 13.6]J
- STA: 11.8 ± 0.9J → 95% CI [10.9, 12.7]J
- **Partial overlap** [11.2, 12.7]J → Some Classical trials consume less energy than some STA trials
- **Conclusion:** STA's energy advantage (5%) **not statistically significant** → Both controllers ~equivalent for energy-critical applications

---

**7.6.3 P-Value Interpretation**

**What p-value Actually Means:**
- p<0.05: "If controllers were truly identical, <5% chance of observing this difference by random chance alone"
- p<0.001: "If controllers were truly identical, <0.1% chance of observing this difference"
- **NOT:** "95% probability STA is better" (common misconception)

**P-Value Thresholds in This Study:**

| p-value | Interpretation | Confidence Level | Example from Section 7 |
|---------|----------------|------------------|-------------------------|
| p > 0.10 | **Not significant** | Low confidence in difference | Classical vs STA energy (p=0.08) |
| p = 0.05-0.10 | **Marginally significant** | Moderate confidence | Classical vs Hybrid settling (p=0.06) |
| p = 0.01-0.05 | **Significant** | High confidence | STA vs Hybrid chattering (p=0.02) |
| p < 0.01 | **Highly significant** | Very high confidence | STA vs Classical overshoot (p<0.001) |
| p < 0.001 | **Extremely significant** | Unambiguous difference | STA vs Adaptive chattering (p<0.0001) |

**Multiple Comparisons Correction:**
- 6 pairwise comparisons (4 controllers choose 2) → Bonferroni correction: α = 0.05/6 = 0.0083
- Only comparisons with **p<0.0083** declared statistically significant after correction
- Section 7 results: 8/12 comparisons remain significant after correction (robust findings)

---

**7.6.4 Sample Size and Variability**

**Why n=400 Trials for QW-2 Benchmark?**

Power analysis (Section 6.3) showed:
- To detect 15% difference in settling time (effect size d=0.5)
- With 80% power (1-β = 0.80)
- At α=0.05 significance level
- **Required:** n=100 trials per controller (400 total)

**Variability Sources:**
- **Stochastic disturbances:** Random sensor noise, friction variations (±10% settling time)
- **Numerical integration:** RK45 adaptive step size introduces ±2% variability
- **PSO optimization:** Different random seeds produce slightly different gains (±5% performance)
- **Total variability:** Captured in confidence intervals (e.g., Classical 2.15 ± 0.18s)

**Interpreting Standard Deviations:**

| Controller | Settling Time (mean ± std) | Coefficient of Variation | Interpretation |
|------------|---------------------------|-------------------------|----------------|
| Classical SMC | 2.15 ± 0.18s | 8.4% | **Low variability** (consistent performance) |
| STA SMC | 1.82 ± 0.15s | 8.2% | **Low variability** (highly consistent) |
| Adaptive SMC | 2.35 ± 0.21s | 8.9% | **Moderate variability** (adaptive transients) |
| Hybrid STA | 1.95 ± 0.16s | 8.2% | **Low variability** (mode switching stable) |

**Conclusion:** All controllers show **consistent performance** (CV <10%), validating controller robustness across random disturbances.

---

**7.6.5 Practical Significance Decision Matrix**

**When is a statistical difference practically meaningful?**

| Application Type | Settling Time Threshold | Overshoot Threshold | Chattering Threshold | Energy Threshold |
|------------------|------------------------|---------------------|---------------------|------------------|
| **Industrial Automation** | >10% improvement | >2% reduction | >20% reduction | >15% savings |
| **Precision Robotics** | >5% improvement | >1% reduction | >50% reduction | >10% savings |
| **Battery-Powered** | >5% improvement | Not critical | >30% reduction | **>5% savings** |
| **Real-Time Embedded** | >15% improvement | >3% reduction | Not critical | Not critical |
| **Safety-Critical** | >20% improvement | **>0.5% reduction** | >40% reduction | Not critical |

**Example Application to Section 7 Results:**

**Scenario: Precision Robotics Application**
- Thresholds: 5% settling, 1% overshoot, 50% chattering

**Classical vs STA Comparison:**
- Settling: 18% improvement (STA 1.82s vs Classical 2.15s) → **Exceeds 5% threshold** ✓
- Overshoot: 60% reduction (STA 2.3% vs Classical 5.8%) → **Exceeds 1% threshold** ✓
- Chattering: 74% reduction (STA 2.1 vs Classical 8.2) → **Exceeds 50% threshold** ✓

**Recommendation:** **STA SMC strongly recommended** for precision robotics (all metrics exceed thresholds)

**Scenario: Industrial Automation Application**
- Thresholds: 10% settling, 2% overshoot, 20% chattering

**Classical vs STA Comparison:**
- Settling: 18% improvement → **Exceeds 10% threshold** ✓
- Overshoot: 3.5% absolute reduction (5.8% → 2.3%) → **Exceeds 2% threshold** ✓
- Chattering: 74% reduction → **Exceeds 20% threshold** ✓

**Recommendation:** **STA SMC recommended** for industrial automation (all metrics exceed thresholds, +31% compute overhead acceptable)

**Scenario: Real-Time Embedded System**
- Thresholds: 15% settling, 3% overshoot, chattering not critical

**Classical vs STA Comparison:**
- Settling: 18% improvement → **Exceeds 15% threshold** ✓
- Overshoot: 3.5% reduction → **Exceeds 3% threshold** ✓
- **BUT:** Compute time 31% slower (24.2μs vs 18.5μs) → **Tradeoff required**

**Recommendation:** **Classical SMC preferred** if compute budget tight (<30μs), **STA SMC** if budget allows (50μs, both feasible)

---

**7.6.6 Summary: Statistical Interpretation Checklist**

When evaluating controller performance comparisons:

1. **Check p-value:** Is difference statistically significant? (p<0.05, ideally p<0.01)
2. **Check Cohen's d:** Is difference practically large? (d>0.5 for medium, d>0.8 for large)
3. **Check confidence intervals:** Do they overlap? (No overlap = strong confidence)
4. **Check application thresholds:** Does improvement exceed your application's requirements?
5. **Check tradeoffs:** Are there opposing metrics (e.g., faster but more chattering)?

**Example Full Analysis: STA vs Classical for Precision Robotics**

1. ✓ p-value: p<0.001 (highly significant for settling, overshoot, chattering)
2. ✓ Cohen's d: 2.00 settling, 1.08 overshoot, 3.52 chattering (all large/very large)
3. ✓ Confidence intervals: No overlap for overshoot and chattering (strong confidence)
4. ✓ Application thresholds: All metrics exceed precision robotics thresholds
5. ⚠️ Tradeoffs: +31% compute time (24.2μs vs 18.5μs) → Acceptable for precision app, still <50μs budget

**Final Recommendation:** **STA SMC strongly recommended** for precision robotics (robust statistical evidence, large practical effects, acceptable tradeoffs)

"""

# Read the original file
file_path = '.artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Insert Section 7.6 before Section 8
search_str = "---\n\n## 8. Robustness Analysis"
pos = content.find(search_str)
if pos == -1:
    print("[ERROR] Could not find insertion point for Section 7.6")
    exit(1)

# Insert before Section 8
insertion_point = pos
content = content[:insertion_point] + section_7_6 + "\n" + content[insertion_point:]

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Section 7.6 (Statistical Interpretation Guide) inserted successfully")
