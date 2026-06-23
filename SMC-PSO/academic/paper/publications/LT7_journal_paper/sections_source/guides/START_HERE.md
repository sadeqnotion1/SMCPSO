# Start Here - Simplest Audit Workflow

✅ **ALL 10 AUDIT PROMPTS ARE READY!** Just open, copy, paste!

Files are in: `audits/` (renamed by priority order 01-10)

## What You Need

1. **Gemini CLI installed** - Get it from: https://ai.google.dev/gemini-api/docs/cli
2. **API key set** - `set GOOGLE_API_KEY=your-key` (Windows) or `export GOOGLE_API_KEY=your-key` (Mac/Linux)
3. **No scripts needed** - All prompt files are pre-generated!

## Super Simple 2-Step Process

### Step 1: Open & Copy Prompt File (10 seconds)

```bash
# Navigate to audits directory
cd .artifacts/research/papers/LT7_journal_paper/sections/audits

# Open first priority file (Lyapunov Stability)
start 01-PRIORITY-Lyapunov_Stability-Section_04_PROMPT.txt

# Or in File Explorer, navigate to audits/ and open the file
```

**Then:** Select all (Ctrl+A), Copy (Ctrl+C)

### Step 2: Paste to Gemini & Save (30-60 seconds)

1. Open Gemini CLI: `gemini`
2. Paste (Ctrl+V)
3. Wait for response
4. Copy Gemini's entire response
5. Save to: `audits\01-AUDIT-Section_04_Lyapunov_Stability.md`

**Done! Move to next file: `02-PRIORITY-...`**

## All Section Numbers

| Number | Section | Priority |
|--------|---------|----------|
| 1 | Introduction | Medium |
| 2 | System Model | Medium |
| 3 | Controller Design | Medium |
| 4 | Lyapunov Stability | **HIGH** ⚠️ |
| 5 | PSO Methodology | Medium |
| 6 | Experimental Setup | Medium |
| 7 | Performance Results | **HIGH** ⚠️ |
| 8 | Robustness Analysis | **HIGH** ⚠️ |
| 9 | Discussion | Medium |
| 10 | Conclusion | Low |

**Start with sections 4, 7, 8 (marked HIGH ⚠️)**

## Example: Audit Section 4 (Lyapunov Stability)

**All prompts are already generated and renamed by priority!**

```bash
# The files are in: audits/

# Step 1: Open the first priority file
start audits\01-PRIORITY-Lyapunov_Stability-Section_04_PROMPT.txt

# Step 2: Copy all content (Ctrl+A, Ctrl+C)

# Step 3: Paste into Gemini CLI
gemini
# [Paste content here]

# Step 4: Save Gemini's response to:
# audits\01-AUDIT-Section_04_Lyapunov_Stability.md
```

## What You Get

Each audit report includes:

- **Scores (1-10):** Technical accuracy, writing quality, completeness
- **Strengths:** What's good
- **Issues:** What needs fixing (CRITICAL = must fix)
- **Recommendations:** How to improve

## After Auditing

Check your results:

```bash
# See all scores
grep "Overall:" audits/*_AUDIT_REPORT.md

# Find critical issues
grep "CRITICAL" audits/*_AUDIT_REPORT.md
```

## Total Time

- **Per section:** 5-10 minutes
- **Priority 3 sections (4, 7, 8):** 30 minutes
- **All 10 sections:** 1-2 hours

## Need Help?

See these files for more details:
- `QUICK_AUDIT_GUIDE.md` - Quick reference with more options
- `AUDIT_GUIDE.md` - Complete detailed guide
- `audit_config.json` - All audit prompts

## Ready?

```bash
python generate_audit_prompt.py 4
```

Start with Section 4 (Lyapunov Stability) - it's the most critical!
