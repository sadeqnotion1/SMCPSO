# Annotated Code Listings

This directory contains annotated Python code listings with line-by-line correspondence to algorithm pseudocode.

## Files Created (Agent 2)

- **listing_ch03_classical_smc.tex** - Classical SMC (184 lines, fully annotated)
- **listing_ch08_pso.tex** - PSO Tuner (231 lines, fully annotated)

**Total**: 2 comprehensive listings, ~415 lines of LaTeX

## Integration Instructions

### In Appendix B (Code Listings)

Add these files as separate sections:

```latex
\chapter{Appendix B: Code Listings}

\section{Classical Sliding Mode Controller}
\input{source/code_listings/listing_ch03_classical_smc.tex}

\section{PSO Tuner for Controller Optimization}
\input{source/code_listings/listing_ch08_pso.tex}
```

### Cross-Referencing Listings

Use `\cref{lst:label}` to reference code listings:

```latex
See \cref{lst:classical_smc} for the complete implementation.
```

This will render as: "See Listing B.1 for the complete implementation."

### Listing Labels

All listings use the format `lst:<descriptive_name>`:

- `lst:classical_smc` - Classical SMC full implementation
- `lst:pso_tuner` - PSO Tuner full implementation

## Listing Features

### 1. Line-by-Line Algorithm Mapping

Each listing includes a correspondence table:

```latex
\textbf{Algorithm-Code Correspondence}:
\begin{itemize}
    \item \textbf{Line 53-57}: Sliding surface → Algorithm 3.1, Line 2
    \item \textbf{Line 71-108}: Equivalent control → Algorithm 3.2, Complete
    ...
\end{itemize}
```

### 2. Complexity Annotations

Complexity is documented both:
- In algorithm blocks (as `\textbf{Complexity}: ...`)
- In code comments (as `# O(n³) time complexity`)

### 3. In-Code Algorithm References

Python code includes comments like:
```python
# Maps to Algorithm 3.1, Line 2
sigma = self.k1 * (theta1_dot + self.lam1 * theta1) + ...
```

### 4. Detailed Docstrings

Every method includes:
- **Args**: Input parameters with types
- **Returns**: Output type and meaning
- **Complexity**: Time/space analysis
- **Maps to**: Corresponding algorithm

Example:
```python
def _compute_sliding_surface(self, state):
    """Compute sliding surface sigma (Equation 3.7).

    Maps to Algorithm 3.1, Line 2.
    Time complexity: O(1), Space: O(1).
    """
```

## Code Listing Style

### Python Syntax Highlighting

Uses `listings` package with custom Python style:

```latex
\lstdefinestyle{pythonstyle}{
    language=Python,
    basicstyle=\ttfamily\small,
    keywordstyle=\color{blue}\bfseries,
    commentstyle=\color{gray}\itshape,
    stringstyle=\color{red},
    numbers=left,
    numberstyle=\tiny\color{gray},
    frame=single,
    breaklines=true
}
```

### Line Numbering

All listings use `numbers=left` for easy reference to specific lines in correspondence tables.

### Frame Style

`frame=single` provides a clear visual boundary for code blocks.

## Compilation Requirements

Ensure preamble.tex includes:

```latex
\usepackage{listings}
\usepackage{xcolor}
\lstset{style=pythonstyle}
```

Or if using minted (requires -shell-escape):

```latex
\usepackage{minted}
\usemintedstyle{friendly}
```

## What's NOT Included (Deferred to Agent 6)

The following code listings are planned for Appendix C but not yet created:

- `listing_ch04_sta_smc.tex` - Super-Twisting SMC (Numba core)
- `listing_ch05_adaptive_smc.tex` - Adaptive SMC
- `listing_ch06_hybrid_smc.tex` - Hybrid Adaptive STA-SMC
- `listing_ch07_swing_up.tex` - Swing-Up Controller
- `listing_ch11_factory.tex` - Controller Factory Pattern
- `listing_ch11_config.tex` - Config.yaml with Pydantic Validation
- `listing_ch11_tests.tex` - Test Suite Example

**Recommendation**: Agent 6 (Software Chapter) should create these for Appendix C (30 pages of complete annotated source).

## Algorithm-Code Verification

### Classical SMC (listing_ch03_classical_smc.tex)

| Algorithm | Code Method | Lines | Verified |
|-----------|-------------|-------|----------|
| Alg 3.1 (Control Law) | `compute_control()` | 127-165 | ✓ |
| Alg 3.2 (Equiv Control) | `_compute_equivalent_control()` | 71-108 | ✓ |
| Alg 3.3 (Saturation) | `saturate()` utility | - | ✓ |
| Alg 3.4 (Validation) | `validate_gains()` | 168-184 | ✓ |

### PSO Tuner (listing_ch08_pso.tex)

| Algorithm | Code Method | Lines | Verified |
|-----------|-------------|-------|----------|
| Alg 8.1 (PSO Main) | `optimise()` | 179-231 | ✓ |
| Alg 8.2 (Cost Function) | `_compute_cost_from_traj()` | 63-130 | ✓ |
| Alg 8.3 (Velocity Clamp) | Velocity clamp setup | 214-219 | ✓ |
| Alg 8.4 (Batch Sim) | `_fitness()` with batch call | 147-163 | ✓ |

**Verification Rate**: 100% (8/8 algorithms mapped)

## Status

- [✓] Classical SMC listing complete
- [✓] PSO Tuner listing complete
- [✓] Algorithm-code correspondence verified
- [✓] Complexity analysis included
- [✓] Cross-references to equations/theorems added
- [✓] Ready for Agent 7 integration

---

**Created by**: Agent 2 (Algorithm Extraction)
**Date**: January 5, 2026
**See**: `../AGENT2_SUMMARY.md` for complete report
