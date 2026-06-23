# Bibliography & Academic References

Complete academic citations for all control theory, optimization theory, and mathematical foundations used in this project.

## Master Bibliography

**Note**: This page provides a category-organized view of the project bibliography. For the complete authoritative bibliography with full research context, impact metrics, and citation guidelines, see {doc}`references/bibliography`.

**Quick Category Navigation:**

- {ref}`sliding-mode-control-theory` - SMC foundations
- {ref}`pso-optimization-theory` - PSO algorithms
- {ref}`stability-theory-refs` - Lyapunov stability
- {ref}`adaptive-control-theory` - Adaptive systems
- {ref}`fault-detection-refs` - FDI methods
- {ref}`numerical-methods-refs` - ODE integration
- {ref}`software-tools-refs` - Python libraries

---

(sliding-mode-control-theory)=
## Sliding Mode Control Theory

Foundational and advanced SMC techniques including classical, super-twisting, adaptive, and hybrid controllers.

**See**: {doc}`references/bibliography` for complete SMC references with research context

(pso-optimization-theory)=
## PSO Optimization Theory

Particle swarm optimization theory, convergence analysis, and parameter tuning methods.

**See**: {doc}`references/bibliography` for complete PSO references with convergence analysis

(stability-theory-refs)=
## Stability Theory

Lyapunov stability, finite-time stability, and fixed-time stability analysis.

**See**: {doc}`references/bibliography` for complete stability theory references

(adaptive-control-theory)=
## Adaptive Control Theory

Model reference adaptive systems, robust adaptive laws, and parameter estimation.

**See**: {doc}`references/bibliography` for complete adaptive control references

(fault-detection-refs)=
## Fault Detection & Isolation

Threshold selection, hysteresis methods, and robust fault diagnosis techniques.

**See**: {doc}`references/bibliography` for complete FDI references

(numerical-methods-refs)=
## Numerical Methods

Runge-Kutta integration, stiff ODE solvers, and numerical stability analysis.

**See**: {doc}`references/bibliography` for complete numerical methods references

(software-tools-refs)=
## Software & Tools

Python scientific computing libraries and numerical computation frameworks.

**See**: {doc}`references/bibliography` for complete software references

---

## Complete Bibliography

**For the full bibliography with citations, see**: {doc}`references/bibliography`

The master bibliography includes:
- Complete BibTeX entries for all references
- Research area categorization
- Citation quality metrics
- Impact factors and citation counts
- Keyword-based filtering
- Citation style guidelines

---

## Citation Usage in Documentation

To cite a reference in your documentation, use the `{cite}` role:

```markdown
See {cite}`smc_utkin_1992_sliding_modes` for the original sliding mode formulation.

Multiple citations: {cite}`pso_kennedy_1995_particle_swarm_optimization,pso_clerc_2002_particle_swarm`
```

**Example output:**

See {cite}`smc_utkin_1992_sliding_modes` for the original sliding mode formulation.

---

## See Also

For detailed attribution with exact page numbers and theorem references:

- {doc}`references/bibliography` - **Master Bibliography** with full research context
- {doc}`CITATIONS_ACADEMIC` - Academic theory citations linked to exact locations in codebase
- {doc}`DEPENDENCIES` - Software library citations and licenses
- {doc}`meta/PATTERNS` - Design pattern attribution and architectural decisions
- {doc}`CITATIONS` - Master citation index and quick reference guide

---

## BibTeX Source Files

The bibliography is generated from the following BibTeX files:

- `refs.bib` - Main bibliography
- `bib/smc.bib` - Sliding mode control references
- `bib/pso.bib` - PSO optimization references
- `bib/stability.bib` - Lyapunov and stability theory
- `bib/adaptive.bib` - Adaptive control theory
- `bib/fdi.bib` - Fault detection and isolation
- `bib/numerical.bib` - Numerical methods and integration
- `bib/software.bib` - Software and tools
- `bib/dip.bib` - Double inverted pendulum references

All BibTeX files are located in the `docs/` and `docs/bib/` directories.
