# DAY 29: Content Polish and Consistency Check

**Time**: 8 hours
**Output**: Publication-ready thesis (final draft)
**Difficulty**: Moderate (detail-oriented)

---

## OVERVIEW

Day 29 transforms the "working draft" from Day 28 into a "publication-ready" thesis. Focus on consistency, tone, formatting, and eliminating AI-generated language patterns.

**Why This Matters**: The difference between a "complete" thesis and an "excellent" thesis is polish. Day 29 brings yours from good to great.

---

## OBJECTIVES

By end of Day 29, you will have:

1. [ ] AI patterns removed (<5 per chapter)
2. [ ] Notation consistent throughout
3. [ ] Academic tone verified (no conversational language)
4. [ ] Figure and table quality verified
5. [ ] Math notation consistent
6. [ ] Spelling and grammar checked
7. [ ] Ready for final validation (Day 30)

---

## TIME BREAKDOWN

| Step | Task | Time | Output |
|------|------|------|--------|
| 1 | Run AI pattern detection | 1 hour | Pattern report |
| 2 | Remove AI patterns manually | 2 hours | Clean chapters |
| 3 | Consistency check (notation) | 2 hours | Uniform notation |
| 4 | Figure/table quality review | 1 hour | Publication quality |
| 5 | Grammar and spell check | 1 hour | Error-free text |
| 6 | Final compile and verify | 1 hour | Polished PDF |
| **TOTAL** | | **8 hours** | **Publication-ready** |

---

## STEPS

### Step 1: Run AI Pattern Detection (1 hour)
**File**: `step_01_ai_detection.md`
- Use: `python scripts/docs/detect_ai_patterns.py`
- Run on all 15 chapters
- Generate report: `ai_patterns_report.txt`
- Target: <5 patterns per chapter (75 total max)

### Step 2: Remove AI Patterns (2 hours)
**File**: `step_02_remove_patterns.md`
- Fix conversational language ("Let's explore" → "This section presents")
- Remove vague qualifiers ("comprehensive", "significant" without numbers)
- Eliminate "It is clear that", "As we can see", "Obviously"
- Replace with direct technical statements

### Step 3: Consistency Check - Notation (2 hours)
**File**: `step_03_consistency_notation.md`
- Verify vectors: always \vect{x}, never \mathbf{x}
- Verify matrices: always \mat{M}
- Check angles: θ₁ vs. theta1 vs. \theta_1 (pick one!)
- Controller names: "Classical SMC" not "classical SMC" or "CSMC"
- Units: always consistent (m/s² not m/s/s)

### Step 4: Figure/Table Quality Review (1 hour)
**File**: `step_04_visual_quality.md`
- All figures high resolution (300 DPI minimum)
- All axis labels readable
- All captions descriptive (not just "Results")
- All tables use booktabs format
- All visuals referenced in text

### Step 5: Grammar and Spell Check (1 hour)
**File**: `step_05_grammar_spell.md`
- Run spell checker on all .tex files
- Fix common errors: "it's" → "its", "effect" vs. "affect"
- Check passive voice excessive usage
- Verify comma usage in equations

### Step 6: Final Compile and Verify (1 hour)
**File**: `step_06_final_compile.md`
- Full rebuild: `bash scripts/build.sh`
- Verify no new errors introduced
- Check page count still in range (180-220)
- Archive final Day 29 PDF

---

## SOURCE FILES

### AI Pattern Detection Tool
- `scripts/docs/detect_ai_patterns.py`
- Detects: "Let's", "We can see", "comprehensive", "significant", "robust" (without context)
- Target: <5 patterns per chapter

### Thesis Validation Framework
- `docs/thesis/validation/` (12 chapter checklists)
- Use these to verify quality per chapter

### Spell Check
- LaTeX: Use TexStudio built-in spell check
- VS Code: Install LaTeX Workshop extension
- Command line: `aspell -t -c chapter01.tex`

---

## EXPECTED OUTPUT

### AI Pattern Report (before fixes)

Example `ai_patterns_report.txt`:
```
Chapter 1: 12 patterns detected
  - Line 45: "Let's explore the motivation..."
  - Line 102: "We can see that the system is underactuated..."
  - Line 178: "This comprehensive analysis shows..."

Chapter 2: 8 patterns detected
Chapter 3: 5 patterns detected
...
Total: 87 patterns (target: <75)
```

### AI Pattern Report (after fixes)

```
Chapter 1: 3 patterns detected (acceptable)
Chapter 2: 4 patterns detected (acceptable)
Chapter 3: 2 patterns detected (acceptable)
...
Total: 48 patterns (under target 75)
```

### Consistency Report

Before:
```
Notation Issues Found:
- Chapter 4: Uses \mathbf{x} for vectors
- Chapter 5: Uses \vect{x} for vectors
- Chapter 7: Uses "theta1" in text
- Chapter 10: Uses θ₁ in text
- Chapter 13: Uses \theta_1 in math
```

After:
```
Notation Consistent:
- All vectors: \vect{x}
- All matrices: \mat{M}
- All angles: \theta_1 (in math), θ₁ (in text)
- All controller names: Capitalized (Classical SMC)
```

---

## VALIDATION CHECKLIST

### AI Patterns
- [ ] Ran detect_ai_patterns.py on all chapters
- [ ] Total patterns: <75 (or <5 per chapter average)
- [ ] No "Let's" or "We can see" remaining
- [ ] No unsupported "comprehensive" or "significant"
- [ ] No "It is clear that" or "Obviously"

### Notation Consistency
- [ ] Vectors: uniform notation throughout
- [ ] Matrices: uniform notation throughout
- [ ] Scalars vs. vectors distinguished (bold vs. regular)
- [ ] Controller names capitalized consistently
- [ ] Units always with values (5 m/s, not just 5)

### Academic Tone
- [ ] No conversational phrases
- [ ] No first person ("I implemented" → "The system implements")
- [ ] No contractions ("don't" → "do not")
- [ ] No informal expressions ("a lot of" → "numerous")

### Mathematical Notation
- [ ] All equations numbered if referenced
- [ ] Equation punctuation correct (comma or period at end)
- [ ] Variables defined before first use
- [ ] Consistent use of ≈ vs. ~ vs. ≅
- [ ] Consistent use of · vs. × vs. * for multiplication

### Figures and Tables
- [ ] All captions start with capital letter, end with period
- [ ] All captions descriptive (explain what's shown)
- [ ] All axis labels have units in parentheses
- [ ] All legends clear (no "Line 1", "Line 2")
- [ ] All tables use \toprule, \midrule, \bottomrule

### Grammar and Spelling
- [ ] No spelling errors (spell check passed)
- [ ] Subject-verb agreement correct
- [ ] Comma splices fixed
- [ ] Apostrophe usage correct ("its" vs. "it's")
- [ ] Consistent tense (past for experiments, present for facts)

---

## TROUBLESHOOTING

### Too Many AI Patterns (100+)

**Problem**: detect_ai_patterns.py finds 100+ issues
**Solution**:
- Prioritize chapters: Fix Chapters 1, 2, 14, 15 first (most visible)
- Batch replace: Find/replace "Let's" → "This section" across all files
- Accept some patterns if technically accurate

### Inconsistent Notation Hard to Fix

**Problem**: Vector notation differs across 15 chapters
**Solution**:
```bash
# Batch replace across all chapters
cd thesis/chapters
sed -i 's/\\mathbf{x}/\\vect{x}/g' chapter*.tex
```

### Figure Quality Issues

**Problem**: Some figures pixelated or blurry
**Solution**:
- Regenerate at higher DPI: `plt.savefig('fig.pdf', dpi=600)`
- Use vector formats (PDF, SVG) not raster (PNG, JPG)
- Remake figure if necessary

### Grammar Check Finds 500+ "Errors"

**Problem**: Many false positives (LaTeX commands, math notation)
**Solution**:
- Ignore LaTeX commands (\\cite, \\ref, etc.)
- Focus on prose paragraphs
- Use context: "it's" in math (derivative) is okay, "it's" in text (it is) is wrong

---

## AUTOMATED FIXES

### Batch Remove AI Patterns

```bash
cd thesis/chapters
# Remove "Let's"
sed -i "s/Let's explore/This section explores/g" *.tex
sed -i "s/Let's examine/This section examines/g" *.tex

# Remove "We can see"
sed -i "s/We can see that/The results show that/g" *.tex
sed -i "s/As we can see/As shown/g" *.tex

# Remove "It is clear"
sed -i "s/It is clear that/The analysis indicates/g" *.tex
```

### Batch Fix Notation

```bash
# Unify vector notation
sed -i 's/\\mathbf{\([^}]*\)}/\\vect{\1}/g' *.tex

# Unify matrix notation
sed -i 's/\\mathbf{\([A-Z][^}]*\)}/\\mat{\1}/g' *.tex
```

---

## TIME MANAGEMENT

### If Many Issues Found

**Problem**: 200+ AI patterns, inconsistencies everywhere
**Solution**:
- Extend Day 29 to 10-12 hours
- Use automated batch fixes (sed commands above)
- Focus on most visible chapters (1, 2, 14, 15)

### If Few Issues Found

**Problem**: Only 30 AI patterns, notation consistent
**Solution**:
- Complete in 5-6 hours
- Use extra time for deep grammar check
- Or start Day 30 validation early

---

## STYLE GUIDE QUICK REFERENCE

### Replace These Phrases

| Bad (AI-like) | Good (Academic) |
|---------------|-----------------|
| Let's explore | This section examines |
| We can see that | The results show |
| It is clear that | The analysis indicates |
| As we can see | As shown in Figure X |
| comprehensive analysis | analysis (be specific what was analyzed) |
| significant improvement | 28% reduction (quantify!) |
| robust performance | performance under ±30% uncertainty |
| state-of-the-art | (delete or cite specific papers) |

### Notation Standards

| Item | Standard | Example |
|------|----------|---------|
| Vectors | \vect{x} | **x** (bold) |
| Matrices | \mat{M} | **M** (bold) |
| Scalars | x | x (italic) |
| Sets | \mathcal{X} | 𝓧 (calligraphic) |
| Norm | \\|x\\| | ‖x‖ |
| Absolute | |x| | |x| |

---

## NEXT STEPS

Once Day 29 checklist is complete:

1. Archive polished PDF: `cp build/main.pdf ../thesis_day29_polished.pdf`
2. Commit: `git add . && git commit -m "docs(thesis): Day 29 polish complete"`
3. Read thesis abstract one more time (catches last-minute issues)
4. Read `day_30_final/README.md` (10 min)

**Tomorrow (Day 30)**: Final validation, submission package

---

## ESTIMATED COMPLETION TIME

- **Few issues (<50 patterns)**: 5-6 hours
- **Moderate issues (50-100 patterns)**: 7-9 hours
- **Many issues (100+ patterns)**: 10-12 hours

**Most theses need 7-8 hours** for thorough polishing.

---

**[OK] Polish makes perfect! Open `step_01_ai_detection.md` and refine your work!**
