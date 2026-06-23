"""
Extract individual sections from LT7_RESEARCH_PAPER.md into separate files.
Each section file includes the front matter for standalone compilation.
"""

# Section boundaries (line numbers)
sections = [
    {
        "name": "Section_00_Front_Matter",
        "title": "Front Matter & Abstract",
        "start": 1,
        "end": 40
    },
    {
        "name": "Section_01_Introduction",
        "title": "Section 1: Introduction",
        "start": 41,
        "end": 235
    },
    {
        "name": "Section_02_System_Model",
        "title": "Section 2: System Model and Problem Formulation",
        "start": 236,
        "end": 557
    },
    {
        "name": "Section_03_Controller_Design",
        "title": "Section 3: Controller Design",
        "start": 558,
        "end": 1595
    },
    {
        "name": "Section_04_Lyapunov_Stability",
        "title": "Section 4: Lyapunov Stability Analysis",
        "start": 1596,
        "end": 2475
    },
    {
        "name": "Section_05_PSO_Methodology",
        "title": "Section 5: PSO Optimization Methodology",
        "start": 2476,
        "end": 3149
    },
    {
        "name": "Section_06_Experimental_Setup",
        "title": "Section 6: Experimental Setup and Benchmarking Protocol",
        "start": 3150,
        "end": 4149
    },
    {
        "name": "Section_07_Performance_Results",
        "title": "Section 7: Performance Comparison Results",
        "start": 4150,
        "end": 4967
    },
    {
        "name": "Section_08_Robustness_Analysis",
        "title": "Section 8: Robustness Analysis",
        "start": 4968,
        "end": 6012
    },
    {
        "name": "Section_09_Discussion",
        "title": "Section 9: Discussion",
        "start": 6013,
        "end": 6457
    },
    {
        "name": "Section_10_Conclusion",
        "title": "Section 10: Conclusion and Future Work",
        "start": 6458,
        "end": 6639
    },
    {
        "name": "Section_11_References",
        "title": "References",
        "start": 6640,
        "end": 6932
    }
]

# Read the main file
source_file = "../LT7_RESEARCH_PAPER.md"
with open(source_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extract front matter (lines 1-40) for reuse
front_matter = lines[0:40]

print(f"[INFO] Extracting {len(sections)} sections from {source_file}")
print(f"[INFO] Total lines in source: {len(lines)}")

# Extract each section
for section in sections:
    output_file = f"{section['name']}.md"

    # For sections 1-11, include front matter + section content
    # For section 0 (front matter), just extract it as-is
    if section['name'] == "Section_00_Front_Matter":
        content = lines[section['start']-1:section['end']]
    else:
        # Include front matter + section content
        section_lines = lines[section['start']-1:section['end']]
        content = front_matter + ["\n\n"] + section_lines

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(content)

    line_count = len(content)
    print(f"[OK] Created {output_file} ({line_count} lines)")

print(f"\n[OK] All sections extracted successfully!")
print(f"[INFO] Output directory: sections/")
