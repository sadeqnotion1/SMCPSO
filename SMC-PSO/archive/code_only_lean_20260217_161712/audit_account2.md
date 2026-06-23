# Audit Report — Account 2
## Simulation Engine + Optimization Core
**Files reviewed:** 57
**Scope:** `src\simulation\`, `src\optimizer\`, `src\optimization\algorithms\`, `src\optimization\core\`

---

## Critical Issues Summary

### BROKEN (7 files)

| File | Issue |
|---|---|
| `src\simulation\engines\vector_sim.py` | Energy guard type crash; batch simulate stubs results instead of re-simulating |
| `src\simulation\integrators\adaptive\runge_kutta.py` | Rejected steps silently freeze state — adaptive integrator not actually adaptive |
| `src\simulation\orchestrators\batch.py` | Terminated trajectories misreported as full-length (trailing zeros) |
| `src\simulation\orchestrators\parallel.py` | Worker context init incompatible with SimulationContext constructor |
| `src\simulation\safety\guards.py` | Safety guard crashes on typed config models instead of enforcing limits |
| `src\simulation\context\simulation_context.py` | Stale duplicate context — unguarded import breaks simplified-model-only builds |
| `src\optimizer\ga_optimizer.py` | Result field mismatch — cannot return valid framework result |
| `src\optimization\algorithms\evolutionary\genetic.py` | OptimizationResult constructor called with wrong fields — always crashes |
| `src\optimization\algorithms\gradient_based\bfgs.py` | Same result contract break as genetic.py |
| `src\optimization\algorithms\gradient_based\nelder_mead.py` | Same result contract break |
| `src\optimization\core\context.py` | Factory creates optimizers with wrong constructors/import paths |

### NEEDS WORK (9 files)

| File | Issue |
|---|---|
| `src\simulation\engines\adaptive_integrator.py` | RK45 reject exponent inconsistent; no pathological tolerance guard |
| `src\simulation\engines\simulation_runner.py` | round() for n_steps can overshoot sim horizon |
| `src\simulation\integrators\compatibility.py` | Silently drops time arg and collapses vector control to scalar |
| `src\simulation\orchestrators\real_time.py` | Forced dummy arrays for callback controllers; broad 0.0 fallback |
| `src\simulation\orchestrators\sequential.py` | round() horizon drift + multi-input collapse |
| `src\simulation\core\state_space.py` | compute_energy() only computes kinetic — named incorrectly |
| `src\simulation\core\time_domain.py` | int(inf) raises overflow on undefined horizon |
| `src\optimization\algorithms\base.py` | Duplicate abstraction layer unused by key algorithms |
| `src\optimization\algorithms\pso_optimizer.py` | params_list batch path replicates not re-simulates |
| `src\optimization\algorithms\memory_efficient_pso.py` | History tracking hooks partially disconnected |
| `src\optimization\algorithms\multi_objective_pso.py` | Not true multi-objective; parallel path defeats parallelism |

### CLEAN (35 files — no issues found)

---

## Full File-by-File Report

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports are consistently wired
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\engines\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] compatibility exports are coherent
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\engines\adaptive_integrator.py
- CORRECTNESS:  [ISSUE] RK45 reject-step resize exponent (-0.25) is inconsistent with the method order usage in the same function
- AI SLOP:      [ISSUE] docstring contains corrupted text/citation artifacts
- ARCHITECTURE: [PASS] API shape is clear and compatible
- SAFETY:       [ISSUE] no explicit guard for pathological tolerance settings (can generate invalid scaling)
- VERDICT:      [NEEDS WORK]
- NOTES:        numerical method intent is good, but needs cleanup and tighter stability handling

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\engines\simulation_runner.py
- CORRECTNESS:  [ISSUE] n_steps uses round(sim_time/dt) despite doc saying "not exceeding sim_time"; this can overshoot horizon semantics
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] routing and legacy interface are wired correctly
- SAFETY:       [PASS] non-finite dynamics output is handled with truncation/strict-mode raise
- VERDICT:      [NEEDS WORK]
- NOTES:        replace round with floor-like behavior for deterministic horizon bounds

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\engines\vector_sim.py
- CORRECTNESS:  [FAIL] final _guard_energy call always casts energy_limits to float; dict input path crashes
- AI SLOP:      [FAIL] params_list path in simulate_system_batch is documented as robust/multi-params but currently replicates results instead of re-simulating
- ARCHITECTURE: [ISSUE] batch simulate() path calls _step_fn on batched state directly; depends on non-guaranteed vectorization in dynamics step
- SAFETY:       [FAIL] safety guard path can fail due type mismatch instead of enforcing limits
- VERDICT:      [BROKEN]
- NOTES:        robustness/uncertainty execution is effectively stubbed in current form

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\integrators\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports are consistent with submodules
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\integrators\base.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] interface abstraction is coherent
- SAFETY:       [PASS] input validation checks finite state/control and positive dt
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\integrators\compatibility.py
- CORRECTNESS:  [ISSUE] wrapper silently retries without t, dropping time argument on signature mismatch
- AI SLOP:      [ISSUE] LegacyDynamicsWrapper collapses vector control to first scalar element
- ARCHITECTURE: [ISSUE] compatibility path can mask real interface defects instead of surfacing them
- SAFETY:       [ISSUE] fallback path can return unchanged/zero-like dynamics, hiding unstable behavior
- VERDICT:      [NEEDS WORK]
- NOTES:        compatibility shim currently trades correctness for silent fallback

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\integrators\factory.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] factory registry and aliases are clean
- SAFETY:       [PASS] unknown integrator type is explicitly rejected
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\integrators\adaptive\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] re-exports are coherent
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\integrators\adaptive\error_control.py
- CORRECTNESS:  [PASS] error controller formulas are internally consistent
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] controller classes are clearly separated
- SAFETY:       [PASS] step factor clipping prevents extreme growth/shrink
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\integrators\adaptive\runge_kutta.py
- CORRECTNESS:  [FAIL] integrate() performs one adaptive attempt and returns current state on rejection without retry loop or caller-facing dt update
- AI SLOP:      [ISSUE] unused wrapper (dynamics_wrapper) indicates leftover/refactor artifact
- ARCHITECTURE: [ISSUE] adaptive integrator contract is incomplete for orchestrator use (reject path not propagated)
- SAFETY:       [FAIL] rejected steps can silently freeze state progression
- VERDICT:      [BROKEN]
- NOTES:        adaptive method is not operationally adaptive in current engine flow

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\integrators\discrete\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] export is minimal and correct
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\integrators\discrete\zero_order_hold.py
- CORRECTNESS:  [PASS] ZOH discretization (augmented-matrix exponential) is mathematically correct
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] linear/nonlinear paths are clearly split
- SAFETY:       [PASS] missing matrix setup is explicitly rejected
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\integrators\fixed_step\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] export wiring is clean
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\integrators\fixed_step\euler.py
- CORRECTNESS:  [PASS] Euler formulas are correct (x+dt*f, implicit residual form)
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] integrator interfaces align
- SAFETY:       [PASS] fallback handling present if implicit solver fails
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\integrators\fixed_step\runge_kutta.py
- CORRECTNESS:  [PASS] RK2/RK4/3-8 formulas are correct
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] method classes are cleanly separated
- SAFETY:       [PASS] input validation is enforced
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\orchestrators\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports are consistent with package layout
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\orchestrators\base.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] base orchestration responsibilities are clear
- SAFETY:       [PASS] simulation input validation exists
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\orchestrators\batch.py
- CORRECTNESS:  [FAIL] terminated/failed trajectories can be misreported as full-length due zero-initialized finite tail and "last valid step" logic
- AI SLOP:      [ISSUE] vectorized framing exists, but execution is largely per-item loops with shape edge-case risk
- ARCHITECTURE: [ISSUE] control normalization paths are brittle across input rank variants
- SAFETY:       [ISSUE] safety failures deactivate trajectories but do not preserve explicit failure markers
- VERDICT:      [BROKEN]
- NOTES:        truncated trajectories can contain misleading trailing zeros

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\orchestrators\parallel.py
- CORRECTNESS:  [FAIL] worker context is instantiated with model_dump_json() as if it were config path, which breaks config loading in worker simulations
- AI SLOP:      [ISSUE] fallback behavior prints and swallows worker errors rather than preserving typed failure detail
- ARCHITECTURE: [FAIL] thread worker setup is incompatible with SimulationContext constructor contract
- SAFETY:       [ISSUE] failed workers are silently converted to None
- VERDICT:      [BROKEN]
- NOTES:        parallel batch path is structurally incorrect for real execution

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\orchestrators\real_time.py
- CORRECTNESS:  [ISSUE] control-input validation is enforced even when runtime controller callback is used, forcing unused dummy arrays
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] scheduler integration is coherent
- SAFETY:       [ISSUE] broad exception fallback to 0.0 control can hide control-path defects
- VERDICT:      [NEEDS WORK]
- NOTES:        realtime loop structure is sound but API coupling is awkward

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\orchestrators\sequential.py
- CORRECTNESS:  [ISSUE] legacy run_simulation uses round(sim_time/dt) and collapses multi-input control to first channel
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] backward-compatibility interface is preserved
- SAFETY:       [ISSUE] broad catch/trim behavior suppresses root-cause details
- VERDICT:      [NEEDS WORK]
- NOTES:        core flow works, but control-shape handling is lossy

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\safety\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] safety API exports are consistent
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\safety\constraints.py
- CORRECTNESS:  [PASS] constraint checks are internally consistent
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] compositional checker pattern is clear
- SAFETY:       [PASS] constraint violations are explicitly returned
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\safety\guards.py
- CORRECTNESS:  [FAIL] apply_safety_guards/create_default_guards assume dict-like energy_limits ("max" in ...), which can crash on object-style config
- AI SLOP:      [ISSUE] hardcoded step_idx * 0.01 time proxy is a placeholder, not real simulation time
- ARCHITECTURE: [ISSUE] config-shape handling is inconsistent across guard helpers
- SAFETY:       [FAIL] safety layer can raise type errors instead of enforcing constraints
- VERDICT:      [BROKEN]
- NOTES:        guard enforcement path is fragile for typed config models

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\safety\monitors.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] monitoring responsibilities are well-separated
- SAFETY:       [PASS] event tracking is non-intrusive and deterministic
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\safety\recovery.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] strategy abstraction is coherent
- SAFETY:       [PASS] default emergency-stop fallback is present
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\context\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] compatibility exports are clear
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\context\safety_guards.py
- CORRECTNESS:  [PASS] guard formulas/check semantics are correct
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] vectorized guard API is clear
- SAFETY:       [PASS] violations raise explicitly
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\context\simulation_context.py
- CORRECTNESS:  [FAIL] unguarded import of full dynamics module occurs before use_full_dynamics branch, breaking light builds even when full model is disabled
- AI SLOP:      [ISSUE] duplicate context implementation diverges from core/simulation_context.py
- ARCHITECTURE: [FAIL] stale parallel context implementation conflicts with newer core context behavior
- SAFETY:       [ISSUE] import-time failure prevents fallback to safe simplified model path
- VERDICT:      [BROKEN]
- NOTES:        this module is an outdated duplicate and currently hazardous

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\core\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] core exports are coherent
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\core\interfaces.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] abstract contracts are clear
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\core\simulation_context.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] lazy import/factory wiring is solid
- SAFETY:       [PASS] optional full-model/fdi paths fail gracefully
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\core\state_space.py
- CORRECTNESS:  [ISSUE] compute_energy() claims total energy but only computes kinetic term
- AI SLOP:      [ISSUE] "potential energy" comment indicates unimplemented placeholder semantics
- ARCHITECTURE: [PASS] utility methods are modular
- SAFETY:       [PASS] operations are numerically straightforward
- VERDICT:      [NEEDS WORK]
- NOTES:        method naming/docs should match returned quantity

### D:\Projects\main\code_only_lean_20260217_161712\src\simulation\core\time_domain.py
- CORRECTNESS:  [ISSUE] remaining_steps() can raise on int(float('inf')) when horizon is undefined
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] time/scheduler abstractions are coherent
- SAFETY:       [ISSUE] edge case produces runtime overflow instead of sentinel handling
- VERDICT:      [NEEDS WORK]
- NOTES:        use explicit sentinel (None/np.inf) instead of int(inf)

### D:\Projects\main\code_only_lean_20260217_161712\src\optimizer\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] deprecation shim is explicit
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\optimizer\pso_optimizer.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] compatibility re-exports are clear
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\optimizer\cmaes_optimizer.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] tuner wraps objective and evaluator cleanly
- SAFETY:       [PASS] external dependency is explicitly checked
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\optimizer\de_optimizer.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] wrapper/problem adapter is coherent
- SAFETY:       [PASS] finite-cost fallback is handled by evaluator
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\optimizer\ga_optimizer.py
- CORRECTNESS:  [FAIL] expects GA result fields (best_parameters, best_cost) that are inconsistent with core result contracts
- AI SLOP:      [ISSUE] wrapper assumes a result schema that does not match the framework
- ARCHITECTURE: [FAIL] adapter contract between tuner and algorithm result is mismatched
- SAFETY:       [ISSUE] runtime attribute errors likely during successful optimize return path
- VERDICT:      [BROKEN]
- NOTES:        result object mapping is currently incompatible

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] commented placeholders are explicit
- ARCHITECTURE: [PASS] package exports are coherent
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\base.py
- CORRECTNESS:  [ISSUE] class hierarchy here is largely unused by key algorithms that inherit from core optimizer interfaces instead
- AI SLOP:      [ISSUE] dead/parallel abstraction layer increases confusion without clear runtime value
- ARCHITECTURE: [ISSUE] duplicate abstraction stack with core.interfaces weakens consistency
- SAFETY:       [PASS] none found
- VERDICT:      [NEEDS WORK]
- NOTES:        unify on one optimizer base contract

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\pso_optimizer.py
- CORRECTNESS:  [ISSUE] uncertainty aggregation depends on simulate_system_batch(params_list=...), but that path currently replicates results instead of distinct scenario simulation
- AI SLOP:      [ISSUE] some version-compatibility/manual-step codepaths appear unverified
- ARCHITECTURE: [PASS] overall tuner structure is coherent
- SAFETY:       [ISSUE] robustness claims are weakened by upstream scenario execution behavior
- VERDICT:      [NEEDS WORK]
- NOTES:        ISE computation correct for zero-reference error; IAE/ITAE not implemented in this cost path

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\robust_pso_optimizer.py
- CORRECTNESS:  [PASS] robust path correctly overrides fitness to multi-scenario evaluator
- AI SLOP:      [PASS] not identical to base PSO
- ARCHITECTURE: [PASS] inheritance and fallback behavior are clear
- SAFETY:       [PASS] robust evaluator path improves stress-case coverage
- VERDICT:      [CLEAN]
- NOTES:        key difference vs base PSO: uses RobustCostEvaluator.evaluate_batch_robust() (scenario ensemble, mean + alpha*worst) instead of single-scenario _fitness

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\memory_efficient_pso.py
- CORRECTNESS:  [ISSUE] history tracking relies on _last_best_cost/_last_best_position that are not set in this class path
- AI SLOP:      [ISSUE] several memory-history hooks are present but partially disconnected
- ARCHITECTURE: [PASS] memory-management wrappers are logically structured
- SAFETY:       [PASS] emergency cleanup and thresholds are implemented
- VERDICT:      [NEEDS WORK]
- NOTES:        monitoring is useful, but some metrics paths are effectively inert

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\multi_objective_pso.py
- CORRECTNESS:  [ISSUE] "multi-objective" helper objectives are scalar rescalings of one base cost, not true independent objective decomposition
- AI SLOP:      [ISSUE] create_control_objectives() is a heuristic stub
- ARCHITECTURE: [ISSUE] parallel evaluation path calls future.result() immediately, defeating actual parallelism
- SAFETY:       [PASS] bound and velocity clipping are present
- VERDICT:      [NEEDS WORK]
- NOTES:        PSO velocity/position update itself matches standard form

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\swarm\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] export scope is clear
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\swarm\pso.py
- CORRECTNESS:  [PASS] PSO update is correct: v = w*v + c1*r1*(pbest-x) + c2*r2*(gbest-x), then x = x + v
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] optimizer integrates cleanly with framework interfaces
- SAFETY:       [PASS] bounds/velocity clamping and constraint penalties are applied
- VERDICT:      [CLEAN]
- NOTES:        required PSO law matches specification

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\evolutionary\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports are consistent
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\evolutionary\differential.py
- CORRECTNESS:  [PASS] DE mutation/crossover/selection logic is coherent
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] aligns with core optimizer interface
- SAFETY:       [PASS] parameter ranges are clipped and validated
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\evolutionary\genetic.py
- CORRECTNESS:  [FAIL] _create_result() builds OptimizationResult with wrong constructor fields (missing required x/fun/status), causing runtime failure
- AI SLOP:      [ISSUE] mixed interface assumptions (problem.evaluate) diverge from standard OptimizationProblem API (evaluate_objective)
- ARCHITECTURE: [FAIL] result contract is incompatible with framework core interfaces
- SAFETY:       [ISSUE] failed evaluations degrade to inf, but terminal result construction can still crash
- VERDICT:      [BROKEN]
- NOTES:        this algorithm currently cannot return a valid framework OptimizationResult

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\gradient_based\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports are coherent
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\gradient_based\bfgs.py
- CORRECTNESS:  [FAIL] uses problem.evaluate(...) and returns OptimizationResult with incompatible kwargs (best_parameters, best_value, etc.)
- AI SLOP:      [ISSUE] interface assumptions do not match core optimizer contracts
- ARCHITECTURE: [FAIL] result API mismatch breaks integration with framework context/results tooling
- SAFETY:       [ISSUE] warnings/fallbacks exist, but final result path is structurally invalid
- VERDICT:      [BROKEN]
- NOTES:        needs alignment to OptimizationResult(x, fun, success, status, ...) contract

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\algorithms\gradient_based\nelder_mead.py
- CORRECTNESS:  [FAIL] same contract break: problem.evaluate(...) assumption and invalid OptimizationResult constructor usage
- AI SLOP:      [ISSUE] algorithm code is substantial but wired against the wrong core interface shape
- ARCHITECTURE: [FAIL] integration with shared optimization context is broken
- SAFETY:       [ISSUE] error handling exists, but terminal return object cannot be constructed correctly
- VERDICT:      [BROKEN]
- NOTES:        needs alignment to OptimizationResult(x, fun, success, status, ...) contract

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\core\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] export map is consistent
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\optimization\core\context.py
- CORRECTNESS:  [FAIL] factory creates some optimizers with wrong constructors/import paths (notably GA and several non-existent module paths)
- AI SLOP:      [ISSUE] advertised available algorithms include paths not implemented in this tree
- ARCHITECTURE: [FAIL] context-to-optimizer wiring is inconsistent with algorithm signatures
- SAFETY:       [ISSUE] runtime failures occur at optimizer creation/execution boundaries
- VERDICT:      [BROKEN]
- NOTES:        run_optimization() also assumes optimize signature that does not match all algorithms
