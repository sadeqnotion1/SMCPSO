"""LT-7 Markdown to LaTeX Converter (80% Automated)

Converts LT7_RESEARCH_PAPER.md to LaTeX format for IJC submission.
Automates common conversions; requires manual polish (equation numbering, table formatting).

Usage:
    python scripts/lt7_markdown_to_latex.py

Output:
    benchmarks/LT7_RESEARCH_PAPER.tex (LaTeX source)
    benchmarks/LT7_RESEARCH_PAPER.bib (Bibliography)
"""

import re
from pathlib import Path

INPUT_PATH = Path(".artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md")
OUTPUT_TEX = Path(".artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.tex")
OUTPUT_BIB = Path(".artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.bib")

PREAMBLE = r"""\documentclass[11pt,twocolumn]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{cite}

\title{Comparative Analysis of Sliding Mode Control Variants for Double-Inverted Pendulum Systems: Performance, Stability, and Robustness}

\author{
[AUTHOR_NAMES_PLACEHOLDER] \\
[AFFILIATION_PLACEHOLDER] \\
\texttt{[EMAIL_PLACEHOLDER]}
}

\date{\today}

\begin{document}

\maketitle

"""

POSTAMBLE = r"""
\bibliography{LT7_RESEARCH_PAPER}
\bibliographystyle{IEEEtran}

\end{document}
"""

def convert_headers(line: str) -> str:
    """Convert markdown headers to LaTeX sections."""
    if line.startswith("## "):
        return "\\section{" + line[3:].strip() + "}\n"
    elif line.startswith("### "):
        return "\\subsection{" + line[4:].strip() + "}\n"
    elif line.startswith("#### "):
        return "\\subsubsection{" + line[5:].strip() + "}\n"
    return line

def convert_emphasis(text: str) -> str:
    """Convert bold/italic to LaTeX."""
    # Bold (**text** or __text__)
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'__(.+?)__', r'\\textbf{\1}', text)

    # Italic (*text* or _text_)
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)
    text = re.sub(r'_(.+?)_', r'\\textit{\1}', text)

    return text

def convert_math(text: str) -> str:
    """Convert inline and block math."""
    # Block math $$...$$ -> equation environment
    text = re.sub(r'\$\$(.+?)\$\$', r'\\begin{equation}\n\1\n\\end{equation}', text, flags=re.DOTALL)

    # Inline math $...$ stays the same
    return text

def convert_citations(text: str) -> str:
    """Convert [1] to \cite{ref1}, [1,2,3] to \cite{ref1,ref2,ref3}."""
    def replace_citation(match):
        cites = match.group(1)
        # Handle ranges like "1-5"
        if '-' in cites:
            parts = cites.split('-')
            if len(parts) == 2 and all(p.strip().isdigit() for p in parts):
                start, end = map(int, [p.strip() for p in parts])
                cite_list = [f"ref{i}" for i in range(start, end + 1)]
                return f"\\cite{{{','.join(cite_list)}}}"
        # Handle comma-separated like "1,2,3"
        elif ',' in cites:
            nums = [n.strip() for n in cites.split(',')]
            cite_list = [f"ref{n}" for n in nums if n.isdigit()]
            return f"\\cite{{{','.join(cite_list)}}}"
        # Single citation [1]
        else:
            return f"\\cite{{ref{cites}}}"

    text = re.sub(r'\[(\d+(?:,\d+|-\d+|,\s*\d+)*)\]', replace_citation, text)
    return text

def convert_figures(text: str) -> str:
    """Convert ![Figure X.Y: Caption](path) to LaTeX figure environment."""
    pattern = r'!\[Figure\s+(.+?):\s+(.+?)\]\((.+?)\)'

    def replace_figure(match):
        fig_num, caption, path = match.groups()
        # Extract filename from path
        filename = Path(path).name
        return (
            f"\\begin{{figure}}[htbp]\n"
            f"  \\centering\n"
            f"  \\includegraphics[width=0.9\\columnwidth]{{figures/{filename}}}\n"
            f"  \\caption{{{caption}}}\n"
            f"  \\label{{fig:{fig_num.replace('.', '_')}}}\n"
            f"\\end{{figure}}\n"
        )

    return re.sub(pattern, replace_figure, text)

def extract_references(lines: list) -> tuple:
    """Extract references section and return (body_lines, bib_entries)."""
    ref_start = None
    for i, line in enumerate(lines):
        if "## References" in line:
            ref_start = i
            break

    if ref_start is None:
        return lines, []

    body = lines[:ref_start]
    refs = lines[ref_start+2:]  # Skip "## References" and blank line

    # Parse references [1] Author, "Title", Journal, Year
    bib_entries = []
    for line in refs:
        match = re.match(r'^\[(\d+)\]\s+(.+)', line.strip())
        if match:
            num, ref_text = match.groups()
            # Create BibTeX entry (simplified - requires manual completion)
            bib_entry = (
                f"@article{{ref{num},\n"
                f"  title={{{ref_text[:80]}...}},\n"
                f"  note={{[COMPLETE MANUALLY FROM LINE: {ref_text[:50]}...]}}\n"
                f"}}\n"
            )
            bib_entries.append(bib_entry)

    return body, bib_entries

def convert_markdown_to_latex():
    """Main conversion function."""
    print("[INFO] Loading markdown...")
    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("[INFO] Extracting references...")
    body_lines, bib_entries = extract_references(lines)

    print("[INFO] Converting content...")
    latex_lines = [PREAMBLE]

    skip_until_abstract = True
    for line in body_lines:
        # Skip front matter until Abstract
        if skip_until_abstract:
            if "## Abstract" in line:
                skip_until_abstract = False
                latex_lines.append("\\begin{abstract}\n")
                continue
            continue

        # End abstract
        if "## Abstract" in line and not skip_until_abstract:
            latex_lines.append("\\end{abstract}\n\n")
            continue

        # Convert headers
        line = convert_headers(line)

        # Convert emphasis
        line = convert_emphasis(line)

        # Convert math
        line = convert_math(line)

        # Convert citations
        line = convert_citations(line)

        # Convert figures
        line = convert_figures(line)

        # Skip markdown artifacts
        if line.strip() in ["---", "**Keywords:**"]:
            continue

        latex_lines.append(line)

    latex_lines.append(POSTAMBLE)

    print("[INFO] Writing LaTeX file...")
    with open(OUTPUT_TEX, 'w', encoding='utf-8') as f:
        f.writelines(latex_lines)

    print("[INFO] Writing bibliography file...")
    with open(OUTPUT_BIB, 'w', encoding='utf-8') as f:
        f.write("% LT-7 Bibliography (AUTO-GENERATED - REQUIRES MANUAL COMPLETION)\n")
        f.write("% TODO: Complete all @article entries with full citation info\n\n")
        f.writelines(bib_entries)

    print(f"\n[OK] LaTeX conversion complete!")
    print(f"     Output: {OUTPUT_TEX}")
    print(f"     Bibliography: {OUTPUT_BIB}")
    print(f"\n[WARNING] Manual tasks required:")
    print(f"     1. Complete bibliography entries in {OUTPUT_BIB}")
    print(f"     2. Add equation numbering and labels")
    print(f"     3. Format tables (convert markdown tables to tabular)")
    print(f"     4. Adjust figure placements (htbp flags)")
    print(f"     5. Replace [AUTHOR_NAMES_PLACEHOLDER] in preamble")
    print(f"     6. Check for special characters needing escaping")

def main():
    print("\n" + "="*70)
    print("LT-7 MARKDOWN TO LATEX CONVERTER")
    print("="*70 + "\n")

    convert_markdown_to_latex()

    print("\n[INFO] Next steps:")
    print("     1. Review {OUTPUT_TEX} for conversion accuracy")
    print("     2. Compile with: pdflatex LT7_RESEARCH_PAPER.tex")
    print("     3. Run bibtex: bibtex LT7_RESEARCH_PAPER")
    print("     4. Recompile twice: pdflatex (2x)")
    print()

if __name__ == "__main__":
    main()
