# LT7 RESEARCH PAPER - MANDATORY FIXES CHECKLIST
# Action Items Before Journal Submission

**Status:** CONDITIONAL PASS - Requires mandatory fixes
**Created:** December 26, 2025
**Priority:** HIGH - Complete before submission
**Estimated Total Time:** 15-20 hours

---

## CRITICAL PRIORITY (SEVERITY 1) - MANDATORY

### [ ] Issue 1: Fix β≠1 Mathematical Error

**Affected Sections:** 3, 4, 5, 7, 8, 9, 10
**Root Cause:** Theorem 4.3 assumes β=1 but β≈0.78 from Example 4.1
**Impact:** Invalidates theoretical proofs, affects all results interpretation

**Action Items:**

#### Section 4 (Lyapunov Stability)
- [ ] **Option A:** Modify adaptation law to include β explicitly
  ```
  Change: K̇ = γ|s|
  To:     K̇ = γβ|s|
  ```
- [ ] **Option B:** Add explicit caveat to Theorem 4.3:
  > "Proof assumes β=1 for clarity. For β≠1, gains must be scaled by β⁻¹ in implementation."
- [ ] Update Example 4.1 to show corrected calculation with β=0.78
- [ ] Verify V̇ < 0 condition still holds with corrected proof

**Time:** 3-4 hours | **Priority:** CRITICAL

#### Section 3 (Controller Design)
- [ ] Add β⁻¹ scaling note to ALL control law equations (3.2, 3.3, 3.4, 3.5, 3.6)
  ```
  Add after each equation:
  "Note: For implementation with β≠1, gains must be scaled by β⁻¹.
  With β≈0.78, use K_impl = 1.28·K_nominal."
  ```
- [ ] Update Section 3.9.1 (Tuning Guidelines), Step 2:
  ```
  Change: "Set initial K = 1.2d̄"
  To:     "Set initial K = 1.5d̄/β_min where β = ||LM⁻¹B||"
  ```
- [ ] Add β calculation to Section 3.9.3 (Implementation Checklist)

**Time:** 2 hours | **Priority:** CRITICAL

#### Section 5 (PSO Methodology)
- [ ] Update PSO parameter bounds (Table 5.2) to account for β scaling
- [ ] Add note: "Bounds reflect effective gains; implementation uses K_impl = K_PSO/β"

**Time:** 30 minutes | **Priority:** HIGH

#### Sections 7-10 (Results & Discussion)
- [ ] Global search & replace: "validates theoretical predictions" → "empirically consistent with theoretical expectations"
- [ ] Section 9.4: Add note about β≠1 impacting Lyapunov validation
- [ ] Section 10 (Future Work): Add item: "Rigorous re-derivation of theoretical proofs for β≠1 case"

**Time:** 1 hour | **Priority:** MEDIUM

**Total Time for Issue 1:** 6-7 hours

---

## HIGH PRIORITY (SEVERITY 2) - STRONGLY RECOMMENDED

### [ ] Issue 2: Harmonize Degradation Ratio

**Affected Sections:** Abstract, 5, 7, 8, 10
**Root Cause:** Multiple metrics used (RMS vs raw sum-squared)
**Values:** 50.4x (Table), 144.6x (Text), 49.3x (Calculated)
**Impact:** Undermines precision, confuses readers

**Action Items:**

#### Global Changes
- [ ] **Standardize on RMS-based metric (49.3x):**
  - Abstract: "50.4x" → "49.3x"
  - Section 5.5: "144.6x" → "49.3x (RMS-based chattering index)"
  - Section 8.3 text: Convert all raw sum-squared values to RMS
  - Section 10.2: "50.4x" → "49.3x"

#### Section 8.3 Specific
- [ ] Table 8.3: Keep existing RMS values (correct)
- [ ] Text below Table 8.3: Remove raw sum-squared metrics
  ```
  Remove: "115,291 chattering index... 144.59x degradation"
  Replace: "107.61 N/s chattering index... 49.3x degradation (consistent with Table 8.3)"
  ```
- [ ] Recalculate all degradation ratios using consistent RMS metric

#### Documentation
- [ ] Add footnote to first occurrence (Abstract):
  > "Degradation ratios computed using RMS chattering index (N/s) for physical interpretability.
  > All comparisons use consistent temporal resolution (Δt=0.01s)."

**Time:** 2-3 hours | **Priority:** HIGH

**Total Time for Issue 2:** 2-3 hours

---

### [ ] Issue 3: Investigate 1104° Overshoot Anomaly

**Affected Sections:** 8 (Table 8.2e), 10 (Finding 6)
**Value:** 1104° overshoot for Adaptive Scheduling
**Impact:** Physically nonsensical (>3 full rotations), suggests data error

**Action Items:**

#### Data Verification
- [ ] Check raw simulation logs for Adaptive Scheduling test
- [ ] Verify units: degrees vs radians vs milliradians
  - 1104 mrad = 63.3° (plausible)
  - 1104° = 3 rotations (implausible for stabilization)
- [ ] Check if value represents:
  - Maximum deviation from setpoint (expected)
  - Cumulative angular displacement (wrong metric)
  - Controller failure/divergence (should be labeled differently)

#### Corrections (depends on verification)
- [ ] **If typo (11.04°):**
  - Update Table 8.2e: "1104°" → "11.04°"
  - Recalculate overshoot penalty in Section 10

- [ ] **If unit error (1104 mrad):**
  - Update Table 8.2e: "1104°" → "63.3° (1104 mrad)"
  - Add note about unit conversion

- [ ] **If controller diverged:**
  - Update Table 8.2e: "Overshoot: 1104°" → "Status: Diverged"
  - Section 10.2 Finding 6: Change from "overshoot penalty" to "failure under step disturbance"

**Time:** 1-2 hours (data check + corrections) | **Priority:** HIGH

**Total Time for Issue 3:** 1-2 hours

---

### [ ] Issue 4: Add Chattering Index Temporal Dependency Disclaimer

**Affected Sections:** 5, 7, 8
**Root Cause:** Metric depends on Δt, not stated
**Impact:** Affects reproducibility and external comparisons

**Action Items:**

#### Section 5.4.2 (Definition)
- [ ] Add after chattering index formula:
  > "Note: The chattering index is computed at sampling rate Δt=0.01s (100 Hz).
  > Metric values depend on temporal resolution—higher sampling rates detect more
  > rapid switching and increase CI. All comparisons in this work use consistent
  > Δt=0.01s for internal validity."

#### Table Captions
- [ ] Table 7.3 (Section 7): Add "(at Δt=0.01s)" to caption
- [ ] Table 8.3 (Section 8): Add "(at Δt=0.01s)" to caption
- [ ] Any other tables reporting chattering index

**Time:** 30 minutes | **Priority:** MEDIUM

**Total Time for Issue 4:** 30 minutes

---

## MEDIUM PRIORITY (SEVERITY 3) - RECOMMENDED

### [ ] Issue 5: Section 2 Clarifications

**Action Items:**
- [ ] Define inertia reference explicitly: "I_link = moment of inertia about COM (not pivot)"
- [ ] Quantify small angle assumption: "Valid for |θ₁|, |θ₂| < 0.5 rad (≈28.6°)"
- [ ] Resolve Abstract vs Section 2.3 contradiction:
  - Abstract claims "general nonlinear"
  - Section 2.3 uses linearized friction
  - Add note: "Full nonlinear dynamics except Coulomb friction (linearized for stability)"

**Time:** 1 hour | **Priority:** LOW

---

### [ ] Issue 6: Statistical Methodology Improvements

**Action Items:**
- [ ] Section 6.4: Add normality verification
  ```
  "Normality of residuals verified using Shapiro-Wilk test (p>0.05 for all datasets)"
  ```
- [ ] Section 7: Apply Bonferroni correction
  ```
  "Multiple comparison correction: Bonferroni-adjusted α = 0.05/21 = 0.0024"
  Update all p-values or note which comparisons remain significant
  ```
- [ ] Section 7: Report pooled standard deviation for Cohen's d verification

**Time:** 3-4 hours (requires re-analysis) | **Priority:** DEFER to reviewer response

---

### [ ] Issue 7: Minor Numerical Corrections

**Action Items:**
- [ ] Section 3: "15% model uncertainty" → "16%" (match Section 8.1)
- [ ] Section 3: MPC feasibility "Marginal" → "Infeasible for 10kHz" (Table 3.2)
- [ ] Section 3: Rename "derivative gain k_d" → "sliding surface damping k_d"
- [ ] Section 8: Define Robustness Score formula or change "30.0" → "0.0 (Failed)"

**Time:** 1 hour | **Priority:** LOW

---

## SUMMARY CHECKLIST

### Before Submission (MANDATORY)
- [ ] Issue 1: β≠1 error fixed (6-7 hours) - CRITICAL
- [ ] Issue 2: Degradation ratio harmonized (2-3 hours) - HIGH
- [ ] Issue 3: 1104° overshoot investigated (1-2 hours) - HIGH
- [ ] Issue 4: Chattering index disclaimer added (30 min) - MEDIUM

**Total Mandatory Time:** 10-13 hours

### Strongly Recommended
- [ ] Issue 5: Section 2 clarifications (1 hour)
- [ ] Issue 7: Minor numerical corrections (1 hour)

**Total Recommended Time:** +2 hours

### Defer to Revision (if reviewers request)
- [ ] Issue 6: Statistical methodology improvements (3-4 hours)

---

## VERIFICATION CHECKLIST

After completing fixes, verify:

### Mathematical Correctness
- [ ] All equations in Section 3 include β scaling notes
- [ ] Theorem 4.3 proof corrected or caveat added
- [ ] PSO bounds updated for β≠1
- [ ] All degradation ratios use same metric (RMS)

### Numerical Consistency
- [ ] Global search: No remaining "50.4x" or "144.6x" (use "49.3x")
- [ ] 1104° value corrected or explained
- [ ] All chattering index tables include Δt notation

### Cross-Section Consistency
- [ ] Abstract ↔ Section 8 ↔ Section 10: Same degradation value
- [ ] Section 3 gains ↔ Section 5 PSO bounds: Consistent scaling
- [ ] Section 4 proofs ↔ Section 9 validation: Language softened

### Documentation Quality
- [ ] All SEVERITY 1 issues marked RESOLVED
- [ ] All SEVERITY 2 issues addressed or deferred with justification
- [ ] MASTER_AUDIT_SUMMARY.md updated with fix status

---

## ESTIMATED TIMELINE

**Minimal submission (SEVERITY 1 only):**
- Time: 6-7 hours
- Status: Acceptable but suboptimal

**Recommended submission (SEVERITY 1 + 2):**
- Time: 10-13 hours
- Status: Strong submission

**Optimal submission (SEVERITY 1 + 2 + selected 3):**
- Time: 12-15 hours
- Status: Publication-ready

---

## NEXT STEPS

1. **Prioritize Issue 1 (β≠1)** - Most critical, affects entire paper
2. **Verify data for Issue 3 (1104°)** - Quick data check prevents embarrassment
3. **Batch process Issue 2 (degradation)** - Global search & replace
4. **Add Issue 4 disclaimer** - Low effort, high reproducibility value
5. **Final verification pass** - Use verification checklist above

---

**Last Updated:** December 26, 2025
**Status:** Ready for fixes
**See Also:** MASTER_AUDIT_SUMMARY.md (complete analysis)
