"""
Pytest configuration and fixtures for browser automation tests.

Provides reusable fixtures for Playwright browser setup, page management,
and helper utilities.
"""

import sys
from pathlib import Path

# Add browser_automation directory to path for utils imports (must be before other imports)
_browser_automation_dir = Path(__file__).parent
sys.path.insert(0, str(_browser_automation_dir))

import pytest

# Check if playwright is available (optional dependency)
try:
    from playwright.sync_api import sync_playwright
    from utils.playwright_helper import PlaywrightHelper
    from utils.screenshot_manager import ScreenshotManager
    from utils.performance_analyzer import PerformanceAnalyzer
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    pytest.skip("Playwright not installed (optional dependency)", allow_module_level=True)


@pytest.fixture(scope="session")
def browser_name(request):
    """Get browser name from pytest command line option."""
    return request.config.getoption("--browser", default="chromium")


@pytest.fixture(scope="session")
def playwright_instance():
    """Create Playwright instance (session scope)."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="function")
def browser(playwright_instance, browser_name):
    """Launch browser for each test."""
    if browser_name == "chromium":
        browser = playwright_instance.chromium.launch(headless=True)
    elif browser_name == "firefox":
        browser = playwright_instance.firefox.launch(headless=True)
    elif browser_name == "webkit":
        browser = playwright_instance.webkit.launch(headless=True)
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")

    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    """Create browser context with viewport."""
    context = browser.new_context(viewport={"width": 1280, "height": 720})
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context):
    """Create new page for each test."""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="function")
def helper(page):
    """Create PlaywrightHelper instance."""
    artifacts_path = Path(".cache/browser_automation/artifacts")
    return PlaywrightHelper(page, base_path=artifacts_path)


@pytest.fixture(scope="function")
def screenshot_manager():
    """Create ScreenshotManager instance."""
    artifacts_path = Path(".cache/browser_automation/artifacts")
    return ScreenshotManager(artifacts_path)


@pytest.fixture(scope="function")
def performance_analyzer():
    """Create PerformanceAnalyzer instance."""
    return PerformanceAnalyzer()


def pytest_addoption(parser):
    """Add custom command line options."""
    # Note: --browser and --headed are already provided by pytest-playwright plugin
    pass


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "functional: functional tests")
    config.addinivalue_line("markers", "performance: performance tests")
    config.addinivalue_line("markers", "accessibility: accessibility tests")
    config.addinivalue_line("markers", "regression: regression tests")
    config.addinivalue_line("markers", "edge_case: edge case tests")
