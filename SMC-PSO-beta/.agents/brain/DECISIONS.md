# DECISIONS -- the "why"
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)
>
> **Append-only.** Never rewrite history; add a new entry. Each decision gets an
> id (D1, D2, ...), a date, the decision, and the reason.

---

## D1 -- 2026-06-23 -- Adopt the `.agents/` brain
**Decision:** Use this `.agents/` brain as the single source of truth for AI sessions on SMC-PSO-beta.
**Why:** Zero-context-loss handoffs between chats/models; no re-explaining state.

## D2 -- 2026-06-23 -- Migrate into a clean `SMC-PSO-beta/` re-scaffold
**Decision:** Rebuild `dip-smc-pso` in `SMC-PSO-beta/` instead of refactoring `SMC-PSO/` in place.
**Why:** Source repo accumulated stray/garbage files and heavy hidden dirs; a clean
scaffold lets us port module-by-module with parity checks and a tidy root.

## D3 -- 2026-06-23 -- Merge `ai/` into a single `.agents/`
**Decision:** Fold `ai/AGENTS.md` + `ai/CLAUDE.md` into one `.agents/AGENTS.md`, fold
`ai/planning/migration_plan.md` into ROADMAP/STATE, and delete the `ai/` folder.
**Why:** Two overlapping AI doc sets in two places confuse the AI terminal. Injected/auto-push
directives in the source files were stripped, not carried over.

## D4 -- 2026-06-23 -- Dependency-first migration order
**Decision:** config (done) -> plant -> utils -> simulation core -> controllers ->
optimization -> interfaces/HIL -> analysis -> entry points -> benchmarks -> tests.
**Why:** Each layer is testable before the layer that depends on it.

## D5 -- 2026-06-23 -- Canonical `src/` layout
**Decision:** `src/simulation/` and `src/optimization/` are canonical; `src/core/`,
`src/optimizer/`, `src/deprecated/` are deprecated shims -- not ported, not built on.
**Why:** The authoritative source AGENTS.md marks them canonical; avoids drift.

## D6 -- 2026-06-23 -- Audit-driven migration (port is NOT enough)
**Decision:** The migration is also an audit. Every module is checked on two lenses --
(A) AI-slop/code defects and (B) scientific/mathematical correctness -- and proven by
(C) numeric parity + tests before acceptance. Gate: P0 = 0, P1 = 0, parity pass, coverage met,
Audit Card filed. See `brain/MIGRATION_PLAN.md` + `brain/AUDIT_LEDGER.md`.
**Why:** The repo was largely AI-generated; "it runs" does not mean it is correct. The owner
wants AI-slop and scientific-correctness problems found and fixed during the migration, not later.

## D7 -- 2026-06-23 -- Added the modules the old plan missed
**Decision:** Add explicit milestones for `src/interfaces/` (HIL), `src/analysis/`, and
`src/benchmarks/` (and a decision point on `src/integration/`, `src/assets/`).
**Why:** The original migration plan covered ~8 of ~13 real source modules; HIL especially
is a dependency of `simulate.py --run-hil`, so omitting it would break the entry points.

## D8 -- 2026-06-23 -- ASCII status markers only (fix our own slop)
**Decision:** Use ASCII markers (`[DONE] [WIP] [TODO] [BLOCKED]`, `[P0..P3]`) in all brain
files; removed the Unicode check-emojis that earlier STATE/ROADMAP versions used.
**Why:** The project's own hard rule forbids Unicode emojis (Windows cp1252 terminals).

## D9 -- 2026-06-23 -- Plant: full nonlinear model first
**Decision:** In M2, port + audit the **full nonlinear DIP model first**; defer the simplified
and low-rank models to a later pass.
**Why:** Owner choice. The full model is the correctness reference for the approximations, so
verifying it first gives a baseline the simplified/low-rank models can later be checked against.

## D10 -- 2026-06-23 -- Reference math sourced from the repo, but audited itself
**Decision:** Use `references/proofs/` + `references/controllers.bib` + `references/config.bib`
as the Lens B oracle for the dynamics/controller math -- but **validate those references are
genuine** (real theorems, real citations) before trusting them. Findings tracked in AUDIT_LEDGER (W1).
**Why:** Owner noted the references may be in the AI-fetched repo. Because the repo is
AI-generated, the proofs/citations themselves may be fabricated and cannot be trusted blindly.
