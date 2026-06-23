# integration.production_readiness

**Source:** `src\integration\production_readiness.py`

## Module Overview Production

readiness scoring system with integrated pytest results and system health monitoring

. This module provides production readiness assessment by integrating


pytest results, coverage monitoring, compatibility analysis, and system health metrics
into a unified scoring framework aligned with CLAUDE.md quality standards. ## Complete Source Code ```{literalinclude} ../../../src/integration/production_readiness.py
:language: python
:linenos:
```

---

## Classes

### `ReadinessLevel`

**Inherits from:** `Enum` Production readiness levels with deployment recommendations.

#### Source Code ```

{literalinclude} ../../../src/integration/production_readiness.py
:language: python
:pyobject: ReadinessLevel
:linenos:
```

---

## `ComponentType`

**Inherits from:** `Enum` System component types for targeted assessment.

### Source Code ```

{literalinclude} ../../../src/integration/production_readiness.py

:language: python
:pyobject: ComponentType
:linenos:
```

### `QualityGate`

Represents a production quality gate with threshold and current value.

#### Source Code ```

{literalinclude} ../../../src/integration/production_readiness.py
:language: python
:pyobject: QualityGate
:linenos:
```

### `ReadinessAssessment`

production readiness assessment results.

#### Source Code ```

{literalinclude} ../../../src/integration/production_readiness.py

:language: python
:pyobject: ReadinessAssessment
:linenos:
```

### `ProductionReadinessScorer`

production readiness scoring system with pytest integration. This class integrates pytest results, coverage monitoring, compatibility analysis,
and system health metrics to provide authoritative production readiness scoring
aligned with CLAUDE.md quality standards and research-grade requirements. #### Source Code ```{literalinclude} ../../../src/integration/production_readiness.py
:language: python
:pyobject: ProductionReadinessScorer
:linenos:
``` #### Methods (21) ##### `__init__(self, project_root)` Initialize production readiness scorer with quality gates. [View full source →](#method-productionreadinessscorer-__init__) ##### `_init_database(self)` Initialize SQLite database for production readiness tracking. [View full source →](#method-productionreadinessscorer-_init_database) ##### `assess_production_readiness(self, run_tests, include_benchmarks, quick_mode)` Perform production readiness assessment. [View full source →](#method-productionreadinessscorer-assess_production_readiness) ##### `_gather_coverage_metrics(self)` Gather current coverage metrics from monitoring system. [View full source →](#method-productionreadinessscorer-_gather_coverage_metrics) ##### `_calculate_testing_score(self, pytest_results)` Calculate testing component score based on pytest results. [View full source →](#method-productionreadinessscorer-_calculate_testing_score) ##### `_calculate_coverage_score(self, coverage_metrics)` Calculate coverage component score. [View full source →](#method-productionreadinessscorer-_calculate_coverage_score) ##### `_calculate_compatibility_score(self, compatibility_analysis)` Calculate compatibility component score. [View full source →](#method-productionreadinessscorer-_calculate_compatibility_score) ##### `_calculate_performance_score(self, pytest_results, include_benchmarks)` Calculate performance component score. [View full source →](#method-productionreadinessscorer-_calculate_performance_score) ##### `_calculate_safety_score(self, coverage_metrics, pytest_results)` Calculate safety component score. [View full source →](#method-productionreadinessscorer-_calculate_safety_score) ##### `_calculate_documentation_score(self)` Calculate documentation component score. [View full source →](#method-productionreadinessscorer-_calculate_documentation_score) ##### `_evaluate_quality_gates(self, pytest_results, coverage_metrics, compatibility_analysis)` Evaluate all quality gates against current system state. [View full source →](#method-productionreadinessscorer-_evaluate_quality_gates) ##### `_get_gate_current_value(self, gate_name, pytest_results, coverage_metrics, compatibility_analysis)` Get current value for a specific quality gate. [View full source →](#method-productionreadinessscorer-_get_gate_current_value) ##### `_get_gate_recommendations(self, gate_name, current_value, threshold)` Get recommendations for improving a specific quality gate. [View full source →](#method-productionreadinessscorer-_get_gate_recommendations) ##### `_calculate_overall_score(self, quality_gates)` Calculate weighted overall readiness score. [View full source →](#method-productionreadinessscorer-_calculate_overall_score) ##### `_determine_readiness_level(self, overall_score, quality_gates)` Determine production readiness level based on score and gate status. [View full source →](#method-productionreadinessscorer-_determine_readiness_level) ##### `_identify_blocking_issues(self, quality_gates)` Identify blocking issues preventing production deployment. [View full source →](#method-productionreadinessscorer-_identify_blocking_issues) ##### `_generate_recommendations(self, quality_gates, readiness_level)` Generate recommendations for improving readiness. [View full source →](#method-productionreadinessscorer-_generate_recommendations) ##### `_calculate_confidence_level(self, overall_score, quality_gates)` Calculate confidence level in readiness assessment. [View full source →](#method-productionreadinessscorer-_calculate_confidence_level) ##### `_analyze_improvement_trend(self, current_score)` Analyze improvement trend based on historical data. [View full source →](#method-productionreadinessscorer-_analyze_improvement_trend) ##### `_get_historical_comparison(self)` Get historical comparison data. [View full source →](#method-productionreadinessscorer-_get_historical_comparison) ##### `_store_assessment(self, assessment)` Store assessment in database for historical tracking. [View full source →](#method-productionreadinessscorer-_store_assessment)

---

## Functions

### `main()`

Main entry point for production readiness assessment.

#### Source Code ```

{literalinclude} ../../../src/integration/production_readiness.py

:language: python
:pyobject: main
:linenos:
```

---

## Dependencies This module imports: - `import sys`
- `import json`
- `import time`
- `import sqlite3`
- `from pathlib import Path`
- `from typing import Dict, List, Any, Optional, Tuple`
- `from dataclasses import dataclass, field, asdict`
- `from datetime import datetime, timedelta`
- `from enum import Enum`
- `import logging`
