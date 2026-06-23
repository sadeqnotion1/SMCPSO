# Citation Guide - DIP-SMC-PSO Project

**Document Version:** 1.0
**Date:** November 12, 2025
**Status:** OPERATIONAL

---

## Table of Contents

1. [How to Cite This Work](#how-to-cite-this-work)
2. [BibTeX Entry](#bibtex-entry)
3. [Citation Formats](#citation-formats)
4. [Component Citations](#component-citations)
5. [Related Publications](#related-publications)
6. [Bibliography Management](#bibliography-management)
7. [Citation Validation](#citation-validation)

---

## How to Cite This Work

### Complete Framework

If you use the DIP-SMC-PSO framework in your research, please cite:

**APA Format:**
```
Your Name. (2025). Sliding Mode Control with PSO Optimization for
Double-Inverted Pendulum: A Comprehensive Study. arXiv preprint arXiv:YYMM.NNNNN.
```

**IEEE Format:**
```
Y. Name, "Sliding mode control with PSO optimization for double-inverted
pendulum: A comprehensive study," arXiv preprint arXiv:YYMM.NNNNN, 2025.
```

**Chicago Format:**
```
Name, Your. 2025. "Sliding Mode Control with PSO Optimization for
Double-Inverted Pendulum: A Comprehensive Study." arXiv preprint arXiv:YYMM.NNNNN.
```

### Software Repository

If you use the software implementation:

**APA Format:**
```
Your Name. (2025). dip-smc-pso: Double-Inverted Pendulum Sliding Mode Control
with PSO Optimization [Software]. GitHub. https://github.com/theSadeQ/dip-smc-pso
```

**BibTeX:**
```bibtex
@misc{dipsmc2025software,
  author = {Your Name},
  title = {{dip-smc-pso}: Double-Inverted Pendulum Sliding Mode Control with PSO Optimization},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/theSadeQ/dip-smc-pso}},
  note = {Software framework for SMC research with PSO optimization}
}
```

---

## BibTeX Entry

### Research Paper (arXiv)

```bibtex
@article{dipsmc2025,
  author = {Your Name},
  title = {Sliding Mode Control with {PSO} Optimization for Double-Inverted Pendulum: A Comprehensive Study},
  journal = {arXiv preprint arXiv:YYMM.NNNNN},
  year = {2025},
  month = {November},
  eprint = {YYMM.NNNNN},
  archivePrefix = {arXiv},
  primaryClass = {cs.SY},
  url = {https://arxiv.org/abs/YYMM.NNNNN},
  note = {14 pages, 14 figures. Submitted to IEEE CDC 2025}
}
```

### Conference Paper (if accepted)

```bibtex
@inproceedings{dipsmc2025cdc,
  author = {Your Name},
  title = {Sliding Mode Control with {PSO} Optimization for Double-Inverted Pendulum: A Comprehensive Study},
  booktitle = {Proceedings of the IEEE Conference on Decision and Control (CDC)},
  year = {2025},
  month = {December},
  address = {Milan, Italy},
  pages = {1--6},
  doi = {10.1109/CDC.2025.XXXXXX},
  note = {Presented at CDC 2025}
}
```

### Journal Article (if published)

```bibtex
@article{dipsmc2025tac,
  author = {Your Name},
  title = {Sliding Mode Control with {PSO} Optimization for Double-Inverted Pendulum: A Comprehensive Study},
  journal = {IEEE Transactions on Automatic Control},
  year = {2026},
  volume = {71},
  number = {1},
  pages = {1--14},
  month = {January},
  doi = {10.1109/TAC.2026.XXXXXX},
  issn = {0018-9286}
}
```

---

## Citation Formats

### Inline Citations (Markdown)

**Narrative citation:**
```
Utkin (1977) introduced sliding mode control for variable structure systems.
```

**Parenthetical citation:**
```
Sliding mode control was introduced for variable structure systems (Utkin, 1977).
```

**Multiple authors:**
```
Particle swarm optimization (Kennedy & Eberhart, 1995) has been successfully
applied to controller tuning.
```

**Three or more authors:**
```
The super-twisting algorithm (Moreno et al., 2012) provides second-order
sliding mode control.
```

### BibTeX Key References (LaTeX)

```latex
% Single citation
\cite{utkin1977}

% Multiple citations
\cite{utkin1977, kennedy1995, moreno2012}

% Inline citation
\citet{utkin1977} introduced sliding mode control

% Parenthetical citation
Sliding mode control \citep{utkin1977} was introduced...
```

### RST Citations (Sphinx)

```rst
.. [Utkin1977] Utkin, V.I. (1977). Variable structure systems with sliding
   modes. IEEE Transactions on Automatic Control, 22(2), 212-222.

See [Utkin1977]_ for details on sliding mode control.
```

---

## Component Citations

### Controllers

**Classical SMC:**
```
- Utkin, V.I. (1977). Variable structure systems with sliding modes.
  IEEE TAC, 22(2), 212-222.
- Slotine, J.J.E., & Li, W. (1991). Applied Nonlinear Control. Prentice Hall.
```

**Super-Twisting Algorithm (STA):**
```
- Levant, A. (1993). Sliding order and sliding accuracy in sliding mode control.
  International Journal of Control, 58(6), 1247-1263.
- Moreno, J.A., & Osorio, M. (2012). Strict Lyapunov functions for the
  super-twisting algorithm. IEEE TAC, 57(4), 1035-1040.
```

**Adaptive SMC:**
```
- Slotine, J.J.E., & Li, W. (1991). Applied Nonlinear Control. Prentice Hall.
- Krstic, M., Kanellakopoulos, I., & Kokotovic, P.V. (1995). Nonlinear and
  Adaptive Control Design. John Wiley & Sons.
```

**Hybrid Adaptive STA-SMC:**
```
- Combines adaptive techniques with super-twisting algorithm
- Novel contribution of this work (cite this paper)
```

### PSO Optimization

```
- Kennedy, J., & Eberhart, R. (1995). Particle swarm optimization.
  Proceedings of IEEE ICNN, 1942-1948.
- Shi, Y., & Eberhart, R. (1998). A modified particle swarm optimizer.
  Proceedings of IEEE CEC, 69-73.
- Clerc, M., & Kennedy, J. (2002). The particle swarm - explosion, stability,
  and convergence in a multidimensional complex space. IEEE TEC, 6(1), 58-73.
```

### Double-Inverted Pendulum

```
- Bogdanov, A. (2004). Optimal control of a double inverted pendulum on a cart.
  Technical Report CSE-04-006, OGI School of Science & Engineering.
- Muskinja, N., & Tovornik, B. (2006). Swinging up and stabilization of a
  real inverted pendulum. IEEE TIE, 53(2), 631-639.
```

---

## Related Publications

### Control Theory

```bibtex
@article{utkin1977,
  author = {Utkin, V.I.},
  title = {Variable structure systems with sliding modes},
  journal = {IEEE Transactions on Automatic Control},
  year = {1977},
  volume = {22},
  number = {2},
  pages = {212--222},
  doi = {10.1109/TAC.1977.1101446}
}

@article{levant1993,
  author = {Levant, Arie},
  title = {Sliding order and sliding accuracy in sliding mode control},
  journal = {International Journal of Control},
  year = {1993},
  volume = {58},
  number = {6},
  pages = {1247--1263},
  doi = {10.1080/00207179308923053}
}

@article{moreno2012,
  author = {Moreno, Jaime A. and Osorio, M.},
  title = {Strict Lyapunov Functions for the Super-Twisting Algorithm},
  journal = {IEEE Transactions on Automatic Control},
  year = {2012},
  volume = {57},
  number = {4},
  pages = {1035--1040},
  doi = {10.1109/TAC.2012.2186179}
}
```

### Optimization

```bibtex
@inproceedings{kennedy1995,
  author = {Kennedy, J. and Eberhart, R.},
  title = {Particle swarm optimization},
  booktitle = {Proceedings of IEEE International Conference on Neural Networks},
  year = {1995},
  pages = {1942--1948},
  doi = {10.1109/ICNN.1995.488968}
}

@inproceedings{shi1998,
  author = {Shi, Y. and Eberhart, R.},
  title = {A modified particle swarm optimizer},
  booktitle = {Proceedings of IEEE Congress on Evolutionary Computation},
  year = {1998},
  pages = {69--73},
  doi = {10.1109/ICEC.1998.699146}
}
```

### Benchmarks

```bibtex
@techreport{bogdanov2004,
  author = {Bogdanov, Alexander},
  title = {Optimal Control of a Double Inverted Pendulum on a Cart},
  institution = {OGI School of Science \& Engineering at OHSU},
  year = {2004},
  number = {CSE-04-006},
  url = {https://web.cecs.pdx.edu/~aml/Tech-Reports/}
}
```

---

## Bibliography Management

### Project Bibliography Files

The project uses categorized BibTeX files in `docs/bib/`:

- **adaptive.bib** - Adaptive control references
- **dip.bib** - Double-inverted pendulum references
- **fdi.bib** - Fault detection and isolation
- **numerical.bib** - Numerical methods
- **pso.bib** - PSO optimization references
- **smc.bib** - Sliding mode control references
- **software.bib** - Software engineering references
- **stability.bib** - Stability theory references

### Consolidated Bibliography

A consolidated bibliography for the research paper is available:
```
docs/theory/dip_smc_pso_bibliography.bib
```

This file contains all citations used in the LT-7 research paper.

### Adding New Citations

1. **Determine category:**
   - SMC-related → `docs/bib/smc.bib`
   - PSO-related → `docs/bib/pso.bib`
   - DIP-related → `docs/bib/dip.bib`
   - Other → Appropriate category file

2. **Create BibTeX entry:**
   ```bibtex
   @article{author2025,
     author = {Author, A. and Co-Author, B.},
     title = {Paper Title},
     journal = {Journal Name},
     year = {2025},
     volume = {10},
     number = {1},
     pages = {1--10},
     doi = {10.1234/journal.2025.001}
   }
   ```

3. **Validate entry:**
   ```bash
   python scripts/publication/validate_citations.py --verbose
   ```

4. **Use in documentation:**
   ```markdown
   See [Author & Co-Author, 2025] for details.
   ```

---

## Citation Validation

### Validation Script

The project includes a citation validation script to ensure 100% bibliography coverage:

```bash
# Validate all citations
python scripts/publication/validate_citations.py

# Generate report
python scripts/publication/validate_citations.py --output citation_report.txt

# Verbose mode
python scripts/publication/validate_citations.py --verbose
```

### Validation Process

1. **Extract citations** from all documentation files (docs/**/*.md, docs/**/*.rst)
2. **Parse BibTeX files** to collect entry keys
3. **Cross-reference** citations with BibTeX entries
4. **Report missing citations** and unused entries
5. **Exit code 0** = 100% coverage, **1** = missing citations

### Output

```
================================================================================
 Citation Validation Report
================================================================================

Summary Statistics:
--------------------------------------------------------------------------------
  Documentation files with citations: 127
  Total citations extracted:          243
  Covered citations:                  241 (99%)
  Missing citations:                  2
  Total BibTeX entries:               156
  Unused BibTeX entries:              14

[ERROR] 2 citations missing from bibliography

Missing Citations:
--------------------------------------------------------------------------------
  - NewAuthor2025
      Used in: theory/lyapunov_proofs.md
  - AnotherAuthor2024
      Used in: research/benchmarks.md

Recommendations:
--------------------------------------------------------------------------------
  1. Add missing BibTeX entries to docs/bib/*.bib files
  2. Update citations to use existing BibTeX keys
  3. Verify citation format: [Author et al., Year] or @key

================================================================================
```

### Fix Missing Citations

1. **Add BibTeX entry:**
   ```bibtex
   @article{newauthor2025,
     author = {New, Author},
     title = {Paper Title},
     journal = {Journal},
     year = {2025}
   }
   ```

2. **Update citation:**
   ```markdown
   See @newauthor2025 for details.
   ```

3. **Re-validate:**
   ```bash
   python scripts/publication/validate_citations.py
   ```

---

## References

### Bibliography Standards

- **IEEE Style:** https://ieee-dataport.org/sites/default/files/analysis/27/IEEE%20Citation%20Guidelines.pdf
- **APA Style 7th ed:** https://apastyle.apa.org/
- **Chicago Manual of Style:** https://www.chicagomanualofstyle.org/

### BibTeX Resources

- **BibTeX.org:** http://www.bibtex.org/
- **JabRef (bibliography manager):** https://www.jabref.org/
- **Zotero (reference manager):** https://www.zotero.org/

### Related Guides

- **arXiv Submission:** `docs/publication/ARXIV_SUBMISSION_GUIDE.md`
- **Submission Checklist:** `docs/publication/SUBMISSION_CHECKLIST.md`
- **GitHub Pages Guide:** `docs/publication/GITHUB_PAGES_GUIDE.md`

---

**End of Citation Guide**

**Document Version:** 1.0
**Last Updated:** November 12, 2025
**Status:** OPERATIONAL
**Maintenance:** Update when research paper is published (arXiv ID, conference, journal)
