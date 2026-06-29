# Audit Card — M4 Slice 5: `results/` + `orchestrators/` (engines DROPPED)

- **Milestone:** M4 (simulation framework migration)
- **Slice:** 5 of 6 — `src/simulation/results/` (5 files) + `src/simulation/orchestrators/` (6 files) + docstring-only `src/simulation/__init__.py`
- **Source:** `SMC-PSO/src/simulation/{results,orchestrators}/`
- **Target:** `SMC-PSO-beta/src/simulation/{results,orchestrators}/`
- **Scope change:** Slice 5 was originally `engines + orchestrators`. Regrouped (SadeQ-confirmed) to `results + orchestrators`; **`engines/` is DROPPED entirely (Trap F)**. Strategies + package-level re-exports move to Slice 6.

## Verdict
**PORT AS-IS (banner-normalize only).** No correctness edits required. All 11 files differ from source by exactly the 3-line `#=` banner (trailing backslashes stripped, CRLF->LF) = **9 bytes each, banner-only**.

## Lens A — AI-slop / structural
- No duplicated/dead twin modules introduced. `results/` and `orchestrators/` are coherent, single-responsibility subpackages.
- No Trap-E citation tokens present (grep clean across all 11 files). The only Trap-E token in the wider source (`engines/adaptive_integrator.py`) lives in the **dropped** tree.
- Banners normalized to the clean beta 3-line `#===` style.

## Lens B — correctness / integration
- **Results layer:** `__init__` exports 6 (StandardResultContainer, BatchResultContainer, ResultProcessor, CSVExporter, HDF5Exporter, ResultValidator). Depends only on numpy + stdlib (`csv`, `pathlib`). `h5py` is imported **lazily** inside `HDF5Exporter` only and raises `ImportError("h5py required for HDF5 export")` when absent. No back-imports of orchestrators/strategies -> no import cycle.
- **Orchestrators layer:** `__init__` exports 5 (Base/Sequential/Batch/Parallel/RealTime). `base.BaseOrchestrator._create_integrator` lazily maps method strings -> Slice 3 integrators: `euler->ForwardEuler`, `rk2->RungeKutta2`, `rk4->RungeKutta4` (default), `adaptive|rk45->DormandPrince45`.
- **Cross-slice contract VERIFIED:** beta integrators expose `integrate(self, dynamics_fn, state, control, dt, t=0.0, **kwargs)` and invoke `dynamics_fn(t, state, control)` — exactly matching `base.step()` which builds `dynamics_fn(time, x, u) = dynamics_model.compute_dynamics(x, u)`.
- **Safety contract VERIFIED:** `safety.apply_safety_guards(state, step_idx, config)` always runs `guard_no_nan`; energy/bounds only fire when `config.simulation.safety` is populated (getattr-with-defaults), so finite-state runs with a minimal config are tolerated.

## Findings logged
- **S5-1 (supersedes S3-2):** `core/time_domain.AdaptiveTimeStep.update_step_size` has a hard-coded `(1/4)` order exponent (L267). **Resolved by analysis — left UNTOUCHED.** It is NOT on the canonical path: orchestrators + integrators perform adaptive stepping via the order-aware `ErrorController` in `integrators/adaptive`. Editing a shipped Slice-2 file for dead code would add parity risk with zero runtime benefit. Re-evaluate only if a consumer of `AdaptiveTimeStep` is found in a later milestone.
- **S5-2:** `orchestrators/sequential.py` legacy module functions `get_step_fn` / `step` / `_load_full_step` / `_load_lowrank_step` reference PRE-migration paths (`src.config.schemas`, `...plant.models.dip_full` / `dip_lowrank`) that do not exist in beta. They are **lazy and dead on the canonical path** (the OOP `SequentialOrchestrator.execute` + `run_simulation` do not touch them). **Preserved byte-identical for parity**; path remap deferred to Slice 6 / M6 when legacy `step` consumers are audited.
- **S5-3 (Trap F closure):** `engines/` (adaptive_integrator, simulation_runner, vector_sim) **DROPPED**. It duplicated the integrators + orchestrators layers, was reachable only via the deprecated `src/core/*` shims (Trap B, also not ported), still imported the removed `context/` package (Trap C), and carried the lone Trap-E citation token. Analogous to the Trap-C `context/` drop in Slice 4.
- **S5-4:** `src/simulation/__init__.py` updated **docstring-only** to record the Slice 5 regrouping (results+orchestrators, engines dropped/Trap F; strategies -> Slice 6). Package remains **import side-effect free**; package-level re-exports + legacy aliases (Trap D) stay DEFERRED to Slice 6.

## Gate results (offline harness)
- **Tests:** 26/26 passed (14 results unit + 12 orchestrator behavioral/import). 0 failed, 0 skipped.
- **Parity:** STRUCTURAL OK (banner-only, 9 bytes/file across 11 files) + BEHAVIORAL OK (RK4 vs closed-form reference).
- **P0 = 0, P1 = 0.**
- **No `src/core/` imports** introduced.

## Carry-forward
- **Slice 6:** port `strategies/` (MonteCarloStrategy), wire package-level `simulation/__init__` re-exports + `_guard_*` aliases (Trap D close), and remap/cleanup the S5-2 legacy plant paths.
- Before fully retiring `engines/` (M6/M9): grep repo for importers of `src.simulation.engines` / `src.core.vector_sim` / `src.core.simulation_runner`.
