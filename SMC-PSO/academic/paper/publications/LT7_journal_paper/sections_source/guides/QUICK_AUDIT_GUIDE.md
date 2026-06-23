# Quick Audit Guide - Minimal Manual Workflow

## Super Quick Method (Recommended)

### Windows

```bash
# Generate ready-to-paste prompt for Section 1
generate_audit_prompt.bat 1

# This creates: audits/Section_01_PROMPT.txt
# Then:
# 1. Open audits/Section_01_PROMPT.txt
# 2. Select all (Ctrl+A), copy (Ctrl+C)
# 3. Paste into Gemini CLI
# 4. Save Gemini's output to: audits/Section_01_AUDIT_REPORT.md
```

### Linux/Mac

```bash
# Generate ready-to-paste prompt for Section 1
chmod +x generate_audit_prompt.sh
./generate_audit_prompt.sh 1

# This outputs the prompt to terminal
# Then:
# 1. Scroll up and select all output
# 2. Copy and paste into Gemini CLI
# 3. Save Gemini's output to: audits/Section_01_AUDIT_REPORT.md
```

## One-Command Method (Advanced)

### Direct File Creation

```bash
# Windows
(type Section_01_Introduction.md && echo. && echo ━━━ AUDIT INSTRUCTIONS ━━━ && echo. && jq -r ".sections[0].audit_prompt" audit_config.json) > audits/Section_01_PROMPT.txt

# Linux/Mac
(cat Section_01_Introduction.md && echo "" && echo "━━━ AUDIT INSTRUCTIONS ━━━" && echo "" && jq -r '.sections[0].audit_prompt' audit_config.json) > audits/Section_01_PROMPT.txt
```

Then open `audits/Section_01_PROMPT.txt`, copy all, paste to Gemini CLI.

### Copy to Clipboard (if clip/pbcopy available)

```bash
# Windows (copy directly to clipboard)
(type Section_01_Introduction.md && echo. && echo ━━━ AUDIT INSTRUCTIONS ━━━ && echo. && jq -r ".sections[0].audit_prompt" audit_config.json) | clip

# Mac (copy directly to clipboard)
(cat Section_01_Introduction.md && echo "" && echo "━━━ AUDIT INSTRUCTIONS ━━━" && echo "" && jq -r '.sections[0].audit_prompt' audit_config.json) | pbcopy

# Linux (copy directly to clipboard - requires xclip)
(cat Section_01_Introduction.md && echo "" && echo "━━━ AUDIT INSTRUCTIONS ━━━" && echo "" && jq -r '.sections[0].audit_prompt' audit_config.json) | xclip -selection clipboard
```

Then just paste (Ctrl+V) into Gemini CLI.

## All Sections Quick Reference

| Section | Command | Priority |
|---------|---------|----------|
| 01: Introduction | `generate_audit_prompt.bat 1` | Medium |
| 02: List of Figures | `generate_audit_prompt.bat 2` | Low |
| 03: System Model | `generate_audit_prompt.bat 3` | Medium |
| 04: Controller Design | `generate_audit_prompt.bat 4` | Medium |
| 05: Lyapunov Stability | `generate_audit_prompt.bat 5` | **HIGH** |
| 06: PSO Methodology | `generate_audit_prompt.bat 6` | Medium |
| 07: Experimental Setup | `generate_audit_prompt.bat 7` | Medium |
| 08: Performance Results | `generate_audit_prompt.bat 8` | **HIGH** |
| 09: Robustness Analysis | `generate_audit_prompt.bat 9` | **HIGH** |
| 10: Discussion | `generate_audit_prompt.bat 10` | Medium |
| 11: Conclusion | `generate_audit_prompt.bat 11` | Low |
| 12: Acknowledgments | `generate_audit_prompt.bat 12` | Low |

## Recommended Audit Order

1. **Section 05** (Lyapunov Stability) - Critical: 4 mathematical proofs
2. **Section 08** (Performance Results) - Critical: Major numerical claims
3. **Section 09** (Robustness Analysis) - Critical: PSO failure claims (50.4x, 90.2%)
4. **Section 04** (Controller Design) - Important: 7 controller equations
5. **Section 01** (Introduction) - Important: Literature survey, research gaps
6. **Sections 03, 06, 07, 10** - Medium priority
7. **Sections 02, 11, 12** - Low priority (formatting/completeness only)

## Minimal Workflow Example

### Step 1: Generate Prompt
```bash
# Windows
generate_audit_prompt.bat 5

# Output: audits/Section_05_PROMPT.txt
```

### Step 2: Copy Prompt
```bash
# Open audits/Section_05_PROMPT.txt
# Ctrl+A (select all)
# Ctrl+C (copy)
```

### Step 3: Paste to Gemini CLI
```bash
gemini

# Paste (Ctrl+V)
# Press Enter or your CLI's submit method
# Wait for response (30-60 seconds)
```

### Step 4: Save Response
```bash
# Copy Gemini's entire response
# Save to: audits/Section_05_AUDIT_REPORT.md
```

### Step 5: Review
```bash
# Open audits/Section_05_AUDIT_REPORT.md
# Look for:
#   - Overall score (target ≥8/10)
#   - CRITICAL issues (must fix)
#   - Top 3 recommendations
```

## Even Simpler: No Scripts

If you don't want to use scripts:

```bash
# 1. Open Section_05_Lyapunov_Stability.md in text editor
# 2. Copy all content

# 3. Open audit_config.json
# 4. Find sections[4].audit_prompt (Section 5 is index 4)
# 5. Copy the audit_prompt text

# 6. In Gemini CLI, paste:
#    - First: markdown content
#    - Then: "--- AUDIT INSTRUCTIONS ---"
#    - Then: audit_prompt text

# 7. Submit and wait for response
# 8. Save response to audits/Section_05_AUDIT_REPORT.md
```

## What to Expect

**Input size:** ~200-1000 lines per section
**Gemini processing time:** 30-60 seconds
**Output size:** ~100-300 lines (audit report)

**Audit report structure:**
- Scores (1-10): Technical accuracy, writing quality, completeness, overall
- Strengths: 3-5 specific positives
- Issues: Critical, minor, suggestions
- Recommendations: 3-5 actionable improvements

## Troubleshooting

**Problem:** "jq: command not found"
- **Windows:** Download from https://stedolan.github.io/jq/download/
- **Linux:** `sudo apt install jq`
- **Mac:** `brew install jq`
- **Alternative:** Manually copy prompts from audit_config.json

**Problem:** "File too large for Gemini"
- **Solution:** Section 04 (Controller Design) is large. If it fails, split into 2-3 subsections.

**Problem:** "Can't paste into Gemini CLI"
- **Solution:** Save prompt to file, then use: `gemini < audits/Section_XX_PROMPT.txt > audits/Section_XX_AUDIT_REPORT.md`

## After All Audits

```bash
# Check overall scores
grep "Overall:" audits/Section_*_AUDIT_REPORT.md

# Find critical issues
grep -A 5 "CRITICAL" audits/Section_*_AUDIT_REPORT.md > audits/CRITICAL_ISSUES.txt

# Calculate average score
grep "Overall:" audits/Section_*_AUDIT_REPORT.md | awk '{sum+=$NF; count++} END {printf "Average: %.1f/10\n", sum/count}'
```

## Time Estimate

- **Per section:** 5-10 minutes (generate prompt + run audit + review)
- **All 12 sections:** 1-2 hours total
- **Priority 3 sections only:** 30 minutes

## Files You'll Create

```
audits/
├── Section_01_PROMPT.txt (generated by script)
├── Section_01_AUDIT_REPORT.md (saved from Gemini)
├── Section_02_PROMPT.txt
├── Section_02_AUDIT_REPORT.md
├── ...
├── Section_12_PROMPT.txt
└── Section_12_AUDIT_REPORT.md
```

**Ready? Start with Section 05 (Lyapunov Stability)!**

```bash
generate_audit_prompt.bat 5
```
