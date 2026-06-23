@echo off
REM Automated Thesis Build Script
REM Windows Batch Version

echo [INFO] Starting thesis compilation...

REM First pass
echo [STEP 1/4] Running pdflatex (1st pass)...
pdflatex -interaction=nonstopmode main.tex

REM BibTeX
echo [STEP 2/4] Running bibtex...
bibtex main

REM Second pass
echo [STEP 3/4] Running pdflatex (2nd pass)...
pdflatex -interaction=nonstopmode main.tex

REM Third pass
echo [STEP 4/4] Running pdflatex (3rd pass)...
pdflatex -interaction=nonstopmode main.tex

REM Cleanup
echo [INFO] Cleaning auxiliary files...
del main.aux main.log main.out main.toc main.lof main.lot main.bbl main.blg 2>nul

echo [OK] Build complete! Output: main.pdf
pause
