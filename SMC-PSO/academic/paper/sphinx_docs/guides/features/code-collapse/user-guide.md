# Collapsible Code Blocks - User Guide

**Feature Status:** ✅ Production Ready (v1.0.0)
**Last Updated:** 2025-10-12

---

## What is This Feature?

Collapsible code blocks allow you to collapse and expand code examples on documentation pages, making it easier to focus on the content you care about. Code blocks that you collapse will stay collapsed even when you reload the page.

**Key Benefits:**
- Reduce visual clutter on pages with many code examples
- Focus on specific code sections
- Preserve your reading preferences across page reloads
- Works seamlessly with all code block types (Python, Bash, JavaScript, etc.)

---

## How to Use

### Individual Code Blocks

Every code block has two buttons in the top-right corner:

1. **Copy button** (📋) - copies code to clipboard
2. **Collapse button** (▼/▲) - collapses or expands the code block

#### To Collapse a Code Block

1. Find the collapse button in the top-right corner (shows **▼** when expanded)
2. Click the button
3. The code smoothly slides up (curtain effect)
4. A message appears: "Code hidden (click ▲ to expand)"

#### To Expand a Code Block

1. Find the expand button in the top-right corner (shows **▲** when collapsed)
2. Click the button
3. The code smoothly slides down

**The button gap is 5-8px** - easy to distinguish which button you're clicking!

---

### Master Controls

At the top of each documentation page (below the first heading), you'll find master control buttons:

```
[X code blocks:]  [▲ Collapse All]  [▼ Expand All]
```

- **Collapse All** - Collapses all code blocks on the current page
- **Expand All** - Expands all code blocks on the current page

**Use case:** Reading a guide with 20+ code examples? Collapse all, then expand only the ones you need!

---

### Keyboard Shortcuts

Power users can use keyboard shortcuts for even faster control:

| Shortcut | Action | Windows/Linux | Mac |
|----------|--------|---------------|-----|
| **Collapse All** | Collapse all code blocks | `Ctrl+Shift+C` | `Cmd+Shift+C` |
| **Expand All** | Expand all code blocks | `Ctrl+Shift+E` | `Cmd+Shift+E` |

**Note:** On some browsers, `Ctrl+Shift+C` may open Developer Tools. If this happens, use the "Collapse All" button instead.

---

### State Persistence

**Your collapsed blocks stay collapsed!**

When you collapse a code block, your preference is saved in your browser's local storage. When you:
- Reload the page
- Navigate away and come back
- Close the browser and reopen

...the code blocks you collapsed will remain collapsed.

#### Resetting Collapsed State

To clear your collapse preferences and expand all blocks:

1. Open browser console (F12)
2. Type: `clearCodeBlockStates()`
3. Press Enter
4. Reload the page

All code blocks will be expanded again.

---

## Features

### Smart Exclusions

**Math equations are never collapsed.** The feature automatically excludes:
- LaTeX math blocks (`.amsmath`, `.math`)
- KaTeX equations
- MathJax content

This ensures mathematical formulas remain visible for reference.

**Very short code snippets are excluded.** Code blocks with fewer than 10 characters are skipped (likely inline code or trivial examples).

---

### Accessibility

**Keyboard navigation fully supported:**
- Press `Tab` to focus collapse buttons
- Press `Enter` or `Space` to toggle
- Visible focus indicator (blue outline) shows which button is focused

**Screen reader compatible:**
- Buttons announce as: "Toggle code block visibility, button, expanded/collapsed"
- ARIA attributes update when state changes
- Collapse state is announced

**Reduced motion support:**
- If you have "Reduce motion" enabled in your OS settings
- Collapse/expand happens instantly (no animation)
- Functionality still works perfectly

---

### Mobile Support

**Touch-friendly buttons:**
- Larger touch targets on mobile (6px padding)
- Buttons clearly visible on small screens (320px+)
- Gap between buttons reduced to 5px on mobile for easier tapping

**Responsive master controls:**
- Control bar wraps on narrow screens
- Buttons remain accessible at all viewport sizes

---

### Print Support

**All code blocks expand when printing.**

When you print a page (Ctrl+P or Cmd+P):
- All collapsed code blocks automatically expand
- Collapse buttons are hidden
- "Code hidden" messages don't appear in print
- Full code content is included in the printout

**This ensures complete documentation in printed copies!**

---

## Browser Support

| Browser | Minimum Version | Status |
|---------|----------------|--------|
| **Chrome** | 90+ | ✅ Fully supported |
| **Firefox** | 88+ | ✅ Fully supported |
| **Edge** | 90+ | ✅ Fully supported |
| **Safari** | 14+ | ⚠️ Partial GPU acceleration |

**All core functionality works on all modern browsers.** Some advanced GPU acceleration features may be limited in older Safari versions.

---

## FAQ

### Why don't I see collapse buttons on some code blocks?

**Math blocks are intentionally excluded.** LaTeX equations and mathematical content never get collapse buttons.

**Very short code snippets are excluded.** Code blocks with fewer than 10 characters are skipped.

If you see code blocks that should have collapse buttons but don't, check the browser console (F12) for error messages.

### Why is the animation choppy?

**Try these solutions:**
1. **Update your browser** to the latest version
2. **Enable hardware acceleration** in browser settings
3. **Disable browser extensions** (test in Incognito mode)
4. **Close other tabs** to free up resources

Expected performance: 55-60 FPS during collapse/expand animation.

### Can I change the collapse button icon?

**Not as an end user.** The icons are configured by the documentation maintainer.

If you're a developer integrating this feature, see the [Integration Guide](integration-guide.md) for customization options.

### Does this work offline?

**Yes!** Once the page is loaded:
- Collapse/expand works without internet
- State persistence uses browser's local storage (no server needed)

However, your collapsed state is stored per-browser. If you switch browsers, you'll need to collapse blocks again.

### What if I run out of local storage space?

**Very unlikely.** Each page's collapse state uses about 1KB per 100 code blocks.

If you somehow reach your browser's storage limit (~5-10MB):
- New collapse states won't be saved
- Existing functionality still works
- Clear old data: `localStorage.clear()` in console

### Can I collapse code blocks across all pages at once?

**No.** Collapse state is per-page. Each documentation page has independent collapse settings.

**Workaround:** Use keyboard shortcuts (`Ctrl+Shift+C`) to quickly collapse all blocks on each page you visit.

---

## Tips & Tricks

### Tip 1:

Collapse on Long Pages

When reading a guide with many code examples:
1. Click "Collapse All" at the top
2. Skim the text to find what you need
3. Expand only the code blocks you want to study

**Saves scrolling time!**

### Tip 2:

Keep Reference Code Expanded

Reading a tutorial that references one code block multiple times?
1. Collapse all other blocks
2. Keep the reference code expanded
3. Easier to scroll back to it

### Tip 3:

Keyboard Shortcuts for Power Users

Memorize `Ctrl+Shift+E` (Expand All) for when you need to see all code at once (e.g., before printing).

### Tip 4:

Mobile Reading

On mobile, collapse code blocks you don't need to reduce vertical scrolling. The master controls wrap nicely on narrow screens.

---

## Getting Help

### Documentation Resources

- **Integration Guide:** [integration-guide.md](integration-guide.md) - For developers adding this to their docs
- **Troubleshooting:** [troubleshooting.md](troubleshooting.md) - Common issues and solutions
- **Configuration:** [configuration-reference.md](configuration-reference.md) - Technical configuration options

### Reporting Issues

If you encounter a bug:
1. Check the [Troubleshooting Guide](troubleshooting.md) first
2. Note your browser version and operating system
3. Take a screenshot of any error messages in the console
4. Report via GitHub issues (link to repository)

---

**Enjoy cleaner, more focused documentation reading!** 📚
