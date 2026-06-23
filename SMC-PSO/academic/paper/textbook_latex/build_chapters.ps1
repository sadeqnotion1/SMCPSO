# Build Individual Chapter PDFs - PowerShell Script
# This script compiles each chapter as a standalone PDF

Write-Host "=" * 70
Write-Host "BUILDING INDIVIDUAL CHAPTER PDFs"
Write-Host "=" * 70

# Create build directory
$buildDir = "build\individual_chapters"
if (!(Test-Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
}

Write-Host "`n[INFO] Build directory: $buildDir`n"

# Chapter definitions (Number is used to set \setcounter{chapter}{Number})
# FIX: hyperref prevents \chapter from incrementing, so use final value not N-1
$chapters = @(
    @{Name="chapter_01"; Path="chapters/ch01_introduction.tex"; Title="Chapter 1: Introduction"; Number=1},
    @{Name="chapter_02"; Path="chapters/ch02_mathematical_foundations.tex"; Title="Chapter 2: Mathematical Preliminaries"; Number=2},
    @{Name="chapter_03"; Path="chapters/ch03_classical_smc.tex"; Title="Chapter 3: Classical SMC"; Number=3},
    @{Name="chapter_04"; Path="chapters/ch04_super_twisting.tex"; Title="Chapter 4: Super-Twisting Algorithm"; Number=4},
    @{Name="chapter_05"; Path="chapters/ch05_adaptive_smc.tex"; Title="Chapter 5: Adaptive SMC"; Number=5},
    @{Name="chapter_06"; Path="chapters/ch06_hybrid_smc.tex"; Title="Chapter 6: Hybrid SMC"; Number=6},
    @{Name="chapter_07"; Path="chapters/ch07_pso_theory.tex"; Title="Chapter 7: PSO Theory"; Number=7},
    @{Name="chapter_08"; Path="chapters/ch08_benchmarking.tex"; Title="Chapter 8: Benchmarking"; Number=8},
    @{Name="chapter_09"; Path="chapters/ch09_pso_results.tex"; Title="Chapter 9: PSO Results"; Number=9},
    @{Name="chapter_10"; Path="chapters/ch10_advanced_topics.tex"; Title="Chapter 10: Advanced Topics"; Number=10},
    @{Name="chapter_11"; Path="chapters/ch11_software.tex"; Title="Chapter 11: Software Implementation"; Number=11},
    @{Name="chapter_12"; Path="chapters/ch12_case_studies.tex"; Title="Chapter 12: Case Studies"; Number=12}
)

$appendices = @(
    @{Name="appendix_a"; Path="appendices/appendix_a_math.tex"; Title="Appendix A: Mathematical Prerequisites"},
    @{Name="appendix_b"; Path="appendices/appendix_b_lyapunov_proofs.tex"; Title="Appendix B: Lyapunov Proofs"},
    @{Name="appendix_c"; Path="appendices/appendix_c_api.tex"; Title="Appendix C: API Reference"},
    @{Name="appendix_d"; Path="appendices/appendix_d_solutions.tex"; Title="Appendix D: Exercise Solutions"}
)

# Function to compile a chapter
function Compile-Chapter {
    param($Name, $ContentPath, $Title, $ChapterNumber = $null, $IsAppendix = $false)

    Write-Host "[$($script:count)] $Title..."
    $script:count++

    # Determine counter setup
    # FIX: Use final chapter number (N), not N-1, because hyperref prevents \chapter from incrementing
    $counterSetup = ""
    if ($IsAppendix) {
        $counterSetup = "\appendix"
    } elseif ($null -ne $ChapterNumber) {
        $counterSetup = "\setcounter{chapter}{$ChapterNumber}"
    }

    # Create wrapper .tex file
    $wrapperPath = Join-Path $buildDir "$Name.tex"
    $wrapperContent = @"
\documentclass[11pt,oneside]{book}

% Include preamble
\input{../../preamble.tex}

\begin{document}

% Title page
\begin{titlepage}
\centering
\vspace*{2cm}
{\Huge\bfseries $Title \par}
\vspace{1cm}
{\Large Sliding Mode Control and PSO Optimization \par}
{\Large for Double-Inverted Pendulum Systems \par}
\vfill
{\large Standalone Chapter \par}
\end{titlepage}

% Table of contents
\tableofcontents
\clearpage

% Set chapter/appendix counter
$counterSetup

% Include chapter content
\input{../../source/$ContentPath}

\end{document}
"@

    $wrapperContent | Out-File -FilePath $wrapperPath -Encoding UTF8

    # Compile with pdflatex (2 runs for cross-references)
    Push-Location $buildDir
    $null = pdflatex -shell-escape -interaction=batchmode "$Name.tex" 2>&1
    $null = pdflatex -shell-escape -interaction=batchmode "$Name.tex" 2>&1
    Pop-Location

    # Check if PDF was created
    $pdfPath = Join-Path $buildDir "$Name.pdf"
    if (Test-Path $pdfPath) {
        $sizeKB = [math]::Round((Get-Item $pdfPath).Length / 1KB, 1)
        Write-Host "   [OK] $Name.pdf ($sizeKB KB)" -ForegroundColor Green
        $script:successCount++

        # Cleanup aux files
        Remove-Item (Join-Path $buildDir "$Name.aux") -ErrorAction SilentlyContinue
        Remove-Item (Join-Path $buildDir "$Name.log") -ErrorAction SilentlyContinue
        Remove-Item (Join-Path $buildDir "$Name.out") -ErrorAction SilentlyContinue
        Remove-Item (Join-Path $buildDir "$Name.toc") -ErrorAction SilentlyContinue
    } else {
        Write-Host "   [ERROR] Compilation failed for $Name.pdf" -ForegroundColor Red
    }
}

# Initialize counters
$script:count = 1
$script:successCount = 0

# Build chapters
Write-Host "`n[PHASE 1] Building Chapters (1-12)...`n"
foreach ($chapter in $chapters) {
    Compile-Chapter -Name $chapter.Name -ContentPath $chapter.Path -Title $chapter.Title -ChapterNumber $chapter.Number
}

# Build appendices
Write-Host "`n[PHASE 2] Building Appendices (A-D)...`n"
foreach ($appendix in $appendices) {
    Compile-Chapter -Name $appendix.Name -ContentPath $appendix.Path -Title $appendix.Title -IsAppendix $true
}

# Final summary
$totalCount = $chapters.Count + $appendices.Count
Write-Host "`n" + ("=" * 70)
Write-Host "[FINAL] $script:successCount/$totalCount PDFs created successfully"
Write-Host "[LOCATION] $(Resolve-Path $buildDir)"
Write-Host "=" * 70
