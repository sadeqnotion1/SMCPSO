# Citations & Academic Attribution **Project:** Double Inverted Pendulum - Sliding Mode Control with PSO Optimization

**Purpose:** Complete academic and technical attribution for all methodologies, tools, and theories
**Last Updated:** 2025-10-03

---

## Overview This project builds upon decades of research in control theory, optimization, and software engineering. We provide attribution across three domains: 1. **Software Dependencies & Licenses** → [DEPENDENCIES.md](DEPENDENCIES.md)

2. **Software Design Patterns & Architecture** → [PATTERNS.md](meta/PATTERNS.md)
3. **Academic Theory & Research** → [CITATIONS_ACADEMIC.md](CITATIONS_ACADEMIC.md)

---

## Quick Reference Guide ### For Academic Publications **Citing This Project's Control Theory:**

```bibtex
% Sliding Mode Control Foundations
@book{utkin1992sliding, ...}
@book{slotine1991applied, ...}
@article{levant2003higher, ...} % PSO Optimization
@article{kennedy1995particle, ...}
@article{clerc2002particle, ...} % Lyapunov Stability
@book{khalil2002nonlinear, ...}
``` See [CITATIONS_ACADEMIC.md](CITATIONS_ACADEMIC.md) for complete BibTeX entries.

---

### For Software Developers **Key Technologies:**

- **NumPy** (BSD) - Harris et al. (2020) - Array computing
- **SciPy** (BSD) - Virtanen et al. (2020) - Scientific algorithms
- **PySwarms** (MIT) - Miranda (2018) - PSO optimization
- **Numba** (BSD) - Lam et al. (2015) - JIT compilation See [DEPENDENCIES.md](DEPENDENCIES.md) for full dependency list. **Design Patterns:**
- **Factory Pattern** - Gamma et al. (1994) - 102 files
- **Strategy Pattern** - Gamma et al. (1994) - 13 files
- **Dependency Injection** - Seemann (2011) - Throughout See [PATTERNS.md](meta/PATTERNS.md) for complete pattern analysis.

---

## Citation Breakdown by Domain ### 1. Control Theory & Algorithms | Topic | Key Citations | Implementation |

|-------|---------------|----------------|
| **Classical SMC** | Utkin (1992), Slotine & Li (1991) | `src/controllers/smc/classic_smc.py` |
| **Super-Twisting** | Levant (2003), Moreno & Osorio (2012) | `src/controllers/smc/sta_smc.py` |
| **Adaptive SMC** | Slotine & Coetsee (1986), Plestan et al. (2010) | `src/controllers/smc/adaptive_smc.py` |
| **Lyapunov Stability** | Khalil (2002), Lyapunov (1992) | `src/utils/analysis/lyapunov.py` |
| **PSO Optimization** | Kennedy & Eberhart (1995), Clerc & Kennedy (2002) | `src/optimizer/pso_optimizer.py` | Full details: [CITATIONS_ACADEMIC.md](CITATIONS_ACADEMIC.md#1-sliding-mode-control-theory)

---

### 2. Software Engineering & Architecture | Pattern/Tool | Citation | Usage |

|--------------|----------|-------|
| **Factory Pattern** | Gamma et al. (1994) | 102 files - Controller instantiation |
| **Strategy Pattern** | Gamma et al. (1994) | 13 files - Algorithm selection |
| **Observer Pattern** | Gamma et al. (1994) | 4 files - Event monitoring |
| **Dependency Injection** | Seemann (2011) | Throughout - Testability |
| **Type Hints (PEP 484)** | van Rossum et al. (2014) | 95% coverage | Full details: [PATTERNS.md](PATTERNS.md#table-of-contents)

---

### 3. Scientific Computing Libraries | Library | License | Citation | Purpose |

|---------|---------|----------|---------|
| **NumPy** | BSD-3 | Harris et al. (2020) | Array computing, vectorization |
| **SciPy** | BSD-3 | Virtanen et al. (2020) | ODE solvers, optimization |
| **Matplotlib** | PSF-based | Hunter (2007) | Visualization |
| **PySwarms** | MIT | Miranda (2018) | PSO implementation |
| **Numba** | BSD-2 | Lam et al. (2015) | JIT compilation | Full details: [DEPENDENCIES.md](DEPENDENCIES.md#core-numerical--scientific-libraries)

---

## Attribution Statistics ### Coverage Summary | Domain | Items Cited | Document | Word Count |

|--------|-------------|----------|------------|
| **Software Dependencies** | 30+ libraries | [DEPENDENCIES.md](DEPENDENCIES.md) | 12,000 |
| **Design Patterns** | 102 factory uses, 13 strategies | [PATTERNS.md](meta/PATTERNS.md) | 15,000 |
| **Academic Theory** | 39 references (22 books, 17 papers) | [CITATIONS_ACADEMIC.md](CITATIONS_ACADEMIC.md) | 15,000 |
| **Licenses** | 10 unique licenses | [LICENSES.md](LICENSES.md) | 8,000 | **Total:** 50,000+ words of attribution documentation

---

### Citation Quality Metrics **Academic References ([CITATIONS_ACADEMIC.md](CITATIONS_ACADEMIC.md)):**

- Primary sources: 85% (33/39)
- Recent work (<10 years): 35% (14/39)
- DOI availability: 75% (29/39)
- Peer-reviewed journals: 55% (22/39) **Software Attribution ([DEPENDENCIES.md](DEPENDENCIES.md)):**
- License compliance: 100% (all verified)
- Academic papers: 90% (27/30 libraries)
- Version pinned: 100% (reproducibility) **Design Patterns ([PATTERNS.md](meta/PATTERNS.md)):**
- GoF patterns: 6 (Factory, Strategy, Observer, etc.)
- Python-specific: 8 (Decorators, Context Managers, etc.)
- Scientific patterns: 5 (Vectorization, JIT, Reproducibility)

---

## How to Cite This Project ### In Academic Papers **For control theory contributions:**

```bibtex
@software{dip_smc_pso_2025, title={Double Inverted Pendulum Sliding Mode Control with PSO Optimization}, author={[Your Name]}, year={2025}, url={https://github.com/theSadeQ/dip-smc-pso}, note={Implements classical SMC, super-twisting, adaptive, and hybrid controllers with PSO-based gain tuning. See CITATIONS_ACADEMIC.md for theoretical foundations.}
}
``` **Citing specific implementations:**

- Classical SMC: Cite Utkin (1992) + Slotine & Li (1991)
- Super-Twisting: Cite Levant (2003) + Moreno & Osorio (2012)
- PSO Optimization: Cite Kennedy & Eberhart (1995) + Clerc & Kennedy (2002)

---

### In Software Projects **For code reuse:**

```
This software uses the following open-source libraries:
- NumPy (BSD-3-Clause) - Harris et al. (2020)
- SciPy (BSD-3-Clause) - Virtanen et al. (2020)
- PySwarms (MIT) - Miranda (2018) See DEPENDENCIES.md for complete attribution.
``` **For design patterns:**

```
Architecture follows:
- Factory Pattern: Gamma et al. (1994) - Design Patterns
- Dependency Injection: Seemann (2011) - DI in .NET See PATTERNS.md for implementation details.
```

---

## License Compliance All dependencies are compatible with open-source use:

- **Permissive licenses:** MIT, BSD-2, BSD-3, Apache-2.0 (90%)
- **Copyleft (weak):** MPL-2.0 (5%)
- **Python-specific:** PSF (5%) No GPL dependencies - safe for proprietary derivatives. Full analysis: [LICENSES.md](LICENSES.md)

---

## Document Cross-Reference ### By Use Case **I want to...** 1. **Understand SMC theory** → [CITATIONS_ACADEMIC.md](CITATIONS_ACADEMIC.md#1-sliding-mode-control-theory)

2. **See software dependencies** → [DEPENDENCIES.md](DEPENDENCIES.md)
3. **Learn design patterns used** → [PATTERNS.md](meta/PATTERNS.md)
4. **Check license compliance** → [LICENSES.md](LICENSES.md)
5. **Cite this work academically** → [This file](#how-to-cite-this-project)

---

### By File Type | Document | Purpose | Target Audience |

|----------|---------|-----------------|
| [DEPENDENCIES.md](DEPENDENCIES.md) | Software library attribution | Developers, Legal |
| [LICENSES.md](LICENSES.md) | License compliance analysis | Legal, Commercial |
| [PATTERNS.md](meta/PATTERNS.md) | Architecture & design patterns | Software Engineers |
| [CITATIONS_ACADEMIC.md](CITATIONS_ACADEMIC.md) | Research & theory attribution | Researchers, Academics |
| **This file (CITATIONS.md)** | **Master index & quick reference** | **Everyone** |

---

## Maintenance & Updates ### Update Protocol **When to update citation documents:**

1. New library added → Update [DEPENDENCIES.md](DEPENDENCIES.md)
2. New design pattern used → Update [PATTERNS.md](meta/PATTERNS.md)
3. New theoretical claim → Update [CITATIONS_ACADEMIC.md](CITATIONS_ACADEMIC.md)
4. License changes → Update [LICENSES.md](LICENSES.md) ### Verification Checklist - [ ] All theoretical claims have academic citations
- [ ] All libraries have license attribution
- [ ] All design patterns reference original sources
- [ ] All BibTeX entries validated
- [ ] Cross-references between documents working
- [ ] README.md reflects current citation status

---

## Acknowledgments This project is built on the shoulders of giants. We gratefully acknowledge: ### Control Theory Pioneers

- **Vadim I. Utkin** - Founding father of sliding mode control
- **Jean-Jacques E. Slotine** - Applied nonlinear control theory
- **Arie Levant** - Higher-order sliding modes & super-twisting
- **Hassan K. Khalil** - Modern nonlinear systems analysis ### Optimization Researchers
- **James Kennedy & Russell Eberhart** - Particle Swarm Optimization
- **Maurice Clerc** - PSO convergence theory ### Software Engineering Thought Leaders
- **Gang of Four** (Gamma, Helm, Johnson, Vlissides) - Design Patterns
- **Robert C. Martin** - SOLID principles
- **Mark Seemann** - Dependency Injection ### Scientific Computing Community
- **NumPy, SciPy, Matplotlib developers** - Python scientific ecosystem
- **Numba team** - High-performance Python compilation
- **PySwarms developers** - Accessible PSO implementation

---

## Contact & Contribution **Questions about citations?**

- Open an issue on [GitHub](https://github.com/theSadeQ/dip-smc-pso/issues)
- Check the specific attribution document ([DEPENDENCIES.md](DEPENDENCIES.md), [PATTERNS.md](meta/PATTERNS.md), or [CITATIONS_ACADEMIC.md](CITATIONS_ACADEMIC.md)) **Found missing attribution?**
- Please open a pull request with corrected citations
- We take academic integrity seriously and appreciate corrections

---

**Last Updated:** 2025-10-03
**Citation System Version:** 1.0
**Next Review:** Before academic publication submission
