# Audit Prompt Files - Priority Order

All audit prompts are ready! Work through them in order from 01 to 10.

## Files Ordered by Priority

### HIGH PRIORITY ⚠️ (Do These First!)

**01. Lyapunov Stability** (37 KB) - Section 4
- **File:** `01-PRIORITY-Lyapunov_Stability-Section_04_PROMPT.txt`
- **Why Critical:** Contains 4 mathematical proofs (Theorems 4.1-4.4)
- **What to Check:** Proof correctness, Lyapunov functions, derivatives
- **Save Response To:** `01-AUDIT-Section_04_Lyapunov_Stability.md`

**02. Performance Results** (54 KB) - Section 7
- **File:** `02-PRIORITY-Performance_Results-Section_07_PROMPT.txt`
- **Why Critical:** All major numerical claims (1.82s, 91% chattering reduction, etc.)
- **What to Check:** Data consistency, statistical significance, confidence intervals
- **Save Response To:** `02-AUDIT-Section_07_Performance_Results.md`

**03. Robustness Analysis** (70 KB) - Section 8
- **File:** `03-PRIORITY-Robustness_Analysis-Section_08_PROMPT.txt`
- **Why Critical:** PSO failure claims (50.4x degradation, 90.2% failure rate)
- **What to Check:** All degradation metrics, failure rate calculations
- **Save Response To:** `03-AUDIT-Section_08_Robustness_Analysis.md`

---

### MEDIUM PRIORITY (Do After High Priority)

**04. Controller Design** (45 KB) - Section 3
- **File:** `04-Controller_Design-Section_03_PROMPT.txt`
- **Focus:** 7 controller equations and design rationale
- **Save Response To:** `04-AUDIT-Section_03_Controller_Design.md`

**05. Experimental Setup** (49 KB) - Section 6
- **File:** `05-Experimental_Setup-Section_06_PROMPT.txt`
- **Focus:** Statistical methodology (Welch's t-test, bootstrap, etc.)
- **Save Response To:** `05-AUDIT-Section_06_Experimental_Setup.md`

**06. Introduction** (26 KB) - Section 1
- **File:** `06-Introduction-Section_01_PROMPT.txt`
- **Focus:** Literature survey (68 citations), research gaps
- **Save Response To:** `06-AUDIT-Section_01_Introduction.md`

**07. PSO Methodology** (42 KB) - Section 5
- **File:** `07-PSO_Methodology-Section_05_PROMPT.txt`
- **Focus:** PSO algorithm, objective function, multi-scenario approach
- **Save Response To:** `07-AUDIT-Section_05_PSO_Methodology.md`

**08. System Model** (20 KB) - Section 2
- **File:** `08-System_Model-Section_02_PROMPT.txt`
- **Focus:** DIP equations, parameters, mathematical model
- **Save Response To:** `08-AUDIT-Section_02_System_Model.md`

---

### LOW PRIORITY (Do Last)

**09. Discussion** (35 KB) - Section 9
- **File:** `09-Discussion-Section_09_PROMPT.txt`
- **Focus:** Design guidelines, synthesis, application matrix
- **Save Response To:** `09-AUDIT-Section_09_Discussion.md`

**10. Conclusion** (19 KB) - Section 10
- **File:** `10-Conclusion-Section_10_PROMPT.txt`
- **Focus:** Summary, future work (no new claims)
- **Save Response To:** `10-AUDIT-Section_10_Conclusion.md`

---

## Quick Workflow

### For Each File (in order 01-10):

1. **Open the prompt file:**
   ```
   audits\01-PRIORITY-Lyapunov_Stability-Section_04_PROMPT.txt
   ```

2. **Copy all content:** Ctrl+A, Ctrl+C

3. **Paste to Gemini CLI:**
   ```bash
   gemini
   # Paste and submit
   ```

4. **Save Gemini's response:**
   - Copy the entire audit report
   - Save to: `01-AUDIT-Section_04_Lyapunov_Stability.md`

5. **Move to next file:** Open `02-PRIORITY-...`

## Progress Tracking

Mark sections as you complete them:

- [ ] 01. Lyapunov Stability ⚠️
- [ ] 02. Performance Results ⚠️
- [ ] 03. Robustness Analysis ⚠️
- [ ] 04. Controller Design
- [ ] 05. Experimental Setup
- [ ] 06. Introduction
- [ ] 07. PSO Methodology
- [ ] 08. System Model
- [ ] 09. Discussion
- [ ] 10. Conclusion

## After All Audits

```bash
# Check all scores
grep "Overall:" *-AUDIT-*.md

# Find critical issues
grep "CRITICAL" *-AUDIT-*.md

# Calculate average
grep "Overall:" *-AUDIT-*.md | awk '{sum+=$NF; count++} END {printf "Average: %.1f/10\n", sum/count}'
```

## Time Estimate

- **High priority (01-03):** 30-45 minutes
- **Medium priority (04-08):** 45-60 minutes
- **Low priority (09-10):** 15-20 minutes
- **Total:** ~2 hours for all 10 sections

---

**Ready? Start with file 01!**

Location: `D:\Projects\main\.artifacts\research\papers\LT7_journal_paper\sections\audits\`
