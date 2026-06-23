#======================================================================================\\\
#======================= src/interfaces/monitoring/__init__.py ========================\\\
#======================================================================================\\\

"""
Comprehensive monitoring and diagnostics system for the interfaces framework.
This module provides real-time monitoring, health checks, performance metrics,
system diagnostics, alerting, and dashboard capabilities for all interface
components including network communication, hardware devices, and HIL systems.
"""

from .health_monitor import (
    HealthStatus, HealthCheck, ComponentHealth,
    HealthMonitor, SystemHealthMonitor
)
from .metrics_collector import (
    MetricType, Metric, MetricsCollector,
    SystemMetricsCollector, create_metric
)
from .performance_tracker import (
    PerformanceMonitor, SerializationMetrics
)
from .diagnostics import (
    DiagnosticLevel, DiagnosticResult, DiagnosticCheck,
    DiagnosticEngine, TroubleshootingAssistant
)
from .alerting import (
    AlertLevel, Alert, AlertRule, AlertManager,
    NotificationChannel, EmailNotificationHandler, LogNotificationHandler
)
from .dashboard import (
    ChartConfig, DashboardManager,
    MetricSeries, DashboardLayout, DashboardServer
)
# Note: system_monitor module not found - commenting out for now
# from .system_monitor import (
#     SystemMonitor, MonitoringConfig,
#     InterfaceSystemMonitor
# )

__all__ = [
    # Health monitoring
    'HealthStatus', 'HealthCheck', 'ComponentHealth',
    'HealthMonitor', 'SystemHealthMonitor',

    # Metrics collection
    'MetricType', 'Metric', 'MetricsCollector',
    'SystemMetricsCollector', 'create_metric',

    # Performance tracking
    'PerformanceMonitor', 'SerializationMetrics',

    # Diagnostics
    'DiagnosticLevel', 'DiagnosticResult', 'DiagnosticCheck',
    'DiagnosticEngine', 'TroubleshootingAssistant',

    # Alerting
    'AlertLevel', 'Alert', 'AlertRule', 'AlertManager',
    'NotificationChannel', 'EmailNotificationHandler', 'LogNotificationHandler',

    # Dashboard
    'ChartConfig', 'DashboardManager',
    'MetricSeries', 'DashboardLayout', 'DashboardServer',

    # System monitoring (commented out - module not found)
    # 'SystemMonitor', 'MonitoringConfig',
    # 'InterfaceSystemMonitor'
]