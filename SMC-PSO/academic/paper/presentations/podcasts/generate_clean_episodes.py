#!/usr/bin/env python
"""
Generate clean learning episodes from presentation sections.
Creates both markdown (for reading) and LaTeX/PDF (for NotebookLM).
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List

# Episode mapping
EPISODES = {
    "E001": {"section": "01_project_overview.tex", "part": "part1_foundations", "title": "Project Overview and Introduction"},
    "E002": {"section": "02_control_theory.tex", "part": "part1_foundations", "title": "Control Theory Fundamentals"},
    "E003": {"section": "03_plant_models.tex", "part": "part1_foundations", "title": "Plant Models and Dynamics"},
    "E004": {"section": "04_optimization_pso.tex", "part": "part1_foundations", "title": "PSO Optimization Fundamentals"},
    "E005": {"section": "05_simulation_engine.tex", "part": "part1_foundations", "title": "Simulation Engine Architecture"},
    "E006": {"section": "06_analysis_visualization.tex", "part": "part2_infrastructure", "title": "Analysis and Visualization Tools"},
    "E007": {"section": "07_testing_qa.tex", "part": "part2_infrastructure", "title": "Testing and Quality Assurance"},
    "E008": {"section": "08_research_outputs.tex", "part": "part2_infrastructure", "title": "Research Outputs and Publications"},
    "E009": {"section": "09_educational_materials.tex", "part": "part2_infrastructure", "title": "Educational Materials and Learning Paths"},
    "E010": {"section": "10_documentation_system.tex", "part": "part2_infrastructure", "title": "Documentation System and Navigation"},
    "E011": {"section": "11_configuration_deployment.tex", "part": "part2_infrastructure", "title": "Configuration and Deployment"},
    "E012": {"section": "12_hil_system.tex", "part": "part3_advanced", "title": "Hardware-in-the-Loop System"},
    "E013": {"section": "13_monitoring_infrastructure.tex", "part": "part3_advanced", "title": "Monitoring Infrastructure"},
    "E014": {"section": "14_development_infrastructure.tex", "part": "part3_advanced", "title": "Development Infrastructure"},
    "E015": {"section": "15_architectural_standards.tex", "part": "part3_advanced", "title": "Architectural Standards and Patterns"},
    "E016": {"section": "16_attribution_citations.tex", "part": "part3_advanced", "title": "Attribution and Citations"},
    "E017": {"section": "17_memory_performance.tex", "part": "part3_advanced", "title": "Memory Management and Performance"},
    "E018": {"section": "18_browser_automation.tex", "part": "part4_professional", "title": "Browser Automation and Testing"},
    "E019": {"section": "19_workspace_organization.tex", "part": "part4_professional", "title": "Workspace Organization"},
    "E020": {"section": "20_version_control.tex", "part": "part4_professional", "title": "Version Control and Git Workflow"},
    "E021": {"section": "21_future_work.tex", "part": "part4_professional", "title": "Future Work and Roadmap"},
    "E022": {"section": "22_key_statistics.tex", "part": "part4_professional", "title": "Key Statistics and Metrics"},
    "E023": {"section": "23_visual_diagrams.tex", "part": "part4_professional", "title": "Visual Diagrams and Schematics"},
    "E024": {"section": "24_lessons_learned.tex", "part": "part4_professional", "title": "Lessons Learned and Best Practices"},
    "E025": {"section": "appendix_01.tex", "part": "appendix", "title": "Appendix Reference Part 1"},
    "E026": {"section": "appendix_02.tex", "part": "appendix", "title": "Appendix Reference Part 2"},
    "E027": {"section": "appendix_03.tex", "part": "appendix", "title": "Appendix Reference Part 3"},
    "E028": {"section": "appendix_04.tex", "part": "appendix", "title": "Appendix Reference Part 4"},
    "E029": {"section": "appendix_05.tex", "part": "appendix", "title": "Appendix Reference Part 5"},
}


def latex_to_plain_text(text: str) -> str:
    """Convert LaTeX to plain text for markdown."""
    # Remove comments
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)

    # Convert formatting
    text = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', text)
    text = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', text)
    text = re.sub(r'\\texttt\{([^}]+)\}', r'`\1`', text)
    text = re.sub(r'\\highlight\{([^}]+)\}', r'**\1**', text)
    text = re.sub(r'\\url\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\statusok', '[OK]', text)
    text = re.sub(r'\\success\{([^}]+)\}', r'\1', text)

    # Remove blocks
    text = re.sub(r'\\begin\{(block|alertblock|exampleblock)\}(\{[^}]+\})?', '', text)
    text = re.sub(r'\\end\{(block|alertblock|exampleblock)\}', '', text)

    # Convert lists
    text = re.sub(r'\\begin\{itemize\}', '', text)
    text = re.sub(r'\\end\{itemize\}', '', text)
    text = re.sub(r'\\begin\{enumerate\}', '', text)
    text = re.sub(r'\\end\{enumerate\}', '', text)
    text = re.sub(r'\\item\s+', '- ', text)

    # Remove graphics/diagrams
    text = re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', '[Visual diagram - see PDF]', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{columns\}.*?\\end\{columns\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{column\}.*?\\end\{column\}', '', text, flags=re.DOTALL)

    # Remove spacing commands
    text = re.sub(r'\\vspace\{[^}]+\}', '', text)
    text = re.sub(r'\\hspace\{[^}]+\}', '', text)

    # Clean up whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = text.strip()

    return text


def extract_frames(tex_file: Path) -> List[Dict[str, str]]:
    """Extract frame content from LaTeX file."""
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()

    frames = []
    pattern = r'\\begin\{frame\}\{([^}]+)\}(.*?)\\end\{frame\}'

    for match in re.finditer(pattern, content, re.DOTALL):
        title = match.group(1).strip()
        body = match.group(2).strip()

        # Convert to plain text
        body_clean = latex_to_plain_text(body)

        if body_clean:
            frames.append({"title": title, "content": body_clean})

    return frames


def generate_markdown(episode_id: str, info: Dict, frames: List[Dict]) -> str:
    """Generate markdown content."""
    md = f"""# {episode_id}: {info['title']}

**Part:** {info['part'].replace('_', ' ').title()}
**Duration:** 15-20 minutes
**Source:** DIP-SMC-PSO Comprehensive Presentation

---

## Overview

This episode covers {info['title'].lower()} from the DIP-SMC-PSO project.

"""

    # Add frames
    for frame in frames:
        md += f"## {frame['title']}\n\n"
        md += frame['content'] + "\n\n"
        md += "---\n\n"

    # Add footer
    md += """## Resources

- **Repository:** https://github.com/theSadeQ/dip-smc-pso.git
- **Documentation:** `docs/` directory
- **Getting Started:** `docs/guides/getting-started.md`

---

*Educational podcast episode generated from comprehensive presentation materials*
"""

    return md


def generate_latex_pdf(episode_id: str, info: Dict, frames: List[Dict], output_dir: Path) -> bool:
    """Generate LaTeX file and compile to PDF."""
    latex_content = f"""\\documentclass[11pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{hyperref}}
\\usepackage{{enumitem}}
\\usepackage{{fancyhdr}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\rhead{{{episode_id}}}
\\lhead{{DIP-SMC-PSO Learning Episode}}
\\rfoot{{\\thepage}}

\\title{{\\Large\\textbf{{{episode_id}: {info['title']}}}}}
\\author{{DIP-SMC-PSO Educational Series}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\section*{{Overview}}

This episode covers {info['title'].lower()} from the DIP-SMC-PSO project.

\\textbf{{Part:}} {info['part'].replace('_', ' ').title()}

\\textbf{{Duration:}} 15-20 minutes

\\textbf{{Source:}} Comprehensive Presentation Materials

\\newpage

"""

    # Add frames
    for i, frame in enumerate(frames, 1):
        latex_content += f"""\\section{{{frame['title']}}}

{frame['content']}

"""

    # Add resources
    latex_content += """\\newpage

\\section*{{Resources}}

\\begin{itemize}
    \\item \\textbf{Repository:} \\url{https://github.com/theSadeQ/dip-smc-pso.git}
    \\item \\textbf{Documentation:} See \\texttt{docs/} directory
    \\item \\textbf{Getting Started:} \\texttt{docs/guides/getting-started.md}
\\end{itemize}

\\vfill

\\noindent\\textit{Educational podcast episode generated from comprehensive presentation materials}

\\end{document}
"""

    # Write LaTeX file
    tex_file = output_dir / f"{episode_id}_{info['title'].lower().replace(' ', '_').replace(',', '').replace(':', '')}.tex"
    tex_file.parent.mkdir(parents=True, exist_ok=True)

    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    print(f"[OK] Generated LaTeX: {tex_file.name}")

    # Compile to PDF
    pdf_file = tex_file.with_suffix('.pdf')

    try:
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', str(output_dir), str(tex_file)],
            capture_output=True,
            text=True,
            timeout=30
        )

        if pdf_file.exists():
            # Clean up auxiliary files
            for ext in ['.aux', '.log', '.out']:
                aux_file = tex_file.with_suffix(ext)
                if aux_file.exists():
                    aux_file.unlink()

            print(f"[OK] Generated PDF: {pdf_file.name}")
            return True
        else:
            print(f"[ERROR] PDF generation failed")
            return False

    except Exception as e:
        print(f"[ERROR] LaTeX compilation failed: {e}")
        return False


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    presentations_dir = script_dir.parent
    sections_dir = presentations_dir / "sections"
    output_base = script_dir / "episodes_final"

    output_md = output_base / "markdown"
    output_pdf = output_base / "pdf"
    output_md.mkdir(parents=True, exist_ok=True)
    output_pdf.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print("Generating Educational Podcast Episodes (Clean Version)")
    print(f"{'='*70}\n")

    success_count = 0

    for episode_id in sorted(EPISODES.keys()):
        info = EPISODES[episode_id]
        print(f"\nProcessing {episode_id}: {info['title']}")
        print("-" * 70)

        # Find section file
        section_file = sections_dir / info['part'] / info['section']

        if not section_file.exists():
            print(f"[WARNING] Section not found: {section_file}")
            continue

        # Extract frames
        frames = extract_frames(section_file)

        if not frames:
            print(f"[WARNING] No frames found")
            continue

        print(f"[OK] Extracted {len(frames)} frames")

        # Generate markdown
        md_content = generate_markdown(episode_id, info, frames)
        md_file = output_md / f"{episode_id}_{info['title'].lower().replace(' ', '_').replace(',', '').replace(':', '')}.md"

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"[OK] Generated markdown: {md_file.name}")

        # Generate PDF
        pdf_success = generate_latex_pdf(episode_id, info, frames, output_pdf)

        if pdf_success:
            success_count += 1

    print(f"\n{'='*70}")
    print(f"Complete: {success_count}/{len(EPISODES)} PDFs generated")
    print(f"{'='*70}\n")
    print(f"Markdown: {output_md}")
    print(f"PDFs: {output_pdf}")
    print(f"\nNext: Upload PDFs to NotebookLM (notebooklm.google.com)")


if __name__ == "__main__":
    main()
