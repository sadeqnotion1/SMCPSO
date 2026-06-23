# MIGRATION PLAN (audit-driven) -- SMC-PSO -> SMC-PSO-beta

> Repo: https://github.com/sadeqnotion1/smcpso  |  Source: `SMC-PSO/`  Target: `SMC-PSO-beta/`
>
> **This plan does TWO jobs at once for every module:**
> 1. **Port** it into the clean beta (dependency-first).
> 2. **Audit** it for AI-slop and **scientific/mathematical correctness** BEFORE it is
>    accepted. Nothing enters beta until it passes the gate in section 2.
>
> Working assumption (explicit): large parts of `SMC-PSO/` were AI-generated, so every
> ported file is treated as **"guilty until verified."** We are not just moving code --
> we are using the migration as a forcing function to find and fix real problems.
>
> ASCII status markers only (project rule): `[DONE] [WIP] [TODO] [BLOCKED]`.
> Finding severities: `[P0] [P1] [P2] [P3]` (defined in section 2).

---

## 0) What we are guarding against

Two failure classes, audited on every module:

**A. AI-slop / engineering defects** -- plausible-looking code that is wrong, fake, or rotten.
**B. Scientific defects** -- the control theory, physics, optimization, or statistics is
incorrect, unstable, or unjustified, even if the code "runs."

A module that runs without crashing tells us almost nothing. The bar is: *provably the
same as (or better than) the source, and scientifically defensible.*

---

## 1) Core principle -- "port, audit, prove, then accept"

For each unit of migration:

```
PORT  ->  AUDIT (A: slop, B: science)  ->  PROVE (C: tests + numeric parity)  ->  GATE  ->  ACCEPT
           |                                                                       |
           +--- findings logged to brain/AUDIT_LEDGER.md (P0..P3) ----------------+
```

No module is marked `[DONE]` in STATE.md until its **Audit Card** is filed and the gate passes.

---

## 2) Severity + the acceptance gate

| Sev | Meaning | Example | Blocks acceptance? |
|-----|---------|---------|--------------------|
| **P0** | Scientifically wrong / unsafe | Wrong equation of motion; `Vdot` not <= 0; super-twisting gains violate stability condition; PSO can return unstable gains | **YES -- must fix** |
| **P1** | Functional bug | Wrong sign, off-by-one, NaN/inf, config key code reads but doesn't exist | **YES -- must fix** |
| **P2** | Slop / maintainability | Dead code, fake/empty test, duplicated logic, docstring lies, silent `except: pass` | Fix or file a ticket; cannot accumulate |
| **P3** | Nit | Naming, formatting, minor typing | Optional |

**Acceptance gate for a module (ALL must hold):**
- [ ] `[P0] = 0` and `[P1] = 0` open.
- [ ] Numeric **parity** vs `SMC-PSO/` passes within tolerance (section 6), OR a deliberate,
      documented divergence with justification.
- [ ] Coverage gate met: overall **>= 85%**, critical **>= 95%**, safety-critical **= 100%**
      (sliding surface, switching/sat function, state validation, plant dynamics).
- [ ] Audit Card filed (template: `brain/templates/AUDIT_CARD.md`) and ledger updated.
- [ ] No new emojis / `python3` / hard-coded magic numbers that belong in `config.yaml`.

If the gate fails, the module stays in a `migration/<module>` branch -- it does NOT land on the trunk.

---

## 3) The three audit lenses (concrete checklists)

### Lens A -- AI-slop / code-quality audit (run on every file)
- [ ] **Fake completeness:** `pass`, `return None`, `...`, `raise NotImplementedError`, `# TODO`
      hiding inside something documented as finished.
- [ ] **Hallucinated APIs:** imports/attributes/kwargs that don't exist in the installed
      library version (NumPy <2.0, SciPy, PySwarms, Pydantic, Numba). Grep imports, resolve each.
- [ ] **Dead / unreachable code:** unused functions, branches that can't execute, orphaned files.
- [ ] **Duplicated logic / drift:** same math implemented twice (e.g. `src/core/` vs
      `src/simulation/`, `src/optimizer/` vs `src/optimization/`, nested `src/plant/core/`).
      Pick the canonical one; the other becomes a thin shim or is dropped.
- [ ] **Docstring/comment lies:** claims that don't match the code's actual behavior.
- [ ] **Fake tests:** `assert True`, no assertions, everything mocked so nothing real runs,
      tests that can never fail, snapshot tests with no baseline.
- [ ] **Silent failures:** bare `except:` / `except Exception: pass`, swallowed errors.
- [ ] **Config drift:** keys read in code but missing from `config.yaml` (and unused keys).
- [ ] **Magic numbers:** physical or tuning constants hard-coded instead of in `config.yaml`.
- [ ] **Type honesty:** type hints that don't match real return values.

### Lens B -- Scientific / mathematical correctness audit (per module type)

**Plant / DIP dynamics (`src/plant/`)**
- [ ] Equations of motion match the cited reference (see section 6b): mass matrix `M(q)`,
      Coriolis/centrifugal `C(q,qdot)`, gravity `G(q)`. `M(q)` must be **symmetric and
      positive-definite**.
- [ ] **Energy check:** with zero input and zero friction, total mechanical energy is
      conserved over a sim (within integrator tolerance). This catches most dynamics bugs.
- [ ] Equilibria correct (upright/down); linearization eigenvalues have the expected
      unstable/stable structure; small-angle behavior matches a linear pendulum.
- [ ] Simplified and low-rank models are documented **approximations** of the full model,
      with the assumption stated and the error bounded vs the full model.
- [ ] Units consistent (SI) throughout; parameters trace back to `config.yaml` physics block.

**Controllers (`src/controllers/`)**
- [ ] **Sliding surface** `s` defined correctly (e.g. `s = lambda*e + edot`) with positive gains.
- [ ] **Reaching condition / Lyapunov:** with `V = 0.5*s^2`, show `Vdot <= -eta*|s|`
      (or finite-time reaching) -- verify analytically AND numerically (sample states, check sign).
- [ ] **Chattering control** (classical): boundary-layer `sat(s/phi)` / `tanh(s/phi)` correct;
      quantify residual chattering with a chattering index.
- [ ] **Super-twisting (`sta_smc`)**: algorithm is the true STA form
      (`u = -k1*|s|^0.5*sign(s) + v`, `vdot = -k2*sign(s)`); gains satisfy the stability
      inequalities relative to the disturbance Lipschitz bound.
- [ ] **Adaptive (`adaptive_smc`)**: adaptation law is bounded; includes leakage/projection
      so gains can't drift to infinity; stability of the combined law shown.
- [ ] **Hybrid (`hybrid_adaptive_sta_smc`)**: switching logic well-defined, no Zeno behavior,
      continuity/initialization handled.
- [ ] Gain **positivity / bound constraints** enforced; actuator **saturation** modeled;
      controller degrades safely at saturation.

**Optimization (`src/optimization/`)**
- [ ] Fitness function is well-posed (ISE/IAE/ITAE/composite) and **penalizes instability
      and constraint violation** -- not just tracking error.
- [ ] Gain **search bounds** are physically sensible; PSO respects them (no out-of-bounds gains).
- [ ] **Reproducibility:** fixed seed => identical result; results are not cherry-picked.
- [ ] No **evaluation leakage** (same IC/disturbance set used to both tune and "validate");
      hold-out scenarios exist.
- [ ] Convergence is real (monitor best-cost curve), not a flat line from a broken objective.

**Numerics (cross-cutting)**
- [ ] Integrator stated (e.g. RK4) and timestep within its stability region for the dynamics.
- [ ] **Numba path == pure-Python path** numerically (parity test), or the gap is documented.
- [ ] No `NaN`/`inf` over long runs; state/energy stays bounded; deterministic with seed.

**Statistics / analysis (`src/analysis/`)**
- [ ] Confidence intervals / t-tests state and meet their assumptions; Welch used for unequal var.
- [ ] Monte Carlo sample size justified; multiple-comparison correction where needed.
- [ ] Claimed metrics (settling time, overshoot, ISE) computed by their textbook definitions.

### Lens C -- tests + numeric parity (proof)
- [ ] Port/author real tests with real assertions; meet the coverage gate.
- [ ] **Parity harness** (section 6) passes for the module.
- [ ] Property-based tests (Hypothesis) encode the invariants above (`M` PD, `Vdot<=0`,
      energy bounded, gains in-bounds).

---

## 4) Per-module workflow (the loop you run every time)

1. **Branch:** `migration/<module>` off the beta trunk.
2. **Port:** copy from `SMC-PSO/` to the matching canonical path (`src/simulation/`,
   `src/optimization/` -- NOT the deprecated `src/core/`, `src/optimizer/`).
3. **Lens A** pass -> log slop findings.
4. **Lens B** pass -> log scientific findings; for each, cite the equation/reference it should match.
5. **Fix P0/P1**, then **Lens C**: write/port tests, run the parity harness, hit coverage.
6. **File the Audit Card**, update `brain/AUDIT_LEDGER.md`, update `STATE.md`.
7. **Gate** (section 2). If green, merge to trunk and mark `[DONE]`. If not, stay on the branch.
8. **WRAP_UP**: STATE / NEXT / SESSION_LOG / graph.

---

## 5) Milestones (dependency-first, with the modules the old plan MISSED)

> The previous plan covered ~8 of ~13 source modules. The interfaces/HIL, analysis,
> benchmarks, and integration modules were missing and are added here.

- **M1 -- Environment & config** `[DONE]` -- requirements, setup, `config.yaml`, `src/config/`.
  - Re-audit: confirm dependency **pins** (esp. `numpy<2.0` for Numba) and that Pydantic
    schema rejects unknown keys; no secrets committed.
- **M2 -- Plant dynamics (FULL model first)** `[WIP]` `src/plant/` -- port + audit the **full
  nonlinear model** from `src/plant/models/` (+ `core/`, `parameters/`). Simplified/low-rank
  variants are **deferred** to a later pass (owner decision D9).
  - Science gate: `M(q)` symmetric PD, energy-conservation test, equilibria/linearization,
    code matches `references/proofs/` (section 6b).
  - Also build the shared **parity harness** here.
- **M3 -- Utils & primitives** `[TODO]` `src/utils/` -- types, validation, logging, metrics, viz.
  - Audit: dedupe vs `core/`; verify metric definitions (ISE/IAE/ITAE) before controllers use them.
- **M4 -- Controllers base + simulation core** `[TODO]` `src/controllers/base.py`, `src/simulation/`.
  - Science gate: integrator correctness + energy/parity on an uncontrolled drop test;
    one full end-to-end sim runs.
- **M5 -- Controller implementations** `[TODO]` classical / sta / adaptive / hybrid + `factory.py`.
  - Science gate: Lyapunov/reaching per controller, STA gain conditions, adaptive boundedness,
    chattering index, saturation behavior. Highest-scrutiny milestone.
- **M6 -- Optimization** `[TODO]` `src/optimization/` (PSO + objectives + validation).
  - Science gate: fitness penalizes instability, bounds respected, seed-reproducible, hold-out.
- **M7 -- Interfaces / HIL** `[TODO]` `src/interfaces/` (HIL server/client, test-automation).
  - **(MISSING from old plan.)** Needed before entry points, since `simulate.py --run-hil`
    depends on it. Audit latency monitoring + safe-stop on deadline miss.
- **M8 -- Analysis** `[TODO]` `src/analysis/` (statistics, metrics, comparison).
  - **(MISSING from old plan.)** Statistical-correctness audit (Lens B stats section).
- **M9 -- Entry points** `[TODO]` `simulate.py`, `streamlit_app.py`.
  - Audit: every CLI flag/UI control maps to working code; HIL flag works (needs M7).
- **M10 -- Benchmarks** `[TODO]` `src/benchmarks/` (+ decide on `src/integration/`, `src/assets/`).
  - **(MISSING from old plan.)** Confirm benchmarks measure what they claim; pin baselines.
- **M11 -- Verification suite & gates** `[TODO]` `tests/` full suite, coverage gates, CI.
  - Wire `.pytest.ini` / `.coveragerc`; CI runs parity + property tests on every push.
- **Follow-up -- plant simplified/low-rank** `[TODO]` -- after M2, port + audit the reduced
  models, bounding their error against the verified full model.

> Skipped on purpose: `src/core/`, `src/optimizer/`, `src/deprecated/` (compat shims).
> Root `src/__init__.py` + `src/ARCHITECTURE.md` come across with M4 and are audited then.

---

## 6) Cross-cutting scientific validation harness (build once, in M2)

A small `scripts/parity_check.py` (beta) + golden baselines so every later module can prove parity:

- **Golden trajectories:** for fixed seeds, ICs, and gains, run the SAME scenario in
  `SMC-PSO/` and `SMC-PSO-beta/`; assert state trajectories match within `rtol/atol`.
- **Invariant tests (Hypothesis):** `M(q)` PD for random `q`; energy bounded; `Vdot<=0`
  sampled across the state space; PSO gains always within bounds.
- **Analytical anchors:** equilibria, linearized eigenvalues, small-angle limit.
- **Long-run stability:** N-second sim with no NaN/inf and bounded state/energy.
- **Numba-vs-Python parity:** same inputs, both code paths, assert equal within tolerance.

This harness IS the definition of "verified" referenced by the gate.

## 6b) Where the reference math lives -- and why it ALSO gets audited

The repo ships its own references (the Lens B oracle):
- `references/proofs/` -- stability / correctness proofs.
- `references/controllers.bib` -- controller citations.
- `references/config.bib` -- config/parameter citations.
- `references/README.md`, plus `discussed_sources/` and `undiscussed_sources/`.

**Critical caveat (ledger W1):** because the repo was AI-generated, these proofs and citations
may themselves be **fabricated** (hallucinated theorems, citations to papers that don't exist or
don't say what is claimed). So before using them as the correctness oracle:
- [ ] Spot-check each `.bib` entry resolves to a real publication that actually supports the claim.
- [ ] Read each proof in `references/proofs/` for logical validity, not just presence.
- [ ] Where a reference is unverifiable, mark the dependent code as **unverified** (not wrong),
      and prefer an independent textbook derivation as the oracle instead.

Never let an AI-written proof certify AI-written code without an independent check.

---

## 7) Tooling to make the audit cheap
- Static: `ruff`/`flake8`, `mypy` (honest types), `vulture` (dead code), `radon` (complexity),
  `pip-audit` (vuln deps). Run in CI.
- Slop greps: `grep -rn "except:\|except Exception: *pass\|TODO\|NotImplementedError\|assert True"`.
- Coverage: `pytest --cov=src` with thresholds in `.coveragerc`.
- CI gate: lint + types + parity + property tests must pass before merge to trunk.

---

## 8) Deliverables & tracking
- `brain/AUDIT_LEDGER.md` -- append-only list of findings (id, module, severity, status, fix).
- One **Audit Card** per module (`brain/templates/AUDIT_CARD.md`).
- `STATE.md` phase table reflects only **gated** completion.
- `DECISIONS.md` records any deliberate divergence from the source (and why).

---

## 9) Honest limitations
- I can read the repo (read-only) but **cannot run code or push** from here -- you (or a local
  AI agent following this plan) execute the harness and commit. The gates are written so a
  local run produces objective pass/fail.
- "Scientifically defensible" still needs **your domain sign-off** on the reference equations
  and the controller stability conditions; this plan structures that review, it doesn't replace it.
