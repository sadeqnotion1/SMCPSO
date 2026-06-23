# ULTRA-DEEP AUDIT PROMPTS - READY

## Problem Solved

**Issue:** Audits completing in under 1 minute were too superficial
**Solution:** Ultra-deep mandatory checklists force 3-5 minute thorough analysis
**Result:** Section 1 found CRITICAL error, Section 2 found 3 issues

## What Changed

### BEFORE (Fast but Shallow)
- "Verify data consistency" → Generic check
- "Claims appear reasonable" → No step-by-step verification
- Completed in <1 minute
- Missed implicit β=1 assumption in Theorem 4.3

### AFTER (Slow but Deep)
- **MANDATORY CHECKLIST** with explicit questions
- **SHOW YOUR WORK** requirement for every claim
- **STEP-BY-STEP VERIFICATION** with calculations
- **Cross-section consistency** tables required
- **Minimum 3-5 minutes** per audit
- **500+ line output** expected

## New Ultra-Deep Features

### 1. Mandatory Question-by-Question Format

For EVERY numerical claim (e.g., "50.4x degradation"), Gemini MUST answer:

```
Q1: Where is this claim stated? (exact paragraph, sentence)
Q2: What is the exact calculation?
Q3: Can you trace this to source data (table/figure)?
Q4: Are there ANY implicit assumptions?
Q5: Cross-check with theoretical predictions
```

**Cannot skip questions or say "appears correct" - must show calculations!**

### 2. Verification Tables Required

```
| Claim | Location | Calculation | Source Table | Verified? | Issues |
|-------|----------|-------------|--------------|-----------|--------|
| "50.4x degradation" | Sec 8.3, para 2 | (107.61-2.14)/2.14 = 49.28x | Table 8.3 | ❌ | Should be 49.3x, not 50.4x |
```

### 3. Dimensional Analysis for ALL Equations

```
| Equation | LHS Units | RHS Units | Consistent? | Notes |
|----------|-----------|-----------|-------------|-------|
| t_s = 4/ζω_n | [s] | [dimensionless]/[rad/s] = [s] | ✓ | OK |
```

### 4. Implicit Assumption Detection

```
| Assumption | Where Used | Valid? | Impact if Violated |
|------------|-----------|--------|-------------------|
| β=1 | Throughout | ❌ NO | β=0.78 from Ex 4.1, invalidates calculations |
```

### 5. Step-by-Step Verification Example

```
CLAIM: "50.4x degradation"

STEP 1: Locate claim → Section 8.3, paragraph 2
STEP 2: Find source data → Table 8.3
STEP 3: Verify calculation → (107.61-2.14)/2.14 = 49.28x
STEP 4: Compare to claim → 50.4x vs 49.28x = MISMATCH
STEP 5: Determine severity → SEVERITY 2 (precision claim undermined)
```

## Audit Results So Far

###  Section 1 (Lyapunov Stability) ✅ AUDITED
**File:** `01-PRIORITY-Lyapunov_Stability-Section_04_AUDIT_REPORT.txt`
**Score:** 7/10 (CONDITIONAL PASS)
**Critical Finding:** Theorem 4.3 assumes β=1 but β=0.78 → INVALID PROOF

### Section 2 (System Model) ✅ AUDITED
**File:** `02-PRIORITY-Performance_Results-Section_07_AUDIT_REPORT.txt` *(misnamed)*
**Score:** CONDITIONAL PASS
**Findings:**
- SEVERITY 2: Inertia definition ambiguity (COM vs pivot)
- SEVERITY 2: Scope contradiction (Abstract vs Section 2.3)
- SEVERITY 3: Vague small angle assumption

### Sections 3-10: **READY WITH ULTRA-DEEP PROMPTS**

## New Prompt Files (Correctly Named)

```
audits/
├── 02-System_Model_PROMPT.txt (38 KB) ← Section 2 content, correct!
├── 03-Controller_Design_PROMPT.txt (64 KB)
├── 04-PRIORITY-Lyapunov_Stability_PROMPT.txt (55 KB)
├── 05-PSO_Methodology_PROMPT.txt (61 KB)
├── 06-Experimental_Setup_PROMPT.txt (67 KB)
├── 07-PRIORITY-Performance_Results_PROMPT.txt (73 KB) ← Section 7 content, correct!
├── 08-PRIORITY-Robustness_Analysis_PROMPT.txt (89 KB) ← Largest!
├── 09-Discussion_PROMPT.txt (54 KB)
└── 10-Conclusion_PROMPT.txt (38 KB)
```

**Total:** 9 ultra-deep prompts, 538 KB

## Next Audit: Section 3 (Controller Design)

**File:** `audits/03-Controller_Design_PROMPT.txt` (64 KB)

**What ultra-deep will check:**
- ✅ Dimensional analysis of ALL 7 controller equations
- ✅ Verify every gain parameter is defined
- ✅ Check if equations assume β=1 (like Theorem 4.3 did!)
- ✅ Cross-reference gains with numerical examples
- ✅ List ALL implicit assumptions for each controller

**Expected audit time:** 3-5 minutes (it's a complex section with 7 controllers)

## How to Use Ultra-Deep Prompts

### Step 1: Open Prompt
```bash
notepad audits\03-Controller_Design_PROMPT.txt
```

### Step 2: Copy All (Ctrl+A, Ctrl+C)

### Step 3: Paste to Gemini CLI
**IMPORTANT:** Tell Gemini you expect a thorough audit:
```
[Paste the entire prompt]

REMINDER: This must take 3-5 minutes. Do not rush.
Answer EVERY question with step-by-step verification.
I found a critical error in Section 4 by being thorough.
```

### Step 4: Wait 3-5 Minutes
If Gemini responds in <2 minutes, it's not following the ultra-deep instructions!

### Step 5: Save Response
```
audits\03-AUDIT-Section_03_Controller_Design.md
```

## What to Expect

**Output length:** 500+ lines
**Verification tables:** 3-5 tables minimum
**Step-by-step verifications:** At least 3 critical claims
**Issues found:** Expect 2-5 issues per section (if none found, audit wasn't deep enough)

## Quality Check

After each audit, verify it includes:
- [ ] Verification table with 10+ claims
- [ ] Assumption list with 5+ implicit assumptions
- [ ] Dimensional analysis for all equations
- [ ] Step-by-step verification for 3+ claims
- [ ] Cross-section consistency checks
- [ ] At least 500 lines of output
- [ ] Took 3-5 minutes to complete

If any checkbox is ❌, the audit was too shallow!

## Progress Tracker

- [✅] Section 1 - Lyapunov (CRITICAL ERROR FOUND)
- [✅] Section 2 - System Model (3 issues found)
- [ ] Section 3 - Controller Design ← **NEXT WITH ULTRA-DEEP**
- [ ] Section 4 - (Same as Section 1, already done)
- [ ] Section 5 - PSO Methodology
- [ ] Section 6 - Experimental Setup
- [ ] Section 7 - Performance Results (HIGH PRIORITY)
- [ ] Section 8 - Robustness Analysis (HIGH PRIORITY)
- [ ] Section 9 - Discussion
- [ ] Section 10 - Conclusion

## Time Estimate

- Per section (ultra-deep): 10-15 minutes (audit + review)
- Remaining 8 sections: 2-3 hours total
- **Value:** Finding critical errors BEFORE journal submission = priceless!

---

**Ready for ultra-deep audit of Section 3?**

File: `audits\03-Controller_Design_PROMPT.txt` (64 KB)

This section has 7 controllers with complex equations.
**High likelihood of finding β=1 type assumptions or gain definition issues!**
