#!/usr/bin/env python
"""
Build Individual Chapter PDFs

This script generates standalone PDFs for each chapter and appendix by creating
temporary wrapper .tex files that include the preamble and individual content.

Usage:
    python build_individual_chapters.py [--chapters-only] [--appendices-only]

Output:
    build/individual_chapters/chapter_01.pdf
    build/individual_chapters/chapter_02.pdf
    ...
    build/individual_chapters/appendix_a.pdf
    ...
"""

import os
import subprocess
import sys
from pathlib import Path

# Configuration
TEXTBOOK_ROOT = Path(__file__).parent
SOURCE_DIR = TEXTBOOK_ROOT / "source"
BUILD_DIR = TEXTBOOK_ROOT / "build" / "individual_chapters"
PREAMBLE_FILE = TEXTBOOK_ROOT / "source" / "preamble.tex"

# Chapter and appendix mapping (with chapter numbers)
CHAPTERS = {
    "chapter_01": ("chapters/ch01_introduction.tex", 1),
    "chapter_02": ("chapters/ch02_mathematical_foundations.tex", 2),
    "chapter_03": ("chapters/ch03_classical_smc.tex", 3),
    "chapter_04": ("chapters/ch04_super_twisting.tex", 4),
    "chapter_05": ("chapters/ch05_adaptive_smc.tex", 5),
    "chapter_06": ("chapters/ch06_hybrid_smc.tex", 6),
    "chapter_07": ("chapters/ch07_pso_theory.tex", 7),
    "chapter_08": ("chapters/ch08_benchmarking.tex", 8),
    "chapter_09": ("chapters/ch09_pso_results.tex", 9),
    "chapter_10": ("chapters/ch10_advanced_topics.tex", 10),
    "chapter_11": ("chapters/ch11_software.tex", 11),
    "chapter_12": ("chapters/ch12_case_studies.tex", 12),
}

APPENDICES = {
    "appendix_a": "appendices/appendix_a_math.tex",
    "appendix_b": "appendices/appendix_b_lyapunov_proofs.tex",
    "appendix_c": "appendices/appendix_c_api.tex",
    "appendix_d": "appendices/appendix_d_solutions.tex",
}

# LaTeX template for standalone chapter
STANDALONE_TEMPLATE = r"""\documentclass[11pt,oneside]{{book}}

% Include standalone preamble (without hyperref to avoid counter bugs)
\input{{../../preamble_standalone.tex}}

\begin{{document}}

% Title page for standalone chapter
\begin{{titlepage}}
\centering
\vspace*{{2cm}}
{{\Huge\bfseries {title} \par}}
\vspace{{1cm}}
{{\Large Sliding Mode Control and PSO Optimization \par}}
{{\Large for Double-Inverted Pendulum Systems \par}}
\vfill
{{\large Standalone Chapter \par}}
\end{{titlepage}}

% Table of contents for this chapter
\tableofcontents
\clearpage

% Set chapter/appendix counter
{counter_setup}

% FIX: Redefine counter display to work around hyperref bug
{counter_fix}

% Include the chapter content
\input{{../../source/{content_path}}}

\end{{document}}
"""

def create_build_directory():
    """Create build directory for individual chapters."""
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Build directory: {BUILD_DIR}")

def generate_wrapper_tex(output_name, content_path, title, chapter_number=None, is_appendix=False):
    """Generate a standalone .tex wrapper file for a chapter/appendix."""
    # Determine counter setup
    # NOTE: hyperref is in draft mode for standalone chapters to avoid counter bugs
    if is_appendix:
        counter_setup = r"\appendix"
        counter_fix = ""
    elif chapter_number is not None:
        # Set to N-1 since \chapter will increment
        counter_setup = f"\\setcounter{{chapter}}{{{chapter_number - 1}}}"
        counter_fix = ""
    else:
        counter_setup = ""
        counter_fix = ""

    wrapper_content = STANDALONE_TEMPLATE.format(
        title=title,
        content_path=content_path,
        counter_setup=counter_setup,
        counter_fix=counter_fix
    )

    wrapper_file = BUILD_DIR / f"{output_name}.tex"
    wrapper_file.write_text(wrapper_content, encoding='utf-8')
    print(f"[OK] Generated wrapper: {wrapper_file.name}")
    return wrapper_file

def compile_pdf(tex_file):
    """Compile a .tex file to PDF using pdflatex."""
    print(f"[INFO] Compiling {tex_file.name}...")

    # Run pdflatex twice for cross-references
    # NOTE: Ignore return code - MiKTeX warnings cause non-zero exit even on success
    for run in [1, 2]:
        result = subprocess.run(
            ["pdflatex", "-shell-escape", "-interaction=nonstopmode", tex_file.name],
            cwd=BUILD_DIR,
            capture_output=True,
            text=True
        )

    # Check if PDF was created (this is the real success indicator)
    pdf_file = BUILD_DIR / tex_file.with_suffix('.pdf').name
    if pdf_file.exists():
        pdf_size = pdf_file.stat().st_size / 1024  # KB
        print(f"[OK] Created {pdf_file.name} ({pdf_size:.1f} KB)")
        return True
    else:
        print(f"[ERROR] PDF not created: {pdf_file.name}")
        # Print last stderr for debugging
        if result.stderr:
            print(f"  Last error: {result.stderr[:300]}")
        return False

def cleanup_aux_files(base_name):
    """Remove auxiliary LaTeX files after compilation."""
    extensions = ['.aux', '.log', '.out', '.toc', '.lof', '.lot']
    for ext in extensions:
        aux_file = BUILD_DIR / f"{base_name}{ext}"
        if aux_file.exists():
            aux_file.unlink()

def build_chapters(chapters_dict, prefix="Chapter", is_appendix=False):
    """Build individual PDFs for a dictionary of chapters/appendices."""
    success_count = 0
    total_count = len(chapters_dict)

    for output_name, content_data in chapters_dict.items():
        # Handle tuple format (path, number) for chapters or string for appendices
        if isinstance(content_data, tuple):
            content_path, chapter_number = content_data
        else:
            content_path = content_data
            chapter_number = None

        # Generate title from output name
        if "chapter" in output_name:
            chapter_num = output_name.split("_")[1]
            title = f"Chapter {chapter_num}"
        else:
            appendix_letter = output_name.split("_")[1].upper()
            title = f"Appendix {appendix_letter}"

        # Generate wrapper .tex file
        wrapper_file = generate_wrapper_tex(
            output_name, content_path, title,
            chapter_number=chapter_number,
            is_appendix=is_appendix
        )

        # Compile to PDF
        if compile_pdf(wrapper_file):
            success_count += 1

        # Cleanup auxiliary files
        cleanup_aux_files(output_name)

    print(f"\n[SUMMARY] {prefix}: {success_count}/{total_count} PDFs created successfully")
    return success_count

def main():
    """Main build function."""
    import argparse

    parser = argparse.ArgumentParser(description="Build individual chapter PDFs")
    parser.add_argument("--chapters-only", action="store_true", help="Build only chapters")
    parser.add_argument("--appendices-only", action="store_true", help="Build only appendices")
    args = parser.parse_args()

    print("=" * 70)
    print("BUILDING INDIVIDUAL CHAPTER PDFs")
    print("=" * 70)

    # Create build directory
    create_build_directory()

    total_success = 0

    # Build chapters
    if not args.appendices_only:
        print("\n[PHASE 1] Building Chapters (1-12)...")
        total_success += build_chapters(CHAPTERS, "Chapters")

    # Build appendices
    if not args.chapters_only:
        print("\n[PHASE 2] Building Appendices (A-D)...")
        total_success += build_chapters(APPENDICES, "Appendices", is_appendix=True)

    # Final summary
    total_files = len(CHAPTERS) + len(APPENDICES)
    if not args.chapters_only and not args.appendices_only:
        print("\n" + "=" * 70)
        print(f"[FINAL] {total_success}/{total_files} total PDFs created successfully")
        print(f"[LOCATION] {BUILD_DIR}")
        print("=" * 70)

    return 0 if total_success > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
