#==========================================================================================\
#==================== docs/workflows/pytest_testing_workflow.md ====================\
#==========================================================================================\ # Pytest Testing Workflow
# Quick Start Guide for Running Tests **Document Version**: 1.0

**Last Updated**: 2025-09-29
**Target Audience**: Developers, New Contributors

---

## 🚀 Quick Start (2-Minute Workflow) ### Essential Commands ```bash

# 1. Run all tests (basic command)

pytest # 2. Run tests with coverage
pytest --cov=src --cov-report=html # 3. Run specific test categories
pytest -m "unit" -v # Unit tests only
pytest -m "integration and not slow" # Fast integration tests
pytest -m "benchmark" --benchmark-only # Performance benchmarks # 4. Run specific test files
pytest tests/test_controllers/test_classical_smc.py -v
pytest tests/test_optimization/ -v # 5. Debug failing tests
pytest --tb=short # Short traceback
pytest -x # Stop on first failure
pytest --lf # Re-run last failed tests
```

---

## 📋 Development Workflow ### Pre-Commit Testing (Quick Feedback)
```bash
# Fast development cycle (~30 seconds)

pytest -m "unit" --tb=short
``` ### Before Pull Request
```bash
# validation (~5 minutes)

pytest -m "integration and not slow" -v
pytest --cov=src --cov-fail-under=85
``` ### Full Validation
```bash
# Complete test suite (~15-30 minutes)

pytest --cov=src --cov-report=html
pytest -m "benchmark" --benchmark-only
```

---

## 🎯 Test Categories | Category | Command | Purpose | Duration |
|----------|---------|---------|----------|
| **Unit** | `pytest -m "unit"` | Individual component testing | ~30s |
| **Integration** | `pytest -m "integration"` | End-to-end workflows | ~5min |
| **Scientific** | `pytest -m "convergence"` | Algorithm validation | ~2min |
| **Performance** | `pytest -m "benchmark"` | Regression detection | ~3min |
| **Coverage** | `pytest --cov=src` | Code coverage analysis | ~2min |

---

## 🔧 Common Use Cases ### Testing Specific Components
```bash
# Test controllers

pytest tests/test_controllers/ -v # Test PSO optimization
pytest tests/test_optimization/ -v # Test dynamics models
pytest tests/test_physics/ -v # Test configuration system
pytest tests/test_config/ -v
``` ### Coverage Analysis
```bash
# Generate HTML coverage report

pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser # Terminal coverage with missing lines

pytest --cov=src --cov-report=term-missing # Critical component coverage (must be ≥95%)
pytest tests/test_controllers/ --cov=src/controllers --cov-fail-under=95
``` ### Performance Testing
```bash
# Run performance benchmarks

pytest -m "benchmark" --benchmark-only # Compare with baseline
pytest -m "benchmark" --benchmark-compare=baseline # Save new baseline
pytest -m "benchmark" --benchmark-save=new_baseline
```

---

## ⚡ Quick Troubleshooting | Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'src'` | Ensure working directory is project root |
| `ValidationError: config validation failed` | Run `python -c "import src.config; print('Config OK')"` |
| Tests pass locally but fail in CI | Check Python version compatibility |
| Matplotlib backend errors | Set `export MPLBACKEND=Agg` |
| Slow test performance | Use `pytest -m "not slow"` for development |

## 📚 Detailed Documentation References

For testing information, see: - **[📖 Complete Test Execution Guide](../test_execution_guide.md)** - 733-line guide covering: - Scientific validation testing (convergence, stability, robustness) - Advanced execution patterns and CI/CD integration - Performance benchmarking and regression detection - Troubleshooting guide and best practices - **[📋 Basic Testing Guide](../TESTING.md)** - Golden-path testing workflow and architecture - **[🔧 Coverage Documentation](../testing/)** - Coverage analysis and quality gates - **[🚀 Integration Workflows](./complete_integration_guide.md)** - End-to-end system workflows

---

## 🎓 Learning Path ### New Developers
1. Start with this **Quick Start** workflow
2. Read **[Basic Testing Guide](../TESTING.md)** for fundamentals
3. Explore **[Complete Test Execution Guide](../test_execution_guide.md)** for advanced usage ### Research Scientists
1. Focus on **[Scientific Validation](../test_execution_guide.md#scientific-validation-tests)** section
2. Use **[Statistical Testing](../test_execution_guide.md#statistical-validation-tests)** for research validation
3. uses **[Property-Based Testing](../test_execution_guide.md#property-based-testing)** for theoretical properties ### CI/CD Engineers
1. Review **[CI/CD Integration Examples](../test_execution_guide.md#cicd-integration-examples)**
2. Implement **[Quality Gate Scripts](../test_execution_guide.md#quality-gate-script)**
3. Configure **[Pre-commit Hooks](../test_execution_guide.md#pre-commit-hook-configuration)**

---

## ✅ Success Criteria **Your tests are working correctly when:** - ✅ `pytest` runs without import errors
- ✅ Coverage reports generate successfully
- ✅ Performance benchmarks execute without regression
- ✅ Scientific validation tests pass (convergence, stability)
- ✅ All test categories complete within expected timeframes **Need Help?** Check the **[Complete Test Execution Guide](../test_execution_execution_guide.md)** for detailed troubleshooting and advanced patterns.

---

**Document Authority**: Documentation Expert Agent
**Technical Review**: Integration Coordinator
**Quality Assurance**: Ultimate Orchestrator **🤖 Generated with [Claude Code](https://claude.ai/code)** **Co-Authored-By: Claude <noreply@anthropic.com>**
