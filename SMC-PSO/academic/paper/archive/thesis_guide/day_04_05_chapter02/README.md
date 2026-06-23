# DAYS 4-5: Chapter 2 - Literature Review

**Time**: 16 hours over 2 days
**Output**: 18-20 pages
**Difficulty**: Hard (extensive reading + synthesis)

---

## OVERVIEW

Days 4-5 create the literature review chapter, surveying the research landscape of double-inverted pendulum control, sliding mode control theory, and particle swarm optimization. This is one of the most time-intensive chapters because it requires reading, synthesizing, and citing 30+ papers.

**Why This Matters**: Literature review demonstrates you understand the field and positions your work within existing research.

---

## OBJECTIVES

By end of Day 5, you will have:

1. [ ] Section 2.1: History of inverted pendulum control (4 pages)
2. [ ] Section 2.2: Sliding mode control theory overview (4 pages)
3. [ ] Section 2.3: Particle swarm optimization fundamentals (3 pages)
4. [ ] Section 2.4: Related work on DIP-SMC systems (4 pages)
5. [ ] Section 2.5: Literature gaps and thesis positioning (3 pages)
6. [ ] 2-3 comparison tables (existing approaches vs. this work)
7. [ ] 30+ citations properly formatted

---

## TIME BREAKDOWN (2 DAYS)

### Day 4 (8 hours)

| Step | Task | Time | Output |
|------|------|------|--------|
| 1 | Extract existing literature review | 3 hours | Base content |
| 2 | Write Section 2.1 (Inverted pendulum) | 2 hours | 4 pages |
| 3 | Write Section 2.2 (SMC theory) | 2 hours | 4 pages |
| 4 | Build and verify | 1 hour | Day 4 progress check |

### Day 5 (8 hours)

| Step | Task | Time | Output |
|------|------|------|--------|
| 1 | Write Section 2.3 (PSO) | 2 hours | 3 pages |
| 2 | Write Section 2.4 (Related work) | 3 hours | 4 pages |
| 3 | Write Section 2.5 (Gaps) | 2 hours | 3 pages |
| 4 | Create comparison tables | 1 hour | 2-3 tables |
| 5 | Integrate and polish | 1 hour | Complete chapter |

**Total**: 16 hours → 18-20 pages

---

## STEPS

### Day 4 Steps

#### Step 1: Extract Existing Literature Review (3 hours)
**File**: `day4_step_01_extract_existing.md`
- Read `docs/thesis/chapters/02_literature_review.md` (253 lines)
- Convert to LaTeX using md_to_tex.py
- Identify gaps to fill

#### Step 2: Write Section 2.1 - Inverted Pendulum History (2 hours)
**File**: `day4_step_02_section_2_1_inverted.md`
- Survey pendulum control from 1960s to present
- Single pendulum → double pendulum → triple pendulum
- Classical control → modern nonlinear control
- 8-10 citations

#### Step 3: Write Section 2.2 - SMC Theory Overview (2 hours)
**File**: `day4_step_03_section_2_2_smc.md`
- SMC fundamentals (Utkin 1977)
- Robustness properties
- Chattering problem
- Higher-order sliding modes (STA, HOSM)
- 10-12 citations

#### Step 4: Day 4 Build Check (1 hour)
**File**: `day4_step_04_polish.md`
- Compile what you have
- Verify citations work
- Check page count (~8 pages so far)

### Day 5 Steps

#### Step 1: Write Section 2.3 - PSO Fundamentals (2 hours)
**File**: `day5_step_01_section_2_3_pso.md`
- PSO algorithm (Kennedy & Eberhart 1995)
- Convergence properties
- Parameter selection
- Applications to control tuning
- 8-10 citations

#### Step 2: Write Section 2.4 - Related Work (3 hours)
**File**: `day5_step_02_section_2_4_related.md`
- Survey 15+ papers on DIP control
- Group by approach: PID, LQR, MPC, SMC, neural, fuzzy
- Compare performance metrics
- Identify what's missing

#### Step 3: Write Section 2.5 - Literature Gaps (2 hours)
**File**: `day5_step_03_section_2_5_gaps.md`
- Synthesize what literature lacks
- Position this thesis contribution
- Connect to Chapter 1 contributions

#### Step 4: Create Comparison Tables (1 hour)
**File**: `day5_step_04_tables.md`
- Table 2.1: SMC variants comparison
- Table 2.2: DIP control approaches comparison
- Table 2.3: PSO tuning studies comparison

#### Step 5: Integrate and Polish (1 hour)
**File**: `day5_step_05_integrate.md`
- Ensure smooth transitions between sections
- Verify all citations present
- Check for redundancy

---

## SOURCE FILES

### Primary Source (253 lines - excellent starting point!)
- `docs/thesis/chapters/02_literature_review.md`
  - Already structured with SMC, PSO, DIP sections
  - ~50% of chapter content exists

### Secondary Sources

**For Section 2.1 (Inverted Pendulum)**:
- Fantoni & Lozano (2001) - Nonlinear Control for Underactuated Mechanical Systems
- Åström & Furuta (2000) - Swinging up a pendulum by energy control
- Survey papers on pendulum control benchmarks

**For Section 2.2 (SMC Theory)**:
- `docs/theory/smc_theory_complete.md` (~1,200 lines)
- `docs/guides/theory/smc-theory.md`
- Utkin (1977, 1992) - Original SMC papers
- Levant (1993, 2005) - Higher-order sliding modes
- Edwards & Spurgeon (1998) - Sliding Mode Control book

**For Section 2.3 (PSO)**:
- `docs/theory/pso_optimization_complete.md`
- `docs/pso_convergence_theory.md`
- Kennedy & Eberhart (1995) - Original PSO paper
- Shi & Eberhart (1998) - Inertia weight
- Clerc & Kennedy (2002) - Constriction factor

**For Section 2.4 (Related Work)**:
- `docs/CITATIONS_ACADEMIC.md` (39 references)
- Search Google Scholar: "double inverted pendulum sliding mode control"
- Recent papers (2015-2024) on DIP control

**For Section 2.5 (Gaps)**:
- `.project/ai/planning/research/RESEARCH_COMPLETION_SUMMARY.md`
- Your own contributions from completed research tasks

---

## EXPECTED OUTPUT

### Section 2.1: Inverted Pendulum (4 pages)
- Historical timeline: 1960s classical → 2024 learning-based
- Benchmark evolution: single → double → triple
- Control challenges: underactuated, nonlinear, unstable
- 8-10 citations

### Section 2.2: SMC Theory (4 pages)
- Fundamentals: sliding surface, reaching phase, sliding phase
- Robustness properties: matched disturbance rejection
- Chattering: causes, consequences, mitigation
- Advanced SMC: STA, adaptive, hybrid
- 10-12 citations

### Section 2.3: PSO (3 pages)
- Algorithm description: particles, velocity, position updates
- Convergence theory: exploration vs. exploitation
- Parameter selection: w, c1, c2
- Control tuning applications
- 8-10 citations

### Section 2.4: Related Work (4 pages)
- Survey organized by control approach:
  - PID/LQR (classical linear methods)
  - MPC (model predictive control)
  - SMC (existing DIP-SMC papers)
  - Intelligent (neural, fuzzy, adaptive)
- Comparison of performance metrics
- 15+ citations

### Section 2.5: Gaps (3 pages)
- What's missing in literature:
  - Comprehensive SMC variant comparison on DIP
  - Systematic PSO tuning for SMC gains
  - Chattering mitigation analysis
  - Robustness under realistic disturbances
- How this thesis addresses gaps
- Preview of contributions

### Comparison Tables
- Table 2.1: SMC Variants (Classical, STA, Adaptive, Hybrid)
- Table 2.2: DIP Control Approaches (10+ papers, metrics)
- Table 2.3: PSO Tuning Studies (5+ papers, parameters)

---

## VALIDATION CHECKLIST

### Day 4 End (after 8 hours):
- [ ] Sections 2.1-2.2 written (~8 pages)
- [ ] 18-20 citations so far
- [ ] Compiles without errors
- [ ] At least 1 comparison table drafted

### Day 5 End (after 16 hours total):
- [ ] All 5 sections complete (18-20 pages)
- [ ] 30+ citations properly formatted
- [ ] 2-3 comparison tables present
- [ ] Smooth transitions between sections
- [ ] No duplicate citations
- [ ] All cited papers accessible (for committee review)

### Content Quality
- [ ] Every paragraph has at least 1 citation
- [ ] No unsupported claims ("It is well-known..." needs cite)
- [ ] Technical accuracy (correct equations, parameter definitions)
- [ ] Chronological coherence (don't cite 2024 before 1977)

### Citations
- [ ] IEEE format: \cite{Utkin1977}
- [ ] All entries in bibliography/papers.bib
- [ ] No "Citation undefined" warnings
- [ ] Full citation info (author, title, journal, year, pages)

### Tables
- [ ] Booktabs format (\toprule, \midrule, \bottomrule)
- [ ] Caption and label (\caption{...} \label{tab:...})
- [ ] Referenced in text ("Table 2.1 shows...")
- [ ] No overfull boxes (table fits page width)

---

## TROUBLESHOOTING

### Too Many Papers to Read

**Problem**: 50+ relevant papers found, can't read all
**Solution**:
- Read abstracts first (5 min each)
- Identify 15 most relevant (read intro + conclusion)
- Cite 5 others from abstract only
- Focus on papers comparing multiple approaches

### Missing Citations

**Problem**: Can't access some papers behind paywall
**Solution**:
- Use Google Scholar for preprints/author copies
- Check ResearchGate, arXiv
- Email authors directly
- University library access
- Cite from secondary sources if necessary

### Section Redundancy

**Problem**: Section 2.2 (SMC theory) overlaps with Chapter 5
**Solution**:
- Chapter 2: High-level overview, historical context
- Chapter 5: Deep mathematical detail, proofs, implementation
- Rule: If it has equations, save for Chapter 5

### Inconsistent Terminology

**Problem**: Some papers say "chattering", others "switching noise"
**Solution**:
- Choose one term, use consistently
- Note alternatives: "...chattering (also called switching noise)..."
- Add to nomenclature

---

## TIME MANAGEMENT

### If Behind Schedule

At end of Day 4, only 6 pages done (target: 8):
- **Option 1**: Extend to 2.5 days (add 4 hours to Day 5)
- **Option 2**: Reduce Section 2.4 from 4 pages to 3 pages
- **Option 3**: Compress Section 2.1 (less historical detail)

### If Ahead of Schedule

At end of Day 4, 10 pages done (target: 8):
- **Option 1**: Take longer break, review quality
- **Option 2**: Start Day 5 work early (Section 2.3)
- **Option 3**: Add extra comparison table

---

## NEXT STEPS

Once Day 5 checklist is complete:

1. Review entire Chapter 2 (30 min read-through)
2. Check citation diversity (not all from 1-2 authors)
3. Verify no AI patterns (run detection script)
4. Read `day_06_chapter03/README.md` (10 min)

**Day 6**: Write Chapter 3 - Problem Formulation (10-12 pages)

---

## ESTIMATED COMPLETION TIME

- **Beginner** (first literature review): 18-20 hours
- **Intermediate** (some review experience): 14-16 hours
- **Advanced** (familiar with DIP/SMC literature): 12-14 hours

**This is the hardest chapter** - Literature reviews require extensive reading and synthesis. Budget extra time if needed.

---

**[OK] Ready for the literature deep dive? Open `day4_step_01_extract_existing.md`!**
