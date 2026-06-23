#!/usr/bin/env python3
"""
extract_claims.py - Technical Claims Extraction Script

Extracts and categorizes all technical claims from thesis using Claude API:
- Theoretical claims (control theory, mathematics, proofs)
- Empirical claims (experimental results, performance)
- Design claims (controller architecture, implementation)
- Evidence identification (equations, figures, citations, experiments)
- Unsupported claim detection

Created: November 5, 2025
Priority: 3 (Quick Win - 80% automated)
Manual Work: 1 hour review (validate 30% of claims)
Cost: $5-10 (Claude API)

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python extract_claims.py [--config config.yaml] [--chapters all] [--output claims_audit.csv]

Requirements:
    pip install anthropic pyyaml
"""

import os
import sys
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
import yaml
from datetime import datetime


# Check if anthropic is available
try:
    import anthropic
except ImportError:
    print("[ERROR] anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)


@dataclass
class TechnicalClaim:
    """Represents a technical claim extracted from the thesis."""
    claim_id: str
    chapter: str
    section: str
    claim_text: str
    claim_type: str  # 'theoretical', 'empirical', 'design'
    evidence_type: str  # 'equation', 'figure', 'citation', 'experiment', 'derivation', 'none'
    evidence_location: str  # e.g., "Eq. 3.12", "Figure 4.3", "[Smith2023]"
    risk_level: str  # 'high', 'medium', 'low'
    validation_status: str = "pending"  # 'validated', 'questionable', 'rejected', 'pending'
    notes: str = ""


@dataclass
class ExtractionResult:
    """Results of claims extraction."""
    total_claims: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_evidence: Dict[str, int] = field(default_factory=dict)
    unsupported_claims: List[TechnicalClaim] = field(default_factory=list)
    high_risk_claims: List[TechnicalClaim] = field(default_factory=list)
    claims: List[TechnicalClaim] = field(default_factory=list)
    api_cost_estimate: float = 0.0


class ClaimsExtractor:
    """Extracts technical claims from thesis using Claude API."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize extractor with configuration."""
        self.config = self._load_config(config_path)
        self.thesis_path = Path(self.config['thesis']['base_path'])
        self.reports_path = Path(self.config['output']['reports_path'])

        # Initialize Claude API client
        api_key = os.environ.get(self.config['api']['anthropic']['api_key_env'])
        if not api_key:
            print(f"[ERROR] {self.config['api']['anthropic']['api_key_env']} not set")
            print("Set it with: export ANTHROPIC_API_KEY='sk-ant-...'")
            sys.exit(1)

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = self.config['api']['anthropic']['model']
        self.max_tokens = self.config['api']['anthropic']['max_tokens']

        # Cost tracking
        self.input_tokens = 0
        self.output_tokens = 0

        # Claim counter
        self.claim_counter = 0

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        config_file = Path(__file__).parent / config_path
        if not config_file.exists():
            print(f"[WARNING] Config not found: {config_file}, using defaults")
            return self._default_config()

        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _default_config(self) -> dict:
        """Return default configuration."""
        return {
            'thesis': {
                'base_path': 'docs/thesis',
                'chapters': [],
            },
            'output': {
                'reports_path': '.artifacts/thesis/reports',
                'verbose': True,
            },
            'api': {
                'anthropic': {
                    'api_key_env': 'ANTHROPIC_API_KEY',
                    'model': 'claude-3-5-sonnet-20241022',
                    'max_tokens': 4000,
                },
            },
        }

    def load_chapter(self, chapter_file: Path) -> Optional[str]:
        """Load chapter content."""
        try:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[ERROR] Cannot read {chapter_file}: {e}")
            return None

    def extract_chapter_number(self, file_path: Path) -> str:
        """Extract chapter number from filename."""
        match = re.match(r'(\d+)_', file_path.name)
        return match.group(1) if match else "00"

    def extract_claims_from_chapter(self, chapter_content: str, chapter_num: str, chapter_file: Path) -> List[TechnicalClaim]:
        """Extract claims from a single chapter using Claude API."""
        print(f"[INFO] Extracting claims from Chapter {chapter_num} ({chapter_file.name})...")

        # Prepare prompt for Claude
        prompt = f"""You are a technical thesis validator. Extract ALL technical claims from this thesis chapter.

For EACH claim, provide:
1. The exact claim text (verbatim, 1-2 sentences max)
2. Section number (e.g., "3.2", "4.1.3")
3. Claim type: 'theoretical' (control theory, math, proofs), 'empirical' (experimental results), or 'design' (architecture, implementation)
4. Evidence type: 'equation', 'figure', 'table', 'citation', 'experiment', 'derivation', or 'none'
5. Evidence location: specific reference (e.g., "Eq. 3.12", "Figure 4.3", "[Smith2023]", or "none")
6. Risk level: 'high' (novel claim, critical to thesis), 'medium' (standard claim), 'low' (common knowledge)

Format your response as JSON array:
[
  {{
    "claim_text": "exact claim here",
    "section": "3.2",
    "claim_type": "theoretical",
    "evidence_type": "equation",
    "evidence_location": "Eq. 3.12",
    "risk_level": "high"
  }},
  ...
]

IMPORTANT:
- Extract EVERY technical claim, no matter how small
- A "claim" is any assertion about properties, behavior, performance, correctness, etc.
- If evidence is implicit (e.g., "as shown in the derivation"), note it
- Flag unsupported claims (no evidence) as 'none'

Here is Chapter {chapter_num}:

{chapter_content[:20000]}
"""

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.0,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Track token usage
            self.input_tokens += response.usage.input_tokens
            self.output_tokens += response.usage.output_tokens

            # Parse response
            response_text = response.content[0].text

            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # Try to parse entire response as JSON
                json_text = response_text

            claims_data = json.loads(json_text)

            # Convert to TechnicalClaim objects
            claims = []
            for claim_dict in claims_data:
                self.claim_counter += 1
                claim = TechnicalClaim(
                    claim_id=f"TC-{self.claim_counter:03d}",
                    chapter=chapter_num,
                    section=claim_dict.get('section', ''),
                    claim_text=claim_dict.get('claim_text', ''),
                    claim_type=claim_dict.get('claim_type', 'unknown'),
                    evidence_type=claim_dict.get('evidence_type', 'none'),
                    evidence_location=claim_dict.get('evidence_location', 'none'),
                    risk_level=claim_dict.get('risk_level', 'medium'),
                )
                claims.append(claim)

            print(f"[INFO]   - Extracted {len(claims)} claims from Chapter {chapter_num}")
            return claims

        except anthropic.APIError as e:
            print(f"[ERROR] Claude API error: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse Claude response as JSON: {e}")
            print(f"[DEBUG] Response: {response_text[:500]}")
            return []
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return []

    def extract_all_claims(self, chapters: str = "all") -> ExtractionResult:
        """Extract claims from specified chapters."""
        result = ExtractionResult()

        # Get chapter files
        if chapters == "all":
            chapter_files = sorted(self.thesis_path.glob("[0-9][0-9]_*.md"))
        else:
            chapter_nums = chapters.split(',')
            chapter_files = []
            for num in chapter_nums:
                matching = list(self.thesis_path.glob(f"{num.zfill(2)}_*.md"))
                chapter_files.extend(matching)

        if not chapter_files:
            print(f"[ERROR] No chapter files found in {self.thesis_path}")
            return result

        print(f"[INFO] Found {len(chapter_files)} chapter files")

        # Extract claims from each chapter
        for chapter_file in chapter_files:
            content = self.load_chapter(chapter_file)
            if not content:
                continue

            chapter_num = self.extract_chapter_number(chapter_file)
            claims = self.extract_claims_from_chapter(content, chapter_num, chapter_file)
            result.claims.extend(claims)

        # Compute statistics
        result.total_claims = len(result.claims)

        result.by_type = {
            'theoretical': sum(1 for c in result.claims if c.claim_type == 'theoretical'),
            'empirical': sum(1 for c in result.claims if c.claim_type == 'empirical'),
            'design': sum(1 for c in result.claims if c.claim_type == 'design'),
        }

        result.by_evidence = {
            'equation': sum(1 for c in result.claims if c.evidence_type == 'equation'),
            'figure': sum(1 for c in result.claims if c.evidence_type == 'figure'),
            'table': sum(1 for c in result.claims if c.evidence_type == 'table'),
            'citation': sum(1 for c in result.claims if c.evidence_type == 'citation'),
            'experiment': sum(1 for c in result.claims if c.evidence_type == 'experiment'),
            'derivation': sum(1 for c in result.claims if c.evidence_type == 'derivation'),
            'none': sum(1 for c in result.claims if c.evidence_type == 'none'),
        }

        result.unsupported_claims = [c for c in result.claims if c.evidence_type == 'none']
        result.high_risk_claims = [c for c in result.claims if c.risk_level == 'high']

        # Calculate API cost
        # Claude 3.5 Sonnet: $3/M input tokens, $15/M output tokens
        input_cost = (self.input_tokens / 1_000_000) * 3.0
        output_cost = (self.output_tokens / 1_000_000) * 15.0
        result.api_cost_estimate = input_cost + output_cost

        return result

    def generate_csv_report(self, result: ExtractionResult, output_path: Path):
        """Generate CSV audit spreadsheet."""
        os.makedirs(output_path.parent, exist_ok=True)

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'Claim_ID', 'Chapter', 'Section', 'Claim_Text', 'Claim_Type',
                'Evidence_Type', 'Evidence_Location', 'Risk_Level',
                'Validation_Status', 'Notes'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for claim in result.claims:
                writer.writerow({
                    'Claim_ID': claim.claim_id,
                    'Chapter': claim.chapter,
                    'Section': claim.section,
                    'Claim_Text': claim.claim_text,
                    'Claim_Type': claim.claim_type,
                    'Evidence_Type': claim.evidence_type,
                    'Evidence_Location': claim.evidence_location,
                    'Risk_Level': claim.risk_level,
                    'Validation_Status': claim.validation_status,
                    'Notes': claim.notes,
                })

        print(f"[INFO] CSV report generated: {output_path}")

    def generate_summary_report(self, result: ExtractionResult, output_path: Path):
        """Generate markdown summary report."""
        md_path = output_path.with_suffix('.md')

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Technical Claims Audit Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # Summary
            f.write("## SUMMARY\n\n")
            f.write(f"- **Total Claims Extracted**: {result.total_claims}\n")
            f.write(f"- **Unsupported Claims**: {len(result.unsupported_claims)} ({len(result.unsupported_claims)/result.total_claims*100:.1f}%)\n")
            f.write(f"- **High-Risk Claims**: {len(result.high_risk_claims)} ({len(result.high_risk_claims)/result.total_claims*100:.1f}%)\n")
            f.write(f"- **API Cost**: ${result.api_cost_estimate:.2f}\n")
            f.write(f"- **Tokens Used**: {self.input_tokens:,} input + {self.output_tokens:,} output\n\n")

            # By type
            f.write("## CLAIMS BY TYPE\n\n")
            for claim_type, count in result.by_type.items():
                f.write(f"- **{claim_type.capitalize()}**: {count} ({count/result.total_claims*100:.1f}%)\n")
            f.write("\n")

            # By evidence
            f.write("## CLAIMS BY EVIDENCE TYPE\n\n")
            for evidence_type, count in result.by_evidence.items():
                icon = "[ERROR]" if evidence_type == 'none' else "[OK]"
                f.write(f"- **{evidence_type.capitalize()}**: {count} ({count/result.total_claims*100:.1f}%) {icon if evidence_type == 'none' else ''}\n")
            f.write("\n")

            # Unsupported claims
            if result.unsupported_claims:
                f.write("## UNSUPPORTED CLAIMS (REQUIRES EVIDENCE)\n\n")
                f.write("| ID | Chapter | Section | Claim | Risk |\n")
                f.write("|----|---------|---------|-------|------|\n")
                for claim in result.unsupported_claims[:20]:  # Show first 20
                    claim_short = claim.claim_text[:60] + "..." if len(claim.claim_text) > 60 else claim.claim_text
                    f.write(f"| {claim.claim_id} | {claim.chapter} | {claim.section} | {claim_short} | {claim.risk_level} |\n")
                if len(result.unsupported_claims) > 20:
                    f.write(f"\n*... and {len(result.unsupported_claims)-20} more (see CSV for full list)*\n")
                f.write("\n")

            # High-risk claims
            if result.high_risk_claims:
                f.write("## HIGH-RISK CLAIMS (PRIORITY VALIDATION)\n\n")
                f.write("| ID | Chapter | Section | Claim | Evidence |\n")
                f.write("|----|---------|---------|-------|----------|\n")
                for claim in result.high_risk_claims[:20]:
                    claim_short = claim.claim_text[:60] + "..." if len(claim.claim_text) > 60 else claim.claim_text
                    f.write(f"| {claim.claim_id} | {claim.chapter} | {claim.section} | {claim_short} | {claim.evidence_location} |\n")
                if len(result.high_risk_claims) > 20:
                    f.write(f"\n*... and {len(result.high_risk_claims)-20} more (see CSV for full list)*\n")
                f.write("\n")

            # Next steps
            f.write("---\n\n")
            f.write("## NEXT STEPS (MANUAL REVIEW)\n\n")
            f.write("1. **Validate 30% Sample**: Manually review ~{} randomly selected claims\n".format(int(result.total_claims * 0.3)))
            f.write("2. **Address Unsupported Claims**: Add evidence or clarify implicit evidence for {} claims\n".format(len(result.unsupported_claims)))
            f.write("3. **Verify High-Risk Claims**: Expert validation of {} critical claims\n".format(len(result.high_risk_claims)))
            f.write("4. **Update Validation Status**: Mark claims in CSV as 'validated', 'questionable', or 'rejected'\n")
            f.write("5. **Document Issues**: Add notes in CSV for any claims requiring revision\n\n")

            # Verdict
            evidence_rate = 1 - (len(result.unsupported_claims) / result.total_claims)
            threshold = self.config.get('thresholds', {}).get('claims', {}).get('min_evidence_rate', 0.9)

            f.write("## VALIDATION VERDICT\n\n")
            if evidence_rate >= threshold:
                f.write("**STATUS**: [OK] PASS\n\n")
                f.write(f"Evidence rate ({evidence_rate*100:.1f}%) meets threshold ({threshold*100:.0f}%).\n")
            else:
                f.write("**STATUS**: [WARNING] CONDITIONAL\n\n")
                f.write(f"Evidence rate ({evidence_rate*100:.1f}%) below threshold ({threshold*100:.0f}%).\n")
                f.write("Manual review required to address unsupported claims.\n")

        print(f"[INFO] Summary report generated: {md_path}")

    def run(self, chapters: str = "all", output_file: str = "technical_claims_audit.csv"):
        """Run complete extraction workflow."""
        print("\n" + "="*60)
        print("TECHNICAL CLAIMS EXTRACTION")
        print("="*60 + "\n")

        # Extract claims
        result = self.extract_all_claims(chapters)

        # Generate reports
        output_path = self.reports_path / output_file
        self.generate_csv_report(result, output_path)
        self.generate_summary_report(result, output_path)

        # Print summary
        print("\n" + "="*60)
        print("EXTRACTION COMPLETE")
        print("="*60)
        print(f"Total Claims: {result.total_claims}")
        print(f"Unsupported: {len(result.unsupported_claims)} ({len(result.unsupported_claims)/result.total_claims*100:.1f}%)")
        print(f"High-Risk: {len(result.high_risk_claims)} ({len(result.high_risk_claims)/result.total_claims*100:.1f}%)")
        print(f"API Cost: ${result.api_cost_estimate:.2f}")
        print(f"\nReports: {output_path}, {output_path.with_suffix('.md')}")
        print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Extract technical claims from thesis")
    parser.add_argument('--config', default='config.yaml', help='Configuration file')
    parser.add_argument('--chapters', default='all', help='Chapters to process (e.g., "03,04,05" or "all")')
    parser.add_argument('--output', default='technical_claims_audit.csv', help='Output CSV file')
    args = parser.parse_args()

    extractor = ClaimsExtractor(config_path=args.config)
    extractor.run(chapters=args.chapters, output_file=args.output)


if __name__ == "__main__":
    main()
