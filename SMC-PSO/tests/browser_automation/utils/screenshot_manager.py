"""Screenshot capture, comparison, and baseline management for visual testing."""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from PIL import Image, ImageChops
import numpy as np


class ScreenshotManager:
    """Manages screenshot capture, baseline comparison, and visual regression testing."""

    def __init__(self, artifacts_path: Path):
        self.artifacts_path = artifacts_path
        self.screenshots_path = artifacts_path / "screenshots"
        self.baseline_path = self.screenshots_path / "baseline"
        self.test_run_path = self.screenshots_path / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create directories
        self.baseline_path.mkdir(parents=True, exist_ok=True)
        self.test_run_path.mkdir(parents=True, exist_ok=True)

    def save_screenshot(self, screenshot_path: Path, name: str, is_baseline: bool = False) -> Path:
        """
        Save screenshot to appropriate directory.

        Args:
            screenshot_path: Source screenshot path
            name: Screenshot name
            is_baseline: Whether to save as baseline

        Returns:
            Path where screenshot was saved
        """
        target_dir = self.baseline_path if is_baseline else self.test_run_path
        target_path = target_dir / f"{name}.png"

        # Copy screenshot
        Image.open(screenshot_path).save(target_path)

        return target_path

    def compare_with_baseline(self, test_screenshot: Path, baseline_name: str,
                               tolerance: float = 0.05) -> Dict[str, Any]:
        """
        Compare test screenshot with baseline.

        Args:
            test_screenshot: Path to test screenshot
            baseline_name: Name of baseline screenshot (without .png)
            tolerance: Acceptable difference percentage (0.0-1.0)

        Returns:
            Dictionary with comparison results
        """
        baseline_path = self.baseline_path / f"{baseline_name}.png"

        if not baseline_path.exists():
            return {
                "match": False,
                "error": "Baseline not found",
                "diff_percentage": None,
                "message": f"Baseline {baseline_name} does not exist. Create it first."
            }

        # Load images
        test_img = Image.open(test_screenshot).convert("RGB")
        baseline_img = Image.open(baseline_path).convert("RGB")

        # Check dimensions
        if test_img.size != baseline_img.size:
            return {
                "match": False,
                "error": "Dimension mismatch",
                "diff_percentage": None,
                "message": f"Size mismatch: test={test_img.size}, baseline={baseline_img.size}"
            }

        # Calculate difference
        diff = ImageChops.difference(test_img, baseline_img)
        diff_np = np.array(diff)
        total_pixels = diff_np.size
        diff_pixels = np.count_nonzero(diff_np)
        diff_percentage = diff_pixels / total_pixels

        # Save diff image if significant
        if diff_percentage > tolerance:
            diff_path = self.test_run_path / f"{baseline_name}_diff.png"
            diff.save(diff_path)

        matches = diff_percentage <= tolerance

        return {
            "match": matches,
            "error": None,
            "diff_percentage": diff_percentage,
            "tolerance": tolerance,
            "message": f"{'PASS' if matches else 'FAIL'}: {diff_percentage:.2%} difference (tolerance: {tolerance:.2%})"
        }
