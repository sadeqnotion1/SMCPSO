# docs/guides/ Gap Analysis

**Audit Date:** November 10, 2025

---

## Summary

- Incomplete files: 8
- Outdated content: 51
- Missing topics: 0

## Controller Documentation Coverage

| Controller | Documented | Status |
|------------|------------|--------|
| classical_smc | True | [OK] YES |
| sta_smc | True | [OK] YES |
| adaptive_smc | True | [OK] YES |
| hybrid_adaptive_sta_smc | True | [OK] YES |
| swing_up_smc | False | [ERROR] NO |
| mpc_controller | False | [ERROR] NO |
| factory | True | [OK] YES |

[WARNING] Missing controller docs: swing_up_smc, mpc_controller

## Incomplete Files

| File | Lines | Issue | Examples |
|------|-------|-------|----------|
| guides\workflows\hil-disaster-recovery.md | 42 | Only 42 lines (likely incomplete) | N/A |
| guides\workflows\hil-multi-machine.md | 31 | Only 31 lines (likely incomplete) | N/A |
| guides\workflows\hil-production-checklist.md | 42 | Only 42 lines (likely incomplete) | N/A |
| guides\workflows\hil-safety-validation.md | 31 | Only 31 lines (likely incomplete) | N/A |
| guides\workflows\pso-adaptive-smc.md | 36 | Only 36 lines (likely incomplete) | N/A |
| guides\workflows\pso-hil-tuning.md | 28 | Only 28 lines (likely incomplete) | N/A |
| guides\workflows\pso-hybrid-smc.md | 43 | Only 43 lines (likely incomplete) | N/A |
| guides\workflows\pso-vs-grid-search.md | 36 | Only 36 lines (likely incomplete) | N/A |

## Outdated Content

| File | Issue | Examples |
|------|-------|----------|
| guides\api\configuration.md | 115 old version references | 1.5, 0.5, 0.75 |
| guides\api\controllers.md | 71 old version references | 0.0, 0.0, 0.0 |
| guides\api\optimization.md | 84 old version references | 0.7298, 1.49618, 1.49618 |
| guides\api\plant-models.md | 53 old version references | 1.5, 0.5, 0.75 |
| guides\api\README.md | 8 old version references | 1.0, 0.1, 0.1 |
| guides\api\simulation.md | 67 old version references | 0.01, 1.5, 0.5 |
| guides\api\utilities.md | 39 old version references | 0.1, 0.05, 0.2 |
| guides\features\code-collapse\changelog.md | 5 old version references | 1.0, 1.0, 0.05 |
| guides\features\code-collapse\configuration-reference.md | 23 old version references | 0.4, 0.0, 0.2 |
| guides\features\code-collapse\integration-guide.md | 2 old version references | 0.5, 0.3 |
| guides\features\code-collapse\maintenance-guide.md | 8 old version references | 0.1, 1.0, 1.0 |
| guides\features\code-collapse\PHASE6_COMPLETION_SUMMARY.md | 5 old version references | 0.1, Version 1.0, v1.0 |
| guides\features\code-collapse\technical-reference.md | 11 old version references | 1.0, 0.4, 0.0 |
| guides\features\code-collapse\troubleshooting.md | 3 old version references | 0.15, 0.25, 1.2 |
| guides\features\code-collapse\user-guide.md | 1 old version references | v1.0 |
| guides\features\README.md | 1 old version references | v1.0 |
| guides\getting-started-validation-report.md | 8 old version references | 0.5, 0.5, 0.5 |
| guides\getting-started.md | 44 old version references | 1.5, 0.001, 0.1 |
| guides\how-to\optimization-workflows.md | 75 old version references | 0.1, 0.0, 0.1 |
| guides\how-to\result-analysis.md | 30 old version references | 0.3, 0.3, 0.6 |
| guides\how-to\robust-pso-optimization.md | 72 old version references | 0.3, 0.05, 0.7 |
| guides\how-to\running-simulations.md | 48 old version references | 0.0, 0.0, 0.05 |
| guides\how-to\testing-validation.md | 48 old version references | 0.0, 0.0, 0.0 |
| guides\icon_usage_guide.md | 6 old version references | 1.21, 0.875, 0.875 |
| guides\INDEX.md | 2 old version references | 0.5, 0.5 |
| guides\interactive\3d-pendulum-demo.md | 22 old version references | 0.00, 0.10, 0.5 |
| guides\interactive\jupyter-notebooks-demo.md | 5 old version references | 0.1, 0.0, 0.25 |
| guides\interactive\live-python-demo.md | 8 old version references | 0.3, 0.3, 0.3 |
| guides\interactive\mathematical-visualizations-demo.md | 43 old version references | 0.2, 0.1, 0.15 |
| guides\interactive\plotly-charts-demo.md | 21 old version references | 0.5, 1.0, 1.5 |
| guides\interactive_configuration_guide.md | 55 old version references | 0.7, 0.7, 0.7 |
| guides\interactive_visualizations.md | 26 old version references | 0.1, 0.5, 0.9 |
| guides\QUICK_REFERENCE.md | 45 old version references | 0.0, 0.0, 0.0 |
| guides\README.md | 2 old version references | v1.0, 0.02 |
| guides\sphinx_theme_guide.md | 4 old version references | 0.15, 0.0, 0.0 |
| guides\theory\dip-dynamics.md | 3 old version references | 0.2, 0.3, 0.5 |
| guides\theory\pso-theory.md | 19 old version references | 0.9, 0.7, 0.4 |
| guides\theory\smc-theory.md | 51 old version references | 0.3, 0.2, 0.15 |
| guides\tutorials\tutorial-01-first-simulation.md | 147 old version references | 1.0, 0.1, 0.1 |
| guides\tutorials\tutorial-01-validation-report.md | 26 old version references | 0.5, 0.5, 0.5 |
| guides\tutorials\tutorial-02-controller-comparison.md | 89 old version references | 1.1, 0.45, 1.2 |
| guides\tutorials\tutorial-03-pso-optimization.md | 163 old version references | 0.4, 0.9, 0.729844 |
| guides\tutorials\tutorial-04-custom-controller.md | 110 old version references | 0.5, 0.7, 1.0 |
| guides\tutorials\tutorial-05-research-workflow.md | 53 old version references | 0.05, 1.0, 0.1 |
| guides\user-guide.md | 105 old version references | 1.0, 1.0, 0.1 |
| guides\workflows\batch-simulation-workflow.md | 46 old version references | 1.0, 1.1, 1.2 |
| guides\workflows\hil-workflow.md | 66 old version references | 1.0, 0.0, 0.0 |
| guides\workflows\monte-carlo-validation-quickstart.md | 51 old version references | 1.0, 0.1, 0.5 |
| guides\workflows\pso-optimization-workflow.md | 52 old version references | 1.0, 0.7, 0.000000 |
| guides\workflows\pso-sta-smc.md | 49 old version references | 0.7, 0.74, 0.59 |
| guides\workflows\streamlit-theme-integration.md | 3 old version references | 0.0, 0.05, 0.1 |

## Missing Topics

None found
