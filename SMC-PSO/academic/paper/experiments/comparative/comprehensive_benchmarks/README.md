# Benchmark Suite

Publication-ready benchmark data supporting research validation and performance analysis.

## Directory Structure

- `raw/` - Immutable original benchmark outputs, organized by research task
- `processed/` - Derived/aggregated analysis datasets
- `figures/` - Publication-ready plots and visualizations
- `reports/` - Task completion summaries and research documentation

## Research Task Provenance

- **MT-5** (Oct 25, 2025): Comprehensive benchmark suite (7 controllers)
- **MT-6** (Oct 26-27, 2025): Boundary layer optimization and chattering reduction
- **MT-7** (Oct 28, 2025): Robust PSO tuning with multiple seeds
- **MT-8** (Oct 29, 2025): Disturbance rejection testing
- **LT-4** (Oct 30, 2025): Lyapunov stability proofs
- **QW-2** (Nov 7, 2025): Quick win comprehensive benchmark

## Reproduction Instructions

1. Run batch benchmarks: `python scripts/benchmarks/batch_benchmark.py`
2. View results: `cat benchmarks/raw/MT-5_comprehensive/comprehensive_benchmark.csv`
3. Generate figures: Check `benchmarks/figures/` for visualization outputs

## Data Organization Philosophy

Raw data is immutable and organized by research task for traceability. Processed data
represents aggregated analysis and cross-controller comparisons. All benchmark outputs
preserve git history for scientific reproducibility.

## Migration History

This directory was reorganized on December 18, 2025 to separate raw benchmark outputs
from analysis modules and create publication-ready structure. See:
- Migration script: `scripts/migration/update_benchmark_paths.py`
- Backup: `.artifacts/backups/benchmarks_pre_reorg_20251218.tar.gz`
