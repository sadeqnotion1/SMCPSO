@echo off
cd /d "%~dp0"
echo Compiling EP001 with MiKTeX...
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex
if exist EP001_unified.pdf (
    echo.
    echo [OK] EP001_unified.pdf created successfully!
) else (
    echo [ERROR] PDF creation failed.
)
