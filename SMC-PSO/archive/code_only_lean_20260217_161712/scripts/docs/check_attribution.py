#!/usr/bin/env python3
"""
Attribution Completeness Checker
=================================

Scans documentation for assertive claims without proper citations.

Usage:
    python scripts/docs/check_attribution.py

Output:
    - .artifacts/attribution_coverage_report.md
    - Console summary with statistics

Validation Criteria:
    - Technical claims should have citations within 2 sentences
    - Theorems/proofs must have immediate citations
    - Methodology descriptions should cite sources
    - "Well-known" results still need citations for academic rigor

Author: Claude Code
Date: 2025-10-09
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class UncitedClaim:
    """Represents a potentially uncited claim."""
    file: str
    line_num: int
    sentence: str
    claim_type: str
    severity: str  # "high", "medium", "low"
    context: str


def load_docs(docs_dir: Path) -> Dict[str, List[str]]:
    """Load all markdown documentation files."""
    docs = {}

    # Scan theory and API docs
    for pattern in ["docs/theory/**/*.md", "docs/api/**/*.md", "docs/user_guide/**/*.md"]:
        for md_file in Path(".").glob(pattern):
            if md_file.name.startswith("_"):
                continue  # Skip Sphinx build files

            with open(md_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            docs[str(md_file)] = lines

    return docs


def extract_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    # Simple sentence splitting (handles most cases)
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in sentences if s.strip()]


def has_nearby_citation(sentences: List[str], index: int, window: int = 2) -> bool:
    """Check if there's a citation within `window` sentences."""
    start = max(0, index - window)
    end = min(len(sentences), index + window + 1)

    for i in range(start, end):
        if "{cite}" in sentences[i] or r"\cite{" in sentences[i]:
            return True

    return False


def classify_claim_type(sentence: str) -> Tuple[str, str]:
    """
    Classify the type of claim and assign severity.

    Returns:
        (claim_type, severity)
    """
    sentence_lower = sentence.lower()

    # High severity: Technical claims requiring citation
    if any(keyword in sentence_lower for keyword in [
        "theorem", "proof", "lemma", "corollary", "proposition",
        "guarantees", "ensures", "converges to", "asymptotically stable"
    ]):
        return ("theorem_or_proof", "high")

    if any(keyword in sentence_lower for keyword in [
        "lyapunov", "sliding surface", "super-twisting", "finite-time",
        "exponentially stable", "boundary layer"
    ]):
        return ("technical_concept", "high")

    # Medium severity: Methodological claims
    if any(keyword in sentence_lower for keyword in [
        "algorithm", "method", "approach", "technique", "design",
        "parameter tuning", "optimization"
    ]):
        return ("methodology", "medium")

    # Medium severity: Quantitative assertions
    if re.search(r'\d+%|\d+\.\d+|factor of \d+', sentence_lower):
        return ("quantitative_claim", "medium")

    # Low severity: Implementation details
    if any(keyword in sentence_lower for keyword in [
        "implementation", "code", "python", "function", "class"
    ]):
        return ("implementation_detail", "low")

    # Default: General assertion
    if any(keyword in sentence for keyword in [
        " is ", " are ", " must ", " should ", " always ", " never ",
        " ensures ", " provides ", " achieves "
    ]):
        return ("general_assertion", "medium")

    return ("unknown", "low")


def is_citation_worthy(sentence: str) -> bool:
    """Determine if a sentence makes a claim that needs citation."""
    # Skip obvious non-claims
    if any(skip in sentence.lower() for skip in [
        "in this section", "we implement", "the following", "for example",
        "see figure", "as shown", "note that", "recall that"
    ]):
        return False

    # Skip code blocks and inline code
    if "`" in sentence or "```" in sentence:
        return False

    # Skip questions
    if sentence.strip().endswith("?"):
        return False

    # Check if it's an assertive claim
    claim_type, _ = classify_claim_type(sentence)
    return claim_type != "unknown"


def check_file_attribution(file_path: str, lines: List[str]) -> List[UncitedClaim]:
    """Check a single file for uncited claims."""
    uncited = []

    # Join lines into text, preserving line numbers
    text_with_lines = []
    for i, line in enumerate(lines, 1):
        if not line.strip().startswith("#"):  # Skip headers
            text_with_lines.append((i, line.strip()))

    # Group into paragraphs
    paragraphs = []
    current_para = []
    current_lines = []

    for line_num, text in text_with_lines:
        if text:
            current_para.append(text)
            current_lines.append(line_num)
        else:
            if current_para:
                paragraphs.append((" ".join(current_para), current_lines[0]))
                current_para = []
                current_lines = []

    if current_para:
        paragraphs.append((" ".join(current_para), current_lines[0]))

    # Check each paragraph
    for para_text, start_line in paragraphs:
        sentences = extract_sentences(para_text)

        for i, sentence in enumerate(sentences):
            if is_citation_worthy(sentence):
                if not has_nearby_citation(sentences, i, window=2):
                    claim_type, severity = classify_claim_type(sentence)

                    # Get context (surrounding sentences)
                    context_start = max(0, i - 1)
                    context_end = min(len(sentences), i + 2)
                    context = " ".join(sentences[context_start:context_end])

                    uncited.append(UncitedClaim(
                        file=file_path,
                        line_num=start_line,
                        sentence=sentence,
                        claim_type=claim_type,
                        severity=severity,
                        context=context
                    ))

    return uncited


def generate_report(uncited_claims: List[UncitedClaim], output_path: Path) -> None:
    """Generate attribution coverage report."""
    # Sort by severity and file
    severity_order = {"high": 0, "medium": 1, "low": 2}
    uncited_claims.sort(key=lambda c: (severity_order[c.severity], c.file, c.line_num))

    # Group by file
    by_file = {}
    for claim in uncited_claims:
        if claim.file not in by_file:
            by_file[claim.file] = []
        by_file[claim.file].append(claim)

    # Count by severity
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for claim in uncited_claims:
        severity_counts[claim.severity] += 1

    # Write report
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Attribution Completeness Report\n\n")
        f.write("**Generated:** 2025-10-09\n\n")
        f.write("---\n\n")

        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"**Total Uncited Claims:** {len(uncited_claims)}\n\n")
        f.write("| Severity | Count | Percentage |\n")
        f.write("|----------|-------|-----------|\n")
        total = len(uncited_claims) if uncited_claims else 1
        for severity in ["high", "medium", "low"]:
            count = severity_counts[severity]
            pct = (count / total) * 100
            f.write(f"| {severity.upper()} | {count} | {pct:.1f}% |\n")

        f.write("\n---\n\n")

        # Assessment
        if severity_counts["high"] == 0:
            f.write("## ✅ PASS: No High-Severity Uncited Claims\n\n")
            f.write("All critical technical claims (theorems, proofs, stability assertions) have proper citations.\n\n")
        else:
            f.write("## ⚠️ ACTION REQUIRED: High-Severity Uncited Claims Found\n\n")
            f.write(f"Found {severity_counts['high']} high-severity claims without citations.\n")
            f.write("These must be addressed before publication.\n\n")

        f.write("---\n\n")

        # Detailed Findings by File
        f.write("## Detailed Findings\n\n")

        for file_path, claims in by_file.items():
            f.write(f"### {file_path}\n\n")
            f.write(f"**Total claims:** {len(claims)}\n\n")

            # Group by severity
            for severity in ["high", "medium", "low"]:
                severity_claims = [c for c in claims if c.severity == severity]
                if not severity_claims:
                    continue

                f.write(f"#### {severity.upper()} Severity ({len(severity_claims)} claims)\n\n")

                for claim in severity_claims:
                    f.write(f"**Line {claim.line_num}** - `{claim.claim_type}`\n\n")
                    f.write(f"> {claim.sentence}\n\n")
                    f.write(f"**Context:**\n> {claim.context}\n\n")
                    f.write("**Recommendation:** Add citation or rephrase as implementation detail.\n\n")
                    f.write("---\n\n")

        # Recommendations
        f.write("## Recommendations\n\n")
        f.write("### For High-Severity Claims\n")
        f.write("1. Add citations to authoritative sources (textbooks, papers)\n")
        f.write("2. If original contribution, mark explicitly as \"our approach\"\n")
        f.write("3. Move implementation-specific details to code comments\n\n")

        f.write("### For Medium-Severity Claims\n")
        f.write("1. Add citations for methodological claims\n")
        f.write("2. Cite sources for quantitative assertions\n")
        f.write("3. Reference standard practices if applicable\n\n")

        f.write("### For Low-Severity Claims\n")
        f.write("1. Review for citation opportunities\n")
        f.write("2. Consider moving to implementation guides\n")
        f.write("3. Low priority for immediate action\n\n")

        # Validation Criteria
        f.write("---\n\n")
        f.write("## Validation Criteria\n\n")
        f.write("- [{}] Zero high-severity uncited claims\n".format(
            "PASS" if severity_counts["high"] == 0 else "FAIL"
        ))
        f.write("- [{}] < 5 medium-severity uncited claims per document\n".format(
            "PASS" if all(
                len([c for c in claims if c.severity == "medium"]) < 5
                for claims in by_file.values()
            ) else "WARN"
        ))
        f.write("- [INFO] Low-severity claims tracked for optional improvement\n\n")


def main():
    """Main entry point."""
    print("Attribution Completeness Checker")
    print("=" * 50)
    print()

    # Load documentation files
    print("[1/4] Loading documentation files...")
    docs = load_docs(Path("."))
    print(f"      Loaded {len(docs)} documentation files")

    # Check each file
    print("[2/4] Analyzing assertions and citations...")
    all_uncited = []

    for file_path, lines in docs.items():
        uncited = check_file_attribution(file_path, lines)
        all_uncited.extend(uncited)
        if uncited:
            print(f"      {file_path}: {len(uncited)} uncited claims")

    print(f"      Total uncited claims found: {len(all_uncited)}")

    # Generate report
    print("[3/4] Generating attribution report...")
    output_path = Path(".artifacts/attribution_coverage_report.md")
    generate_report(all_uncited, output_path)
    print(f"      Report saved to: {output_path}")

    # Summary statistics
    print("[4/4] Summary Statistics")
    print()

    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for claim in all_uncited:
        severity_counts[claim.severity] += 1

    print(f"      High-severity:   {severity_counts['high']}")
    print(f"      Medium-severity: {severity_counts['medium']}")
    print(f"      Low-severity:    {severity_counts['low']}")
    print()

    # Validation status
    if severity_counts["high"] == 0:
        print("✅ PASS: No high-severity uncited claims")
    else:
        print(f"⚠️  FAIL: {severity_counts['high']} high-severity claims need citations")

    print()
    print(f"Full report: {output_path}")
    print()


if __name__ == "__main__":
    main()
