"""
Tests for Chart.js Sphinx extension.

Validates that the chartjs_extension module loads correctly and provides
expected directives for interactive documentation.
"""
import pytest
import sys
from pathlib import Path


# Add docs/_ext to path for imports
DOCS_EXT_PATH = Path(__file__).parent.parent.parent / "docs" / "_ext"
sys.path.insert(0, str(DOCS_EXT_PATH))


class TestChartJSExtensionImport:
    """Test that the extension can be imported."""

    def test_extension_imports(self):
        """Test that chartjs_extension module can be imported."""
        try:
            import chartjs_extension
            assert chartjs_extension is not None
        except ImportError as e:
            pytest.fail(f"Failed to import chartjs_extension: {e}")

    def test_extension_has_setup_function(self):
        """Test that the extension has a setup() function."""
        import chartjs_extension
        assert hasattr(chartjs_extension, 'setup')
        assert callable(chartjs_extension.setup)

    def test_extension_has_directive_classes(self):
        """Test that expected directive classes are defined."""
        import chartjs_extension
        assert hasattr(chartjs_extension, 'ChartJSDirective')
        assert hasattr(chartjs_extension, 'ControllerComparisonDirective')
        assert hasattr(chartjs_extension, 'PSOConvergenceDirective')


class TestChartJSDirective:
    """Test the ChartJSDirective class."""

    def test_directive_has_required_attributes(self):
        """Test that directive has required Sphinx directive attributes."""
        import chartjs_extension
        directive = chartjs_extension.ChartJSDirective

        assert hasattr(directive, 'has_content')
        assert hasattr(directive, 'required_arguments')
        assert hasattr(directive, 'optional_arguments')
        assert hasattr(directive, 'option_spec')
        assert hasattr(directive, 'run')

    def test_directive_option_spec(self):
        """Test that directive has expected options."""
        import chartjs_extension
        directive = chartjs_extension.ChartJSDirective

        expected_options = {'type', 'data', 'height', 'width', 'title', 'responsive', 'animation'}
        actual_options = set(directive.option_spec.keys())

        assert expected_options == actual_options


class TestControllerComparisonDirective:
    """Test the ControllerComparisonDirective class."""

    def test_directive_has_required_attributes(self):
        """Test that directive has required attributes."""
        import chartjs_extension
        directive = chartjs_extension.ControllerComparisonDirective

        assert hasattr(directive, 'has_content')
        assert hasattr(directive, 'required_arguments')
        assert hasattr(directive, 'optional_arguments')
        assert hasattr(directive, 'option_spec')
        assert hasattr(directive, 'run')

    def test_directive_has_controller_colors(self):
        """Test that directive defines controller color mappings."""
        import chartjs_extension
        directive = chartjs_extension.ControllerComparisonDirective

        assert hasattr(directive, 'CONTROLLER_COLORS')
        assert isinstance(directive.CONTROLLER_COLORS, dict)
        assert 'classical_smc' in directive.CONTROLLER_COLORS
        assert 'adaptive_smc' in directive.CONTROLLER_COLORS

    def test_directive_has_metric_labels(self):
        """Test that directive defines metric label mappings."""
        import chartjs_extension
        directive = chartjs_extension.ControllerComparisonDirective

        assert hasattr(directive, 'METRIC_LABELS')
        assert isinstance(directive.METRIC_LABELS, dict)
        assert 'settling_time' in directive.METRIC_LABELS
        assert 'overshoot' in directive.METRIC_LABELS


class TestPSOConvergenceDirective:
    """Test the PSOConvergenceDirective class."""

    def test_directive_has_required_attributes(self):
        """Test that directive has required attributes."""
        import chartjs_extension
        directive = chartjs_extension.PSOConvergenceDirective

        assert hasattr(directive, 'has_content')
        assert hasattr(directive, 'required_arguments')
        assert hasattr(directive, 'optional_arguments')
        assert hasattr(directive, 'option_spec')
        assert hasattr(directive, 'run')

    def test_directive_option_spec(self):
        """Test that directive has expected options."""
        import chartjs_extension
        directive = chartjs_extension.PSOConvergenceDirective

        expected_options = {'iterations', 'particles', 'height'}
        actual_options = set(directive.option_spec.keys())

        assert expected_options == actual_options


class TestExtensionSetup:
    """Test the extension setup() function."""

    def test_setup_returns_metadata(self):
        """Test that setup() returns required metadata."""
        import chartjs_extension

        # Create mock Sphinx app
        class MockApp:
            def add_directive(self, name, directive_class):
                pass

            def connect(self, event_name, handler):
                pass

        app = MockApp()
        metadata = chartjs_extension.setup(app)

        assert isinstance(metadata, dict)
        assert 'version' in metadata
        assert 'parallel_read_safe' in metadata
        assert 'parallel_write_safe' in metadata

    def test_setup_version_format(self):
        """Test that version follows semantic versioning."""
        import chartjs_extension
        import re

        class MockApp:
            def add_directive(self, name, directive_class):
                pass

            def connect(self, event_name, handler):
                pass

        app = MockApp()
        metadata = chartjs_extension.setup(app)

        version = metadata['version']
        semver_pattern = r'^\d+\.\d+\.\d+$'
        assert re.match(semver_pattern, version), f"Version {version} doesn't match semver format"


class TestDataFiles:
    """Test that sample data files exist and are valid JSON."""

    def test_controller_comparison_data_exists(self):
        """Test that controller comparison sample data exists."""
        data_file = Path(__file__).parent.parent.parent / "docs" / "_data" / "controller_comparison_settling_time.json"
        assert data_file.exists(), f"Data file not found: {data_file}"

    def test_pso_convergence_data_exists(self):
        """Test that PSO convergence sample data exists."""
        data_file = Path(__file__).parent.parent.parent / "docs" / "_data" / "pso_convergence_sample.json"
        assert data_file.exists(), f"Data file not found: {data_file}"

    def test_controller_comparison_data_valid_json(self):
        """Test that controller comparison data is valid JSON."""
        import json

        data_file = Path(__file__).parent.parent.parent / "docs" / "_data" / "controller_comparison_settling_time.json"
        with open(data_file, 'r') as f:
            data = json.load(f)

        assert 'labels' in data
        assert 'datasets' in data
        assert isinstance(data['datasets'], list)
        assert len(data['datasets']) > 0

    def test_pso_convergence_data_valid_json(self):
        """Test that PSO convergence data is valid JSON."""
        import json

        data_file = Path(__file__).parent.parent.parent / "docs" / "_data" / "pso_convergence_sample.json"
        with open(data_file, 'r') as f:
            data = json.load(f)

        assert 'labels' in data
        assert 'datasets' in data
        assert isinstance(data['datasets'], list)
        assert len(data['datasets']) > 0


class TestDocumentationFiles:
    """Test that interactive documentation files exist."""

    def test_interactive_visualizations_guide_exists(self):
        """Test that interactive visualizations guide exists."""
        guide_file = Path(__file__).parent.parent.parent / "docs" / "guides" / "interactive_visualizations.md"
        assert guide_file.exists(), f"Guide not found: {guide_file}"

    def test_controller_comparison_tutorial_exists(self):
        """Test that controller comparison tutorial exists."""
        tutorial_file = Path(__file__).parent.parent.parent / "docs" / "tutorials" / "02_controller_performance_comparison.md"
        assert tutorial_file.exists(), f"Tutorial not found: {tutorial_file}"

    def test_interactive_configuration_guide_exists(self):
        """Test that interactive configuration guide exists."""
        guide_file = Path(__file__).parent.parent.parent / "docs" / "guides" / "interactive_configuration_guide.md"
        assert guide_file.exists(), f"Guide not found: {guide_file}"

    def test_guides_contain_chartjs_directives(self):
        """Test that guides contain Chart.js directive examples."""
        guide_file = Path(__file__).parent.parent.parent / "docs" / "guides" / "interactive_visualizations.md"

        with open(guide_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for directive usage
        assert '.. chartjs::' in content
        assert '.. controller-comparison::' in content
        assert '.. pso-convergence::' in content


class TestExtensionConfiguration:
    """Test that conf.py includes the extension."""

    def test_conf_py_includes_chartjs_extension(self):
        """Test that docs/conf.py includes chartjs_extension."""
        conf_file = Path(__file__).parent.parent.parent / "docs" / "conf.py"

        with open(conf_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "'chartjs_extension'" in content or '"chartjs_extension"' in content

    def test_conf_py_has_ext_path(self):
        """Test that conf.py adds _ext directory to sys.path."""
        conf_file = Path(__file__).parent.parent.parent / "docs" / "conf.py"

        with open(conf_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert '_ext' in content
        assert 'sys.path' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
