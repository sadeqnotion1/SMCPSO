# Troubleshooting Guide - Collapsible Code Blocks

**Last Updated:** 2025-10-12

**What This Guide Covers:**
This troubleshooting guide provides step-by-step solutions for common issues with collapsible code blocks. Each issue includes symptoms, diagnosis procedures, multiple solution paths, and prevention strategies.

**Who This Is For:**
- **End users**: Experiencing issues with code block functionality
- **Developers**: Debugging integration problems
- **Support team**: Assisting users with technical problems
- **Maintainers**: Resolving production issues

**How to Use This Guide:**
1. Find your issue in the table of contents below
2. Check symptoms match your situation
3. Follow diagnosis steps to confirm root cause
4. Try solutions in order (A → B → C)
5. If unresolved, see "Getting Help" section at end

**Quick Diagnosis:**
- **No buttons?** → Issue #1 (JavaScript not loaded)
- **Buttons misaligned?** → Issue #2 (CSS conflict)
- **State not saved?** → Issue #5 (LocalStorage blocked)
- **Slow animations?** → Issue #7 (GPU acceleration disabled)

**Related Documentation:**
- [User Guide](user-guide.md) - Normal usage instructions
- [Configuration Reference](configuration-reference.md) - Settings and options
- [Technical Reference](technical-reference.md) - Architecture details
- [Maintenance Guide](maintenance-guide.md) - Developer procedures

---

## Common Issues & Solutions

### 1.

Collapse Buttons Not Appearing

#### Symptoms

- No collapse buttons visible on code blocks
- Only copy buttons appear

#### Diagnosis

1. Open browser console (F12)
2. Look for `[CodeCollapse]` messages
3. Check for red error messages

#### Solutions

**Solution A: JavaScript Not Loaded**
```javascript
// In console, verify script loaded:
document.querySelector('script[src*="code-collapse.js"]')
// Should return: <script> element
// If null: Script not loaded
```

**Fix:** Verify `conf.py` includes script:
```python
# In docs/conf.py, verify these lines exist:
html_js_files = [
    'code-collapse.js',
]
```

**Solution B: Copy Button Dependency Missing**
```javascript
// In console, check if copybutton.js loaded:
document.querySelector('.copybtn')
// Should return: copy button elements
// If null: copybutton.js missing
```

**Fix:** Install sphinx-copybutton extension:
```bash
pip install sphinx-copybutton
```

**Solution C: Clear Browser Cache**
1. Press Ctrl+Shift+Delete (Windows/Linux) or Cmd+Shift+Delete (Mac)
2. Select "Cached images and files"
3. Clear cache
4. Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

---

### 2.

Animation Feels Janky or Slow

#### Symptoms

- Choppy collapse/expand animation
- Visible stutter or lag

#### Diagnosis

1. Open DevTools → Performance tab
2. Click "Record" button
3. Collapse a code block
4. Stop recording
5. Check FPS chart (should be ≥55 FPS)

#### Solutions

**Solution A: Enable GPU Acceleration (Chrome)**
1. Navigate to `chrome://flags`
2. Search "hardware acceleration"
3. Enable "Hardware-accelerated video decode"
4. Restart browser

**Solution B: Disable Browser Extensions**
1. Open Incognito/Private mode (extensions disabled by default)
2. Test collapse/expand functionality
3. If smooth: Disable extensions one by one to find culprit
4. Common culprits: Ad blockers, CSS injectors, animation modifiers

**Solution C: Update Browser**

Minimum supported versions:
- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+

Check current version and update if below minimum.

---

### 3.

Code Blocks Not Staying Collapsed

#### Symptoms

- Collapse a code block
- Reload page
- Block is expanded again (state not persisted)

#### Diagnosis

```javascript
// In console, check localStorage:
localStorage.getItem('code-block-states')
// Should return: JSON string like {"0":"collapsed","3":"collapsed"}
// If null: State not saving
```

#### Solutions

**Solution A: LocalStorage Disabled**
1. Check browser privacy settings
2. Enable "Allow sites to save data"
3. Ensure not in Private/Incognito mode (state won't persist in these modes)

**Solution B: Clear and Retry**
```javascript
// In console, clear saved states:
clearCodeBlockStates()

// Collapse a code block
// Reload page
// Check if it stayed collapsed
```

**Solution C: Quota Exceeded**
```javascript
// In console, check localStorage size:
JSON.stringify(localStorage).length
// If >5MB: Clear old data
localStorage.clear()
```

---

### 4.

Console Shows "X Unmatched <pre> Elements"

#### Symptoms

- Warning in console: `⚠️ X unmatched <pre> elements found`

#### Diagnosis

Console output shows:
```
[CodeCollapse] ⚠️ 2 unmatched <pre> elements found:
  [1] Parent classes: "amsmath"
  [2] Parent classes: "math"
```

#### Is This a Problem?

**Expected (Not a bug):**
- Math blocks: `.amsmath`, `.math`, `.nohighlight`
- Very short code snippets (<10 characters)
- Inline code (not in `.highlight` container)

**Unexpected (Potential bug):**
- Code blocks in `.highlight` container not matched
- Programming language code blocks missing buttons

#### Action Needed

- If unmatched = math blocks: ✅ OK (intentional exclusion)
- If unmatched = code blocks: ❌ Report as bug with console output

---

### 5.

Buttons Overlap Copy Button

#### Symptoms

- Collapse and copy buttons on top of each other
- Hard to click either button
- Buttons visually merged

#### Diagnosis

1. Right-click between buttons → Inspect Element
2. Check CSS in DevTools → Styles tab
3. Look for `.copybtn + .code-collapse-btn` margin

#### Solutions

**Solution: Adjust Spacing**
```css
/* In code-collapse.css, find this rule (around line 104-106): */
.copybtn + .code-collapse-btn {
    margin-left: 12px;  /* Increase gap (default: 8px) */
}
```yaml

Recommended values:
- Desktop: 8-12px
- Mobile: 5-8px

---

### 6.

Keyboard Shortcuts Not Working

#### Symptoms

- Ctrl+Shift+C doesn't collapse all
- Ctrl+Shift+E doesn't expand all

#### Diagnosis

1. Check if shortcuts conflict with browser/OS
2. **Chrome**: Ctrl+Shift+C opens DevTools (conflict!)
3. **Windows**: Some shortcuts reserved by OS

#### Solutions

**Solution A: Use Master Control Buttons**
- Click "Collapse All" button at top of page
- Click "Expand All" button at top of page

**Solution B: Change Shortcuts (For Developers)**
```javascript
// In code-collapse.js, find keyboard event handler (around line 424-433)
// Change 'C' to 'K' and 'E' to 'J' to avoid conflicts:

if (e.ctrlKey && e.shiftKey && e.key === 'K') {  // Changed from 'C'
    collapseAll();
    e.preventDefault();
}
else if (e.ctrlKey && e.shiftKey && e.key === 'J') {  // Changed from 'E'
    expandAll();
    e.preventDefault();
}
```

---

### 7.

Print Preview Shows Collapsed Blocks

#### Symptoms

- Print preview shows "Code hidden..." message
- Code blocks not expanded when printing

#### Expected Behavior

Code blocks should **automatically expand** when printing.

#### Diagnosis

This should not happen - print styles force expansion.

If it happens:
1. Check browser's print CSS support
2. Try "Print as PDF" option
3. Check if print styles are loaded

#### Solutions

**Verify Print Styles:**
```css
/* In code-collapse.css, verify this rule exists (around line 225-233): */
@media print {
    div[class*="highlight"] pre {
        max-height: none !important;
        opacity: 1 !important;
    }
    .code-collapse-btn {
        display: none !important;
    }
}
```

**Workaround:**
1. Click "Expand All" before printing
2. Print
3. Click "Collapse All" after printing (if needed)

---

### 8.

Dark Mode Issues

#### Symptoms

- Buttons invisible in dark mode
- Poor contrast with dark background

#### Diagnosis

1. Toggle dark mode (if available)
2. Check button visibility
3. Inspect button styles in DevTools

#### Solutions

**Customize Dark Mode Colors:**
```css
/* In code-collapse.css, find dark mode section (around line 181-203): */
[data-theme="dark"] .code-collapse-btn {
    background: rgba(255, 255, 255, 0.15);  /* Adjust transparency */
    color: #ffffff;                         /* Adjust text color */
}

[data-theme="dark"] .code-collapse-btn:hover {
    background: rgba(255, 255, 255, 0.25);  /* Adjust hover state */
}
```

**Test:**
1. Rebuild docs
2. Toggle dark mode
3. Verify button visibility

---

### 9.

Mobile Touch Issues

#### Symptoms

- Hard to tap buttons on mobile
- Buttons too small
- Accidental taps on wrong button

#### Diagnosis

1. Open DevTools → Device toolbar (Ctrl+Shift+M)
2. Emulate mobile device (320px width)
3. Try tapping collapse buttons

#### Solutions

**Increase Touch Target Size:**
```css
/* In code-collapse.css, find mobile section (around line 156-170): */
@media (max-width: 768px) {
    .code-collapse-btn {
        padding: 6px 12px;  /* Increase from 3px 6px */
        font-size: 1.2rem;  /* Larger icon (default: 1rem) */
        min-width: 44px;    /* Apple recommends 44×44px minimum */
        min-height: 44px;
    }
}
```

---

### 10.

Feature Works Locally But Not on Server

#### Symptoms

- Works on `localhost` during development
- Doesn't work on deployed documentation site

#### Diagnosis

1. Check server's deployed `_static` directory
2. Verify files uploaded: `code-collapse.js`, `code-collapse.css`

#### Solutions

**Verify Deployment:**
```bash
# Check files on server (replace URL with your docs site):
curl https://your-docs-site.com/_static/code-collapse.js
curl https://your-docs-site.com/_static/code-collapse.css

# Should return: file contents (not 404 error)
```

**Clear CDN Cache:**

If using CDN (Cloudflare, Fastly, AWS CloudFront, etc.):
1. Purge cache for `_static/*` files
2. Wait 5-10 minutes for propagation
3. Hard refresh browser (Ctrl+Shift+R)

**Check File Permissions:**
```bash
# On server, verify files are readable:
ls -la _build/html/_static/code-collapse.*

# Should show: -rw-r--r-- (readable by all)
```

---

## Getting Help

### 1.

Check Documentation

Before reporting an issue, review:
- **User Guide**: `user-guide.md` (basic usage)
- **Technical Reference**: `technical-reference.md` (architecture)
- **Testing Procedures**: `../../testing/TESTING_PROCEDURES.md`

### 2.

Browser Console Debug Info

Enable and collect debug information:
```javascript
// In console, check for debug messages:
// Look for lines starting with: [CodeCollapse]

// Example output:
[CodeCollapse] Found 42 code blocks
[CodeCollapse] ✅ 100% coverage (42 matched, 0 unmatched)
[CodeCollapse] Selector performance: [table]
```

### 3. Report a Bug

Include in bug report:
- **Browser version**: (Chrome 118, Firefox 119, etc.)
- **Operating system**: (Windows 11, macOS 14, etc.)
- **Console error messages**: (screenshot or copy/paste)
- **Steps to reproduce**:
  1. Open page
  2. Do action X
  3. See error Y
- **Expected vs actual behavior**
- **Screenshots** (if visual issue)

### 4.

Community Support

- **GitHub Issues**: [Link to your repository]
- **Documentation**: [Link to this guide]
- **Email**: [Maintainer contact]

---

## Quick Diagnostics Script

Run this in browser console for full diagnostic report:

```javascript
console.log('=== Code Collapse Diagnostics ===');
console.log('Script loaded:', !!document.querySelector('script[src*="code-collapse.js"]'));
console.log('CSS loaded:', !!document.querySelector('link[href*="code-collapse.css"]'));
console.log('Copy button extension:', !!document.querySelector('.copybtn'));
console.log('Code blocks found:', document.querySelectorAll('.code-collapse-btn').length);
console.log('LocalStorage enabled:', !!window.localStorage);
console.log('Saved states:', localStorage.getItem('code-block-states'));
console.log('Browser:', navigator.userAgent);
console.log('Viewport:', window.innerWidth + 'x' + window.innerHeight);
```

---

## Still Having Issues?

If none of the above solutions work:

1. **Clear all browser data** (nuclear option):
   - Settings → Privacy → Clear browsing data
   - Select: Cache, Cookies, Site data
   - Time range: All time

2. **Try different browser**:
   - Test in Chrome, Firefox, Edge
   - Helps isolate browser-specific issues

3. **Disable all extensions**:
   - Test in Incognito/Private mode
   - Extensions can interfere with DOM manipulation

4. **Check for JavaScript errors**:
   - Open console (F12)
   - Look for red error messages
   - Copy/paste exact error text when reporting

5. **Report bug with diagnostic info**:
   - Use quick diagnostics script above
   - Include all output in bug report
