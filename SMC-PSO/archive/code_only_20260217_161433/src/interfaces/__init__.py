#======================================================================================\\
#============================= src/interfaces/__init__.py =============================\\
#======================================================================================\\

"""
Interfaces framework for control engineering applications.
This module provides interface systems for network communication, hardware abstraction,
HIL systems, data exchange, and monitoring capabilities designed for real-time
control systems and scientific computing applications.

Note: This module uses lazy imports to avoid loading heavy dependencies
(websockets, pyserial, etc.) unless actually needed.
"""

__version__ = "1.0.0"

# Define what's available for import without actually importing
__all__ = [
    # Hardware-in-the-Loop (HIL) System
    'EnhancedHILSystem', 'HILConfig', 'HILMode', 'TestScenario',
    'RealTimeScheduler', 'TimingConstraints', 'DeadlineMissHandler',
    'FaultInjector', 'FaultType', 'FaultScenario',
    'HILTestFramework', 'TestSuite', 'TestCase',
    'HILDataLogger', 'LoggingConfig',
    'SimulationBridge', 'ModelInterface',
    'HILControllerClient', 'PlantServer', 'run_client',

    # Data Exchange and Serialization
    'SerializationFormat', 'SerializerInterface', 'SerializationError',
    'JSONSerializer', 'MessagePackSerializer', 'PickleSerializer',
    'BinarySerializer', 'CompressionSerializer',
    'DataPacket',
    'DataSchema', 'SchemaValidator', 'ValidationError',
    'SerializerFactory', 'StreamingSerializer',

    # Monitoring and Diagnostics
    'HealthStatus', 'HealthCheck', 'ComponentHealth',
    'HealthMonitor', 'SystemHealthMonitor',
    'MetricType', 'Metric', 'MetricsCollector',
    'PerformanceMonitor', 'SystemMetricsCollector',
    'DiagnosticEngine', 'DiagnosticResult',
    'AlertManager', 'Alert', 'AlertRule', 'AlertLevel',
    'EmailNotificationHandler', 'LogNotificationHandler',
    'DashboardServer', 'MetricSeries', 'ChartConfig',

    # Hardware Abstraction
    'DeviceDriver', 'DeviceStatus', 'BaseDevice',
    'DeviceManager', 'HardwareInterfaceFactory',
    'SerialDevice', 'DAQInterface', 'SensorInterface',
    'ActuatorInterface', 'AnalogSensor', 'DigitalSensor',

    # Network Interfaces
    'TCPInterface', 'UDPInterface', 'WebSocketInterface',
    'HTTPInterface', 'NetworkInterfaceFactory',
    'MessageQueueInterface', 'ZeroMQInterface', 'RabbitMQInterface',
    'TCPServer', 'UDPServer', 'WebSocketServer',

    # Core interfaces
    'CommunicationProtocol', 'MessageProtocol', 'ConnectionProtocol',
    'InterfaceType', 'Message', 'ConnectionInfo', 'InterfaceConfig',
]

# Lazy import mapping: attribute name -> (module, import_from)
_LAZY_IMPORTS = {
    # HIL System
    'EnhancedHILSystem': ('hil', 'EnhancedHILSystem'),
    'HILConfig': ('hil', 'HILConfig'),
    'HILMode': ('hil', 'HILMode'),
    'TestScenario': ('hil', 'TestScenario'),
    'RealTimeScheduler': ('hil', 'RealTimeScheduler'),
    'TimingConstraints': ('hil', 'TimingConstraints'),
    'DeadlineMissHandler': ('hil', 'DeadlineMissHandler'),
    'FaultInjector': ('hil', 'FaultInjector'),
    'FaultType': ('hil', 'FaultType'),
    'FaultScenario': ('hil', 'FaultScenario'),
    'HILTestFramework': ('hil', 'HILTestFramework'),
    'TestSuite': ('hil', 'TestSuite'),
    'TestCase': ('hil', 'TestCase'),
    'HILDataLogger': ('hil', 'HILDataLogger'),
    'LoggingConfig': ('hil', 'LoggingConfig'),
    'SimulationBridge': ('hil', 'SimulationBridge'),
    'ModelInterface': ('hil', 'ModelInterface'),
    'HILControllerClient': ('hil', 'HILControllerClient'),
    'PlantServer': ('hil', 'PlantServer'),
    'run_client': ('hil', 'run_client'),

    # Data Exchange
    'SerializationFormat': ('data_exchange', 'SerializationFormat'),
    'SerializerInterface': ('data_exchange', 'SerializerInterface'),
    'SerializationError': ('data_exchange', 'SerializationError'),
    'JSONSerializer': ('data_exchange', 'JSONSerializer'),
    'MessagePackSerializer': ('data_exchange', 'MessagePackSerializer'),
    'PickleSerializer': ('data_exchange', 'PickleSerializer'),
    'BinarySerializer': ('data_exchange', 'BinarySerializer'),
    'CompressionSerializer': ('data_exchange', 'CompressionSerializer'),
    'DataPacket': ('data_exchange', 'DataPacket'),
    'DataSchema': ('data_exchange', 'DataSchema'),
    'SchemaValidator': ('data_exchange', 'SchemaValidator'),
    'ValidationError': ('data_exchange', 'ValidationError'),
    'SerializerFactory': ('data_exchange', 'SerializerFactory'),
    'StreamingSerializer': ('data_exchange', 'StreamingSerializer'),

    # Monitoring
    'HealthStatus': ('monitoring', 'HealthStatus'),
    'HealthCheck': ('monitoring', 'HealthCheck'),
    'ComponentHealth': ('monitoring', 'ComponentHealth'),
    'HealthMonitor': ('monitoring', 'HealthMonitor'),
    'SystemHealthMonitor': ('monitoring', 'SystemHealthMonitor'),
    'MetricType': ('monitoring', 'MetricType'),
    'Metric': ('monitoring', 'Metric'),
    'MetricsCollector': ('monitoring', 'MetricsCollector'),
    'PerformanceMonitor': ('monitoring', 'PerformanceMonitor'),
    'SystemMetricsCollector': ('monitoring', 'SystemMetricsCollector'),
    'DiagnosticEngine': ('monitoring', 'DiagnosticEngine'),
    'DiagnosticResult': ('monitoring', 'DiagnosticResult'),
    'AlertManager': ('monitoring', 'AlertManager'),
    'Alert': ('monitoring', 'Alert'),
    'AlertRule': ('monitoring', 'AlertRule'),
    'AlertLevel': ('monitoring', 'AlertLevel'),
    'EmailNotificationHandler': ('monitoring', 'EmailNotificationHandler'),
    'LogNotificationHandler': ('monitoring', 'LogNotificationHandler'),
    'DashboardServer': ('monitoring', 'DashboardServer'),
    'MetricSeries': ('monitoring', 'MetricSeries'),
    'ChartConfig': ('monitoring', 'ChartConfig'),

    # Hardware
    'DeviceDriver': ('hardware', 'DeviceDriver'),
    'DeviceStatus': ('hardware', 'DeviceStatus'),
    'BaseDevice': ('hardware', 'BaseDevice'),
    'DeviceManager': ('hardware', 'DeviceManager'),
    'HardwareInterfaceFactory': ('hardware', 'HardwareInterfaceFactory'),
    'SerialDevice': ('hardware', 'SerialDevice'),
    'DAQInterface': ('hardware', 'DAQInterface'),
    'SensorInterface': ('hardware', 'SensorInterface'),
    'ActuatorInterface': ('hardware', 'ActuatorInterface'),
    'AnalogSensor': ('hardware', 'AnalogSensor'),
    'DigitalSensor': ('hardware', 'DigitalSensor'),

    # Network
    'TCPInterface': ('network', 'TCPInterface'),
    'UDPInterface': ('network', 'UDPInterface'),
    'WebSocketInterface': ('network', 'WebSocketInterface'),
    'HTTPInterface': ('network', 'HTTPInterface'),
    'NetworkInterfaceFactory': ('network', 'NetworkInterfaceFactory'),
    'MessageQueueInterface': ('network', 'MessageQueueInterface'),
    'ZeroMQInterface': ('network', 'ZeroMQInterface'),
    'RabbitMQInterface': ('network', 'RabbitMQInterface'),
    'TCPServer': ('network', 'TCPServer'),
    'UDPServer': ('network', 'UDPServer'),
    'WebSocketServer': ('network', 'WebSocketServer'),

    # Core
    'CommunicationProtocol': ('core', 'CommunicationProtocol'),
    'MessageProtocol': ('core', 'MessageProtocol'),
    'ConnectionProtocol': ('core', 'ConnectionProtocol'),
    'InterfaceType': ('core', 'InterfaceType'),
    'Message': ('core', 'Message'),
    'ConnectionInfo': ('core', 'ConnectionInfo'),
    'InterfaceConfig': ('core', 'InterfaceConfig'),
}

# Cache for imported modules
_imported_cache = {}


def __getattr__(name):
    """
    Lazy import attributes on demand.

    This function is called when an attribute is not found in the module's namespace.
    It allows us to defer imports until they're actually needed, avoiding loading
    heavy dependencies (websockets, pyserial, etc.) at module import time.
    """
    if name in _LAZY_IMPORTS:
        # Check cache first
        if name in _imported_cache:
            return _imported_cache[name]

        # Import the module and get the attribute
        module_name, attr_name = _LAZY_IMPORTS[name]
        try:
            from importlib import import_module
            module = import_module(f'.{module_name}', package='interfaces')
            attr = getattr(module, attr_name)
            _imported_cache[name] = attr
            return attr
        except ImportError as e:
            raise AttributeError(
                f"Cannot import '{name}' from interfaces.{module_name}. "
                f"This may be due to missing optional dependencies. "
                f"Original error: {e}"
            )

    raise AttributeError(f"module 'interfaces' has no attribute '{name}'")


def __dir__():
    """Return list of available attributes for tab completion."""
    return list(__all__) + ['__version__', 'get_framework_info']


def get_framework_info():
    """Get information about the available interfaces framework components."""
    return {
        "version": __version__,
        "modules": {
            "hil": "Hardware-in-the-Loop system with real-time capabilities",
            "data_exchange": "Data serialization and exchange framework",
            "monitoring": "System monitoring, diagnostics, and alerting",
            "hardware": "Hardware abstraction layer with device drivers",
            "network": "Network interfaces for TCP/UDP/WebSocket communication",
            "core": "Core interface protocols and data types"
        },
        "features": [
            "Hardware-in-the-Loop testing framework",
            "Multi-format data serialization",
            "Real-time system monitoring",
            "Hardware device abstraction",
            "Network communication interfaces",
            "Performance optimization",
            "Scientific computing integration"
        ],
        "total_components": len(__all__)
    }
