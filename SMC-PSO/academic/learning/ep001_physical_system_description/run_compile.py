#!/usr/bin/env python3
import subprocess
import sys
import os

def windows_to_wsl_path(windows_path):
    """Convert Windows path to WSL path."""
    result = subprocess.run(
        ['wslpath', '-u', windows_path],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return windows_path

# Windows paths (as Python strings, not shell)
windows_pdflatex = r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe"
windows_tex = r"D:\Projects\main\academic\learning\ep001_physical_system_description\EP001_unified.tex"

# Convert to WSL format
wsl_pdflatex = windows_to_wsl_path(windows_pdflatex)
wsl_tex = windows_to_wsl_path(windows_tex)

print(f"Windows pdflatex: {windows_pdflatex}")
print(f"WSL pdflatex: {wsl_pdflatex}")
print(f"Input file: {wsl_tex}")

if not os.path.exists(wsl_tex):
    print(f"[ERROR] File not found: {wsl_tex}")
    sys.exit(1)

print("\n=== Compiling (4 passes) ===\n")

for i in range(4):
    print(f"Pass {i+1}/4...")
    result = subprocess.run(
        [wsl_pdflatex, "-interaction=nonstopmode", wsl_tex],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("  ✓ Success")
    else:
        lines = result.stderr.split('\n')[-5:]
        for line in lines:
            if line.strip():
                print(f"  {line.strip()}")

# Check for PDF
pdf_path = wsl_tex.replace('.tex', '.pdf')
if os.path.exists(pdf_path):
    size = os.path.getsize(pdf_path) / 1024
    print(f"\n✅ SUCCESS!")
    print(f"   PDF: {pdf_path}")
    print(f"   Size: {size:.1f} KB")
else:
    print(f"\n❌ FAILED - PDF not created")
