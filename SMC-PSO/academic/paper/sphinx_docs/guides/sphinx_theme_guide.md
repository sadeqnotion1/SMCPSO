# Sphinx Theme Guide

**Purpose**: Technical reference for the custom Sphinx theme implementation
**Audience**: Documentation maintainers, theme developers
**Last Updated**: 2025-10-16

---

## Theme Overview

The DIP SMC PSO documentation uses a custom Sphinx theme built on the **PyData Sphinx Theme** with extensive CSS customizations for enhanced visual design, accessibility, and user experience.

**Base Theme**: PyData Sphinx Theme 0.15+
**Custom CSS**: `docs/_static/custom.css` (1,682 lines)
**Design System**: Phase 3 Design Tokens v2.0.0

---

## Architecture

### Theme Layers

```
Sphinx HTML Build
    │
    ├─ PyData Sphinx Theme (base)
    │   └─ Bootstrap 5 grid system
    │
    ├─ Design Tokens (CSS variables)
    │   └─ docs/_static/design-tokens.css
    │
    └─ Custom Theme Extensions
        ├─ custom.css (main theme)
        ├─ code-collapse.css (interactive code blocks)
        ├─ mathviz.css (LaTeX rendering)
        ├─ plotly-charts.css (data visualization)
        └─ pwa.css (progressive web app features)
```

### File Structure

```
docs/_static/
├── custom.css                 # Main theme (this guide)
├── design-tokens.css          # Color/spacing tokens
├── code-collapse.css          # Collapsible code blocks
├── code-collapse.js           # Code block interactions
├── dark-mode.js               # Theme switcher
├── mathviz.css                # LaTeX equation styling
├── plotly-integration.js      # Interactive charts
├── icons/                     # SVG icon library
├── css-themes/                # Alternative color schemes
└── back-to-top.js             # Scroll-to-top button
```

---

## Custom CSS Sections

`docs/_static/custom.css` is organized into 25 major sections:

### 1. Design Tokens (Lines 1-104)

**Purpose**: CSS custom properties for colors, spacing, typography, shadows

**Key Variables**:
```css
--color-primary: #2563eb;        /* Brand blue (8.21:1 contrast) */
--color-success: #10b981;        /* Green status */
--color-warning: #f59e0b;        /* Orange alerts */
--color-error: #ef4444;          /* Red errors */
--space-4: 16px;                 /* Base spacing unit */
--font-size-body-1: 1rem;        /* Body text (16px) */
--shadow-md: 0 6px 18px ...;     /* Medium elevation shadow */
```

**Usage**: Reference tokens throughout CSS for consistency:
```css
.my-element {
    color: var(--color-primary);
    padding: var(--space-4);
}
```

### 2. Animated Admonitions (Lines 256-383)

**Purpose**: Styled callout boxes (note, warning, tip, danger, success)

**Features**:
- Gradient backgrounds with brand colors
- Animated icon circles (pulse, glow effects)
- Hover lift animation
- Semantic color coding

**Example**:
```rst
.. note::
   This is a note admonition with animated blue icon.

.. warning::
   This is a warning with pulsing orange icon.
```

### 3. Status Badges (Lines 386-465)

**Purpose**: Visual indicators for feature stability (stable, experimental, beta, deprecated)

**Features**:
- Gradient backgrounds
- Icon prefixes (✓, ⚡, β, ⊘)
- Hover animations
- Uppercase typography with tracking

**HTML Usage**:
```html
<span class="status-badge status-stable">Stable</span>
<span class="status-badge status-experimental">Experimental</span>
```

### 4. Code Blocks (Lines 468-520)

**Purpose**: Syntax highlighting for code examples

**Features**:
- Dark background (#1e293b slate)
- Header bar with gradient
- Line numbers with custom styling
- Horizontal scroll for overflow
- Border and shadow for depth

**Automatic** via Sphinx `highlight` directive:
```rst
.. code-block:: python
   :linenos:

   def compute_control(state):
       return -K * tanh(s / epsilon)
```

### 5. Tables (Lines 523-573)

**Purpose**: Modern data table styling

**Features**:
- Separated borders with rounded corners
- Gradient header (blue primary colors)
- Striped rows (nth-child alternate bg)
- Hover highlights
- Enhanced font size (15px, UI-011 fix)

**Automatic** for all docutils tables:
```rst
.. list-table::
   :header-rows: 1

   * - Metric
     - Formula
   * - ISE
     - ∫‖x‖² dt
```

### 6. Buttons & Links (Lines 576-605)

**Purpose**: Call-to-action buttons with gradient styling

**Features**:
- Primary gradient (blue to dark blue)
- Hover lift animation
- Shadow elevation
- Icon prefixes (download arrow)

**CSS Classes**:
```html
<a href="file.pdf" class="download-link">Download PDF</a>
<button class="btn-primary">Get Started</button>
```

### 7. Callout Boxes (Lines 608-638)

**Purpose**: Bordered callout boxes for highlights

**Features**:
- Left border accent (5px solid)
- Gradient backgrounds
- Semantic color variants (info, success, warning, danger)

**HTML Usage**:
```html
<div class="callout callout-info">
  <p>Important information here.</p>
</div>
```

### 8. Dark Mode (Lines 641-676)

**Purpose**: Dark theme color overrides

**Trigger**: `[data-theme="dark"]` attribute on `<html>`

**Overrides**:
- Background colors (dark slate tones)
- Text colors (light grays)
- Border colors (dark borders)
- Shadow opacities (stronger for dark backgrounds)

**Toggle**: `docs/_static/dark-mode.js` handles theme switching

### 9. Animations & Interactions (Lines 679-710)

**Purpose**: Smooth interactions and loading states

**Features**:
- Smooth scroll behavior
- Custom selection color (brand blue)
- Focus outlines for accessibility
- Shimmer loading skeletons

### 10. Print Styles (Lines 713-728)

**Purpose**: Optimize for printing

**Actions**:
- Disable animations
- Remove shadows
- Simplify colors

### 11-21. UI Fixes (Lines 731-1547)

**Purpose**: Targeted fixes for specific UI issues from Phase 2-3 audits

**Notable Fixes**:
- **UI-002**: Muted text accessibility (WCAG AA contrast)
- **UI-006**: Status badge typography improvement
- **UI-007**: Project info link spacing
- **UI-008**: Visual navigation card spacing
- **UI-009**: Quick nav mega list refactoring
- **UI-011**: Table font size increase (11px → 15px)
- **UI-020**: Mobile H1 word-break fix
- **UI-022**: Mobile grid 1-column force
- **UI-023**: Footer metadata spacing
- **UI-024**: Tablet nav grid 2-column adjustment
- **UI-025**: Tablet anchor rail font scaling
- **UI-026**: Anchor rail active state enhancement
- **UI-027**: Back-to-top button shadow
- **UI-028**: Quick reference card heading contrast
- **UI-032**: Breadcrumb link text truncation
- **UI-033**: Coverage matrix sticky header
- **UI-034**: Hero feature bullet typography

### 22. Spacing & Responsive Utilities (Lines 107-255)

**Purpose**: Wave 2 foundations for spacing and responsive design

**Features**:
- Stack utilities (vertical spacing)
- Inset utilities (padding)
- Inline utilities (horizontal spacing)
- Gap utilities (flexbox/grid)
- Responsive breakpoint utilities
- Mobile-specific overrides
- Hide/show utilities

**Usage**:
```html
<div class="u-stack-lg u-inset-md">
  <p>Content with 24px bottom margin and 16px padding</p>
</div>

<div class="u-grid-2col@tablet u-grid-3col@desktop">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
</div>
```

### 23. Icon System (Lines 1549-1678)

**Purpose**: SVG icon styling (Wave 3 UI-029 deployment)

**Features**:
- Base icon sizing (1em, scales with text)
- Size variants (.icon-sm, .icon-lg, .icon-xl)
- Semantic color classes (.icon-success, .icon-danger, etc.)
- Context-specific styling (tables, headings, buttons)
- Dark mode adjustments
- High contrast mode support
- Print optimizations

**Usage**:
```html
<img src="../_static/icons/status/check.svg" class="icon icon-success" alt="Success" />
```

---

## Collapsible Code Blocks

**File**: `docs/_static/code-collapse.css` + `code-collapse.js`

**Purpose**: Allow users to collapse/expand code blocks

**Features**:
- Toggle button in code block header
- Smooth height animation
- Preserves syntax highlighting
- Keyboard accessible (Enter/Space to toggle)

**Activation**: Automatically applied to all code blocks with `.. code-block::`

**CSS Classes**:
```css
.code-collapse-toggle    /* Toggle button */
.highlight.collapsed     /* Collapsed state */
```

---

## Syntax Highlighting

**Pygments Style**: Custom dark theme (slate background)

**Configuration**: `docs/conf.py`
```python
pygments_style = 'monokai'
```

**Custom Overrides**: `docs/_static/custom.css` (lines 468-520)

**Supported Languages**:
- Python (primary)
- YAML (config files)
- Bash (shell commands)
- JSON (data formats)
- RST (documentation)
- LaTeX (equations)

**Example**:
```rst
.. code-block:: python

   from src.controllers import ClassicalSMC
   controller = ClassicalSMC(gains=[10, 8, 15, 12, 50, 5])
```

---

## LaTeX Equation Rendering

**File**: `docs/_static/mathviz.css`

**Renderer**: MathJax 3.x (configured in `conf.py`)

**Purpose**: Styled mathematical notation

**Features**:
- Centered display equations
- Inline equation styling
- Hover highlights
- Mobile-responsive sizing

**Usage**:
```rst
The sliding surface is defined as:

.. math::

   s = \lambda_1 e_1 + \lambda_2 e_2 + \dot{e}_1 + \dot{e}_2

where :math:`e_i` represents tracking errors.
```

---

## Dark Mode Implementation

**Trigger**: JavaScript toggle in header

**Persistence**: LocalStorage (`theme` key)

**File**: `docs/_static/dark-mode.js`

**Mechanism**:
1. User clicks theme toggle button
2. JS sets `<html data-theme="dark">`
3. CSS overrides apply via `[data-theme="dark"]` selector
4. Preference saved to `localStorage`

**CSS Overrides** (`custom.css` lines 641-676):
```css
[data-theme="dark"] {
    --color-bg-primary: #0f172a;        /* Dark slate */
    --color-text-primary: #f1f5f9;      /* Light gray */
    --color-border: #334155;            /* Dark borders */
}
```

**Toggle Button** (added by PyData theme + custom JS):
```html
<button id="theme-toggle" aria-label="Toggle dark mode">
  <svg class="icon-sun">...</svg>
  <svg class="icon-moon">...</svg>
</button>
```

---

## Responsive Design

**Breakpoints** (from design tokens):
- **Mobile**: < 768px (1 column layouts)
- **Tablet**: 768px - 1023px (2 column layouts)
- **Desktop**: ≥ 1024px (3+ column layouts)

**Mobile-First Approach**: Base styles for mobile, media queries add complexity

**Key Responsive Features**:
1. **Navigation** (UI-024): 3-col grid → 2-col @ tablet → 1-col @ mobile
2. **Typography** (UI-020): H1 clamp(2.25rem, 3.2vw, 2.5rem) prevents overflow
3. **Touch Targets**: 48×48px minimum (WCAG 2.1 AA compliance)
4. **Anchor Rail** (UI-025): 16px font @ desktop → 14px @ tablet
5. **Footer**: Single-column @ mobile with increased line-height (UI-023)

**Example**:
```css
/* Mobile (default) */
.visual-nav-grid {
    grid-template-columns: 1fr; /* Single column */
}

/* Tablet */
@media (min-width: 768px) {
    .visual-nav-grid {
        grid-template-columns: repeat(2, 1fr); /* 2 columns */
    }
}

/* Desktop */
@media (min-width: 1024px) {
    .visual-nav-grid {
        grid-template-columns: repeat(3, 1fr); /* 3 columns */
    }
}
```

---

## Accessibility Features

### WCAG 2.1 Level AA Compliance

**Color Contrast**:
- Primary text: 16.24:1 (far exceeds 4.5:1 minimum)
- Secondary text: 5.12:1
- Muted text: 4.52:1 (UI-002 fix)
- Link colors: 8.21:1

**Touch Targets** (UI-WAVE1 lines 766-946):
- All interactive elements: 48×48px minimum
- Buttons, links, form controls: adequate padding
- Adjacent elements: 8px spacing

**Focus Indicators**:
- Visible focus outlines (3px solid primary)
- 2px offset for clarity
- Custom focus styles for buttons, links

**Keyboard Navigation**:
- Tab order follows visual layout
- Skip links (PyData theme built-in)
- Collapsible code blocks: Enter/Space to toggle
- Theme toggle: keyboard accessible

**Screen Reader Support**:
- Semantic HTML5 elements (`<nav>`, `<main>`, `<aside>`)
- ARIA labels for icon-only buttons
- Alt text for images
- Caption text for tables

**Reduced Motion Support**:
```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation: none !important;
        transition: none !important;
    }
}
```

---

## Customization Guide

### Changing Brand Colors

**Edit**: `docs/_static/custom.css` lines 22-25

```css
:root {
    --color-primary: #2563eb;        /* Change to your brand blue */
    --color-primary-hover: #0b2763;  /* Darker shade for hover */
    --color-primary-light: #e6ebf5;  /* Light tint for backgrounds */
}
```

**Impact**: Updates buttons, links, headings, status badges, admonitions

### Adding New Status Badge

**Step 1**: Add CSS (append to lines 410-465):
```css
.status-alpha {
    background: linear-gradient(135deg, #ec4899, #be185d); /* Pink gradient */
    color: white;
    border: none;
}

.status-alpha::before {
    content: "α";
    font-size: 16px;
    font-style: italic;
}
```

**Step 2**: Use in RST docs:
```rst
.. raw:: html

   <span class="status-badge status-alpha">Alpha</span>
```

### Creating Custom Admonition

**Step 1**: Add CSS (append to lines 296-383):
```css
.admonition.research {
    --admonition-bg-start: #fef3c7; /* Yellow tint */
    --admonition-bg-end: #ffffff;
    border-color: #fbbf24;
}

.admonition.research::before {
    content: "🔬";
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    font-size: 16px;
}
```

**Step 2**: Configure Sphinx (`docs/conf.py`):
```python
# Add custom admonition
rst_prolog = """
.. role:: research(admonition)
   :class: admonition research
"""
```

**Step 3**: Use in docs:
```rst
.. research::
   This feature is under active research.
```

### Adjusting Spacing

**Change spacing scale**: Edit lines 63-70
```css
:root {
    --space-1: 4px;   /* Increase for more breathing room */
    --space-2: 8px;
    --space-4: 16px;  /* Base unit */
    --space-5: 24px;
    --space-6: 32px;
}
```

**Apply to element**:
```css
.my-section {
    margin-bottom: var(--space-5); /* 24px */
    padding: var(--space-4);       /* 16px */
}
```

### Adding New Icon Color

**Step 1**: Define token (line 22-50):
```css
:root {
    --color-custom: #ec4899; /* Pink */
}
```

**Step 2**: Add icon class (lines 1576-1582):
```css
.icon-custom { color: var(--color-custom); }
```

**Step 3**: Use with icon:
```html
<img src="../_static/icons/status/check.svg" class="icon icon-custom" alt="Custom" />
```

---

## Build Integration

### Sphinx Configuration

**File**: `docs/conf.py`

**Theme Setup**:
```python
html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    'logo': {
        'text': 'DIP SMC PSO',
    },
    'navbar_end': ['theme-switcher', 'navbar-icon-links'],
}
```

**Static Files**:
```python
html_static_path = ['_static']
html_css_files = [
    'custom.css',              # Main theme (loads first)
    'code-collapse.css',
    'mathviz.css',
]
html_js_files = [
    'dark-mode.js',
    'code-collapse.js',
]
```

**Build Command**:
```bash
sphinx-build -M html docs docs/_build
```

### Rebuilding After Changes

**Critical**: Always rebuild Sphinx after modifying static assets

**Full rebuild**:
```bash
sphinx-build -M html docs docs/_build -W --keep-going
```

**Verification**:
```bash
# Check file copied
stat docs/_static/custom.css docs/_build/html/_static/custom.css

# Check MD5 sums match
md5sum docs/_static/custom.css docs/_build/html/_static/custom.css

# Verify localhost serves new version
curl -s "http://localhost:9000/_static/custom.css" | grep "YOUR_UNIQUE_CHANGE"
```

**Browser Cache**: Hard refresh (Ctrl+Shift+R) to clear cached CSS

---

## Troubleshooting

### Theme Not Loading

**Symptom**: Documentation displays with minimal styling

**Causes**:
1. Sphinx build failed (check console for errors)
2. Static files not copied (missing `html_static_path` in `conf.py`)
3. CSS file path incorrect (must be `_static/` not `static/`)

**Solution**:
```bash
# Rebuild with verbose output
sphinx-build -M html docs docs/_build -v

# Verify static files copied
ls docs/_build/html/_static/custom.css
```

### CSS Changes Not Appearing

**Symptom**: Modified CSS doesn't reflect in browser

**Causes**:
1. Sphinx not rebuilt after changes
2. Browser cache serving old CSS
3. Changes made to wrong file (edit source, not build output)

**Solution**:
```bash
# 1. Rebuild Sphinx
sphinx-build -M html docs docs/_build

# 2. Hard refresh browser (Ctrl+Shift+R)

# 3. Verify timestamps match
stat docs/_static/custom.css docs/_build/html/_static/custom.css
```

### Dark Mode Not Switching

**Symptom**: Theme toggle button doesn't work

**Causes**:
1. JavaScript not loaded (`dark-mode.js` missing)
2. `[data-theme="dark"]` selector missing in CSS
3. Browser localStorage disabled

**Solution**:
```javascript
// Check if JS loaded
console.log(document.querySelector('#theme-toggle'));

// Check localStorage
localStorage.getItem('theme');

// Manually toggle
document.documentElement.setAttribute('data-theme', 'dark');
```

### Icons Not Displaying

**Symptom**: Broken image icons or alt text shown

**Causes**:
1. Icon file missing from `docs/_static/icons/`
2. Incorrect path (use `../_static/` not `/_static/` in guides)
3. SVG file corrupted

**Solution**:
```bash
# Verify icon exists
ls docs/_static/icons/status/check.svg

# Check SVG valid
cat docs/_static/icons/status/check.svg

# Rebuild Sphinx
sphinx-build -M html docs docs/_build
```

### Mobile Layout Breaking

**Symptom**: Content overflows or columns collapse incorrectly

**Causes**:
1. Missing responsive utilities
2. Incorrect breakpoint usage
3. Fixed widths without max-width

**Solution**: Use responsive utilities from Wave 2:
```html
<div class="u-grid-2col@tablet u-grid-1col@mobile">
  <div>Column 1</div>
  <div>Column 2</div>
</div>
```

---

## Performance Optimization

### Asset Sizes

**CSS Files**:
- `custom.css`: ~70 KB (uncompressed)
- `code-collapse.css`: ~5 KB
- `mathviz.css`: ~3 KB
- **Total CSS**: ~78 KB (gzipped: ~15 KB)

**JavaScript Files**:
- `dark-mode.js`: ~2 KB
- `code-collapse.js`: ~3 KB
- **Total JS**: ~5 KB (gzipped: ~2 KB)

**Icons**:
- Per icon: 250-400 bytes
- Total (7 icons): ~2.5 KB
- **Gzipped**: ~1 KB

### Loading Strategy

**CSS**: Loaded in `<head>` (blocking, but cached)
**JS**: Loaded at end of `<body>` (non-blocking)
**Icons**: Lazy-loaded as `<img>` tags (browser native)

### Caching

**Sphinx build**: Copies to `_build/html/_static/` with original timestamps
**Browser**: Caches static assets (CSS, JS, icons) for 1 day
**CDN**: Serve via CDN for production (optional)

### Optimization Tips

1. **Minimize CSS**: Remove unused rules (carefully!)
2. **Combine files**: Merge related CSS files to reduce requests
3. **Optimize SVGs**: Use SVGOMG for icon optimization
4. **Enable compression**: Configure server for gzip/brotli
5. **CDN**: Serve static assets from CDN (Cloudflare, AWS CloudFront)

---

## References

- PyData Sphinx Theme: https://pydata-sphinx-theme.readthedocs.io/
- Sphinx Documentation: https://www.sphinx-doc.org/
- Design Tokens v2.0.0: `.codex/phase2_audit/design_tokens_v2.json`
- Phase 3 UI Audit: `.codex/phase3/ui_audit_comprehensive.md`
- Icon System: `docs/_static/icons/README.md`
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/

---

**Last Updated**: 2025-10-16
**Theme Version**: 3.0 (Phase 3 Wave 3 completion)
**Framework Version**: 1.0
