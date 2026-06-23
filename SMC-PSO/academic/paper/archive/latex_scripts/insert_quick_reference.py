#!/usr/bin/env python
"""Insert Quick Reference Table 6.1."""

quick_reference = """

### 6.7 Experimental Setup Quick Reference

This table provides a one-page lookup of all critical setup specifications for rapid reference during replication.

**Table 6.1: Experimental Setup Quick Reference Card**

| Category | Specification | Value | Purpose | Reference |
|----------|--------------|-------|---------|-----------|
| **Software** | Python | 3.9+ | Primary language | Section 6.1 |
| | NumPy | 1.24+ | Numerical arrays | Section 6.1 |
| | SciPy | 1.10+ | ODE integration (RK45) | Section 6.1 |
| | PySwarms | 1.3+ | PSO optimization | Section 5.4 |
| | Matplotlib | 3.5+ | Visualization | Section 6.1 |
| **Hardware** | CPU | i7-10700K (8 cores, 3.8 GHz) | Simulation compute | Section 6.1 |
| | RAM | 16 GB DDR4 | Batch storage | Section 6.1 |
| | Storage | NVMe SSD | Fast I/O for data logging | Section 6.1 |
| **Simulation** | Time step | dt = 0.01s | 100 Hz control rate | Section 6.1 |
| | Duration | T = 10s | Full transient capture | Section 6.3 |
| | Integrator | RK45 (adaptive) | scipy.integrate.solve_ivp | Section 6.1 |
| | Absolute tolerance | atol = 10^-6 | Numerical accuracy | Section 6.1 |
| | Relative tolerance | rtol = 10^-3 | Computational efficiency | Section 6.1 |
| **Benchmarks** | QW-2 trials | 400 (100/controller) | Nominal scenario | Section 6.3.1 |
| | MT-7 trials | 500 (50/controller × 10 seeds) | Large perturbation | Section 6.3.2 |
| | Random seed | 42 | Reproducibility (NumPy) | Section 6.1 |
| | Initial state | x = [0, 0, 0.2, 0.1, 0, 0] | Standard test condition | Section 6.3 |
| **Statistics** | Significance level | α = 0.05 | 95% confidence | Section 6.4 |
| | Effect size | Cohen's d | Practical significance | Section 6.4 |
| | CI method | Bootstrap BCa (B=10,000) | Non-parametric intervals | Section 6.4 |
| | Multiple comparison | Bonferroni (α/6 = 0.0083) | Family-wise error control | Section 6.4 |
| | Power analysis | 1-β = 0.80 | Sample size justification | Section 6.3 |
| **Performance Metrics** | Computational | t_compute, M_peak | Runtime profiling | Section 6.2.1 |
| | Transient | t_s, OS, t_r | Classical control metrics | Section 6.2.2 |
| | Chattering | CI, f_chatter, E_HF | SMC-specific quality | Section 6.2.3 |
| | Energy | E_ctrl, P_peak | Actuator effort | Section 6.2.4 |
| | Robustness | Δ_tol, A_dist | Sensitivity analysis | Section 6.2.5 |
| **PSO Configuration** | Swarm size | N_p = 40 particles | Balance exploration/cost | Section 5.4 |
| | Max iterations | 200 | Convergence criterion | Section 5.4 |
| | Inertia weight | w = 0.7 | Exploration decay | Section 5.4 |
| | Cognitive coeff | c₁ = 2.0 | Personal memory | Section 5.4 |
| | Social coeff | c₂ = 2.0 | Swarm learning | Section 5.4 |
| | Boundary velocity | v_max = 0.1 × (u_b - l_b) | Prevent explosion | Section 5.4 |
| **Controllers** | Classical SMC | 6 gains [k₁, k₂, λ₁, λ₂, K, k_d] | Baseline controller | Section 3.2 |
| | STA-SMC | 6 gains [k₁, k₂, λ₁, λ₂, K₁, K₂] | Chattering reduction | Section 3.3 |
| | Adaptive SMC | 8 gains [k₁, k₂, λ₁, λ₂, K, k_d, γ, κ] | Uncertainty handling | Section 3.4 |
| | Hybrid Adaptive STA | 8 gains [k₁, k₂, λ₁, λ₂, K₁, K₂, γ, κ] | Combined robustness | Section 3.5 |
| **Disturbance Scenarios** | Friction | d_friction = 0.3 N | Viscous damping | Section 6.5 |
| | Mass uncertainty | Δm = ±20% | Parameter variation | Section 6.5 |
| | Sensor noise | σ_sensor = 0.01 | Gaussian noise | Section 6.5 |
| | External force | F_ext = 2.0 N (pulse) | Impact disturbance | Section 6.5 |
| **Data Archival** | File format | JSON + CSV | Human-readable | Section 6.4 |
| | Compression | gzip (level 9) | Space efficiency | Section 6.4 |
| | Checksum | SHA256 | Integrity verification | Section 6.4 |
| | Repository | Zenodo DOI | Public access | Section 6.4 |

---

**Usage Guidelines:**

- **For replication:** Use values in "Value" column exactly as specified
- **For cross-reference:** See "Reference" column for detailed explanations
- **For custom experiments:** Modify values and document changes in experimental log
- **For troubleshooting:** Compare actual vs expected values from this table

**Critical Parameters (DO NOT MODIFY without justification):**
- Random seed (42) - Required for reproducibility
- Integrator tolerances (atol, rtol) - Affects numerical accuracy
- Statistical significance (α = 0.05) - Standard in control systems literature
- PSO hyperparameters (w, c₁, c₂) - Validated in Section 5.7

**Platform-Specific Adjustments:**
- **CPU speed:** If slower than i7-10700K, increase timeout limits proportionally
- **RAM:** If <16 GB, reduce batch size or use sequential simulation
- **Python version:** If 3.10+, verify NumPy compatibility (no major issues expected)

"""

# Read the original file
file_path = '.artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Insert Section 6.7 Quick Reference before Section 7
search_str = "---\n\n## 7. Performance Comparison Results"
pos = content.find(search_str)
if pos == -1:
    print("[ERROR] Could not find insertion point for Section 6.7")
    exit(1)

# Insert before Section 7
insertion_point = pos
content = content[:insertion_point] + quick_reference + "\n" + content[insertion_point:]

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Section 6.7 (Quick Reference Table 6.1) inserted successfully")
