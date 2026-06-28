# SMC-PSO Migration — Audit Note & M5/M8 Porting Traps

> Permanent checklist from the 2026-06-28 cross-check of `graph.json` (target) vs `STATE.md` (plan) vs the actual `SMC-PSO-beta/` and `SMC-PSO/` trees.
> Use the M5 and M8 sections as gates before porting those milestones.
> Source-of-truth rule: **code wins** — if reality and this note disagree, fix the brain.

## Migration status snapshot
- **M1** Environment & config — DONE
- **M2** Plant dynamics (FULL model) — DONE
- **M3** Utils & primitives — WIP (Slices 1-7 accepted)
- **M4-M11** — TODO

`graph.json` describes the **target** architecture, not the current files: of its 17 nodes, only **config**, **plant**, and **utils (partial)** exist in beta. This is expected — it is not drift.

## Finding #1 — STATE.md reconciliation (simplified / low-rank plant)
Scaffold files for the simplified and low-rank plant models already exist in beta
(`src/plant/models/simplified/`, `src/plant/models/lowrank/`), but validation + parity
testing are deferred. The original `[TODO]` row read as if the files were missing.
See `patches/STATE.md.patch.md` for the exact edit.

## Finding #2 — physics_matrices: canonical vs deprecated
During the M2 audit, a physical inconsistency was found in the source's inertia-matrix
equations. The corrected math lives in `physics_matrices_corrected.py`, which is now the
active source of truth. The original `physics_matrices.py` is deprecated.

Action items:
- [ ] Confirm all beta imports reference `physics_matrices_corrected`, not `physics_matrices`.
- [ ] Remove `physics_matrices.py` or clearly mark it deprecated (docstring + no live imports).
- [ ] Record the inertia-matrix fix in the audit ledger (Lens B / scientific correctness) with the reference used.
- [ ] (Optional) Note in STATE.md M2 row that accepted physics uses the corrected matrices.

## M5 trap — controller consolidation (flat target vs nested source)
`graph.json` targets a FLAT controller layout; `SMC-PSO/` holds the same logic in TWO
parallel nested trees. Decide the canonical source and consolidate before porting — do not port both.

Target (graph.json):
- `src/controllers/factory.py`
- `src/controllers/classical_smc.py`
- `src/controllers/sta_smc.py`
- `src/controllers/adaptive_smc.py`
- `src/controllers/hybrid_adaptive_sta_smc.py`

Source has it twice:
- `src/controllers/smc/` -> `classic_smc.py`, `sta_smc.py`, `adaptive_smc.py`, `hybrid_adaptive_sta_smc.py`
- `src/controllers/algorithms/{classical,super_twisting,adaptive,hybrid}/controller.py` (+ `config.py`, helpers) and `src/controllers/factory/` (multi-file package)

M5 checklist:
- [ ] Pick the canonical implementation: flat `smc/` modules vs `algorithms/` packages (port one, not both).
- [ ] Rename `classic_smc.py` -> `classical_smc.py` to match the target node path.
- [ ] Collapse `controllers/factory/` (package) into the single target `controllers/factory.py`, or justify keeping a package.
- [ ] Fold needed pieces of `controllers/base/` and `controllers/core/` into the M4 `controllers/base.py` target.
- [ ] Map `algorithms/*/` helpers (boundary_layer, twisting_algorithm, switching_logic, adaptation_law) to their new home.
- [ ] Exclude `controllers/specialized/swing_up_smc.py` and `mpc/` unless explicitly in scope.
- [ ] Run parity vs source after consolidation; file the Audit Card before marking DONE.

## M8 trap — src/analysis/ is NOT src/utils/analysis/
Two different things with confusingly similar names. Do not mark M8 done just because a
`statistics.py` exists under utils.

| Path | What it is | Milestone |
| --- | --- | --- |
| `src/utils/analysis/statistics.py` | small statistics helper under utils | part of M3 (utils) — already in beta |
| `src/analysis/` | full analysis module: FDI/fault_detection, performance, validation, visualization, reports | M8 — not yet ported |

M8 checklist:
- [ ] Port `src/analysis/fault_detection/` (fdi, fdi_system, residual_generators, threshold_adapters).
- [ ] Port `src/analysis/performance/` (control_analysis, control_metrics, robustness, stability_analysis).
- [ ] Port `src/analysis/validation/` (benchmarking, cross_validation, monte_carlo, statistical_tests, ...).
- [ ] Port `src/analysis/visualization/` (analysis_plots, diagnostic_plots, report_generator, statistical_plots).
- [ ] Keep utils `analysis/statistics.py` separate; reconcile any overlap deliberately.
- [ ] Confirm the `analysis` graph node resolves to top-level `src/analysis/`, not utils.

## Not-yet-ported graph nodes (reference)
| Node | Target path | Milestone |
| --- | --- | --- |
| cli | `simulate.py` | M9 |
| web | `streamlit_app.py` | M9 |
| factory | `src/controllers/factory.py` | M5 |
| smc_classical | `src/controllers/classical_smc.py` | M5 |
| smc_sta | `src/controllers/sta_smc.py` | M5 |
| smc_adaptive | `src/controllers/adaptive_smc.py` | M5 |
| smc_hybrid | `src/controllers/hybrid_adaptive_sta_smc.py` | M5 |
| runner | `src/simulation/` | M4 |
| vector_sim | `src/simulation/` | M4 |
| safety_guards | `src/simulation/safety` | M4 |
| pso | `src/optimization/algorithms` | M6 |
| cost | `src/optimization/objectives` | M6 |
| analysis | `src/analysis` | M8 |
| hil | `src/interfaces/hil` | M7 |
