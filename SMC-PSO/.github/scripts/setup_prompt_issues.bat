@echo off
REM ==========================================================================================\\\
REM ========================== setup_prompt_issues.bat ====================================\\\
REM ==========================================================================================\\\
REM
REM Setup script to create GitHub issues from the prompt folder documentation.
REM This script will create 9 comprehensive issues based on the documented test failures
REM and analysis reports found in the prompt/ directory.
REM
REM Usage:
REM   .github\scripts\setup_prompt_issues.bat          # Create all issues
REM   .github\scripts\setup_prompt_issues.bat --dry-run # Preview what would be created
REM

setlocal enabledelayedexpansion

echo ============================================
echo   DIP SMC PSO - GitHub Issues Setup
echo ============================================
echo.

REM Get the script directory and repository root
set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\"

REM Check if we're in the right directory
if not exist "%REPO_ROOT%prompt\pytest_analysis_report.md" (
    echo Error: Cannot find prompt\pytest_analysis_report.md
    echo Please run this script from the repository root
    exit /b 1
)

REM Check if GitHub CLI is installed
gh --version >nul 2>&1
if errorlevel 1 (
    echo Error: GitHub CLI ^(gh^) is not installed
    echo Install it with: winget install GitHub.cli
    exit /b 1
)

REM Check if authenticated
gh auth status >nul 2>&1
if errorlevel 1 (
    echo Error: GitHub CLI is not authenticated
    echo Please run: gh auth login
    exit /b 1
)

echo [OK] GitHub CLI is installed and authenticated

REM Check if create_issue script exists
if not exist "%REPO_ROOT%.github\scripts\create_issue.bat" (
    echo Error: create_issue.bat script not found
    echo Expected: %REPO_ROOT%.github\scripts\create_issue.bat
    exit /b 1
)

echo [OK] Issue creation script found

REM Parse command line arguments
set "DRY_RUN="
if "%1"=="--dry-run" (
    set "DRY_RUN=--dry-run"
    echo DRY RUN MODE - No issues will be created
)

echo.
echo Analyzing prompt folder documentation...

REM Check what's in the prompt folder
echo Found documentation files:
dir /b "%REPO_ROOT%prompt\*.md" "%REPO_ROOT%prompt\*.txt" 2>nul | findstr /E ".md .txt"

echo.
echo Creating GitHub issues from documented problems...

REM Run the Python script to create issues
cd /d "%REPO_ROOT%"
python .github\scripts\create_prompt_issues.py %DRY_RUN%

if "%DRY_RUN%"=="" (
    echo.
    echo ============================================
    echo   Issues Created Successfully!
    echo ============================================
    echo.
    echo Next Steps:
    echo.
    echo 1. View all created issues:
    echo    gh issue list --search "state:open"
    echo.
    echo 2. View critical issues:
    echo    gh issue list --search "label:critical state:open"
    echo.
    echo 3. Access the Issue Dashboard:
    echo    type .github\ISSUE_DASHBOARD.md
    echo.
    echo 4. Use the Navigation Guide:
    echo    type .github\ISSUE_NAVIGATION_GUIDE.md
    echo.
    echo 5. Web interface links:
    echo    - All Issues: https://github.com/theSadeQ/dip-smc-pso/issues
    echo    - Critical Issues: https://github.com/theSadeQ/dip-smc-pso/issues?q=is%%3Aissue+is%%3Aopen+label%%3Acritical
    echo    - High Priority: https://github.com/theSadeQ/dip-smc-pso/issues?q=is%%3Aissue+is%%3Aopen+label%%3Ahigh
    echo.
    echo Issue Summary:
    echo   - 3 CRITICAL issues ^(stability, safety, configuration^)
    echo   - 3 HIGH priority issues ^(PSO, factory, adaptive SMC^)
    echo   - 3 MEDIUM priority issues ^(testing, performance, UI^)
    echo.
    echo IMPORTANT: Critical issues require response within 4 hours!

) else (
    echo.
    echo ============================================
    echo   Dry Run Complete
    echo ============================================
    echo.
    echo To actually create the issues, run:
    echo    .github\scripts\setup_prompt_issues.bat
    echo.
)

echo Setup complete!
pause