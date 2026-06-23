# interfaces.monitoring.dashboard

**Source:** `src\interfaces\monitoring\dashboard.py`

## Module Overview Real-time

monitoring dashboard for interface systems

.


This module provides dashboard features including
real-time metrics visualization, interactive charts, system status
displays, alert management interface, and customizable monitoring
views for all interface components. ## Complete Source Code ```{literalinclude} ../../../src/interfaces/monitoring/dashboard.py
:language: python
:linenos:
```

---

## Classes

### `MetricSeries`

Time series data for a metric.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/dashboard.py
:language: python
:pyobject: MetricSeries
:linenos:
```

---

## `ChartConfig`

Configuration for dashboard charts.

### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/dashboard.py

:language: python
:pyobject: ChartConfig
:linenos:
```

### `DashboardLayout`

Dashboard layout configuration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/dashboard.py
:language: python
:pyobject: DashboardLayout
:linenos:
```

### `DashboardServer`

Web-based dashboard server.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/dashboard.py

:language: python
:pyobject: DashboardServer
:linenos:
``` #### Methods (22) ##### `__init__(self, host, port)` [View full source →](#method-dashboardserver-__init__) ##### `_create_default_layout(self)` Create default dashboard layout. [View full source →](#method-dashboardserver-_create_default_layout) ##### `register_metric(self, name, unit, description, color)` Register a new metric for monitoring. [View full source →](#method-dashboardserver-register_metric) ##### `update_metric(self, name, value, timestamp)` Update metric value. [View full source →](#method-dashboardserver-update_metric) ##### `update_metrics(self, metrics, timestamp)` Update multiple metrics at once. [View full source →](#method-dashboardserver-update_metrics) ##### `get_metric_data(self, name, duration_minutes)` Get metric data for the last N minutes. [View full source →](#method-dashboardserver-get_metric_data) ##### `get_latest_metrics(self)` Get latest values for all metrics. [View full source →](#method-dashboardserver-get_latest_metrics) ##### `create_layout(self, name, layout)` Create a new dashboard layout. [View full source →](#method-dashboardserver-create_layout) ##### `set_current_layout(self, name)` Set the current active layout. [View full source →](#method-dashboardserver-set_current_layout) ##### `generate_html_dashboard(self)` Generate HTML dashboard. [View full source →](#method-dashboardserver-generate_html_dashboard) ##### `_generate_chart_html(self, layout)` Generate HTML for charts. [View full source →](#method-dashboardserver-_generate_chart_html) ##### `_generate_chart_javascript(self, layout)` Generate JavaScript for charts. [View full source →](#method-dashboardserver-_generate_chart_javascript) ##### `_generate_line_chart_js(self, chart_id, chart)` Generate JavaScript for line charts. [View full source →](#method-dashboardserver-_generate_line_chart_js) ##### `_generate_gauge_chart_js(self, chart_id, chart)` Generate JavaScript for gauge charts. [View full source →](#method-dashboardserver-_generate_gauge_chart_js) ##### `_generate_bar_chart_js(self, chart_id, chart)` Generate JavaScript for bar charts. [View full source →](#method-dashboardserver-_generate_bar_chart_js) ##### `start_server(self)` Start the dashboard web server. [View full source →](#method-dashboardserver-start_server) ##### `_handle_dashboard(self, request)` Handle dashboard page request. [View full source →](#method-dashboardserver-_handle_dashboard) ##### `_handle_metrics_api(self, request)` Handle metrics API request. [View full source →](#method-dashboardserver-_handle_metrics_api) ##### `_handle_export_api(self, request)` Handle data export API request. [View full source →](#method-dashboardserver-_handle_export_api) ##### `_handle_layouts_api(self, request)` Handle layouts API request. [View full source →](#method-dashboardserver-_handle_layouts_api) ##### `_handle_create_layout_api(self, request)` Handle create layout API request. [View full source →](#method-dashboardserver-_handle_create_layout_api) ##### `stop_server(self)` Stop the dashboard server. [View full source →](#method-dashboardserver-stop_server)

### `DashboardManager`

Manager for multiple dashboard instances.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/dashboard.py
:language: python
:pyobject: DashboardManager
:linenos:
``` #### Methods (6) ##### `__init__(self)` [View full source →](#method-dashboardmanager-__init__) ##### `create_dashboard(self, name, host, port)` Create a new dashboard instance. [View full source →](#method-dashboardmanager-create_dashboard) ##### `get_dashboard(self, name)` Get dashboard by name. [View full source →](#method-dashboardmanager-get_dashboard) ##### `remove_dashboard(self, name)` Remove dashboard instance. [View full source →](#method-dashboardmanager-remove_dashboard) ##### `start_all_dashboards(self)` Start all dashboard servers. [View full source →](#method-dashboardmanager-start_all_dashboards) ##### `stop_all_dashboards(self)` Stop all dashboard servers. [View full source →](#method-dashboardmanager-stop_all_dashboards)

---

## Functions

### `create_system_dashboard()`

Create default system monitoring dashboard.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/dashboard.py

:language: python
:pyobject: create_system_dashboard
:linenos:
```

### `create_performance_dashboard()`

Create performance monitoring dashboard.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/dashboard.py
:language: python
:pyobject: create_performance_dashboard
:linenos:
```

### `start_monitoring_dashboards()`

Start all monitoring dashboards.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/dashboard.py

:language: python
:pyobject: start_monitoring_dashboards
:linenos:
```

---

## Dependencies This module imports: - `import asyncio`
- `import json`
- `import logging`
- `import time`
- `import webbrowser`
- `from collections import defaultdict, deque`
- `from dataclasses import dataclass, field`
- `from datetime import datetime, timedelta`
- `from pathlib import Path`
- `from typing import Any, Dict, List, Optional, Set, Tuple, Callable` *... and 1 more*
