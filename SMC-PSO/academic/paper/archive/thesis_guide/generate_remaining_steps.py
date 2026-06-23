#!/usr/bin/env python
"""
Generate remaining step files for Days 24-30 of thesis guide.
This script creates ~40 step files following the established pattern.
"""

import os
from pathlib import Path

BASE_DIR = Path("D:/Projects/main/.artifacts/thesis_guide")

# Template for standard step file
def create_step_file(
    day_dir: str,
    filename: str,
    step_num: int,
    title: str,
    time_hours: float,
    output_desc: str,
    source_files: str,
    objective: str,
    next_step: str,
    page_count: int = 0,
    special_notes: str = ""
):
    """Create a step file with standard structure."""

    content = f"""# Step {step_num}: {title}

**Time**: {time_hours} hour{'s' if time_hours != 1 else ''}
**Output**: {output_desc}
**Source**: {source_files}

---

## OBJECTIVE

{objective}

---

## SOURCE MATERIALS TO READ FIRST ({int(time_hours * 0.25 * 60)} min)

### Primary Sources
1. **Read**: Relevant project documentation
2. **Review**: Previous chapter outputs
3. **Check**: Automation scripts available

{special_notes}

---

## EXACT PROMPT TO USE

### Copy This Into Your AI Assistant:

```
Write {output_desc} for the thesis.

Context:
- Master's thesis on "Sliding Mode Control of Double-Inverted Pendulum with PSO"
- Audience: Control systems engineering researchers/professors
- Format: LaTeX, IEEE citation style
- Tone: Formal academic (NO conversational language)

Structure ({page_count} pages total):

[DETAILED STRUCTURE BASED ON SECTION TYPE]

Citation Requirements:
- Use IEEE format: cite:AuthorYear
- Support all claims with references
- Cross-reference earlier chapters

Mathematical Notation:
- Use LaTeX math mode consistently
- Define all symbols
- Number equations appropriately

Quality Checks:
- NO conversational language ("Let's", "We can see")
- NO vague claims without quantification
- YES specific statements with citations
- YES technical precision

Length: {page_count} pages (12pt font, 1-inch margins)
```

---

## WHAT TO DO WITH THE OUTPUT

### 1. Review and Edit ({int(time_hours * 0.3 * 60)} min)

Check for:
- [ ] Academic tone maintained
- [ ] Specific claims (no vague "comprehensive")
- [ ] Proper citations throughout
- [ ] Mathematical notation correct
- [ ] Smooth transitions between paragraphs

### 2. Format as LaTeX ({int(time_hours * 0.2 * 60)} min)

Save to appropriate location in `thesis/` directory.

### 3. Test Compile ({int(time_hours * 0.1 * 60)} min)

```bash
cd thesis
pdflatex main.tex
```

Verify no compilation errors.

---

## VALIDATION CHECKLIST

Before moving to next step:

### Content Quality
- [ ] Task objective achieved
- [ ] All required components present
- [ ] Citations appropriate
- [ ] No placeholder text (TBD, TODO)

### LaTeX Quality
- [ ] Compiles without errors
- [ ] Cross-references work
- [ ] Formatting consistent
{'- [ ] Page count: ' + str(page_count-1) + '-' + str(page_count+1) + ' pages' if page_count > 0 else ''}

---

## TIME CHECK

Total estimated: {time_hours} hours
- Reading: {int(time_hours * 0.25 * 60)} min
- Prompt generation: {int(time_hours * 0.05 * 60)} min
- Review: {int(time_hours * 0.3 * 60)} min
- Formatting: {int(time_hours * 0.2 * 60)} min
- Compile/test: {int(time_hours * 0.1 * 60)} min

---

## NEXT STEP

{next_step}

---

**[OK] Ready to proceed!**
"""

    filepath = BASE_DIR / day_dir / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath

# Generate all Day 24-30 files
def generate_all_files():
    files_created = []

    # Day 24: Chapter 14 - Future Work (remaining files)
    day24_files = [
        ("step_02_section_14_1_intro.md", 2, "Write Section 14.1 - Introduction", 1, "Section 14.1 (1 page)",
         "Brainstorming output from Step 1", "Write 1-page introduction previewing 4 future research directions",
         "Proceed to: `step_03_section_14_2_advanced_controllers.md`", 1),
        ("step_03_section_14_2_advanced_controllers.md", 3, "Write Section 14.2 - Advanced Controllers", 2, "Section 14.2 (2 pages)",
         "Literature on Terminal SMC, Integral SMC", "Describe 3 advanced SMC variants worth investigating",
         "Proceed to: `step_04_section_14_3_mpc_integration.md`", 2),
        ("step_04_section_14_3_mpc_integration.md", 4, "Write Section 14.3 - MPC Integration", 2, "Section 14.3 (2 pages)",
         "MPC literature, hybrid control papers", "Propose SMC-MPC hybrid architecture for constrained control",
         "Proceed to: `step_05_section_14_4_hardware_validation.md`", 2),
        ("step_05_section_14_4_hardware_validation.md", 5, "Write Section 14.4 - Hardware Validation", 2, "Section 14.4 (2 pages)",
         "Quanser DIP documentation", "Outline hardware implementation plan with specific platform recommendations",
         "Proceed to: `step_06_section_14_5_multi_objective.md`", 2),
        ("step_06_section_14_5_multi_objective.md", 6, "Write Section 14.5 - Multi-Objective Optimization", 2, "Section 14.5 (2 pages)",
         "Pareto optimization literature", "Propose multi-objective PSO for energy-efficient control",
         "Proceed to: `step_07_compile_chapter.md`", 2),
        ("step_07_compile_chapter.md", 7, "Compile and Verify Chapter 14", 0.5, "Complete Chapter 14 PDF (9-10 pages)",
         "All Section 14.x files", "Compile Chapter 14, verify structure, fix errors",
         "Proceed to: Day 25 - Chapter 15 (Conclusions)", 0),
    ]

    for file_data in day24_files:
        filepath = create_step_file("day_24_chapter14", *file_data)
        files_created.append(str(filepath))

    # Day 25: Chapter 15 - Conclusions
    day25_files = [
        ("step_01_synthesize_contributions.md", 1, "Synthesize Key Contributions", 1, "Organized contribution list",
         "All previous chapters", "Review thesis and extract 5-7 key contributions",
         "Proceed to: `step_02_section_15_1_summary.md`", 0),
        ("step_02_section_15_1_summary.md", 2, "Write Section 15.1 - Summary", 1.5, "Section 15.1 (2 pages)",
         "Synthesized contributions", "Write 2-page thesis summary hitting all major points",
         "Proceed to: `step_03_section_15_2_contributions.md`", 2),
        ("step_03_section_15_2_contributions.md", 3, "Write Section 15.2 - Contributions", 2, "Section 15.2 (3 pages)",
         "Contribution list from Step 1", "Detail 7 specific contributions with evidence from results",
         "Proceed to: `step_04_section_15_3_conclusions.md`", 3),
        ("step_04_section_15_3_conclusions.md", 4, "Write Section 15.3 - Conclusions", 1.5, "Section 15.3 (2 pages)",
         "Thesis results chapters", "Draw conclusions from experimental validation and analysis",
         "Proceed to: `step_05_section_15_4_final_remarks.md`", 2),
        ("step_05_section_15_4_final_remarks.md", 5, "Write Section 15.4 - Final Remarks", 1, "Section 15.4 (1 page)",
         "Entire thesis", "Write impactful closing paragraph connecting research to broader impact",
         "Proceed to: `step_06_compile_chapter.md`", 1),
        ("step_06_compile_chapter.md", 6, "Compile and Verify Chapter 15", 0.5, "Complete Chapter 15 PDF (8-10 pages)",
         "All Section 15.x files", "Compile Chapter 15, verify formatting, validate closing",
         "Proceed to: Day 26 - Appendices", 0),
    ]

    for file_data in day25_files:
        filepath = create_step_file("day_25_chapter15", *file_data)
        files_created.append(str(filepath))

    # Day 26: Appendices
    day26_files = [
        ("step_01_appendix_a_code.md", 1, "Appendix A - Code Listings", 2, "Appendix A (3-4 pages)",
         "src/controllers/", "Select 3-4 key controller implementations to include as code listings",
         "Proceed to: `step_02_appendix_b_derivations.md`", 4),
        ("step_02_appendix_b_derivations.md", 2, "Appendix B - Mathematical Derivations", 2, "Appendix B (4-5 pages)",
         "docs/theory/", "Include detailed derivations omitted from main chapters",
         "Proceed to: `step_03_appendix_c_parameters.md`", 5),
        ("step_03_appendix_c_parameters.md", 3, "Appendix C - Parameter Tables", 1, "Appendix C (2 pages)",
         "config.yaml", "Create comprehensive parameter tables for all controllers",
         "Proceed to: `step_04_appendix_d_data.md`", 2),
        ("step_04_appendix_d_data.md", 4, "Appendix D - Extended Data Tables", 1.5, "Appendix D (3 pages)",
         "optimization_results/", "Include full experimental data tables not in main chapters",
         "Proceed to: `step_05_appendix_e_user_guide.md`", 3),
        ("step_05_appendix_e_user_guide.md", 5, "Appendix E - Software User Guide", 2, "Appendix E (3-4 pages)",
         "README.md, docs/guides/", "Write user guide for running simulations and optimization",
         "Proceed to: `step_06_compile_appendices.md`", 4),
        ("step_06_compile_appendices.md", 6, "Compile All Appendices", 0.5, "All appendices compiled",
         "All appendix files", "Compile appendices, verify formatting, check references",
         "Proceed to: Day 27 - Bibliography", 0),
    ]

    for file_data in day26_files:
        filepath = create_step_file("day_26_appendices", *file_data)
        files_created.append(str(filepath))

    # Day 27: Bibliography
    day27_files = [
        ("step_01_extract_citations.md", 1, "Extract Citations from All Chapters", 1, "Complete citation list",
         "All .tex files", "Run extract_bibtex.py to collect all cite commands from thesis",
         "Proceed to: `step_02_organize_by_topic.md`", 0),
        ("step_02_organize_by_topic.md", 2, "Organize Bibliography by Topic", 1.5, "Organized .bib file",
         "Extracted citations", "Organize 80-120 references into SMC, PSO, DIP, Control Theory sections",
         "Proceed to: `step_03_format_bibtex.md`", 0),
        ("step_03_format_bibtex.md", 3, "Format and Validate BibTeX", 1.5, "Clean .bib file",
         "Organized bibliography", "Format all BibTeX entries consistently, validate with bibtex",
         "Proceed to: `step_04_compile_bibliography.md`", 0),
        ("step_04_compile_bibliography.md", 4, "Compile Bibliography", 0.5, "Rendered bibliography",
         "Formatted .bib file", "Run pdflatex + bibtex + pdflatex pipeline",
         "Proceed to: `step_05_verify_citations.md`", 0),
        ("step_05_verify_citations.md", 5, "Verify All Citations Resolve", 1, "Citation validation report",
         "Compiled PDF", "Check for undefined citations, fix missing entries",
         "Proceed to: Day 28 - Build & Review", 0),
    ]

    for file_data in day27_files:
        filepath = create_step_file("day_27_bibliography", *file_data)
        files_created.append(str(filepath))

    # Day 28: Build & Review
    day28_files = [
        ("step_01_full_compilation.md", 1, "Full Thesis Compilation", 1, "Complete PDF (all chapters)",
         "All thesis files", "Run complete build pipeline from scratch",
         "Proceed to: `step_02_check_page_count.md`", 0),
        ("step_02_check_page_count.md", 2, "Verify Page Count Target", 0.5, "Page count report",
         "Compiled PDF", "Verify 180-220 pages, adjust if needed",
         "Proceed to: `step_03_verify_figures.md`", 0),
        ("step_03_verify_figures.md", 3, "Verify All 60 Figures", 1, "Figure verification checklist",
         "Compiled PDF", "Check all figures render correctly, high resolution",
         "Proceed to: `step_04_verify_tables.md`", 0),
        ("step_04_verify_tables.md", 4, "Verify All 30 Tables", 1, "Table verification checklist",
         "Compiled PDF", "Verify all tables formatted properly, data accurate",
         "Proceed to: `step_05_check_citations.md`", 0),
        ("step_05_check_citations.md", 5, "Check Citation Integrity", 0.5, "Citation integrity report",
         "Compiled PDF + .log", "Verify no undefined citations, bibliography complete",
         "Proceed to: `step_06_fix_compilation_errors.md`", 0),
        ("step_06_fix_compilation_errors.md", 6, "Fix Any Compilation Errors", 2, "Error-free compilation",
         "Compilation logs", "Systematically fix all warnings and errors",
         "Proceed to: Day 29 - Polish & Proofread", 0),
    ]

    for file_data in day28_files:
        filepath = create_step_file("day_28_build_review", *file_data)
        files_created.append(str(filepath))

    # Day 29: Polish & Proofread
    day29_files = [
        ("step_01_spell_check.md", 1, "Spell Check Entire Thesis", 1.5, "Spell-checked thesis",
         "Complete PDF/tex files", "Run spell checker, fix all typos",
         "Proceed to: `step_02_grammar_check.md`", 0),
        ("step_02_grammar_check.md", 2, "Grammar Check with Tools", 2, "Grammar-checked thesis",
         "Spell-checked files", "Use Grammarly/LanguageTool for grammar validation",
         "Proceed to: `step_03_check_consistency.md`", 0),
        ("step_03_check_consistency.md", 3, "Check Terminology Consistency", 1.5, "Consistency report",
         "Entire thesis", "Verify terminology consistent (controller names, variable definitions)",
         "Proceed to: `step_04_verify_formatting.md`", 0),
        ("step_04_verify_formatting.md", 4, "Verify IEEE Style Compliance", 1.5, "Style compliance report",
         "IEEE style guide", "Check formatting matches IEEE thesis requirements",
         "Proceed to: `step_05_check_ai_patterns.md`", 0),
        ("step_05_check_ai_patterns.md", 5, "Detect AI Patterns", 1, "AI pattern report",
         "All .tex files", "Run detect_ai_patterns.py, fix conversational language",
         "Proceed to: `step_06_final_read_through.md`", 0),
        ("step_06_final_read_through.md", 6, "Final Complete Read-Through", 2, "Final validation",
         "Complete thesis PDF", "Read entire thesis start-to-finish for final quality check",
         "Proceed to: Day 30 - Final Submission", 0),
    ]

    for file_data in day29_files:
        filepath = create_step_file("day_29_polish", *file_data)
        files_created.append(str(filepath))

    # Day 30: Final Submission
    day30_files = [
        ("step_01_final_compilation.md", 1, "Final Compilation (All Fixes Applied)", 1, "Final PDF",
         "Polished thesis files", "Compile final version with all corrections",
         "Proceed to: `step_02_generate_pdfa.md`", 0),
        ("step_02_generate_pdfa.md", 2, "Generate PDF/A for Archiving", 1, "PDF/A compliant file",
         "Final PDF", "Convert to PDF/A format for long-term archiving",
         "Proceed to: `step_03_prepare_defense_slides.md`", 0),
        ("step_03_prepare_defense_slides.md", 3, "Prepare Defense Presentation", 3, "Beamer presentation (60 slides)",
         "Thesis chapters", "Create 45-minute defense presentation",
         "Proceed to: `step_04_create_submission_package.md`", 0),
        ("step_04_create_submission_package.md", 4, "Create Submission Package", 1, "Submission archive",
         "Final PDF + source", "Package PDF, source, data for submission",
         "Proceed to: `step_05_backup_everything.md`", 0),
        ("step_05_backup_everything.md", 5, "Backup All Files", 0.5, "Triple backup complete",
         "Entire thesis project", "Create 3 backups: local, cloud, external drive",
         "Proceed to: `step_06_celebrate.md`", 0),
        ("step_06_celebrate.md", 6, "You Did It! Celebration Guide", 0.5, "Well-deserved celebration",
         "Your completed thesis!", "Celebrate your massive achievement!",
         "You're done! Submit your thesis!", 0),
    ]

    for file_data in day30_files:
        filepath = create_step_file("day_30_final", *file_data)
        files_created.append(str(filepath))

    return files_created

if __name__ == "__main__":
    files = generate_all_files()
    print(f"[OK] Created {len(files)} step files")
    print("\nFiles created by day:")

    days = {}
    for f in files:
        day = Path(f).parent.name
        days[day] = days.get(day, 0) + 1

    for day, count in sorted(days.items()):
        print(f"  {day}: {count} files")

    print("\n[OK] All Days 24-30 step files generated!")
