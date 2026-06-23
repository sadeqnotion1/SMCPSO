#!/usr/bin/env python3
"""
Compile EP001 LaTeX to PDF using WSL pdflatex (Linux LaTeX installation).

This script uses pdflatex available in the WSL environment.
"""

import subprocess
import sys
import os
from pathlib import Path


# Configuration
TARGET_DIR = Path(__file__).parent.resolve()
TARGET_FILE = TARGET_DIR / "EP001_unified.tex"


def compile_latex(tex_file: Path, output_dir: Path = None):
    """
    Compile LaTeX file to PDF using WSL pdflatex.
    
    Args:
        tex_file: Path to .tex file
        output_dir: Output directory for PDF (optional)
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"Input file: {tex_file}")
    
    # Check if tex file exists
    if not tex_file.exists():
        print(f"[ERROR] LaTeX file not found: {tex_file}")
        return False
    
    # Check for available LaTeX compilers
    latex_compilers = ['pdflatex', 'latexmk']
    compiler = None
    
    for comp in latex_compilers:
        try:
            result = subprocess.run(
                [comp, '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                compiler = comp
                print(f"[OK] Found compiler: {comp}")
                break
        except FileNotFoundError:
            continue
    
    if not compiler:
        print("[ERROR] No LaTeX compiler found (pdflatex or latexmk)")
        print("Please install texlive-latex-base or texlive-full:")
        print("  sudo apt-get install texlive-latex-base")
        print("  or")
        print("  sudo apt-get install texlive-full")
        return False
    
    # Run pdflatex (4 passes for references)
    print(f"\n=== Compiling PDF with {compiler} (4 passes) ===\n")
    
    for i in range(4):
        pass_name = "Main" if i == 0 else f"Pass {i}"
        print(f"[{pass_name}] Running {compiler}...")
        
        try:
            # For pdflatex, run directly; for latexmk, use -pdf flag
            if compiler == 'latexmk':
                cmd = [compiler, '-pdf', '-interaction=nonstopmode', str(tex_file)]
            else:
                cmd = [compiler, '-interaction=nonstopmode', str(tex_file)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(tex_file.parent)
            )
            
            if result.returncode == 0:
                print(f"  [{pass_name}] ✓ Success")
            else:
                print(f"  [{pass_name}] ⚠ Warning (return code: {result.returncode})")
                # Print last 5 lines of stderr for debugging
                lines = result.stderr.strip().split('\n')[-5:]
                for line in lines:
                    if line and 'Error' in line or 'Package' in line or 'File' in line:
                        print(f"    {line}")
        
        except Exception as e:
            print(f"  [ERROR] {e}")
            return False
    
    # Check for bibliography (optional)
    aux_file = tex_file.with_suffix('.aux')
    if aux_file.exists():
        if 'cite' in open(tex_file).read() and compiler == 'pdflatex':
            print("\n[INFO] Checking for bibliography...")
            try:
                subprocess.run(
                    ['bibtex', str(tex_file.with_suffix(''))],
                    capture_output=True,
                    cwd=str(tex_file.parent),
                    check=True
                )
                print("  [bibtex] ✓ Bibliography processed")
            except Exception as e:
                print(f"  [bibtex] Warning: {e}")
    
    # Run pdflatex one more time after bibtex if needed
    if aux_file.exists() and 'cite' in open(tex_file).read():
        print("\n[INFO] Final pass after bibliography...")
        subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', str(tex_file)],
            capture_output=True,
            cwd=str(tex_file.parent)
        )
    
    # Check if PDF was created
    pdf_file = tex_file.with_suffix('.pdf')
    if pdf_file.exists():
        print(f"\n✅ SUCCESS! PDF created: {pdf_file}")
        print(f"   Location: {pdf_file.resolve()}")
        print(f"   Size: {pdf_file.stat().st_size / 1024:.1f} KB")
        return True
    else:
        print(f"\n❌ FAILED! PDF not created.")
        return False


def main():
    """Main entry point."""
    print("=" * 60)
    print("EP001 LaTeX to PDF Compiler (WSL)")
    print("=" * 60)
    print()
    
    success = compile_latex(TARGET_FILE, TARGET_DIR)
    
    print()
    print("=" * 60)
    if success:
        print("✅ Compilation complete!")
        print(f"   Open in Windows Explorer: {TARGET_DIR}")
    else:
        print("❌ Compilation failed!")
        print("   Please check the error messages above.")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
