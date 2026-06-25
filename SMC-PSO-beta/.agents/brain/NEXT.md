# NEXT -- the handoff card

> Exactly one task, run with the audit loop in `brain/MIGRATION_PLAN.md`. ASCII markers only.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## Just completed (2026-06-25)
- **M3 Slice 6 (monitoring) applied.** Ported `src/utils/monitoring/` and `src/utils/infrastructure/threading/` (AtomicCounter dependency) from source, updated requirements for `psutil`. 26 tests passed.
- **M3 Slice 7 (infrastructure: logging + memory) applied.** Ported `src/utils/infrastructure/logging/` and `src/utils/infrastructure/memory/` and widened `infrastructure/__init__.py` to expose logging, memory, and threading. 41 tests passed.
- Bumped package version to `0.5.0-m3slice7`.
- Brain documents updated (`STATE.md`, `ROADMAP.md`, `AUDIT_LEDGER.md`, `SESSION_LOG.md`).

## -> The one next task (M3): port + AUDIT `src/utils/` -- EIGHTH SLICE

Suggested eighth slice: `src/utils/visualization/` port (audit-driven, same kit format).

### Start the next chat with this
> "Read .agents/AGENTS.md + brain. M3 slices 1-7 DONE. Begin M3 eighth slice -- visualization. Show the file-level plan BEFORE writing code. Run Lens A/B/C plus Lens D (append any references to REFERENCES_LEDGER.md). Dedupe vs core/ = FLAG-ONLY. Gate P0=0/P1=0; update Audit Card + ledgers + STATE/ROADMAP/NEXT/SESSION_LOG."

## Decisions locked (2026-06-25)
- Dedupe policy: FLAG-ONLY (log overlaps as [P2] watch-items; do not consolidate this pass).
- `src/core/`, `src/optimizer/`, `src/deprecated/` are deprecated compat shims: do NOT port.
- Reference policy: harvest every reference into REFERENCES_LEDGER.md as we audit (Lens D); never let a fabricated citation survive (W1).

## New watch-items from slice 7
- INFRA-LOG-1 [P2]: decide on default log directory (`academic/logs` vs `logs/`) before any production log run; or document the LOG_DIR override.
- INFRA-LOG-DEPR-1 [P3]: schedule `datetime.utcfromtimestamp` -> timezone-aware replacement during a future hardening pass (affects JSON + Metric formatters).
- INFRA-MEM-1 [P3]: if MemoryPool gets broader use, consider returning an (index, array) handle from get_block to remove the caller-tracking burden.

## New watch-items from slice 6
- MON-LAT-1 [P2]: maintainer decision on deadline-miss threshold inconsistency (`dt*margin` vs `dt`).
- MON-LENSA-1 [P2]: bare `except:` in visualization.py matplotlib style setup.
- MON-EMOJI-1 / MON-UNICODE-1 [P3]: clean up unicode emojis and non-ASCII math glyphs.
- MON-PROV-1 [P3]: decide coverage_monitoring provenance rebrand (`theSadeQ/dip-smc-pso` -> `sadeqnotion1/SMCPSO`).

## Carried watch-items (unchanged)
- GAP-1 [OPEN]: `references/undiscussed_sources/` PDFs not yet catalogued in the ledger; enumerate locally and add rows as their modules (mostly M5/M6) are reached.
- M2.v5 [P2/OPEN]: golden source-parity never run; run `scripts/parity_check.py --emit-golden` / `--compare` or record a formal deferral in DECISIONS.md.
- F-PLANT-2, F-PLANT-3 [P2/OPEN]: revisit at M4 (DIPParams compat defaults; DIPDynamics alias).
- plant.A7 [P2/OPEN]: simplified-model inertia fudge (deferred per D9).
- UTILS-DEDUP-4 [P2/OPEN]: top-level `src/utils/seed.py` vs `testing/reproducibility/seed.py`.
- UTILS-DEDUP-5 [P2/OPEN]: `EPSILON_EXP = 700.0` duplicates saturation overflow clamp.
- S5-A3 [P2/OPEN]: return type uses builtin `any` instead of `typing.Any` in `analysis/statistics.py`.
- scipy pinning: Ensure SciPy is listed in requirements (added in reqs, confirm pinning in M1 re-audit).
