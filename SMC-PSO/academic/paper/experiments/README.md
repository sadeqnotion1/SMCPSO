# Experiments - Controller-Based Organization

## Purpose

This directory contains all experimental data, benchmarks, and research results organized by controller type and cross-controller comparative studies.

## Structure

```
experiments/
├── comparative/              [Cross-controller comparative studies]
│   ├── comprehensive_benchmarks/  [MT-5: 7 controllers performance comparison]
│   ├── pso_robustness/       [MT-7: PSO robustness across seeds]
│   ├── disturbance_rejection/ [MT-8: Disturbance rejection tests]
│   ├── model_uncertainty/    [LT-6: Model uncertainty analysis]
│   └── baselines/            [Baseline performance data]
│
├── classical_smc/            [Classical SMC controller]
│   └── optimization/         [PSO gains and convergence]
│
├── sta_smc/                  [Super-Twisting Algorithm SMC]
│   ├── boundary_layer/       [MT-6: Boundary layer optimization]
│   └── optimization/         [PSO gains and convergence]
│
├── adaptive_smc/             [Adaptive SMC controller]
│   └── optimization/         [PSO gains, including 2024_10 archive]
│
├── hybrid_adaptive_sta/      [Hybrid Adaptive STA SMC]
│   ├── anomaly_analysis/     [Phases 2-4 anomaly investigations]
│   ├── investigations/       [Zero variance investigation]
│   └── optimization/         [PSO gains and convergence]
│
├── figures/                  [Publication-ready figures]
│   └── LT7_section_*.png     [9 figures for LT7 journal paper]
│
└── reports/                  [Research task summaries and analyses]
```

## Directory Details

### comparative/

Cross-controller comparative studies testing ALL 4 main controllers (Classical, STA, Adaptive, Hybrid).

**Research Tasks:**
- **MT-5**: Comprehensive benchmarks (7 controllers, 4 metrics)
- **MT-7**: PSO robustness testing (10 seeds, statistical analysis)
- **MT-8**: Disturbance rejection + HIL validation
- **LT-6**: Model uncertainty analysis

**Size:** ~4 MB | **Files:** ~50

### classical_smc/

Classical Sliding Mode Control experiments.

**Contents:**
- PSO-optimized gains (phase53)
- MT-8 reproduction results
- Test panel configurations

**Size:** ~50 KB | **Files:** ~3

### sta_smc/

Super-Twisting Algorithm SMC experiments.

**Contents:**
- **boundary_layer/**: MT-6 adaptive boundary layer optimization (21 files, 600 KB)
- **optimization/**: PSO gains, Lyapunov-optimized gains, convergence plots

**Size:** ~700 KB | **Files:** ~30

### adaptive_smc/

Adaptive SMC controller experiments.

**Contents:**
- PSO-optimized gains (phase2, phase53)
- Robust gains (2024_10 archive, robust_2025_12)
- Experimental fixed gains

**Size:** ~120 KB | **Files:** ~10

### hybrid_adaptive_sta/

Hybrid Adaptive STA SMC - the primary research controller.

**Contents:**
- **anomaly_analysis/**: Phases 2-4 experiments
  - Phase 2: Gain interference, mode confusion, feedback instability
  - Phase 3: Selective scheduling, lambda scheduling, statistical validation
  - Phase 4: S-based scheduler, final validation
- **investigations/**: Zero variance investigation
- **optimization/**: PSO gains across all phases

**Size:** ~11 MB | **Files:** ~70

### figures/

Publication-ready figures for LT7 journal paper.

**Contents:**
- 9 LT7 section figures (PSO convergence, compute time, transient response, chattering, energy, model uncertainty, disturbance rejection, PSO generalization)
- MT6/MT7 performance comparison plots

**Size:** ~250 KB | **Files:** ~16

**CRITICAL:** Do NOT move or rename files in this directory - LT7 paper references them.

### reports/

Research task completion summaries and analysis reports.

**Contents:**
- MT5_ANALYSIS_SUMMARY.md
- QW2_COMPREHENSIVE_REPORT.md
- LT4_COMPLETION_SUMMARY.md
- Statistical comparisons

**Size:** ~100 KB | **Files:** ~7

## File Counts

- **Total files:** 154
- **Total size:** 16 MB
- **Markdown files:** ~40
- **JSON files:** ~40
- **CSV files:** ~30
- **PNG files:** ~20
- **NPZ files:** ~5

## Migration History

**Dec 29, 2025 - Controller-Based Reorganization (v3.0)**
- Reorganized from mixed task-based structure to controller-based + comparative
- Original structure:
  - benchmarks/ → comparative/comprehensive_benchmarks/ + figures/ + reports/
  - MT6_boundary_layer/ → sta_smc/boundary_layer/
  - MT7_robust_pso/ → comparative/pso_robustness/
  - MT8_disturbance_rejection/ → comparative/disturbance_rejection/
  - LT6_model_uncertainty/ → comparative/model_uncertainty/
  - phases/ → hybrid_adaptive_sta/anomaly_analysis/
  - optimization/ → distributed across controller-specific directories
- Git history preserved for all tracked files

## Research Task Cross-Reference

| Task ID | Location | Description |
|---------|----------|-------------|
| MT-5 | comparative/comprehensive_benchmarks/ | 7-controller performance comparison |
| MT-6 | sta_smc/boundary_layer/ | Adaptive boundary layer optimization |
| MT-7 | comparative/pso_robustness/ | PSO robustness (10 seeds) |
| MT-8 | comparative/disturbance_rejection/ | Disturbance rejection + HIL |
| LT-6 | comparative/model_uncertainty/ | Model uncertainty analysis |
| QW-2 | comparative/comprehensive_benchmarks/processed/ | Performance ranking |
| LT-4 | reports/LT4_COMPLETION_SUMMARY.md | Lyapunov analysis completion |
| Phase 2-4 | hybrid_adaptive_sta/anomaly_analysis/ | Hybrid controller investigations |

## Usage Guidelines

### For Researchers

1. **Adding new experiments**: Place in appropriate controller directory
2. **Cross-controller studies**: Use comparative/ directory
3. **Figures for papers**: Add to figures/ with descriptive names
4. **Completion summaries**: Add to reports/ directory

### For Developers

1. **PSO optimization results**: Store in controller-specific optimization/ subdirectories
2. **Phase-based data**: Use optimization/phases/phaseXX/ structure
3. **Archive old gains**: Use optimization/archive/ with date prefixes

### For Students

1. **Finding benchmark data**: Check comparative/comprehensive_benchmarks/
2. **Controller-specific results**: Navigate to controller directory (classical_smc/, sta_smc/, etc.)
3. **Research task data**: Use cross-reference table above

## Related Directories

- **D:\Projects\main\benchmarks/** - Project-level benchmarks (separate from experimental results)
- **academic/paper/publications/LT7_journal_paper/** - Journal paper using figures/ data
- **academic/paper/thesis/** - Thesis incorporating experimental results
- **academic/logs/benchmarks/** - Execution logs for benchmark runs

## Notes

- **Optimization files**: Many optimization results are gitignored (not tracked)
- **LT7 figures**: Critical for paper compilation - preserved exact paths
- **Git history**: All tracked files preserve full commit history via git mv
- **Backup**: Pre-reorganization backup available at project root (academic_experiments_pre_reorg_backup_*.tar.gz)

## Status

**Last Updated:** December 29, 2025
**Reorganization:** v3.0 - Controller-based + comparative structure
**Migration:** Complete (154 files, 16 MB)
**Verification:** Passed (file count, size, git history)

## See Also

- `academic/paper/README.md` - Overall paper/ directory structure
- `CLAUDE.md` Section 14 - Workspace organization guidelines
- `comparative/comprehensive_benchmarks/README.md` - MT-5 benchmark details
- `reports/MT5_ANALYSIS_SUMMARY.md` - Comprehensive benchmark analysis
