# Compile EP001 LaTeX to PDF using MiKTeX
$TARGET_FILE = "EP001_unified.tex"
$PDFLATEX = "C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe"

Set-Location -LiteralPath $PSScriptRoot

Write-Host "Compiling $TARGET_FILE with MiKTeX..." -ForegroundColor Cyan

for ($i = 0; $i -lt 4; $i++) {
    $pass = if ($i -eq 0) { "Main" } else { "Pass $i" }
    Write-Host "[$pass] Running pdflatex..." -ForegroundColor Gray
    
    & $PDFLATEX -interaction=nonstopmode $TARGET_FILE 2>&1 | Select-Object -Last 3
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [$pass] ✓ Success" -ForegroundColor Green
    } else {
        Write-Host "  [$pass] ⚠ Warning" -ForegroundColor Yellow
    }
}

if (Test-Path "$TARGET_FILE.pdf") {
    $size = (Get-Item "$TARGET_FILE.pdf").Length / 1KB
    Write-Host ""
    Write-Host "[OK] PDF created: EP001_unified.pdf" -ForegroundColor Green
    Write-Host "   Size: $([math]::Round($size, 1)) KB" -ForegroundColor Gray
    Write-Host "   Location: $(Get-Location)" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "[ERROR] PDF not created." -ForegroundColor Red
}
