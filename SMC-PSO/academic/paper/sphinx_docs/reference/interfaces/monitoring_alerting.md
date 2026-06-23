# interfaces.monitoring.alerting

**Source:** `src\interfaces\monitoring\alerting.py`

## Module Overview Intelligent

alerting system for interface monitoring

.


This module provides alerting features including
rule-based alerts, adaptive thresholds, notification channels,
alert correlation, and escalation management for proactive
monitoring of all interface components. ## Complete Source Code ```{literalinclude} ../../../src/interfaces/monitoring/alerting.py
:language: python
:linenos:
```

---

## Classes

### `AlertLevel`

**Inherits from:** `Enum` Alert severity levels.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py
:language: python
:pyobject: AlertLevel
:linenos:
```

---

## `AlertStatus`

**Inherits from:** `Enum` Alert lifecycle status.

### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py

:language: python
:pyobject: AlertStatus
:linenos:
```

### `NotificationChannel`

**Inherits from:** `Enum` Available notification channels.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py
:language: python
:pyobject: NotificationChannel
:linenos:
```

### `Alert`

Alert message with metadata.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py

:language: python
:pyobject: Alert
:linenos:
```

### `AlertRule`

Rule for triggering alerts.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py
:language: python
:pyobject: AlertRule
:linenos:
```

### `NotificationConfig`

Configuration for notification channels.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py

:language: python
:pyobject: NotificationConfig
:linenos:
```

### `AlertCondition`

**Inherits from:** `ABC` Base class for alert conditions.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py
:language: python
:pyobject: AlertCondition
:linenos:
``` #### Methods (1) ##### `evaluate(self, metrics)` Evaluate condition against metrics. [View full source →](#method-alertcondition-evaluate)

### `ThresholdCondition`

**Inherits from:** `AlertCondition` Simple threshold-based condition.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py

:language: python
:pyobject: ThresholdCondition
:linenos:
``` #### Methods (2) ##### `__init__(self, metric_name, threshold, operator)` [View full source →](#method-thresholdcondition-__init__) ##### `evaluate(self, metrics)` [View full source →](#method-thresholdcondition-evaluate)

### `CompositeCondition`

**Inherits from:** `AlertCondition` Composite condition combining multiple conditions.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py
:language: python
:pyobject: CompositeCondition
:linenos:
``` #### Methods (2) ##### `__init__(self, conditions, operator)` [View full source →](#method-compositecondition-__init__) ##### `evaluate(self, metrics)` [View full source →](#method-compositecondition-evaluate)

### `TrendCondition`

**Inherits from:** `AlertCondition` Trend-based condition for detecting patterns.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py

:language: python
:pyobject: TrendCondition
:linenos:
``` #### Methods (2) ##### `__init__(self, metric_name, window_size, trend_threshold)` [View full source →](#method-trendcondition-__init__) ##### `evaluate(self, metrics)` [View full source →](#method-trendcondition-evaluate)

### `NotificationHandler`

**Inherits from:** `ABC` Base class for notification handlers.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py
:language: python
:pyobject: NotificationHandler
:linenos:
``` #### Methods (4) ##### `__init__(self, config)` [View full source →](#method-notificationhandler-__init__) ##### `can_send(self, alert)` Check if notification can be sent (rate limiting). [View full source →](#method-notificationhandler-can_send) ##### `send_notification(self, alert)` Send notification for alert. [View full source →](#method-notificationhandler-send_notification) ##### `record_notification(self, alert)` Record that notification was sent. [View full source →](#method-notificationhandler-record_notification)

### `EmailNotificationHandler`

**Inherits from:** `NotificationHandler` Email notification handler.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py

:language: python
:pyobject: EmailNotificationHandler
:linenos:
``` #### Methods (1) ##### `send_notification(self, alert)` [View full source →](#method-emailnotificationhandler-send_notification)

### `WebhookNotificationHandler`

**Inherits from:** `NotificationHandler` Webhook notification handler.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py
:language: python
:pyobject: WebhookNotificationHandler
:linenos:
``` #### Methods (1) ##### `send_notification(self, alert)` [View full source →](#method-webhooknotificationhandler-send_notification)

### `LogNotificationHandler`

**Inherits from:** `NotificationHandler` Log-based notification handler.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py

:language: python
:pyobject: LogNotificationHandler
:linenos:
``` #### Methods (1) ##### `send_notification(self, alert)` [View full source →](#method-lognotificationhandler-send_notification)

### `AlertManager`

Main alert management system.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py
:language: python
:pyobject: AlertManager
:linenos:
``` #### Methods (21) ##### `__init__(self)` [View full source →](#method-alertmanager-__init__) ##### `register_notification_handler(self, channel, handler)` Register a notification handler. [View full source →](#method-alertmanager-register_notification_handler) ##### `add_rule(self, rule, condition)` Add an alert rule with condition. [View full source →](#method-alertmanager-add_rule) ##### `remove_rule(self, rule_id)` Remove an alert rule. [View full source →](#method-alertmanager-remove_rule) ##### `update_metrics(self, metrics)` Update metrics for alert evaluation. [View full source →](#method-alertmanager-update_metrics) ##### `get_current_metrics(self)` Get current metrics values. [View full source →](#method-alertmanager-get_current_metrics) ##### `evaluate_rules(self)` Evaluate all alert rules against current metrics. [View full source →](#method-alertmanager-evaluate_rules) ##### `_create_alert(self, rule, metrics)` Create alert from rule and metrics. [View full source →](#method-alertmanager-_create_alert) ##### `_send_notifications(self, alert, rule)` Send notifications for alert. [View full source →](#method-alertmanager-_send_notifications) ##### `acknowledge_alert(self, alert_id, acknowledged_by)` Acknowledge an alert. [View full source →](#method-alertmanager-acknowledge_alert) ##### `resolve_alert(self, alert_id)` Resolve an alert. [View full source →](#method-alertmanager-resolve_alert) ##### `suppress_alert(self, alert_id, duration)` Suppress an alert for a duration. [View full source →](#method-alertmanager-suppress_alert) ##### `get_active_alerts(self)` Get all active alerts. [View full source →](#method-alertmanager-get_active_alerts) ##### `get_alerts_by_level(self, level)` Get alerts by severity level. [View full source →](#method-alertmanager-get_alerts_by_level) ##### `get_alerts_by_source(self, source)` Get alerts by source. [View full source →](#method-alertmanager-get_alerts_by_source) ##### `get_alert_statistics(self)` Get alert statistics. [View full source →](#method-alertmanager-get_alert_statistics) ##### `check_escalations(self)` Check for alerts that need escalation. [View full source →](#method-alertmanager-check_escalations) ##### `cleanup_resolved_alerts(self, retention_hours)` Clean up old resolved alerts. [View full source →](#method-alertmanager-cleanup_resolved_alerts) ##### `start_monitoring(self)` Start continuous alert monitoring. [View full source →](#method-alertmanager-start_monitoring) ##### `stop_monitoring(self)` Stop alert monitoring. [View full source →](#method-alertmanager-stop_monitoring) ##### `export_alerts(self, file_path, format)` Export alerts to file. [View full source →](#method-alertmanager-export_alerts)

---

## Functions

### `create_threshold_rule(name, metric_name, threshold, level, operator, channels)`

Create a simple threshold-based alert rule.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py

:language: python
:pyobject: create_threshold_rule
:linenos:
```

### `create_composite_rule(name, conditions, level, logic, channels)`

Create a composite alert rule with multiple conditions.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py
:language: python
:pyobject: create_composite_rule
:linenos:
```

### `setup_default_alerts()`

Set up default system alerts.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py

:language: python
:pyobject: setup_default_alerts
:linenos:
```

### `configure_email_notifications(smtp_server, smtp_port, username, password, from_address, to_addresses)`

Configure email notification handler.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py
:language: python
:pyobject: configure_email_notifications
:linenos:
```

### `configure_webhook_notifications(url, headers)`

Configure webhook notification handler.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py

:language: python
:pyobject: configure_webhook_notifications
:linenos:
```

### `configure_log_notifications(log_level, logger_name)`

Configure log notification handler.

#### Source Code ```

{literalinclude} ../../../src/interfaces/monitoring/alerting.py
:language: python
:pyobject: configure_log_notifications
:linenos:
```

---

## Dependencies This module imports: - `import asyncio`

- `import json`
- `import logging`
- `import smtplib`
- `import time`
- `from abc import ABC, abstractmethod`
- `from collections import defaultdict, deque`
- `from dataclasses import dataclass, field`
- `from datetime import datetime, timedelta`
- `from email.mime.multipart import MIMEMultipart` *... and 5 more*
