@echo off
REM Generate minimal audit prompt for manual copy/paste into Gemini CLI
REM Usage: generate_audit_prompt.bat [section_number]
REM Example: generate_audit_prompt.bat 1  (for Section 01)
REM          generate_audit_prompt.bat 5  (for Section 05)

setlocal enabledelayedexpansion

if "%1"=="" (
    echo Usage: %0 ^<section_number^>
    echo Example: %0 1  ^(for Section 01: Introduction^)
    echo.
    echo Available sections:
    echo   1  - Introduction
    echo   2  - List of Figures
    echo   3  - System Model
    echo   4  - Controller Design
    echo   5  - Lyapunov Stability [PRIORITY]
    echo   6  - PSO Methodology
    echo   7  - Experimental Setup
    echo   8  - Performance Results [PRIORITY]
    echo   9  - Robustness Analysis [PRIORITY]
    echo   10 - Discussion
    echo   11 - Conclusion
    echo   12 - Acknowledgments
    exit /b 1
)

REM Calculate section index (0-based) and section number (01-12)
set /a section_idx=%1-1
set /a section_num=%1
if %section_num% LSS 10 (set section_num=0%section_num%)

REM Get section metadata
for /f "delims=" %%a in ('jq -r ".sections[%section_idx%].section_name" audit_config.json') do set section_name=%%a
for /f "delims=" %%b in ('jq -r ".sections[%section_idx%].markdown_file" audit_config.json') do set md_file=%%b

REM Check if file exists
if not exist "%md_file%" (
    echo ERROR: File not found: %md_file%
    exit /b 1
)

REM Set output file
set output_file=audits\Section_%section_num%_PROMPT.txt

REM Print header
echo ========================================================================
echo AUDIT PROMPT FOR GEMINI CLI
echo Section %section_num%: %section_name%
echo ========================================================================
echo.
echo INSTRUCTIONS:
echo 1. Output saved to: %output_file%
echo 2. Open the file and copy ALL content
echo 3. Paste into Gemini CLI
echo 4. Wait for response
echo 5. Save response to: audits\Section_%section_num%_AUDIT_REPORT.md
echo.
echo ========================================================================
echo Generating prompt...
echo ========================================================================

REM Create output file
echo ======================================================================== > "%output_file%"
echo COPY EVERYTHING BELOW THIS LINE >> "%output_file%"
echo ======================================================================== >> "%output_file%"
echo. >> "%output_file%"

REM Add markdown content
type "%md_file%" >> "%output_file%"

REM Add separator
echo. >> "%output_file%"
echo. >> "%output_file%"
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ >> "%output_file%"
echo AUDIT INSTRUCTIONS >> "%output_file%"
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ >> "%output_file%"
echo. >> "%output_file%"

REM Add audit prompt
jq -r ".sections[%section_idx%].audit_prompt" audit_config.json >> "%output_file%"

REM Add footer
echo. >> "%output_file%"
echo ======================================================================== >> "%output_file%"
echo END OF PROMPT >> "%output_file%"
echo ======================================================================== >> "%output_file%"

echo.
echo [OK] Prompt generated successfully!
echo [INFO] File: %output_file%
echo.
echo Next steps:
echo   1. Open: %output_file%
echo   2. Select all (Ctrl+A) and copy (Ctrl+C)
echo   3. Paste into Gemini CLI
echo   4. Save Gemini's response to: audits\Section_%section_num%_AUDIT_REPORT.md

endlocal
