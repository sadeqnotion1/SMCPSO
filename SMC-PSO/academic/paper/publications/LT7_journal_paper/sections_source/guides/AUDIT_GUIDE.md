# LT-7 Research Paper - Section Audit Guide

## Overview

This guide explains how to audit each section of the LT-7 research paper using Gemini CLI. Each section gets a comprehensive audit covering:
- **Technical Accuracy** - Mathematical correctness, claims verification
- **Writing Quality** - Clarity, flow, academic tone
- **Completeness** - All required elements present

## Prerequisites

1. **Gemini CLI installed** - Install from: https://ai.google.dev/gemini-api/docs/cli
2. **API key configured** - Set GOOGLE_API_KEY environment variable
3. **Files ready** - All markdown files in `sections/` directory

## Audit Configuration

All audit prompts are in `audit_config.json`:
- 12 sections with comprehensive prompts
- Expected content checklist for each section
- Specific checks for technical accuracy
- Output format specification

## Quick Start

### Example: Audit Section 1 (Introduction)

```bash
# Navigate to sections directory
cd .artifacts/research/papers/LT7_journal_paper/sections

# Create audits directory
mkdir -p audits

# Run audit (Method 1: Combined file)
cat Section_01_Introduction.md > temp_audit_input.txt
echo "\n\n---AUDIT PROMPT---\n\n" >> temp_audit_input.txt
jq -r '.sections[0].audit_prompt' audit_config.json >> temp_audit_input.txt
gemini < temp_audit_input.txt > audits/Section_01_AUDIT_REPORT.md

# OR Method 2: Manual prompt
# 1. Open Section_01_Introduction.md
# 2. Copy audit_prompt from audit_config.json (sections[0].audit_prompt)
# 3. Paste both into Gemini CLI
# 4. Save output to audits/Section_01_AUDIT_REPORT.md
```

## Step-by-Step Manual Execution

### Step 1: Prepare Audit Inputs

For each section XX (01-12):

1. Open `Section_XX_Name.md` in a text editor
2. Open `audit_config.json` and find the section's `audit_prompt`
3. Combine them for Gemini

### Step 2: Run Gemini CLI

**Option A: Interactive Mode**
```bash
gemini

# Then paste:
# 1. Content from Section_XX_Name.md
# 2. The audit_prompt from audit_config.json
# 3. Type "DONE" or use your CLI's end-of-input method
```

**Option B: File Input**
```bash
# Create combined input file
cat Section_XX_Name.md > temp_input.txt
echo "\n\n=== AUDIT INSTRUCTIONS ===\n\n" >> temp_input.txt
jq -r ".sections[X].audit_prompt" audit_config.json >> temp_input.txt

# Run audit
gemini < temp_input.txt > audits/Section_XX_AUDIT_REPORT.md
```

**Option C: Direct Pipe** (if Gemini CLI supports stdin)
```bash
(cat Section_XX_Name.md && echo "\n\n" && jq -r ".sections[X].audit_prompt" audit_config.json) | gemini > audits/Section_XX_AUDIT_REPORT.md
```

### Step 3: Review Audit Report

Each audit report will contain:

```markdown
# Audit Report: Section XX - [Name]

## SCORES (1-10 scale)
- Technical Accuracy: X/10
- Writing Quality: X/10
- Completeness: X/10
- **Overall: X/10**

## STRENGTHS
1. [Specific strength 1]
2. [Specific strength 2]
3. [Specific strength 3]

## ISSUES FOUND

### CRITICAL (Must Fix)
- [Issue 1 with line reference if possible]
- [Issue 2]

### MINOR (Should Fix)
- [Issue 1]
- [Issue 2]

### SUGGESTIONS (Optional)
- [Suggestion 1]
- [Suggestion 2]

## IMPROVEMENT RECOMMENDATIONS
1. [Actionable recommendation 1]
2. [Actionable recommendation 2]
3. [Actionable recommendation 3]
```

## All Sections Quick Reference

### Section 01: Introduction
- **File:** `Section_01_Introduction.md`
- **Config Index:** `sections[0]`
- **Focus:** Literature survey, research gaps, contributions
- **Key Metrics:** 68 citations, 5 quantified gaps, 6 contributions

```bash
jq -r '.sections[0].audit_prompt' audit_config.json
```

### Section 02: List of Figures
- **File:** `Section_02_List_of_Figures.md`
- **Config Index:** `sections[1]`
- **Focus:** Figure numbering, caption quality
- **Key Metrics:** 14 figures, sequential numbering

```bash
jq -r '.sections[1].audit_prompt' audit_config.json
```

### Section 03: System Model
- **File:** `Section_03_System_Model.md`
- **Config Index:** `sections[2]`
- **Focus:** Mathematical correctness, dimensional analysis
- **Key Metrics:** 10+ equations, physical parameters

```bash
jq -r '.sections[2].audit_prompt' audit_config.json
```

### Section 04: Controller Design
- **File:** `Section_04_Controller_Design.md`
- **Config Index:** `sections[3]`
- **Focus:** 7 controller variants, equations, design rationale
- **Key Metrics:** 7 controllers, 3-5 equations each

```bash
jq -r '.sections[3].audit_prompt' audit_config.json
```

### Section 05: Lyapunov Stability
- **File:** `Section_05_Lyapunov_Stability.md`
- **Config Index:** `sections[4]`
- **Focus:** Mathematical rigor of 4 proofs (Theorems 4.1-4.4)
- **Key Metrics:** 4 theorems, 96.2% validation agreement
- **CRITICAL:** Flag any mathematical errors in proofs

```bash
jq -r '.sections[4].audit_prompt' audit_config.json
```

### Section 06: PSO Methodology
- **File:** `Section_06_PSO_Methodology.md`
- **Config Index:** `sections[5]`
- **Focus:** PSO algorithm, objective function, multi-scenario approach
- **Key Metrics:** 15 scenarios, alpha=0.3 penalty

```bash
jq -r '.sections[5].audit_prompt' audit_config.json
```

### Section 07: Experimental Setup
- **File:** `Section_07_Experimental_Setup.md`
- **Config Index:** `sections[6]`
- **Focus:** Statistical rigor, reproducibility, methodology
- **Key Metrics:** 4 scenarios, 12 metrics, 400-500 Monte Carlo runs

```bash
jq -r '.sections[6].audit_prompt' audit_config.json
```

### Section 08: Performance Results
- **File:** `Section_08_Performance_Results.md`
- **Config Index:** `sections[7]`
- **Focus:** Data consistency, statistical claims, confidence intervals
- **Key Metrics:** 7 controllers, 12 metrics, 95% CI
- **CRITICAL:** Verify all numerical claims are supported

```bash
jq -r '.sections[7].audit_prompt' audit_config.json
```

### Section 09: Robustness Analysis
- **File:** `Section_09_Robustness_Analysis.md`
- **Config Index:** `sections[8]`
- **Focus:** PSO failure analysis (50.4x degradation), robustness testing
- **Key Metrics:** ±20% uncertainty, ±0.3 rad disturbances, 90.2% failure rate
- **CRITICAL:** Verify all major claims (50.4x, 90.2%, 7.5x improvement)

```bash
jq -r '.sections[8].audit_prompt' audit_config.json
```

### Section 10: Discussion
- **File:** `Section_10_Discussion.md`
- **Config Index:** `sections[9]`
- **Focus:** Design guidelines, selection matrix, synthesis
- **Key Metrics:** Table 9.1, evidence-based recommendations

```bash
jq -r '.sections[9].audit_prompt' audit_config.json
```

### Section 11: Conclusion
- **File:** `Section_11_Conclusion.md`
- **Config Index:** `sections[10]`
- **Focus:** Findings summary, no new claims, numerical accuracy
- **Key Metrics:** 3-5 future directions, ~1500 words

```bash
jq -r '.sections[10].audit_prompt' audit_config.json
```

### Section 12: Acknowledgments
- **File:** `Section_12_Acknowledgments.md`
- **Config Index:** `sections[11]`
- **Focus:** Completeness, professional tone
- **Key Metrics:** ~200 words

```bash
jq -r '.sections[11].audit_prompt' audit_config.json
```

## Batch Processing Script

Create `run_all_audits.sh` for automated execution:

```bash
#!/bin/bash
# Run all 12 section audits

mkdir -p audits

for i in {0..11}; do
    # Get section number with zero padding
    section_num=$(printf "%02d" $((i + 1)))

    # Get section name from JSON
    section_name=$(jq -r ".sections[$i].section_name" audit_config.json)

    # Get markdown filename
    md_file=$(jq -r ".sections[$i].markdown_file" audit_config.json)

    # Get audit prompt
    prompt=$(jq -r ".sections[$i].audit_prompt" audit_config.json)

    echo "[INFO] Auditing Section $section_num: $section_name"

    # Create combined input
    cat "$md_file" > temp_input.txt
    echo "\n\n=== AUDIT INSTRUCTIONS ===\n\n" >> temp_input.txt
    echo "$prompt" >> temp_input.txt

    # Run Gemini audit
    gemini < temp_input.txt > "audits/Section_${section_num}_AUDIT_REPORT.md"

    echo "[OK] Created audits/Section_${section_num}_AUDIT_REPORT.md"
    echo ""
done

# Cleanup
rm temp_input.txt

echo "[OK] All 12 audits complete!"
echo "[INFO] Reports saved to audits/ directory"
```

Make executable:
```bash
chmod +x run_all_audits.sh
./run_all_audits.sh
```

## Expected Output Structure

After running all audits, you'll have:

```
sections/
├── audits/
│   ├── Section_01_AUDIT_REPORT.md
│   ├── Section_02_AUDIT_REPORT.md
│   ├── Section_03_AUDIT_REPORT.md
│   ├── Section_04_AUDIT_REPORT.md (CRITICAL: Lyapunov proofs)
│   ├── Section_05_AUDIT_REPORT.md
│   ├── Section_06_AUDIT_REPORT.md
│   ├── Section_07_AUDIT_REPORT.md
│   ├── Section_08_AUDIT_REPORT.md (CRITICAL: Performance claims)
│   ├── Section_09_AUDIT_REPORT.md (CRITICAL: PSO failure)
│   ├── Section_10_AUDIT_REPORT.md
│   ├── Section_11_AUDIT_REPORT.md
│   ├── Section_12_AUDIT_REPORT.md
│   └── AUDIT_SUMMARY.md (create this manually after reviewing all)
├── Section_01_Introduction.md
├── Section_02_List_of_Figures.md
├── ...
├── audit_config.json
└── AUDIT_GUIDE.md (this file)
```

## Post-Audit Analysis

After all audits are complete:

1. **Review CRITICAL sections first:**
   - Section 04 (Lyapunov proofs)
   - Section 08 (Performance claims)
   - Section 09 (PSO failure analysis)

2. **Check overall scores:**
   ```bash
   grep "Overall:" audits/*.md
   ```

3. **Collect all CRITICAL issues:**
   ```bash
   grep -A 5 "CRITICAL" audits/*.md > audits/CRITICAL_ISSUES.txt
   ```

4. **Create summary report:**
   - Average scores across all sections
   - List of all critical issues
   - Top 10 improvement priorities

## Troubleshooting

### Gemini CLI Issues

**Problem:** `gemini: command not found`
- **Solution:** Install Gemini CLI: `pip install google-generativeai-cli`

**Problem:** API key error
- **Solution:** Set environment variable: `export GOOGLE_API_KEY="your-api-key"`

**Problem:** Input too long
- **Solution:** Split large sections (e.g., Section 04 Controller Design) into subsections

### JSON Parsing

**Problem:** `jq: command not found`
- **Solution:** Install jq: `sudo apt install jq` (Linux) or `brew install jq` (Mac)
- **Alternative:** Manually copy audit prompts from `audit_config.json`

## Tips for Better Audits

1. **Run audits on fresh eyes:** Don't audit immediately after writing
2. **Use specific examples:** When Gemini flags issues, ask for specific line references
3. **Iterate:** If an audit seems off, re-run with clarifying questions
4. **Cross-reference:** Compare audit findings across related sections
5. **Focus on CRITICAL sections:** Prioritize mathematical proofs and data claims

## See Also

- `audit_config.json` - Complete audit configuration
- `README.md` - Section PDFs overview
- `../LT7_PROFESSIONAL_FINAL.pdf` - Full paper (71 pages)
- `../LT7_RESEARCH_PAPER.md` - Markdown source (6,932 lines)
