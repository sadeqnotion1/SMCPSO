#!/usr/bin/env python
"""
Quick generator for Parts 2-4 + Appendix episodes
Creates placeholder PDFs for all remaining episodes without detailed definitions
"""

import subprocess
from pathlib import Path

# Episode ranges for each part
PART_RANGES = {
    "part2_infrastructure": {
        "start": 21,
        "end": 44,
        "title_prefix": "Part 2 Infrastructure Episode",
        "sections": ["06", "07", "08", "09", "10", "11"]
    },
    "part3_advanced": {
        "start": 45,
        "end": 68,
        "title_prefix": "Part 3 Advanced Topics Episode",
        "sections": ["12", "13", "14", "15", "16", "17"]
    },
    "part4_professional": {
        "start": 69,
        "end": 96,
        "title_prefix": "Part 4 Professional Practice Episode",
        "sections": ["18", "19", "20", "21", "22", "23", "24"]
    },
    "appendix": {
        "start": 97,
        "end": 116,
        "title_prefix": "Appendix Reference Episode",
        "sections": ["A1", "A2", "A3", "A4", "A5"]
    }
}

def create_episode_tex(episode_num, part_name, section, output_dir):
    """Create a simple episode .tex file"""

    episode_id = f"E{episode_num:03d}"
    title = f"{PART_RANGES[part_name]['title_prefix']} {episode_num - PART_RANGES[part_name]['start'] + 1}"
    safe_title = title.lower().replace(' ', '_')

    tex_content = f"""% ============================================================================
% Podcast Episode {episode_id}: {title}
% ============================================================================

\\documentclass[11pt,a4paper]{{article}}
\\input{{../../../speaker_config.tex}}

\\title{{%
    \\Large\\textbf{{Podcast Episode {episode_id}}} \\\\[0.5em]
    \\large {title} \\\\[1em]
    \\normalsize DIP-SMC-PSO Project
}}
\\author{{Generated from comprehensive presentation materials}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle
\\thispagestyle{{empty}}

\\section*{{Episode Overview}}

This episode is part of the comprehensive 100+ episode podcast series.

\\textbf{{Episode:}} {episode_id}

\\textbf{{Part:}} {part_name.replace('_', ' ').title()}

\\textbf{{Section:}} {section}

\\textbf{{Duration:}} 15-20 minutes (estimated)

\\section{{Introduction}}

[TODO: Add detailed content for this episode]

This episode covers key topics from {part_name.replace('_', ' ')}.

\\section{{Main Content}}

[TODO: Extract relevant content from presentation slides]

\\section{{Key Takeaways}}

\\begin{{itemize}}
    \\item Key insight 1
    \\item Key insight 2
    \\item Key insight 3
\\end{{itemize}}

\\section*{{Production Notes}}

\\textbf{{NotebookLM Processing:}}
\\begin{{enumerate}}
    \\item Compile this .tex file to PDF
    \\item Upload PDF to NotebookLM
    \\item Generate audio overview
    \\item Download as {episode_id}.mp3
\\end{{enumerate}}

\\end{{document}}
"""

    # Create output directory
    part_dir = output_dir / part_name
    part_dir.mkdir(parents=True, exist_ok=True)

    # Write .tex file
    tex_file = part_dir / f"{episode_id}_{safe_title}.tex"
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(tex_content)

    return tex_file


def compile_pdf(tex_file, output_dir):
    """Compile .tex to PDF"""
    try:
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory',
             str(tex_file.parent), str(tex_file)],
            capture_output=True,
            text=True,
            check=False,
            timeout=30
        )

        pdf_file = tex_file.with_suffix('.pdf')
        if pdf_file.exists():
            # Cleanup aux files
            for ext in ['.aux', '.log', '.out']:
                aux = tex_file.with_suffix(ext)
                if aux.exists():
                    aux.unlink()
            return True
        return False
    except Exception as e:
        print(f"[ERROR] Compilation failed for {tex_file.name}: {e}")
        return False


def main():
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / "episodes"

    total_episodes = 0
    total_compiled = 0

    for part_name, config in PART_RANGES.items():
        print(f"\n[INFO] Generating {part_name}...")
        start = config["start"]
        end = config["end"]
        sections = config["sections"]

        episodes_in_part = end - start + 1
        episodes_per_section = episodes_in_part // len(sections)

        section_idx = 0
        for episode_num in range(start, end + 1):
            # Determine which section this episode belongs to
            if section_idx < len(sections) - 1 and \
               (episode_num - start) >= (section_idx + 1) * episodes_per_section:
                section_idx += 1

            section = sections[section_idx]

            # Create .tex file
            tex_file = create_episode_tex(episode_num, part_name, section, output_dir)
            print(f"[OK] Created E{episode_num:03d}")
            total_episodes += 1

            # Compile to PDF
            if compile_pdf(tex_file, output_dir):
                print(f"[OK] Compiled E{episode_num:03d}")
                total_compiled += 1

    print(f"\n[SUMMARY]")
    print(f"Total episodes created: {total_episodes}")
    print(f"Total PDFs compiled: {total_compiled}")
    print(f"\n[OK] All parts generated in {output_dir}")


if __name__ == '__main__':
    main()
