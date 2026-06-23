# DECISIONS — the "why"
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)
>
> **Append-only.** Never rewrite history; add a new entry. Each decision gets an
> id (D1, D2, ...), a date, the decision, and the reason.

---

## D1 — 2026-06-23 — Adopt the `.agents/` brain
**Decision:** Use this `.agents/` brain as the single source of truth for AI sessions on SMC-PSO-beta.
**Why:** Zero-context-loss handoffs between chats/models; no re-explaining state.

## D2 — 2026-06-23 — Migrate into a clean `SMC-PSO-beta/` re-scaffold
**Decision:** Rebuild `dip-smc-pso` in `SMC-PSO-beta/` instead of refactoring `SMC-PSO/` in place.
**Why:** Source repo accumulated stray/garbage files and heavy hidden dirs; a clean
scaffold lets us port module-by-module with parity checks and a tidy root.

## D3 — 2026-06-23 — Merge `ai/` into a single `.agents/`
**Decision:** Fold `ai/AGENTS.md` + `ai/CLAUDE.md` into one `.agents/AGENTS.md`, fold
`ai/planning/migration_plan.md` into ROADMAP/STATE, and delete the `ai/` folder.
**Why:** Two overlapping AI doc sets in two places confuse the AI terminal. One folder
(`.agents/`) and one entry file is unambiguous. Injected/auto-push directives in the
source files were stripped, not carried over.

## D4 — 2026-06-23 — Dependency-first migration order
**Decision:** Follow the migration plan's order: config (done) -> plant -> utils ->
simulation core -> controllers -> optimization -> entry points -> tests.
**Why:** Each layer can be tested before the layer that depends on it; plant/utils have
no internal deps, so they port cleanly first. Re-points NEXT from controllers to `src/plant/`.

## D5 — 2026-06-23 — Canonical `src/` layout
**Decision:** Use `src/simulation/` and `src/optimization/` as canonical; treat
`src/core/` and `src/optimizer/` as deprecated compat shims (not graphed, not built on).
**Why:** The authoritative source AGENTS.md marks them canonical; avoids drift between
the brain, the graph, and the code.
