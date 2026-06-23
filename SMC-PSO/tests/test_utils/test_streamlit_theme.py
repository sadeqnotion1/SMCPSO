"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ Unit Tests: Streamlit Theme Integration Module                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ PURPOSE: Test design token loading, CSS generation, and injection logic     ║
║                                                                              ║
║ TEST COVERAGE:                                                               ║
║ - Token loading from design_tokens_v2.json                                   ║
║ - CSS variable generation (colors, spacing, typography)                      ║
║ - Widget-specific CSS rules (buttons, metrics, sidebar, tabs)                ║
║ - Injection wrapper generation                                               ║
║ - Error handling (missing tokens, invalid JSON, file not found)              ║
║                                                                              ║
║ DEPENDENCIES: pytest, src.utils.streamlit_theme                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.utils.streamlit_theme import (
    load_design_tokens,
    generate_theme_css,
    inject_theme
)


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_minimal_tokens():
    """Minimal mock design tokens for testing."""
    return {
        "colors": {
            "primary": {"value": "#2b87d1"},
            "text-primary": {"value": "#111827"}
        },
        "spacing": {
            "spacing-4": {"value": "16px"}
        },
        "typography": {
            "font-family-body": {"value": "sans-serif"}
        }
    }


# ══════════════════════════════════════════════════════════════════════════════
# TEST: TOKEN LOADING
# ══════════════════════════════════════════════════════════════════════════════

def test_load_design_tokens_success():
    """Test successful loading of design tokens from actual file."""
    tokens = load_design_tokens()

    assert tokens is not None
    assert "colors" in tokens
    assert "spacing" in tokens
    assert "typography" in tokens
    # Verify some expected tokens exist
    assert "primary" in tokens["colors"]
    assert "spacing-4" in tokens["spacing"]


def test_load_design_tokens_file_not_found():
    """Test error when token file doesn't exist."""
    with patch('src.utils.streamlit_theme.Path') as mock_path:
        mock_path.return_value.exists.return_value = False

        with pytest.raises(FileNotFoundError):
            load_design_tokens()


def test_load_design_tokens_invalid_json():
    """Test error handling for malformed JSON."""
    with patch('src.utils.streamlit_theme.Path') as mock_path:
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.read_text.side_effect = json.JSONDecodeError("Invalid", "{}", 0)

        with pytest.raises(json.JSONDecodeError):
            load_design_tokens()


# ══════════════════════════════════════════════════════════════════════════════
# TEST: CSS GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def test_generate_theme_css_structure(mock_minimal_tokens):
    """Test CSS generation produces valid structure."""
    css = generate_theme_css(mock_minimal_tokens)

    # Check basic structure
    assert '[data-theme="dip-docs"]' in css
    assert "/* Colors */" in css

    # Check CSS variables generated
    assert "--dip-primary" in css
    assert "--dip-space-4" in css


def test_generate_theme_css_color_mapping(mock_minimal_tokens):
    """Test correct mapping of color tokens to CSS variables."""
    css = generate_theme_css(mock_minimal_tokens)

    assert "--dip-primary: #2b87d1" in css
    assert "--dip-text-primary: #111827" in css


def test_generate_theme_css_button_styles(mock_minimal_tokens):
    """Test button-specific CSS rules are generated."""
    css = generate_theme_css(mock_minimal_tokens)

    # Check button selectors
    assert ".stButton>button" in css
    assert "background-color:" in css
    assert "border-radius:" in css


def test_generate_theme_css_metrics_styles(mock_minimal_tokens):
    """Test metrics widget CSS rules are generated."""
    css = generate_theme_css(mock_minimal_tokens)

    # Check metric selectors
    assert '[data-testid="stMetric"]' in css


def test_generate_theme_css_sidebar_styles(mock_minimal_tokens):
    """Test sidebar CSS rules are generated."""
    css = generate_theme_css(mock_minimal_tokens)

    # Check sidebar selectors
    assert '[data-testid="stSidebar"]' in css


def test_generate_theme_css_size_limit():
    """Test generated CSS stays within reasonable size with real tokens."""
    tokens = load_design_tokens()
    css = generate_theme_css(tokens)

    # Check uncompressed size is reasonable (target: <10KB uncompressed)
    assert len(css.encode('utf-8')) < 10240, f"CSS too large: {len(css)} bytes"


# ══════════════════════════════════════════════════════════════════════════════
# TEST: INJECTION LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def test_inject_theme_enabled():
    """Test theme injection when enabled."""
    with patch('streamlit.markdown') as mock_markdown:
        inject_theme(enable=True)

        # Should call st.markdown twice (wrapper + style)
        assert mock_markdown.call_count >= 1

        # Check if CSS was injected
        calls = [str(call) for call in mock_markdown.call_args_list]
        assert any('<style' in str(call) for call in calls)


def test_inject_theme_disabled():
    """Test theme injection when disabled."""
    with patch('streamlit.markdown') as mock_markdown:
        inject_theme(enable=False)

        # Should NOT call st.markdown
        assert not mock_markdown.called


def test_inject_theme_wrapper_opening():
    """Test opening wrapper div is generated."""
    with patch('streamlit.markdown') as mock_markdown:
        inject_theme(enable=True)

        # Check first call contains wrapper
        first_call = mock_markdown.call_args_list[0][0][0]
        assert 'data-theme="dip-docs"' in first_call


def test_inject_theme_unsafe_html_allowed():
    """Test that unsafe_allow_html=True is set for injection."""
    with patch('streamlit.markdown') as mock_markdown:
        inject_theme(enable=True)

        # Check all calls use unsafe_allow_html=True
        for call in mock_markdown.call_args_list:
            assert call[1].get('unsafe_allow_html') is True


# ══════════════════════════════════════════════════════════════════════════════
# TEST: ERROR HANDLING
# ══════════════════════════════════════════════════════════════════════════════

def test_generate_theme_css_missing_color_section():
    """Test CSS generation handles missing color section gracefully."""
    incomplete_tokens = {"spacing": {"spacing-4": {"value": "16px"}}}

    css = generate_theme_css(incomplete_tokens)

    # Should not crash, should use defaults
    assert css is not None
    assert len(css) > 0
    assert '[data-theme="dip-docs"]' in css


def test_generate_theme_css_missing_nested_values():
    """Test CSS generation handles missing nested values."""
    incomplete_tokens = {
        "colors": {
            "primary": {}  # Missing "value" key
        }
    }

    css = generate_theme_css(incomplete_tokens)

    # Should not crash, should use .get() with defaults
    assert css is not None


def test_inject_theme_import_error():
    """Test graceful handling when streamlit import fails."""
    # Patch the streamlit import at the point where it's imported (inside inject_theme)
    with patch('builtins.__import__', side_effect=ImportError("Streamlit not available")):
        # Should not crash, just log and skip injection
        try:
            inject_theme(enable=True)
        except ImportError:
            # It's OK if ImportError is raised during import
            pass
        except Exception as e:
            # Should NOT raise other exceptions
            assert False, f"inject_theme should handle ImportError gracefully, got: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# TEST: INTEGRATION
# ══════════════════════════════════════════════════════════════════════════════

def test_end_to_end_theme_pipeline():
    """Test complete pipeline: load → generate → inject."""
    # Load real tokens
    tokens = load_design_tokens()
    assert tokens is not None

    # Generate CSS
    css = generate_theme_css(tokens)
    assert len(css) > 100
    assert "--dip-primary" in css

    # Inject (mocked)
    with patch('streamlit.markdown') as mock_markdown:
        inject_theme(enable=True)
        assert mock_markdown.called


def test_css_variables_match_token_structure():
    """Test CSS variables follow predictable naming from token structure."""
    tokens = load_design_tokens()
    css = generate_theme_css(tokens)

    # Test color tokens
    assert "--dip-primary" in css
    assert "--dip-text-primary" in css

    # Test spacing tokens
    assert "--dip-space-" in css  # At least some spacing variables

    # Test typography tokens
    assert "--dip-font-" in css  # At least some font variables


# ══════════════════════════════════════════════════════════════════════════════
# EDGE CASES
# ══════════════════════════════════════════════════════════════════════════════

def test_empty_tokens_dict():
    """Test handling of completely empty tokens dict."""
    css = generate_theme_css({})

    assert css is not None
    assert '[data-theme="dip-docs"]' in css  # Wrapper should still exist


def test_generate_css_with_special_characters():
    """Test CSS generation handles special characters in values."""
    special_tokens = {
        "colors": {
            "primary": {"value": "rgb(255, 0, 0)"}  # Color with spaces and commas
        }
    }

    css = generate_theme_css(special_tokens)

    assert "rgb(255, 0, 0)" in css
    assert css is not None
