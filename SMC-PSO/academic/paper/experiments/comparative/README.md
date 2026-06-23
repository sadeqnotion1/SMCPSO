# Comparative Studies - Cross-Controller Experiments

## Purpose

This directory contains experimental studies that test ALL controllers comparatively. These experiments evaluate multiple controllers under identical conditions to enable fair performance comparisons.

## Contents

```
comparative/
├── comprehensive_benchmarks/  [MT-5]
│   ├── raw/                   [Original benchmark outputs]
│   ├── processed/             [Aggregated analysis]
│   └── README.md
├── pso_robustness/            [MT-7]
├── disturbance_rejection/     [MT-8]
├── model_uncertainty/         [LT-6]
└── baselines/                 [Reference performance data]
```

## Research Tasks

### MT-5: Comprehensive Benchmarks

**Location:** `comprehensive_benchmarks/`
**Controllers Tested:** 7 (Classical SMC, STA SMC, Adaptive SMC, Hybrid Adaptive STA, Boundary Layer, Swing-Up, MPC)
**Metrics:** 4 (RMSE, Settling Time, Chattering, Control Effort)
**Status:** Complete (October 25, 2025)

**Key Files:**
- `raw/comprehensive_benchmark.csv` - Tabular results
- `raw/comprehensive_benchmark.json` - Time series data
- `processed/qw2_performance_ranking.csv` - Ranked performance
- `processed/hybrid_anomaly_trend_analysis.json` - Anomaly detection

**Related:**
- Figures: `../figures/LT7_section_7_*`
- Reports: `../reports/MT5_ANALYSIS_SUMMARY.md`, `../reports/QW2_COMPREHENSIVE_REPORT.md`

### MT-7: PSO Robustness

**Location:** `pso_robustness/`
**Controllers Tested:** 4 main controllers
**Seeds:** 10 (seeds 42-51)
**Status:** Complete (November 2025)

**Key Files:**
- `MT7_seed_42_results.csv` through `MT7_seed_51_results.csv` - Individual seed results
- `MT7_robustness_summary.json` - Statistical summary
- `MT7_statistical_comparison.json` - Cross-seed analysis

**Related:**
- Figures: `../figures/MT7_robustness_*` (4 plots)
- Reports: `MT7_COMPLETE_REPORT.md`

### MT-8: Disturbance Rejection

**Location:** `disturbance_rejection/`
**Controllers Tested:** 4 main controllers + Hybrid deep dive
**Tests:** Simulation + HIL validation
**Status:** Complete (November 2025)

**Key Files:**
- `MT8_disturbance_rejection.csv` - Simulation results
- `MT8_hil_validation_results.json` - Hardware-in-the-loop data
- `MT8_adaptive_scheduling_results.json` - Adaptive scheduler performance
- `MT8_robust_validation_summary.json` - Summary statistics

**Related:**
- Figures: `../figures/LT7_section_8_2_disturbance_rejection.png`
- Reports: `MT8_COMPLETE_REPORT.md`, `MT8_HIL_VALIDATION_SUMMARY.md`

### LT-6: Model Uncertainty

**Location:** `model_uncertainty/`
**Controllers Tested:** 4 main controllers
**Perturbations:** Mass, length, damping variations
**Status:** Complete (November 2025)

**Key Files:**
- `LT6_uncertainty_analysis.csv` - Uncertainty test results
- `LT6_robustness_ranking.csv` - Controller ranking under uncertainty

**Related:**
- Figures: `../figures/LT7_section_8_1_model_uncertainty.png`
- Reports: `LT6_UNCERTAINTY_REPORT.md`

### Baselines

**Location:** `baselines/`
**Purpose:** Reference performance data for comparison

**Key Files:**
- `baseline_performance.csv` - Standard baseline metrics
- `baseline_integration.csv` - Integration test results
- `baseline_integration_template.csv` - Template for new baselines

## Size Summary

- **Total:** ~4 MB
- comprehensive_benchmarks/: ~3.8 MB
- pso_robustness/: ~120 KB
- disturbance_rejection/: ~100 KB
- model_uncertainty/: ~25 KB
- baselines/: ~50 KB

## Usage Guidelines

### Adding New Comparative Studies

1. Create subdirectory: `comparative/NEW_TASK_NAME/`
2. Add README.md with research task ID and purpose
3. Include all controller results in same format
4. Add summary JSON with cross-controller statistics
5. Reference figures in `../figures/` directory
6. Add completion report to `../reports/`

### Data Format Standards

**CSV Files:**
- Column 1: Controller name (e.g., "classical_smc", "sta_smc")
- Columns 2-N: Metrics (RMSE, settling_time, chattering, etc.)
- One row per controller

**JSON Files:**
- Top-level keys: controller names
- Nested: metric → value mappings
- Include metadata: date, seed, parameters

## Migration History

**Dec 29, 2025:**
- Created comparative/ directory to consolidate cross-controller studies
- Moved from original locations:
  - benchmarks/raw/MT-5_comprehensive/ → comprehensive_benchmarks/raw/
  - benchmarks/processed/ → comprehensive_benchmarks/processed/
  - MT7_robust_pso/ → pso_robustness/
  - MT8_disturbance_rejection/ → disturbance_rejection/
  - LT6_model_uncertainty/ → model_uncertainty/
  - benchmarks/raw/baselines/ → baselines/

## Related Directories

- **../hybrid_adaptive_sta/anomaly_analysis/** - Controller-specific hybrid investigations
- **../sta_smc/boundary_layer/** - Controller-specific STA boundary layer (MT-6)
- **../figures/** - Publication-ready comparative plots
- **../reports/** - Cross-controller analysis summaries

## Notes

- All experiments use identical simulation parameters for fair comparison
- Controllers tested: Classical SMC, STA SMC, Adaptive SMC, Hybrid Adaptive STA SMC
- Baseline data provides reference for regression testing
- Statistical significance tested using Welch's t-test and ANOVA

## Status

**Last Updated:** December 29, 2025
**Total Studies:** 4 (MT-5, MT-7, MT-8, LT-6)
**Controllers Evaluated:** 7
**Total Files:** ~50
