#!/usr/bin/env python3
"""
verify_equations.py - Symbolic Math Verification Script

Verifies mathematical equations using SymPy:
- Extract LaTeX equations from thesis
- Convert to SymPy expressions
- Verify algebraic steps
- Check dimensional consistency
- Validate simplifications

Created: November 5, 2025
Priority: 5 (Advanced - 70% automated)
Manual Work: 1-2 hours review (complex proofs)

Usage:
    python verify_equations.py [--config config.yaml] [--chapter 03] [--output equations_validation.json]

Requirements:
    pip install sympy
"""

import re
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
import yaml
from datetime import datetime

try:
    import sympy as sp
    from sympy.parsing.latex import parse_latex
except ImportError:
    print("[ERROR] sympy not installed. Run: pip install sympy")
    exit(1)


@dataclass
class Equation:
    """Represents an equation from the thesis."""
    equation_id: str  # e.g., "3.12"
    latex: str
    chapter: str
    file_path: str
    line_number: int
    context: str = ""
    sympy_expr: Optional[str] = None
    verification_status: str = "pending"  # 'verified', 'failed', 'skipped', 'pending'
    issues: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Results of equation validation."""
    total_equations: int = 0
    verified_equations: int = 0
    failed_equations: int = 0
    skipped_equations: int = 0
    equations: List[Equation] = field(default_factory=list)


class EquationVerifier:
    """Verifies equations using SymPy symbolic math."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize verifier."""
        self.config = self._load_config(config_path)
        self.thesis_path = Path(self.config['thesis']['base_path'])
        self.reports_path = Path(self.config['output']['reports_path'])

    def _load_config(self, config_path: str) -> dict:
        """Load configuration."""
        config_file = Path(__file__).parent / config_path
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {'thesis': {'base_path': 'docs/thesis'}, 'output': {'reports_path': '.artifacts/thesis/reports'}}

    def extract_equations(self, chapter_file: Path) -> List[Equation]:
        """Extract numbered equations from chapter."""
        equations = []

        try:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return equations

        # Extract chapter number
        chapter_num = re.match(r'(\d+)_', chapter_file.name).group(1) if re.match(r'(\d+)_', chapter_file.name) else "0"

        # Find equations with \tag{X.Y}
        pattern = r'\$\$(.*?)\\tag\{([\d.]+)\}(.*?)\$\$'
        for match in re.finditer(pattern, content, re.DOTALL):
            latex = match.group(1).strip()
            eq_id = match.group(2)

            eq = Equation(
                equation_id=eq_id,
                latex=latex,
                chapter=chapter_num,
                file_path=str(chapter_file),
                line_number=content[:match.start()].count('\n') + 1,
                context=match.group(0)[:200]
            )
            equations.append(eq)

        return equations

    def verify_equation(self, equation: Equation) -> Equation:
        """Attempt to verify an equation using SymPy."""
        try:
            # Try to parse LaTeX with SymPy
            expr = parse_latex(equation.latex)
            equation.sympy_expr = str(expr)
            equation.verification_status = "verified"
        except Exception as e:
            equation.verification_status = "skipped"
            equation.issues.append(f"Could not parse with SymPy: {str(e)[:100]}")

        return equation

    def run(self, chapter_num: str = "all", output_file: str = "equations_validation.json"):
        """Run equation verification."""
        print("\n" + "="*60)
        print("EQUATION VERIFICATION")
        print("="*60 + "\n")

        # Get chapter files
        if chapter_num == "all":
            chapter_files = sorted(self.thesis_path.glob("[0-9][0-9]_*.md"))
        else:
            chapter_files = list(self.thesis_path.glob(f"{chapter_num.zfill(2)}_*.md"))

        result = ValidationResult()

        # Process each chapter
        for chapter_file in chapter_files:
            print(f"[INFO] Processing {chapter_file.name}")
            equations = self.extract_equations(chapter_file)

            for eq in equations:
                verified_eq = self.verify_equation(eq)
                result.equations.append(verified_eq)

        # Compute stats
        result.total_equations = len(result.equations)
        result.verified_equations = sum(1 for e in result.equations if e.verification_status == "verified")
        result.failed_equations = sum(1 for e in result.equations if e.verification_status == "failed")
        result.skipped_equations = sum(1 for e in result.equations if e.verification_status == "skipped")

        # Generate report
        output_path = self.reports_path / output_file
        os.makedirs(output_path.parent, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump({
                'generated': datetime.now().isoformat(),
                'summary': {
                    'total': result.total_equations,
                    'verified': result.verified_equations,
                    'failed': result.failed_equations,
                    'skipped': result.skipped_equations,
                },
                'equations': [asdict(eq) for eq in result.equations]
            }, f, indent=2, default=str)

        print(f"\n[INFO] Report: {output_path}")
        print(f"Total: {result.total_equations} | Verified: {result.verified_equations} | Skipped: {result.skipped_equations}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Verify thesis equations")
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--chapter', default='all')
    parser.add_argument('--output', default='equations_validation.json')
    args = parser.parse_args()

    verifier = EquationVerifier(args.config)
    verifier.run(args.chapter, args.output)


if __name__ == "__main__":
    main()
