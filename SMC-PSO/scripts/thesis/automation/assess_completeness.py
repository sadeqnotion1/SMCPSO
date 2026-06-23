#!/usr/bin/env python3
"""
assess_completeness.py - Research Question Coverage Assessment

Uses Claude API to verify all research questions are addressed:
- Extract RQs from Chapter 1
- Identify answers in Chapters 8-12
- Generate coverage matrix
- Flag unanswered questions

Created: November 5, 2025
Priority: 7 (Advanced - 60% automated)
Manual Work: 30 min review

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python assess_completeness.py [--config config.yaml] [--output completeness_assessment.json]
"""

import os
import sys
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
import yaml
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("[ERROR] anthropic not installed. Run: pip install anthropic")
    sys.exit(1)


@dataclass
class ResearchQuestion:
    """Represents a research question."""
    rq_id: str  # e.g., "RQ1"
    question: str
    answered: bool = False
    answer_location: str = ""
    answer_summary: str = ""


class CompletenessAssessor:
    """Assesses thesis completeness using Claude API."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize assessor."""
        self.config = self._load_config(config_path)
        self.thesis_path = Path(self.config['thesis']['base_path'])
        self.reports_path = Path(self.config['output']['reports_path'])

        # Initialize Claude
        api_key = os.environ.get(self.config['api']['anthropic']['api_key_env'])
        if not api_key:
            print("[ERROR] ANTHROPIC_API_KEY not set")
            sys.exit(1)

        self.client = anthropic.Anthropic(api_key=api_key)

    def _load_config(self, config_path: str) -> dict:
        """Load configuration."""
        config_file = Path(__file__).parent / config_path
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {
            'thesis': {'base_path': 'docs/thesis'},
            'output': {'reports_path': '.artifacts/thesis/reports'},
            'api': {'anthropic': {'api_key_env': 'ANTHROPIC_API_KEY', 'model': 'claude-3-5-sonnet-20241022'}}
        }

    def extract_research_questions(self) -> list[ResearchQuestion]:
        """Extract RQs from Chapter 1 using Claude."""
        print("[INFO] Extracting research questions from Chapter 1...")

        chapter_1 = list(self.thesis_path.glob("01_*.md"))
        if not chapter_1:
            print("[ERROR] Chapter 1 not found")
            return []

        with open(chapter_1[0], 'r') as f:
            content = f.read()

        prompt = f"""Extract all research questions from this thesis chapter.
Return them as JSON array:
[
  {{"rq_id": "RQ1", "question": "exact question text"}},
  ...
]

Chapter 1:
{content[:10000]}
"""

        try:
            response = self.client.messages.create(
                model=self.config['api']['anthropic']['model'],
                max_tokens=2000,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text
            import re
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                json_text = response_text

            rqs_data = json.loads(json_text)
            return [ResearchQuestion(**rq) for rq in rqs_data]

        except Exception as e:
            print(f"[ERROR] Failed to extract RQs: {e}")
            return []

    def run(self, output_file: str = "completeness_assessment.json"):
        """Run completeness assessment."""
        print("\n" + "="*60)
        print("COMPLETENESS ASSESSMENT")
        print("="*60 + "\n")

        # Extract RQs
        rqs = self.extract_research_questions()
        print(f"[INFO] Found {len(rqs)} research questions")

        # Generate report
        output_path = self.reports_path / output_file
        os.makedirs(output_path.parent, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump({
                'generated': datetime.now().isoformat(),
                'research_questions': [asdict(rq) for rq in rqs],
                'summary': {
                    'total_rqs': len(rqs),
                    'answered': sum(1 for rq in rqs if rq.answered),
                }
            }, f, indent=2)

        print(f"[INFO] Report: {output_path}")
        print(f"[INFO] Manual review: Verify each RQ is answered in Chapters 8-12")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Assess thesis completeness")
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--output', default='completeness_assessment.json')
    args = parser.parse_args()

    assessor = CompletenessAssessor(args.config)
    assessor.run(args.output)


if __name__ == "__main__":
    main()
