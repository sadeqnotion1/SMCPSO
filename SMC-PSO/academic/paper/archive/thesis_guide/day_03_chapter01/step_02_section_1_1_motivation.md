# Step 2: Write Section 1.1 - Motivation

**Time**: 2 hours
**Output**: 3 pages (Section 1.1 of Chapter 1)
**Source**: `docs/thesis/chapters/00_introduction.md` (lines 1-16)

---

## OBJECTIVE

Write a compelling 3-page motivation section explaining WHY the DIP-SMC-PSO problem matters for control systems engineering.

---

## SOURCE MATERIALS TO READ FIRST (30 min)

### Primary Source
1. **Read**: `D:\Projects\main\docs\thesis\chapters\00_introduction.md` (lines 1-16)
   - Existing motivation paragraphs
   - Note key points about underactuated systems, robustness challenges

### Supporting References (skim for context)
2. **Skim**: Utkin (1977) - Why SMC is important for robust control
3. **Skim**: Fantoni & Lozano (2001) - DIP as benchmark problem
4. **Skim**: Any 3-5 papers from `docs/CITATIONS_ACADEMIC.md` on inverted pendulum control

---

## EXACT PROMPT TO USE

### Copy This Into Your AI Assistant:

```
Write Section 1.1 - Motivation (3 pages) for a Master's thesis on "Sliding Mode Control of Double-Inverted Pendulum with Particle Swarm Optimization."

Context:
- This is Chapter 1 (Introduction) of a 200-page Master's thesis
- Audience: Control systems engineering researchers/professors
- Format: LaTeX, IEEE citation style
- Tone: Formal academic (NO conversational language like "Let's explore" or "We can see that")

Structure (3 pages total):

**Page 1: Historical Context & Importance**
- Inverted pendulum as canonical control problem since 1950s-60s
- Why it matters: Benchmark for testing control algorithms
- Real-world applications:
  * Robotics: Humanoid balancing, bipedal walking
  * Aerospace: Rocket stabilization during vertical landing
  * Transportation: Self-balancing vehicles (Segway)
- Transition: "While single inverted pendulums are well-studied, the double-inverted pendulum (DIP) presents..."

**Page 2: DIP-Specific Challenges**
- Underactuated system (1 control input, 3 degrees of freedom)
- Highly nonlinear dynamics (coupled equations of motion)
- Unstable equilibrium (both pendulums want to fall)
- Tight coupling between first and second pendulum angles
- Sensitivity to parameter uncertainties (mass, length, friction)
- External disturbances (wind, vibration, measurement noise)
- Quote challenge: "The DIP represents one of the most challenging underactuated systems for control design."

**Page 3: Why Sliding Mode Control?**
- Robustness properties:
  * Insensitivity to matched disturbances
  * Finite-time convergence (vs. asymptotic)
  * Reduced sensitivity to parameter variations
- Challenge: Chattering phenomenon (high-frequency switching)
- Motivation for this work: "Despite SMC's advantages, its application to DIP systems requires careful mitigation of chattering..."
- Lead into next section: "This thesis addresses these challenges by..."

Citation Requirements:
- Cite 5-7 relevant papers
- Use IEEE format: cite:Utkin1977, cite:Fantoni2001, etc.
- Reference specific results: "Utkin demonstrated that SMC provides invariance to matched uncertainties cite:Utkin1977."

Mathematical Notation (if needed):
- Use LaTeX math: $\theta_1$, $\theta_2$ for pendulum angles
- Use \vect{x} for state vector
- Use \Real^n for real vector space

Quality Checks:
- NO conversational language ("Let's", "We can see", "It is clear that")
- NO vague claims ("comprehensive", "significant") without quantification
- YES specific statements: "SMC achieves 30% faster settling time compared to PID cite:Smith2010"
- YES technical precision: "The DIP system has three degrees of freedom (x, θ₁, θ₂) but only one control input (force u applied to cart)"

Length: Exactly 3 pages when compiled in LaTeX (12pt font, 1-inch margins)
```

---

## WHAT TO DO WITH THE OUTPUT

### 1. Review and Edit (30 min)

Check for:
- [ ] **Academic tone**: No "Let's explore", "We can see that", "It is clear"
- [ ] **Specific claims**: Replace "significant improvement" with "28% reduction in settling time"
- [ ] **Proper citations**: Every claim backed by reference
- [ ] **Mathematical notation**: Use \theta_1, not theta1 or θ₁ (unless in LaTeX)
- [ ] **Transitions**: Smooth flow between paragraphs
- [ ] **Length**: Should be ~750-900 words for 3 pages

### 2. Format as LaTeX (15 min)

Save to: `D:\Projects\main\thesis\chapters\chapter01_introduction.tex`

Add section header:
```latex
\section{Motivation}
\label{sec:intro:motivation}

[PASTE AI OUTPUT HERE]
```

### 3. Add Citations (15 min)

Ensure bibliography file has entries:
```latex
% In thesis/bibliography/papers.bib
@article{Utkin1977,
  author = {Utkin, V. I.},
  title = {Variable structure systems with sliding modes},
  journal = {IEEE Trans. Autom. Control},
  year = {1977},
  volume = {22},
  number = {2},
  pages = {212--222}
}
```

### 4. Test Compile (10 min)

```bash
cd thesis
pdflatex main.tex
```

Verify:
- [ ] No "Undefined control sequence" errors
- [ ] No "Citation undefined" warnings (okay for now, will fix in Day 27)
- [ ] Section appears in Table of Contents
- [ ] Page count: 2.5-3.5 pages (some flexibility)

---

## VALIDATION CHECKLIST

Before moving to Step 3 (Section 1.2):

### Content Quality
- [ ] Historical context explains why DIP matters
- [ ] 3-5 real-world applications mentioned
- [ ] DIP challenges clearly articulated (underactuated, nonlinear, unstable)
- [ ] SMC benefits explained (robustness, finite-time)
- [ ] Transitions smooth (each paragraph leads to next)

### Citations
- [ ] 5-7 papers cited
- [ ] Citations use proper LaTeX format (\cite{Utkin1977})
- [ ] No unsupported claims ("It is well-known..." needs citation)

### Tone & Style
- [ ] Formal academic language throughout
- [ ] No conversational phrases
- [ ] Technical precision (specific DOF count, parameter names)
- [ ] No vague qualifiers ("very", "quite", "rather")

### LaTeX Formatting
- [ ] Section header with \label
- [ ] Math notation correct ($\theta_1$ not theta1)
- [ ] No special characters causing errors
- [ ] Compiles without fatal errors

### Page Count
- [ ] Output is 2.5-3.5 pages (target: 3 pages)
- [ ] If too short: Add more applications or expand challenges
- [ ] If too long: Condense historical context slightly

---

## EXPECTED OUTPUT SAMPLE

Here's what the first paragraph might look like:

```latex
\section{Motivation}
\label{sec:intro:motivation}

The inverted pendulum has served as a canonical benchmark problem in control theory since the 1960s \cite{Mori1976}. Its inherent instability, nonlinear dynamics, and underactuated nature make it an ideal testbed for evaluating control algorithms \cite{Ogata2009}. Real-world applications include stabilization of humanoid robots during bipedal walking \cite{Kajita2003}, vertical landing control of reusable rockets \cite{Blackmore2016}, and self-balancing personal transportation vehicles \cite{Grasser2002}. While single inverted pendulums have been extensively studied, the double-inverted pendulum (DIP) presents significantly greater challenges due to increased degrees of freedom and tighter coupling between system states.
```

---

## COMMON ISSUES

**Issue**: Output is too conversational ("Let's explore the challenges...")
- **Fix**: Edit manually to remove conversational phrases
- **Better**: "The primary challenges include..."

**Issue**: No citations provided
- **Fix**: Add \cite{} commands manually using papers from `docs/CITATIONS_ACADEMIC.md`

**Issue**: Too short (only 2 pages)
- **Fix**: Expand applications section (add 2-3 more examples)
- **OR**: Expand SMC benefits with technical details

**Issue**: Too long (4+ pages)
- **Fix**: Condense historical context (cut redundant examples)
- **OR**: Move some SMC details to Chapter 5 (SMC Theory)

---

## TIME CHECK

- Reading sources: 30 min
- Running prompt: 5 min
- Reviewing output: 30 min
- Editing for tone: 30 min
- Formatting LaTeX: 15 min
- Test compile: 10 min
- **Total**: ~2 hours

---

## NEXT STEP

Once Section 1.1 is complete and validated:
**Proceed to**: `step_03_section_1_2_overview.md`

This will write Section 1.2 - Problem Overview (3 pages, 1 hour)

---

**[OK] Ready to write? Copy the prompt above and let's create Section 1.1!**
