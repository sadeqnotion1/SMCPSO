@echo off
cd /d D:\Projects\main\academic\learning\ep001_physical_system_description
del /f /q EP001_unified.pdf EP001_unified.aux EP001_unified.log 2>nul
echo [INFO] Compiling EP001_unified.tex with hyperref fix
pdflatex -interaction=nonstopmode EP001_unified.tex
pdflatex -interaction=nonstopmode EP001_unified.tex
pdflatex -interaction=nonstopmode EP001_unified.tex
pdflatex -interaction=nonstopmode EP001_unified.tex
echo [OK] Compilation complete
if exist EP001_unified.pdf (
    echo [OK] PDF created successfully
    dir EP001_unified.pdf
) else (
    echo [ERROR] PDF not created
)
pause
