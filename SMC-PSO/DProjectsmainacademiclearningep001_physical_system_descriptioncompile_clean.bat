@echo off
cd /d "%~dp0"
echo ========================================
echo Compiling EP001 - Clean Build
echo ========================================
echo.

REM Delete old files
del /f /q EP001_unified.pdf EP001_unified.aux EP001_unified.log EP001_unified.toc EP001_unified.out 2>nul
echo [OK] Deleted old files

REM Run pdflatex 4 times
echo [1/4] Running pdflatex...
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex > compile_log.txt 2>&1
echo [OK] Pass 1 complete

echo [2/4] Running pdflatex...
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex >> compile_log.txt 2>&1
echo [OK] Pass 2 complete

echo [3/4] Running pdflatex...
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex >> compile_log.txt 2>&1
echo [OK] Pass 3 complete

echo [4/4] Running pdflatex...
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex >> compile_log.txt 2>&1
echo [OK] Pass 4 complete

REM Check if PDF was created
if exist EP001_unified.pdf (
    echo.
    echo ========================================
    echo [SUCCESS] PDF created successfully!
    echo ========================================
    for %%f in (EP001_unified.pdf) do echo File size: %%~zf bytes
    dir /B EP001_unified.pdf EP001_unified.log
) else (
    echo.
    echo ========================================
    echo [ERROR] PDF NOT created
    echo ========================================
    type compile_log.txt
)
