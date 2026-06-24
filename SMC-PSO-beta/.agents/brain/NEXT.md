# NEXT -- the handoff card

> Exactly one task, run with the audit loop in `brain/MIGRATION_PLAN.md`. ASCII markers only.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## Just completed (2026-06-24)
- **W-REFS reference back-fill DONE.** `brain/REFERENCES_LEDGER.md` now catalogues every reference
  across M1 (config), M2 (plant + references/), and M3 slices 1-5: 14 references (10 web-verified,
  incl. Steimann&Mayer 2005, Golub&Van Loan 2013, Higham 2002, Welch 1947, Cohen 1988, plus the
  6 W1-verified .bib refs), 3 physical-principle/benchmark rows, 2 fabricated-removed. No dangling
  proof citation keys. "Lens D -- references" added to the audit loop for all future slices.
- M3 slices 1-5 already [DONE] + accepted on main.

## -> The one next task (M3): port + AUDIT `src/utils/` -- SIXTH SLICE

Suggested sixth slice: `src/utils/monitoring/` OR `src/utils/infrastructure/` (pick the one with
fewer downstream deps first). Same loop: port faithfully (minimal/additive/anchored), Lens A (slop),
Lens B (correctness), Lens C (tests + coverage), **Lens D (references -> append to
REFERENCES_LEDGER.md)**. Dedupe vs core/ = FLAG-ONLY. Gate P0=0 / P1=0. Work on `main`, no new branch.

### Start the next chat with this
> "Read .agents/AGENTS.md + brain. M3 slices 1-5 DONE; W-REFS reference back-fill DONE. Begin M3
> sixth slice -- monitoring (or infrastructure). Show the file-level plan BEFORE writing code. Run
> Lens A/B/C plus Lens D (append any references to REFERENCES_LEDGER.md). Dedupe vs core/ = FLAG-ONLY.
> Gate P0=0/P1=0; update Audit Card + ledgers + STATE/ROADMAP/NEXT/SESSION_LOG."

## Decisions locked (2026-06-24)
- Dedupe policy: FLAG-ONLY (log overlaps as [P2] watch-items; do not consolidate this pass).
- `src/core/`, `src/optimizer/`, `src/deprecated/` are deprecated compat shims: do NOT port.
- Reference policy: harvest every reference into REFERENCES_LEDGER.md as we audit (Lens D);
  never let a fabricated citation survive (W1).

## Watch-items carried in (do NOT lose)
- GAP-1 [OPEN]: `references/undiscussed_sources/` PDFs not yet catalogued in the ledger; enumerate
  locally and add rows as their modules (mostly M5/M6) are reached.
- M2.v5 [P2/OPEN]: golden source-parity never run; run `scripts/parity_check.py --emit-golden`
  / `--compare` OR record a formal deferral in DECISIONS.md.
- F-PLANT-2, F-PLANT-3 [P2/OPEN]: revisit at M4 (DIPParams compat defaults; DIPDynamics alias).
- plant.A7 [P2/OPEN]: simplified-model inertia fudge (deferred per D9).
- UTILS-DEDUP-4 [P2/OPEN]: top-level `src/utils/seed.py` vs `testing/reproducibility/seed.py`.
- UTILS-DEDUP-5 [P2/OPEN]: `EPSILON_EXP = 700.0` duplicates saturation overflow clamp.
- S5-A3 [P2/OPEN]: return type uses builtin `any` instead of `typing.Any` in `analysis/statistics.py`.
- scipy dependency: Ensure SciPy is listed in requirements (added in reqs, confirm pinning in M1 re-audit).
