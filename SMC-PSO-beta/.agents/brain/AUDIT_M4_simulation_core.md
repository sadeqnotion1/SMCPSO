# M4 Audit Note — Controllers base + Simulation core (porting traps & gates)

> Built from a real read of `SMC-PSO/src/controllers/base/`, `SMC-PSO/src/simulation/`, the deprecated `SMC-PSO/src/core/`, and the beta `src/` tree.
> Source-of-truth rule: **code wins**. Use this as the gate before accepting M4.

## M4 scope (per STATE.md / graph.json)
- `src/controllers/base.py` (base controller interface + primitives)
- `src/simulation/` (canonical framework: core, integrators, orchestrators/engines, safety, results, strategies). graph nodes: `runner`, `vector_sim`, `safety_guards`.

## Source -> target map
| Source (SMC-PSO) | Target (beta) | Note |
|---|---|---|
| `src/controllers/base/` (package: `__init__`, `control_primitives.py`, `controller_interface.py`) | `src/controllers/base.py` | graph node is a single file -> flatten OR keep package (Trap F) |
| `src/simulation/core/` | `src/simulation/core/` | abstract interfaces (clean) |
| `src/simulation/integrators/` | `src/simulation/integrators/` | fixed_step, adaptive, discrete, factory |
| `src/simulation/safety/` | `src/simulation/safety/` | canonical safety (Trap C) |
| `src/simulation/engines/` + `orchestrators/` | `src/simulation/` | runner, vector_sim, sequential/batch/parallel/real_time |
| `src/simulation/results/`, `strategies/` | `src/simulation/` | containers, processors, monte_carlo |
| `src/core/` (deprecated flat twin) | ❌ DO NOT PORT | superseded by `src/simulation/` (Trap B) |

## Traps (gate before porting)

### Trap A — STATE-VECTOR ORDERING MISMATCH (critical)
- Controllers (`controller_interface.py`) document `[x, x_dot, theta1, theta1_dot, theta2, theta2_dot]` (interleaved).
- Corrected physics (`physics_matrices_corrected.py`) uses `[x, theta1, theta2, x_dot, theta1_dot, theta2_dot]` (grouped).
- These disagree. If a controller feeds a state straight into the plant without re-ordering, the dynamics are silently WRONG (no exception, just bad results).
- [ ] Choose ONE canonical ordering for beta, document it once, and adapt at every plant<->controller<->simulation boundary. Add a unit test that asserts the convention.

### Trap B — deprecated `src/core/` flat twin
`src/core/` holds `dynamics.py`, `dynamics_full.py`, `safety_guards.py`, `simulation_context.py`, `simulation_runner.py`, `vector_sim.py` — the OLD flat versions superseded by `src/simulation/`.
- [ ] Do not port `src/core/`. Confirm nothing in beta imports from `src/core` (grep before/after).

### Trap C — duplication INSIDE `src/simulation/`
Two parallel copies of the same concepts:
- `simulation/context/simulation_context.py` vs `simulation/core/simulation_context.py`
- `simulation/context/safety_guards.py` vs `simulation/safety/guards.py`
- [ ] Decide canonical (the "new framework" `core/` + `safety/` vs legacy `context/`), port ONE, drop the other. Don't port both.

### Trap D — legacy compat shims in `simulation/__init__.py`
The source `__init__` re-exports legacy names: `get_step_fn`, `step`, `run_simulation`, `simulate`, `rk45_step`, `_guard_no_nan/_energy/_bounds`.
- [ ] Decide whether beta keeps these aliases (back-compat) or goes clean to match the flat graph target. If dropped, update every importer.

### Trap E — AI-slop citation tokens (Lens A)
`control_primitives.py` docstrings contain hallucinated-looking reference anchors, e.g. `【462167782799487†L186-L195】`. These are fake citation tokens (AI artifact), not real references.
- [ ] Strip them; replace with a real `references/` citation or remove. Sweep the rest of the port for the same pattern.

### Trap F — base package vs single-file node
`controllers/base/` is a 3-file package; the graph node is `controllers/base.py`.
- [ ] Decide: flatten to one `base.py` (matches graph) or keep the package and treat `base.py` as the node. (Mirror of the M5 factory-package decision — be consistent.) This kit ships a flattened `src/controllers/base.py` for Slice 1.

## Slice plan (dependency-first; each slice = port -> audit A+B -> parity vs source -> tests -> Audit Card -> STATE update)
1. **controllers/base.py** — `ControllerInterface` + `saturate` + validators. (Drop-in provided in this kit.) Resolve Trap F; note Trap A.
2. **simulation/core** — interfaces, simulation_context, state_space, time_domain.
3. **integrators** — fixed_step (euler, rk4), adaptive (rk45 + error_control), discrete (ZOH), factory.
4. **safety** — guards, constraints, monitors, recovery. Resolve Trap C.
5. **engines + orchestrators** — simulation_runner, vector_sim, sequential/batch/parallel/real_time.
6. **results + strategies** — containers, processors, exporters, validators, monte_carlo.

## Gate (per slice, before marking accepted)
- [ ] P0 = 0, P1 = 0
- [ ] Parity vs source within tolerance (esp. Numba vs pure-Python path)
- [ ] Coverage target met; tests green
- [ ] State-ordering convention asserted by a test (Trap A)
- [ ] No imports from deprecated `src/core/`
- [ ] Audit Card filed; findings -> `AUDIT_LEDGER.md`
