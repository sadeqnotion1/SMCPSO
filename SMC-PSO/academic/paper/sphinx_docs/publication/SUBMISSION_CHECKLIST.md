# Research Paper Submission Checklist

**Document Version:** 1.0
**Date:** November 12, 2025
**Status:** OPERATIONAL
**Target:** LT-7 v2.1 Research Paper (DIP-SMC-PSO)

---

## Table of Contents

1. [Overview](#overview)
2. [Phase 1: Pre-Submission](#phase-1-pre-submission)
3. [Phase 2: Submission](#phase-2-submission)
4. [Phase 3: Post-Submission](#phase-3-post-submission)
5. [Cover Letter Template](#cover-letter-template)
6. [Suggested Reviewers](#suggested-reviewers)
7. [Response to Reviews](#response-to-reviews)

---

## Overview

This checklist ensures a complete and professional research paper submission for the DIP-SMC-PSO work (LT-7 v2.1). Follow all three phases sequentially for successful publication.

**Timeline:**
- Phase 1 (Pre-Submission): 8-12 hours
- Phase 2 (Submission): 1-2 hours
- Phase 3 (Post-Submission): 1-2 hours
- Total: 10-16 hours

**Target Venues:**
- IEEE Conference on Decision and Control (CDC) 2025
- IFAC World Congress 2026
- IEEE Transactions on Automatic Control (journal)
- Automatica (journal)

---

## Phase 1: Pre-Submission

### 1.1 Manuscript Preparation (30 items)

#### Content Validation

- [ ] **Title**: Clear, descriptive, <15 words
  - Current: "Sliding Mode Control with PSO Optimization for Double-Inverted Pendulum: A Comprehensive Study"
  - Length: 14 words [OK]

- [ ] **Abstract**: Complete, <250 words
  - Structure: Background, Methods, Results, Conclusions
  - Keywords included: SMC, PSO, DIP, Lyapunov, robustness
  - Word count validated

- [ ] **Keywords**: 5-7 keywords selected
  - Suggested: Sliding Mode Control, PSO, Double-Inverted Pendulum, Lyapunov Stability, Robustness, Adaptive Control, Optimization

- [ ] **Introduction**: Clear motivation and contributions
  - Research gap identified
  - Novelty statement explicit
  - Contributions enumerated (3-5 bullet points)

- [ ] **Related Work**: Comprehensive literature review
  - SMC history (Utkin 1977 - present)
  - PSO evolution (Kennedy & Eberhart 1995 - present)
  - DIP benchmarks (Bogdanov 2004, Muskinja 2006)
  - Gaps identified (no comprehensive SMC + PSO study for DIP)

- [ ] **Methodology**: Clear and reproducible
  - Controller equations provided (7 controllers)
  - PSO algorithm detailed (pseudocode/flowchart)
  - Simulation parameters specified (timestep, duration, initial conditions)
  - Reproducibility: 95% automation level

- [ ] **Results**: Complete and convincing
  - All 7 controllers benchmarked (100 runs each)
  - Statistical analysis (mean, std, confidence intervals)
  - Figures: 14 publication-quality plots
  - Tables: Performance comparison matrix

- [ ] **Discussion**: Thorough analysis
  - Results interpreted correctly
  - Limitations acknowledged
  - Future work identified

- [ ] **Conclusion**: Strong and concise
  - Contributions restated
  - Impact summarized
  - Recommendations provided

#### Formatting

- [ ] **Page limit**: Within conference/journal limits
  - IEEE CDC: 6 pages (+ 2 optional)
  - IFAC: 6 pages
  - IEEE TAC: 12-14 pages typical

- [ ] **Template**: Correct LaTeX template used
  - IEEE CDC: IEEEtran.cls (conference mode)
  - IEEE TAC: IEEEtran.cls (journal mode)
  - IFAC: ifacconf.cls

- [ ] **Font**: Correct font and size
  - IEEE: Times New Roman, 10pt
  - IFAC: Times New Roman, 10pt

- [ ] **Margins**: Correct margins
  - IEEE: 0.75" top/bottom, 0.625" left/right
  - IFAC: 25mm top/bottom, 20mm left/right

- [ ] **Line spacing**: Single-spaced

- [ ] **Column format**: Two-column (IEEE/IFAC)

#### Figures and Tables

- [ ] **Figure quality**: 300+ DPI
  - All 14 figures validated
  - Vector format (PDF) preferred for plots
  - Raster format (PNG) for screenshots

- [ ] **Figure captions**: Descriptive and complete
  - Format: "Fig. 1. Classical SMC performance..."
  - Self-contained (understandable without reading text)

- [ ] **Figure placement**: Correct position
  - Top/bottom of columns
  - No large white spaces
  - Referenced in text before appearance

- [ ] **Table formatting**: Professional appearance
  - Horizontal lines only (no vertical lines)
  - Centered alignment
  - Units specified in column headers

- [ ] **Color**: Accessible to color-blind readers
  - Avoid red-green combinations
  - Use patterns/markers in addition to colors
  - Verify with color-blind simulator

#### References

- [ ] **Bibliography**: Complete and formatted correctly
  - IEEE style: [1], [2], [3]...
  - No "et al." for <6 authors
  - DOI included where available

- [ ] **Citations**: All references cited in text
  - No orphan references (in bibliography but not cited)
  - No missing references (cited but not in bibliography)

- [ ] **Validation**: Citation coverage 100%
  ```bash
  python scripts/publication/validate_citations.py
  ```

- [ ] **Key references included**:
  - Utkin (1977) - SMC foundations
  - Levant (1993) - Higher-order SMC
  - Kennedy & Eberhart (1995) - PSO
  - Moreno & Osorio (2012) - Super-twisting Lyapunov
  - Project repository (this work)

#### Authors and Affiliations

- [ ] **Author names**: Correct spelling and order
  - First author = corresponding author
  - Co-authors listed in order of contribution

- [ ] **Affiliations**: Complete and accurate
  - Institution name
  - Department
  - City, Country

- [ ] **Email addresses**: Valid and professional
  - Institutional email preferred
  - Corresponding author marked with *

- [ ] **ORCID IDs**: Provided (if required)
  - Format: 0000-0001-2345-6789

#### Acknowledgments

- [ ] **Funding**: All funding sources acknowledged
  - Grant numbers specified
  - Funding agency named

- [ ] **Contributors**: Non-author contributors acknowledged
  - Code contributors
  - Data collection assistants
  - Computational resources

- [ ] **Disclaimer**: Conflict of interest statement
  - "The authors declare no conflict of interest"
  - Or disclose conflicts if present

#### Supplementary Materials

- [ ] **Code**: Repository link provided
  - GitHub: https://github.com/theSadeQ/dip-smc-pso
  - DOI: Zenodo archive (optional)
  - License: MIT/Apache 2.0

- [ ] **Data**: Datasets available
  - Benchmarks: `benchmarks/baseline_integration.csv`
  - Raw simulation data (if requested)
  - README with data dictionary

- [ ] **Videos**: Animations (optional)
  - Double pendulum simulations
  - Controller comparisons
  - YouTube/Vimeo links

### 1.2 Technical Validation (10 items)

#### LaTeX Compilation

- [ ] **Clean compilation**: No errors
  ```bash
  pdflatex paper.tex
  bibtex paper
  pdflatex paper.tex
  pdflatex paper.tex
  ```
  - Exit code: 0
  - No "undefined references"
  - No "missing citations"

- [ ] **PDF generation**: PDF created successfully
  - File size: <10MB (for arXiv)
  - All figures embedded
  - Hyperlinks functional

- [ ] **arXiv compatibility**: arXiv submission test
  ```bash
  bash scripts/publication/arxiv_submit.sh --dry-run
  ```
  - Tarball size < 10MB
  - All files included
  - LaTeX compiles on arXiv servers

#### Content Verification

- [ ] **Equations**: All equations numbered and referenced
  - Cross-references correct (\ref{eq:lyapunov})
  - No orphan equations (numbered but not referenced)

- [ ] **Algorithms**: Pseudocode clear and complete
  - PSO algorithm (Algorithm 1)
  - Controller tuning (Algorithm 2)
  - Syntax consistent

- [ ] **Notation**: Consistent throughout
  - Bold for vectors (\mathbf{x})
  - Italic for scalars (u)
  - Defined in nomenclature section

- [ ] **Units**: SI units used consistently
  - Length: meters (m)
  - Time: seconds (s)
  - Force: Newtons (N)

- [ ] **Abbreviations**: Defined at first use
  - SMC = Sliding Mode Control
  - PSO = Particle Swarm Optimization
  - DIP = Double-Inverted Pendulum

#### Proofreading

- [ ] **Grammar**: No grammatical errors
  - Use Grammarly or LanguageTool
  - Subject-verb agreement
  - Tense consistency (past for methods, present for results)

- [ ] **Spelling**: No spelling errors
  - Use spell checker
  - Technical terms verified (e.g., "Lyapunov" not "Liapunov")

### 1.3 Pre-Submission Review (5 items)

#### Internal Review

- [ ] **Self-review**: Author review complete
  - Read paper aloud
  - Check figure-text alignment
  - Verify claims supported by results

- [ ] **Co-author review**: All co-authors approved
  - All authors reviewed draft
  - Authorship order agreed
  - Affiliations confirmed

#### External Review (Optional)

- [ ] **Colleague review**: Peer feedback received
  - Ask colleague in related field
  - Address feedback before submission

- [ ] **Advisor review**: Thesis advisor approved (if applicable)

#### Final Checks

- [ ] **Conference deadlines**: Submission deadline verified
  - IEEE CDC 2025: March 15, 2025
  - IFAC 2026: October 1, 2025

---

## Phase 2: Submission (10 items)

### 2.1 Conference Portal

- [ ] **Account creation**: Portal account created
  - IEEE CDC: PaperPlaza/PaperCept
  - IFAC: IFAC-PapersOnLine
  - Email verified

- [ ] **Profile completion**: Author profile updated
  - Name, affiliation, email
  - Research interests
  - ORCID (if available)

### 2.2 Manuscript Upload

- [ ] **Title upload**: Title entered correctly
  - Exact match to PDF
  - Special characters handled (LaTeX vs plain text)

- [ ] **Abstract upload**: Abstract entered
  - Plain text format (no LaTeX)
  - Unicode for special characters (α, β, etc.)
  - <250 words

- [ ] **PDF upload**: Manuscript uploaded
  - File size <10MB
  - PDF/A format (preferred)
  - Fonts embedded

### 2.3 Metadata Entry

- [ ] **Keywords**: Keywords entered (5-7)

- [ ] **Authors**: All authors added
  - Correct order
  - Affiliations linked
  - Corresponding author designated

- [ ] **Categories**: Subject areas selected
  - Primary: Nonlinear Systems
  - Secondary: Optimal Control, Robotics

### 2.4 Supplementary Materials

- [ ] **Code upload**: GitHub repository link added
  - URL: https://github.com/theSadeQ/dip-smc-pso
  - README includes installation instructions

- [ ] **Data upload**: Datasets provided (if required)

### 2.5 Finalization

- [ ] **Copyright form**: Copyright transfer signed
  - IEEE copyright form
  - IFAC copyright form

- [ ] **Fees**: Submission fee paid (if applicable)
  - IEEE CDC: $50-100 USD
  - IFAC: Free

- [ ] **Confirmation**: Submission ID received
  - Email confirmation received
  - Submission ID recorded

---

## Phase 3: Post-Submission (10 items)

### 3.1 Immediate Actions

- [ ] **Confirmation email**: Received and verified
  - Submission ID: CDC-2025-12345
  - PDF accessible via portal

- [ ] **Co-authors notified**: All co-authors informed
  - Email with submission ID
  - Link to portal (if accessible)

### 3.2 arXiv Preprint

- [ ] **arXiv submission**: Preprint uploaded
  ```bash
  bash scripts/publication/arxiv_submit.sh
  ```
  - arXiv ID: arXiv:2511.12345
  - Categories: cs.SY, cs.RO, math.OC

- [ ] **arXiv announcement**: Preprint announced
  - Check announcement time: 8pm ET daily
  - Verify live on arXiv.org

### 3.3 Social Media and Academic Networks

- [ ] **Twitter/X announcement**: Preprint shared
  ```
  Excited to share our new preprint on arXiv!

  "Sliding Mode Control with PSO Optimization for Double-Inverted Pendulum"
  https://arxiv.org/abs/2511.12345

  We present 7 SMC controllers with formal stability proofs and
  comprehensive benchmarks.

  #ControlTheory #Robotics #Optimization #arXiv
  ```

- [ ] **ResearchGate upload**: Preprint shared
  - Upload arXiv PDF
  - Link to GitHub repository
  - Tag co-authors

- [ ] **Academia.edu upload**: Preprint shared (if applicable)

- [ ] **LinkedIn post**: Professional announcement
  - Link to arXiv preprint
  - Brief summary of contributions
  - Tag institution

### 3.4 Tracking and Follow-Up

- [ ] **Review status**: Track review progress
  - Portal status: Submitted → Under Review → Decision
  - Expected decision: 2-4 months

- [ ] **Reviewer assignments**: Check if reviewers assigned

- [ ] **Reminder**: Set calendar reminder for decision date

---

## Cover Letter Template

**File:** `docs/publication/COVER_LETTER_TEMPLATE.txt`

```
[Date]

Dear Editor-in-Chief,

Subject: Submission of Manuscript for [Conference/Journal Name]

I am pleased to submit our manuscript entitled "Sliding Mode Control with PSO
Optimization for Double-Inverted Pendulum: A Comprehensive Study" for
consideration for publication in [Conference/Journal Name].

This manuscript presents a comprehensive study of sliding mode control (SMC)
techniques applied to the double-inverted pendulum (DIP) system, with particle
swarm optimization (PSO) for gain tuning. The key contributions include:

1. Implementation and validation of seven SMC controllers (Classical SMC,
   Super-Twisting Algorithm, Adaptive SMC, Hybrid Adaptive STA-SMC, Swing-Up
   SMC, MPC, and Factory registry) with formal Lyapunov stability proofs.

2. Comprehensive benchmarks (100 runs per controller) demonstrating superior
   robustness of adaptive and hybrid controllers under high-disturbance
   environments.

3. 95% automation level for reproducibility, enabling researchers to replicate
   results with minimal effort.

4. Open-source software framework available at
   https://github.com/theSadeQ/dip-smc-pso with extensive documentation.

This work addresses a significant gap in the literature by providing the first
comprehensive comparison of SMC variants with PSO optimization for the DIP
benchmark problem. The results have important implications for industrial
applications requiring robust control under model uncertainty and disturbances.

The manuscript has not been published previously and is not under consideration
elsewhere. All authors have approved the manuscript and agree with its submission
to [Conference/Journal Name].

We suggest the following reviewers for this manuscript:

1. [Reviewer 1 Name], [Institution], [Email]
   Expertise: Sliding mode control, robust control
   Relevant publication: [Key paper]

2. [Reviewer 2 Name], [Institution], [Email]
   Expertise: PSO optimization, evolutionary algorithms
   Relevant publication: [Key paper]

3. [Reviewer 3 Name], [Institution], [Email]
   Expertise: Inverted pendulum control, benchmarks
   Relevant publication: [Key paper]

Thank you for considering our manuscript. We look forward to hearing from you.

Sincerely,

[Your Name]
[Title]
[Affiliation]
[Email]
[ORCID: 0000-0001-2345-6789]

Corresponding Author
```

---

## Suggested Reviewers

### Reviewer Selection Criteria

- **Expertise**: Relevant to SMC, PSO, or DIP control
- **Recent publications**: Active researcher (published in last 2-3 years)
- **No conflicts**: No prior collaboration (>5 years)
- **Availability**: Typically responds to review requests
- **Quality**: High-quality reviewer (constructive feedback)

### Sample Reviewer List

**Category: Sliding Mode Control**

1. **Dr. Arie Levant**
   - Affiliation: Tel Aviv University, Israel
   - Expertise: Higher-order SMC, super-twisting algorithm
   - Email: levant@post.tau.ac.il
   - Relevant publication: Levant (2003), "Higher-order sliding modes..."

2. **Dr. Jaime Moreno**
   - Affiliation: Universidad Nacional Autónoma de México, Mexico
   - Expertise: Lyapunov functions for SMC, super-twisting
   - Email: jmoreno@ii.unam.mx
   - Relevant publication: Moreno & Osorio (2012), "Strict Lyapunov functions..."

**Category: PSO Optimization**

3. **Dr. Maurice Clerc**
   - Affiliation: Independent Researcher, France
   - Expertise: PSO theory, convergence analysis
   - Email: maurice.clerc@writeme.com
   - Relevant publication: Clerc & Kennedy (2002), "The particle swarm..."

4. **Dr. Yuhui Shi**
   - Affiliation: Southern University of Science and Technology, China
   - Expertise: PSO variants, swarm intelligence
   - Email: shiyh@sustech.edu.cn
   - Relevant publication: Shi & Eberhart (1998), "A modified particle swarm..."

**Category: Inverted Pendulum Control**

5. **Dr. Naresh Bogdanov**
   - Affiliation: Portland State University, USA
   - Expertise: Optimal control, inverted pendulum benchmarks
   - Email: bogdanov@pdx.edu
   - Relevant publication: Bogdanov (2004), "Optimal Control of a Double Inverted Pendulum..."

---

## Response to Reviews

### Review Decision Types

**Accept (10%):**
- Accepted without revisions
- Extremely rare for first submission

**Minor Revisions (30%):**
- Accept conditional on minor changes
- Typical response time: 2 weeks
- High likelihood of final acceptance

**Major Revisions (40%):**
- Accept conditional on substantial revisions
- Typical response time: 1-2 months
- Requires careful addressing of reviewer concerns

**Reject (20%):**
- Manuscript rejected
- Can revise and resubmit to different venue
- Consider reviewer feedback for improvement

**Reject and Resubmit (rare):**
- Fundamental issues but promising work
- Major revisions required
- Treated as new submission after revision

### Response Letter Template

```
[Date]

Dear Editor and Reviewers,

We thank the editor and reviewers for their valuable feedback on our manuscript
"Sliding Mode Control with PSO Optimization for Double-Inverted Pendulum: A
Comprehensive Study" (Manuscript ID: CDC-2025-12345).

We have carefully addressed all comments and believe the manuscript is
significantly improved as a result. Below, we provide a detailed point-by-point
response to each reviewer comment.

=============================================================================
Reviewer 1
=============================================================================

Comment 1.1: "The paper lacks discussion of chattering mitigation techniques."

Response: We thank the reviewer for this important observation. We have added
a new subsection (Section 3.4) discussing chattering mitigation techniques,
including boundary layer implementation and super-twisting algorithm advantages.
The new content appears on pages 5-6, lines 234-278.

Changes made:
- Added Section 3.4 "Chattering Mitigation Strategies" (1.5 pages)
- Included Figure 7 showing chattering frequency comparison
- Added 5 new references on chattering [24-28]

=============================================================================
Reviewer 2
=============================================================================

Comment 2.1: "Figure 3 is difficult to read due to small font size."

Response: We have increased the font size in Figure 3 from 8pt to 10pt and
improved the legend placement for better readability.

Changes made:
- Regenerated Figure 3 with larger fonts
- Moved legend outside plot area
- Increased figure size from 3in to 4in width

=============================================================================

We believe these revisions have addressed all reviewer concerns and hope the
manuscript is now suitable for publication.

Sincerely,

[Your Name]
[Affiliation]
[Email]
```

---

**End of Submission Checklist**

**Document Version:** 1.0
**Last Updated:** November 12, 2025
**Status:** OPERATIONAL
**Total Items:** 50+ checklist items across 3 phases
