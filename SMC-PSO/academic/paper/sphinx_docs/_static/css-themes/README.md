# CSS Theme Library for DIP-SMC-PSO Documentation

Professional CSS theme collection for Sphinx documentation. Pick a theme, switch easily, rebuild docs.

---

## Directory Structure

```
docs/_static/
├── custom.css              ← ACTIVE theme (loaded by Sphinx)
└── css-themes/             ← Theme library (you are here)
    ├── README.md           ← This file
    ├── switch.sh           ← Theme switcher script
    ├── base-theme.css      ← Backup of original custom.css
    ├── minimal-professional.css
    ├── academic-journal.css
    ├── modern-tech.css
    └── colorful-indicators.css
```

---

## Available Themes

### 1. **base-theme.css**

**Description:** Original custom.css backup - dark mode, back-to-top, lazy loading
**Best For:** Current state preservation
**Features:**
- Dark mode toggle
- Reading progress bar
- Back-to-top button
- Lazy loading images
- Print-friendly styles

### 2. **minimal-professional.css** (TO BE CREATED)

**Description:** Clean, minimal design for academic rigor
**Best For:** Thesis, research papers, academic submissions
**Features:**
- Subtle colors (grays, blues)
- No flashy animations
- Simple admonition boxes
- Professional status badges

### 3. **academic-journal.css** (TO BE CREATED)

**Description:** IEEE/ACM journal style
**Best For:** Publications, formal documentation
**Features:**
- Serif fonts for body text
- Citation-friendly styling
- Figure/table captions
- Numbered sections

### 4. **modern-tech.css** (TO BE CREATED)

**Description:** Modern tech docs style (GitHub, Stripe, Vercel)
**Best For:** Developer-facing documentation
**Features:**
- Bold colors
- Interactive elements
- Code-first design
- Developer-friendly patterns

### 5. **colorful-indicators.css** (TO BE CREATED)

**Description:** Visual indicators without emojis (reactbits.dev inspired)
**Best For:** Quick visual scanning, tutorials
**Features:**
- Colored status badges
- Icon-like CSS prefixes
- Animated admonitions
- High visual hierarchy

---

## How to Use

### Option 1: Manual Switch (Windows)

```cmd
cd docs\_static\css-themes
copy minimal-professional.css ..\custom.css
cd ..\..\..
```

Then rebuild docs:
```cmd
cd docs
make html
```

### Option 2: Using Switcher Script (Git Bash/WSL)

```bash
cd docs/_static/css-themes
./switch.sh minimal-professional
cd ../../..
make -C docs html
```

### Option 3: Direct Edit

Edit `docs/_static/custom.css` directly with code from any theme file.

---

## Creating New Themes

### Step 1: Copy Base Template

```bash
cp base-theme.css my-custom-theme.css
```

### Step 2: Edit Sections

Each theme CSS should have these sections:

```css
/* ============================================================================
   Theme Name: My Custom Theme
   Description: Brief description
   Best For: Use case
   ============================================================================ */

/* 1. CSS Variables (Colors) */
:root {
    --color-primary: #2962ff;
    --color-secondary: #1976d2;
}

/* 2. Admonitions (note, warning, tip, danger) */
.admonition { ... }

/* 3. Status Badges (stable, experimental, beta) */
.status-badge { ... }

/* 4. Code Blocks */
div[class*="highlight"] { ... }

/* 5. Tables */
table.docutils { ... }

/* 6. Dark Mode Overrides */
[data-theme="dark"] { ... }
```

### Step 3: Test Locally

```bash
cd docs
make html
python -m http.server 8000 --directory _build/html
```

Open: http://localhost:8000

---

## Theme Sections Reference

### Required Sections (All Themes Must Have)

1. **Admonitions** - `note`, `tip`, `warning`, `danger`, `error`
2. **Status Badges** - `stable`, `experimental`, `beta`, `deprecated`
3. **Code Blocks** - Syntax highlighting backgrounds
4. **Tables** - `table.docutils` styling
5. **Dark Mode** - `[data-theme="dark"]` overrides

### Optional Sections

- Back-to-top button
- Reading progress bar
- Breadcrumb styling
- Print styles
- Mobile responsive adjustments

---

## Integration with reactbits.dev

You can adapt CSS patterns from https://reactbits.dev/ by:

1. **Inspecting Elements** - Right-click → Inspect on reactbits.dev
2. **Copy CSS** - Find the styles you like
3. **Adapt to RST** - Translate React classes to Sphinx directives

### Example Translation

**React (reactbits.dev):**
```jsx
<div className="badge badge-success">Stable</div>
```

**Sphinx RST:**
```rst
:status-stable:`STABLE`
```

**CSS (your theme):**
```css
.status-stable {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}
```

---

## Sphinx Directive → CSS Class Mapping

| Sphinx Directive | CSS Class | Purpose |
|------------------|-----------|---------|
| `.. note::` | `.admonition.note` | Information box |
| `.. warning::` | `.admonition.warning` | Warning box |
| `.. tip::` | `.admonition.tip` | Best practice tip |
| `.. danger::` | `.admonition.danger` | Critical warning |
| `:code:` | `code` | Inline code |
| `.. code-block::` | `div.highlight` | Code block |
| Table | `table.docutils` | Documentation table |

---

## Quality Checklist

Before adding a new theme, verify:

- [ ] All required sections present
- [ ] Dark mode styles defined
- [ ] Print styles included
- [ ] Mobile responsive (< 768px)
- [ ] Works with Furo theme
- [ ] No emoji characters (Windows cp1252 compatible)
- [ ] Tested locally with `make html`

---

## Maintenance

**When to Update Themes:**
- New Sphinx version changes CSS classes
- Furo theme updated
- New admonition types added
- User feedback on readability

**Backup Strategy:**
- Always keep `base-theme.css` as original
- Version control all theme files
- Document changes in git commits

---

## Resources

**Sphinx CSS Classes:**
- https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html

**Furo Theme Docs:**
- https://pradyunsg.me/furo/

**Inspiration Libraries:**
- https://reactbits.dev/ - Modern component library
- https://docs.github.com/ - GitHub docs style
- https://stripe.com/docs - Stripe docs style
- https://docs.python.org/ - Python docs style

---

**Created:** 2025-10-10
**Purpose:** Professional CSS theme system for academic documentation
**Status:** Base structure ready, themes to be created from reactbits.dev library
