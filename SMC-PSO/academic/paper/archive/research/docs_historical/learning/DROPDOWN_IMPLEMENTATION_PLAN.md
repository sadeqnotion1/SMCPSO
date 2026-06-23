# Dropdown Implementation Plan - Phase 1 Foundations

**Status**: Ready for implementation
**Agent**: Agent 2 (Dropdown Specialist)
**Coordinate with**: Agent 1 (Tab Specialist - working on Phases 2-5)

---

## Implementation Strategy

Due to concurrent file editing (Agent 1 adding tabs), implement dropdowns in this order:

1. Read current file state
2. Add dropdowns section-by-section
3. Commit immediately after each section
4. Coordinate merge conflicts if they arise

---

## Section 1: Python Basics Dropdowns (Phase 1.2, Lines ~270-380)

**Target**: Replace numbered list items (1-6) with sphinx-design dropdowns

### Current Structure
```markdown
1. **Variables and Data Types** (2 hours)
   - Numbers (integers, floats)
   ...
```

### New Structure
```markdown
:::{dropdown} 1. Variables and Data Types (2 hours)
:animate: fade-in-slide-down
:color: primary

Learn how to store and manipulate different types of data in Python.

**Topics Covered**:
- Numbers (integers, floats)
- Strings (text)
- Booleans (True/False)
- Type conversion

**Code Examples**:
```python
[existing code block]
```

**Practice**: Try creating variables for your name, age, and favorite number. Print them!
:::
```

**Apply to**: Items 1-6 in Phase 1.2 Step 2

---

## Section 2: Exercise Solutions (Phase 1.2, Lines ~381-393)

**Target**: Wrap solutions in success-colored dropdowns

### Exercise 1 Solution
```markdown
**Exercise 1**: Write a function that takes a temperature in Celsius and converts it to Fahrenheit.

```python
def celsius_to_fahrenheit(celsius):
    # Formula: F = C * 9/5 + 32
    # Your code here
    pass
```

:::{dropdown} Solution (try first!)
:color: success
:icon: octicon-light-bulb

```python
def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    fahrenheit = celsius * 9/5 + 32
    return fahrenheit

# Test it
print(celsius_to_fahrenheit(0))    # 32.0
print(celsius_to_fahrenheit(100))  # 212.0
print(celsius_to_fahrenheit(25))   # 77.0
```
:::
```

**Apply to**: Exercises 1-3

---

## Section 3: Troubleshooting Dropdowns (Phase 1.3, Lines ~758-772)

**Target**: Replace bullet-point troubleshooting with warning dropdowns

### Current Structure
```markdown
**Troubleshooting**:

- **"Microsoft Visual C++ required" (Windows)**:
  - Install: [Visual C++ Build Tools](...)
```

### New Structure
```markdown
**Troubleshooting**:

:::{dropdown} Microsoft Visual C++ required (Windows)
:color: warning
:icon: octicon-alert

**Error Message**: "Microsoft Visual C++ 14.0 or greater is required"

**Solution**:
1. Download Visual C++ Build Tools from: [Visual C++ Build Tools](...)
2. Run the installer
3. Select "Desktop development with C++" workload
4. Install and restart your terminal
5. Try `pip install -r requirements.txt` again

**Why This Happens**: Some Python packages (like NumPy) need to compile C code during installation.
:::
```

**Add 5 dropdowns**:
1. Microsoft Visual C++ required
2. pip command not found
3. Permission denied errors
4. Virtual environment activation fails (PowerShell)
5. Import errors after installation

---

## Section 4: Physics Theory Dropdowns (Phase 1.4, Lines ~810-1050)

**Target**: Wrap "Step 1-4" sections in info-colored dropdowns

### Current Structure
```markdown
**Step 1: Forces and Newton's Laws (2 hours)**

**Newton's First Law** (Inertia):
...
```

### New Structure
```markdown
:::{dropdown} Step 1: Forces and Newton's Laws (2 hours)
:animate: fade-in-slide-down
:color: info
:icon: octicon-mortar-board

Understanding the fundamental laws that govern motion.

**Newton's First Law** (Inertia):
- An object at rest stays at rest
- An object in motion stays in motion
- Unless acted upon by a force

**Example**: A pendulum at rest won't start swinging unless you push it.

[... continue with existing content ...]

**Practice Exercise**:
1. If a cart has mass 2 kg and you apply 10 N force, what is the acceleration?
2. What happens to acceleration if you double the force?
3. What happens if you double the mass instead?

:::{dropdown} Exercise Solutions
:color: success
:icon: octicon-light-bulb

1. **Acceleration = Force / Mass = 10 N / 2 kg = 5 m/s²**

2. **If you double the force (20 N)**: Acceleration = 20 / 2 = 10 m/s² (doubles!)

3. **If you double the mass (4 kg)**: Acceleration = 10 / 4 = 2.5 m/s² (halves!)

**Key Insight**: Acceleration is directly proportional to force, inversely proportional to mass.
:::

**Resources**:
- [Newton's Laws Explained (Video, 15 min)](...)
- [Khan Academy: Newton's Laws](...)
:::
```

**Apply to**: Steps 1-4 in Phase 1.4, each with nested solution dropdowns

---

## Section 5: CSS Enhancements (docs/_static/beginner-roadmap.css)

Add at end of file (~line 602):

```css
/* ===== 14. SPHINX-DESIGN DROPDOWN ENHANCEMENTS ===== */

/* Dropdown hover effects */
.sd-dropdown > .sd-summary-title {
    transition: all 0.2s ease;
}

.sd-dropdown:hover > .sd-summary-title {
    transform: translateX(4px);
}

.sd-dropdown[open] > .sd-summary-title {
    color: var(--phase-color);
    font-weight: 600;
}

/* Enhanced icon colors for better contrast */
.sd-dropdown[data-sd-icon="octicon-light-bulb"] .sd-summary-icon {
    color: #10b981;  /* Green for success/tips */
}

.sd-dropdown[data-sd-icon="octicon-alert"] .sd-summary-icon {
    color: #f59e0b;  /* Orange for warnings */
}

.sd-dropdown[data-sd-icon="octicon-mortar-board"] .sd-summary-icon {
    color: #3b82f6;  /* Blue for education */
}

.sd-dropdown[data-sd-icon="octicon-tools"] .sd-summary-icon {
    color: #8b5cf6;  /* Purple for technical */
}

/* Smoother dropdown animations */
.sd-dropdown {
    transition: all var(--transition-base);
}

.sd-dropdown[open] {
    background: var(--phase-bg-light);
    box-shadow: var(--shadow-md);
}

/* Nested dropdown styling (2 levels max) */
.sd-dropdown .sd-dropdown {
    margin-left: var(--space-4);
    border-left: 3px solid var(--phase-color);
    background: transparent;
}

.sd-dropdown .sd-dropdown[open] {
    background: rgba(255, 255, 255, 0.5);
}

/* Dropdown content spacing */
.sd-dropdown-content {
    padding-top: var(--space-3);
}

/* ===== END OF SPHINX-DESIGN ENHANCEMENTS ===== */
```

---

## Implementation Checklist

- [ ] Section 1: Python basics dropdowns (6 dropdowns)
- [ ] Section 2: Exercise solutions (3 dropdowns)
- [ ] Section 3: Troubleshooting (5 dropdowns)
- [ ] Section 4: Physics theory (4 main + 3 nested = 7 dropdowns)
- [ ] Section 5: CSS enhancements (~52 lines)
- [ ] Test Sphinx build
- [ ] Commit with proper message format
- [ ] Update WEEK3_IMPLEMENTATION_SUMMARY.md

---

## Conflict Resolution

If Agent 1's tabs conflict with dropdowns:

1. **Tabs are wrappers** (OS-specific content) - Outer level
2. **Dropdowns are toggles** (Progressive disclosure) - Can nest inside tabs
3. **Solution**: Dropdowns can exist WITHIN tab panels if needed

Example of compatible nesting:
```markdown
::::{tab-set}
:::{tab-item} Windows

:::{dropdown} Troubleshooting: pip not found
:color: warning

[Windows-specific solution]
:::

:::
:::{tab-item} Mac/Linux

:::{dropdown} Troubleshooting: pip not found
:color: warning

[Mac/Linux-specific solution]
:::

:::
::::
```

---

## Success Criteria

✅ 21 dropdowns total (6+3+5+7)
✅ 5 semantic colors (primary, success, warning, info, light)
✅ 4 icon types (light-bulb, alert, mortar-board, tools)
✅ ~52 CSS lines
✅ Sphinx build succeeds
✅ No merge conflicts with Agent 1

---

**Ready for Implementation**: Yes
**Coordination Needed**: Monitor Agent 1's commits to Phase 1
