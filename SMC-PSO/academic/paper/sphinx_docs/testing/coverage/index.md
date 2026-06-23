# Coverage & Quality Gates

This section documents the test coverage analysis system and quality gates for the DIP-SMC-PSO project.

## Contents

- [Coverage Analysis & Quality Gates](README.md) - Complete coverage documentation, metrics, commands, and quality gate integration

## Quick Reference

### Current Coverage Status
- **Overall Coverage**: 25.9% → Target: 85%
- **Critical Components**: Measurement pending → Target: 95%
- **Safety-Critical**: Measurement pending → Target: 100%

### Run Coverage Analysis
```bash
# Generate coverage reports
python -m pytest tests/ \
  --cov=src \
  --cov-report=html:validation/htmlcov \
  --cov-report=xml:validation/coverage.xml \
  --cov-report=term-missing
```

### View Reports
- **HTML Report**: `validation/htmlcov/index.html`
- **XML Report**: `validation/coverage.xml`
- **JSON Report**: `validation/coverage.json`

For complete documentation, see [Coverage Analysis & Quality Gates](README.md).
---

**Navigation**: Return to [Master Navigation Hub](../NAVIGATION.md) | Browse all [Documentation Categories](../index.md)
