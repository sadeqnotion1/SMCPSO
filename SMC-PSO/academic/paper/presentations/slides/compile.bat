@echo off
REM ============================================================================
REM Compile Script for DIP-SMC-PSO Presentation (Windows)
REM ============================================================================
REM This script compiles both the main Beamer presentation and speaker scripts
REM Usage: compile.bat [presentation|scripts|all|clean]
REM ============================================================================

setlocal enabledelayedexpansion

REM Configuration
set PRESENTATION=comprehensive_project_presentation
set SCRIPTS=speaker_scripts
set BUILD_DIR=build
set OUTPUT_DIR=output

REM Parse command line argument
set TARGET=%1
if "%TARGET%"=="" set TARGET=all

REM Main execution
if "%TARGET%"=="presentation" goto compile_presentation
if "%TARGET%"=="scripts" goto compile_scripts
if "%TARGET%"=="all" goto compile_all
if "%TARGET%"=="clean" goto clean_build
if "%TARGET%"=="-h" goto usage
if "%TARGET%"=="--help" goto usage

echo [ERROR] Unknown option: %TARGET%
goto usage

:compile_presentation
echo =====================================
echo Compiling Beamer Presentation
echo =====================================
call :compile_latex %PRESENTATION% "Beamer Presentation"
goto end

:compile_scripts
echo =====================================
echo Compiling Speaker Scripts
echo =====================================
call :compile_latex %SCRIPTS% "Speaker Scripts"
goto end

:compile_all
echo =====================================
echo Compiling All Documents
echo =====================================
call :compile_latex %PRESENTATION% "Beamer Presentation"
echo.
call :compile_latex %SCRIPTS% "Speaker Scripts"
echo.
echo =====================================
echo Compilation Complete!
echo =====================================
echo [INFO] Output files:
dir /B %OUTPUT_DIR%\*.pdf
goto end

:clean_build
echo [CLEAN] Removing build artifacts...
if exist "%BUILD_DIR%" rmdir /S /Q "%BUILD_DIR%"
if exist "%OUTPUT_DIR%" rmdir /S /Q "%OUTPUT_DIR%"
echo [OK] Build directories cleaned
goto end

:usage
echo Usage: %0 [presentation^|scripts^|all^|clean]
echo.
echo Options:
echo   presentation  - Compile main Beamer presentation only
echo   scripts       - Compile speaker scripts only
echo   all           - Compile both presentation and scripts (default)
echo   clean         - Remove all build artifacts
echo.
goto end

REM ============================================================================
REM Function: Compile LaTeX document
REM ============================================================================
:compile_latex
set filename=%~1
set document_type=%~2

echo [INFO] Compiling %document_type%: %filename%.tex

REM Create output directories
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM First pass: Generate aux files
echo [COMPILE] First pass (pdflatex)...
pdflatex -interaction=nonstopmode -output-directory="%BUILD_DIR%" "%filename%.tex" >nul 2>&1

REM Second pass: Process bibliography (if exists)
if exist "references.bib" (
    echo [COMPILE] Processing bibliography (biber)...
    biber --input-directory="%BUILD_DIR%" --output-directory="%BUILD_DIR%" "%filename%" >nul 2>&1
)

REM Third pass: Resolve references
echo [COMPILE] Second pass (pdflatex)...
pdflatex -interaction=nonstopmode -output-directory="%BUILD_DIR%" "%filename%.tex" >nul 2>&1

REM Fourth pass: Final compilation
echo [COMPILE] Final pass (pdflatex)...
pdflatex -interaction=nonstopmode -output-directory="%BUILD_DIR%" "%filename%.tex" >nul 2>&1

REM Move PDF to output directory
if exist "%BUILD_DIR%\%filename%.pdf" (
    move /Y "%BUILD_DIR%\%filename%.pdf" "%OUTPUT_DIR%\" >nul
    echo [OK] PDF generated: %OUTPUT_DIR%\%filename%.pdf

    REM Display file size
    for %%A in ("%OUTPUT_DIR%\%filename%.pdf") do (
        set size=%%~zA
        set /A size_mb=!size! / 1048576
        echo [INFO] File size: !size_mb! MB
    )
) else (
    echo [ERROR] PDF generation failed for %filename%
    exit /b 1
)

goto :eof

:end
endlocal
