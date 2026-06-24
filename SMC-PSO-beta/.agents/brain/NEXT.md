# NEXT -- the handoff card

> Exactly one task, run with the audit loop in `brain/MIGRATION_PLAN.md`. ASCII markers only.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## -> The one next task (W-REFS): reference harvest back-fill (M1 -> M3 slice 5)

Reason this is next (owner request, 2026-06-24): the references the code relies on are needed
for the thesis bibliography, and we have NOT been collecting them -- only verifying/removing the
ones we tripped over. Build the running bibliography now, while the audited modules are fresh,
BEFORE porting more slices.

### Scope
1. Populate `brain/REFERENCES_LEDGER.md` (already seeded with M3 s1-s5 + W1-verified M1/M2 refs).
2. Exhaustive scan of every ACCEPTED module's source for citations + standard methods:
   - M1 config: `src/config/`, `config.yaml`, `requirements.txt` comments.
   - M2 plant: `src/plant/**` docstrings AND `references/proofs/*`, `references/*.bib`,
     `references/discussed_sources/`, `references/undiscussed_sources/`.
   - M3 slices 1-5: re-scan all `src/utils/**` docstrings (most already seeded).
3. For each reference: append a row (citation, file:location, what it supports, status).
   - Web-verify CITED/UNVERIF rows where cheap (Crossref/DOI/publisher) -> promote to VERIFIED.
   - Mark standard methods with no in-code cite as CANDIDATE for owner decision.
   - Record any fabricated/unverifiable citation as REMOVED-FAKE (do not re-add) -- W1 lesson.
4. Cross-check: every key cited in `references/proofs/` resolves to a real .bib entry (no danglers).

### Definition of done (gate)
- REFERENCES_LEDGER.md covers all accepted modules; 0 unresolved dangling citation keys.
- Every CITED/UNVERIF row is either promoted to VERIFIED or has a clear web-check note.
- CANDIDATE methods listed for the thesis with a suggested canonical source.
- Audit loop updated: add "Lens D -- references" so each future slice appends to the ledger.

### Start the next chat with this
> "Read .agents/AGENTS.md + brain. Run W-REFS: back-fill brain/REFERENCES_LEDGER.md by scanning
> every accepted module (M1 config, M2 plant + references/, M3 utils slices 1-5) for citations and
> standard methods. Web-verify what's cheap, mark candidates, record fabricated refs as REMOVED-FAKE,
> and resolve dangling proof citations. Then add a Lens D references step to the audit loop."

## After W-REFS
- Resume M3 slice 6 (next utils domain -- suggest `monitoring` or `infrastructure`).
- Then remaining M3 slices -> M4 controllers base + `src/simulation/`.

## Decisions locked (2026-06-24)
- Dedupe policy: FLAG-ONLY (log overlaps as [P2] watch-items; do not consolidate this pass).
- `src/core/`, `src/optimizer/`, `src/deprecated/` are deprecated compat shims: do NOT port.
- Reference policy (NEW): harvest every reference into REFERENCES_LEDGER.md as we audit;
  never let a fabricated citation survive (W1).

## Watch-items carried in (do NOT lose)
- M2.v5 [P2/OPEN]: golden source-parity never run; run `scripts/parity_check.py --emit-golden`
  / `--compare` OR record a formal deferral in DECISIONS.md.
- F-PLANT-2, F-PLANT-3 [P2/OPEN]: revisit at M4 (DIPParams compat defaults; DIPDynamics alias).
- plant.A7 [P2/OPEN]: simplified-model inertia fudge (deferred per D9).
- UTILS-DEDUP-4 [P2/OPEN]: top-level `src/utils/seed.py` vs `testing/reproducibility/seed.py`.
- UTILS-DEDUP-5 [P2/OPEN]: `EPSILON_EXP = 700.0` duplicates saturation overflow clamp.
- S5-A3 [P2/OPEN]: return type uses builtin `any` instead of `typing.Any` in `analysis/statistics.py`.
- scipy dependency: Ensure SciPy is listed in requirements (added in reqs, confirm pinning in M1 re-audit).
