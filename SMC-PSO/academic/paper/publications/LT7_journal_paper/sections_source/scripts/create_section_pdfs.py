"""
Create individual section PDFs from LT7_PROFESSIONAL_FINAL.tex
Each section is extracted to a standalone .tex file and compiled to PDF.
"""

import subprocess
import os

# Section boundaries from the LaTeX file (line numbers)
sections = [
    {
        "num": "00",
        "name": "Front_Matter",
        "title": "Front Matter & Abstract",
        "start": 1,
        "end": 27
    },
    {
        "num": "01",
        "name": "Introduction",
        "title": "Section 1: Introduction",
        "start": 28,
        "end": 172
    },
    {
        "num": "02",
        "name": "List_of_Figures",
        "title": "List of Figures",
        "start": 173,
        "end": 212
    },
    {
        "num": "03",
        "name": "System_Model",
        "title": "Section 2: System Model and Problem Formulation",
        "start": 213,
        "end": 453
    },
    {
        "num": "04",
        "name": "Controller_Design",
        "title": "Section 3: Controller Design",
        "start": 454,
        "end": 1210
    },
    {
        "num": "05",
        "name": "Lyapunov_Stability",
        "title": "Section 4: Lyapunov Stability Analysis",
        "start": 1211,
        "end": 1831
    },
    {
        "num": "06",
        "name": "PSO_Methodology",
        "title": "Section 5: PSO Optimization Methodology",
        "start": 1832,
        "end": 2353
    },
    {
        "num": "07",
        "name": "Experimental_Setup",
        "title": "Section 6: Experimental Setup and Benchmarking Protocol",
        "start": 2354,
        "end": 3065
    },
    {
        "num": "08",
        "name": "Performance_Results",
        "title": "Section 7: Performance Comparison Results",
        "start": 3066,
        "end": 3723
    },
    {
        "num": "09",
        "name": "Robustness_Analysis",
        "title": "Section 8: Robustness Analysis",
        "start": 3724,
        "end": 4673
    },
    {
        "num": "10",
        "name": "Discussion",
        "title": "Section 9: Discussion",
        "start": 4674,
        "end": 5102
    },
    {
        "num": "11",
        "name": "Conclusion",
        "title": "Section 10: Conclusion and Future Work",
        "start": 5103,
        "end": 5272
    },
    {
        "num": "12",
        "name": "Acknowledgments",
        "title": "Acknowledgments",
        "start": 5273,
        "end": 5289
    }
]

# LaTeX preamble template (lines 1-18 from original file)
preamble = r"""\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage[margin=1in]{geometry}

"""

postamble = r"""
\end{document}
"""

# Read the main LaTeX file
source_file = "../LT7_PROFESSIONAL_FINAL.tex"
print(f"[INFO] Reading {source_file}")
with open(source_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"[INFO] Total lines in source: {len(lines)}")
print(f"[INFO] Extracting {len(sections)} sections")
print()

# Process each section
for section in sections:
    tex_filename = f"Section_{section['num']}_{section['name']}.tex"
    pdf_filename = f"Section_{section['num']}_{section['name']}.pdf"

    # Extract section content
    section_lines = lines[section['start']-1:section['end']]

    # Build LaTeX document
    if section['num'] == '00':
        # Front matter already has document structure
        content = section_lines
    else:
        # Create standalone document
        title_escaped = section['title'].replace(':', r'\textcolon')
        content = (
            preamble +
            f"\\title{{{title_escaped}}}\n" +
            f"\\date{{December 25, 2025}}\n\n" +
            "\\begin{document}\n" +
            "\\maketitle\n\n" +
            ''.join(section_lines) +
            postamble
        )

    # Write .tex file
    with open(tex_filename, 'w', encoding='utf-8') as f:
        if isinstance(content, list):
            f.writelines(content)
        else:
            f.write(content)

    line_count = len(section_lines)
    print(f"[OK] Created {tex_filename} ({line_count} lines)")

    # Compile to PDF using pdflatex
    print(f"[INFO] Compiling {tex_filename} to PDF...")
    try:
        # Run pdflatex (suppress output)
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', tex_filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )

        if result.returncode == 0 and os.path.exists(pdf_filename):
            # Get PDF file size
            pdf_size = os.path.getsize(pdf_filename) / 1024  # KB
            print(f"[OK] Created {pdf_filename} ({pdf_size:.1f} KB)")

            # Clean up LaTeX auxiliary files
            aux_extensions = ['.aux', '.log', '.out', '.toc']
            for ext in aux_extensions:
                aux_file = tex_filename.replace('.tex', ext)
                if os.path.exists(aux_file):
                    os.remove(aux_file)
        else:
            print(f"[ERROR] PDF compilation failed for {tex_filename}")
            print(f"[ERROR] Return code: {result.returncode}")

    except FileNotFoundError:
        print(f"[ERROR] pdflatex not found. Please install TeX Live or MiKTeX.")
        print(f"[INFO] LaTeX file created: {tex_filename}")
        print(f"[INFO] Compile manually: pdflatex {tex_filename}")
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Compilation timeout for {tex_filename}")
    except Exception as e:
        print(f"[ERROR] Compilation error: {e}")

    print()

print("[OK] Section extraction complete!")
print(f"[INFO] Output directory: sections/")
