# interfaces.__init__

**Source:** `src\interfaces\__init__.py`

## Module Overview

Interfaces framework for control engineering applications.
This module provides interface systems for network communication, hardware abstraction,
HIL systems, data exchange, and monitoring features designed for real-time
control systems and scientific computing applications.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/__init__.py
:language: python
:linenos:
```



## Functions

### `get_framework_info()`

Get information about the available interfaces framework components.

#### Source Code

```{literalinclude} ../../../src/interfaces/__init__.py
:language: python
:pyobject: get_framework_info
:linenos:
```



### `create_basic_interfaces_manager()`

Create a basic manager for core interface components.

#### Source Code

```{literalinclude} ../../../src/interfaces/__init__.py
:language: python
:pyobject: create_basic_interfaces_manager
:linenos:
```



### `create_hil_system(config)`

Create and configure a HIL system.

#### Source Code

```{literalinclude} ../../../src/interfaces/__init__.py
:language: python
:pyobject: create_hil_system
:linenos:
```



### `create_data_serializer(format_type)`

Create a data serializer for the specified format.

#### Source Code

```{literalinclude} ../../../src/interfaces/__init__.py
:language: python
:pyobject: create_data_serializer
:linenos:
```



### `create_health_monitor()`

Create a system health monitor.

#### Source Code

```{literalinclude} ../../../src/interfaces/__init__.py
:language: python
:pyobject: create_health_monitor
:linenos:
```



### `create_hardware_manager()`

Create a hardware device manager.

#### Source Code

```{literalinclude} ../../../src/interfaces/__init__.py
:language: python
:pyobject: create_hardware_manager
:linenos:
```



## Dependencies

This module imports:

- `from .hil import EnhancedHILSystem, HILConfig, HILMode, TestScenario, RealTimeScheduler, TimingConstraints, DeadlineMissHandler, FaultInjector, FaultType, FaultScenario, HILTestFramework, TestSuite, TestCase, HILDataLogger, LoggingConfig, SimulationBridge, ModelInterface, HILControllerClient, PlantServer, run_client`
- `from .data_exchange import SerializationFormat, SerializerInterface, SerializationError, JSONSerializer, MessagePackSerializer, PickleSerializer, BinarySerializer, CompressionSerializer, DataPacket, DataSchema, SchemaValidator, ValidationError, SerializerFactory, StreamingSerializer`
- `from .monitoring import HealthStatus, HealthCheck, ComponentHealth, HealthMonitor, SystemHealthMonitor, MetricType, Metric, MetricsCollector, PerformanceMonitor, SystemMetricsCollector, DiagnosticEngine, DiagnosticResult, AlertManager, Alert, AlertRule, AlertLevel, EmailNotificationHandler, LogNotificationHandler, DashboardServer, MetricSeries, ChartConfig`
- `from .hardware import DeviceDriver, DeviceStatus, BaseDevice, DeviceManager, HardwareInterfaceFactory, SerialDevice, DAQInterface, SensorInterface, ActuatorInterface, AnalogSensor, DigitalSensor`
- `from .network import TCPInterface, UDPInterface, WebSocketInterface, HTTPInterface, NetworkInterfaceFactory, MessageQueueInterface, ZeroMQInterface, RabbitMQInterface, TCPServer, UDPServer, WebSocketServer`
- `from .core import CommunicationProtocol, MessageProtocol, ConnectionProtocol, InterfaceType, Message, ConnectionInfo, InterfaceConfig`
