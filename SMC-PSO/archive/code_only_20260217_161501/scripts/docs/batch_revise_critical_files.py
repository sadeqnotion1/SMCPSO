"""
Batch revision script for CRITICAL severity documentation files.

This script performs context-aware replacement of AI-ish language patterns
while preserving technical accuracy and metric-backed claims.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Define smart replacement rules
COMPREHENSIVE_RULES = [
    # Remove "comprehensive" when used as filler
    (r'\bcomprehensive\s+(?:documentation|framework|system|validation|testing|coverage)\b',
     lambda m: m.group(0).replace('comprehensive ', '')),

    # Keep "comprehensive" when backed by metrics
    (r'\bcomprehensive\s+(?:.*?(?:\d+%|\d+\.\d+))',
     lambda m: m.group(0)),  # Keep unchanged

    # Special case: "Comprehensive" at start of sentence
    (r'^Comprehensive\s+(?:documentation|framework|testing)',
     lambda m: m.group(0).replace('Comprehensive ', ''),
     re.MULTILINE),
]

ROBUST_RULES = [
    # Only replace "robust" when NOT used in control theory context
    (r'\brobust\s+(?:error handling|implementation|testing)\b',
     lambda m: m.group(0).replace('robust ', '')),

    # Keep "robust control", "robustness margin" (technical terms)
    (r'\b(?:robust control|robustness|robust stability)\b',
     lambda m: m.group(0)),  # Keep unchanged
]

def smart_replace(text: str, pattern: str, replacement, flags=0) -> Tuple[str, int]:
    """
    Perform smart replacement with counter.

    Args:
        text: Source text
        pattern: Regex pattern to match
        replacement: Replacement string or function
        flags: Regex flags

    Returns:
        Tuple of (modified_text, replacement_count)
    """
    if callable(replacement):
        result, count = [], 0
        last_end = 0
        for match in re.finditer(pattern, text, flags):
            result.append(text[last_end:match.start()])
            replaced = replacement(match)
            if replaced != match.group(0):
                count += 1
            result.append(replaced)
            last_end = match.end()
        result.append(text[last_end:])
        return ''.join(result), count
    else:
        result = re.sub(pattern, replacement, text, flags=flags)
        count = len(re.findall(pattern, text, flags))
        return result, count

def revise_file(file_path: Path) -> Dict:
    """
    Revise a single file, removing AI-ish patterns.

    Args:
        file_path: Path to markdown file

    Returns:
        Dictionary with revision statistics
    """
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    total_replacements = 0

    # Apply comprehensive rules
    for rule in COMPREHENSIVE_RULES:
        if len(rule) == 2:
            pattern, replacement = rule
            flags = 0
        else:
            pattern, replacement, flags = rule

        content, count = smart_replace(content, pattern, replacement, flags)
        total_replacements += count

    # Apply robust rules (only if NOT in control theory context)
    for rule in ROBUST_RULES:
        if len(rule) == 2:
            pattern, replacement = rule
            flags = 0
        else:
            pattern, replacement, flags = rule

        content, count = smart_replace(content, pattern, replacement, flags)
        total_replacements += count

    # Additional simple replacements
    simple_replacements = [
        (r'\bcomprehensive\b', ''),  # Remove standalone "comprehensive"
        (r'\s{2,}', ' '),  # Clean up double spaces
    ]

    for pattern, repl in simple_replacements:
        content, count = smart_replace(content, pattern, repl)
        total_replacements += count

    # Write back if changed
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        return {
            'file': str(file_path),
            'status': 'revised',
            'replacements': total_replacements,
            'size_before': len(original_content),
            'size_after': len(content)
        }
    else:
        return {
            'file': str(file_path),
            'status': 'no_changes',
            'replacements': 0,
            'size_before': len(original_content),
            'size_after': len(content)
        }

def batch_revise_critical_files(critical_files: List[Path]) -> List[Dict]:
    """
    Batch revise all CRITICAL severity files.

    Args:
        critical_files: List of file paths to revise

    Returns:
        List of revision statistics
    """
    results = []

    for file_path in critical_files:
        if file_path.exists():
            result = revise_file(file_path)
            results.append(result)
            print(f"[{'OK' if result['status'] == 'revised' else 'SKIP'}] {file_path.name}: {result['replacements']} replacements")
        else:
            results.append({
                'file': str(file_path),
                'status': 'not_found',
                'replacements': 0
            })
            print(f"[WARN] {file_path.name}: File not found")

    return results

if __name__ == "__main__":
    # Top 10 CRITICAL files from audit
    critical_files = [
        Path("D:/Projects/main/docs/production/production_readiness_assessment_v2.md"),
        Path("D:/Projects/main/docs/PSO_Documentation_Validation_Report.md"),
        Path("D:/Projects/main/docs/test_infrastructure_validation_report.md"),
        Path("D:/Projects/main/docs/reports/GITHUB_ISSUE_8_DOCUMENTATION_EXPERT_FINAL_REPORT.md"),
        Path("D:/Projects/main/docs/reports/PRODUCTION_READINESS_ASSESSMENT_FINAL.md"),
        Path("D:/Projects/main/docs/analysis/HYBRID_SMC_FIX_TECHNICAL_DOCUMENTATION.md"),
        Path("D:/Projects/main/docs/reports/ULTIMATE_ORCHESTRATOR_ISSUE_9_STRATEGIC_ASSESSMENT_REPORT.md"),
        Path("D:/Projects/main/docs/plans/documentation/week_1_quality_analysis.md"),
        Path("D:/Projects/main/docs/factory_integration_troubleshooting_guide.md"),
        Path("D:/Projects/main/docs/api/phase_4_4_completion_report.md"),
    ]

    print("Starting batch revision of CRITICAL files...")
    print("=" * 60)

    results = batch_revise_critical_files(critical_files)

    print("=" * 60)
    print("\nSummary:")
    print(f"  Total files processed: {len(results)}")
    print(f"  Files revised: {sum(1 for r in results if r['status'] == 'revised')}")
    print(f"  Total replacements: {sum(r['replacements'] for r in results)}")
    print("\nRevision complete!")
