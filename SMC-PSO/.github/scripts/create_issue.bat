@echo off
REM GitHub Issues Creation Script for Windows (DIP_SMC_PSO Project)
REM Wrapper for create_issue.sh

REM Check if Git Bash is available
where bash >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Git Bash not found. Please install Git for Windows.
    echo Download from: https://git-scm.com/download/win
    exit /b 1
)

REM Run the bash script with all arguments
bash "%~dp0create_issue.sh" %*