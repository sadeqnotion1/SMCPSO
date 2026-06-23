#!/usr/bin/env python3
"""
Generate minimal audit prompt for manual copy/paste into Gemini CLI
No external dependencies required (no jq needed)

Usage:
    python generate_audit_prompt.py <section_number>

Example:
    python generate_audit_prompt.py 1   # Section 01: Introduction
    python generate_audit_prompt.py 5   # Section 05: Lyapunov Stability
"""

import json
import sys
import os

def print_usage():
    print("Usage: python generate_audit_prompt.py <section_number>")
    print("Example: python generate_audit_prompt.py 1  (for Section 01: Introduction)")
    print("")
    print("Available sections:")
    print("  1  - Introduction")
    print("  2  - List of Figures")
    print("  3  - System Model")
    print("  4  - Controller Design")
    print("  5  - Lyapunov Stability [PRIORITY]")
    print("  6  - PSO Methodology")
    print("  7  - Experimental Setup")
    print("  8  - Performance Results [PRIORITY]")
    print("  9  - Robustness Analysis [PRIORITY]")
    print("  10 - Discussion")
    print("  11 - Conclusion")
    print("  12 - Acknowledgments")

def main():
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    try:
        section_num_input = int(sys.argv[1])
        if section_num_input < 1 or section_num_input > 12:
            print("ERROR: Section number must be between 1 and 12")
            sys.exit(1)
    except ValueError:
        print("ERROR: Section number must be an integer")
        print_usage()
        sys.exit(1)

    # Calculate indices
    section_idx = section_num_input - 1
    section_num = f"{section_num_input:02d}"

    # Load audit config
    try:
        with open('audit_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("ERROR: audit_config.json not found")
        print("Make sure you're in the sections/ directory")
        sys.exit(1)

    # Get section metadata
    section = config['sections'][section_idx]
    section_name = section['section_name']
    md_file = section['markdown_file']
    prompt = section['audit_prompt']

    # Check if markdown file exists
    if not os.path.exists(md_file):
        print(f"ERROR: File not found: {md_file}")
        sys.exit(1)

    # Output file
    os.makedirs('audits', exist_ok=True)
    output_file = f"audits/Section_{section_num}_PROMPT.txt"

    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Generate combined prompt
    combined_prompt = f"""{'='*72}
COPY EVERYTHING BELOW THIS LINE
{'='*72}

{md_content}


{'━'*72}
AUDIT INSTRUCTIONS
{'━'*72}

{prompt}

{'='*72}
END OF PROMPT
{'='*72}
"""

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_prompt)

    # Print instructions
    print("="*72)
    print("AUDIT PROMPT GENERATOR")
    print(f"Section {section_num}: {section_name}")
    print("="*72)
    print("")
    print("[OK] Prompt generated successfully!")
    print(f"[INFO] File: {output_file}")
    print("")
    print("Next steps:")
    print(f"  1. Open: {output_file}")
    print("  2. Select all (Ctrl+A) and copy (Ctrl+C)")
    print("  3. Paste into Gemini CLI")
    print(f"  4. Save Gemini's response to: audits/Section_{section_num}_AUDIT_REPORT.md")
    print("")
    print("File stats:")
    file_size = os.path.getsize(output_file)
    line_count = combined_prompt.count('\n')
    print(f"  - Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"  - Lines: {line_count:,}")
    print("")

if __name__ == '__main__':
    main()
