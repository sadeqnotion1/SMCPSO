@echo off
REM Combine a prompt file with enhanced rigor supplement
REM Usage: add_enhanced_rigor.bat <prompt_number>
REM Example: add_enhanced_rigor.bat 2  (for Section 02 - Performance Results)

if "%1"=="" (
    echo Usage: add_enhanced_rigor.bat ^<section_number^>
    echo.
    echo Example: add_enhanced_rigor.bat 2
    echo.
    echo Available sections:
    echo   02 - Performance Results [HIGH PRIORITY]
    echo   03 - Robustness Analysis [HIGH PRIORITY]
    echo   04 - Controller Design
    echo   05 - Experimental Setup
    echo   06 - Introduction
    echo   07 - PSO Methodology
    echo   08 - System Model
    echo   09 - Discussion
    echo   10 - Conclusion
    exit /b 1
)

set section_num=%1
if %section_num% LSS 10 (set section_num=0%section_num%)

REM Find the matching prompt file
set "prompt_file="
for %%f in (%section_num%-*.txt) do (
    if not defined prompt_file set "prompt_file=%%f"
)

if not defined prompt_file (
    echo [ERROR] No prompt file found starting with %section_num%-
    echo.
    echo Files in directory:
    dir /b %section_num%-*.txt
    exit /b 1
)

set "output_file=%section_num%-ENHANCED_PROMPT.txt"

echo ========================================================================
echo ENHANCED RIGOR PROMPT GENERATOR
echo ========================================================================
echo.
echo [INFO] Source prompt: %prompt_file%
echo [INFO] Output file: %output_file%
echo.

REM Combine files
type "%prompt_file%" > "%output_file%"
echo. >> "%output_file%"
echo. >> "%output_file%"
type "ENHANCED_RIGOR_SUPPLEMENT.txt" >> "%output_file%"

echo [OK] Enhanced prompt created successfully!
echo.
echo File stats:
for %%A in ("%output_file%") do echo   - Size: %%~zA bytes
for /f %%A in ('find /c /v "" ^< "%output_file%"') do echo   - Lines: %%A
echo.
echo Next steps:
echo   1. Open: %output_file%
echo   2. Copy all content (Ctrl+A, Ctrl+C)
echo   3. Paste into Gemini CLI
echo   4. Save response to: %section_num%-ENHANCED-AUDIT-REPORT.md
echo.
