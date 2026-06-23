"""LT-7 Reviewer Suggestion Script

Extracts author names from most-cited references and suggests expert reviewers
based on citation frequency and research domain.

Usage:
    python scripts/lt7_suggest_reviewers.py

Input:  benchmarks/LT7_CITATION_REPORT.md, benchmarks/LT7_RESEARCH_PAPER.md
Output: benchmarks/LT7_SUGGESTED_REVIEWERS.md
"""

import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

CITATION_REPORT = Path("benchmarks/LT7_CITATION_REPORT.md")
PAPER_FILE = Path("benchmarks/LT7_RESEARCH_PAPER.md")
OUTPUT_FILE = Path("benchmarks/LT7_SUGGESTED_REVIEWERS.md")

def extract_citation_counts() -> Dict[int, int]:
    """Extract citation usage counts from citation report."""
    with open(CITATION_REPORT, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find "Most Frequently Cited References" section
    pattern = r'\[(\d+)\]: (\d+) times'
    counts = {}

    for match in re.finditer(pattern, content):
        ref_num = int(match.group(1))
        count = int(match.group(2))
        counts[ref_num] = count

    return counts

def extract_references() -> Dict[int, str]:
    """Extract all references from markdown paper."""
    with open(PAPER_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    references = {}
    in_references = False
    current_ref_num = None
    current_ref_text = []

    for line in lines:
        if "## References" in line:
            in_references = True
            continue

        if in_references:
            if line.startswith("##") and "Appendix" in line:
                break

            match = re.match(r'^\[(\d+)\]\s+(.+)', line.strip())
            if match:
                if current_ref_num and current_ref_text:
                    references[current_ref_num] = ' '.join(current_ref_text).strip()

                current_ref_num = int(match.group(1))
                current_ref_text = [match.group(2)]
            elif current_ref_num and line.strip():
                current_ref_text.append(line.strip())

    if current_ref_num and current_ref_text:
        references[current_ref_num] = ' '.join(current_ref_text).strip()

    return references

def extract_primary_author(ref_text: str) -> Tuple[str, str]:
    """Extract first author name and affiliation hint from reference."""
    # Pattern: "FirstAuthor, ... et al." or "FirstAuthor and SecondAuthor"
    # Returns (last_name, full_author_string)

    # Try to get first author before comma or "and"
    match = re.match(r'^([^,]+?)(?:,|\s+and\s+|\s+et\s+al)', ref_text)
    if match:
        first_author = match.group(1).strip()

        # Try to extract last name (usually last word, might have initials)
        # Handle cases like "V. I. Utkin" or "J.-J. E. Slotine"
        parts = first_author.split()
        if parts:
            # Last part is usually the last name
            last_name = parts[-1].strip('.')
            return last_name, first_author

    return "Unknown", ref_text[:50]

def categorize_by_domain(references: Dict[int, str]) -> Dict[str, List[int]]:
    """Categorize references by research domain keywords."""
    domains = {
        'Higher-Order SMC / Super-Twisting': [12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
        'Adaptive Control': [22, 23, 24, 25, 26, 27, 28, 29],
        'PSO Optimization': [37, 38, 39, 40, 41, 42, 43, 44],
        'Inverted Pendulum / Underactuated Systems': [45, 46, 47, 48, 49, 50, 51, 52, 53],
        'Lyapunov Stability': [54, 55, 56, 57, 58, 59, 60],
        'Classical SMC Theory': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        'Hybrid / Switching Control': [30, 31, 32, 33, 34, 35, 36],
    }

    return domains

def suggest_reviewers(citation_counts: Dict[int, int], references: Dict[int, str]) -> List[Dict]:
    """Suggest top reviewers based on citation frequency and domain expertise."""
    domains = categorize_by_domain(references)

    suggested = []

    # Prioritize heavily cited authors
    sorted_refs = sorted(citation_counts.items(), key=lambda x: x[1], reverse=True)

    # Get top cited authors from different domains
    domain_coverage = set()

    for ref_num, count in sorted_refs[:20]:  # Top 20 most cited
        if ref_num not in references:
            continue

        ref_text = references[ref_num]
        last_name, full_author = extract_primary_author(ref_text)

        # Find which domain this reference belongs to
        ref_domain = None
        for domain, refs in domains.items():
            if ref_num in refs:
                ref_domain = domain
                break

        if not ref_domain:
            ref_domain = "Other"

        # Skip if we already have someone from this exact domain (diversity)
        if ref_domain in domain_coverage and len(suggested) >= 3:
            continue

        suggested.append({
            'ref_num': ref_num,
            'last_name': last_name,
            'full_author': full_author,
            'citation_count': count,
            'domain': ref_domain,
            'ref_text': ref_text[:150] + "..." if len(ref_text) > 150 else ref_text
        })

        domain_coverage.add(ref_domain)

        if len(suggested) >= 8:  # Suggest 8 reviewers (user picks 4-5)
            break

    return suggested

def generate_report(reviewers: List[Dict]) -> str:
    """Generate markdown report with suggested reviewers."""
    report = []
    report.append("# LT-7 SUGGESTED REVIEWERS\n")
    report.append("**Generated:** Auto-extracted from citation analysis")
    report.append("**Total Suggestions:** {}\n".format(len(reviewers)))
    report.append("---\n")

    report.append("## INSTRUCTIONS\n")
    report.append("1. Select 4-5 experts from the list below")
    report.append("2. Look up their current affiliation and email (Google Scholar, institution website)")
    report.append("3. Copy the template entries into LT7_COVER_LETTER.md")
    report.append("4. Replace placeholders with actual details\n")
    report.append("---\n")

    report.append("## SUGGESTED REVIEWERS\n")

    for i, reviewer in enumerate(reviewers, 1):
        report.append(f"### {i}. {reviewer['full_author']}")
        report.append(f"**Domain:** {reviewer['domain']}")
        report.append(f"**Cited:** {reviewer['citation_count']} times in paper (Ref [{reviewer['ref_num']}])")
        report.append(f"**Reference:** {reviewer['ref_text']}\n")

        report.append("**Template for Cover Letter:**")
        report.append("```markdown")
        report.append(f"{i}. **{reviewer['full_author']}** - Expert in {reviewer['domain'].lower()}")
        report.append("   - Affiliation: [LOOK UP ON GOOGLE SCHOLAR]")
        report.append("   - Email: [FIND ON INSTITUTION WEBSITE]")
        report.append(f"   - Relevant expertise: Cited {reviewer['citation_count']} times in our work ([{reviewer['ref_num']}])")
        report.append("```\n")

        report.append("**How to Find Details:**")
        report.append(f"1. Google Scholar: `{reviewer['full_author']} sliding mode control`")
        report.append(f"2. Check recent publications (2020-2025) for current affiliation")
        report.append(f"3. Visit institution website for official email\n")
        report.append("---\n")

    report.append("## DOMAIN COVERAGE\n")
    domains_covered = set(r['domain'] for r in reviewers)
    report.append(f"Suggested reviewers cover {len(domains_covered)} domains:\n")
    for domain in sorted(domains_covered):
        count = sum(1 for r in reviewers if r['domain'] == domain)
        report.append(f"- {domain}: {count} reviewer(s)")

    report.append("\n---\n")
    report.append("## ALTERNATIVE APPROACH\n")
    report.append("If any suggested reviewers have conflicts (collaborators, advisors, etc.):\n")
    report.append("1. Check LT7_CITATION_REPORT.md for next most-cited references")
    report.append("2. Look up authors from references [15-30]")
    report.append("3. Ensure reviewers are from different institutions")
    report.append("4. Avoid authors you've collaborated with in past 3 years\n")

    return '\n'.join(report)

def main():
    print("\n" + "="*70)
    print("LT-7 REVIEWER SUGGESTION")
    print("="*70 + "\n")

    print("[INFO] Loading citation counts...")
    citation_counts = extract_citation_counts()
    print(f"[OK] Found usage data for {len(citation_counts)} references")

    print("[INFO] Extracting references from paper...")
    references = extract_references()
    print(f"[OK] Extracted {len(references)} references")

    print("[INFO] Suggesting reviewers based on citation frequency...")
    reviewers = suggest_reviewers(citation_counts, references)
    print(f"[OK] Generated {len(reviewers)} reviewer suggestions")

    print("[INFO] Generating report...")
    report = generate_report(reviewers)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n[OK] Reviewer suggestions saved to: {OUTPUT_FILE}")

    print(f"\n[INFO] Top suggestions:")
    for i, reviewer in enumerate(reviewers[:5], 1):
        print(f"     {i}. {reviewer['full_author']} ({reviewer['domain']}) - cited {reviewer['citation_count']}x")

    print(f"\n[WARNING] Manual steps required:")
    print(f"     1. Look up current affiliations on Google Scholar")
    print(f"     2. Find official email addresses")
    print(f"     3. Verify no conflicts of interest")
    print(f"     4. Select 4-5 reviewers for cover letter")
    print()

if __name__ == "__main__":
    main()
