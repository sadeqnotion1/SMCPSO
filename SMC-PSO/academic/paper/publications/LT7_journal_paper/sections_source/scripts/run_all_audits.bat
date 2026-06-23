@echo off
REM Run all 12 section audits using Gemini CLI (Windows version)
REM Usage: run_all_audits.bat

setlocal enabledelayedexpansion

echo [INFO] LT-7 Research Paper - Automated Section Audits
echo [INFO] Starting audit process for 12 sections...
echo.

REM Check prerequisites
where gemini >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Gemini CLI not found. Install with: pip install google-generativeai-cli
    exit /b 1
)

where jq >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] jq not found. Download from: https://stedolan.github.io/jq/download/
    echo [INFO] Or install with chocolatey: choco install jq
    exit /b 1
)

if "%GOOGLE_API_KEY%"=="" (
    echo [WARNING] GOOGLE_API_KEY not set. You may encounter authentication errors.
    echo [INFO] Set with: set GOOGLE_API_KEY=your-api-key
)

REM Create audits directory
if not exist "audits" mkdir audits

REM Track statistics
set total_sections=12
set completed=0
set failed=0

REM Process each section
for /L %%i in (0,1,11) do (
    REM Calculate section number with zero padding
    set /a section_idx=%%i
    set /a section_num=%%i+1
    if !section_num! LSS 10 (set section_num=0!section_num!)

    REM Get section metadata from JSON
    for /f "delims=" %%a in ('jq -r ".sections[%%i].section_name" audit_config.json') do set section_name=%%a
    for /f "delims=" %%b in ('jq -r ".sections[%%i].markdown_file" audit_config.json') do set md_file=%%b

    REM Output files
    set output_file=audits\Section_!section_num!_AUDIT_REPORT.md
    set temp_input=temp_audit_input_!section_num!.txt

    echo [INFO] ==========================================
    echo [INFO] Section !section_num!: !section_name!
    echo [INFO] Source: !md_file!
    echo [INFO] Output: !output_file!
    echo.

    REM Check if source file exists
    if not exist "!md_file!" (
        echo [ERROR] Source file not found: !md_file!
        set /a failed+=1
        goto :continue_loop
    )

    REM Create combined input file
    echo [INFO] Creating audit input...
    type "!md_file!" > "!temp_input!"
    echo. >> "!temp_input!"
    echo. >> "!temp_input!"
    echo === AUDIT INSTRUCTIONS === >> "!temp_input!"
    echo. >> "!temp_input!"
    jq -r ".sections[%%i].audit_prompt" audit_config.json >> "!temp_input!"

    REM Run Gemini audit
    echo [INFO] Running Gemini audit (this may take 30-60 seconds)...
    gemini < "!temp_input!" > "!output_file!" 2>&1
    if %ERRORLEVEL% EQU 0 (
        if exist "!output_file!" (
            for %%F in ("!output_file!") do set file_size=%%~zF
            if !file_size! GTR 0 (
                echo [OK] Audit completed successfully (!file_size! bytes)
                set /a completed+=1
            ) else (
                echo [ERROR] Audit produced empty output
                set /a failed+=1
            )
        ) else (
            echo [ERROR] Output file not created
            set /a failed+=1
        )
    ) else (
        echo [ERROR] Gemini audit failed
        set /a failed+=1
    )

    REM Cleanup temp file
    if exist "!temp_input!" del "!temp_input!"

    echo.

    :continue_loop
)

REM Print summary
echo [INFO] ==========================================
echo [INFO] AUDIT SUMMARY
echo [INFO] ==========================================
echo [INFO] Total sections: %total_sections%
echo [OK] Completed: %completed%
echo [ERROR] Failed: %failed%
echo.

if %completed% EQU %total_sections% (
    echo [OK] All audits completed successfully!
    echo [INFO] Reports saved to audits\ directory
    echo.
    echo [INFO] Next steps:
    echo   1. Review audit reports in audits\ directory
    echo   2. Focus on CRITICAL sections first (05, 08, 09^)
    echo   3. Extract overall scores: findstr "Overall:" audits\*.md
    echo   4. Collect critical issues: findstr "CRITICAL" audits\*.md
    echo   5. Create AUDIT_SUMMARY.md after reviewing all reports
) else (
    echo [WARNING] Some audits failed. Check error messages above.
    echo [INFO] Successfully audited %completed% out of %total_sections% sections.
)

echo.
echo [INFO] Audit process complete.

endlocal
