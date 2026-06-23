# .artifacts/ - Runtime Outputs and Research Archive

**Purpose:** Runtime artifacts, research outputs, and archived historical data

**Created:** December 17, 2025
**Maintained By:** Workspace organization automation

---

## Directory Structure

### archive/
Historical artifacts and archived documentation
- `temp_docs_2025-12-16/` - Archived temporary markdown docs from workspace cleanup
- `pso_logs/` - Archived PSO optimization logs
- `completed_tasks/` - Archived research task outputs (LT-4, MT-5, QW-2)
- `backups/` - Backup files (*.backup, *BACKUP*)

### qa_audits/
Quality assurance audit deliverables
- `CA-01_CONTROLLER_SIMULATION_AUDIT/` - Controller simulation audit
- `CA-02_MEMORY_MANAGEMENT_AUDIT/` - Memory management audit
- `MA-01_GUIDES_AUDIT_2025-11-10/` - Guides audit
- `MA-02_HYBRID_ADAPTIVE_STA_SMC_2025-11-10/` - Hybrid adaptive STA-SMC audit

### research/
Research outputs (papers, experiments, phases)
- `papers/` - Research papers and publications
  - `LT7_journal_paper/` - LT-7 SUBMISSION-READY research paper
- `experiments/` - Research experiments and analysis
  - `MT6_boundary_layer/` - MT-6 boundary layer optimization
  - `MT7_robust_pso/` - MT-7 robust PSO validation
  - `MT8_disturbance_rejection/` - MT-8 disturbance rejection
  - `LT6_model_uncertainty/` - LT-6 model uncertainty analysis
  - `archive/` - Completed tasks (LT-4, MT-5, QW-2)
- `phases/` - Research phase experiments
  - `phase2_experiments/` - Phase 2 experimental data
  - `phase3_experiments/` - Phase 3 experimental data
  - `phase4_experiments/` - Phase 4 experimental data (includes 7.4MB PSO log)
  - `investigations/` - Special investigations (zero variance, etc.)
- `optimization_results/` - PSO optimization baseline data

### testing/
Test summaries and quality gates status
- `archive/` - Archived old test summaries by month
- `quality_gates_status.json` - Current quality gates status
- `test_summary_*.json` - Recent test run summaries

### thesis/
LaTeX thesis source and PDFs (moved from root for workspace cleanliness)
- Full thesis directory structure preserved
- Contains: chapters/, figures/, bibliography/, sources_archive/ (96MB PDFs)
- Build artifacts: main.pdf (707KB), main.tex, LaTeX auxiliary files

### thesis_guide/
30-day thesis writing guide structure

### Root Files
- `production_readiness.db` (90KB) - Production readiness tracking database
- `CA-02_PRODUCTION_READINESS_CHECKLIST.md` (28KB) - Production checklist
- `CA-02_VICTORY_SUMMARY.md` (21KB) - CA-02 audit summary

---

## Archival Policy

### Test Summaries
- Archive after 30 days
- Keep most recent quality_gates_status.json at testing/ root
- Monthly archives in `testing/archive/YYYY-MM/`

### Research Outputs
- Archive completed tasks after 1 month of completion
- SUBMISSION-READY papers remain in `research/papers/` for easy access
- Phase experiments archived when phase concludes

### QA Audits
- Retain indefinitely for compliance
- Never delete audit deliverables

### Thesis
- Active development location (moved from root)
- Build artifacts cleaned periodically (*.aux, *.bbl, *.blg, *.log)
- PDF outputs preserved

---

## Size Guidelines

**Target:** <100MB total for .artifacts/

**Current Breakdown:**
- thesis/: ~98MB (LaTeX thesis + PDFs)
- research/: ~19MB (papers, experiments, phases)
- qa_audits/: ~932KB (audit deliverables)
- archive/: ~2.2MB (temp docs, archived data)
- testing/: ~36KB (test summaries)
- Other: ~137KB (production readiness data)

**Total:** ~121MB (exceeds target, monitor thesis/ size)

---

## Maintenance

### Weekly
- Check .artifacts/ total size: `du -sh .artifacts/`
- Review for stale data (files >90 days old)

### Monthly
- Archive old test summaries to `testing/archive/YYYY-MM/`
- Clean thesis build artifacts
- Review research outputs for archival candidates

### Quarterly
- Audit QA deliverables for completeness
- Consolidate old phase experiments
- Update this README if structure changes

---

**Last Updated:** December 17, 2025
**Workspace Organization:** Professional grade structure (CLAUDE.md compliant)
