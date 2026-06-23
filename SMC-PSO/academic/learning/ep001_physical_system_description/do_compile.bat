@echo off
cd /d %~dp0
echo Cleaning old files...
del /f /q *.pdf *.aux *.log *.toc *.out 2>nul
echo Running pdflatex 4 times...
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex
echo.
if exist EP001_unified.pdf (
    echo [OK] PDF Created Successfully!
    dir /B EP001_unified.pdf
) else (
    echo [ERROR] PDF not created
)
