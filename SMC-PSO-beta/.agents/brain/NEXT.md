# NEXT -- the handoff card

> Exactly one task, run with the audit loop in `brain/MIGRATION_PLAN.md`. ASCII markers only.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## Just completed (2026-06-30)
- **M6 Slice 1b (PSOTuner) applied.** Ported `PSOTuner` class as a flat, beta-native module and wired its dependency on the restored `simulate_system_batch` closed-loop batched simulation.
- **M6 Slice 1a-fix applied.** Fixed missing `import logging` in `batch.py` and installed `START.md` loop protocol.
- **M6 Slice 1a applied.** Restored `simulate_system_batch` on the canonical simulation surface in `src/simulation/orchestrators/batch.py`.
- **M5 Milestone completed.** Ported classical, STA, adaptive, and hybrid SMC monoliths and wired them through a clean flat controller factory.
- Brain documents updated (`STATE.md`, `ROADMAP.md`, `AUDIT_LEDGER.md`, `SESSION_LOG.md`).

## -> The one next task (M6): port + AUDIT `src/optimization/` -- SECOND SLICE

Suggested second slice: `src/optimization/integration/pso_factory_bridge.py` port (audit-driven, same kit format).

### Start the next chat with this
> "Read .agents/brain/START.md. M6 Slice 1 (1a + 1a-fix + 1b) DONE. Begin M6 second slice -- pso_factory_bridge.py. Show the file-level plan BEFORE writing code. Run Lens A/B/C plus Lens D. Gate P0=0/P1=0; update Audit Card + ledgers + STATE/ROADMAP/NEXT/SESSION_LOG."

## Decisions locked (2026-06-30)
- Optimization Scoping: Option (A) is locked. We drop the unused "professional optimization framework" subdirectories (core, swarm, evolutionary, gradient_based, benchmarks, objectives) to keep the beta tree lean.
- Reference policy: harvest every reference into REFERENCES_LEDGER.md as we audit (Lens D).
- Dedupe policy: FLAG-ONLY (log overlaps as [P2] watch-items; do not consolidate this pass).
