# Thesis Production Readiness Plan - 78% to 100%

**Target**: Achieve 100% submission-ready status
**Current Status**: 78/100 (NEAR SUBMISSION-READY)
**Timeline**: 29 hours over 3-4 weeks
**Completion Target**: January 24, 2025

---

## Executive Summary

This plan addresses all gaps identified in the production readiness analysis to elevate the thesis from 78% to 100% submission-ready status. The plan is divided into 6 phases spanning 29 hours of focused work, with clear deliverables, acceptance criteria, and quality gates.

**Key Improvements**:
- Generate 4 missing architecture/schematic figures (+15 points)
- Create 3 comprehensive parameter tables (+5 points)
- Expand bibliography with 15 recent citations (+2 points)
- Complete professional proofreading and quality verification (+5 points)
- External review and feedback incorporation (+5 points)

**Expected Final Score**: 100/100 (SUBMISSION-READY)

---

## Phase 1: Generate Missing Architecture Figures

**Duration**: 8 hours
**Priority**: CRITICAL
**Score Impact**: +15 points (70→85)

### Deliverables

#### 1.1 System Architecture Diagram (2 hours)
**Output**: `figures/architecture/system_overview.pdf`

**Content Requirements**:
- High-level block diagram showing:
  - Double-inverted pendulum plant (3 DOF, 1 input)
  - Four controller variants (Classical SMC, STA-SMC, Adaptive SMC, Hybrid)
  - PSO optimization layer
  - Simulation engine (Numba-accelerated)
  - Monitoring & visualization components
- Use professional academic style (IEEE/Elsevier template)
- Color-coded subsystems (plant=blue, controllers=green, optimization=red)

**Data Sources**:
- `src/` directory structure
- `README.md` architecture section
- `docs/architecture/` (if available)

**Tools**:
- Draw.io / diagrams.net (export to PDF)
- Or Python: matplotlib + networkx for programmatic generation
- Or LaTeX: TikZ for publication-quality diagrams

**Acceptance Criteria**:
- [X] PDF renders at 300 DPI minimum
- [X] All components labeled with proper terminology
- [X] Arrows show data flow direction
- [X] Legend explains color coding
- [X] File size <500 KB
- [X] Compiles in LaTeX without errors

---

#### 1.2 Control Loop Schematic (3 hours)
**Output**: `figures/schematics/control_loop.pdf`

**Content Requirements**:
- Detailed control flow showing:
  - State measurement (cart position x, angles θ₁, θ₂, velocities)
  - Sliding surface calculation: s = λ₁θ₁ + θ̇₁ + λ₂θ₂ + θ̇₂
  - Controller law (specific to each variant)
  - Saturation and boundary layer
  - Force application to cart
  - Dynamics integration (Runge-Kutta)
- Mathematical notation matching thesis preamble.tex
- Feedback loop clearly marked
- Sample time annotations (dt=0.001s)

**Data Sources**:
- `src/controllers/` implementation
- `source/report/section3_controllers.tex` equations
- `config.yaml` controller parameters

**Tools**:
- LaTeX TikZ (recommended for math notation integration)
- Or Inkscape with LaTeX plugin

**Acceptance Criteria**:
- [X] Matches equations in Section 3
- [X] Consistent mathematical notation
- [X] Clear feedback loop structure
- [X] Time domain annotations present
- [X] Compiles in LaTeX without errors

---

#### 1.3 Lyapunov Stability Diagram (2 hours)
**Output**: `figures/lyapunov/stability_regions.pdf`

**Content Requirements**:
- Phase portrait showing:
  - Sliding surface (s=0 line)
  - Trajectories converging to surface
  - Lyapunov function contours (V = ½s²)
  - Reaching phase (s≠0) and sliding phase (s=0)
  - Stability region boundaries
- Annotated with key properties (finite-time convergence)

**Data Sources**:
- `source/report/appendix_b_lyapunov.tex` (9.1 KB theory)
- Simulation data from `academic/paper/experiments/`
- Or generate synthetic trajectories via simulation

**Tools**:
- Python: matplotlib + numpy (generate from simulation)
- Script: `python scripts/generate_phase_portrait.py --controller classical_smc --output figures/lyapunov/`

**Acceptance Criteria**:
- [X] Sliding surface clearly visible
- [X] Multiple trajectories shown (≥5)
- [X] Convergence to s=0 demonstrated
- [X] Axes labeled (θ, θ̇)
- [X] Legend explains phases

---

#### 1.4 PSO Convergence 3D Surface (1 hour)
**Output**: `figures/convergence/pso_3d_surface.pdf`

**Content Requirements**:
- 3D surface plot of cost function landscape
- PSO particle trajectories overlaid
- Global best position marked
- Axes: two gain parameters (e.g., k1, k2) vs cost
- Demonstrates optimization convergence

**Data Sources**:
- Existing: `academic/paper/experiments/figures/LT7_section_5_1_pso_convergence.png`
- PSO logs: `academic/logs/pso/` (978 KB)
- Or re-run: `python simulate.py --ctrl classical_smc --run-pso --save gains.json`

**Tools**:
- Python: matplotlib 3D projection
- Script: `python scripts/visualize_pso_3d.py`

**Acceptance Criteria**:
- [X] Clear 3D visualization
- [X] Particle paths visible
- [X] Global optimum marked
- [X] Colormap shows cost gradient
- [X] Export to PDF (vector format)

---

### Phase 1 Quality Gate

**Checklist**:
- [ ] All 4 figures generated (architecture, schematic, lyapunov, pso_3d)
- [ ] PDFs compile in LaTeX main.tex
- [ ] Figures referenced in appropriate sections
- [ ] Captions written (2-3 sentences each)
- [ ] File sizes <500 KB each
- [ ] Visual quality: 300 DPI minimum
- [ ] Git commit: `docs(thesis): Add architecture and schematic figures`

**Estimated Score After Phase 1**: 85/100

---

## Phase 2: Create Missing Parameter Tables

**Duration**: 4 hours
**Priority**: HIGH
**Score Impact**: +5 points (85→90)

### Deliverables

#### 2.1 System Parameter Table (1.5 hours)
**Output**: `tables/parameters/system_params.tex`

**Content Requirements**:
```latex
\begin{table}[ht]
\centering
\caption{Double-Inverted Pendulum System Parameters}
\label{tab:system_params}
\begin{tabular}{llll}
\toprule
Parameter & Symbol & Value & Unit \\
\midrule
Cart mass & $m_0$ & 1.0 & kg \\
Link 1 mass & $m_1$ & 0.1 & kg \\
Link 2 mass & $m_2$ & 0.1 & kg \\
Link 1 length & $L_1$ & 0.5 & m \\
Link 2 length & $L_2$ & 0.5 & m \\
Gravity & $g$ & 9.81 & m/s² \\
Damping (cart) & $b_0$ & 0.1 & N·s/m \\
Damping (link 1) & $b_1$ & 0.01 & N·m·s/rad \\
Damping (link 2) & $b_2$ & 0.01 & N·m·s/rad \\
\bottomrule
\end{tabular}
\end{table}
```

**Data Sources**:
- `config.yaml` physics section
- `src/plant/models/` dynamics parameters
- Or default values from code

**Tools**:
- Manual LaTeX editing
- Or script: `python scripts/extract_params_to_latex.py config.yaml > tables/parameters/system_params.tex`

**Acceptance Criteria**:
- [X] All parameters from config.yaml included
- [X] Consistent units
- [X] Professional table formatting (booktabs package)
- [X] Compiles without errors
- [X] Referenced in Section 2 (System Model)

---

#### 2.2 Controller Gains Table (1.5 hours)
**Output**: `tables/parameters/controller_gains.tex`

**Content Requirements**:
- Table showing optimized gains for all 4 controllers
- Columns: Parameter, Classical SMC, STA-SMC, Adaptive SMC, Hybrid
- Rows: k1, k2, ..., boundary layer, max force
- Annotations: MT-8 robust optimization source

**Data Sources**:
- `config.yaml` lines 39-73 (controller_defaults section)
- MT-8 optimization results: `academic/paper/experiments/comparative/mt8_robust_pso/`

**Example Structure**:
```latex
\begin{table}[ht]
\centering
\caption{Optimized Controller Gains (MT-8 Robust PSO)}
\label{tab:controller_gains}
\begin{tabular}{lcccc}
\toprule
Parameter & Classical & STA & Adaptive & Hybrid \\
\midrule
$k_1$ & 23.07 & 2.02 & 2.14 & 10.15 \\
$k_2$ & 12.85 & 6.67 & 3.36 & 12.84 \\
... \\
Boundary layer & 0.3 & 0.3 & - & - \\
\bottomrule
\end{tabular}
\end{table}
```

**Acceptance Criteria**:
- [X] Gains match config.yaml exactly
- [X] All 4 controllers represented
- [X] Units/scaling documented
- [X] Referenced in Section 3 (Controllers)

---

#### 2.3 Performance Comparison Table (1 hour)
**Output**: `tables/comparisons/performance_summary.tex`

**Content Requirements**:
- Benchmark metrics for all controllers:
  - Settling time (seconds)
  - Overshoot (%)
  - Energy consumption (J)
  - Chattering amplitude (N)
  - Robustness score (%)
- Data from MT-5 comprehensive benchmark

**Data Sources**:
- Existing: `academic/paper/thesis/tables/benchmarks/` (5 .tex files)
- Benchmark data: `academic/paper/experiments/comparative/mt5_comprehensive_benchmark/`
- Reports: `academic/paper/experiments/reports/MT5_COMPLETE_REPORT.md`

**Tools**:
- Consolidate existing tables/benchmarks/*.tex
- Or regenerate: `python scripts/generate_summary_table.py`

**Acceptance Criteria**:
- [X] Metrics from MT-5 benchmark
- [X] Statistical significance markers (* p<0.05)
- [X] Best performer highlighted (bold)
- [X] Referenced in Section 5 (Results)

---

### Phase 2 Quality Gate

**Checklist**:
- [ ] All 3 tables created
- [ ] Tables compile in LaTeX
- [ ] Tables referenced in text
- [ ] Data matches source files (config.yaml, benchmarks)
- [ ] Professional formatting (booktabs)
- [ ] Git commit: `docs(thesis): Add parameter and comparison tables`

**Estimated Score After Phase 2**: 90/100

---

## Phase 3: Expand Bibliography

**Duration**: 3 hours
**Priority**: MEDIUM
**Score Impact**: +2 points (90→92)

### Deliverables

#### 3.1 Add 15 Recent Citations (2020-2025) (3 hours)

**Target Areas**:
1. **Modern SMC Applications** (5 citations)
   - Robotics: exoskeletons, humanoids
   - Aerospace: rocket landing, spacecraft
   - Recent surveys (2020+)

2. **PSO Advances** (3 citations)
   - Hybrid PSO algorithms (PSO-GA, PSO-DE)
   - Deep learning + PSO
   - Multi-objective PSO

3. **Underactuated Systems** (4 citations)
   - Recent DIP control papers
   - Acrobots, cart-pole variants
   - Energy-based swing-up

4. **Benchmark & Reproducibility** (3 citations)
   - Reproducible research practices
   - Control benchmarks (like OpenAI Gym)
   - Open-source control frameworks

**Data Sources**:
- Google Scholar: "sliding mode control" + "2020..2025"
- IEEE Xplore: "inverted pendulum" + recent
- Existing references: `academic/paper/thesis/references/` (96 MB, 23 PDFs)

**Tools**:
- Manual search and BibTeX export
- Or script: `python scripts/extract_bibtex.py --query "sliding mode control 2020" --output bibliography/main.bib`

**BibTeX Format**:
```bibtex
@article{Author2023,
  author = {Last, First and Second, Name},
  title = {Modern Sliding Mode Control for Robotics},
  journal = {IEEE Transactions on Control Systems Technology},
  year = {2023},
  volume = {31},
  number = {2},
  pages = {456--470},
  doi = {10.1109/TCST.2023.1234567}
}
```

**Acceptance Criteria**:
- [X] 15 new citations added to bibliography/main.bib
- [X] All citations from 2020-2025
- [X] Peer-reviewed journals/conferences
- [X] Citations integrated into text (at least 10 cited)
- [X] BibTeX compiles without warnings
- [X] PDFs downloaded to references/ (optional, not committed)

---

### Phase 3 Quality Gate

**Checklist**:
- [ ] Bibliography expanded to ~40-45 entries (from ~25-30)
- [ ] All new citations from 2020+
- [ ] Citations referenced in introduction/literature review
- [ ] `bibtex main` runs without errors
- [ ] Git commit: `docs(thesis): Expand bibliography with recent citations`

**Estimated Score After Phase 3**: 92/100

---

## Phase 4: Proofreading and Spell Check

**Duration**: 4 hours
**Priority**: HIGH
**Score Impact**: +3 points (92→95)

### Deliverables

#### 4.1 Automated Spell Check (1 hour)

**Tools**:
```bash
# Makefile target
cd academic/paper/thesis
make spell

# Manual aspell
aspell --mode=tex --lang=en check source/report/*.tex

# Or hunspell
hunspell -t -d en_US source/report/*.tex
```

**Acceptance Criteria**:
- [X] All .tex files checked
- [X] Technical terms added to dictionary (SMC, PSO, DIP, etc.)
- [X] Zero spelling errors remaining
- [X] Log saved: `academic/logs/thesis_spell_check.log`

---

#### 4.2 Grammar and Style Check (1.5 hours)

**Tools**:
- LanguageTool (open-source grammar checker)
- Or Grammarly (if available)
- Or manual read-through

**Focus Areas**:
- Passive voice reduction
- Sentence clarity (max 25 words)
- Consistent terminology (e.g., "sliding mode control" vs "SMC")
- Proper hyphenation (double-inverted pendulum, particle-swarm optimization)

**Acceptance Criteria**:
- [X] All sections reviewed
- [X] Grammar issues fixed
- [X] Consistent terminology throughout
- [X] Readability score ≥60 (Flesch-Kincaid)

---

#### 4.3 LaTeX Formatting Check (0.5 hours)

**Checks**:
- Consistent spacing (use `~` for non-breaking spaces)
- Proper math mode ($inline$ vs \[display\])
- Citation style (e.g., "Smith et al.~\cite{Smith2020}")
- Table/figure numbering consistency
- Cross-reference validation (all \ref{} resolve)

**Tools**:
```bash
# Check for broken references
pdflatex main.tex 2>&1 | grep -i "reference\|citation\|undefined"

# Count warnings
pdflatex main.tex 2>&1 | grep -c "Warning"
```

**Acceptance Criteria**:
- [X] Zero LaTeX warnings
- [X] All cross-references resolve
- [X] Consistent formatting style
- [X] PDF compiles on first pass (after bibtex)

---

#### 4.4 Content Consistency Check (1 hour)

**Verifications**:
- [ ] Figures match captions
- [ ] Tables match text descriptions
- [ ] Equations numbered consecutively
- [ ] Appendices referenced correctly
- [ ] Nomenclature matches usage
- [ ] Abstract matches contributions
- [ ] Conclusion matches introduction promises

**Tools**:
- Manual review checklist
- Or script: `python scripts/check_thesis_consistency.py`

**Acceptance Criteria**:
- [X] All figures/tables referenced in text
- [X] No orphaned equations
- [X] Introduction/conclusion alignment verified
- [X] Nomenclature complete

---

### Phase 4 Quality Gate

**Checklist**:
- [ ] Zero spelling errors
- [ ] Zero grammar issues (critical)
- [ ] Zero LaTeX warnings
- [ ] All cross-references valid
- [ ] Content consistency verified
- [ ] Git commit: `docs(thesis): Proofreading and formatting improvements`

**Estimated Score After Phase 4**: 95/100

---

## Phase 5: Final Quality Verification

**Duration**: 2 hours
**Priority**: CRITICAL
**Score Impact**: +3 points (95→98)

### Deliverables

#### 5.1 Compilation Test (0.5 hours)

**Full Clean Build**:
```bash
cd academic/paper/thesis
make cleanall
make
make view
```

**Acceptance Criteria**:
- [X] PDF compiles successfully
- [X] All figures render correctly
- [X] All tables display properly
- [X] Bibliography complete (no "?" citations)
- [X] Table of contents accurate
- [X] Page count: 38-45 pages (within target)
- [X] File size: 600-800 KB (reasonable)

---

#### 5.2 PDF Quality Check (0.5 hours)

**Visual Inspection**:
- [ ] Fonts embedded (check with pdffonts)
- [ ] Figures high-resolution (zoom to 200%)
- [ ] No broken images
- [ ] Hyperlinks functional (if enabled)
- [ ] Margins consistent (1 inch standard)
- [ ] Page breaks logical (no orphan headers)

**Tools**:
```bash
# Check fonts
pdffonts main.pdf

# Check metadata
pdfinfo main.pdf

# Check PDF/A compliance (optional)
veraPDF main.pdf
```

**Acceptance Criteria**:
- [X] All fonts embedded
- [X] Figures render at 300+ DPI
- [X] PDF opens in multiple viewers (Adobe, SumatraPDF, web)
- [X] File size optimized (<1 MB)

---

#### 5.3 Submission Checklist (1 hour)

**Final Verifications**:
- [ ] Title page correct (author, date, institution)
- [ ] Abstract: 150-250 words
- [ ] Keywords: 4-6 terms
- [ ] Page numbering: correct throughout
- [ ] Sections: properly numbered (1, 1.1, 1.1.1)
- [ ] References: alphabetically sorted (if required)
- [ ] Appendices: labeled correctly (A, B, C)
- [ ] Acknowledgments: present and appropriate
- [ ] Declaration: added (if required)

**Generate Submission Package**:
```bash
# Create submission archive
cd academic/paper/thesis
mkdir submission_package
cp main.pdf submission_package/Thesis_FINAL.pdf
cp -r source/ submission_package/
cp bibliography/main.bib submission_package/
tar -czf thesis_submission_$(date +%Y%m%d).tar.gz submission_package/
```

**Acceptance Criteria**:
- [X] All submission requirements met
- [X] Submission package created
- [X] Archive size <5 MB (without references/)
- [X] README included in package

---

### Phase 5 Quality Gate

**Checklist**:
- [ ] Clean compilation successful
- [ ] PDF quality verified
- [ ] Submission checklist complete
- [ ] Final PDF generated: Thesis_FINAL.pdf
- [ ] Git commit: `docs(thesis): Final quality verification and submission package`

**Estimated Score After Phase 5**: 98/100

---

## Phase 6: External Review and Feedback

**Duration**: 8 hours (distributed)
**Priority**: HIGH
**Score Impact**: +2 points (98→100)

### Deliverables

#### 6.1 Advisor Review (4 hours distributed)

**Process**:
1. Send PDF to advisor/supervisor
2. Request feedback on:
   - Technical accuracy
   - Clarity of explanations
   - Completeness of literature review
   - Quality of results presentation
   - Overall structure and flow
3. Schedule 30-minute review meeting
4. Document feedback in issues tracker

**Timeline**: 1 week turnaround

**Acceptance Criteria**:
- [X] PDF sent to advisor
- [X] Feedback received (within 1 week)
- [X] Review meeting completed
- [X] Feedback documented

---

#### 6.2 Peer Review (2 hours distributed)

**Process**:
1. Share with 2-3 colleagues/peers
2. Request focused review on:
   - Readability (non-expert perspective)
   - Figure/table clarity
   - Abstract completeness
   - Typos/formatting issues
3. Collect written feedback

**Timeline**: 3-5 days turnaround

**Acceptance Criteria**:
- [X] PDF sent to ≥2 peers
- [X] Feedback collected
- [X] Issues documented

---

#### 6.3 Feedback Incorporation (2 hours)

**Process**:
1. Triage feedback (critical vs nice-to-have)
2. Address critical issues:
   - Technical errors
   - Missing citations
   - Unclear explanations
   - Formatting problems
3. Document changes in CHANGELOG.md
4. Regenerate final PDF

**Acceptance Criteria**:
- [X] Critical feedback addressed (100%)
- [X] Nice-to-have feedback addressed (≥70%)
- [X] Changes documented
- [X] Final PDF regenerated

---

### Phase 6 Quality Gate

**Checklist**:
- [ ] Advisor approval received
- [ ] Peer feedback incorporated
- [ ] All critical issues resolved
- [ ] Final PDF version 1.0 generated
- [ ] Git commit: `docs(thesis): Incorporate external review feedback - v1.0 FINAL`

**Final Score After Phase 6**: 100/100 - SUBMISSION-READY

---

## Timeline and Milestones

| Phase | Duration | Completion Date | Score |
|-------|----------|-----------------|-------|
| **Phase 1**: Figures | 8h (1 week) | Jan 5, 2025 | 85/100 |
| **Phase 2**: Tables | 4h (3 days) | Jan 8, 2025 | 90/100 |
| **Phase 3**: Bibliography | 3h (2 days) | Jan 10, 2025 | 92/100 |
| **Phase 4**: Proofreading | 4h (3 days) | Jan 13, 2025 | 95/100 |
| **Phase 5**: Verification | 2h (1 day) | Jan 14, 2025 | 98/100 |
| **Phase 6**: External Review | 8h (1 week) | Jan 24, 2025 | 100/100 |
| **TOTAL** | **29 hours** | **4 weeks** | **100/100** |

**Critical Path**: Phase 1 (figures) → Phase 4 (proofreading) → Phase 6 (external review)

---

## Resource Requirements

### Software Tools
- [X] LaTeX distribution (TeX Live or MiKTeX)
- [X] Python 3.9+ (for scripts)
- [X] Matplotlib, NumPy (for figure generation)
- [X] Draw.io or Inkscape (for diagrams)
- [X] Spell checker (aspell or hunspell)
- [ ] Optional: Grammarly, LanguageTool

### Data Sources
- [X] config.yaml (system parameters)
- [X] academic/paper/experiments/ (benchmark data)
- [X] academic/logs/pso/ (PSO optimization logs)
- [X] src/ (code structure for architecture)
- [X] README.md, docs/ (system documentation)

### External Support
- [ ] Advisor/supervisor (Phase 6.1)
- [ ] 2-3 peer reviewers (Phase 6.2)
- [ ] Optional: Professional proofreader

---

## Risk Assessment and Mitigation

### High-Risk Items

**Risk 1**: Figure generation takes longer than estimated (8h → 12h)
- **Mitigation**: Start with simplest figures first; use existing tools/templates
- **Contingency**: Simplify diagrams; use screenshots from existing docs

**Risk 2**: External reviewers unavailable or slow response
- **Mitigation**: Send requests early (Phase 5 completion)
- **Contingency**: Use online communities (r/LaTeX, ResearchGate) for quick feedback

**Risk 3**: Major technical issues found during review
- **Mitigation**: Self-review thoroughly in Phase 4-5
- **Contingency**: Allocate extra 4 hours for rework

### Medium-Risk Items

**Risk 4**: Bibliography expansion difficult (paywalled papers)
- **Mitigation**: Use institutional access, ResearchGate, arXiv
- **Contingency**: Use preprints, conference papers, open-access journals

**Risk 5**: LaTeX compilation issues after changes
- **Mitigation**: Commit frequently; test after each phase
- **Contingency**: Use git revert to previous working state

---

## Success Metrics

### Phase-Level Metrics
- [ ] Phase 1: 4 figures generated, all compile
- [ ] Phase 2: 3 tables created, all referenced
- [ ] Phase 3: 15 citations added, 10+ cited
- [ ] Phase 4: 0 spelling errors, 0 LaTeX warnings
- [ ] Phase 5: Clean compilation, submission package ready
- [ ] Phase 6: Advisor approval, feedback incorporated

### Overall Metrics
- [ ] Production readiness score: 100/100
- [ ] PDF page count: 38-45 pages
- [ ] File size: <1 MB
- [ ] Compilation time: <30 seconds
- [ ] Figures: 14 total (10 existing + 4 new)
- [ ] Tables: 8 total (5 existing + 3 new)
- [ ] Bibliography: 40-45 entries (25-30 existing + 15 new)
- [ ] Zero critical issues
- [ ] Advisor approval obtained

---

## Next Actions

### Immediate (This Week)
1. **Start Phase 1** - Generate system architecture diagram
2. **Set up tools** - Install Draw.io, verify LaTeX compilation
3. **Extract data** - Run parameter extraction scripts
4. **Schedule reviews** - Contact advisor and peers early

### Week 2-3
4. **Complete Phases 1-5** - All technical work
5. **Generate submission package** - Archive ready
6. **Send for review** - Distribute to reviewers

### Week 4
7. **Incorporate feedback** - Address all critical issues
8. **Final verification** - One last clean build
9. **Declare 100% ready** - Submit or publish

---

## Appendix: Script Helpers

### A.1 Generate Architecture Diagram (Python + matplotlib)
```python
# scripts/generate_architecture_diagram.py
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(12, 8))
# ... (diagram generation code)
plt.savefig('figures/architecture/system_overview.pdf', bbox_inches='tight', dpi=300)
```

### A.2 Extract Parameters to LaTeX Table
```python
# scripts/extract_params_to_latex.py
import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)
# ... (table generation code)
with open('tables/parameters/system_params.tex', 'w') as f:
    f.write(latex_table)
```

### A.3 Spell Check Automation
```bash
# scripts/thesis_spell_check.sh
#!/bin/bash
cd academic/paper/thesis
for file in source/report/*.tex; do
    echo "Checking $file..."
    aspell --mode=tex --lang=en check "$file"
done
```

---

## Document Control

**Version**: 1.0
**Created**: December 29, 2025
**Author**: Claude Code (AI Assistant)
**Status**: Active
**Next Review**: Upon Phase 1 completion (January 5, 2025)

**Change Log**:
- v1.0 (Dec 29, 2025): Initial plan created, 6 phases defined
