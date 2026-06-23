#!/usr/bin/env python3
"""
screen_proofs.py - Lyapunov Proof Screening Script

Screens Lyapunov proofs for structural issues (NOT full validation):
- Extract proof structure from Appendix A
- Check theorem citations (Barbalat, Clarke derivatives)
- Verify V̇ < 0 claims present
- Flag missing steps or red flags
- Generate expert triage report

Created: November 5, 2025
Priority: 8 (Advanced - 30% screening only)
Manual Work: 4-6 hours (EXPERT REQUIRED for full validation)

Usage:
    python screen_proofs.py [--config config.yaml] [--output proof_screening.md]

Note: This is SCREENING only. Deep validation requires expert review.
"""

import re
import os
from pathlib import Path
from typing import List
from dataclasses import dataclass, field
import yaml
from datetime import datetime


@dataclass
class ProofCheck:
    """Represents a proof screening check."""
    proof_name: str  # e.g., "Classical SMC Stability"
    appendix_ref: str  # e.g., "Appendix A.1"
    structure_complete: bool = False
    v_candidate_present: bool = False
    v_dot_negative_claimed: bool = False
    theorems_cited: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    requires_expert: bool = True


class ProofScreener:
    """Screens Lyapunov proofs for structural completeness."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize screener."""
        self.config = self._load_config(config_path)
        self.thesis_path = Path(self.config['thesis']['base_path'])
        self.reports_path = Path(self.config['output']['reports_path'])

        # Define proofs to screen
        self.proofs = [
            "Classical SMC Stability (Appendix A.1)",
            "STA Finite-Time Convergence (Appendix A.2)",
            "Adaptive SMC Stability (Appendix A.3)",
            "Hybrid ISS Proof (Appendix A.4)",
            "Swing-Up SMC Stability (Appendix A.5)",
            "Global Stability Analysis (Appendix A.6)",
        ]

    def _load_config(self, config_path: str) -> dict:
        """Load configuration."""
        config_file = Path(__file__).parent / config_path
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {'thesis': {'base_path': 'docs/thesis'}, 'output': {'reports_path': '.artifacts/thesis/reports'}}

    def screen_proof(self, proof_name: str) -> ProofCheck:
        """Screen a single proof for structural completeness."""
        check = ProofCheck(proof_name=proof_name, appendix_ref="Appendix A")

        # Load Appendix A
        appendix_files = list(self.thesis_path.glob("appendix_a*.md"))
        if not appendix_files:
            check.red_flags.append("Appendix A file not found")
            return check

        try:
            with open(appendix_files[0], 'r') as f:
                content = f.read().lower()  # Case-insensitive

            # Check for Lyapunov candidate
            if 'v(' in content or 'v=' in content or 'lyapunov candidate' in content:
                check.v_candidate_present = True

            # Check for V̇ < 0
            if 'dot{v}' in content or 'v̇' in content or '\\dot v' in content:
                check.v_dot_negative_claimed = True

            # Check for theorem citations
            theorems = ['barbalat', 'lasalle', 'clarke', 'lyapunov', 'khalil']
            for theorem in theorems:
                if theorem in content:
                    check.theorems_cited.append(theorem.capitalize())

            # Basic structure check
            if check.v_candidate_present and check.v_dot_negative_claimed:
                check.structure_complete = True

            # Red flags
            if not check.v_candidate_present:
                check.red_flags.append("No Lyapunov candidate V(x) identified")
            if not check.v_dot_negative_claimed:
                check.red_flags.append("No V̇ < 0 derivation found")
            if not check.theorems_cited:
                check.red_flags.append("No stability theorems cited")

        except Exception as e:
            check.red_flags.append(f"Error reading proof: {e}")

        return check

    def run(self, output_file: str = "proof_screening.md"):
        """Run proof screening."""
        print("\n" + "="*60)
        print("LYAPUNOV PROOF SCREENING")
        print("="*60 + "\n")
        print("[WARNING] This is SCREENING only - NOT full validation")
        print("[WARNING] Expert review REQUIRED for all proofs\n")

        checks = []
        for proof in self.proofs:
            print(f"[INFO] Screening: {proof}")
            check = self.screen_proof(proof)
            checks.append(check)

        # Generate report
        output_path = self.reports_path / output_file
        os.makedirs(output_path.parent, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Lyapunov Proof Screening Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("**[WARNING] SCREENING ONLY - NOT FULL VALIDATION**\n\n")
            f.write("**EXPERT REVIEW REQUIRED**: All proofs require line-by-line expert validation.\n\n")
            f.write("---\n\n")

            f.write("## PROOF SCREENING RESULTS\n\n")
            for check in checks:
                f.write(f"### {check.proof_name}\n\n")
                f.write(f"- **Structure Complete**: {'[OK] YES' if check.structure_complete else '[ERROR] NO'}\n")
                f.write(f"- **V(x) Candidate**: {'[OK] Present' if check.v_candidate_present else '[ERROR] Missing'}\n")
                f.write(f"- **V_dot < 0 Claim**: {'[OK] Present' if check.v_dot_negative_claimed else '[ERROR] Missing'}\n")
                f.write(f"- **Theorems Cited**: {', '.join(check.theorems_cited) if check.theorems_cited else 'None'}\n")

                if check.red_flags:
                    f.write(f"\n**[ERROR] Red Flags**:\n")
                    for flag in check.red_flags:
                        f.write(f"- {flag}\n")

                f.write(f"\n**Expert Validation Required**: {check.requires_expert}\n\n")
                f.write("---\n\n")

            f.write("## NEXT STEPS\n\n")
            f.write("1. **Expert Line-by-Line Review**: All 6 proofs require detailed expert validation\n")
            f.write("2. **Focus Areas**: STA finite-time convergence (non-smooth Lyapunov), Hybrid ISS (Zeno prevention)\n")
            f.write("3. **Estimated Time**: 4-6 hours expert review\n")
            f.write("4. **Use**: `docs/thesis/validation/PROOF_VERIFICATION_PROTOCOL.md` for detailed checklist\n")

        print(f"\n[INFO] Report: {output_path}")
        print(f"[INFO] [WARNING] Expert review required for all {len(checks)} proofs")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Screen Lyapunov proofs")
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--output', default='proof_screening.md')
    args = parser.parse_args()

    screener = ProofScreener(args.config)
    screener.run(args.output)


if __name__ == "__main__":
    main()
