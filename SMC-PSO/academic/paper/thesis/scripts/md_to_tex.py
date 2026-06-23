#!/usr/bin/env python
"""
Markdown to LaTeX Converter for Thesis Writing

Converts markdown files from docs/thesis/ to LaTeX format.
Handles headers, emphasis, code blocks, math, lists, and citations.

Usage:
    python md_to_tex.py input.md output.tex

Example:
    python md_to_tex.py docs/thesis/chapters/04_sliding_mode_control.md \
                        thesis/chapters/chapter05_smc_theory.tex

Saves ~15 hours of manual conversion work!
"""

import re
import sys
import argparse
from pathlib import Path

def convert_headers(content):
    """Convert markdown headers to LaTeX sections."""
    # # Header -> \chapter{}
    content = re.sub(r'^# (.+)$', r'\\chapter{\1}', content, flags=re.MULTILINE)
    # ## Header -> \section{}
    content = re.sub(r'^## (.+)$', r'\\section{\1}', content, flags=re.MULTILINE)
    # ### Header -> \subsection{}
    content = re.sub(r'^### (.+)$', r'\\subsection{\1}', content, flags=re.MULTILINE)
    # #### Header -> \subsubsection{}
    content = re.sub(r'^#### (.+)$', r'\\subsubsection{\1}', content, flags=re.MULTILINE)
    return content

def convert_emphasis(content):
    """Convert markdown emphasis to LaTeX."""
    # **bold** -> \textbf{bold}
    content = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', content)
    # *italic* -> \textit{italic}
    content = re.sub(r'\*(.+?)\*', r'\\textit{\1}', content)
    # `code` -> \texttt{code}
    content = re.sub(r'`([^`]+)`', r'\\texttt{\1}', content)
    return content

def convert_math(content):
    """Convert markdown math blocks to LaTeX."""
    # $$...$$ -> \begin{equation}...\end{equation}
    content = re.sub(
        r'\$\$\s*(.+?)\s*\$\$',
        r'\\begin{equation}\n\1\n\\end{equation}',
        content,
        flags=re.DOTALL
    )
    # Inline math $...$ stays the same
    return content

def convert_code_blocks(content):
    """Convert markdown code blocks to LaTeX listings."""
    # ```python ... ``` -> \begin{lstlisting}[language=Python]...\end{lstlisting}
    def replace_code_block(match):
        language = match.group(1) if match.group(1) else ''
        code = match.group(2)
        if language:
            lang_map = {
                'python': 'Python',
                'bash': 'bash',
                'latex': 'TeX',
                'yaml': 'yaml'
            }
            lang = lang_map.get(language.lower(), language)
            return f'\\begin{{lstlisting}}[language={lang}]\n{code}\n\\end{{lstlisting}}'
        else:
            return f'\\begin{{verbatim}}\n{code}\n\\end{{verbatim}}'

    content = re.sub(
        r'```(\w+)?\s*\n(.+?)\n```',
        replace_code_block,
        content,
        flags=re.DOTALL
    )
    return content

def convert_lists(content):
    """Convert markdown lists to LaTeX itemize/enumerate."""
    lines = content.split('\n')
    result = []
    in_list = False

    for line in lines:
        # Unordered list: - item
        if re.match(r'^- (.+)$', line):
            if not in_list:
                result.append('\\begin{itemize}')
                in_list = True
            item = re.sub(r'^- (.+)$', r'\\item \1', line)
            result.append(item)
        # Ordered list: 1. item
        elif re.match(r'^\d+\. (.+)$', line):
            if not in_list:
                result.append('\\begin{enumerate}')
                in_list = 'enum'
            item = re.sub(r'^\d+\. (.+)$', r'\\item \1', line)
            result.append(item)
        else:
            if in_list:
                if in_list == 'enum':
                    result.append('\\end{enumerate}')
                else:
                    result.append('\\end{itemize}')
                in_list = False
            result.append(line)

    if in_list:
        if in_list == 'enum':
            result.append('\\end{enumerate}')
        else:
            result.append('\\end{itemize}')

    return '\n'.join(result)

def convert_citations(content):
    """Convert markdown citations [Ref] to LaTeX \cite{Ref}."""
    # [Utkin1977] -> \cite{Utkin1977}
    content = re.sub(r'\[([A-Z]\w+\d{4})\]', r'\\cite{\1}', content)
    return content

def add_labels(content):
    """Add LaTeX labels to sections for cross-referencing."""
    def add_label_to_section(match):
        section_type = match.group(1)
        title = match.group(2)
        # Create label from title (lowercase, replace spaces with hyphens)
        label = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        return f'\\{section_type}{{{title}}}\n\\label{{{section_type}:{label}}}'

    content = re.sub(
        r'\\(section|subsection|subsubsection)\{(.+?)\}',
        add_label_to_section,
        content
    )
    return content

def clean_special_chars(content):
    """Escape LaTeX special characters."""
    # Don't escape in math mode or commands
    # This is a simplified version - may need refinement
    replacements = {
        '%': '\\%',
        '&': '\\&',
        '#': '\\#',
    }
    for char, escaped in replacements.items():
        # Only replace if not already escaped
        content = re.sub(f'(?<!\\\\){re.escape(char)}', escaped, content)
    return content

def markdown_to_latex(md_content):
    """
    Main conversion function.

    Args:
        md_content (str): Markdown content

    Returns:
        str: LaTeX content
    """
    content = md_content

    # Apply conversions in order
    content = convert_code_blocks(content)  # First, to protect code from other conversions
    content = convert_math(content)         # Second, to protect math
    content = convert_headers(content)
    content = convert_emphasis(content)
    content = convert_lists(content)
    content = convert_citations(content)
    content = add_labels(content)
    content = clean_special_chars(content)

    return content

def main():
    parser = argparse.ArgumentParser(
        description='Convert markdown to LaTeX for thesis writing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python md_to_tex.py docs/thesis/chapters/04_sliding_mode_control.md \
                      thesis/chapters/chapter05_smc_theory.tex

  python md_to_tex.py --help
        """
    )
    parser.add_argument('input', help='Input markdown file')
    parser.add_argument('output', help='Output LaTeX file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Print output instead of writing to file')

    args = parser.parse_args()

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {args.input}")
        sys.exit(1)

    print(f"[INFO] Reading: {args.input}")
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert
    print(f"[INFO] Converting markdown to LaTeX...")
    latex_content = markdown_to_latex(md_content)

    # Write output or print
    if args.dry_run:
        print("\n" + "="*80)
        print("CONVERTED OUTPUT:")
        print("="*80)
        print(latex_content)
    else:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)

        print(f"[OK] Written to: {args.output}")
        print(f"[INFO] Converted {len(md_content)} chars -> {len(latex_content)} chars")

        # Count conversions
        sections = len(re.findall(r'\\section\{', latex_content))
        subsections = len(re.findall(r'\\subsection\{', latex_content))
        citations = len(re.findall(r'\\cite\{', latex_content))

        print(f"[INFO] Found: {sections} sections, {subsections} subsections, {citations} citations")

if __name__ == '__main__':
    main()
