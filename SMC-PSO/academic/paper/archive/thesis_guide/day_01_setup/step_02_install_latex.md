# Step 2: Install LaTeX Distribution

**Time**: 45 minutes
**Difficulty**: Easy (mostly waiting for downloads)
**Tools**: Web browser, command line

---

## OBJECTIVE

Install a complete LaTeX distribution on your system so you can compile .tex files into professional PDFs.

---

## WHICH DISTRIBUTION TO INSTALL?

### Windows Users

**MiKTeX** (Recommended)
- Download: https://miktex.org/download
- Size: ~200 MB installer, ~1.5 GB installed
- Features: Auto-installs packages on-demand
- Time: 15-20 minutes

**Alternative**: TeX Live
- Download: https://tug.org/texlive/windows.html
- Size: ~4 GB (full installation)
- Features: All packages pre-installed
- Time: 45-60 minutes

### macOS Users

**MacTeX** (Recommended)
- Download: https://www.tug.org/mactex/
- Size: ~4.5 GB
- Features: Complete TeX Live + Mac-specific tools
- Time: 30-45 minutes

### Linux Users

**TeX Live** (Recommended)
- Ubuntu/Debian:
  ```bash
  sudo apt update
  sudo apt install texlive-full
  ```
- Fedora/RHEL:
  ```bash
  sudo dnf install texlive-scheme-full
  ```
- Size: ~3-5 GB
- Time: 30-60 minutes (depending on internet speed)

### No Installation Option

**Overleaf** (Online LaTeX Editor)
- URL: https://www.overleaf.com/
- Features: No installation, web-based, real-time collaboration
- Limitation: Free plan has compilation timeout (4 min)
- Best for: Quick start, collaborative writing

---

## INSTALLATION INSTRUCTIONS

### Windows - MiKTeX (Detailed Steps)

1. **Download Installer**
   - Visit: https://miktex.org/download
   - Click "Download" for Windows
   - Get: `basic-miktex-x64.exe` (~200 MB)

2. **Run Installer**
   - Double-click downloaded file
   - Click "Yes" on User Account Control prompt
   - Accept license agreement
   - Choose installation type:
     - **Install for All Users** (recommended if admin)
     - Install for Current User (if no admin rights)

3. **Choose Installation Directory**
   - Default: `C:\Program Files\MiKTeX`
   - Can change to: `C:\MiKTeX` (shorter path)

4. **Configure Settings**
   - Package repository: **Any CTAN mirror** (default)
   - Install missing packages: **Yes** (automatic)
   - Paper size: **A4** (or Letter for US)

5. **Wait for Installation**
   - Progress bar: 5-10 minutes
   - Downloads ~1.2 GB of core packages

6. **Add to PATH**
   - Installer usually does this automatically
   - Verify: Open Command Prompt, run `pdflatex --version`
   - If command not found, manually add:
     ```powershell
     setx PATH "%PATH%;C:\Program Files\MiKTeX\miktex\bin\x64"
     ```

### macOS - MacTeX (Detailed Steps)

1. **Download PKG**
   - Visit: https://www.tug.org/mactex/
   - Click "MacTeX.pkg" (~4.5 GB download)
   - Save to Downloads folder

2. **Run Installer**
   - Double-click `MacTeX.pkg`
   - Click "Continue" through introduction screens
   - Accept license
   - Click "Install" (requires admin password)

3. **Wait for Installation**
   - Progress bar: 15-30 minutes
   - Installs to: `/Library/TeX/`

4. **Update PATH**
   - Installer adds to PATH automatically
   - Close and reopen Terminal
   - Verify: `pdflatex --version`

### Linux - TeX Live (Detailed Steps)

**Ubuntu/Debian**:
```bash
# Update package lists
sudo apt update

# Install full TeX Live (recommended)
sudo apt install texlive-full

# Lighter alternative (basic + science packages):
# sudo apt install texlive-latex-base texlive-latex-extra texlive-science

# Wait 20-40 minutes for download + installation
```

**Fedora/RHEL**:
```bash
# Install full scheme
sudo dnf install texlive-scheme-full

# Lighter alternative:
# sudo dnf install texlive-latex texlive-xetex
```

**Arch Linux**:
```bash
# Install full TeX Live
sudo pacman -S texlive-most texlive-lang
```

---

## VERIFICATION

### Test 1: Check Installation

**Windows**:
```powershell
pdflatex --version
```

**macOS/Linux**:
```bash
pdflatex --version
```

**Expected Output**:
```
pdfLaTeX 3.141592653-2.6-1.40.XX (TeX Live 2023 or MiKTeX)
```

If you see version info, installation succeeded!

### Test 2: Compile a Simple Document

**Create test file** (`test.tex`):
```latex
\documentclass{article}
\begin{document}
Hello, LaTeX!
\end{document}
```

**Compile**:
```bash
pdflatex test.tex
```

**Expected Output**:
- `test.pdf` file created
- No errors in terminal output
- Opens to show "Hello, LaTeX!" text

### Test 3: Check Essential Packages

**Windows (MiKTeX)**:
```powershell
mpm --list | findstr "amsmath graphicx hyperref"
```

**macOS/Linux (TeX Live)**:
```bash
tlmgr list --only-installed | grep -E "amsmath|graphicx|hyperref"
```

**Expected**: All three packages should appear in list.

---

## REQUIRED PACKAGES FOR THESIS

Your thesis will need these packages (most are included in full installs):

**Core Packages** (must have):
- `amsmath`, `amsfonts`, `amssymb` - Math symbols and equations
- `graphicx` - Figures and images
- `hyperref` - Clickable table of contents, citations
- `natbib` or `biblatex` - Bibliography management
- `geometry` - Page margins and layout
- `fancyhdr` - Headers and footers

**Science/Engineering** (highly recommended):
- `algorithm2e` - Algorithm pseudocode
- `listings` - Code listings
- `siunitx` - SI units formatting
- `nomencl` - Nomenclature/symbol list
- `tikz`, `pgfplots` - Drawing diagrams and plots

**Utilities**:
- `caption` - Figure/table caption customization
- `subcaption` - Subfigures (a), (b), (c)
- `booktabs` - Professional tables
- `float` - Figure placement control
- `xcolor` - Colors for code/diagrams

### How to Install Missing Packages

**MiKTeX** (automatic):
- Just compile your document
- Pop-up will ask: "Install package X?"
- Click "Install" (happens automatically)

**TeX Live** (manual):
```bash
sudo tlmgr install <package-name>
# Example:
sudo tlmgr install siunitx algorithm2e nomencl
```

**Overleaf**:
- All packages pre-installed, no action needed

---

## TROUBLESHOOTING

### Issue: "pdflatex: command not found"

**Cause**: LaTeX not in system PATH

**Windows Fix**:
```powershell
# Add to PATH manually
setx PATH "%PATH%;C:\Program Files\MiKTeX\miktex\bin\x64"
# Close and reopen Command Prompt
```

**macOS Fix**:
```bash
# Add to ~/.zshrc or ~/.bash_profile
echo 'export PATH="/Library/TeX/texbin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Linux Fix**:
```bash
# Usually auto-added, but if not:
echo 'export PATH="/usr/local/texlive/2023/bin/x86_64-linux:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Issue: "! LaTeX Error: File 'amsmath.sty' not found"

**Cause**: Incomplete installation or missing package

**MiKTeX Fix**:
- Open "MiKTeX Console" (Start Menu → MiKTeX Console)
- Click "Updates" tab
- Click "Check for updates"
- Install all available updates

**TeX Live Fix**:
```bash
sudo tlmgr update --self --all
sudo tlmgr install amsmath
```

### Issue: Installation taking forever (1+ hour)

**Cause**: Full installation downloads 3-5 GB

**Solutions**:
1. **Be patient**: Full install takes 30-60 min on slow connections
2. **Install basic version**:
   - MiKTeX "Basic" installer (installs packages on-demand)
   - TeX Live "scheme-basic" (400 MB instead of 5 GB)
3. **Use Overleaf**: Skip local installation entirely

### Issue: Not enough disk space

**Cause**: Full LaTeX distribution needs 4-6 GB free space

**Solutions**:
- Free up disk space (delete temp files, old downloads)
- Install basic version (~1 GB):
  - MiKTeX: Basic installer
  - TeX Live: `texlive-latex-base` + needed packages only
- Use Overleaf (no local storage needed)

---

## OPTIONAL: INSTALL LATEX EDITOR

While you can use any text editor, these provide helpful features:

### TeXstudio (Beginner-Friendly)

**Windows/macOS/Linux**:
- Download: https://www.texstudio.org/
- Features: Auto-completion, built-in PDF viewer, syntax highlighting
- Best for: Beginners, those who want "LaTeX IDE"

### VS Code + LaTeX Workshop (Advanced)

**All platforms**:
1. Install VS Code: https://code.visualstudio.com/
2. Install extension: "LaTeX Workshop" by James Yu
3. Features: Live preview, IntelliSense, Git integration
4. Best for: Programmers, those familiar with VS Code

### Overleaf (Online)

- No installation needed
- Web browser only
- Real-time collaboration
- Best for: Quick start, team projects

---

## VALIDATION CHECKLIST

Before proceeding to Step 3:

- [ ] `pdflatex --version` shows version info
- [ ] Created and compiled `test.tex` successfully
- [ ] `test.pdf` opens and shows "Hello, LaTeX!"
- [ ] Essential packages installed (amsmath, graphicx, hyperref)
- [ ] (Optional) LaTeX editor installed and configured
- [ ] At least 5 GB free disk space remaining

---

## TIME CHECK

- Download LaTeX distribution: 10-20 min (depends on internet)
- Install: 10-30 min (depends on system speed)
- Verify installation: 5 min
- Install editor (optional): 10 min
- **Total**: 35-65 minutes

If you're over 1 hour, consider using Overleaf to save time.

---

## NEXT STEP

Once LaTeX is installed and verified:

**Proceed to**: `step_03_setup_automation_scripts.md`

This will set up Python scripts to automate:
- Markdown → LaTeX conversion
- CSV → LaTeX table generation
- Figure generation from data

---

**[OK] LaTeX installed? Test with `pdflatex --version` and move on!**
