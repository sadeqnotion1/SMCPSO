#!/usr/bin/env python3
"""
===============================================================================
             DIP-SMC-PSO Documentation - Performance Audit
===============================================================================
File: scripts/analysis/performance_audit.py
Purpose: Measure and analyze page load performance metrics for documentation
===============================================================================
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict
from playwright.async_api import async_playwright


class PerformanceAuditor:
    """Performance auditing tool for documentation pages."""

    def __init__(self, docs_dir: Path, output_file: Path):
        """
        Initialize performance auditor.

        Args:
            docs_dir: Path to docs/_build/html/ directory
            output_file: Path to save performance report JSON
        """
        self.docs_dir = Path(docs_dir)
        self.output_file = Path(output_file)
        self.results: List[Dict] = []

    def find_html_files(self, limit: int = 20) -> List[Path]:
        """Find HTML files to audit (limit to most important pages)."""
        html_files = sorted(self.docs_dir.rglob("*.html"))

        # Prioritize important pages
        priority_patterns = [
            "index.html",
            "theory",
            "implementation",
            "controllers",
            "optimization",
            "presentation"
        ]

        priority_files = []
        other_files = []

        for html_file in html_files:
            if any(pattern in str(html_file) for pattern in priority_patterns):
                priority_files.append(html_file)
            else:
                other_files.append(html_file)

        # Return priority files + some others, up to limit
        selected = (priority_files + other_files)[:limit]
        print(f"[*] Selected {len(selected)} pages for performance audit")
        return selected

    async def audit_page_performance(self, page, html_file: Path) -> Dict:
        """
        Measure page performance metrics.

        Args:
            page: Playwright browser page instance
            html_file: Path to HTML file to audit

        Returns:
            Dictionary of performance metrics
        """
        url = f"file:///{html_file.as_posix()}"
        page_name = html_file.relative_to(self.docs_dir)

        try:
            # Navigate to page
            await page.goto(url, wait_until="load", timeout=30000)

            # Wait for page to be fully interactive
            await page.wait_for_load_state("networkidle", timeout=10000)

            # Get comprehensive performance metrics
            metrics = await page.evaluate("""
                () => {
                    const timing = performance.timing;
                    const navigation = performance.getEntriesByType('navigation')[0];
                    const paintEntries = performance.getEntriesByType('paint');

                    // Calculate timing metrics
                    const domContentLoaded = timing.domContentLoadedEventEnd - timing.navigationStart;
                    const pageLoad = timing.loadEventEnd - timing.navigationStart;
                    const firstPaint = paintEntries.find(e => e.name === 'first-paint')?.startTime || 0;
                    const firstContentfulPaint = paintEntries.find(e => e.name === 'first-contentful-paint')?.startTime || 0;

                    // Resource metrics
                    const resources = performance.getEntriesByType('resource');
                    const resourceCount = resources.length;

                    // Calculate total resource sizes
                    let totalTransferSize = navigation?.transferSize || 0;
                    let totalEncodedSize = navigation?.encodedBodySize || 0;
                    let totalDecodedSize = navigation?.decodedBodySize || 0;

                    // Count resource types
                    const resourceTypes = {};
                    resources.forEach(r => {
                        const type = r.initiatorType || 'other';
                        resourceTypes[type] = (resourceTypes[type] || 0) + 1;
                    });

                    // Page size metrics
                    const images = document.querySelectorAll('img').length;
                    const scripts = document.querySelectorAll('script').length;
                    const stylesheets = document.querySelectorAll('link[rel="stylesheet"]').length;

                    // DOM metrics
                    const domNodes = document.querySelectorAll('*').length;
                    const pageHeight = document.documentElement.scrollHeight;

                    return {
                        timing: {
                            domContentLoaded: Math.round(domContentLoaded),
                            pageLoad: Math.round(pageLoad),
                            firstPaint: Math.round(firstPaint),
                            firstContentfulPaint: Math.round(firstContentfulPaint)
                        },
                        resources: {
                            count: resourceCount,
                            types: resourceTypes
                        },
                        size: {
                            transferSize: totalTransferSize,
                            encodedSize: totalEncodedSize,
                            decodedSize: totalDecodedSize,
                            compressionRatio: totalEncodedSize > 0 ?
                                (1 - totalTransferSize / totalEncodedSize).toFixed(2) : 0
                        },
                        content: {
                            images: images,
                            scripts: scripts,
                            stylesheets: stylesheets,
                            domNodes: domNodes,
                            pageHeight: pageHeight
                        }
                    };
                }
            """)

            # Calculate performance score (0-100)
            score = self._calculate_performance_score(metrics)

            return {
                "page": str(page_name),
                "url": url,
                "metrics": metrics,
                "score": score,
                "status": "success"
            }

        except Exception as e:
            return {
                "page": str(page_name),
                "url": url,
                "error": str(e),
                "status": "failed"
            }

    def _calculate_performance_score(self, metrics: Dict) -> int:
        """
        Calculate performance score (0-100) based on metrics.

        Scoring criteria:
        - Page load time: < 2s (excellent), < 5s (good), > 5s (poor)
        - Resource count: < 50 (excellent), < 100 (good), > 100 (poor)
        - Page size: < 1MB (excellent), < 3MB (good), > 3MB (poor)
        """
        score = 100

        # Deduct points for slow page load
        page_load = metrics['timing']['pageLoad']
        if page_load > 5000:
            score -= 30
        elif page_load > 2000:
            score -= 15

        # Deduct points for many resources
        resource_count = metrics['resources']['count']
        if resource_count > 100:
            score -= 20
        elif resource_count > 50:
            score -= 10

        # Deduct points for large page size
        transfer_size_mb = metrics['size']['transferSize'] / 1024 / 1024
        if transfer_size_mb > 3:
            score -= 30
        elif transfer_size_mb > 1:
            score -= 15

        # Deduct points for large DOM
        dom_nodes = metrics['content']['domNodes']
        if dom_nodes > 3000:
            score -= 10
        elif dom_nodes > 1500:
            score -= 5

        return max(0, score)

    async def run_audit(self):
        """Run performance audit on selected documentation pages."""
        html_files = self.find_html_files(limit=20)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            print("\n[*] Starting performance audit...")
            print(f"[*] Auditing {len(html_files)} pages\n")

            for i, html_file in enumerate(html_files, 1):
                result = await self.audit_page_performance(page, html_file)
                self.results.append(result)

                # Display progress
                if result['status'] == 'success':
                    metrics = result['metrics']
                    load_time = metrics['timing']['pageLoad']
                    size_mb = metrics['size']['transferSize'] / 1024 / 1024
                    score = result['score']

                    print(f"[{i:2d}/{len(html_files)}] {result['page']}")
                    print(f"        Load: {load_time}ms | Size: {size_mb:.2f}MB | Score: {score}/100")
                else:
                    print(f"[{i:2d}/{len(html_files)}] {result['page']} - FAILED: {result.get('error', 'Unknown')}")

            await browser.close()

        # Save results
        self._save_results()
        self._print_summary()

    def _save_results(self):
        """Save performance audit results to JSON file."""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_file, "w") as f:
            json.dump({
                "audit_date": "2025-10-03",
                "total_pages": len(self.results),
                "results": self.results,
                "summary": self._generate_summary()
            }, f, indent=2)

        print(f"\n[*] Results saved to: {self.output_file}")

    def _generate_summary(self) -> Dict:
        """Generate summary statistics."""
        successful = [r for r in self.results if r['status'] == 'success']

        if not successful:
            return {"status": "No successful audits"}

        # Calculate averages
        avg_load_time = sum(r['metrics']['timing']['pageLoad'] for r in successful) / len(successful)
        avg_size = sum(r['metrics']['size']['transferSize'] for r in successful) / len(successful) / 1024 / 1024
        avg_score = sum(r['score'] for r in successful) / len(successful)

        # Find slowest and largest pages
        slowest = max(successful, key=lambda r: r['metrics']['timing']['pageLoad'])
        largest = max(successful, key=lambda r: r['metrics']['size']['transferSize'])

        return {
            "successful_audits": len(successful),
            "failed_audits": len(self.results) - len(successful),
            "averages": {
                "load_time_ms": round(avg_load_time),
                "size_mb": round(avg_size, 2),
                "performance_score": round(avg_score)
            },
            "slowest_page": {
                "page": slowest['page'],
                "load_time_ms": slowest['metrics']['timing']['pageLoad']
            },
            "largest_page": {
                "page": largest['page'],
                "size_mb": round(largest['metrics']['size']['transferSize'] / 1024 / 1024, 2)
            }
        }

    def _print_summary(self):
        """Print human-readable summary."""
        summary = self._generate_summary()

        print("\n" + "="*70)
        print("PERFORMANCE AUDIT SUMMARY")
        print("="*70)
        print(f"Successful audits: {summary['successful_audits']}")
        print(f"Failed audits: {summary['failed_audits']}")
        print()
        print(f"Average load time: {summary['averages']['load_time_ms']}ms")
        print(f"Average page size: {summary['averages']['size_mb']}MB")
        print(f"Average performance score: {summary['averages']['performance_score']}/100")
        print()
        print(f"Slowest page: {summary['slowest_page']['page']}")
        print(f"  Load time: {summary['slowest_page']['load_time_ms']}ms")
        print()
        print(f"Largest page: {summary['largest_page']['page']}")
        print(f"  Size: {summary['largest_page']['size_mb']}MB")
        print("="*70)


async def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent
    docs_dir = project_root / "docs" / "_build" / "html"
    output_file = project_root / ".test_artifacts" / "performance_audit.json"

    if not docs_dir.exists():
        print(f"[ERROR] Documentation directory not found: {docs_dir}")
        print("        Run: sphinx-build -b html docs docs/_build/html")
        sys.exit(1)

    auditor = PerformanceAuditor(docs_dir, output_file)
    await auditor.run_audit()


if __name__ == "__main__":
    asyncio.run(main())
