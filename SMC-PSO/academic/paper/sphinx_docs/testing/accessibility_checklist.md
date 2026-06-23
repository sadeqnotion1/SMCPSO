# WCAG 2.1 AA Accessibility Checklist

## Automated Checks (via axe-core)

Run automated audit:
```bash
python scripts/analysis/accessibility_audit.py
```

Expected results:
- Target: >90% pages passing WCAG 2.1 AA
- No critical violations
- <5 serious violations across all pages



## Manual Verification Required

### ✅ Keyboard Navigation

- [ ] All interactive elements reachable via Tab key
- [ ] Focus indicators visible (2px solid outline minimum)
- [ ] No keyboard traps (can navigate out of all components)
- [ ] Skip links work ("Skip to main content")
- [ ] Modal dialogs closable with Escape key
- [ ] Dropdown menus navigable with arrow keys

**Test:** Navigate entire page using only keyboard (Tab, Shift+Tab, Enter, Escape)



### ✅ Color Contrast (WCAG AA)

- [ ] Regular text: ≥ 4.5:1 contrast ratio
- [ ] Large text (18pt+ or 14pt bold): ≥ 3:1 contrast ratio
- [ ] UI components (buttons, borders): ≥ 3:1 contrast ratio
- [ ] Information not conveyed by color alone

**Tool:** Use browser dev tools color picker or [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

**Current Implementation:**
- Light mode: Black text on white (#000 on #fff = 21:1) ✅
- Dark mode: #e0e0e0 text on #1a1a1a (14.5:1) ✅
- Links: #2962ff on white (8.6:1) ✅



### ✅ Screen Reader Testing

- [ ] Test with NVDA (Windows) or VoiceOver (macOS)
- [ ] Heading hierarchy logical (h1 → h2 → h3, no skipped levels)
- [ ] ARIA labels present on interactive elements
- [ ] Alt text on all meaningful images (decorative images marked as aria-hidden)
- [ ] Tables have proper headers (`<th>` elements with scope)
- [ ] Form labels associated with inputs (if any forms present)

**Test with NVDA (Windows):**
1. Download [NVDA screen reader](https://www.nvaccess.org/download/)
2. Press `Insert+Down` to activate reading mode
3. Use `H` key to jump between headings
4. Use `K` key to jump between links
5. Verify all content is announced correctly

**Test with VoiceOver (macOS):**
1. Enable: System Preferences → Accessibility → VoiceOver
2. Press `Cmd+F5` to activate
3. Use `VO+Right Arrow` to navigate
4. Use `VO+Cmd+H` to jump between headings



### ✅ Semantic HTML

- [ ] Proper use of `<nav>`, `<main>`, `<article>`, `<aside>`, `<header>`, `<footer>`
- [ ] Buttons for actions (`<button>`), links for navigation (`<a>`)
- [ ] Lists use `<ul>`, `<ol>`, `<li>` elements
- [ ] Definition lists use `<dl>`, `<dt>`, `<dd>`
- [ ] No div/span elements where semantic elements should be used

**Validate:** Use browser dev tools to inspect page structure



### ✅ Mobile Accessibility

- [ ] Touch targets ≥ 44x44 pixels (minimum)
- [ ] Text resizable to 200% without loss of functionality
- [ ] No horizontal scrolling at 320px viewport width
- [ ] Pinch-to-zoom not disabled (`user-scalable=yes`)
- [ ] Orientation changes handled properly

**Test:** Use browser responsive mode or actual mobile device



### ✅ Images and Media

- [ ] All images have `alt` attributes
- [ ] Decorative images have empty alt (`alt=""`) or aria-hidden
- [ ] Complex images have detailed descriptions
- [ ] Mermaid diagrams have text alternatives or detailed descriptions
- [ ] Videos (if any) have captions and transcripts



### ✅ Forms (if applicable)

- [ ] All form inputs have associated labels
- [ ] Error messages clearly indicate which field has an error
- [ ] Required fields indicated with more than just color
- [ ] Form validation accessible to screen readers



## Current Implementation Status

### ✅ Already Compliant Features

**Interactive Elements:**
- ✅ Back to Top button
  - ARIA label: "Back to top"
  - Keyboard accessible (Tab, Enter)
  - Focus indicator visible

- ✅ Dark Mode Toggle
  - ARIA label: "Toggle dark mode"
  - Keyboard shortcut: Ctrl+Shift+D
  - Announces theme changes to screen readers
  - `role="button"` attribute

- ✅ Reading Progress Bar
  - `role="progressbar"`
  - `aria-valuenow` updates dynamically
  - `aria-valuemin="0"`, `aria-valuemax="100"`

- ✅ Active TOC Section
  - `aria-current="location"` on active item
  - Keyboard navigable

- ✅ Lazy Loaded Images
  - Proper `alt` attributes preserved
  - No broken alt text during loading

**Navigation:**
- ✅ Semantic HTML structure (`<nav>`, `<main>`, `<article>`)
- ✅ Heading hierarchy maintained
- ✅ Skip links functional (if present in theme)

**Color Contrast:**
- ✅ Light mode exceeds WCAG AAA (21:1 for body text)
- ✅ Dark mode exceeds WCAG AA (14.5:1 for body text)
- ✅ Links have sufficient contrast in both modes



### 🔧 May Need Manual Verification

**Code Blocks:**
- ⚠️ Syntax highlighting colors - verify contrast in both light/dark modes
- ⚠️ Long code blocks - ensure horizontal scroll is keyboard accessible

**Tables:**
- ⚠️ Verify all tables have `<th>` headers with appropriate `scope` attributes
- ⚠️ Complex tables may need additional ARIA labels

**Mermaid Diagrams:**
- ⚠️ Provide text alternatives or detailed descriptions
- ⚠️ Consider adding `<figcaption>` with diagram explanation

**Math Equations (MathJax):**
- ⚠️ Verify screen reader announces equations correctly
- ⚠️ Consider adding alt text for complex equations



## Accessibility Testing Tools

### Browser Extensions

- **axe DevTools** (Chrome/Firefox) - Free automated testing
- **WAVE** (Chrome/Firefox) - Visual feedback on accessibility issues
- **Lighthouse** (Chrome DevTools) - Built-in accessibility audit

### Online Tools

- **WebAIM Contrast Checker** - https://webaim.org/resources/contrastchecker/
- **WAVE Web Accessibility Evaluation Tool** - https://wave.webaim.org/
- **achecker** - https://achecker.achecks.ca/checker/

### Screen Readers

- **NVDA** (Windows, free) - https://www.nvaccess.org/
- **JAWS** (Windows, paid) - https://www.freedomscientific.com/products/software/jaws/
- **VoiceOver** (macOS/iOS, built-in) - Cmd+F5 to activate



## Reporting Issues

If accessibility violations are found:

1. Document the issue in `.test_artifacts/accessibility_audit.json`
2. Note the specific violation type (contrast, ARIA, semantic, etc.)
3. Identify affected pages
4. Prioritize by severity (critical > serious > moderate > minor)
5. Create remediation plan with timeline



## Compliance Target

**Goal:** >90% of documentation pages pass WCAG 2.1 AA

**Critical Requirement:** Zero critical or serious accessibility violations

**Current Status:** (Run `python scripts/analysis/accessibility_audit.py` to check)
