# Collapsible Code Blocks - Testing Procedures

**Phase 5: Testing & Validation**
**Last Updated:** 2025-10-12

---

## Table of Contents

1. [Overview](#overview)
2. [Test Environment Setup](#test-environment-setup)
3. [Automated Verification](#automated-verification)
4. [Manual Browser Testing](#manual-browser-testing)
5. [Performance Testing](#performance-testing)
6. [Accessibility Testing](#accessibility-testing)
7. [Troubleshooting](#troubleshooting)
8. [Reporting](#reporting)

---

## Overview

This document provides step-by-step procedures for validating the collapsible code blocks feature implemented in Phases 1-4.

**Test Duration:** 2-2.5 hours (comprehensive) or 30 minutes (smoke test)

**Prerequisites:**
- Modern browser (Chrome, Firefox, or Edge recommended)
- Browser DevTools knowledge (basic)
- Access to local build: `docs/_build/html/index.html`

---

## Test Environment Setup

### Step 1:

Verify Build Files

```bash
# Check files exist and are recent
ls -lh docs/_build/html/_static/code-collapse.*

# Expected output:
# code-collapse.css  ~8.9KB  (modified today)
# code-collapse.js   ~21KB   (modified today)
```

### Step 2:

Open Test Page

**Option A: File Protocol**
```
file:///D:/Projects/main/docs/_build/html/index.html
```

**Option B: Local Server** (recommended for full testing)
```bash
# From docs/_build/html directory
python -m http.server 8000

# Then open: http://localhost:8000/index.html
```

### Step 3:

Open Browser DevTools

- **Windows/Linux:** Press `F12` or `Ctrl+Shift+I`
- **Mac:** Press `Cmd+Option+I`

**Required Tabs:**
- Console (for debug logs)
- Performance (for FPS measurement)
- Rendering (for GPU verification)

---

## Automated Verification

### Console Coverage Report

**Expected Output:**
```javascript
[CodeCollapse] Found X code blocks (Y raw matches)
[CodeCollapse] Total <pre> elements: Z
[CodeCollapse] ✅ 100% coverage - all <pre> elements matched

┌─────────────────────────────────────────────┬───────┐
│ Selector                                    │ Count │
├─────────────────────────────────────────────┼───────┤
│ div.notranslate[class*="highlight-"]        │ XX    │
│ div[class*="highlight-"]:not(.nohighlight)  │ XX    │
│ div.doctest                                 │ X     │
│ div.literal-block                           │ X     │
│ div.code-block                              │ X     │
│ pre.literal-block                           │ X     │
└─────────────────────────────────────────────┴───────┘
```

**✅ Pass Criteria:**
- Message: `✅ 100% coverage - all <pre> elements matched`
- No warnings: `⚠️ X unmatched <pre> elements found`
- Selector table shows counts for all selectors

**❌ Fail Actions:**
- Check if unmatched `<pre>` elements are math blocks (expected exclusion)
- If real code blocks are unmatched, file a P0 bug

### Verify Debug Features

```bash
# Count debug logging statements
grep -c "console\." docs/_build/html/_static/code-collapse.js

# Expected: 12+ statements
```

### Verify Phase 4 Improvements

```bash
# Check for requestAnimationFrame (double-RAF pattern)
grep -c "requestAnimationFrame" docs/_build/html/_static/code-collapse.js

# Expected: 6 occurrences

# Check for GPU acceleration
grep "will-change\|contain: layout\|translateZ" docs/_build/html/_static/code-collapse.css

# Expected:

Multiple matches
```

---

## Manual Browser Testing

### Test 1:

Button Insertion (5min)

**Procedure:**
1. Load page in browser
2. Scroll through page
3. Visually inspect all code blocks

**Checks:**
- [ ] All code blocks have collapse button (▼)
- [ ] All code blocks have copy button
- [ ] Buttons are adjacent (not separated)
- [ ] Gap between buttons = 5-8px (estimate visually)

**Measurement (Precise):**
1. Right-click on space between buttons → Inspect
2. In DevTools → Styles tab
3. Look for `.copybtn + .code-collapse-btn { margin-left: 8px; }`
4. Confirm 8px gap (5px on mobile)

### Test 2:

Collapse Animation (5min)

**Procedure:**
1. Find a medium-sized code block (10-20 lines)
2. Click collapse button (▼)
3. Observe animation

**Checks:**
- [ ] Code slides up smoothly (curtain effect)
- [ ] Animation duration feels natural (~350ms)
- [ ] Button changes to expand icon (▲)
- [ ] Message appears: "Code hidden (click ▲ to expand)"
- [ ] No visible jank or stuttering

### Test 3:

Expand Animation (5min)

**Procedure:**
1. Click expand button (▲) on collapsed block
2. Observe animation

**Checks:**
- [ ] Code slides down smoothly
- [ ] Animation duration consistent with collapse
- [ ] Button changes to collapse icon (▼)
- [ ] Message disappears
- [ ] Final state matches original (no layout shift)

### Test 4:

Master Controls (3min)

**Procedure:**
1. Scroll to top of page
2. Find master control bar

**Checks:**
- [ ] Control bar visible with count: "X code blocks:"
- [ ] Two buttons present: "Collapse All" and "Expand All"

**Test Collapse All:**
1. Click "Collapse All"
2. Verify all code blocks collapse
3. Verify smooth stagger effect (if multiple blocks)

**Test Expand All:**
1. Click "Expand All"
2. Verify all code blocks expand

### Test 5:

State Persistence (3min)

**Procedure:**
1. Collapse 2-3 specific code blocks (note which ones)
2. Reload page (F5)
3. Verify same blocks remain collapsed

**Clear State Test:**
1. Open browser console
2. Run: `clearCodeBlockStates()`
3. Verify console shows: `Code block states cleared`
4. Reload page
5. Verify all blocks expanded

### Test 6:

Keyboard Shortcuts (2min)

**Procedure:**
1. Press `Ctrl+Shift+C` (Windows/Linux) or `Cmd+Shift+C` (Mac)
2. Verify all code blocks collapse

3. Press `Ctrl+Shift+E` (Windows/Linux) or `Cmd+Shift+E` (Mac)
4. Verify all code blocks expand

**Note:** If shortcuts don't work, check for browser extension conflicts.

---

## Performance Testing

### FPS Measurement (15min)

**Setup:**
1. Open DevTools → Performance tab
2. Find a large code block (30+ lines)

**Procedure:**
1. Click record button (circle) in Performance tab
2. Click collapse button on large code block
3. Wait for animation to complete
4. Stop recording (click stop button)

**Analysis:**
1. Look at FPS chart (top of timeline)
2. During animation, FPS should be ≥55 (green line)
3. Check for red/yellow bars (frame drops)

**Chrome Performance Insights:**
1. Click "Insights" button (if available)
2. Look for layout shift warnings
3. Target: No warnings during animation

**Success Criteria:**
- ✅ FPS ≥ 55 during animation
- ✅ No layout shift warnings
- ✅ Consistent frame timing (no spikes)

### GPU Acceleration Check (10min)

**Setup:**
1. Open DevTools → Rendering tab (three dots → More tools → Rendering)
2. Enable:
   - ✅ Paint flashing
   - ✅ Layer borders

**Procedure:**
1. Collapse a code block
2. Observe visual indicators

**Expected Behavior:**
- **Green border** appears around code block (indicates GPU layer)
- **Minimal paint flashing** (only animation area flashes, not whole page)
- **Orange border** on collapse button (composited layer)

**Success Criteria:**
- ✅ Green layer borders visible
- ✅ Paint flashing contained to animation area
- ✅ No purple/red flashing (indicates layout thrashing)

### Layout Shift Test (5min)

**Procedure:**
1. Open DevTools → Performance tab
2. Record while collapsing/expanding
3. Check for layout shift events in timeline

**Chrome DevTools:**
- Look for "Layout Shift" entries in timeline
- Click on them to see CLS (Cumulative Layout Shift) score

**Success Criteria:**
- ✅ CLS < 0.1 (Google Core Web Vitals threshold)
- ✅ No unexpected layout shifts outside code block

---

## Accessibility Testing

### Keyboard Navigation (10min)

**Procedure:**
1. Click in address bar (to reset focus)
2. Press `Tab` repeatedly
3. Observe focus indicator moving through page

**Checks:**
- [ ] Collapse buttons receive focus (blue outline)
- [ ] Focus indicator clearly visible
- [ ] Focus order logical (top to bottom)
- [ ] Pressing `Enter` or `Space` toggles collapse

**Master Controls:**
- [ ] "Collapse All" button focusable
- [ ] "Expand All" button focusable
- [ ] Pressing `Enter` activates button

### ARIA Attributes (5min)

**Procedure:**
1. Inspect a collapse button (right-click → Inspect)
2. Check HTML attributes in Elements tab

**Expected Attributes:**
```html
<button class="code-collapse-btn"
        aria-label="Toggle code block visibility"
        aria-expanded="true"
        title="Collapse code block">
```

**Checks:**
- [ ] `aria-label` present and descriptive
- [ ] `aria-expanded="true"` when expanded
- [ ] `aria-expanded="false"` when collapsed
- [ ] `aria-expanded` updates on toggle

### Screen Reader Test (Optional - 10min)

**Tools:**
- Windows: NVDA (free) or JAWS
- Mac: VoiceOver (built-in)
- Linux: Orca

**Procedure:**
1. Start screen reader
2. Navigate to collapse button (Tab key)
3. Listen to announcement

**Expected Announcement:**
- "Toggle code block visibility, button, expanded" (or similar)
- When collapsed: "Toggle code block visibility, button, collapsed"

### Reduced Motion Test (5min)

**Setup:**
1. DevTools → Rendering tab
2. Enable "Emulate CSS media prefers-reduced-motion"

**Procedure:**
1. Click collapse button
2. Observe behavior

**Expected:**
- ✅ Code collapses instantly (no animation)
- ✅ Button still functions
- ✅ State still persists

**Disable Test:**
1. Disable "prefers-reduced-motion"
2. Verify animations return

### High Contrast Mode (Windows only - 5min)

**Procedure:**
1. Press `Left Alt + Left Shift + Print Screen`
2. Enable High Contrast mode
3. Reload page

**Checks:**
- [ ] Buttons have thicker borders (3px)
- [ ] Text readable
- [ ] Sufficient color contrast
- [ ] Buttons still functional

---

## Troubleshooting

### Issue: No Collapse Buttons Appear

**Check 1:** Verify files loaded
```javascript
// In browser console
document.querySelector('script[src*="code-collapse.js"]')
// Should return: <script> element
```

**Check 2:** Check for JavaScript errors
- Open Console tab
- Look for red error messages
- Check if copybutton.js loaded before code-collapse.js

**Check 3:** Verify code blocks exist
```javascript
document.querySelectorAll('pre').length
// Should return: > 0
```

### Issue:

Console Shows "X unmatched <pre> elements"

**Diagnosis:**
- This is expected for math blocks (LaTeX equations)
- Check unmatched elements in console warning

**Action:**
- If unmatched elements are math blocks: OK (expected exclusion)
- If unmatched elements are code blocks: File a bug

### Issue:

Animations Feel Janky

**Check 1:** GPU acceleration active
- DevTools → Rendering → Layer borders
- Verify green borders appear

**Check 2:** Measure FPS
- DevTools → Performance → Record animation
- Check FPS chart for drops below 55

**Check 3:** Browser extensions
- Try in Incognito/Private mode
- Disable extensions one by one

### Issue:

State Not Persisting

**Check 1:** LocalStorage enabled
```javascript
// In console
localStorage.setItem('test', 'test')
localStorage.getItem('test')
// Should return: "test"
```

**Check 2:** Verify state saved
```javascript
localStorage.getItem('code-block-states')
// Should return: JSON string with block states
```

**Check 3:** Clear and retry
```javascript
clearCodeBlockStates()
// Then try collapsing again
```

---

## Reporting

### Quick Summary Template

```markdown
**Browser:** Chrome 118.0.5993.89
**Date:** 2025-10-12
**Tester:** John Doe

**Results:**
- ✅ Functional: 5/5 tests passed
- ✅ Performance: FPS 58 avg, CLS 0.03
- ✅ Accessibility: 4/4 criteria met
- ⚠️ Edge case: LocalStorage disabled warning too subtle

**Recommendation:** Pass with minor note for localStorage UX
```

### Full Report

**Use:** `docs/testing/code_collapse_validation_report.md`
- Fill in all test sections
- Attach screenshots
- Document browser versions
- List any issues discovered

---

## Phase 5 Completion Criteria

**Required:**
- [ ] All 7 test categories completed
- [ ] Validation report filled out
- [ ] Browser testing checklist completed
- [ ] No P0 (critical) bugs
- [ ] 90%+ success rate across metrics

**Optional:**
- [ ] Screen reader testing completed
- [ ] Safari testing completed
- [ ] Performance profiling attached
- [ ] Screenshots documented

**Sign-Off:**
- [ ] Tester reviewed results
- [ ] Phase 5 marked complete
- [ ] Ready for Phase 6 (Documentation & Maintenance)

---

## Additional Resources

**Related Files:**
- Validation Report: `docs/testing/code_collapse_validation_report.md`
- Browser Checklist: `docs/testing/BROWSER_TESTING_CHECKLIST.md`
- Source Code: `docs/_static/code-collapse.js`
- Styles: `docs/_static/code-collapse.css`

**Browser DevTools Documentation:**
- Chrome: https://developer.chrome.com/docs/devtools/
- Firefox: https://firefox-source-docs.mozilla.org/devtools-user/
- Edge: https://docs.microsoft.com/microsoft-edge/devtools-guide-chromium/

**Accessibility Tools:**
- NVDA Screen Reader: https://www.nvaccess.org/
- WAVE Accessibility Tool: https://wave.webaim.org/
- axe DevTools: https://www.deque.com/axe/devtools/
