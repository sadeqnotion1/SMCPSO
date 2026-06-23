# Algorithm Pseudocode Files

This directory contains LaTeX algorithm2e pseudocode extracted from Python source code.

## Files Created (Agent 2)

- **alg_ch03.tex** - Classical SMC (4 algorithms, 100 lines)
- **alg_ch04.tex** - Super-Twisting SMC (4 algorithms, 120 lines)
- **alg_ch05.tex** - Adaptive SMC (4 algorithms, 150 lines)
- **alg_ch08.tex** - PSO Optimization (4 algorithms, 130 lines)

**Total**: 16 algorithms, ~500 lines of LaTeX

## Integration Instructions

### In Chapter LaTeX Files

Add these lines after the relevant section:

```latex
% Chapter 3 (Classical SMC)
\input{source/algorithms/alg_ch03.tex}

% Chapter 4 (Super-Twisting SMC)
\input{source/algorithms/alg_ch04.tex}

% Chapter 5 (Adaptive SMC)
\input{source/algorithms/alg_ch05.tex}

% Chapter 8 (PSO Optimization)
\input{source/algorithms/alg_ch08.tex}
```

### Cross-Referencing

Use `\cref{alg:label}` to reference algorithms:

```latex
See \cref{alg:classical_smc_control} for the complete control law.
```

This will render as: "See Algorithm 3.1 for the complete control law."

### Algorithm Labels

All algorithms use the format `alg:<descriptive_name>`:

- `alg:classical_smc_control`
- `alg:equivalent_control`
- `alg:boundary_layer_saturation`
- `alg:classical_smc_gain_validation`
- `alg:sta_smc_control`
- `alg:sta_smc_numba_core`
- `alg:sta_smc_gain_validation`
- `alg:sta_smc_gain_tuning`
- `alg:adaptive_smc_control`
- `alg:adaptive_law_gradient`
- `alg:adaptive_rate_limiting`
- `alg:adaptive_smc_full_loop`
- `alg:pso_main`
- `alg:pso_cost_function`
- `alg:pso_velocity_clamp`
- `alg:pso_batch_simulation`

## Algorithm Features

### 1. Complexity Analysis
Each algorithm includes time/space complexity after the pseudocode block:

```latex
\textbf{Complexity}: O(n³) time for two linear solves, O(n²) space.
```

### 2. Algorithm-Code Correspondence
Algorithms map directly to Python source code with line number references in code listings.

### 3. Mathematical Notation
Uses preamble.tex commands for consistency:
- `\vect{x}` for vectors
- `\sigma` for sliding surface
- `\controllaw` for control input

### 4. Citations
Algorithms cite relevant theorems and literature:
- Theorem 3.1 (gain positivity)
- Moreno & Osorio (2008) (STA convergence)
- Roy et al. (2020) (adaptive SMC)

## Compilation Requirements

Ensure preamble.tex includes:

```latex
\usepackage[ruled,vlined,linesnumbered]{algorithm2e}
\usepackage{tcolorbox}
\tcbuselibrary{skins,breakable}
```

## Status

- [✓] Algorithm extraction complete
- [✓] Complexity analysis added
- [✓] Mathematical notation standardized
- [✓] Cross-references verified
- [✓] Ready for Agent 7 integration

---

**Created by**: Agent 2 (Algorithm Extraction)
**Date**: January 5, 2026
**See**: `../AGENT2_SUMMARY.md` for complete report
