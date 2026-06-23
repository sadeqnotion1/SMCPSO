"""
Add Index Entries to Textbook Chapters
=====================================

Systematically adds \index{} commands throughout all chapters for key terms,
concepts, algorithms, and technical vocabulary.

Strategy:
- Add index entries at FIRST occurrence of each term in each chapter
- Use subentries for hierarchical organization (e.g., "SMC!classical")
- Avoid indexing within equations, captions, or comments
- Target: 200-300 total entries across 12 chapters (~17-25 per chapter)

Usage:
    python scripts/add_index_entries.py
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Set

# Master index term dictionary (term -> index entry)
# Format: "text to match" -> "index entry (with optional !subentry)"
INDEX_TERMS = {
    # Controllers
    "Sliding Mode Control": "sliding mode control",
    "SMC": "sliding mode control|see{SMC}",
    "classical SMC": "sliding mode control!classical",
    "Super-Twisting Algorithm": "Super-Twisting Algorithm",
    "STA": "Super-Twisting Algorithm|see{STA}",
    "adaptive SMC": "sliding mode control!adaptive",
    "hybrid adaptive": "sliding mode control!hybrid adaptive",

    # Underactuated systems
    "underactuated": "underactuated systems",
    "double-inverted pendulum": "double-inverted pendulum",
    "DIP": "double-inverted pendulum|see{DIP}",
    "cart-pole": "cart-pole system",
    "degrees of freedom": "degrees of freedom",

    # Mathematical concepts
    "Lyapunov": "Lyapunov stability",
    "sliding surface": "sliding surface",
    "reaching condition": "reaching condition",
    "Lagrangian": "Lagrangian mechanics",
    "inertia matrix": "inertia matrix",
    "Coriolis": "Coriolis forces",

    # Chattering
    "chattering": "chattering",
    "boundary layer": "boundary layer",
    "quasi-sliding mode": "quasi-sliding mode",

    # Optimization
    "Particle Swarm Optimization": "Particle Swarm Optimization",
    "PSO": "Particle Swarm Optimization|see{PSO}",
    "fitness function": "fitness function",
    "global best": "Particle Swarm Optimization!global best",
    "personal best": "Particle Swarm Optimization!personal best",
    "inertia weight": "Particle Swarm Optimization!inertia weight",
    "velocity update": "Particle Swarm Optimization!velocity update",

    # Performance metrics
    "settling time": "performance metrics!settling time",
    "steady-state error": "performance metrics!steady-state error",
    "overshoot": "performance metrics!overshoot",
    "energy consumption": "performance metrics!energy consumption",
    "control effort": "performance metrics!control effort",

    # Robustness
    "model uncertainty": "model uncertainty",
    "parameter variation": "parameter variation",
    "disturbance rejection": "disturbance rejection",
    "robustness": "robustness",

    # Research tasks
    "MT-6": "research tasks!MT-6",
    "MT-7": "research tasks!MT-7",
    "MT-8": "research tasks!MT-8",
    "LT-6": "research tasks!LT-6",
    "LT-7": "research tasks!LT-7",

    # Software/Implementation
    "Python": "Python implementation",
    "NumPy": "NumPy",
    "SciPy": "SciPy",
    "Numba": "Numba optimization",
    "Streamlit": "Streamlit",

    # Control theory
    "stability": "stability",
    "controllability": "controllability",
    "reachability": "reachability",
    "equilibrium": "equilibrium",
    "phase portrait": "phase portrait",

    # Physical parameters
    "generalized coordinates": "generalized coordinates",
    "state space": "state space",
    "control input": "control input",
    "gravitational force": "gravitational force",

    # Additional mathematical concepts (NEW)
    "Hamiltonian": "Hamiltonian mechanics",
    "Euler-Lagrange": "Euler-Lagrange equations",
    "Jacobian": "Jacobian matrix",
    "linearization": "linearization",
    "nonholonomic": "nonholonomic constraints",
    "passivity": "passivity-based control",
    "energy-based": "energy-based control",

    # Additional control concepts (NEW)
    "gain tuning": "gain tuning",
    "feedback": "feedback control",
    "feedforward": "feedforward control",
    "trajectory tracking": "trajectory tracking",
    "swing-up": "swing-up control",
    "stabilization": "stabilization",
    "region of attraction": "region of attraction",
    "Barbalat": "Barbalat's lemma",

    # Additional chattering mitigation (NEW)
    "saturation function": "saturation function",
    "sign function": "sign function",
    "smoothing": "smoothing techniques",
    "switching frequency": "switching frequency",

    # Additional PSO concepts (NEW)
    "swarm intelligence": "swarm intelligence",
    "convergence": "convergence",
    "exploration": "Particle Swarm Optimization!exploration",
    "exploitation": "Particle Swarm Optimization!exploitation",
    "local minima": "local minima",
    "global minimum": "global minimum",

    # Additional performance metrics (NEW)
    "rise time": "performance metrics!rise time",
    "peak time": "performance metrics!peak time",
    "tracking error": "performance metrics!tracking error",
    "control bandwidth": "performance metrics!bandwidth",

    # Additional implementation topics (NEW)
    "real-time": "real-time control",
    "simulation": "simulation",
    "hardware-in-the-loop": "hardware-in-the-loop",
    "Monte Carlo": "Monte Carlo simulation",
    "benchmarking": "benchmarking",

    # Additional robustness topics (NEW)
    "noise": "sensor noise",
    "uncertainty": "uncertainty",
    "perturbation": "perturbation",
    "worst-case": "worst-case analysis",
}


def find_chapter_files(base_dir: Path) -> List[Path]:
    """Find all chapter .tex files."""
    chapter_dir = base_dir / "source" / "chapters"
    return sorted(chapter_dir.glob("ch*.tex"))


def is_in_protected_context(text: str, pos: int) -> bool:
    """
    Check if position is inside a protected context where we shouldn't add index.

    Protected contexts:
    - Inside equations: \begin{equation}...\end{equation}, $ ... $, \[ ... \]
    - Inside captions: \caption{...}
    - Inside comments: % ...
    - Inside labels: \label{...}
    - Inside citations: \cite{...}
    """
    # Check if inside comment (from % to end of line before pos)
    line_start = text.rfind('\n', 0, pos)
    line_text = text[line_start:pos]
    if '%' in line_text:
        return True

    # Check if inside equation environment
    before_pos = text[:pos]

    # Count equation delimiters
    eq_begin_count = before_pos.count(r'\begin{equation}') + before_pos.count(r'\[')
    eq_end_count = before_pos.count(r'\end{equation}') + before_pos.count(r'\]')
    if eq_begin_count > eq_end_count:
        return True

    # Check if inside caption, label, or cite
    # Look for unclosed braces in \caption{, \label{, \cite{
    for cmd in [r'\caption{', r'\label{', r'\cite{', r'\cref{', r'\Cref{']:
        last_cmd = before_pos.rfind(cmd)
        if last_cmd != -1:
            # Count braces after command
            after_cmd = before_pos[last_cmd:]
            brace_count = after_cmd.count('{') - after_cmd.count('}')
            if brace_count > 0:  # Still inside the command
                return True

    return False


def add_index_to_chapter(chapter_path: Path, terms: Dict[str, str], dry_run: bool = False) -> Tuple[int, List[str]]:
    """
    Add index entries to a single chapter file.

    Returns:
        (num_added, list_of_added_terms)
    """
    text = chapter_path.read_text(encoding='utf-8')
    original_text = text

    added_terms = []
    num_added = 0

    # Track which terms we've already indexed in this chapter (avoid duplicates)
    indexed_terms: Set[str] = set()

    # Sort terms by length (longest first) to match more specific terms first
    sorted_terms = sorted(terms.items(), key=lambda x: len(x[0]), reverse=True)

    for term_text, index_entry in sorted_terms:
        # Skip if already indexed in this chapter
        if term_text in indexed_terms:
            continue

        # Find first occurrence of term (case-sensitive)
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(term_text) + r'\b'
        match = re.search(pattern, text)

        if match:
            pos = match.start()

            # Check if in protected context
            if is_in_protected_context(text, pos):
                continue

            # Add index entry immediately after the term
            # Format: "term\index{index entry}"
            insert_pos = match.end()
            index_cmd = f"\\index{{{index_entry}}}"

            text = text[:insert_pos] + index_cmd + text[insert_pos:]
            indexed_terms.add(term_text)
            added_terms.append(f"{term_text} -> {index_entry}")
            num_added += 1

    # Write modified text if not dry run and changes were made
    if not dry_run and text != original_text:
        chapter_path.write_text(text, encoding='utf-8')

    return num_added, added_terms


def main():
    """Main execution."""
    base_dir = Path(__file__).resolve().parents[1]  # Go up to textbook_latex/

    print("[INFO] Starting index entry generation")
    print(f"[INFO] Base directory: {base_dir}")
    print(f"[INFO] Total terms in dictionary: {len(INDEX_TERMS)}")
    print()

    # Find all chapter files
    chapter_files = find_chapter_files(base_dir)
    print(f"[INFO] Found {len(chapter_files)} chapter files")
    print()

    # Process each chapter
    total_added = 0
    chapter_summary = []

    for chapter_path in chapter_files:
        chapter_name = chapter_path.stem  # e.g., "ch01_introduction"
        print(f"[INFO] Processing {chapter_name}...")

        num_added, added_terms = add_index_to_chapter(chapter_path, INDEX_TERMS, dry_run=False)
        total_added += num_added

        chapter_summary.append((chapter_name, num_added))

        if num_added > 0:
            print(f"  [OK] Added {num_added} index entries")
            # Show first 5 terms added
            for term in added_terms[:5]:
                print(f"       - {term}")
            if len(added_terms) > 5:
                print(f"       ... and {len(added_terms) - 5} more")
        else:
            print(f"  [INFO] No new entries added (terms already indexed or not found)")
        print()

    # Print summary
    print("=" * 70)
    print("INDEX GENERATION SUMMARY")
    print("=" * 70)
    print(f"Total index entries added: {total_added}")
    print()
    print("Chapter breakdown:")
    for chapter, count in chapter_summary:
        print(f"  {chapter:30} {count:3} entries")
    print()
    print(f"[INFO] Target: 200-300 entries | Current: {total_added}")

    if total_added < 200:
        print(f"[WARNING] Below target by {200 - total_added} entries")
        print("[INFO] Consider expanding INDEX_TERMS dictionary")
    elif total_added > 300:
        print(f"[WARNING] Above target by {total_added - 300} entries")
    else:
        print("[OK] Within target range!")

    print()
    print("[INFO] Next step: Build index with 'makeindex main.idx'")


if __name__ == "__main__":
    main()
