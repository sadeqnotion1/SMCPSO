# Software Dependencies & Citations **Project:** Double Inverted Pendulum - Sliding Mode Control with PSO Optimization

**Last Updated:** 2025-10-03
**Total Dependencies:** 30+ external libraries This document provides attribution for all software dependencies used in this project, including proper citations, licenses, and usage information.

---

## Table of Contents 1. [Core Scientific Computing](#core-scientific-computing)

2. [Optimization & Control](#optimization--control)
3. [Performance & Compilation](#performance--compilation)
4. [Configuration & Validation](#configuration--validation)
5. [Testing Framework](#testing-framework)
6. [Web Interface](#web-interface)
7. [Documentation](#documentation)
8. [Code Quality Tools](#code-quality-tools)
9. [License Summary](#license-summary)
10. [Citation Instructions](#citation-instructions)

---

## Core Scientific Computing ### NumPy

- **Version:** ≥1.21.0, <2.0.0
- **License:** BSD-3-Clause
- **Purpose:** Core numerical computing and array operations
- **GitHub:** https://github.com/numpy/numpy
- **Citation:** ```bibtex @article{harris2020array, title={Array programming with NumPy}, author={Harris, Charles R and Millman, K Jarrod and van der Walt, St{\'e}fan J and others}, journal={Nature}, volume={585}, number={7825}, pages={357--362}, year={2020}, publisher={Nature Publishing Group}, doi={10.1038/s41586-020-2649-2} } ```
- **Used in:** All numerical computations, matrix operations, dynamics calculations
- **Note:** Pinned to <2.0.0 for Numba compatibility

---

### SciPy

- **Version:** ≥1.10.0, <1.14.0
- **License:** BSD-3-Clause
- **Purpose:** Scientific algorithms (ODE integration, optimization, signal processing)
- **GitHub:** https://github.com/scipy/scipy
- **Citation:** ```bibtex @article{virtanen2020scipy, title={SciPy 1.0: fundamental algorithms for scientific computing in Python}, author={Virtanen, Pauli and Gommers, Ralf and Oliphant, Travis E and others}, journal={Nature methods}, volume={17}, number={3}, pages={261--272}, year={2020}, publisher={Nature Publishing Group}, doi={10.1038/s41592-019-0686-2} } ```
- **Used in:** ODE integration (RK45), statistical functions, optimization solvers

---

### Matplotlib

- **Version:** ≥3.6.0, <4.0.0
- **License:** PSF-based (BSD-compatible)
- **Purpose:** Plotting and data visualization
- **GitHub:** https://github.com/matplotlib/matplotlib
- **Citation:** ```bibtex @article{hunter2007matplotlib, title={Matplotlib: A 2D graphics environment}, author={Hunter, John D}, journal={Computing in science \& engineering}, volume={9}, number={3}, pages={90--95}, year={2007}, publisher={IEEE Computer Society}, doi={10.1109/MCSE.2007.55} } ```
- **Used in:** Performance plots, animation, simulation visualization

---

### Pandas

- **Version:** ≥1.5.0, <3.0.0
- **License:** BSD-3-Clause
- **Purpose:** Data management and analysis of simulation results
- **GitHub:** https://github.com/pandas-dev/pandas
- **Citation:** ```bibtex @software{reback2020pandas, author={The pandas development team}, title={pandas-dev/pandas: Pandas}, year={2020}, publisher={Zenodo}, version={latest}, doi={10.5281/zenodo.3509134}, url={https://doi.org/10.5281/zenodo.3509134} } ```
- **Used in:** CSV export, data analysis, result tabulation

---

## Optimization & Control ### PySwarms

- **Version:** ≥1.3.0, <2.0.0
- **License:** MIT
- **Purpose:** **Primary PSO implementation** for controller gain tuning
- **GitHub:** https://github.com/ljvmiranda921/pyswarms
- **Citation:** ```bibtex @article{miranda2018pyswarms, title={PySwarms: a research toolkit for Particle Swarm Optimization in Python}, author={Miranda, Lester James V}, journal={Journal of Open Source Software}, volume={3}, number={21}, pages={433}, year={2018}, doi={10.21105/joss.00433} } ```
- **Used in:** PSO optimization for SMC gain tuning, hyperparameter optimization
- **Critical dependency** - Core to project functionality

---

### Optuna

- **Version:** ≥3.0.0, <4.0.0
- **License:** MIT
- **Purpose:** Alternative hyperparameter optimization framework
- **GitHub:** https://github.com/optuna/optuna
- **Citation:** ```bibtex @inproceedings{akiba2019optuna, title={Optuna: A next-generation hyperparameter optimization framework}, author={Akiba, Takuya and Sano, Shotaro and Yanase, Toshihiko and Ohta, Takeru and Koyama, Masanori}, booktitle={Proceedings of the 25th ACM SIGKDD international conference on knowledge discovery \& data mining}, pages={2623--2631}, year={2019}, doi={10.1145/3292500.3330701} } ```
- **Used in:** Alternative optimization backend, hyperparameter tuning experiments

---

### CVXPY

- **Version:** ≥1.3.0, <2.0.0
- **License:** Apache 2.0
- **Purpose:** Convex optimization for experimental MPC controller
- **GitHub:** https://github.com/cvxpy/cvxpy
- **Citation:** ```bibtex @article{diamond2016cvxpy, title={CVXPY: A Python-embedded modeling language for convex optimization}, author={Diamond, Steven and Boyd, Stephen}, journal={The Journal of Machine Learning Research}, volume={17}, number={1}, pages={2909--2913}, year={2016}, publisher={JMLR. org} } ```
- **Used in:** MPC constraint optimization (experimental feature)

---

### PyModbus

- **Version:** ≥3.6.0, <4.0.0
- **License:** BSD-3-Clause
- **Purpose:** Modbus communication for industrial control interfaces
- **GitHub:** https://github.com/pymodbus-dev/pymodbus
- **Citation:** GitHub repository (no formal paper)
- **Used in:** HIL (Hardware-in-the-Loop) communication

---

### H5PY

- **Version:** ≥3.11.0, <4.0.0
- **License:** BSD-3-Clause
- **Purpose:** HDF5 file format support for large datasets
- **GitHub:** https://github.com/h5py/h5py
- **Citation:** ```bibtex @software{collette2013h5py, author={Collette, Andrew}, title={Python and HDF5}, year={2013}, publisher={O'Reilly Media, Inc.}, isbn={9781449367831} } ```
- **Used in:** Saving large simulation datasets, batch results

---

## Performance & Compilation ### Numba

- **Version:** ≥0.56.0, <0.60.0
- **License:** BSD-2-Clause
- **Purpose:** **JIT compiler** for accelerating Python simulations
- **GitHub:** https://github.com/numba/numba
- **Citation:** ```bibtex @inproceedings{lam2015numba, title={Numba: A llvm-based python jit compiler}, author={Lam, Siu Kwan and Pitrou, Antoine and Seibert, Stanley}, booktitle={Proceedings of the Second Workshop on the LLVM Compiler Infrastructure in HPC}, pages={1--6}, year={2015}, doi={10.1145/2833157.2833162} } ```
- **Used in:** Vectorized simulation, batch processing, performance-critical loops
- **Critical dependency** - Enables real-time simulation performance
- **Note:** Must be compatible with NumPy <2.0.0

---

## Configuration & Validation ### PyYAML

- **Version:** ≥6.0, <7.0
- **License:** MIT
- **Purpose:** YAML configuration file parsing
- **GitHub:** https://github.com/yaml/pyyaml
- **Citation:** GitHub repository (no formal paper)
- **Used in:** Parsing `config.yaml` for all configuration management

---

### Pydantic

- **Version:** ≥2.5.0, <3.0.0
- **License:** MIT
- **Purpose:** Configuration validation and type-safe data structures
- **GitHub:** https://github.com/pydantic/pydantic
- **Docs:** https://docs.pydantic.dev/
- **Citation:** GitHub repository
- **Used in:** Type-safe configuration, parameter validation, data models

---

### Pydantic Settings

- **Version:** ≥2.0.0, <3.0.0
- **License:** MIT
- **Purpose:** Extension for Pydantic to manage application settings
- **GitHub:** https://github.com/pydantic/pydantic-settings
- **Used in:** Environment-based configuration

---

### JSONSchema

- **Version:** ≥4.17.0, <5.0.0
- **License:** MIT
- **Purpose:** JSON validation for research batch plans
- **GitHub:** https://github.com/python-jsonschema/jsonschema
- **Used in:** Validating research batch JSON files

---

## Testing Framework ### pytest

- **Version:** ≥7.4.0, <9.0.0
- **License:** MIT
- **Purpose:** **Core testing framework**
- **GitHub:** https://github.com/pytest-dev/pytest
- **Docs:** https://docs.pytest.org/
- **Used in:** All unit tests, integration tests, test discovery

---

### pytest-benchmark

- **Version:** ≥4.0.0, <5.0.0
- **License:** BSD-2-Clause
- **Purpose:** Performance benchmarking within pytest
- **GitHub:** https://github.com/ionelmc/pytest-benchmark
- **Used in:** Controller performance benchmarks, optimization speed tests

---

### Hypothesis

- **Version:** ≥6.70.0, <7.0.0
- **License:** MPL 2.0
- **Purpose:** Property-based testing for edge case discovery
- **GitHub:** https://github.com/HypothesisWorks/hypothesis
- **Citation:** ```bibtex @software{maciver2019hypothesis, author={MacIver, David R and Hatfield-Dodds, Zac and Contributors}, title={Hypothesis: A new approach to property-based testing}, year={2019}, publisher={Journal of Open Source Software}, doi={10.21105/joss.01891} } ```
- **Used in:** Property-based tests for control laws, stability verification

---

## Web Interface ### Streamlit

- **Version:** ≥1.28.0, <2.0.0
- **License:** Apache 2.0
- **Purpose:** Interactive web dashboard framework
- **GitHub:** https://github.com/streamlit/streamlit
- **Docs:** https://docs.streamlit.io/
- **Used in:** Main web UI (`streamlit_app.py`), visualization dashboard

---

### Plotly

- **Version:** ≥5.15.0, <6.0.0
- **License:** MIT
- **Purpose:** Interactive plotting for web UI
- **GitHub:** https://github.com/plotly/plotly.py
- **Used in:** Interactive plots in Streamlit dashboard

---

### Altair

- **Version:** ≥4.2.0, <6.0.0
- **License:** BSD-3-Clause
- **Purpose:** Declarative statistical visualization
- **GitHub:** https://github.com/altair-viz/altair
- **Citation:** ```bibtex @article{vanderplas2018altair, title={Altair: Interactive statistical visualizations for python}, author={VanderPlas, Jacob and Granger, Brian and Heer, Jeffrey and others}, journal={Journal of open source software}, volume={3}, number={32}, pages={1057}, year={2018}, doi={10.21105/joss.01057} } ```
- **Used in:** Statistical charts in Streamlit dashboard

---

### Watchdog

- **Version:** ≥3.0.0, <4.0.0
- **License:** Apache 2.0
- **Purpose:** File system event monitoring for Streamlit hot-reloading
- **GitHub:** https://github.com/gorakhargosh/watchdog
- **Used in:** Development file watching

---

### aiohttp

- **Version:** ≥3.9.0, <4.0.0
- **License:** Apache 2.0
- **Purpose:** Asynchronous HTTP client/server
- **GitHub:** https://github.com/aio-libs/aiohttp
- **Used in:** Async communication in HIL interfaces

---

### PyZMQ

- **Version:** ≥26.0.0, <27.0.0
- **License:** BSD-3-Clause + LGPL
- **Purpose:** Python bindings for ZeroMQ messaging
- **GitHub:** https://github.com/zeromq/pyzmq
- **Used in:** Real-time messaging in HIL plant server

---

### aio-pika

- **Version:** ≥9.4.0, <10.0.0
- **License:** Apache 2.0
- **Purpose:** RabbitMQ client for asyncio
- **GitHub:** https://github.com/mosquito/aio-pika
- **Used in:** Message queuing for distributed simulation

---

## Documentation ### Sphinx

- **Version:** ≥5.0.0, <8.0.0
- **License:** BSD-2-Clause
- **Purpose:** **Core documentation generator**
- **GitHub:** https://github.com/sphinx-doc/sphinx
- **Docs:** https://www.sphinx-doc.org/
- **Used in:** Building HTML/PDF documentation

---

### Sphinx RTD Theme

- **Version:** ≥1.3.0, <3.0.0
- **License:** MIT
- **Purpose:** "Read the Docs" theme for Sphinx
- **GitHub:** https://github.com/readthedocs/sphinx_rtd_theme
- **Used in:** Documentation styling

---

### Sphinx Extensions (10+ packages) **sphinxcontrib-bibtex** (≥2.5.0):

- **License:** BSD-2-Clause
- **Purpose:** Bibliography support
- **Used in:** Academic citations in docs **sphinx-copybutton** (≥0.5.0):
- **License:** MIT
- **Purpose:** Copy buttons for code blocks
- **Used in:** User-friendly documentation **sphinx-math-dollar** (≥1.2.0):
- **License:** MIT
- **Purpose:** LaTeX-style math with $...$
- **Used in:** Mathematical equations **sphinx-design** (≥0.4.0):
- **License:** MIT
- **Purpose:** Responsive web components (grids, cards)
- **Used in:** Modern documentation layout **sphinx-togglebutton** (≥0.3.0):
- **License:** MIT
- **Purpose:** Collapsible content sections
- **Used in:** Expandable documentation **sphinxcontrib-mermaid** (≥0.8.0):
- **License:** BSD-2-Clause
- **Purpose:** Mermaid diagram rendering
- **Used in:** Architecture diagrams **sphinxcontrib-plantuml** (≥0.24):
- **License:** BSD-2-Clause
- **Purpose:** PlantUML diagram rendering
- **Used in:** UML diagrams **myst-parser** (≥1.0.0):
- **License:** MIT
- **Purpose:** Markdown parsing in Sphinx
- **Used in:** Markdown documentation files

---

### SymPy

- **Version:** ≥1.11.0, <2.0.0
- **License:** BSD-3-Clause
- **Purpose:** Symbolic mathematics for documentation equations
- **GitHub:** https://github.com/sympy/sympy
- **Citation:** ```bibtex @article{meurer2017sympy, title={SymPy: symbolic computing in Python}, author={Meurer, Aaron and Smith, Christopher P and Paprocki, Mateusz and others}, journal={PeerJ Computer Science}, volume={3}, pages={e103}, year={2017}, publisher={PeerJ Inc.}, doi={10.7717/peerj-cs.103} } ```
- **Used in:** Symbolic equation derivations in documentation

---

## Code Quality Tools ### Pygments

- **Version:** ≥2.14.0, <3.0.0
- **License:** BSD-2-Clause
- **Purpose:** Syntax highlighting for code blocks
- **Used in:** Documentation code formatting

---

### Black

- **Version:** ≥23.0.0, <25.0.0
- **License:** MIT
- **Purpose:** Python code formatter
- **GitHub:** https://github.com/psf/black
- **Used in:** Code style consistency

---

### linkchecker

- **Version:** ≥10.0.0, <11.0.0
- **License:** GPL-2.0
- **Purpose:** Broken link detection in documentation
- **Used in:** Documentation quality assurance

---

### psutil

- **Version:** ≥5.9.0, <6.0.0
- **License:** BSD-3-Clause
- **Purpose:** System monitoring and process utilities
- **GitHub:** https://github.com/giampaolo/psutil
- **Used in:** Memory monitoring, performance profiling

---

## License Summary ### Permissive Licenses (No restrictions for academic/commercial use) **MIT License (16 dependencies):**

- PySwarms, Optuna, PyYAML, Pydantic, pytest, JSONSchema, Plotly, Black
- sphinx-copybutton, sphinx-math-dollar, sphinx-design, sphinx-togglebutton, myst-parser
- sphinx-rtd-theme **BSD-3-Clause License (10 dependencies):**
- NumPy, SciPy, Pandas, PyModbus, H5PY, Altair, PyZMQ, psutil, SymPy **BSD-2-Clause License (4 dependencies):**
- Numba, pytest-benchmark, Sphinx, Pygments
- sphinxcontrib-bibtex, sphinxcontrib-mermaid, sphinxcontrib-plantuml **Apache 2.0 License (6 dependencies):**
- CVXPY, Streamlit, Watchdog, aiohttp, aio-pika **PSF-based License (1 dependency):**
- Matplotlib (BSD-compatible)

---

### Copyleft Licenses (Require attribution) **MPL 2.0 (1 dependency):**

- Hypothesis **GPL-2.0 (1 dependency):**
- linkchecker (development tool only, not distributed)

---

## Citation Instructions ### For Academic Papers/Thesis **Minimal Citation (Core Dependencies):** > This work uses NumPy (Harris et al., 2020), SciPy (Virtanen et al., 2020), and

> PySwarms (Miranda, 2018) for numerical computation and particle swarm optimization. **Complete Citation (Recommended):** > This implementation builds on the following open-source libraries: NumPy (Harris
> et al., 2020) for numerical computation, SciPy (Virtanen et al., 2020) for
> scientific algorithms, Matplotlib (Hunter, 2007) for visualization, PySwarms
> (Miranda, 2018) for particle swarm optimization, and Numba (Lam et al., 2015)
> for performance optimization. Testing uses pytest and Hypothesis (MacIver &
> Hatfield-Dodds, 2019) for property-based testing. **Full BibTeX** (for LaTeX documents):
- See `citations.bib` (to be created in Phase 5)
- All citations above are in BibTeX format

---

### For Software/Code Attribution **In README.md:**

```markdown
## Dependencies This project builds on open-source work:
- [NumPy](https://numpy.org/) - Array programming
- [PySwarms](https://github.com/ljvmiranda921/pyswarms) - PSO optimization
- [Numba](https://numba.pydata.org/) - JIT compilation See [DEPENDENCIES.md](DEPENDENCIES.md) for complete attribution.
``` **In Source Code Headers:**

```python
# example-metadata:
# runnable: false # Uses PySwarms for PSO optimization (Miranda 2018)
# Citation: https://doi.org/10.21105/joss.00433
from pyswarms.single import GlobalBestPSO
```

---

## Compliance Checklist ✅ **Open-Source Best Practices:**

- [ ] All dependencies documented
- [ ] Licenses identified and compatible
- [ ] Citations included where available
- [ ] GitHub repositories linked ✅ **Academic Integrity:**
- [ ] Scientific libraries properly cited
- [ ] BibTeX entries provided
- [ ] DOIs included where available ✅ **Legal Compliance:**
- [ ] No GPL dependencies in distributed code (linkchecker is dev-only)
- [ ] All licenses permit commercial use
- [ ] Attribution requirements met

---

**Document Version:** 1.0
**Last Updated:** 2025-10-03
**Maintained By:** Claude Code (Batch Citation System) For questions about dependencies, see individual library documentation links above.
