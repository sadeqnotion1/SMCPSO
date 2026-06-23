# Scripts Directory - Project Automation & Utilities

This directory contains automation scripts, utilities, and infrastructure tools for the DIP-SMC-PSO project, organized into categorized subdirectories for improved navigation.

---

## Directory Structure (Reorganized Dec 19, 2025)

### Entry Points (Root Level)

**Frequently-used scripts kept at root for convenience:**

- **run_tests.sh / run_tests.bat** - Cross-platform test runner (bash/Windows)
- **rebuild-docs.cmd** - Documentation rebuild utility
- **README.md** - This file

### Categorized Subdirectories

**docs/** - Documentation generation and validation (55 scripts)
- Build scripts: `build_docs.py`, `generate_code_docs.py`
- Validation: `validate_citations.py`, `validate_toctree_structure.py`, `check_docs.py`
- Quality assurance: `detect_ai_patterns.py`, `generate_audit_report.py`
- Fixers: `heading_fixer.py`, `code_block_fixer.py`, `emoji_replacer.py`
- Analysis: `analyze_sphinx_warnings_v2.py`, `map_broken_references.py`

**validation/** - Test validation and quality checks (6 scripts)
- Coverage validation: `check_coverage_gates.py`
- Memory validation: `validate_memory_optimization.py`, `validate_memory_pool.py`
- Tutorial validation: `validate_tutorial_01_experiments.py`, `validate_getting_started.py`
- Quality automation: `run_quality_checks.py`, `pytest_automation.py`

**testing/** - Testing infrastructure and test scripts (2 scripts)
- `test_baseline_chattering.py` - Baseline chattering tests
- `test_session_continuity.py` - Session continuity validation

**optimization/** - PSO optimization utilities (20 scripts)
- PSO tuning: `run_pso_parallel.py`, `update_config_with_gains.py`
- Monitoring: `monitor_pso.py`, `watch_pso.py`, `check_pso_completion.py`
- Chattering optimization: `optimize_chattering_*.py` (5 variants)
- Validation: `validate_optimized_gains.py`, `validate_and_summarize.py`
- Visualization: `visualize_optimization_results.py`, `analyze_pso_convergence.py`

**research/** - Research task scripts (75 scripts across subdirectories)
- `lt7_final_paper/` - LT-7 research paper automation (11 scripts)
- `mt6_boundary_layer/` - MT-6 boundary layer optimization (9 scripts)
- `mt7_robustness/` - MT-7 robustness analysis (4 scripts)
- `mt8_disturbances/` - MT-8 disturbance rejection (9 scripts)
- Phase experiments: `phase2_*.py`, `phase3_*.py`, `phase4_*.py` (14 scripts)
- Debug utilities: `debug_*.py`, `diagnose_*.py`, `investigate_*.py` (5 scripts)
- Monitoring: `monitor_pso_progress.py`

**analysis/** - Performance analysis and visualization (12 scripts)
- Performance: `compute_performance_metrics.py`, `analyze_controller_performance.py`
- Benchmarking: `parse_performance_benchmarks.py`, `generate_performance_matrix.py`
- Chattering: `demo_chattering_analysis.py`
- Accessibility: `accessibility_audit.py`, `performance_audit.py`
- Screenshots: `screenshot_docs.py`, `fix_screenshot_timeouts.py`
- FDI: `fdi_threshold_calibration.py`
- UI verification: `verify_back_to_top.py`

**monitoring/** - Real-time monitoring dashboards (2 scripts)
- `monitor_pso_streamlit.py` - Streamlit PSO monitoring dashboard
- `streamlit_monitoring_dashboard.py` - General monitoring dashboard

**infrastructure/** - System infrastructure and diagnostics (1 script)
- `diagnose_pytest_unicode.py` - Unicode encoding diagnostics for Windows pytest

**utils/** - Miscellaneous utilities
- (Currently empty - reserved for future standalone utilities)

**benchmarks/** - Benchmark runners (5 scripts)
- `batch_benchmark.py` - Batch benchmark execution
- `compare_optimizers.py` - Optimizer comparison utilities
- `run_all_comparisons.py` - Comprehensive comparison runner
- `run_baseline_simulations_l1p5.py` - Baseline simulations
- `validate_mt7_robust_pso.py` - MT-7 robustness validation

**coverage/** - Coverage analysis tools (5 scripts)
- `check_coverage.py`, `run_coverage.py` - Coverage execution
- `coverage_report.py` - Report generation
- `identify_gaps.py` - Coverage gap identification
- `quick_baseline.py` - Quick baseline coverage

**thesis/** - Thesis automation and validation (7 scripts + automation/)
- Verification: `verify_chapter.py`, `verify_equations.py`, `verify_citations.py`, `verify_figures.py`
- Validation: `validate_thesis_content.py`, `check_thesis.py`
- Checkpoints: `checkpoint_verification.py`
- `automation/` - Automated thesis validation (9 scripts)

**Other subdirectories:**
- `archive_management/` - Log compression and archiving (1 script)
- `cleanup/` - Workspace cleanup utilities (1 script)
- `mcp_validation/` - MCP quality analysis (1 script)
- `publication/` - Publication validation (1 script)
- `release/` - Version management (1 script)
- `tutorials/` - Tutorial scripts (2 scripts)
- `visualization/` - Visualization utilities (1 script)
- `migration/` - Migration utilities (4 scripts)

---

## Quick Start

### Running Tests
```bash
# Linux/Mac
bash scripts/run_tests.sh

# Windows
scripts\run_tests.bat
```

### Building Documentation
```bash
# Rebuild all documentation
scripts\rebuild-docs.cmd

# Or use the Python script directly
python scripts/docs/build_docs.py --all
```

### Running Validation
```bash
# Check coverage quality gates
python scripts/validation/check_coverage_gates.py

# Validate tutorial experiments
python scripts/validation/validate_tutorial_01_experiments.py
```

### PSO Optimization
```bash
# Monitor PSO progress
python scripts/optimization/monitor_pso.py

# Visualize optimization results
python scripts/optimization/visualize_optimization_results.py
```

---

## Quality Gates

**Coverage Quality Gates** (check_coverage_gates.py):

**Tier 1 - MINIMUM:**
- Overall coverage >= 85%

**Tier 2 - CRITICAL:**
- Core simulation engine >= 95%
- PSO optimizer >= 95%

**Tier 3 - SAFETY-CRITICAL:**
- Controllers >= 95%
- Plant models >= 95%

**Exit Codes:**
- `0` - All required gates passed
- `1` - One or more gates failed
- `2` - Coverage report not found

---

## Migration History

| Date | Change | Notes |
|------|--------|-------|
| 2025-12-19 | Scripts reorganization | Consolidated 21 root files → 5 root files; merged duplicate directories (documentation/ + docs_organization/ → docs/); created categorized subdirectories |
| 2025-11-11 | Coverage gates validator | Created coverage gates validator |
| 2025-11-11 | Unicode diagnostic tool | Added Unicode diagnostic tool |
| 2025-11-11 | Initial README | Initial README for scripts directory |

**See:** `scripts/migration/MIGRATION_HISTORY.md` for detailed reorganization changelog.

---

## Related Documentation

- **Testing Standards:** `.project/ai/guides/testing_standards.md`
- **Workspace Organization:** `.project/ai/guides/workspace_organization.md`
- **Coverage Configuration:** `.coveragerc`
- **Pytest Configuration:** `.pytest.ini`
- **Measurement Infrastructure:** `.artifacts/checkpoints/L1P1_MEASUREMENT/`
- **Claude.md Workspace Section:** `CLAUDE.md` Section 14

---

## Statistics

- **Total Python files:** 195 scripts
- **Root files:** 5 (3 entry points + README.md + future MIGRATION_HISTORY.md)
- **Subdirectories:** 21 categorized directories
- **Largest category:** docs/ (55 scripts, 28%)
- **Most active:** research/ (75 scripts across subdirectories, 38%)

**Reorganization Impact:**
- Before: 21 root files (cluttered)
- After: 5 root files (73% reduction, publication-ready)
