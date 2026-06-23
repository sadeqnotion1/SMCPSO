# Test Infrastructure Guide ## Overview This document provides guidance for the DIP SMC PSO test infrastructure, including pytest configuration, test execution procedures, and troubleshooting guidelines. ## Pytest Configuration ### Test Markers The project uses an extensive set of pytest markers for test categorization: #### Core Test Categories

- `unit`: Unit tests for individual components
- `integration`: Integration tests for component interactions
- `benchmark`: Performance benchmarks
- `slow`: Long-running tests (can be skipped with `-m "not slow"`)
- `full_dynamics`: Tests using full nonlinear dynamics
- `determinism`: Tests for deterministic behavior validation
- `extra`: Optional/supplementary tests #### Advanced Test Categories
- `concurrent`: Thread-safety and concurrent execution tests
- `end_to_end`: Complete workflow validation tests
- `error_recovery`: Error handling and resilience tests
- `memory`: Memory management and resource tests
- `numerical_stability`: Numerical precision and stability tests
- `convergence`: Algorithm convergence analysis tests
- `numerical_robustness`: Robustness under numerical edge cases
- `property_based`: Hypothesis-driven property-based tests
- `statistical`: Statistical analysis and validation tests ### Configuration Files Primary pytest configuration: `config/testing/pytest.ini` ```ini
[pytest]
addopts = -q
filterwarnings = error
markers = # See full list in config/testing/pytest.ini
``` ## Test Execution Procedures ### Basic Test Execution ```bash
# Run all tests
python -m pytest tests/ # Run specific test categories
python -m pytest tests/ -m unit
python -m pytest tests/ -m integration
python -m pytest tests/ -m "not slow" # Run with coverage
python -m pytest tests/ --cov=src --cov-report=html # Run benchmarks only
python -m pytest tests/ -m benchmark --benchmark-only
``` ### Advanced Test Execution ```bash
# Parallel execution (if pytest-xdist installed)

python -m pytest tests/ -n auto # Verbose output with detailed reporting
python -m pytest tests/ -v --tb=long # Stop on first failure
python -m pytest tests/ -x # Run specific test files
python -m pytest tests/test_controllers/
python -m pytest tests/test_optimization/
``` ## Test Categories and Coverage Requirements ### Coverage Targets
- **Overall Coverage**: ≥85%
- **Critical Components**: ≥95% (controllers, dynamics, optimization)
- **Safety-Critical**: 100% (control laws, safety mechanisms) ### Quality Gates
1. All tests must pass
2. No pytest warnings
3. Coverage targets met
4. Performance benchmarks within acceptable ranges ## Troubleshooting Common Issues ### Unknown Pytest Marks
If you see warnings about unknown pytest marks:
1. Check that the mark is registered in `config/testing/pytest.ini`
2. Verify correct spelling and usage
3. Add new marks to the markers section if needed ### Collection Warnings
Collection warnings typically indicate:
- Test classes incorrectly detected (e.g., enum classes named TestType)
- Import errors in test files
- Missing dependencies ### Test Execution Failures
Common resolution steps:
1. Verify all dependencies are installed
2. Check working directory is project root
3. Ensure pytest configuration is properly loaded
4. Review test isolation and cleanup ## CI/CD Integration ### GitHub Actions Configuration
Test infrastructure integrates with GitHub Actions for:
- Automated test execution on pull requests
- Coverage reporting
- Performance regression detection
- Multi-platform testing ### Quality Assurance Integration
- Pre-commit hooks for code quality
- Automated test execution on changes
- Coverage collection and reporting
- Performance monitoring and alerts ## Best Practices ### Test Organization
- Mirror src/ structure in tests/
- Use descriptive test names and docstrings
- Group related tests in classes
- Implement proper test isolation ### Test Data Management
- Use fixtures for test data setup
- Implement proper cleanup in teardown
- Avoid hard-coded test data paths
- Use temporary directories for file operations ### Performance Testing
- Use pytest-benchmark for performance tests
- Set appropriate performance thresholds
- Monitor for performance regressions
- Include memory usage validation ## Support and Maintenance ### Regular Maintenance Tasks
1. Review and update pytest configuration
2. Monitor test execution times
3. Update coverage requirements
4. Review and optimize slow tests ### Getting Help
- Review this documentation first
- Check pytest official documentation
- Review test execution logs for specific errors
- Consult project-specific test patterns and examples