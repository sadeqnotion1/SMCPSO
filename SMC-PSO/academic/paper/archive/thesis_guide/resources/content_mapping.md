# Content Mapping: Existing Docs → Thesis Chapters

This file shows EXACTLY which existing documentation maps to which thesis chapters.

**Purpose**: Know which files to read/extract for each chapter.

---

## QUICK LOOKUP TABLE

| Thesis Chapter | Primary Source | Lines | Extraction % | Manual % |
|----------------|----------------|-------|--------------|----------|
| Front: Abstract | `00_introduction.md` + LT-7 paper | ~50 | 50% | 50% |
| Front: Nomenclature | `smc_theory_complete.md` | symbols | 80% | 20% |
| Ch 1: Introduction | `00_introduction.md` | 35 | 40% | 60% |
| Ch 2: Literature | `02_literature_review.md` | 253 | 50% | 50% |
| Ch 3: Problem | `01_problem_statement.md` | 57 | 50% | 50% |
| Ch 4: Modeling | `03_system_modeling.md` | 32 | 60% | 40% |
| Ch 5: SMC Theory | `04_sliding_mode_control.md` | 468 | 75% | 25% |
| Ch 6: Chattering | `05_chattering_mitigation.md` | 205 | 70% | 30% |
| Ch 7: PSO | `06_pso_optimization.md` | 62 | 60% | 40% |
| Ch 8: Implementation | `07_simulation_setup.md` | 17 | 65% | 35% |
| Ch 9: Experiments | Workflow docs | - | 50% | 50% |
| Ch 10: Results Comp | `08_results.md` | 119 | 70% | 30% |
| Ch 11: Robustness | LT-6, MT-8 reports | - | 65% | 35% |
| Ch 12: PSO Results | QW-3, MT-7 reports | - | 60% | 40% |
| Ch 13: Stability | `appendix_a_proofs.md` | 453 | 80% | 20% |
| Ch 14: Discussion | LT-7 paper | - | 40% | 60% |
| Ch 15: Conclusion | `09_conclusion.md` | 243 | 70% | 30% |
| App A: Proofs | `appendix_a_proofs.md` | 453 | 90% | 10% |
| App B: Code | `src/controllers/*.py` | code | 95% | 5% |
| App C: Data | `benchmarks/*.csv` | tables | 90% | 10% |
| App D: Config | `config.yaml` | config | 95% | 5% |
| Bibliography | `CITATIONS_ACADEMIC.md` | 39 refs | 70% | 30% |

---

## DETAILED MAPPING

### CHAPTER 1: INTRODUCTION (12-15 pages)

**Primary Source**:
- `docs/thesis/chapters/00_introduction.md` (35 lines)
  - Lines 1-16: Motivation
  - Lines 17-25: Problem overview
  - Lines 26-35: Thesis structure

**Secondary Sources**:
- `.project/ai/planning/research/RESEARCH_COMPLETION_SUMMARY.md`
  - Research objectives
  - 11 completed tasks (QW-1 to LT-7)
- `.project/ai/planning/CURRENT_STATUS.md`
  - Phase 5 status
  - Key achievements
- `.artifacts/LT7_research_paper_v2.1/` (if exists)
  - Contributions section
  - Key results summary

**What to Extract**:
- Section 1.1 (Motivation): Extract paragraphs 1-3 from lines 1-16
- Section 1.2 (Overview): Expand lines 17-25
- Section 1.3 (Objectives): List from CURRENT_STATUS.md
- Section 1.4 (Contributions): From RESEARCH_COMPLETION_SUMMARY.md
- Section 1.5 (Organization): Create chapter roadmap

**Extraction Method**:
```bash
python automation_scripts/md_to_tex.py \
  docs/thesis/chapters/00_introduction.md \
  thesis/chapters/chapter01_introduction_temp.tex
```
Then manually expand from 35 lines → 12-15 pages.

---

### CHAPTER 2: LITERATURE REVIEW (18-20 pages)

**Primary Source**:
- `docs/thesis/chapters/02_literature_review.md` (253 lines)
  - Already well-structured
  - Has sections on SMC, PSO, DIP control

**Secondary Sources**:
- `docs/CITATIONS_ACADEMIC.md` (39 references)
  - Books: 22 references
  - Papers: 17 references
- `docs/guides/theory/smc-theory.md`
  - SMC background
- `docs/guides/theory/pso-theory.md`
  - PSO background

**What to Extract**:
- Section 2.1 (Inverted Pendulum): Expand existing section
- Section 2.2 (SMC Theory): Extract + add 10 citations
- Section 2.3 (PSO): Extract + add convergence theory
- Section 2.4 (Related Work): Survey 15+ papers from CITATIONS_ACADEMIC.md
- Section 2.5 (Gaps): Connect to thesis contributions

**Extraction Method**:
```bash
python automation_scripts/md_to_tex.py \
  docs/thesis/chapters/02_literature_review.md \
  thesis/chapters/chapter02_literature.tex
```
253 lines → ~10 pages automatically, then expand to 18-20 pages manually.

---

### CHAPTER 3: PROBLEM FORMULATION (10-12 pages)

**Primary Source**:
- `docs/thesis/chapters/01_problem_statement.md` (57 lines)

**Secondary Sources**:
- `docs/guides/theory/dip-dynamics.md`
  - System description
  - Physical parameters
- `config.yaml`
  - Exact parameter values (m₀, m₁, m₂, L₁, L₂, etc.)

**What to Extract**:
- Section 3.1 (DIP System): Description + schematic
- Section 3.2 (Control Objectives): Extract from lines 1-20
- Section 3.3 (Constraints): Extract from lines 21-40
- Section 3.4 (Metrics): Extract from lines 41-57
- Section 3.5 (Problem Statement): Formal mathematical formulation

**Extraction Method**:
```bash
python automation_scripts/md_to_tex.py \
  docs/thesis/chapters/01_problem_statement.md \
  thesis/chapters/chapter03_problem.tex

# Extract parameters
grep -A 20 "physics:" config.yaml > params.txt
```

---

### CHAPTER 4: MATHEMATICAL MODELING (15-18 pages)

**Primary Source**:
- `docs/thesis/chapters/03_system_modeling.md` (32 lines)
  - Brief, needs heavy expansion

**Secondary Sources**:
- `src/core/dynamics.py`
  - Simplified model implementation (lines 50-150)
  - State-space representation
- `src/core/dynamics_full.py`
  - Full nonlinear model (lines 80-250)
  - Lagrangian derivation
- `docs/guides/theory/dip-dynamics.md`
  - Mathematical derivations
- `config.yaml`
  - Physical parameters

**What to Extract**:
- Section 4.1 (Lagrangian): From dynamics_full.py docstrings
- Section 4.2 (State-Space): From dynamics.py
- Section 4.3 (Simplified Model): From dynamics.py implementation
- Section 4.4 (Full Model): From dynamics_full.py implementation
- Section 4.5 (Parameters): Table from config.yaml

**Extraction Method**:
```bash
# Convert markdown
python automation_scripts/md_to_tex.py \
  docs/thesis/chapters/03_system_modeling.md \
  thesis/chapters/chapter04_modeling_temp.tex

# Extract code docstrings
grep -A 30 "class SimplifiedDynamics" src/core/dynamics.py
```

---

### CHAPTER 5: SLIDING MODE CONTROL THEORY (20-25 pages)

**Primary Source**:
- `docs/thesis/chapters/04_sliding_mode_control.md` (468 lines)
  - EXCELLENT source! ~70% of chapter already written

**Secondary Sources**:
- `docs/theory/smc_theory_complete.md` (~1,200 lines)
  - Comprehensive SMC theory
  - All 7 controllers documented
- `src/controllers/smc/*.py`
  - Implementation details

**What to Extract**:
- Section 5.1 (Fundamentals): Lines 1-100 of 04_sliding_mode_control.md
- Section 5.2 (Classical SMC): Lines 101-200
- Section 5.3 (Super-Twisting): Lines 201-300
- Section 5.4 (Adaptive SMC): Lines 301-400
- Section 5.5 (Hybrid): Lines 401-468
- Section 5.6 (Stability): From smc_theory_complete.md

**Extraction Method**:
```bash
python automation_scripts/md_to_tex.py \
  docs/thesis/chapters/04_sliding_mode_control.md \
  thesis/chapters/chapter05_smc_theory.tex
```
**Result**: 468 lines → ~16-18 pages automatically! Only needs 2-4 pages of manual addition.

---

### CHAPTER 6: CHATTERING MITIGATION (12-15 pages)

**Primary Source**:
- `docs/thesis/chapters/05_chattering_mitigation.md` (205 lines)

**Secondary Sources**:
- `.artifacts/mt6_validation/` (MT-6 boundary layer optimization)
  - Adaptive boundary layer results
- `src/utils/analysis/chattering.py`
  - Chattering metrics implementation
  - FFT analysis code

**What to Extract**:
- Section 6.1 (Problem): Lines 1-50
- Section 6.2 (Boundary Layer): Lines 51-100
- Section 6.3 (Super-Twisting): Lines 101-150
- Section 6.4 (Adaptive Boundary): MT-6 validation results
- Section 6.5 (Metrics): From chattering.py

**Extraction Method**:
```bash
python automation_scripts/md_to_tex.py \
  docs/thesis/chapters/05_chattering_mitigation.md \
  thesis/chapters/chapter06_chattering.tex
```

---

### CHAPTER 7: PSO OPTIMIZATION (15-18 pages)

**Primary Source**:
- `docs/thesis/chapters/06_pso_optimization.md` (62 lines)
  - Brief, needs expansion

**Secondary Sources**:
- `docs/theory/pso_optimization_complete.md`
  - PSO theory
  - Convergence analysis
- `docs/pso_convergence_theory.md`
  - Mathematical proofs
- `src/optimizer/pso_optimizer.py`
  - Implementation details

**What to Extract**:
- Section 7.1 (Fundamentals): From pso_optimization_complete.md
- Section 7.2 (Convergence): From pso_convergence_theory.md
- Section 7.3 (Cost Function): From pso_optimizer.py docstrings
- Section 7.4 (Robust Optimization): MT-7 research task
- Section 7.5 (Hyperparameters): From config.yaml

---

### CHAPTER 8: IMPLEMENTATION (12-15 pages)

**Primary Source**:
- `docs/thesis/chapters/07_simulation_setup.md` (17 lines)
  - Very brief, mostly manual writing

**Secondary Sources**:
- `docs/architecture.md`
  - Software architecture
  - Module organization
- `docs/CONTROLLER_FACTORY.md`
  - Factory pattern details
- `src/controllers/` (directory structure)
  - 7 controller implementations

**What to Extract**:
- Section 8.1 (Architecture): From architecture.md
- Section 8.2-8.6 (Controller Implementations): From controller code
- Code snippets: Key algorithms from .py files

---

### CHAPTERS 10-12: RESULTS (50 pages total)

**Primary Source**:
- `docs/thesis/chapters/08_results.md` (119 lines)

**Secondary Sources**:
- `benchmarks/baseline_performance.csv` (QW-2)
- `benchmarks/comprehensive_benchmark.csv` (MT-5)
- `benchmarks/LT6_uncertainty_analysis.csv` (LT-6)
- `benchmarks/LT6_robustness_ranking.csv` (LT-6)
- `benchmarks/MT7_robustness_summary.json` (MT-7)
- `benchmarks/MT8_disturbance_results.csv` (MT-8)
- `.artifacts/mt6_validation/` (MT-6)
- `.artifacts/QW3_pso_visualization/` (QW-3)

**What to Extract**:
- **Chapter 10 (Controller Comparison)**:
  - baseline_performance.csv → Table 10.1
  - comprehensive_benchmark.csv → Figures 10.1-10.5
  - Narrative from 08_results.md lines 1-60
- **Chapter 11 (Robustness)**:
  - LT6_*.csv → Tables 11.1-11.3
  - MT8_disturbance_results.csv → Figures 11.1-11.6
  - MT6 validation → Section 11.4
- **Chapter 12 (PSO Results)**:
  - QW3 PSO plots → Figures 12.1-12.4
  - MT7 robust PSO → Tables 12.1-12.2

**Extraction Method**:
```bash
# Generate LaTeX tables from CSV
python automation_scripts/csv_to_table.py \
  benchmarks/baseline_performance.csv \
  thesis/tables/benchmarks/baseline.tex \
  "Baseline Performance Comparison" \
  "tab:baseline"

# Generate figures from data
python automation_scripts/generate_figures.py
```

---

### CHAPTER 13: LYAPUNOV STABILITY (18-22 pages)

**Primary Source**:
- `docs/thesis/chapters/appendix_a_proofs.md` (453 lines)
  - EXCELLENT source! ~80% of chapter exists

**Secondary Sources**:
- `docs/theory/lyapunov_proofs_existing.md` (~1,000 lines)
  - Complete Lyapunov analysis
  - All 7 controller proofs
- `.artifacts/LT4_INTEGRATION_SUMMARY.txt` (LT-4 research task)
  - Proof validation

**What to Extract**:
- Section 13.1-13.4 (Controller Proofs): From appendix_a_proofs.md
- Section 13.5 (Validation): From LT4_INTEGRATION_SUMMARY.txt

**Extraction Method**:
```bash
python automation_scripts/md_to_tex.py \
  docs/thesis/chapters/appendix_a_proofs.md \
  thesis/chapters/chapter13_stability.tex
```
**Result**: 453 lines → ~15-18 pages! Only 3-5 pages manual writing needed.

---

### CHAPTER 15: CONCLUSION (8-10 pages)

**Primary Source**:
- `docs/thesis/chapters/09_conclusion.md` (243 lines)
  - COMPREHENSIVE! ~70% complete

**Secondary Sources**:
- LT-7 research paper conclusion
- RESEARCH_COMPLETION_SUMMARY.md

**What to Extract**:
- Section 15.1 (Contributions): Lines 1-80
- Section 15.2 (Findings): Lines 81-160
- Section 15.3 (Impact): Lines 161-243

**Extraction Method**:
```bash
python automation_scripts/md_to_tex.py \
  docs/thesis/chapters/09_conclusion.md \
  thesis/chapters/chapter15_conclusion.tex
```
**Result**: 243 lines → ~7-8 pages! Only 1-2 pages expansion needed.

---

## APPENDICES

### APPENDIX A: PROOFS (10 pages)

**Source**: `docs/thesis/chapters/appendix_a_proofs.md` (453 lines)
- 90% extraction rate
- Already in thesis format

### APPENDIX B: CODE LISTINGS (15 pages)

**Source**: `src/controllers/smc/*.py`
- Extract key algorithms:
  - `classical_smc.py`: compute_control() method
  - `sta_smc.py`: super_twisting_algorithm()
  - `adaptive_smc.py`: adapt_gains()
  - `hybrid_adaptive_sta_smc.py`: hybrid_control()
  - `swing_up.py`: energy_based_control()

**Extraction Method**:
```bash
# Extract specific functions
grep -A 50 "def compute_control" src/controllers/smc/classical_smc.py
```

### APPENDIX C: BENCHMARK DATA (10 pages)

**Source**: `benchmarks/*.csv`
- All CSV files → LaTeX tables
- 90% automated via csv_to_table.py

### APPENDIX D: CONFIGURATION (5 pages)

**Source**: `config.yaml`
- Extract sections: physics, controllers, PSO, simulation
- Format as code listing

---

## BIBLIOGRAPHY (100+ references)

**Source**: `docs/CITATIONS_ACADEMIC.md` (39 references)
- Books: 22
- Papers: 17

**Additional Sources**:
- Software dependencies (NumPy, SciPy, PySwarms, etc.) - add 30+ references
- Additional papers for literature review - add 20+ references
- Project-specific reports (LT-4, LT-6, LT-7, etc.) - add 15+ references

**Extraction Method**:
```bash
python automation_scripts/extract_bibtex.py \
  docs/CITATIONS_ACADEMIC.md \
  thesis/bibliography/papers.bib
```

---

## SUMMARY

**Total Extraction**:
- **2,101 lines** from existing thesis chapters
- **8,255 lines** from theory documentation
- **20 CSV files** for tables/figures
- **39 citations** for bibliography
- **7 controller implementations** for code listings

**Result**: ~60-65% of 200-page thesis can be extracted/automated!

**Manual Writing Required**: ~35-40% (~56 hours out of 160 total)

---

**[OK] Use this mapping to know exactly which files to read for each chapter!**
