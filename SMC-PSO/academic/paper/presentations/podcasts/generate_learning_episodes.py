#!/usr/bin/env python
"""
Extract real learning material from presentation sections and generate
educational podcast episodes in markdown and PDF formats.

This script replaces placeholder episodes with actual content from the
comprehensive presentation materials.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Episode mapping: real presentation sections to podcast episodes
EPISODE_MAP = {
    # Part 1: Foundations (E001-E005) - 5 episodes
    "E001": {"section": "01_project_overview.tex", "part": "part1_foundations", "title": "Project Overview and Introduction"},
    "E002": {"section": "02_control_theory.tex", "part": "part1_foundations", "title": "Control Theory Fundamentals"},
    "E003": {"section": "03_plant_models.tex", "part": "part1_foundations", "title": "Plant Models and Dynamics"},
    "E004": {"section": "04_optimization_pso.tex", "part": "part1_foundations", "title": "PSO Optimization Fundamentals"},
    "E005": {"section": "05_simulation_engine.tex", "part": "part1_foundations", "title": "Simulation Engine Architecture"},

    # Part 2: Infrastructure (E006-E011) - 6 episodes
    "E006": {"section": "06_analysis_visualization.tex", "part": "part2_infrastructure", "title": "Analysis and Visualization Tools"},
    "E007": {"section": "07_testing_qa.tex", "part": "part2_infrastructure", "title": "Testing and Quality Assurance"},
    "E008": {"section": "08_research_outputs.tex", "part": "part2_infrastructure", "title": "Research Outputs and Publications"},
    "E009": {"section": "09_educational_materials.tex", "part": "part2_infrastructure", "title": "Educational Materials and Learning Paths"},
    "E010": {"section": "10_documentation_system.tex", "part": "part2_infrastructure", "title": "Documentation System and Navigation"},
    "E011": {"section": "11_configuration_deployment.tex", "part": "part2_infrastructure", "title": "Configuration and Deployment"},

    # Part 3: Advanced Topics (E012-E017) - 6 episodes
    "E012": {"section": "12_hil_system.tex", "part": "part3_advanced", "title": "Hardware-in-the-Loop System"},
    "E013": {"section": "13_monitoring_infrastructure.tex", "part": "part3_advanced", "title": "Monitoring Infrastructure"},
    "E014": {"section": "14_development_infrastructure.tex", "part": "part3_advanced", "title": "Development Infrastructure"},
    "E015": {"section": "15_architectural_standards.tex", "part": "part3_advanced", "title": "Architectural Standards and Patterns"},
    "E016": {"section": "16_attribution_citations.tex", "part": "part3_advanced", "title": "Attribution and Citations"},
    "E017": {"section": "17_memory_performance.tex", "part": "part3_advanced", "title": "Memory Management and Performance"},

    # Part 4: Professional Practice (E018-E024) - 7 episodes
    "E018": {"section": "18_browser_automation.tex", "part": "part4_professional", "title": "Browser Automation and Testing"},
    "E019": {"section": "19_workspace_organization.tex", "part": "part4_professional", "title": "Workspace Organization"},
    "E020": {"section": "20_version_control.tex", "part": "part4_professional", "title": "Version Control and Git Workflow"},
    "E021": {"section": "21_future_work.tex", "part": "part4_professional", "title": "Future Work and Roadmap"},
    "E022": {"section": "22_key_statistics.tex", "part": "part4_professional", "title": "Key Statistics and Metrics"},
    "E023": {"section": "23_visual_diagrams.tex", "part": "part4_professional", "title": "Visual Diagrams and Schematics"},
    "E024": {"section": "24_lessons_learned.tex", "part": "part4_professional", "title": "Lessons Learned and Best Practices"},

    # Appendix (E025-E029) - 5 episodes
    "E025": {"section": "appendix_01.tex", "part": "appendix", "title": "Appendix Reference Part 1"},
    "E026": {"section": "appendix_02.tex", "part": "appendix", "title": "Appendix Reference Part 2"},
    "E027": {"section": "appendix_03.tex", "part": "appendix", "title": "Appendix Reference Part 3"},
    "E028": {"section": "appendix_04.tex", "part": "appendix", "title": "Appendix Reference Part 4"},
    "E029": {"section": "appendix_05.tex", "part": "appendix", "title": "Appendix Reference Part 5"},
}


def extract_frame_content(tex_content: str) -> List[Dict[str, str]]:
    """Extract content from LaTeX \\begin{frame} blocks."""
    frames = []

    # Find all frame blocks
    frame_pattern = r'\\begin{frame}{([^}]+)}(.*?)\\end{frame}'
    matches = re.finditer(frame_pattern, tex_content, re.DOTALL)

    for match in matches:
        title = match.group(1)
        content = match.group(2)

        # Clean up LaTeX commands
        content = re.sub(r'\\textbf{([^}]+)}', r'**\1**', content)
        content = re.sub(r'\\highlight{([^}]+)}', r'**\1**', content)
        content = re.sub(r'\\emph{([^}]+)}', r'*\1*', content)
        content = re.sub(r'\\texttt{([^}]+)}', r'`\1`', content)
        content = re.sub(r'\\url{([^}]+)}', r'\1', content)

        # Convert itemize/enumerate to markdown lists
        content = re.sub(r'\\begin{itemize}', '', content)
        content = re.sub(r'\\end{itemize}', '', content)
        content = re.sub(r'\\begin{enumerate}', '', content)
        content = re.sub(r'\\end{enumerate}', '', content)
        content = re.sub(r'\\item\s+', '- ', content)

        # Remove tikzpicture blocks (can't easily convert to markdown)
        content = re.sub(r'\\begin{tikzpicture}.*?\\end{tikzpicture}', '[DIAGRAM]', content, flags=re.DOTALL)

        # Remove columns blocks
        content = re.sub(r'\\begin{columns}.*?\\end{columns}', '', content, flags=re.DOTALL)
        content = re.sub(r'\\begin{column}.*?\\end{column}', '', content, flags=re.DOTALL)

        # Remove vspace commands
        content = re.sub(r'\\vspace{[^}]+}', '', content)

        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = content.strip()

        if content:
            frames.append({"title": title, "content": content})

    return frames


def generate_markdown_episode(episode_id: str, info: Dict[str, str], sections_dir: Path, output_dir: Path) -> bool:
    """Generate markdown episode from presentation section."""
    section_file = sections_dir / info["part"] / info["section"]

    if not section_file.exists():
        print(f"[WARNING] Section file not found: {section_file}")
        return False

    # Read presentation section
    with open(section_file, 'r', encoding='utf-8') as f:
        tex_content = f.read()

    # Extract frames
    frames = extract_frame_content(tex_content)

    if not frames:
        print(f"[WARNING] No frames found in {section_file}")
        return False

    # Generate markdown
    md_content = f"""# {episode_id}: {info['title']}

**Part:** {info['part'].replace('_', ' ').title()}
**Duration:** 15-20 minutes
**Source:** DIP-SMC-PSO Comprehensive Presentation

---

## Learning Objectives

After this episode, you will understand:

"""

    # Add learning objectives from first 3 frame titles
    for i, frame in enumerate(frames[:3]):
        md_content += f"{i+1}. {frame['title']}\n"

    md_content += "\n---\n\n"

    # Add frame content
    for frame in frames:
        md_content += f"## {frame['title']}\n\n"
        md_content += frame['content'] + "\n\n"
        md_content += "---\n\n"

    # Add key takeaways section
    md_content += """## Key Takeaways

"""

    # Extract key points from frame titles
    for i, frame in enumerate(frames[:5], 1):
        md_content += f"{i}. {frame['title']}\n"

    md_content += f"""

---

## Next Steps

1. **Practice:** Try implementing these concepts in the DIP-SMC-PSO codebase
2. **Explore:** Review the documentation at `docs/` directory
3. **Experiment:** Run simulations with different parameters

---

## Resources

- **Repository:** https://github.com/theSadeQ/dip-smc-pso.git
- **Documentation:** See `docs/` directory
- **Getting Started:** `docs/guides/getting-started.md`

---

*Generated from presentation materials for educational podcast series*
"""

    # Write markdown file
    output_file = output_dir / f"{episode_id}_{info['title'].lower().replace(' ', '_').replace(':', '').replace('?', '').replace(',', '')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"[OK] Generated markdown: {output_file.name}")
    return True


def generate_pdf_from_markdown(md_file: Path, output_dir: Path) -> bool:
    """Generate PDF from markdown using pandoc."""
    pdf_file = output_dir / md_file.with_suffix('.pdf').name

    try:
        cmd = [
            'pandoc',
            str(md_file),
            '-o', str(pdf_file),
            '--pdf-engine=xelatex',
            '-V', 'geometry:margin=1in',
            '-V', 'fontsize=11pt',
            '-V', 'mainfont=DejaVu Sans',
            '--toc',
            '--toc-depth=2'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"[OK] Generated PDF: {pdf_file.name}")
            return True
        else:
            print(f"[ERROR] PDF generation failed: {result.stderr}")
            return False

    except FileNotFoundError:
        print("[ERROR] pandoc not found. Install with: choco install pandoc")
        return False


def main():
    """Main entry point."""
    # Paths
    script_dir = Path(__file__).parent  # podcasts/
    presentations_dir = script_dir.parent  # presentations/
    sections_dir = presentations_dir / "sections"
    output_base = script_dir / "episodes_learning"

    # Create output directories
    output_md = output_base / "markdown"
    output_pdf = output_base / "pdf"
    output_md.mkdir(parents=True, exist_ok=True)
    output_pdf.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print("Generating Educational Podcast Episodes")
    print(f"{'='*70}\n")

    # Generate episodes
    success_count = 0
    total_count = len(EPISODE_MAP)

    for episode_id, info in sorted(EPISODE_MAP.items()):
        print(f"\nProcessing {episode_id}: {info['title']}")
        print("-" * 70)

        # Generate markdown
        md_success = generate_markdown_episode(episode_id, info, sections_dir, output_md)

        if md_success:
            # Generate PDF
            md_file = list(output_md.glob(f"{episode_id}_*.md"))[0]
            pdf_success = generate_pdf_from_markdown(md_file, output_pdf)

            if pdf_success:
                success_count += 1

    # Summary
    print(f"\n{'='*70}")
    print(f"Generation Complete: {success_count}/{total_count} episodes")
    print(f"{'='*70}\n")
    print(f"Markdown files: {output_md}")
    print(f"PDF files: {output_pdf}")
    print(f"\nNext steps:")
    print(f"1. Review markdown files for accuracy")
    print(f"2. Upload PDFs to NotebookLM for podcast generation")
    print(f"3. Clean up old placeholder episodes")


if __name__ == "__main__":
    main()
