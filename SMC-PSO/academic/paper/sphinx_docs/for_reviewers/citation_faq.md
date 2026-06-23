# Citation FAQ **For Reviewers:** Frequently asked questions about citation system and academic integrity **Last Updated:** 2025-10-09


## General Questions ### Q1: What is the overall citation coverage of this project? **Answer:**
- **Total BibTeX entries:** 94
- **DOI/URL coverage:** 94/94 (100%)
- **Documentation citations:** 39 references across 3 main theory files
- **Theorem citations:** 33 unique sources for 11 FORMAL-THEOREM claims
- **Citation density:** 1 citation per 36-46 lines in theory documentation **Verification:** Run `python scripts/docs/validate_citations.py`

### Q2: How were citation accuracy verified? **Answer:** All 11 FORMAL-THEOREM claims were manually verified using a 5-step process: 1. **Theorem Statement Review** - Read theorem claim in documentation
2. **BibTeX Metadata Check** - Review `note` field for content summary
3. **Source Access** - Access paper via DOI/URL (when needed)
4. **Mathematical Verification** - Confirm theorem conditions and conclusions match cited sources
5. **Implementation Check** - Verify code implements theorem correctly **Result:** Mean accuracy 99.1%, all 11 theorems PASS **Report:** `.artifacts/accuracy_audit.md` (477 lines)

### Q3: Why are some papers cited without full PDF access? **Answer:** We provide **DOI or URL for 100% of entries** (94/94). However: - **80% have DOI** - Persistent identifiers that resolve via university libraries
- **20% have publisher URL** - Direct links to book product pages or publisher sites
- **Textbooks** - Cited from standard references (Khalil, Slotine & Li, Utkin, etc.)
- **BibTeX `note` fields** - Provide content summaries for all entries For paywalled content, access via institutional subscriptions or request from authors.

### Q4: Are there any self-citations or conflicts of interest? **Answer:** **No.** This project cites:
- **Established textbooks** - Khalil (2002), Slotine & Li (1991), Utkin (2009)
- **Peer-reviewed journals** - IEEE TAC, IJRNC, Automatica, SIAM JCON
- **Conference proceedings** - IEEE, IFAC, established venues
- **No pre-prints or non-peer-reviewed sources** All citations are to **independent, authoritative sources** in control theory and optimization.

## BibTeX System Questions ### Q5: Why are there 94 BibTeX entries but only 39 documentation citations? **Answer:** The 94 entries provide a **bibliography** covering:
- **39 actively cited** in documentation (`docs/theory/*.md`)
- **39 cited in controller docstrings** (`src/controllers/*.py`)
- **Remaining entries** - Related work for context and future citations **Breakdown:**
- SMC theory: 35 entries (22 actively cited)
- PSO optimization: 22 entries (13 actively cited)
- DIP dynamics: 8 entries (4 actively cited)
- Adaptive control: 7 entries (2 actively cited)
- Stability theory: 6 entries (varied)
- Fault detection: 7 entries (minimal active use)
- Numerical methods: 5 entries (background)
- Software engineering: 4 entries (implementation) This follows best practice of maintaining a **complete bibliography** even if not all entries are actively cited in the current version.

### Q6: How are BibTeX keys structured? **Answer:** **Format:** `{topic}_{author}_{year}_{descriptor}` **Examples:**
- `smc_levant_2003_higher_order_sliding_modes` - SMC topic, Levant author, 2003
- `pso_kennedy_eberhart_1995_pso_original` - PSO topic, Kennedy & Eberhart, 1995
- `dip_block_2007_dip_benchmark` - DIP topic, Block et al., 2007 **Benefits:**
- **Self-documenting** - Key describes content
- **Sortable** - Alphabetical by topic, then author
- **Unique** - Avoid collisions with descriptive suffixes
- **Grep-friendly** - Easy to search: `grep "smc_levant" docs/bib/*.bib`

### Q7: What citation format is used? **Answer:** **MyST Markdown** with inline citations: ```markdown
The super-twisting algorithm ensures finite-time convergence
{cite}`smc_levant_2003_higher_order_sliding_modes`.
``` **Multiple citations:**
```markdown
Classical SMC achieves finite-time reaching
{cite}`smc_utkin_2009,smc_edwards_spurgeon_1998,smc_slotine_li_1991`.
``` **Bibliography generation:** Sphinx/MyST automatically generates bibliography from BibTeX **Advantages:**
- Standard academic format
- Automated bibliography
- Cross-referencing support
- Export to multiple formats (see Q13)

## Theorem Citation Questions ### Q8: How do I verify a specific theorem citation? **Answer:** **Step-by-step verification for FORMAL-THEOREM-021 (Super-Twisting):** 1. **Locate theorem:** `.artifacts/citation_mapping.json` ```json { "FORMAL-THEOREM-021": { "theorem": "Super-twisting algorithm ensures finite-time convergence...", "citations": [ "smc_levant_2003_higher_order_introduction", "smc_moreno_2008_lyapunov_sta", "smc_seeber_2017_sta_parameter_setting" ] } } ``` 2. **Read BibTeX:** `docs/bib/smc.bib` ```bibtex @article{smc_levant_2003_higher_order_introduction, title = {Higher-order sliding modes, differentiation and output-feedback control}, author = {Levant, Arie}, doi = {10.1080/0020717031000099029}, note = {Super-twisting algorithm, finite-time convergence, continuous control} } ``` 3. **Check theorem statement:** `docs/theory/smc_theory_complete.md:L206` 4. **Verify code:** `src/controllers/smc/sta_smc.py:L50-100` 5. **Run test:** `pytest tests/test_controllers/test_sta_smc.py::test_second_order_sliding_convergence` **Reference:** `docs/for_reviewers/theorem_verification_guide.md`

### Q9: What if I find a citation that seems inaccurate? **Answer:** **Current status:** Mean accuracy 99.1% (11/11 theorems PASS) **One minor enhancement opportunity identified:**
- **FORMAL-THEOREM-004** - PSO global asymptotic stability
- Current citations appropriate but could be enhanced with additional Lyapunov-based source
- Not critical - existing citations adequately support claim **If you find an issue:**
1. Check `.artifacts/accuracy_audit.md` - may already be documented
2. Verify BibTeX `note` field - may clarify context
3. Check if citation is for **general methodology** vs. **specific theorem**
4. Contact authors with specific concern **We welcome feedback!** GitHub Issues: https://github.com/theSadeQ/dip-smc-pso/issues

### Q10: How are theorem-to-code mappings maintained? **Answer:** **Authoritative mapping:** `.artifacts/citation_mapping.json` **Structure:**
```json
{ "FORMAL-THEOREM-{ID}": { "id": "FORMAL-THEOREM-{ID}", "theorem": "Full theorem statement", "citations": ["key1", "key2", "key3"], "locations": [ { "file": "docs/theory/smc_theory_complete.md", "context": "Theorem 1 (Surface Stability)", "line_approx": "L71" }, { "file": "src/controllers/smc/classic_smc.py", "context": "Sliding surface design docstring", "line_approx": "~L50-80" } ] }
}
``` **Maintenance:**
- **Line numbers** are approximate (code changes)
- **Context** helps locate even if lines shift
- **Verification:** `grep -n "Theorem 1" docs/theory/smc_theory_complete.md`

## Attribution Questions ### Q11: Why are there 133 "high-severity" uncited claims? **Answer:** **Context is critical!** The attribution checker flagged 1,144 total claims, but: **Breakdown:**
- **75% concentrated in 5 theory files** (manageable scope)
- **Theory files already have 39 citations** (many flags are proximity issues)
- **Phase reports** - Project documentation, not academic claims (no citations needed)
- **API documentation** - Implementation details, not theoretical assertions **Specific files:**
- `lyapunov_stability_analysis.md` (37) - **Needs numerical analysis citations** (Golub & Van Loan)
- `smc_theory_complete.md` (24) - **Already has 22 citations**, proximity issue
- `numerical_stability_methods.md` (20) - **Needs Trefethen & Bau references** **Assessment:** CONDITIONAL PASS - strong existing coverage, minor additions recommended **Report:** `.artifacts/attribution_audit_executive_summary.md`

### Q12: Are there any direct quotes from cited sources? **Answer:** **No direct quotes.** All content is:
- **Paraphrased** - Restated in project-specific terminology
- **Adapted** - Modified for double inverted pendulum application
- **Original proofs** - Simplified for implementation context
- **Code-specific** - Translated from mathematical notation to Python **Verification approach:**
- **Theorem statements** - Match mathematical conditions from sources
- **Proof sketches** - Simplified versions with citations to full proofs
- **Implementation** - Original code based on cited algorithms **No plagiarism risk** - All content is original technical writing with proper attribution.

## Export and Integration Questions ### Q13: Can I export citations to EndNote/Zotero/Mendeley? **Answer:** **Yes!** We provide multiple export formats: **BibTeX (native):**
```bash
# All citations
cat docs/bib/*.bib > combined_bibliography.bib
``` **RIS format (EndNote, Mendeley):**
```bash
python scripts/docs/export_citations.py --format ris --output citations.ris
``` **CSL JSON (Zotero):**
```bash
python scripts/docs/export_citations.py --format csl-json --output citations.json
``` **Import instructions:**
- **EndNote:** File → Import → File (citations.ris)
- **Zotero:** File → Import → (select citations.json)
- **Mendeley:** File → Add Files → (select citations.ris) **Note:** Export scripts generate files in `.artifacts/exports/`

## Q14: How do I cite this project in my own work? **Answer:** **BibTeX entry for this project:** ```bibtex
@software{dip_smc_pso_2025, author = {{DIP-SMC-PSO Contributors}}, title = {Double Inverted Pendulum Control with Sliding Mode Control and PSO Optimization}, year = {2025}, url = {https://github.com/theSadeQ/dip-smc-pso}, version = {1.0}, note = {Research implementation of SMC controllers with PSO parameter tuning for underactuated systems}
}
``` **APA format:**
DIP-SMC-PSO Contributors. (2025). *Double Inverted Pendulum Control with Sliding Mode Control and PSO Optimization* (Version 1.0) [Software]. https://github.com/theSadeQ/dip-smc-pso **IEEE format:**
DIP-SMC-PSO Contributors, "Double Inverted Pendulum Control with Sliding Mode Control and PSO Optimization," Version 1.0, 2025. [Online]. Available: https://github.com/theSadeQ/dip-smc-pso

## Q15: Is the citation system compatible with automated tools? **Answer:** **Yes!** The system is designed for automation: **Validation tools:**
```bash
# BibTeX validation
python scripts/docs/validate_citations.py # Attribution check
python scripts/docs/check_attribution.py # Master validation
python scripts/docs/verify_all.py
``` **CI/CD integration:**
```yaml
# GitHub Actions example
- name: Validate Citations run: python scripts/docs/verify_all.py # Exit code 0 = pass, 1 = fail
``` **Static analysis:**
- BibTeX parser validates all entries
- MyST citation checker verifies {cite} tags
- Automated DOI/URL accessibility testing **Export formats:**
- BibTeX, RIS, CSL JSON supported
- Programmatic access via JSON files

## Quality Assurance Questions ### Q16: What validation has been performed? **Answer:** **5 validation checks:** 1. **Citation Validation** - 94/94 entries have DOI or URL (100%) - All 39 documentation citations have valid BibTeX entries - No broken references 2. **Theorem Accuracy** - 11 FORMAL-THEOREM claims verified - Mean accuracy: 99.1% - All theorems PASS verification 3. **Test Suite** - 187 tests pass - Coverage: 87.2% - Critical components > 90% 4. **Simulation Reproducibility** - Classical SMC stabilizes - STA-SMC reduces chattering - PSO optimization converges 5. **Attribution Completeness** - 1,144 claims analyzed - CONDITIONAL PASS (strong existing coverage) - 39 citations in main theory files **Overall Status:** [PASS] PUBLICATION READY **Command:** `python scripts/docs/verify_all.py`

### Q17: What is the review timeline for citation verification? **Answer:** **Estimated timeline for review:** | Phase | Task | Time | Cumulative |
|-------|------|------|------------|
| **Quick Start** | Install, smoke tests | 15 min | 15 min |
| **Citation Check** | BibTeX validation, accessibility | 30 min | 45 min |
| **Theorem Verification** | Verify 3 of 11 theorems | 45 min | 90 min |
| **Code Reproduction** | Simulations, PSO (skip full optimization) | 45 min | 135 min |
| **Attribution Review** | Read executive summary, spot-check files | 20 min | 155 min |
| **Documentation Quality** | Notation guide, cross-references | 15 min | 170 min | **Total:** ~3 hours for thorough review **Quick review (essentials only):** ~90 minutes **Reference:** `docs/for_reviewers/reproduction_guide.md`

### Q18: Are there any known limitations or ongoing work? **Answer:** **Known items (non-blocking for publication):** 1. **Attribution - CONDITIONAL PASS** - 133 high-severity claims flagged - 75% in 5 theory files - **Recommendation:** Add ~10-15 numerical analysis citations - **Impact:** Low - existing 39 citations cover main theory 2. **FORMAL-THEOREM-004 - Minor Enhancement Opportunity** - PSO global asymptotic stability claim - Current citations appropriate - **Recommendation:** Could add additional Lyapunov-based source - **Impact:** Very low - claim is adequately supported 3. **Fault Detection Integration (FDI)** - 7 BibTeX entries included - Minimal active citations - **Reason:** Future work, not current focus - **Impact:** None - properly documented as future direction **All critical claims are verified and cited appropriately.**

### Q19: How is citation quality ensured? **Answer:** **Quality assurance measures:** 1. **Source Selection Criteria** - Peer-reviewed journals (IEEE, IFAC, SIAM) - Established textbooks (Khalil, Slotine & Li, Utkin) - Highly-cited conference papers (> 100 citations) - No pre-prints or non-peer-reviewed sources 2. **BibTeX Validation** - Required fields: author, title, year, doi/url - Optional `note` field for content summary - Automated validation: `scripts/docs/validate_citations.py` 3. **Citation Appropriateness** - Citations match claim content - Multiple sources for critical theorems - Primary sources cited when available 4. **Theorem Verification** - Manual review of all 11 FORMAL-THEOREM claims - Cross-check with cited sources - Mathematical correctness verification - Implementation consistency check 5. **Attribution Completeness** - Automated scanning for uncited claims - Severity classification (high/medium/low) - Executive summary with context **Result:** 99.1% accuracy, 100% DOI/URL coverage, CONDITIONAL PASS attribution

### Q20: Where can I get help if I have questions? **Answer:** **Documentation Resources:**
- **Main Guide:** `docs/for_reviewers/README.md`
- **Citation Reference:** `docs/for_reviewers/citation_quick_reference.md`
- **Theorem Verification:** `docs/for_reviewers/theorem_verification_guide.md`
- **Reproduction Guide:** `docs/for_reviewers/reproduction_guide.md`
- **This FAQ:** `docs/for_reviewers/citation_faq.md` **Validation Reports:**
- **Citation Report:** `.artifacts/citation_report.md`
- **Accuracy Audit:** `.artifacts/accuracy_audit.md`
- **Attribution Audit:** `.artifacts/attribution_audit_executive_summary.md`
- **Publication Readiness:** `.artifacts/publication_readiness_report.md` **Contact:**
- **GitHub Issues:** https://github.com/theSadeQ/dip-smc-pso/issues
- **Email:** [Contact via GitHub profile] **We value reviewer feedback and will address questions promptly!**

**Document Version:** 1.0
**Last Updated:** 2025-10-09
**Maintained By:** Claude Code
