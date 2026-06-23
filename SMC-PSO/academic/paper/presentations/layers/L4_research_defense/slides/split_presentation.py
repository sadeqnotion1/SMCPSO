#!/usr/bin/env python3
"""
Split the monolithic presentation into modular section files.
"""

import re
import os

def main():
    # Read the current presentation
    print("[INFO] Reading comprehensive_project_presentation.tex...")
    with open('comprehensive_project_presentation.tex', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find document boundaries
    begin_doc = content.find(r'\begin{document}')
    end_doc = content.find(r'\end{document}')

    if begin_doc == -1:
        print("[ERROR] Could not find \\begin{document}")
        return 1

    if end_doc == -1:
        print("[ERROR] Could not find \\end{document}")
        return 1

    # Extract sections
    preamble = content[:begin_doc + len(r'\begin{document}')]
    main_content = content[begin_doc + len(r'\begin{document}'):end_doc]
    footer = content[end_doc:]

    print(f"[INFO] Preamble: {len(preamble)} chars")
    print(f"[INFO] Main content: {len(main_content)} chars")
    print(f"[INFO] Footer: {len(footer)} chars")

    # Split by section markers
    # Pattern: % SECTION N: TITLE followed by \section{Title}
    section_pattern = r'(% ={70,}\r?\n% SECTION \d+:.*?\r?\n% ={70,}\r?\n\\section\{[^}]+\})'
    parts = re.split(section_pattern, main_content, flags=re.MULTILINE)

    print(f"[INFO] Split into {len(parts)} parts")

    # Group sections
    sections = []
    intro = parts[0] if parts else ""

    for i in range(1, len(parts), 2):
        if i + 1 <= len(parts):
            header = parts[i] if i < len(parts) else ""
            body = parts[i + 1] if i + 1 < len(parts) else ""

            # Extract section title
            title_match = re.search(r'\\section\{([^}]+)\}', header)
            if title_match:
                title = title_match.group(1)
                sections.append({
                    'header': header,
                    'title': title,
                    'body': body,
                    'full': header + body
                })
                print(f"[SECTION] {len(sections)}. {title}")

    print(f"\n[INFO] Found {len(sections)} sections total")

    # Define file mapping
    file_map = [
        # Part 1: Foundations
        ('sections/part1_foundations/01_project_overview.tex', 0),
        ('sections/part1_foundations/02_control_theory.tex', 1),
        ('sections/part1_foundations/03_plant_models.tex', 2),
        ('sections/part1_foundations/04_optimization_pso.tex', 3),
        ('sections/part1_foundations/05_simulation_engine.tex', 4),

        # Part 2: Infrastructure
        ('sections/part2_infrastructure/06_analysis_visualization.tex', 5),
        ('sections/part2_infrastructure/07_testing_qa.tex', 6),
        ('sections/part2_infrastructure/08_research_outputs.tex', 7),
        ('sections/part2_infrastructure/09_educational_materials.tex', 8),
        ('sections/part2_infrastructure/10_documentation_system.tex', 9),
        ('sections/part2_infrastructure/11_configuration_deployment.tex', 10),

        # Part 3: Advanced
        ('sections/part3_advanced/12_hil_system.tex', 11),
        ('sections/part3_advanced/13_monitoring_infrastructure.tex', 12),
        ('sections/part3_advanced/14_development_infrastructure.tex', 13),
        ('sections/part3_advanced/15_architectural_standards.tex', 14),
        ('sections/part3_advanced/16_attribution_citations.tex', 15),
        ('sections/part3_advanced/17_memory_performance.tex', 16),

        # Part 4: Professional
        ('sections/part4_professional/18_browser_automation.tex', 17),
        ('sections/part4_professional/19_workspace_organization.tex', 18),
        ('sections/part4_professional/20_version_control.tex', 19),
        ('sections/part4_professional/21_future_work.tex', 20),
        ('sections/part4_professional/22_key_statistics.tex', 21),
        ('sections/part4_professional/23_visual_diagrams.tex', 22),
        ('sections/part4_professional/24_lessons_learned.tex', 23),
    ]

    # Write introduction
    intro_path = 'sections/00_introduction.tex'
    print(f"\n[WRITE] {intro_path}")
    with open(intro_path, 'w', encoding='utf-8') as f:
        f.write(intro.strip() + '\n')

    # Write each section file
    created_files = []
    for filepath, section_idx in file_map:
        if section_idx < len(sections):
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            section_content = sections[section_idx]['full']

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(section_content.strip() + '\n')

            print(f"[WRITE] {filepath} <- '{sections[section_idx]['title']}'")
            created_files.append(filepath)

    # Check for remaining sections (appendix)
    appendix_start = 24
    if len(sections) > appendix_start:
        print(f"\n[INFO] Found {len(sections) - appendix_start} appendix sections")
        for i in range(appendix_start, len(sections)):
            filename = f"sections/appendix/appendix_{i - appendix_start + 1:02d}.tex"
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(sections[i]['full'].strip() + '\n')

            print(f"[WRITE] {filename} <- '{sections[i]['title']}'")
            created_files.append(filename)

    print(f"\n[OK] Created {len(created_files)} section files")
    print(f"[INFO] Introduction: {intro_path}")

    return 0

if __name__ == '__main__':
    exit(main())
