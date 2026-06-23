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

## D3 — — 
**Decision:** 
**Why:** 
