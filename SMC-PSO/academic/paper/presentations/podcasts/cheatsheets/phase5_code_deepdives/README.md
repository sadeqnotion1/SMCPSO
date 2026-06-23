# Phase 5: Code Deep-Dives - Controller Episodes

**Purpose**: Comprehensive code-learning episodes covering actual implementation details of all repository modules

**Status**: In Progress - Phase 5A (Controllers) Started

**Build Note (2026-02-04)**: `xelatex` fails with `hyperref` error `\IfFormatAtLeastT{2025-11-01}` on MiKTeX 24.1, so E030/E031 PDF compilation is currently blocked until MiKTeX/hyperref is updated or a template workaround is applied.

**Target Audience**: Developers who want to understand HOW the code works (not just WHAT it does)

---

## Phase 5A: Controller Code Deep-Dives (E030-E036)

### Completed Episodes

#### E030: Controller Base Classes & Factory (11 pages, 383 KB)
- **Duration**: 25-30 minutes
- **Topics**:
  - `ControllerInterface` abstract base class
  - Factory pattern with controller registry
  - Memory management (weakref pattern)
  - Design patterns (ABC, Factory, Strategy, Weak Reference)
- **Code Coverage**:
  - `src/controllers/base/controller_interface.py` (101 lines)
  - `src/controllers/factory/` (modular factory system)
  - Memory management patterns across all controllers
- **Key Concepts**:
  - Abstract methods enforce controller contract
  - Registry pattern enables O(1) controller lookup
  - Weakref prevents circular reference memory leaks
  - Configuration-driven controller selection

**Status**: [OK] Complete and compiled (2026-02-03)

### Planned Episodes

#### E031: Classical SMC Implementation (Planned)
- **Duration**: 25-30 minutes
- **Topics**:
  - `ClassicalSMC` line-by-line walkthrough (539 lines)
  - Sliding surface computation
  - Equivalent control with physics matrices
  - Robust switching control
  - Boundary layer for chattering reduction
- **Code Coverage**: `src/controllers/smc/classic_smc.py`

#### E032: Super-Twisting Algorithm (Planned)
- **Duration**: 25-30 minutes
- **Topics**:
  - `SuperTwistingSMC` 2nd-order algorithm (593 lines)
  - Numba JIT optimization
  - Finite-time convergence
  - Continuous control approximation
  - Anti-windup mechanisms
- **Code Coverage**: `src/controllers/smc/sta_smc.py`

#### E033: Adaptive Controllers (Planned)
- **Duration**: 30-35 minutes
- **Topics**:
  - `AdaptiveSMC` real-time gain adjustment
  - `HybridAdaptiveSTA` combined approach
  - Adaptation laws and Lyapunov tuning
  - Dead-zone wind-up prevention
- **Code Coverage**:
  - `src/controllers/smc/adaptive_smc.py`
  - `src/controllers/smc/hybrid_adaptive_sta_smc.py`

#### E034: Swing-Up Controller (Planned)
- **Duration**: 20-25 minutes
- **Topics**:
  - Energy-based control strategy
  - Mode switching (swing-up vs balance)
  - Phase detection logic
  - Integration with classical SMC
- **Code Coverage**: `src/controllers/specialized/swingup_smc.py`

#### E035: MPC Controller (Experimental) (Planned)
- **Duration**: 20-25 minutes
- **Topics**:
  - Model Predictive Control fundamentals
  - Prediction horizon and receding window
  - Constraint handling
  - Why "experimental" (computational cost)
- **Code Coverage**: `src/controllers/mpc/mpc_controller.py`

#### E036: Controller Integration & Testing (Planned)
- **Duration**: 20-25 minutes
- **Topics**:
  - Testing strategy across all controllers
  - Property-based tests (Hypothesis)
  - Lyapunov stability validation
  - Performance benchmarking framework
  - Memory leak detection
- **Code Coverage**: `tests/test_controllers/`

---

## Progress Summary

**Completed**: 1/7 episodes (14%)
**Total Pages**: 11 (target: ~24-28 pages)
**Total PDF Size**: 383 KB (target: ~2-3 MB)
**Time Invested**: ~2.5 hours (E030 authoring + compilation)
**Time Remaining**: ~12-15 hours (6 episodes × 2-2.5 hours each)

---

## Next Steps

1. **E031**: Author Classical SMC Implementation
2. **E032**: Author Super-Twisting Algorithm
3. **E033**: Author Adaptive Controllers
4. **E034**: Author Swing-Up Controller
5. **E035**: Author MPC Controller
6. **E036**: Author Controller Testing
7. **Batch Compile**: All 7 episodes together
8. **Quality Review**: Technical accuracy, beginner-friendliness
9. **Commit**: Phase 5A complete milestone

---

## Design Decisions

### LaTeX Template Reuse
- **Master Template**: `../templates/master_template.tex` (296 lines)
- **TikZ Components**: `../templates/tikz_components.tex` (reusable diagrams)
- **Consistency**: All episodes use same color palette, fonts, icons

### Code Example Philosophy
- **Show Real Code**: Actual lines from `src/`, not pseudocode
- **Annotate Heavily**: Comments explain WHY, not just WHAT
- **Runnable**: All examples can be copied and executed
- **Line References**: Include file paths and line numbers

### Visual Learning Support
- **TikZ Flowcharts**: 1-2 per episode (architecture, control flow)
- **Code Listings**: 3-5 per episode (Python, YAML)
- **Callout Boxes**: 5-8 per episode (tips, warnings, examples)
- **Multi-column Layouts**: Efficient space usage

---

## File Organization

```
phase5_code_deepdives/
├── E030_controller_base_factory.tex    (11 pages, 383 KB)  [OK]
├── E030_controller_base_factory.pdf    (compiled output)    [OK]
├── E031_classical_smc.tex              (pending)
├── E032_super_twisting_sta.tex         (pending)
├── E033_adaptive_controllers.tex       (pending)
├── E034_swingup_controller.tex         (pending)
├── E035_mpc_experimental.tex           (pending)
├── E036_controller_testing.tex         (pending)
└── README.md                           (this file)
```

---

## Compilation Commands

```bash
# Compile single episode
cd phase5_code_deepdives
pdflatex -interaction=nonstopmode E030_controller_base_factory.tex

# Compile all episodes (batch)
for f in E0*.tex; do pdflatex -interaction=nonstopmode "$f"; done

# Clean auxiliary files
del *.aux *.log *.out *.toc
```

---

## Quality Checklist (Per Episode)

- [ ] All code examples compile and run
- [ ] File paths and line numbers are accurate
- [ ] TikZ diagrams render correctly
- [ ] No technical inaccuracies
- [ ] Beginner-friendly language (jargon explained)
- [ ] Visual consistency with Phase 1-4 episodes
- [ ] Page count within 2-4 page target
- [ ] PDF size < 500 KB
- [ ] Cross-references to related episodes

---

**Last Updated**: 2026-02-03
**Author**: Claude Code (Anthropic)
**Repository**: https://github.com/theSadeQ/dip-smc-pso
