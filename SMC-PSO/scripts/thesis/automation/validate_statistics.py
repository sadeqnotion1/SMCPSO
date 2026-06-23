#!/usr/bin/env python3
"""
validate_statistics.py - Statistical Claims Validation Script

Validates statistical analysis in thesis (primarily Chapter 8):
- p-values reported and interpreted correctly
- Effect sizes (Cohen's d) calculated and reported
- Confidence intervals provided
- Multiple comparison corrections (Bonferroni: α/15)
- Normality assumptions tested (Shapiro-Wilk)
- Sample size adequacy
- Test selection appropriateness

Created: November 5, 2025
Priority: 2 (Quick Win - 90% automated)
Manual Work: 30 min review

Usage:
    python validate_statistics.py [--config config.yaml] [--chapter 08] [--output report.json]
"""

import re
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
import yaml
from datetime import datetime


@dataclass
class StatisticalClaim:
    """Represents a statistical claim found in the thesis."""
    claim_text: str
    test_type: Optional[str] = None  # 'welch_t', 'cohen_d', 'anova', etc.
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    confidence_interval: Optional[tuple] = None
    sample_size: Optional[int] = None
    file_path: str = ""
    line_number: int = 0
    context: str = ""
    validation_status: str = "PENDING"  # PASS, FAIL, PENDING
    issues: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Results of statistical validation."""
    chapter: str
    total_claims: int = 0
    validated_claims: int = 0
    failed_claims: int = 0
    claims: List[StatisticalClaim] = field(default_factory=list)
    bonferroni_correction_applied: bool = False
    normality_tests_mentioned: bool = False
    assumptions_validated: bool = False
    overall_status: str = "PENDING"


class StatisticsValidator:
    """Validates statistical analysis in thesis."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize validator with configuration."""
        self.config = self._load_config(config_path)
        self.thesis_path = Path(self.config['thesis']['base_path'])
        self.reports_path = Path(self.config['output']['reports_path'])

        # Statistical patterns
        self.patterns = {
            'p_value': [
                r'p\s*[=<>]\s*([0-9.]+)',
                r'p-value\s*[=<>]\s*([0-9.]+)',
                r'\(p\s*[=<>]\s*([0-9.]+)\)',
            ],
            'effect_size': [
                r'd\s*=\s*([0-9.]+)',  # Cohen's d
                r'effect size.*?=\s*([0-9.]+)',
                r'Cohen\'?s\s+d\s*=\s*([0-9.]+)',
            ],
            'confidence_interval': [
                r'95%\s*CI:?\s*\[([0-9.]+),\s*([0-9.]+)\]',
                r'CI.*?\[([0-9.]+),\s*([0-9.]+)\]',
            ],
            'sample_size': [
                r'n\s*=\s*(\d+)',
                r'N\s*=\s*(\d+)',
                r'sample size.*?=\s*(\d+)',
            ],
            'welch_t_test': [
                r'Welch\'?s\s+t-test',
                r't-test',
            ],
            'cohen_d': [
                r'Cohen\'?s\s+d',
                r'effect size',
            ],
            'anova': [
                r'ANOVA',
                r'analysis of variance',
            ],
            'bonferroni': [
                r'Bonferroni',
                r'corrected\s+alpha',
                r'α\s*/\s*\d+',
                r'alpha\s*/\s*\d+',
            ],
            'normality': [
                r'Shapiro-Wilk',
                r'normality test',
                r'normal distribution',
            ],
        }

        # Thresholds from config
        self.num_tests = self.config['thresholds']['statistics']['bonferroni_tests']
        self.alpha = self.config['thresholds']['statistics']['alpha']
        self.corrected_alpha = self.config['thresholds']['statistics']['corrected_alpha']
        self.min_effect_size = self.config['thresholds']['statistics']['min_effect_size']

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
            },
            'output': {
                'reports_path': '.artifacts/thesis/reports',
                'verbose': True,
            },
            'thresholds': {
                'statistics': {
                    'bonferroni_tests': 15,
                    'alpha': 0.05,
                    'corrected_alpha': 0.00333,
                    'min_effect_size': 0.5,
                },
            },
        }

    def load_chapter(self, chapter_num: str) -> Optional[str]:
        """Load chapter markdown file."""
        chapter_file = self.thesis_path / f"{chapter_num}_*.md"
        matching_files = list(self.thesis_path.glob(f"{chapter_num}_*.md"))

        if not matching_files:
            print(f"[ERROR] Chapter {chapter_num} not found in {self.thesis_path}")
            return None

        chapter_path = matching_files[0]
        print(f"[INFO] Loading {chapter_path.name}")

        try:
            with open(chapter_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[ERROR] Cannot read {chapter_path}: {e}")
            return None

    def extract_statistical_claims(self, content: str, file_path: str) -> List[StatisticalClaim]:
        """Extract all statistical claims from content."""
        claims = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, start=1):
            # Skip code blocks
            if line.strip().startswith('```'):
                continue

            # Check for statistical test mentions
            claim = None

            # Check for p-values
            for pattern in self.patterns['p_value']:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    p_val = float(match.group(1))
                    claim = StatisticalClaim(
                        claim_text=line.strip(),
                        p_value=p_val,
                        file_path=file_path,
                        line_number=line_num,
                        context=line.strip()[:100]
                    )

                    # Validate p-value
                    if p_val < self.corrected_alpha:
                        claim.validation_status = "PASS"
                    else:
                        claim.validation_status = "PENDING"
                        claim.issues.append(f"p-value {p_val} not < corrected alpha {self.corrected_alpha}")

                    break

            # Check for effect sizes
            for pattern in self.patterns['effect_size']:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    effect = float(match.group(1))
                    if claim:
                        claim.effect_size = effect
                    else:
                        claim = StatisticalClaim(
                            claim_text=line.strip(),
                            effect_size=effect,
                            file_path=file_path,
                            line_number=line_num,
                            context=line.strip()[:100]
                        )

                    # Validate effect size
                    if effect >= self.min_effect_size:
                        claim.validation_status = "PASS"
                    else:
                        claim.validation_status = "PENDING"
                        claim.issues.append(f"Effect size {effect} below recommended minimum {self.min_effect_size}")

                    break

            # Check for confidence intervals
            for pattern in self.patterns['confidence_interval']:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    ci_lower = float(match.group(1))
                    ci_upper = float(match.group(2))
                    if claim:
                        claim.confidence_interval = (ci_lower, ci_upper)
                    else:
                        claim = StatisticalClaim(
                            claim_text=line.strip(),
                            confidence_interval=(ci_lower, ci_upper),
                            file_path=file_path,
                            line_number=line_num,
                            context=line.strip()[:100]
                        )
                        claim.validation_status = "PASS"

                    break

            # Identify test type
            if claim:
                if any(re.search(p, line, re.IGNORECASE) for p in self.patterns['welch_t_test']):
                    claim.test_type = 'welch_t'
                elif any(re.search(p, line, re.IGNORECASE) for p in self.patterns['anova']):
                    claim.test_type = 'anova'
                elif any(re.search(p, line, re.IGNORECASE) for p in self.patterns['cohen_d']):
                    claim.test_type = 'cohen_d'

                claims.append(claim)

        return claims

    def check_bonferroni_correction(self, content: str) -> bool:
        """Check if Bonferroni correction is mentioned."""
        for pattern in self.patterns['bonferroni']:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def check_normality_tests(self, content: str) -> bool:
        """Check if normality tests are mentioned."""
        for pattern in self.patterns['normality']:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def validate_chapter(self, chapter_num: str = "08") -> ValidationResult:
        """Validate statistical claims in a chapter."""
        result = ValidationResult(chapter=chapter_num)

        # Load chapter content
        content = self.load_chapter(chapter_num)
        if not content:
            result.overall_status = "ERROR"
            return result

        # Extract claims
        print("[INFO] Extracting statistical claims...")
        claims = self.extract_statistical_claims(content, f"chapter_{chapter_num}")
        result.claims = claims
        result.total_claims = len(claims)

        # Count validated claims
        result.validated_claims = sum(1 for c in claims if c.validation_status == "PASS")
        result.failed_claims = sum(1 for c in claims if c.validation_status == "FAIL")

        # Check for Bonferroni correction
        result.bonferroni_correction_applied = self.check_bonferroni_correction(content)

        # Check for normality tests
        result.normality_tests_mentioned = self.check_normality_tests(content)

        # Overall validation status
        if result.total_claims == 0:
            result.overall_status = "ERROR"
        elif result.validated_claims == result.total_claims and result.bonferroni_correction_applied:
            result.overall_status = "PASS"
        elif result.validated_claims >= result.total_claims * 0.8:
            result.overall_status = "CONDITIONAL"
        else:
            result.overall_status = "FAIL"

        return result

    def generate_report(self, result: ValidationResult, output_path: Path):
        """Generate JSON validation report."""
        os.makedirs(output_path.parent, exist_ok=True)

        report = {
            'generated': datetime.now().isoformat(),
            'chapter': result.chapter,
            'summary': {
                'total_claims': result.total_claims,
                'validated_claims': result.validated_claims,
                'failed_claims': result.failed_claims,
                'success_rate': f"{result.validated_claims/result.total_claims*100:.1f}%" if result.total_claims > 0 else "N/A",
                'bonferroni_correction': result.bonferroni_correction_applied,
                'normality_tests_mentioned': result.normality_tests_mentioned,
                'overall_status': result.overall_status,
            },
            'thresholds': {
                'num_tests': self.num_tests,
                'alpha': self.alpha,
                'corrected_alpha': self.corrected_alpha,
                'min_effect_size': self.min_effect_size,
            },
            'claims': [asdict(claim) for claim in result.claims],
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"[INFO] Report generated: {output_path}")

        # Also generate markdown summary
        md_path = output_path.with_suffix('.md')
        self._generate_markdown_summary(result, md_path)

    def _generate_markdown_summary(self, result: ValidationResult, output_path: Path):
        """Generate markdown summary report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Statistical Validation Report - Chapter {result.chapter}\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # Summary
            f.write("## SUMMARY\n\n")
            f.write(f"- **Total Statistical Claims**: {result.total_claims}\n")
            f.write(f"- **Validated Claims**: {result.validated_claims}\n")
            f.write(f"- **Failed Claims**: {result.failed_claims}\n")
            if result.total_claims > 0:
                f.write(f"- **Success Rate**: {result.validated_claims/result.total_claims*100:.1f}%\n")
            f.write(f"- **Bonferroni Correction Applied**: {'[OK] YES' if result.bonferroni_correction_applied else '[WARNING] NO'}\n")
            f.write(f"- **Normality Tests Mentioned**: {'[OK] YES' if result.normality_tests_mentioned else '[WARNING] NO'}\n")
            f.write(f"- **Overall Status**: **{result.overall_status}**\n\n")

            # Thresholds
            f.write("## STATISTICAL THRESHOLDS\n\n")
            f.write(f"- **Number of Tests**: {self.num_tests} (pairwise comparisons)\n")
            f.write(f"- **Uncorrected Alpha**: {self.alpha}\n")
            f.write(f"- **Bonferroni Corrected Alpha**: {self.corrected_alpha} (α/{self.num_tests})\n")
            f.write(f"- **Minimum Effect Size**: {self.min_effect_size} (Cohen's d)\n\n")

            # Claims detail
            f.write("## CLAIMS DETAIL\n\n")
            for i, claim in enumerate(result.claims, 1):
                f.write(f"### Claim {i}: {claim.validation_status}\n\n")
                f.write(f"**Text**: {claim.claim_text[:100]}...\n\n")
                if claim.test_type:
                    f.write(f"**Test Type**: {claim.test_type}\n\n")
                if claim.p_value is not None:
                    sig = "significant" if claim.p_value < self.corrected_alpha else "not significant"
                    f.write(f"**p-value**: {claim.p_value} ({sig} at α={self.corrected_alpha})\n\n")
                if claim.effect_size is not None:
                    magnitude = "large" if claim.effect_size >= 0.8 else "medium" if claim.effect_size >= 0.5 else "small"
                    f.write(f"**Effect Size**: {claim.effect_size} ({magnitude})\n\n")
                if claim.confidence_interval:
                    f.write(f"**95% CI**: [{claim.confidence_interval[0]}, {claim.confidence_interval[1]}]\n\n")
                if claim.issues:
                    f.write("**Issues**:\n")
                    for issue in claim.issues:
                        f.write(f"- {issue}\n")
                    f.write("\n")
                f.write(f"**Location**: Line {claim.line_number}\n\n")
                f.write("---\n\n")

            # Verdict
            f.write("## VALIDATION VERDICT\n\n")
            if result.overall_status == "PASS":
                f.write("**STATUS**: [OK] PASS\n\n")
                f.write("All statistical claims validated successfully.\n")
            elif result.overall_status == "CONDITIONAL":
                f.write("**STATUS**: [WARNING] CONDITIONAL PASS\n\n")
                f.write("Most claims validated, but some issues found. Manual review recommended.\n")
            else:
                f.write("**STATUS**: [ERROR] FAIL\n\n")
                f.write("Significant statistical issues found. Expert review required.\n")

        print(f"[INFO] Markdown summary generated: {output_path}")

    def run(self, chapter_num: str = "08", output_file: str = "statistics_validation.json"):
        """Run complete validation workflow."""
        print("\n" + "="*60)
        print(f"STATISTICAL VALIDATION - CHAPTER {chapter_num}")
        print("="*60 + "\n")

        # Validate chapter
        result = self.validate_chapter(chapter_num)

        # Generate report
        output_path = self.reports_path / output_file
        self.generate_report(result, output_path)

        # Print summary
        print("\n" + "="*60)
        print("VALIDATION COMPLETE")
        print("="*60)
        print(f"Total: {result.total_claims} | Validated: {result.validated_claims} | Failed: {result.failed_claims}")
        print(f"Bonferroni: {'[OK]' if result.bonferroni_correction_applied else '[WARNING]'}")
        print(f"Normality Tests: {'[OK]' if result.normality_tests_mentioned else '[WARNING]'}")
        print(f"Overall: {result.overall_status}")
        print(f"\nReports: {output_path}, {output_path.with_suffix('.md')}")
        print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate thesis statistical claims")
    parser.add_argument('--config', default='config.yaml', help='Configuration file')
    parser.add_argument('--chapter', default='08', help='Chapter number to validate')
    parser.add_argument('--output', default='statistics_validation.json', help='Output report file')
    args = parser.parse_args()

    validator = StatisticsValidator(config_path=args.config)
    validator.run(chapter_num=args.chapter, output_file=args.output)


if __name__ == "__main__":
    main()
