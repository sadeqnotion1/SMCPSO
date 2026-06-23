# GitHub Pages Deployment Guide

**Document Version:** 1.0
**Date:** November 12, 2025
**Status:** OPERATIONAL
**Target:** DIP-SMC-PSO Documentation (873 files, WCAG 2.1 Level AA)

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Workflow Configuration](#workflow-configuration)
5. [Repository Settings](#repository-settings)
6. [Verification](#verification)
7. [Custom Domain Setup](#custom-domain-setup)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)
10. [References](#references)

---

## Overview

This guide describes automatic deployment of Sphinx documentation to GitHub Pages using GitHub Actions. The workflow:

- **Automatic deployment** on every push to main branch (docs/ changes)
- **Manual deployment** via GitHub Actions UI (workflow_dispatch)
- **Fast builds** (~3-5 minutes for 873 documentation files)
- **Zero maintenance** after initial setup
- **WCAG 2.1 Level AA** compliant output
- **Lighthouse ≥90** performance score

**URL Format:** `https://<username>.github.io/<repository-name>/`

**Example:** `https://theSadeQ.github.io/dip-smc-pso/`

---

## Prerequisites

### GitHub Account

- GitHub account with repository access
- Push permissions to main branch
- Actions enabled (Settings → Actions → General → Allow all actions)

### Repository Structure

```
dip-smc-pso/
├── .github/
│   └── workflows/
│       └── deploy-docs.yml  # GitHub Pages deployment workflow
├── docs/
│   ├── index.rst            # Sphinx homepage
│   ├── conf.py              # Sphinx configuration
│   ├── _static/             # CSS, JS, images
│   └── ...                  # 873 documentation files
├── requirements.txt         # Python dependencies (Sphinx, theme, extensions)
└── README.md
```

### Sphinx Build Validation

Before enabling GitHub Pages, verify local Sphinx build:

```bash
# Clean build
rm -rf docs/_build
sphinx-build -M html docs docs/_build -W --keep-going

# Expected output:
# build succeeded, 0 errors, <5 warnings

# Verify HTML output
ls -lh docs/_build/html/index.html
# Should show index.html exists
```

---

## Quick Start

### Step 1: Enable GitHub Actions

**File:** `.github/workflows/deploy-docs.yml` (already created)

**Workflow triggers:**
- Push to main branch (docs/ changes)
- Manual trigger (workflow_dispatch)

### Step 2: Configure Repository Settings

1. Go to repository on GitHub.com
2. Click **Settings** → **Pages** (left sidebar)
3. Under **Source**, select:
   - **Branch:** `gh-pages`
   - **Folder:** `/ (root)`
4. Click **Save**
5. Wait 1-2 minutes for initial deployment

### Step 3: Trigger First Deployment

**Option 1: Push to main branch**
```bash
# Make a small change to docs/
echo "# Test" >> docs/test.md
git add docs/test.md
git commit -m "docs: Trigger GitHub Pages deployment"
git push origin main
```

**Option 2: Manual trigger**
1. Go to **Actions** tab on GitHub
2. Click **Deploy Documentation to GitHub Pages**
3. Click **Run workflow** → **Run workflow**
4. Wait 3-5 minutes for completion

### Step 4: Verify Deployment

1. Go to **Actions** tab
2. Click on latest workflow run
3. Check "Deployment summary" step for URL
4. Visit: `https://<username>.github.io/<repository-name>/`
5. Expected: Documentation homepage loads correctly

---

## Workflow Configuration

### Workflow File

**Location:** `.github/workflows/deploy-docs.yml`

**Key sections:**

```yaml
# Trigger on push to main (docs/ changes only)
on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'requirements.txt'
  workflow_dispatch:  # Manual trigger

# Build job
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.9
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Build Sphinx documentation
        run: sphinx-build -M html docs docs/_build -W --keep-going

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/_build/html
          publish_branch: gh-pages
```

### Workflow Outputs

**Success indicators:**
- [OK] Checkout repository
- [OK] Install dependencies
- [OK] Sphinx build completed (exit code 0)
- [OK] HTML output directory exists
- [OK] Deploy to GitHub Pages successful

**Failure indicators:**
- [ERROR] Sphinx build failed (exit code 1)
- [ERROR] HTML output directory not found
- [ERROR] Deployment failed (permissions issue)

---

## Repository Settings

### Pages Configuration

**Navigate to:** Repository → Settings → Pages

**Required settings:**

| Setting | Value |
|---------|-------|
| Source | Deploy from a branch |
| Branch | `gh-pages` |
| Folder | `/ (root)` |
| Enforce HTTPS | ✓ (recommended) |
| Custom domain | (optional) |

### Actions Permissions

**Navigate to:** Repository → Settings → Actions → General

**Required permissions:**

| Permission | Setting |
|------------|---------|
| Actions permissions | Allow all actions and reusable workflows |
| Workflow permissions | Read and write permissions |
| Allow GitHub Actions to create and approve pull requests | ✓ |

---

## Verification

### Step 1: Check Workflow Status

1. Go to **Actions** tab
2. Latest workflow run should show:
   - ✓ Build Sphinx Documentation and Deploy to GitHub Pages
   - Duration: ~3-5 minutes
   - Status: Success (green checkmark)

### Step 2: Verify GitHub Pages URL

1. Go to **Settings** → **Pages**
2. Top banner shows:
   - "Your site is live at https://\<username\>.github.io/\<repository\>/"
   - Click "Visit site" button

### Step 3: Test Documentation

**Homepage:**
- https://\<username\>.github.io/\<repository\>/
- Expected: Sphinx homepage loads with navigation

**Search:**
- Click search icon (top-right)
- Search for "SMC" or "PSO"
- Expected: Search results appear

**Navigation:**
- Click breadcrumbs (top)
- Click sidebar links
- Expected: Pages load correctly

**Responsive:**
- Resize browser window
- Test mobile breakpoints (320px, 768px, 1024px, 1440px)
- Expected: Layout adjusts correctly

### Step 4: Validate Accessibility

**Lighthouse Audit:**
```bash
# Install Lighthouse CLI
npm install -g @lhci/cli

# Run audit
lhci autorun --url=https://<username>.github.io/<repository>/ \
             --collect.settings.preset=desktop \
             --assert.assertions.categories:accessibility=0.90 \
             --assert.assertions.categories:performance=0.90

# Expected:
# Accessibility: ≥90 (WCAG 2.1 Level AA)
# Performance: ≥90
```

**Manual checks:**
- Keyboard navigation (Tab, Shift+Tab, Enter)
- Screen reader (NVDA, JAWS, VoiceOver)
- Color contrast (4.5:1 for text, 3:1 for graphics)

### Step 5: Link Validation

**Check for broken links:**
```bash
# Install linkchecker
pip install linkchecker

# Check all links
linkchecker https://<username>.github.io/<repository>/ \
            --check-extern \
            --no-warnings \
            > linkcheck_report.txt 2>&1

# Review report
cat linkcheck_report.txt | grep "Error"

# Expected: 0 errors
```

---

## Custom Domain Setup

### Step 1: Register Domain

Register a custom domain (e.g., `docs.dip-smc-pso.com`) from:
- Namecheap
- GoDaddy
- Cloudflare
- Google Domains

### Step 2: Configure DNS

Add DNS records at domain registrar:

**Option 1: Apex domain (e.g., dip-smc-pso.com)**
```
Type: A
Host: @
Value: 185.199.108.153
TTL: 3600

Type: A
Host: @
Value: 185.199.109.153
TTL: 3600

Type: A
Host: @
Value: 185.199.110.153
TTL: 3600

Type: A
Host: @
Value: 185.199.111.153
TTL: 3600
```

**Option 2: Subdomain (e.g., docs.dip-smc-pso.com)**
```
Type: CNAME
Host: docs
Value: <username>.github.io
TTL: 3600
```

### Step 3: Add CNAME File

**Create file:** `docs/CNAME`
```
docs.dip-smc-pso.com
```

**Commit and push:**
```bash
echo "docs.dip-smc-pso.com" > docs/CNAME
git add docs/CNAME
git commit -m "docs: Add custom domain CNAME"
git push origin main
```

### Step 4: Configure GitHub Pages

1. Go to **Settings** → **Pages**
2. Under **Custom domain**, enter: `docs.dip-smc-pso.com`
3. Click **Save**
4. Wait 24-48 hours for DNS propagation
5. Enable **Enforce HTTPS** (checkbox)

### Step 5: Verify Custom Domain

```bash
# Check DNS propagation
dig docs.dip-smc-pso.com +short
# Expected: <username>.github.io or GitHub Pages IP

# Check HTTPS
curl -I https://docs.dip-smc-pso.com
# Expected: HTTP/2 200 OK
```

---

## Troubleshooting

### Issue: "Workflow failed - Sphinx build error"

**Symptoms:**
- Workflow fails at "Build Sphinx documentation" step
- Exit code: 1

**Diagnosis:**
```bash
# Check workflow logs
# Actions tab → Failed workflow → "Build Sphinx documentation" step

# Look for errors like:
# - "WARNING: document isn't included in any toctree"
# - "ERROR: Unknown directive type: code-block"
# - "ERROR: Duplicate explicit target name"
```

**Solution:**
```bash
# Reproduce locally
sphinx-build -M html docs docs/_build -W --keep-going

# Fix errors in docs/
# Common fixes:
# - Add missing file to toctree
# - Fix directive syntax
# - Remove duplicate labels

# Test again
sphinx-build -M html docs docs/_build -W --keep-going

# Commit and push
git add docs/
git commit -m "fix: Resolve Sphinx build errors"
git push origin main
```

### Issue: "Pages not loading - 404 error"

**Symptoms:**
- GitHub Pages URL returns 404
- Workflow succeeded

**Diagnosis:**
```bash
# Check gh-pages branch exists
git branch -r | grep gh-pages
# Expected: origin/gh-pages

# Check files in gh-pages branch
git ls-remote --heads origin gh-pages
# Expected: SHA hash
```

**Solution:**
```bash
# Verify .nojekyll file exists in workflow
# Check workflow logs for:
# "[OK] .nojekyll file created"

# If missing, add to workflow:
- name: Create .nojekyll file
  run: touch docs/_build/html/.nojekyll

# Re-run workflow
# Actions tab → Run workflow
```

### Issue: "Assets missing - CSS/JS not loading"

**Symptoms:**
- HTML loads but no styling
- Browser console shows 404 for _static/ files

**Diagnosis:**
```bash
# Check _static/ directory in gh-pages branch
git clone --branch gh-pages --single-branch <repo-url> /tmp/gh-pages-check
ls -lh /tmp/gh-pages-check/_static/

# Expected: CSS, JS, images
```

**Solution:**
```bash
# Verify _static/ copied in workflow
# Check workflow logs for:
# "Files in output directory: ... _static/"

# If missing, rebuild Sphinx locally
sphinx-build -M html docs docs/_build -W --keep-going
ls -lh docs/_build/html/_static/

# If _static/ present locally but missing in deployment:
# - Check .gitignore doesn't exclude _static/
# - Verify peaceiris/actions-gh-pages@v4 copies all files

# Re-run workflow
```

### Issue: "Deployment delayed - DNS propagation"

**Symptoms:**
- Custom domain configured but not resolving
- DNS lookup fails

**Diagnosis:**
```bash
# Check DNS propagation
dig docs.dip-smc-pso.com +short
# Expected: <username>.github.io or GitHub Pages IP

# If empty:
# DNS not propagated yet (wait 24-48 hours)
```

**Solution:**
```bash
# Verify DNS records correct
# Check domain registrar dashboard:
# - CNAME: docs → <username>.github.io
# - TTL: 3600 (1 hour)

# Check CNAME file committed
cat docs/CNAME
# Expected: docs.dip-smc-pso.com

# Force DNS refresh (Linux/macOS)
sudo dscacheutil -flushcache  # macOS
sudo systemd-resolve --flush-caches  # Linux

# Wait 24-48 hours for global DNS propagation
```

### Issue: "HTTPS not available for custom domain"

**Symptoms:**
- Custom domain works over HTTP
- HTTPS returns certificate error

**Diagnosis:**
```bash
# Check HTTPS enforcement
curl -I https://docs.dip-smc-pso.com
# Expected: HTTP/2 200 OK (not "certificate invalid")
```

**Solution:**
```bash
# GitHub Pages generates SSL certificate automatically
# Process takes 15-30 minutes after DNS propagation

# Verify steps:
# 1. DNS propagated (dig confirms CNAME)
# 2. Custom domain configured in Settings → Pages
# 3. "Enforce HTTPS" checkbox enabled
# 4. Wait 15-30 minutes

# If still failing after 1 hour:
# - Remove custom domain (Settings → Pages)
# - Wait 5 minutes
# - Re-add custom domain
# - Enable "Enforce HTTPS"
```

---

## Maintenance

### Weekly Tasks

1. **Check workflow status:**
   - Actions tab → Recent workflows
   - All should show ✓ (green checkmark)

2. **Monitor deployment time:**
   - Expected: 3-5 minutes
   - If >10 minutes: Investigate bottlenecks

3. **Test documentation updates:**
   - Push small change to docs/
   - Verify automatic deployment works

### Monthly Tasks

1. **Update Python version:**
   - Check for Python 3.10+ availability
   - Update `.github/workflows/deploy-docs.yml`:
     ```yaml
     - name: Set up Python 3.10
       uses: actions/setup-python@v5
       with:
         python-version: '3.10'
     ```

2. **Update GitHub Actions:**
   - Check for action updates:
     - `actions/checkout@v4` → `@v5`
     - `actions/setup-python@v5` → `@v6`
     - `peaceiris/actions-gh-pages@v4` → `@v5`

3. **Validate accessibility:**
   - Run Lighthouse audit
   - Verify WCAG 2.1 Level AA compliance
   - Fix any new issues

### Quarterly Tasks

1. **Link validation:**
   - Run linkchecker on entire site
   - Fix broken external links
   - Update outdated documentation references

2. **Performance audit:**
   - Run Lighthouse performance audit
   - Optimize large images (compress, resize)
   - Minify CSS/JS if score <90

3. **Security audit:**
   - Check for vulnerable dependencies
   - Update Sphinx and extensions
   - Review GitHub Actions security advisories

---

## References

### Official Documentation

- **GitHub Pages:** https://docs.github.com/en/pages
- **GitHub Actions:** https://docs.github.com/en/actions
- **Sphinx Deployment:** https://www.sphinx-doc.org/en/master/tutorial/deploying.html

### GitHub Actions

- **actions/checkout:** https://github.com/actions/checkout
- **actions/setup-python:** https://github.com/actions/setup-python
- **peaceiris/actions-gh-pages:** https://github.com/peaceiris/actions-gh-pages

### Troubleshooting

- **GitHub Pages Troubleshooting:** https://docs.github.com/en/pages/getting-started-with-github-pages/troubleshooting-custom-domains-and-github-pages
- **Sphinx Build Issues:** https://www.sphinx-doc.org/en/master/usage/troubleshooting.html

### Related Guides

- **arXiv Submission:** `docs/publication/ARXIV_SUBMISSION_GUIDE.md`
- **Citation Guide:** `docs/publication/CITATION_GUIDE.md`
- **Submission Checklist:** `docs/publication/SUBMISSION_CHECKLIST.md`

---

**End of GitHub Pages Deployment Guide**

**Document Version:** 1.0
**Last Updated:** November 12, 2025
**Status:** OPERATIONAL
**Maintenance:** Update quarterly (dependency updates, security patches)
