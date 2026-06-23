"""
Analyze figure usage across all textbook chapters.

Identifies:
- Available figure files in figures/ directory
- Figure references in LaTeX chapters (\includegraphics)
- Unused figures (files with no references)
- Missing figures (references with no files)
- Caption analysis for quality

Helps identify missing diagrams and improve visual documentation.
"""

import re
from pathlib import Path
from collections import defaultdict

def scan_figure_files():
    """Scan figures/ directory for all image files."""
    figures_dir = Path('figures')

    if not figures_dir.exists():
        print(f'[WARNING] Figures directory not found: {figures_dir}')
        return {}

    # Organize by chapter
    chapter_figures = defaultdict(list)

    for fig_file in figures_dir.rglob('*'):
        if fig_file.is_file() and fig_file.suffix.lower() in ['.png', '.pdf', '.jpg', '.jpeg', '.eps']:
            # Extract chapter prefix (e.g., 'ch03_' from 'ch03_sliding_surface.png')
            name = fig_file.name
            if name.startswith('ch'):
                chapter = name[:4]  # 'ch03'
                chapter_figures[chapter].append(fig_file)
            else:
                chapter_figures['other'].append(fig_file)

    return chapter_figures

def extract_figure_references(tex_file):
    """Extract all \\includegraphics references from a chapter."""
    content = tex_file.read_text(encoding='utf-8')

    # Match \includegraphics[options]{path} or \includegraphics{path}
    pattern = r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}'
    matches = re.findall(pattern, content)

    # Also extract captions for quality analysis
    caption_pattern = r'\\caption\{([^}]+)\}'
    captions = re.findall(caption_pattern, content)

    return matches, captions

def analyze_figure_usage():
    """Build complete figure usage analysis."""
    source_dir = Path('source/chapters')

    # Track all references
    referenced_figures = set()
    chapter_refs = defaultdict(list)
    all_captions = []

    for tex_file in sorted(source_dir.glob('ch*.tex')):
        chapter_num = tex_file.stem[:4]  # 'ch03' from 'ch03_classical_smc.tex'

        refs, captions = extract_figure_references(tex_file)
        chapter_refs[chapter_num] = refs

        for ref in refs:
            # Normalize path (remove 'figures/' prefix if present)
            clean_ref = ref.replace('figures/', '')
            referenced_figures.add(clean_ref)

        all_captions.extend(captions)

    # Scan available files
    available_figures = scan_figure_files()

    return chapter_refs, referenced_figures, available_figures, all_captions

def print_usage_summary(chapter_refs, referenced_figures, available_figures):
    """Print figure usage summary."""
    print('=' * 80)
    print('FIGURE USAGE SUMMARY')
    print('=' * 80)
    print()

    total_refs = sum(len(refs) for refs in chapter_refs.values())
    total_files = sum(len(figs) for figs in available_figures.values())

    print(f'Total \\includegraphics references: {total_refs}')
    print(f'Total figure files available: {total_files}')
    print(f'Unique figure paths referenced: {len(referenced_figures)}')
    print()

    # Per-chapter breakdown
    print('PER-CHAPTER BREAKDOWN:')
    print('-' * 80)
    for ch_num in sorted(chapter_refs.keys()):
        refs = chapter_refs[ch_num]
        status = '[OK]' if len(refs) >= 2 else '[LOW]' if len(refs) == 1 else '[NONE]'
        print(f'{status} {ch_num}: {len(refs)} figures')
        if refs:
            for ref in refs[:3]:  # Show first 3
                print(f'     - {ref}')
            if len(refs) > 3:
                print(f'     ... and {len(refs)-3} more')
    print()

def identify_unused_figures(referenced_figures, available_figures):
    """Find figure files that are never referenced."""
    print('=' * 80)
    print('UNUSED FIGURES ANALYSIS')
    print('=' * 80)
    print()

    unused = []
    for chapter, fig_files in available_figures.items():
        for fig_file in fig_files:
            # Check if this file is referenced
            fig_name = fig_file.name

            # Also check with different path formats
            is_referenced = any(
                fig_name in ref or
                str(fig_file.relative_to(Path('figures'))).replace('\\', '/') in ref
                for ref in referenced_figures
            )

            if not is_referenced:
                unused.append((chapter, fig_file))

    if unused:
        print(f'Found {len(unused)} UNUSED figure files:')
        print('-' * 80)
        for chapter, fig_file in sorted(unused):
            print(f'  [!] {chapter}: {fig_file.name}')
    else:
        print('[OK] All figure files are referenced')
    print()

    return unused

def identify_missing_figures(referenced_figures, available_figures):
    """Find referenced figures with no corresponding files."""
    print('=' * 80)
    print('MISSING FIGURES ANALYSIS')
    print('=' * 80)
    print()

    # Build set of available figure names
    available_names = set()
    for fig_files in available_figures.values():
        for fig_file in fig_files:
            available_names.add(fig_file.name)
            # Also add with path
            rel_path = str(fig_file.relative_to(Path('figures'))).replace('\\', '/')
            available_names.add(rel_path)

    missing = []
    for ref in referenced_figures:
        # Extract filename from reference
        ref_name = Path(ref).name

        # Check if file exists
        is_available = any(ref_name in name for name in available_names)

        if not is_available:
            missing.append(ref)

    if missing:
        print(f'Found {len(missing)} MISSING figure files (referenced but not found):')
        print('-' * 80)
        for ref in sorted(missing):
            print(f'  [!] {ref}')
    else:
        print('[OK] All referenced figures have corresponding files')
    print()

    return missing

def analyze_caption_quality(all_captions):
    """Analyze caption quality."""
    print('=' * 80)
    print('CAPTION QUALITY ANALYSIS')
    print('=' * 80)
    print()

    print(f'Total captions: {len(all_captions)}')

    # Identify short/generic captions (potential quality issues)
    short_captions = [cap for cap in all_captions if len(cap) < 50]
    generic_words = ['Figure', 'Plot', 'Graph', 'Diagram', 'Chart', 'shows', 'depicts']
    generic_captions = [cap for cap in all_captions if any(word in cap for word in generic_words)]

    if short_captions:
        print(f'[WARNING] {len(short_captions)} SHORT captions (<50 chars):')
        for cap in short_captions[:5]:
            print(f'  - "{cap}"')
        if len(short_captions) > 5:
            print(f'  ... and {len(short_captions)-5} more')
        print()

    if generic_captions:
        print(f'[INFO] {len(generic_captions)} captions use generic wording')
        print('      Consider making captions more descriptive and self-contained')
    print()

def recommend_missing_diagrams():
    """Recommend additional diagrams based on textbook content."""
    print('=' * 80)
    print('RECOMMENDED ADDITIONAL DIAGRAMS')
    print('=' * 80)
    print()

    recommendations = [
        ('ch02', 'DIP free-body diagram', 'Show forces/torques for Lagrangian derivation'),
        ('ch02', 'Lyapunov stability regions', 'Visualize basin of attraction'),
        ('ch03', 'Classical SMC control flow', 'Algorithm flowchart with boundary layer logic'),
        ('ch03', 'Chattering visualization', 'Time-domain plot showing high-frequency oscillations'),
        ('ch04', 'STA phase portrait', 'Show finite-time convergence in (s, \\dot{s}) plane'),
        ('ch05', 'Adaptive gain evolution', 'Time series of k_1(t), k_2(t) during adaptation'),
        ('ch06', 'Hybrid mode switching logic', 'State machine diagram for STA/Adaptive switching'),
        ('ch07', 'PSO convergence animation', 'Particle swarm movement in 2D gain space'),
        ('ch08', 'Performance radar chart', 'Multi-metric comparison of 4 controllers'),
        ('ch09', 'Pareto frontier', 'Energy vs. settling time trade-off curve'),
        ('ch10', 'Disturbance rejection', 'Control response under step/impulse disturbances'),
        ('ch12', 'HIL architecture', 'System diagram showing plant server + controller client')
    ]

    print('High-priority diagrams to enhance understanding:')
    print('-' * 80)
    for ch, title, description in recommendations:
        print(f'[~] {ch}: "{title}"')
        print(f'    {description}')
    print()

def main():
    print()
    print('TEXTBOOK FIGURES ANALYSIS')
    print('=' * 80)
    print()

    chapter_refs, referenced_figures, available_figures, all_captions = analyze_figure_usage()

    print_usage_summary(chapter_refs, referenced_figures, available_figures)
    unused = identify_unused_figures(referenced_figures, available_figures)
    missing = identify_missing_figures(referenced_figures, available_figures)
    analyze_caption_quality(all_captions)
    recommend_missing_diagrams()

    print('=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print(f'Unused figures: {len(unused)}')
    print(f'Missing figures: {len(missing)}')
    print(f'Coverage: {len(referenced_figures)}/{len(referenced_figures)+len(unused)} ({len(referenced_figures)/(len(referenced_figures)+len(unused))*100:.1f}%)')
    print()
    print('[OK] Analysis complete.')
    print()

if __name__ == '__main__':
    main()
