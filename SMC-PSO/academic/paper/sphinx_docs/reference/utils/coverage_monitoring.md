# utils.coverage.monitoring

**Source:** `src\utils\coverage\monitoring.py`

## Module Overview

Real-time coverage monitoring and alerting system for GitHub Issue #9.

This module provides advanced coverage monitoring with trend analysis,
automated alerting, and integration with the CLAUDE.md quality standards.

## Complete Source Code

```{literalinclude} ../../../src/utils/coverage/monitoring.py
:language: python
:linenos:
```



## Classes

### `CoverageMetrics`

Coverage metrics data structure with mathematical validation.

#### Source Code

```{literalinclude} ../../../src/utils/coverage/monitoring.py
:language: python
:pyobject: CoverageMetrics
:linenos:
```

#### Methods (1)

##### `__post_init__(self)`

Validate coverage metrics after initialization.

[View full source →](#method-coveragemetrics-__post_init__)



### `CoverageMonitor`

Real-time coverage monitoring with scientific trend analysis.

Implements mathematical analysis of coverage trends with automated
alerting for threshold violations and quality gate enforcement.

#### Source Code

```{literalinclude} ../../../src/utils/coverage/monitoring.py
:language: python
:pyobject: CoverageMonitor
:linenos:
```

#### Methods (9)

##### `__init__(self, db_path)`

Initialize coverage monitor with persistent storage.

[View full source →](#method-coveragemonitor-__init__)

##### `init_database(self)`

Initialize SQLite database for coverage metrics storage.

[View full source →](#method-coveragemonitor-init_database)

##### `record_coverage_run(self, coverage_data)`

Record coverage metrics from test run with validation.

[View full source →](#method-coveragemonitor-record_coverage_run)

##### `get_recent_metrics(self, window_size)`

Retrieve recent coverage metrics from database.

[View full source →](#method-coveragemonitor-get_recent_metrics)

##### `analyze_coverage_trends(self, window_size)`

Analyze coverage trends using mathematical regression analysis.

[View full source →](#method-coveragemonitor-analyze_coverage_trends)

##### `_generate_trend_recommendation(self, slope, velocity)`

Generate actionable recommendations based on trend analysis.

[View full source →](#method-coveragemonitor-_generate_trend_recommendation)

##### `check_quality_gates(self, latest_metrics)`

Check current coverage against quality gate thresholds.

[View full source →](#method-coveragemonitor-check_quality_gates)

##### `generate_coverage_alert(self, alert_level)`

Generate coverage alert with detailed analysis.

[View full source →](#method-coveragemonitor-generate_coverage_alert)

##### `export_metrics_json(self, output_path, days)`

Export coverage metrics to JSON for external analysis.

[View full source →](#method-coveragemonitor-export_metrics_json)



## Functions

### `record_pytest_coverage(coverage_xml_path, monitor)`

Record coverage metrics from pytest-cov XML output.

Args:
    coverage_xml_path: Path to coverage.xml file
    monitor: Optional CoverageMonitor instance

Returns:
    Recorded CoverageMetrics

#### Source Code

```{literalinclude} ../../../src/utils/coverage/monitoring.py
:language: python
:pyobject: record_pytest_coverage
:linenos:
```



## Dependencies

This module imports:

- `import time`
- `import json`
- `import sqlite3`
- `from dataclasses import dataclass, asdict`
- `from typing import Dict, List, Optional, Tuple`
- `from pathlib import Path`
- `import numpy as np`
- `from datetime import datetime, timedelta`
- `import logging`
