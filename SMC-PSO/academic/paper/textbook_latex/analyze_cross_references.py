"""
Analyze cross-reference coverage between chapters.

Creates a matrix showing which chapters reference which, identifies gaps,
and suggests logical connections based on content relationships.
"""

import re
from pathlib import Path
from collections import defaultdict

# Chapter metadata
CHAPTERS = {
    'ch01': 'Introduction',
    'ch02': 'Mathematical Foundations',
    'ch03': 'Classical SMC',
    'ch04': 'Super-Twisting Algorithm',
    'ch05': 'Adaptive SMC',
    'ch06': 'Hybrid Adaptive STA-SMC',
    'ch07': 'PSO Theory',
    'ch08': 'Benchmarking Methodology',
    'ch09': 'PSO Optimization Results',
    'ch10': 'Advanced Topics',
    'ch11': 'Future Directions',
    'ch12': 'Case Studies and Applications'
}

# Mapping from label names to chapter numbers (extracted from \label{ch:...} in each chapter)
LABEL_TO_CHAPTER = {
    'ch:introduction': 'ch01',
    'ch:mathematical_foundations': 'ch02',
    'ch:classical_smc': 'ch03',
    'ch:super_twisting': 'ch04',
    'ch:adaptive_smc': 'ch05',
    'ch:hybrid_smc': 'ch06',
    'ch:pso': 'ch07',
    'ch:benchmarking': 'ch08',
    'ch:pso_results': 'ch09',
    'ch:advanced_topics': 'ch10',
    'ch:software': 'ch11',
    'ch:case_studies': 'ch12'
}

# Content-based relationships for gap detection
LOGICAL_CONNECTIONS = {
    'ch02': ['ch03', 'ch04', 'ch05'],  # Math foundations needed for all SMC
    'ch03': ['ch04', 'ch05', 'ch06'],  # Classical SMC is basis for variants
    'ch04': ['ch06'],  # STA used in hybrid
    'ch05': ['ch06'],  # Adaptive used in hybrid
    'ch06': ['ch08', 'ch12'],  # Hybrid results shown in benchmarks/case studies
    'ch07': ['ch09'],  # PSO theory implemented in results
    'ch08': ['ch09', 'ch12'],  # Benchmarking used in PSO results and case studies
    'ch09': ['ch12'],  # PSO results referenced in case studies
    'ch10': ['ch11'],  # Advanced topics lead to future work
}

def extract_chapter_references(tex_file):
    r"""Extract all \cref{ch:*} and \Cref{ch:*} references from a chapter."""
    content = tex_file.read_text(encoding='utf-8')

    # Match \cref{ch:label} or \Cref{ch:label}
    pattern = r'\\[Cc]ref\{(ch:[^}]+)\}'
    matches = re.findall(pattern, content)

    return matches

def build_reference_matrix():
    """Build a matrix showing which chapters reference which."""
    source_dir = Path('source/chapters')

    matrix = defaultdict(set)

    for tex_file in sorted(source_dir.glob('ch*.tex')):
        chapter_id = tex_file.stem  # e.g., 'ch03_classical_smc'
        chapter_num = chapter_id[:4]  # Get 'ch03' part

        refs = extract_chapter_references(tex_file)

        for ref_label in refs:
            # Convert label (e.g., 'ch:classical_smc') to chapter number (e.g., 'ch03')
            if ref_label in LABEL_TO_CHAPTER:
                ref_num = LABEL_TO_CHAPTER[ref_label]
                if ref_num in CHAPTERS:
                    matrix[chapter_num].add(ref_num)

    return matrix

def print_reference_matrix(matrix):
    """Print a visual matrix of cross-references."""
    print('=' * 80)
    print('CROSS-REFERENCE MATRIX')
    print('=' * 80)
    print()
    print('Format: Chapter X -> [Chapters referenced by X]')
    print()

    total_refs = 0
    for ch_num in sorted(CHAPTERS.keys()):
        refs = sorted(matrix.get(ch_num, []))
        ref_count = len(refs)
        total_refs += ref_count

        status = '[OK]' if ref_count >= 2 else '[LOW]' if ref_count == 1 else '[NONE]'

        print(f'{status} {ch_num} ({CHAPTERS[ch_num]})')
        if refs:
            print(f'     -> {", ".join(refs)}')
        else:
            print('     -> (no references)')
        print()

    print(f'Total cross-references: {total_refs}')
    print(f'Average references per chapter: {total_refs/len(CHAPTERS):.1f}')
    print()

def identify_gaps(matrix):
    """Identify missing cross-references based on logical connections."""
    print('=' * 80)
    print('GAP ANALYSIS - RECOMMENDED ADDITIONS')
    print('=' * 80)
    print()

    high_priority = []
    medium_priority = []

    for source, expected_targets in LOGICAL_CONNECTIONS.items():
        actual_refs = matrix.get(source, set())

        for target in expected_targets:
            if target not in actual_refs:
                # Determine priority
                if source in ['ch03', 'ch06', 'ch08']:  # Core chapters
                    high_priority.append((source, target, CHAPTERS[source], CHAPTERS[target]))
                else:
                    medium_priority.append((source, target, CHAPTERS[source], CHAPTERS[target]))

    if high_priority:
        print('HIGH PRIORITY (Core chapters missing key connections):')
        print('-' * 80)
        for src, tgt, src_name, tgt_name in high_priority:
            print(f'  [!] {src} ({src_name}) -> {tgt} ({tgt_name})')
        print()
    else:
        print('[OK] No high-priority gaps')
        print()

    if medium_priority:
        print('MEDIUM PRIORITY (Recommended for completeness):')
        print('-' * 80)
        for src, tgt, src_name, tgt_name in medium_priority:
            print(f'  [~] {src} ({src_name}) -> {tgt} ({tgt_name})')
        print()
    else:
        print('[OK] No medium-priority gaps')
        print()

def analyze_backward_references(matrix):
    """Find chapters that are never referenced by others."""
    print('=' * 80)
    print('BACKWARD REFERENCE ANALYSIS')
    print('=' * 80)
    print()

    referenced = set()
    for refs in matrix.values():
        referenced.update(refs)

    never_referenced = []
    rarely_referenced = []

    for ch_num in CHAPTERS.keys():
        ref_count = sum(1 for refs in matrix.values() if ch_num in refs)

        if ref_count == 0:
            never_referenced.append((ch_num, CHAPTERS[ch_num]))
        elif ref_count == 1:
            rarely_referenced.append((ch_num, CHAPTERS[ch_num], ref_count))

    if never_referenced:
        print('NEVER REFERENCED (Consider adding backward references):')
        print('-' * 80)
        for ch_num, ch_name in never_referenced:
            print(f'  [!] {ch_num} ({ch_name})')
        print()

    if rarely_referenced:
        print('RARELY REFERENCED (1 reference):')
        print('-' * 80)
        for ch_num, ch_name, count in rarely_referenced:
            print(f'  [~] {ch_num} ({ch_name})')
        print()

def main():
    print()
    print('TEXTBOOK CROSS-REFERENCE ANALYSIS')
    print('='  * 80)
    print()

    matrix = build_reference_matrix()

    print_reference_matrix(matrix)
    identify_gaps(matrix)
    analyze_backward_references(matrix)

    print('=' * 80)
    print('RECOMMENDATIONS')
    print('=' * 80)
    print()
    print('[ACTION] Add high-priority references first (core chapters)')
    print('[INFO] Medium-priority gaps can improve navigation but are optional')
    print('[OK] Analysis complete.')
    print()

if __name__ == '__main__':
    main()
