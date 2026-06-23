#!/usr/bin/env python3
"""
===============================================================================
           DIP-SMC-PSO Documentation - Accessibility Audit
===============================================================================
File: scripts/analysis/accessibility_audit.py
Purpose: Automated WCAG 2.1 AA compliance checking using Playwright and axe-core
===============================================================================
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict
from playwright.async_api import async_playwright


class AccessibilityAuditor:
    """WCAG 2.1 accessibility auditing tool."""

    def __init__(self, docs_dir: Path, output_file: Path):
        """
        Initialize accessibility auditor.

        Args:
            docs_dir: Path to docs/_build/html/ directory
            output_file: Path to save audit results JSON
        """
        self.docs_dir = Path(docs_dir)
        self.output_file = Path(output_file)
        self.results: List[Dict] = []

    def find_html_files(self, limit: int = 30) -> List[Path]:
        """Find important HTML files to audit."""
        html_files = sorted(self.docs_dir.rglob("*.html"))

        # Prioritize key pages
        priority_patterns = [
            "index.html",
            "theory",
            "controllers",
            "presentation",
            "implementation"
        ]

        priority = []
        other = []

        for file in html_files:
            if any(p in str(file) for p in priority_patterns):
                priority.append(file)
            else:
                other.append(file)

        return (priority + other)[:limit]

    async def audit_page(self, page, html_file: Path) -> Dict:
        """
        Run accessibility audit on a page using axe-core.

        Returns dict with violations, passes, incomplete, and inapplicable checks.
        """
        url = f"file:///{html_file.as_posix()}"
        page_name = html_file.relative_to(self.docs_dir)

        try:
            await page.goto(url, wait_until="load", timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=10000)

            # Inject axe-core library from CDN
            await page.add_script_tag(
                url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js"
            )

            # Wait for axe to be available
            await page.wait_for_function("typeof axe !== 'undefined'", timeout=5000)

            # Run axe accessibility audit
            axe_results = await page.evaluate("""
                async () => {
                    return await axe.run();
                }
            """)

            # Categorize results
            violations = axe_results.get('violations', [])
            passes = axe_results.get('passes', [])
            incomplete = axe_results.get('incomplete', [])

            # Calculate severity scores
            critical_count = sum(1 for v in violations if v.get('impact') == 'critical')
            serious_count = sum(1 for v in violations if v.get('impact') == 'serious')
            moderate_count = sum(1 for v in violations if v.get('impact') == 'moderate')
            minor_count = sum(1 for v in violations if v.get('impact') == 'minor')

            # Compliance score (0-100)
            total_checks = len(violations) + len(passes)
            score = round((len(passes) / total_checks * 100)) if total_checks > 0 else 100

            # WCAG AA pass criteria: no critical or serious violations
            wcag_level = "AA" if critical_count == 0 and serious_count == 0 else "Fail"

            return {
                "page": str(page_name),
                "url": url,
                "violations": {
                    "total": len(violations),
                    "critical": critical_count,
                    "serious": serious_count,
                    "moderate": moderate_count,
                    "minor": minor_count,
                    "details": violations[:5]  # Only first 5 for brevity
                },
                "passes": len(passes),
                "incomplete": len(incomplete),
                "score": score,
                "wcag_level": wcag_level,
                "status": "success"
            }

        except Exception as e:
            return {
                "page": str(page_name),
                "url": url,
                "error": str(e),
                "status": "failed"
            }

    async def run_audit(self):
        """Run accessibility audit on selected pages."""
        html_files = self.find_html_files(limit=30)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            print("\n[*] Starting WCAG 2.1 AA Accessibility Audit...")
            print(f"[*] Auditing {len(html_files)} pages")
            print("[*] Using axe-core for automated compliance checking\n")

            for i, html_file in enumerate(html_files, 1):
                result = await self.audit_page(page, html_file)
                self.results.append(result)

                if result['status'] == 'success':
                    v = result['violations']
                    wcag_icon = "✅" if result['wcag_level'] == "AA" else "❌"

                    print(f"[{i:2d}/{len(html_files)}] {wcag_icon} {result['page']}")
                    print(f"        Violations: {v['total']} "
                          f"(Critical: {v['critical']}, Serious: {v['serious']}) "
                          f"| Score: {result['score']}/100")
                else:
                    print(f"[{i:2d}/{len(html_files)}] ❌ {result['page']} - FAILED: {result.get('error', 'Unknown')}")

            await browser.close()

        self._save_results()
        self._print_summary()

    def _save_results(self):
        """Save audit results to JSON."""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_file, "w") as f:
            json.dump({
                "audit_date": "2025-10-03",
                "wcag_version": "2.1",
                "conformance_level": "AA",
                "total_pages": len(self.results),
                "results": self.results,
                "summary": self._generate_summary()
            }, f, indent=2)

        print(f"\n[*] Detailed results saved to: {self.output_file}")

    def _generate_summary(self) -> Dict:
        """Generate summary statistics."""
        successful = [r for r in self.results if r['status'] == 'success']

        if not successful:
            return {"status": "No successful audits"}

        total_violations = sum(r['violations']['total'] for r in successful)
        total_critical = sum(r['violations']['critical'] for r in successful)
        total_serious = sum(r['violations']['serious'] for r in successful)
        avg_score = sum(r['score'] for r in successful) / len(successful)

        passing_pages = sum(1 for r in successful if r['wcag_level'] == 'AA')

        return {
            "pages_audited": len(successful),
            "pages_passing_aa": passing_pages,
            "pass_rate": round((passing_pages / len(successful)) * 100, 1),
            "total_violations": total_violations,
            "critical_violations": total_critical,
            "serious_violations": total_serious,
            "average_score": round(avg_score, 1)
        }

    def _print_summary(self):
        """Print summary report."""
        summary = self._generate_summary()

        print("\n" + "="*70)
        print("WCAG 2.1 AA ACCESSIBILITY AUDIT SUMMARY")
        print("="*70)
        print(f"Pages audited: {summary['pages_audited']}")
        print(f"Pages passing AA: {summary['pages_passing_aa']} ({summary['pass_rate']}%)")
        print()
        print(f"Total violations: {summary['total_violations']}")
        print(f"  Critical: {summary['critical_violations']}")
        print(f"  Serious: {summary['serious_violations']}")
        print()
        print(f"Average accessibility score: {summary['average_score']}/100")
        print()

        if summary['pass_rate'] >= 90:
            print("✅ PASS: Documentation meets >90% WCAG 2.1 AA compliance target")
        elif summary['pass_rate'] >= 75:
            print("⚠️  WARNING: Documentation at {summary['pass_rate']}% compliance")
        else:
            print("❌ FAIL: Documentation below 75% WCAG 2.1 AA compliance")

        print("="*70)


async def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent
    docs_dir = project_root / "docs" / "_build" / "html"
    output_file = project_root / ".test_artifacts" / "accessibility_audit.json"

    if not docs_dir.exists():
        print("[ERROR] Documentation not built")
        print("        Run: sphinx-build -b html docs docs/_build/html")
        sys.exit(1)

    auditor = AccessibilityAuditor(docs_dir, output_file)
    await auditor.run_audit()


if __name__ == "__main__":
    asyncio.run(main())
