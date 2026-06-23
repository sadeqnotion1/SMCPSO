@echo off
REM Build Individual Chapter PDFs - Windows Batch Script
REM This script compiles each chapter as a standalone PDF

setlocal enabledelayedexpansion

echo ======================================================================
echo BUILDING INDIVIDUAL CHAPTER PDFs
echo ======================================================================

REM Create build directory
if not exist "build\individual_chapters" mkdir "build\individual_chapters"

REM Set MiKTeX to auto-install packages (suppresses update warnings)
initexmf --set-config-value [MPM]AutoInstall=1 2>nul

cd build\individual_chapters

echo.
echo [PHASE 1] Building Chapters (1-12)...
echo.

set CHAPTER_COUNT=0
set SUCCESS_COUNT=0

REM Chapter 1
call :compile_chapter chapter_01 "../../source/chapters/ch01_introduction.tex" "Chapter 1: Introduction" 1

REM Chapter 2
call :compile_chapter chapter_02 "../../source/chapters/ch02_mathematical_foundations.tex" "Chapter 2: Mathematical Preliminaries" 2

REM Chapter 3
call :compile_chapter chapter_03 "../../source/chapters/ch03_classical_smc.tex" "Chapter 3: Classical SMC" 3

REM Chapter 4
call :compile_chapter chapter_04 "../../source/chapters/ch04_super_twisting.tex" "Chapter 4: Super-Twisting Algorithm" 4

REM Chapter 5
call :compile_chapter chapter_05 "../../source/chapters/ch05_adaptive_smc.tex" "Chapter 5: Adaptive SMC" 5

REM Chapter 6
call :compile_chapter chapter_06 "../../source/chapters/ch06_hybrid_smc.tex" "Chapter 6: Hybrid SMC" 6

REM Chapter 7
call :compile_chapter chapter_07 "../../source/chapters/ch07_pso_theory.tex" "Chapter 7: PSO Theory" 7

REM Chapter 8
call :compile_chapter chapter_08 "../../source/chapters/ch08_benchmarking.tex" "Chapter 8: Benchmarking" 8

REM Chapter 9
call :compile_chapter chapter_09 "../../source/chapters/ch09_pso_results.tex" "Chapter 9: PSO Results" 9

REM Chapter 10
call :compile_chapter chapter_10 "../../source/chapters/ch10_advanced_topics.tex" "Chapter 10: Advanced Topics" 10

REM Chapter 11
call :compile_chapter chapter_11 "../../source/chapters/ch11_software.tex" "Chapter 11: Software Implementation" 11

REM Chapter 12
call :compile_chapter chapter_12 "../../source/chapters/ch12_case_studies.tex" "Chapter 12: Case Studies" 12

echo.
echo [PHASE 2] Building Appendices (A-D)...
echo.

REM Appendix A
call :compile_chapter appendix_a "../../source/appendices/appendix_a_math.tex" "Appendix A: Mathematical Prerequisites" APPENDIX

REM Appendix B
call :compile_chapter appendix_b "../../source/appendices/appendix_b_lyapunov_proofs.tex" "Appendix B: Lyapunov Proofs" APPENDIX

REM Appendix C
call :compile_chapter appendix_c "../../source/appendices/appendix_c_api.tex" "Appendix C: API Reference" APPENDIX

REM Appendix D
call :compile_chapter appendix_d "../../source/appendices/appendix_d_solutions.tex" "Appendix D: Exercise Solutions" APPENDIX

echo.
echo ======================================================================
echo [FINAL] %SUCCESS_COUNT%/%CHAPTER_COUNT% PDFs created successfully
echo [LOCATION] build\individual_chapters\
echo ======================================================================

cd ..\..
goto :eof

:compile_chapter
REM Function to create wrapper .tex and compile to PDF
REM Args: %1=output_name, %2=content_path, %3=title, %4=chapter_number (or "APPENDIX")

set /a CHAPTER_COUNT+=1
set OUTPUT_NAME=%~1
set CONTENT_PATH=%~2
set TITLE=%~3
set CHAPTER_NUM=%~4

echo [%CHAPTER_COUNT%] %TITLE%...

REM Determine counter setup command
REM FIX: Use final chapter number (N), not N-1, because hyperref prevents \chapter from incrementing
set COUNTER_CMD=
if "%CHAPTER_NUM%"=="APPENDIX" (
    set COUNTER_CMD=\appendix
) else if not "%CHAPTER_NUM%"=="" (
    set COUNTER_CMD=\setcounter{chapter}{%CHAPTER_NUM%}
)

REM Create standalone wrapper .tex file
(
echo \documentclass[11pt,oneside]{book}
echo.
echo %% Include preamble
echo \input{../../preamble.tex}
echo.
echo \begin{document}
echo.
echo %% Title page
echo \begin{titlepage}
echo \centering
echo \vspace*{2cm}
echo {\Huge\bfseries %TITLE% \par}
echo \vspace{1cm}
echo {\Large Sliding Mode Control and PSO Optimization \par}
echo {\Large for Double-Inverted Pendulum Systems \par}
echo \vfill
echo {\large Standalone Chapter \par}
echo \end{titlepage}
echo.
echo %% Table of contents
echo \tableofcontents
echo \clearpage
echo.
echo %% Set chapter/appendix counter
if not "!COUNTER_CMD!"=="" echo !COUNTER_CMD!
echo.
echo %% Include chapter content
echo \input{%CONTENT_PATH%}
echo.
echo \end{document}
) > %OUTPUT_NAME%.tex

REM Compile with pdflatex (2 runs for cross-references)
pdflatex -shell-escape -interaction=batchmode %OUTPUT_NAME%.tex >nul 2>&1
pdflatex -shell-escape -interaction=batchmode %OUTPUT_NAME%.tex >nul 2>&1

REM Check if PDF created
if exist "%OUTPUT_NAME%.pdf" (
    for %%A in ("%OUTPUT_NAME%.pdf") do set SIZE=%%~zA
    set /a SIZE_KB=!SIZE!/1024
    echo    [OK] %OUTPUT_NAME%.pdf ^(!SIZE_KB! KB^)
    set /a SUCCESS_COUNT+=1

    REM Cleanup aux files
    del %OUTPUT_NAME%.aux %OUTPUT_NAME%.log %OUTPUT_NAME%.out %OUTPUT_NAME%.toc 2>nul
) else (
    echo    [ERROR] Compilation failed for %OUTPUT_NAME%.pdf
)

goto :eof
