# Step 3: Format and Validate BibTeX

**Time**: 1.5 hours
**Output**: Clean .bib file
**Source**: Organized bibliography

---

## OBJECTIVE

Format all BibTeX entries consistently, validate with bibtex

---

## SOURCE MATERIALS TO READ FIRST (22 min)

### Primary Sources
1. **Read**: Relevant project documentation
2. **Review**: Previous chapter outputs
3. **Check**: Automation scripts available



---

## EXACT PROMPT TO USE

### Copy This Into Your AI Assistant:

```
Write Clean .bib file for the thesis.

Context:
- Master's thesis on "Sliding Mode Control of Double-Inverted Pendulum with PSO"
- Audience: Control systems engineering researchers/professors
- Format: LaTeX, IEEE citation style
- Tone: Formal academic (NO conversational language)

Structure (0 pages total):

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

Length: 0 pages (12pt font, 1-inch margins)
```

---

## WHAT TO DO WITH THE OUTPUT

### 1. Review and Edit (26 min)

Check for:
- [ ] Academic tone maintained
- [ ] Specific claims (no vague "comprehensive")
- [ ] Proper citations throughout
- [ ] Mathematical notation correct
- [ ] Smooth transitions between paragraphs

### 2. Format as LaTeX (18 min)

Save to appropriate location in `thesis/` directory.

### 3. Test Compile (9 min)

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


---

## TIME CHECK

Total estimated: 1.5 hours
- Reading: 22 min
- Prompt generation: 4 min
- Review: 26 min
- Formatting: 18 min
- Compile/test: 9 min

---

## NEXT STEP

Proceed to: `step_04_compile_bibliography.md`

---

**[OK] Ready to proceed!**
