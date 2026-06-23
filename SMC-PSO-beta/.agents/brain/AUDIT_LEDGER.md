# AUDIT LEDGER -- append-only findings log

> Every problem found during migration lands here: AI-slop AND scientific defects.
> Append at the bottom; never rewrite. Close items by setting Status = FIXED (with the
> commit/branch) or WONTFIX (with justification -> also record in DECISIONS.md).
>
> Severities: [P0] scientifically wrong / unsafe  |  [P1] functional bug  |
>             [P2] slop / maintainability         |  [P3] nit
> Status: OPEN | IN_PROGRESS | FIXED | WONTFIX

| ID | Date | Module | Lens (A/B/C) | Sev | Finding (one line) | Status | Fix ref |
|----|------|--------|--------------|-----|--------------------|--------|---------|
| W1 | 2026-06-23 | references/ | B | P1? | Verify `references/proofs/` + `controllers.bib`/`config.bib` are genuine (real theorems/citations), not AI-fabricated, BEFORE using them as the Lens B oracle | OPEN | M2 |

## Summary counters (update on each session)
- Open P0: 0
- Open P1: 0 (W1 is a pending verification, not yet confirmed a defect)
- Open P2: 0
- Modules accepted to trunk: M1 (config)
