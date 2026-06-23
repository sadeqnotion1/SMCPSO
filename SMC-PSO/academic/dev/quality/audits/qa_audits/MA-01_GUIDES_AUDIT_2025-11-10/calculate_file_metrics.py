#!/usr/bin/env python
"""
MA-01 File Metrics Calculator
Analyzes a single file for completeness, accuracy, readability
Outputs: file_metrics.json
"""

import json
import re
from pathlib import Path
import sys

def calculate_flesch_reading_ease(text):
    """Calculate Flesch Reading Ease score"""
    # Remove code blocks
    text_no_code = re.sub(r'```[\s\S]*?```', '', text)
    text_no_code = re.sub(r'`[^`]+`', '', text_no_code)

    # Count sentences
    sentences = re.split(r'[.!?]+', text_no_code)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = len(sentences)

    if num_sentences == 0:
        return 0

    # Count words
    words = text_no_code.split()
    num_words = len(words)

    if num_words == 0:
        return 0

    # Count syllables (approximation)
    def count_syllables(word):
        word = word.lower()
        count = 0
        vowels = 'aeiouy'
        previous_was_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel
        if word.endswith('e'):
            count -= 1
        if count == 0:
            count = 1
        return count

    num_syllables = sum(count_syllables(word) for word in words)

    # Flesch Reading Ease = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    avg_words_per_sentence = num_words / num_sentences
    avg_syllables_per_word = num_syllables / num_words
    flesch = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)

    return round(flesch, 1)

def analyze_file(file_path):
    """Analyze a single file and return metrics"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    metrics = {
        "file": str(file_path),
        "completeness": {},
        "accuracy": {},
        "readability": {},
        "overall": 0
    }

    # === COMPLETENESS ANALYSIS (0-100) ===
    completeness_score = 0

    # Has H1 title (10 points)
    h1_pattern = r'^# [^#]'
    has_h1 = any(re.match(h1_pattern, line) for line in lines)
    metrics["completeness"]["has_h1_title"] = has_h1
    if has_h1:
        completeness_score += 10

    # Has introduction/overview (15 points)
    # Look for patterns like "## Overview", "## Introduction", or first paragraph after title
    intro_patterns = [r'## (Overview|Introduction|About|Summary)', r'^[A-Z].*paragraph after H1']
    has_intro = any(re.search(pattern, content, re.IGNORECASE | re.MULTILINE) for pattern in intro_patterns)
    # Also check if first 500 chars have substantive content
    if len(content) > 100 and not content[:500].count('#') > 3:
        has_intro = True
    metrics["completeness"]["has_introduction"] = has_intro
    if has_intro:
        completeness_score += 15

    # Has main content sections (30 points)
    # Count H2 headings (should have at least 2)
    h2_count = len(re.findall(r'^## [^#]', content, re.MULTILINE))
    metrics["completeness"]["h2_section_count"] = h2_count
    if h2_count >= 4:
        completeness_score += 30
    elif h2_count >= 2:
        completeness_score += 20
    elif h2_count >= 1:
        completeness_score += 10

    # Has examples (20 points)
    # Look for code blocks or "Example" sections
    code_blocks = len(re.findall(r'```', content))
    example_sections = len(re.findall(r'## .*[Ee]xample', content))
    has_examples = (code_blocks >= 2) or (example_sections >= 1)
    metrics["completeness"]["has_examples"] = has_examples
    metrics["completeness"]["code_block_count"] = code_blocks // 2  # Pairs
    if has_examples:
        if code_blocks >= 4 or example_sections >= 2:
            completeness_score += 20
        else:
            completeness_score += 10

    # Has summary/conclusion (10 points)
    summary_patterns = [r'## (Summary|Conclusion|Next Steps|References)', r'---\n\n## ']
    has_summary = any(re.search(pattern, content, re.IGNORECASE | re.MULTILINE) for pattern in summary_patterns)
    metrics["completeness"]["has_summary"] = has_summary
    if has_summary:
        completeness_score += 10

    # Has navigation links (15 points)
    # Look for links to other docs or "See also" sections
    link_count = len(re.findall(r'\[.*?\]\(.*?\)', content))
    see_also = re.search(r'## (See Also|Related|Next|Previous)', content, re.IGNORECASE)
    has_navigation = (link_count >= 3) or see_also
    metrics["completeness"]["has_navigation"] = has_navigation
    metrics["completeness"]["link_count"] = link_count
    if has_navigation:
        if link_count >= 5 or see_also:
            completeness_score += 15
        else:
            completeness_score += 8

    metrics["completeness"]["score"] = completeness_score

    # === ACCURACY ANALYSIS (0-100) ===
    accuracy_score = 0

    # Code blocks have language tags (20 points)
    code_block_pattern = r'```(\w*)\n'
    code_blocks_all = re.findall(code_block_pattern, content)
    code_blocks_tagged = [cb for cb in code_blocks_all if cb]
    if code_blocks_all:
        tag_ratio = len(code_blocks_tagged) / len(code_blocks_all)
        metrics["accuracy"]["code_blocks_with_tags"] = len(code_blocks_tagged)
        metrics["accuracy"]["code_blocks_total"] = len(code_blocks_all)
        accuracy_score += int(tag_ratio * 20)
    else:
        metrics["accuracy"]["code_blocks_with_tags"] = 0
        metrics["accuracy"]["code_blocks_total"] = 0
        accuracy_score += 20  # No code blocks = no violations

    # File paths exist (30 points)
    # Extract file paths from content
    path_patterns = [
        r'`(docs/[^`]+\.md)`',
        r'`(src/[^`]+\.py)`',
        r'\]\((docs/[^\)]+\.md)\)',
        r'\]\((src/[^\)]+\.py)\)'
    ]
    all_paths = []
    for pattern in path_patterns:
        all_paths.extend(re.findall(pattern, content))

    existing_paths = 0
    for path in all_paths:
        if Path(path).exists():
            existing_paths += 1

    if all_paths:
        path_ratio = existing_paths / len(all_paths)
        metrics["accuracy"]["valid_file_paths"] = existing_paths
        metrics["accuracy"]["total_file_paths"] = len(all_paths)
        accuracy_score += int(path_ratio * 30)
    else:
        metrics["accuracy"]["valid_file_paths"] = 0
        metrics["accuracy"]["total_file_paths"] = 0
        accuracy_score += 30  # No paths = no violations

    # Commands are syntactically valid (30 points)
    # Check bash/python code blocks for obvious syntax errors
    bash_blocks = re.findall(r'```(?:bash|sh)\n(.*?)```', content, re.DOTALL)
    python_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)

    # Simple validation: check for common issues
    invalid_commands = 0
    total_commands = len(bash_blocks) + len(python_blocks)

    for block in bash_blocks:
        # Check for unbalanced quotes, unclosed backticks
        if block.count('"') % 2 != 0 or block.count("'") % 2 != 0:
            invalid_commands += 1

    for block in python_blocks:
        # Check for unbalanced parentheses
        if block.count('(') != block.count(')'):
            invalid_commands += 1

    if total_commands > 0:
        valid_ratio = (total_commands - invalid_commands) / total_commands
        metrics["accuracy"]["valid_commands"] = total_commands - invalid_commands
        metrics["accuracy"]["total_commands"] = total_commands
        accuracy_score += int(valid_ratio * 30)
    else:
        metrics["accuracy"]["valid_commands"] = 0
        metrics["accuracy"]["total_commands"] = 0
        accuracy_score += 30  # No commands = no violations

    # No TODO/FIXME/TBD markers (10 points)
    todo_markers = len(re.findall(r'\b(TODO|FIXME|TBD|XXX)\b', content, re.IGNORECASE))
    metrics["accuracy"]["todo_markers"] = todo_markers
    if todo_markers == 0:
        accuracy_score += 10
    elif todo_markers <= 2:
        accuracy_score += 5

    # Version info matches current (10 points)
    # For now, just check if version numbers are present and not obviously old
    old_versions = len(re.findall(r'v?0\.\d+|version 0\.\d+', content, re.IGNORECASE))
    metrics["accuracy"]["old_version_references"] = old_versions
    if old_versions == 0:
        accuracy_score += 10
    elif old_versions <= 1:
        accuracy_score += 5

    metrics["accuracy"]["score"] = accuracy_score

    # === READABILITY ANALYSIS (0-100) ===
    readability_score = 0

    # Flesch Reading Ease 60-70 (30 points)
    flesch = calculate_flesch_reading_ease(content)
    metrics["readability"]["flesch_reading_ease"] = flesch
    if 60 <= flesch <= 70:
        readability_score += 30
    elif 50 <= flesch <= 80:
        readability_score += 25
    elif 40 <= flesch <= 90:
        readability_score += 20
    else:
        readability_score += 10

    # Average sentence length <25 words (20 points)
    text_no_code = re.sub(r'```[\s\S]*?```', '', content)
    sentences = re.split(r'[.!?]+', text_no_code)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) > 2]

    if sentences:
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        metrics["readability"]["avg_sentence_length"] = round(avg_sentence_length, 1)
        if avg_sentence_length < 20:
            readability_score += 20
        elif avg_sentence_length < 25:
            readability_score += 15
        elif avg_sentence_length < 30:
            readability_score += 10
        else:
            readability_score += 5
    else:
        metrics["readability"]["avg_sentence_length"] = 0
        readability_score += 20

    # Paragraph length <5 sentences (20 points)
    paragraphs = re.split(r'\n\n+', text_no_code)
    paragraphs = [p for p in paragraphs if p.strip() and not p.strip().startswith('#')]

    if paragraphs:
        para_lengths = []
        for para in paragraphs:
            para_sentences = re.split(r'[.!?]+', para)
            para_sentences = [s for s in para_sentences if s.strip()]
            para_lengths.append(len(para_sentences))
        avg_para_length = sum(para_lengths) / len(para_lengths)
        metrics["readability"]["avg_paragraph_sentences"] = round(avg_para_length, 1)
        if avg_para_length < 4:
            readability_score += 20
        elif avg_para_length < 5:
            readability_score += 15
        elif avg_para_length < 6:
            readability_score += 10
        else:
            readability_score += 5
    else:
        metrics["readability"]["avg_paragraph_sentences"] = 0
        readability_score += 20

    # Headings clear and descriptive (15 points)
    # Check if headings are not too short or too long
    headings = re.findall(r'^#{1,6} (.+)$', content, re.MULTILINE)
    if headings:
        heading_lengths = [len(h.split()) for h in headings]
        avg_heading_length = sum(heading_lengths) / len(heading_lengths)
        short_headings = sum(1 for h in heading_lengths if h < 2)
        long_headings = sum(1 for h in heading_lengths if h > 8)
        metrics["readability"]["avg_heading_words"] = round(avg_heading_length, 1)
        metrics["readability"]["headings_too_short"] = short_headings
        metrics["readability"]["headings_too_long"] = long_headings

        if short_headings == 0 and long_headings == 0:
            readability_score += 15
        elif short_headings <= 1 and long_headings <= 1:
            readability_score += 10
        else:
            readability_score += 5
    else:
        metrics["readability"]["avg_heading_words"] = 0
        readability_score += 15

    # Code-to-text ratio appropriate (15 points)
    total_chars = len(content)
    code_chars = sum(len(match.group(0)) for match in re.finditer(r'```[\s\S]*?```', content))
    if total_chars > 0:
        code_ratio = code_chars / total_chars
        metrics["readability"]["code_to_text_ratio"] = round(code_ratio, 2)
        # Ideal ratio depends on file type, but generally 10-40% is good
        if 0.10 <= code_ratio <= 0.40:
            readability_score += 15
        elif 0.05 <= code_ratio <= 0.50:
            readability_score += 10
        elif code_ratio < 0.60:
            readability_score += 5
        else:
            readability_score += 2
    else:
        metrics["readability"]["code_to_text_ratio"] = 0
        readability_score += 15

    metrics["readability"]["score"] = readability_score

    # === OVERALL SCORE ===
    metrics["overall"] = round((completeness_score + accuracy_score + readability_score) / 3, 1)

    return metrics

def main():
    if len(sys.argv) < 2:
        print("Usage: python calculate_file_metrics.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    metrics = analyze_file(file_path)

    # Print summary
    print(f"\n[OK] File: {file_path}")
    print(f"[OK] Overall Score: {metrics['overall']}/100")
    print(f"  - Completeness: {metrics['completeness']['score']}/100")
    print(f"  - Accuracy: {metrics['accuracy']['score']}/100")
    print(f"  - Readability: {metrics['readability']['score']}/100")

    # Save to JSON
    output_path = Path(".artifacts/qa_audits/MA-01_GUIDES_AUDIT_2025-11-10/file_metrics.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[OK] Metrics saved to: {output_path}")

    return metrics

if __name__ == "__main__":
    main()
