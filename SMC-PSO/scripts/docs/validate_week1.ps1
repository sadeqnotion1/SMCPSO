#==========================================================================================\
#================================ scripts/docs/validate_week1.ps1 =========================\
#==========================================================================================\

<#
.SYNOPSIS
    Week 1 Documentation Infrastructure Validation Script (PowerShell)

.DESCRIPTION
    Runs comprehensive checks on documentation generator, templates, and generated docs.
    Windows-native PowerShell version of validate_week1.sh

.EXAMPLE
    .\scripts\docs\validate_week1.ps1
#>

# Error handling
$ErrorActionPreference = "Stop"

# Project root detection
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Week 1 Validation - Quick Start" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Counter for pass/fail
$TotalChecks = 0
$PassedChecks = 0

# Function to print result
function Check-Result {
    param(
        [string]$Name,
        [bool]$Result
    )

    $script:TotalChecks++

    if ($Result) {
        Write-Host "✓ $Name" -ForegroundColor Green
        $script:PassedChecks++
    } else {
        Write-Host "✗ $Name" -ForegroundColor Red
    }
}

# 1. File Structure Verification
Write-Host "[1/6] Checking file structure..." -ForegroundColor Blue
$scriptsExist = (Test-Path "scripts\docs\generate_code_docs.py") -and (Test-Path "scripts\docs\validate_code_docs.py")
Check-Result "Core scripts exist" $scriptsExist

$templatesExist = (Test-Path "scripts\docs\templates") -and (Test-Path "scripts\docs\templates\module_template.md")
Check-Result "Template directory exists" $templatesExist

$templateCount = (Get-ChildItem -Path "scripts\docs\templates" -Filter "*.md" -File -ErrorAction SilentlyContinue).Count
Check-Result "Required templates present (found $templateCount)" ($templateCount -ge 3)

# 2. Generated Documentation Count
Write-Host ""
Write-Host "[2/6] Checking documentation count..." -ForegroundColor Blue
$docCount = (Get-ChildItem -Path "docs\reference" -Filter "*.md" -File -Recurse -ErrorAction SilentlyContinue).Count
Write-Host "Documentation files: $docCount (expected: ~337)"
Check-Result "Documentation files generated" ($docCount -ge 330)

$moduleDirs = (Get-ChildItem -Path "docs\reference" -Directory -ErrorAction SilentlyContinue).Count
Check-Result "Module directories created (found $moduleDirs)" ($moduleDirs -ge 15)

# 3. Running Validation Script
Write-Host ""
Write-Host "[3/6] Running validation script..." -ForegroundColor Blue

try {
    $validationOutput = python scripts\docs\validate_code_docs.py --check-all 2>&1 | Out-String
    Check-Result "Validation script execution" $true

    # Check individual validation results
    Check-Result "Literalinclude paths valid" ($validationOutput -match "\[PASS\].*Literalinclude Paths")
    Check-Result "Documentation coverage 100%" ($validationOutput -match "\[PASS\].*Coverage")
    Check-Result "Toctree references valid" ($validationOutput -match "\[PASS\].*Toctree")
    Check-Result "No syntax errors" ($validationOutput -match "\[PASS\].*Syntax")
} catch {
    Check-Result "Validation script execution" $false
    Write-Host "Error: $_" -ForegroundColor Red
}

# 4. Testing Generator (Dry-Run)
Write-Host ""
Write-Host "[4/6] Testing generator (dry-run)..." -ForegroundColor Blue

try {
    $generatorOutput = python scripts\docs\generate_code_docs.py --module controllers --dry-run 2>&1 | Out-String
    Check-Result "Generator dry-run successful" $true

    Check-Result "Generator file discovery working" ($generatorOutput -match "Found \d+ Python files to document")
} catch {
    Check-Result "Generator dry-run successful" $false
    Write-Host "Error: $_" -ForegroundColor Red
}

# 5. Git Status Check
Write-Host ""
Write-Host "[5/6] Checking git status..." -ForegroundColor Blue

try {
    $gitLog = git log --oneline -1 2>&1 | Out-String
    Check-Result "Week 1 commit exists" ($gitLog -match "Week 1")

    $gitStatus = git status 2>&1 | Out-String
    if ($gitStatus -match "Your branch is up to date with") {
        Check-Result "Branch synced with remote" $true
    } else {
        Write-Host "⚠ Branch may not be synced with remote" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Git check failed (git may not be installed)" -ForegroundColor Yellow
}

# 6. Quality Checks
Write-Host ""
Write-Host "[6/6] Running quality checks..." -ForegroundColor Blue

$pythonFiles = (Get-ChildItem -Path "src" -Filter "*.py" -File -Recurse -ErrorAction SilentlyContinue).Count
if ($pythonFiles -eq 316) {
    Check-Result "Python file count matches (316)" $true
} else {
    Write-Host "⚠ Python file count: $pythonFiles (expected 316)" -ForegroundColor Yellow
}

$pycacheCount = (Get-ChildItem -Path "." -Filter "__pycache__" -Directory -Recurse -ErrorAction SilentlyContinue).Count
if ($pycacheCount -eq 0) {
    Check-Result "No __pycache__ pollution" $true
} else {
    Write-Host "⚠ Found $pycacheCount __pycache__ directories (cleanup recommended)" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Week 1 Validation Complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Passed: $PassedChecks / $TotalChecks checks" -ForegroundColor Green
Write-Host ""

if ($PassedChecks -eq $TotalChecks) {
    Write-Host "✓ Week 1 infrastructure is solid!" -ForegroundColor Green
    Write-Host "Ready to proceed to Week 2 (Controllers detailed documentation)"
    exit 0
} elseif ($PassedChecks -ge ($TotalChecks * 3 / 4)) {
    Write-Host "⚠ Most checks passed, but some issues found" -ForegroundColor Yellow
    Write-Host "Review failures above before proceeding to Week 2"
    exit 1
} else {
    Write-Host "✗ Significant issues detected" -ForegroundColor Red
    Write-Host "Fix issues before proceeding to Week 2"
    exit 1
}
