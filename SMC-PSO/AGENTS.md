# AGENTS.md -- Project Conventions & Agent Instructions

> Universal instructions for any AI coding agent working in this repository.
> For Claude Code-specific features (MCP, recovery, orchestration), see `CLAUDE.md`.

---

## 1) Critical Platform Rules

**NO EMOJIS (MANDATORY):**
- NEVER use Unicode emojis in code, scripts, output, or documentation
- ALWAYS use ASCII text markers: `[OK]`, `[ERROR]`, `[WARNING]`, `[INFO]`, `[AI]`, `[DONE]`, `[FAIL]`, `[PAUSE]`
- Reason: Windows terminal (cp1252 encoding) cannot display Unicode properly, causing crashes
- Applies to: Python scripts, shell output, markdown docs, commit messages, all user-facing text

**WINDOWS PLATFORM (MANDATORY):**
- Platform: Windows (win32) -- Working directory: `D:\Projects\main`
- ALWAYS use `python` NOT `python3` (`python3` does not exist on Windows, causes exit code 49)
- ALWAYS use `python -m pytest` NOT `python3 -m pytest`
- Example: `python simulate.py --ctrl classical_smc --plot`

**PATH SAFETY (MANDATORY):**
- NEVER create directories with braces or spaces: `{dir}/`, `my folder/`
- NEVER use Windows device names: `nul`, `con`, `prn`, `aux`, `com1`..`com9`, `lpt1`..`lpt9`
- NEVER use Unicode characters in file/directory paths on Windows

---

## 2) Repository Information

- **Repository**: https://github.com/theSadeQ/dip-smc-pso.git
- **Branch**: `main`
- **Working directory**: `D:\Projects\main`
- Before any git operations, verify remote URL:
  ```bash
  git remote -v
  # Expected: origin  https://github.com/theSadeQ/dip-smc-pso.git
  ```

---

## 3) Auto-Commit Policy

**SUSPENDED**: GitHub access is currently unavailable. Do NOT push or commit automatically.
Instead, stage changes locally and stop. The user will commit and push manually when access
is restored.

**Current behavior (suspended mode):**
1. Make and verify all file changes
2. Stage with: `git add <changed files>`
3. STOP -- do not commit, do not push
4. Inform the user what is staged and provide the commit command to run manually

**To re-enable:** Replace this section with the original MANDATORY policy once GitHub
access is restored.

**Commit message format:**
```
<Action>: <Brief description>

- <Detailed change 1>
- <Detailed change 2>

[AI] Generated with AI assistance

Co-Authored-By: AI Agent <noreply@agent.ai>
```

**See:** `.ai_workspace/guides/repository_management.md` for complete details.

---

## 4) Project Overview

**Double-Inverted Pendulum Sliding Mode Control with PSO Optimization**

A Python framework for simulating, controlling, and analyzing a double-inverted pendulum (DIP) system. Provides:
- Multiple SMC controller variants (classical, super-twisting, adaptive, hybrid)
- PSO-based gain optimization
- CLI interface (`simulate.py`) and Streamlit web UI (`streamlit_app.py`)
- Rigorous testing infrastructure (pytest, benchmarks, property-based testing)
- Comprehensive documentation (Sphinx, tutorials, research papers)

**Current phase:** Maintenance/Publication
**Completed:** Phase 3 (UI 34/34), Phase 4 (Production 4.1+4.2), Phase 5 (Research 11/11 tasks)

---

## 5) Architecture

### 5.1 High-Level Modules

| Module | Path | Purpose | Status |
|--------|------|---------|--------|
| Controllers | `src/controllers/` | SMC variants (classical, STA, adaptive, hybrid), swing-up, MPC; factory pattern | Stable |
| Simulation | `src/simulation/` | Simulation runners, integrators, orchestrators, context, results | Stable |
| Optimization | `src/optimization/` | PSO, CMA-ES, DE, GA; objective functions, validation | Active |
| Plant | `src/plant/` | DIP dynamics (simplified, full nonlinear, low-rank); physics models | Stable |
| Utils | `src/utils/` | Validation, control primitives, monitoring, visualization, analysis, types | Stable |
| Interfaces | `src/interfaces/` | HIL plant server + controller client; test automation framework | Stable |
| Config | `src/config/` | Pydantic-validated configuration loading and schema | Stable |
| Analysis | `src/analysis/` | Statistical analysis, performance metrics, comparison tools | Stable |
| Benchmarks | `src/benchmarks/` | Benchmark analysis modules (moved from root `benchmarks/`) | Stable |
| Core (compat) | `src/core/` | Backward-compatibility shims for legacy imports | Deprecated shim |
| Optimizer (compat) | `src/optimizer/` | Backward-compatibility shim to `src/optimization/` | Deprecated shim |

### 5.2 Representative Layout

```
src/
  controllers/      # SMC variants, factory, base classes
  simulation/       # Engines, integrators, orchestrators, context
  optimization/     # Algorithms (PSO, CMA-ES), objectives, validation
  plant/            # DIP dynamics models (simplified, full, low-rank)
  utils/            # Validation, monitoring, visualization, types
  interfaces/       # HIL server/client, test automation framework
  config/           # Pydantic config loader and schema
  analysis/         # Statistical analysis and metrics
  benchmarks/       # Benchmark analysis modules
  core/             # Compat shim (use src/simulation/ for new code)
  optimizer/        # Compat shim (use src/optimization/ for new code)
```

### 5.3 Key Entry Points

- `simulate.py` -- CLI for simulation, PSO optimization, HIL
- `streamlit_app.py` -- Interactive web dashboard
- `src/controllers/factory.py` -- Controller instantiation via factory pattern
- `config.yaml` -- Central configuration file

---

## 6) Key Technologies

- **Python 3.9+**
- **NumPy** (<2.0.0, pinned for Numba compatibility), **SciPy**, **Matplotlib**
- **Numba** for vectorized/batch simulation (JIT compilation)
- **PySwarms** / **Optuna** for optimization (PSO primary)
- **Pydantic** for YAML configuration validation
- **pytest** + **pytest-benchmark** + **Hypothesis** for testing
- **Streamlit** + **Plotly** + **Altair** for web UI
- **Sphinx** for documentation builds

---

## 7) Usage & Essential Commands

### Simulations
```bash
python simulate.py --ctrl classical_smc --plot
python simulate.py --ctrl sta_smc --plot
python simulate.py --load tuned_gains.json --plot
python simulate.py --print-config
```

### PSO Optimization
```bash
python simulate.py --ctrl classical_smc --run-pso --save gains_classical.json
python simulate.py --ctrl adaptive_smc --run-pso --seed 42 --save gains_adaptive.json
python simulate.py --ctrl hybrid_adaptive_sta_smc --run-pso --save gains_hybrid.json
```

### Hardware-in-the-Loop (HIL)
```bash
python simulate.py --run-hil --plot
python simulate.py --config custom_config.yaml --run-hil
```

### Testing
```bash
python -m pytest tests/ -v
python -m pytest tests/test_controllers/test_classical_smc.py -v
python -m pytest tests/test_benchmarks/ --benchmark-only
python -m pytest tests/ --cov=src --cov-report=html
```

### Web Interface
```bash
streamlit run streamlit_app.py
```

---

## 8) Configuration System

- Central `config.yaml` with strict Pydantic validation
- Domains: physics parameters, controller settings/gains, PSO parameters, simulation settings, HIL config, fault detection
- Rule: **"configuration first"** -- define parameters in `config.yaml` before implementation changes
- Load config in code:
  ```python
  from src.config import load_config
  config = load_config("config.yaml", allow_unknown=False)
  ```

---

## 9) Development Guidelines

### 9.1 Code Style

- **Type hints** on all function signatures and return types
- **Docstrings**: clear, example-rich, following existing patterns
- **ASCII header format** for Python files (~90 chars width):
  ```python
  #======================================================================================\\\
  #============================ module_name.py ==========================================\\\
  #======================================================================================\\\
  ```
- **Error handling**: explicit error types; avoid broad `except Exception`
- **Comments**: informal, conversational tone explaining the "why" behind the code
- **No Unicode emojis** in any output (see Section 1)

### 9.2 Adding New Controllers

1. Implement controller class in `src/controllers/` (extend base class)
2. Register in `src/controllers/factory.py`
3. Add default gains/config to `config.yaml`
4. Add tests under `tests/test_controllers/`

### 9.3 Controller Factory Usage

```python
from src.controllers.factory import create_controller

controller = create_controller(
    'classical_smc',
    config=controller_config,
    gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
)
control_output = controller.compute_control(state, last_control, history)
```

### 9.4 PSO Optimization (programmatic)

```python
from src.optimizer.pso_optimizer import PSOTuner
# src/optimizer/ is a compat shim; canonical: src/optimization/algorithms/pso_optimizer.py
tuner = PSOTuner(controller_type='classical_smc', config=config)
best_gains = tuner.optimize(n_particles=30, n_iterations=50)
```

### 9.5 Latency Monitoring

```python
from src.utils.monitoring.realtime.latency import LatencyMonitor
monitor = LatencyMonitor(dt=0.01)
start = monitor.start()
# ... control loop body ...
missed = monitor.end(start)
```

### 9.4 Batch Simulation

```python
from src.core.vector_sim import run_batch_simulation
results = run_batch_simulation(controller, dynamics, initial_conditions, sim_params)
```

---

## 10) Testing & Coverage Standards

**Coverage thresholds (enforced):**
- Overall: >= 85%
- Critical components: >= 95%
- Safety-critical (switching functions, sliding surfaces, state validation): **100%**

**Rules:**
- Every production `.py` file should have a corresponding `test_*.py`
- Validate theoretical properties for critical algorithms
- Use `@pytest.mark.critical` for safety-critical tests
- Use `@pytest.mark.slow` for tests > 5 seconds
- Use `@pytest.mark.integration` for multi-component tests

**Running tests:**
```bash
python -m pytest tests/ -v                             # All tests
python -m pytest tests/ --cov=src --cov-report=html    # With coverage
python -m pytest tests/ -m "not slow" -v               # Skip slow tests
python -m pytest tests/ -m critical -v                  # Critical only
```

**Configuration:** `.pytest.ini` (markers, warnings, coverage), `.coveragerc` (source, thresholds, exclusions)

---

## 11) Documentation Quality Standards

**Tone rules:**
- Direct, not conversational (avoid "Let's explore...", "Welcome to...")
- Specific, not generic (no "comprehensive" without metrics backing it)
- Technical, not marketing (facts over enthusiasm)
- Target: < 5 AI-ish patterns per documentation file

**After ANY documentation changes, rebuild Sphinx:**
```bash
sphinx-build -M html docs docs/_build -W --keep-going
```

Then verify:
```bash
stat docs/_static/your-file.css docs/_build/html/_static/your-file.css
```

**See:** `.ai_workspace/guides/documentation_build_system.md` for complete workflow.

---

## 12) Workspace Organization & Directory Rules

### Root Directory

- Target: <= 19 visible items at repo root (currently 14)
- Core visible directories: `src/`, `tests/`, `academic/`, `scripts/`, `data/`
- Core root files: `README.md`, `CHANGELOG.md`, `CLAUDE.md`, `AGENTS.md`, `config.yaml`, `requirements.txt`, `simulate.py`, `streamlit_app.py`, `setup.py`

### Directory Placement Rules

| Directory | Contents | Rule |
|-----------|----------|------|
| `src/` | Production code only | Controllers, models, utils, frameworks |
| `scripts/` | Development tools | Executed, not imported by production code |
| `tests/` | Pytest test files | Files named `test_*.py` |
| `academic/` | Research outputs | Papers (`paper/`), logs (`logs/`), dev artifacts (`dev/`) |
| `.ai_workspace/` | AI operation configs | Tools, guides, planning, state tracking (hidden) |
| `.cache/` | Ephemeral caches | pytest, hypothesis, htmlcov, benchmarks |

### Deprecated Paths (DO NOT USE)

- `.project/` -- migrated to `.ai_workspace/`
- `.ai/` -- migrated to `.ai_workspace/` or `academic/archive/`
- `.artifacts/` -- migrated to `academic/`
- `.logs/` -- migrated to `academic/logs/`

### Canonical Config Root

```
.ai_workspace/
  config/       # Configuration files (claude/, codex/, mcp/)
  tools/        # Development and recovery scripts
  guides/       # Operation documentation
  planning/     # Project planning docs
  state/        # Project state tracking
  archive/      # Archived artifacts
```

### Cleanup Policy (MANDATORY)

- ALWAYS clean up folder after creating/editing multiple files
- NEVER leave intermediate versions, test files, or build artifacts at root level
- Target: <= 5 active files at any folder root (final deliverables only)
- Archive old versions before committing

**See:** `.ai_workspace/guides/workspace_organization.md` for complete details.

---

## 13) Architectural Standards & Invariants

**Status:** Established Dec 29, 2025 via comprehensive structural analysis

### Intentional Patterns -- DO NOT "FIX"

These patterns may look like issues but are CORRECT and serve specific purposes:

**Pattern 1: Compatibility Layer**
- `src/optimizer/` (5 files, shim) re-exports from `src/optimization/` (48 files, production)
- Purpose: backward compatibility for legacy imports
- Action: NEVER consolidate these

**Pattern 2: Re-export Chain**
- `simulation_context.py` exists in 3 locations:
  - `src/core/simulation_context.py` (13 lines, compat layer)
  - `src/simulation/context/simulation_context.py` (116 lines, secondary shim)
  - `src/simulation/core/simulation_context.py` (203 lines, CANONICAL SOURCE)
- Purpose: multiple import paths for flexibility
- Action: DO NOT consolidate

**Pattern 3: Model Variants**
- 8 dynamics files across `src/plant/models/` (simplified, full, low-rank) + base interface + compat re-export
- Purpose: different physics accuracy/computational cost tradeoffs
- Action: NEVER consolidate -- these are different implementations

**Pattern 4: Framework File**
- `src/interfaces/hil/test_automation.py` is PRODUCTION code, NOT a test file
- Despite the `test_` prefix, it is part of the HIL test automation framework
- Action: DO NOT move to `tests/`

### File Classification Checklist

When deciding where a file belongs:
1. Exported in `__init__.py`? --> Production code (`src/`)
2. Imported by production code? --> Production code (`src/`)
3. Framework/infrastructure code? --> Production code (`src/`)
4. Has pytest imports? --> Test file (`tests/`)
5. Development tool (executed, not imported)? --> Script (`scripts/`)

### Quality Gates (ENFORCE STRICTLY)

| Gate | Threshold | Enforcement |
|------|-----------|-------------|
| Critical issues | 0 | MANDATORY |
| High-priority issues | <= 3 | REQUIRED |
| Test pass rate | 100% | MANDATORY |
| Root visible items | <= 19 | REQUIRED |
| Malformed file/dir names | 0 | MANDATORY |

**See:** `.ai_workspace/guides/architectural_standards.md` for complete details.

---

## 14) Production Safety Status

**Production Readiness Score:** 23.9/100 (Phase 4.1+4.2 complete, quality gates 1/8 passing)

- **Research-ready:** [OK] -- single-threaded and multi-threaded operation validated
- **Thread safety:** 100% (11/11 tests passing)
- **NOT production-ready:** [ERROR] -- missing code-level safety hardening, deployment infrastructure, incident response, coverage measurement broken

**Safe for:** research, academic use, simulation experiments, PSO optimization
**Not safe for:** real hardware deployment, safety-critical real-time control

### Phase 5: Research Completion

**Status:** [OK] COMPLETE (11/11 tasks, 100%)
**Focus:** Validate, document, and benchmark 7 controllers
**Roadmap:** 72 hours over 8 weeks -- COMPLETED

**Completed tasks:**
- QW-1 through QW-5: theory docs, benchmarks, PSO visualization, chattering metrics, status updates
- MT-5, MT-6, MT-7, MT-8: comprehensive benchmarks, boundary layer optimization, robust PSO, disturbances
- LT-4, LT-6, LT-7: Lyapunov proofs, model uncertainty, research paper

**Final deliverable:** LT-7 research paper SUBMISSION-READY (v2.1) with 14 figures, automation scripts, comprehensive bibliography

**See:** `.ai_workspace/guides/phase4_status.md` | `.ai_workspace/planning/research/RESEARCH_COMPLETION_SUMMARY.md`


---

## 15) Success Criteria

A successful state of the repository means:
- Clean root (<= 19 visible entries), caches removed, backups archived
- Test coverage gates met (85% overall / 95% critical / 100% safety-critical)
- Single-threaded operation stable; no dependency conflicts; memory bounded
- Clear, validated configuration; reproducible experiments
- All tests passing with 0 critical issues

---

## 16) Visualization & Analysis Toolkit

### Visualization modules (`src/utils/visualization/`)

- `animation.py` -- `DIPAnimator`: real-time pendulum animation during/after simulation
- `static_plots.py` -- static performance plots (state trajectories, phase portraits, error plots)
- `movie_generator.py` -- generates MP4 movies from simulation runs
- `pso_plots.py` -- PSO convergence plots (fitness vs iteration, particle swarm 3D surface)
- `legacy_visualizer.py` -- legacy visualization interface (kept for backward compatibility)

### Statistical analysis (`src/analysis/`)

- Confidence intervals, bootstrap resampling, Welch's t-test, ANOVA, Monte Carlo sensitivity
- Performance metrics: ISE, IAE, ITAE, overshoot, settling time, chattering index
- Comparative analysis across controllers and PSO runs

### Real-time monitoring (`src/utils/monitoring/`)

- `realtime/latency.py` -- `LatencyMonitor`: tracks control loop latency vs deadline
- `realtime/stability.py` -- real-time stability diagnostics
- `realtime/memory_monitor.py` -- memory usage tracking
- `metrics/` -- deadline miss counters, weakly-hard constraint analysis
- `examples.py` -- runnable monitoring examples

---

## 17) Controller Memory Management

All controllers use `weakref` patterns to prevent circular references between controller state, plant, and simulation context.

**Rules:**
- All controller types expose an explicit `cleanup()` method -- call it when done with a controller instance
- Use periodic reset + monitoring in long-running production loops to prevent memory growth
- Never store strong references from controller back to parent simulation objects

**Validation:**
```bash
python -m pytest tests/test_integration/test_memory_management/ -v
```

**See:** `.ai_workspace/guides/controller_memory.md` for complete details.

---

## 18) UI/UX Maintenance Mode Policy

**Phase 3 status:** [OK] COMPLETE (34/34 issues, October 9-17, 2025)
- Merged to main, UI work now in MAINTENANCE MODE
- Achievement: WCAG 2.1 Level AA, 18 design tokens, 4 breakpoints validated
- Browser support: Chromium validated [OK] | Firefox/Safari deferred [PAUSE]

**Maintenance mode rules:**
- **DO**: Fix critical bugs, update docs for new features, maintain WCAG AA compliance
- **DON'T**: Proactive UI enhancements, Firefox/Safari validation, "nice-to-have" polish
- **Focus**: 80-90% of time on research (controllers, PSO, SMC theory)

**See:** `.ai_workspace/guides/phase3_status.md` | `.ai_workspace/planning/phase3/HANDOFF.md`

---

## 19) Documentation Navigation

**Scale:** 985 documentation files total (814 in docs-related dirs, 171 in `.ai_workspace/`)
- Navigation systems: 11 total
- Category indexes: 43 `index.md` files across all documentation domains
- Learning paths: 5 paths from complete beginner (125-150 hrs) to advanced researcher (12+ hrs)

**Key navigation entry points:**
- `README.md` -- project overview and quick start
- `.ai_workspace/guides/` -- operation guides for AI agents and developers
- `.ai_workspace/planning/CURRENT_STATUS.md` -- latest project state
- `.ai_workspace/planning/research/RESEARCH_COMPLETION_SUMMARY.md` -- Phase 5 research summary

**Note:** The `docs/` Sphinx build directory is not committed to the repo. Rebuild locally with:
```bash
sphinx-build -M html docs docs/_build -W --keep-going
```

---

## Appendix: Notes

- This file is authoritative for style, testing, architecture, and operational rules for all AI agents
- `CLAUDE.md` contains additional Claude Code-specific instructions (MCP servers, session recovery, multi-agent orchestration)
- All git operations target `https://github.com/theSadeQ/dip-smc-pso.git`
- Section 13 establishes architectural invariants -- NEVER violate these patterns
- `.ai/` -- migrated to `.ai_workspace/` or `academic/`

---

## 20. LaTeX Compilation & Section Numbering

### LaTeX to PDF Compilation

When compiling LaTeX documents to PDF from WSL using Windows MiKTeX:

**Required Setup:**
```bash
# Check MiKTeX installation
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" --version

# Create compilation script (run_compile.py)
cat > compile_pdf.py << 'ENDSCRIPT'
#!/usr/bin/env python3
import subprocess

def windows_to_wsl_path(windows_path):
    """Convert Windows path to WSL path."""
    result = subprocess.run(
        ['wslpath', '-u', windows_path],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return windows_path

# Configuration
windows_pdflatex = r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe"
windows_tex = r"D:\Projects\main\academic\learning\ep001_physical_system_description\EP001_unified.tex"

# Convert to WSL format
wsl_pdflatex = windows_to_wsl_path(windows_pdflatex)
wsl_tex = windows_to_wsl_path(windows_tex)

print(f"Compiling: {wsl_tex}")

# Compile (4 passes for references)
for i in range(4):
    subprocess.run(
        [wsl_pdflatex, "-interaction=nonstopmode", wsl_tex],
        capture_output=True
    )

print("✅ Compilation complete!")
ENDSCRIPT

chmod +x compile_pdf.py
python3 compile_pdf.py
```

**Alternative Windows batch file:**
```batch
@echo off
cd /d "%~dp0"
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex
echo [OK] PDF created!
```

### **CRITICAL: Avoid "0.0" Section Numbering Errors**

**Problem:** Subsections appear as "0.0", "0.1" instead of "1.1", "1.2"

**Root Cause:** Missing `\documentclass` with proper section counter setup, or `\setcounter{section}{0}` before `\begin{document}`

**Solution:**
```latex
% ✅ CORRECT - Ensure proper document structure
\documentclass[11pt,a4paper]{article}

% ✅ Place package loading BEFORE hyperref
\usepackage{amsmath,amssymb,amsthm}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{xcolor}

% ✅ hyperref LAST (after all other packages)
\usepackage[hypertexnames=false, colorlinks=true]{hyperref}

% ✅ Define section formatting AFTER hyperref
\titleformat{\section}{\normalfont\Large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\normalfont\bfseries}{\thesubsection}{1em}{}

% ✅ Ensure \maketitle is present
\title{Document Title}
\author{Author}
\date{\today}
\maketitle

% ✅ DO NOT add \setcounter{section}{-1} or similar before \begin{document}
% This resets counters and causes 0.0 numbering!

% ✅ TOC should come AFTER \maketitle
\tableofcontents
```

**Common Mistakes to Avoid:**

1. **Wrong order of packages:**
   ```latex
   % ❌ WRONG - hyperref before other packages
   \usepackage{hyperref}
   \usepackage{amsmath}  % This breaks hyperref
   ```

2. **Resetting counters before document:**
   ```latex
   % ❌ WRONG - causes 0.0 numbering
   \setcounter{section}{-1}  % or any negative value
   \setcounter{subsection}{-1}
   \begin{document}
   ```

3. **Missing \maketitle:**
   ```latex
   % ❌ WRONG - TOC shows no sections
   \title{Title}
   \begin{document}
   \tableofcontents  % Sections won't appear!
   ```

4. **Using incompatible hyperref options:**
   ```latex
   % ❌ WRONG - may cause compilation issues
   \usepackage[hyperindex=true, breaklinks=false]{hyperref}
   
   % ✅ CORRECT - use standard options
   \usepackage[hypertexnames=false, colorlinks=true]{hyperref}
   ```

**Verification Checklist:**
- [ ] `\documentclass` is first non-comment line
- [ ] `\maketitle` appears before `\tableofcontents`
- [ ] `\usepackage{hyperref}` is the LAST package loaded
- [ ] No `\setcounter{section}{negative_number}` before `\begin{document}`
- [ ] All sections use `\section{}`, `\subsection{}`, `\subsubsection{}` (not manual text)

**Compilation passes:**
Always run pdflatex **4 times** to ensure:
1. First pass: Extract section references
2. Second pass: Resolve TOC entries
3. Third pass: Cross-reference stability
4. Fourth pass: Finalize all links

```bash
pdflatex file.tex  # Run 4 times total
```

---

