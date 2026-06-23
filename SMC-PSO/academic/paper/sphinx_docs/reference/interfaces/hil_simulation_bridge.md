# interfaces.hil.simulation_bridge

**Source:** `src\interfaces\hil\simulation_bridge.py`

## Module Overview

Simulation bridge for HIL systems.
This module provides integration between hardware components and
simulation models, enabling hybrid testing where some components are real
hardware and others are simulated models.


## Mathematical Foundation

### Bridge Architecture Pattern

The simulation bridge decouples plant and controller execution:

```{math}
\text{Plant} \xleftrightarrow{\text{Bridge}} \text{Controller}
```

**Key Properties:**
1. **Asynchrony**: Plant and controller run at different rates
2. **Location transparency**: Local or remote execution
3. **Protocol abstraction**: TCP, UDP, shared memory, etc.

### Data Exchange Protocol

Bi-directional message passing:

```{math}
\begin{align}
M_{\text{state}} &: \text{Plant} \rightarrow \text{Controller} : (\vec{x}, t, \text{metadata}) \\
M_{\text{control}} &: \text{Controller} \rightarrow \text{Plant} : (u, t, \text{flags})
\end{align}
```

**Message Synchronization:**
```{math}
|t_{\text{state}} - t_{\text{control}}| < \epsilon
```

Ensures temporal consistency between state and control.

### Communication Middleware

**Transport Layer Options:**
1. **TCP**: Reliable, ordered delivery (default)
2. **UDP**: Low-latency, unreliable
3. **Shared Memory**: Zero-copy for co-located processes

**Protocol Selection Criteria:**
```{math}
\text{Protocol} = \begin{cases}
\text{TCP} & \text{if reliability required} \\
\text{UDP} & \text{if latency critical} \\
\text{Shared Mem} & \text{if same machine}
\end{cases}
```

### State Interpolation

For asynchronous execution, interpolate state:

```{math}
\vec{x}(t_{\text{req}}) \approx \vec{x}(t_k) + \frac{t_{\text{req}} - t_k}{t_{k+1} - t_k} (\vec{x}(t_{k+1}) - \vec{x}(t_k))
```

**Linear Interpolation Accuracy:**
```{math}
\|\vec{x}_{\text{true}} - \vec{x}_{\text{interp}}\| \leq C \|\Delta t\|^2
```

### Fault Tolerance

**Heartbeat Mechanism:**
```{math}
\text{Health}(t) = \begin{cases}
\text{OK} & \text{if } t - t_{\text{last\_msg}} < T_{\text{heartbeat}} \\
\text{TIMEOUT} & \text{otherwise}
\end{cases}
```

**Automatic Reconnection:**
- Exponential backoff: $T_{\text{retry}} = T_0 \cdot 2^n$
- Maximum retries: 5 attempts
- Circuit breaker: Disable after persistent failures

### Performance Metrics

**Throughput:**
```{math}
\text{Throughput} = \frac{\text{Messages}}{\text{Time}} \quad [\text{msg/s}]
```

**Latency Percentiles:**
- P50: Median latency (typical)
- P95: 95th percentile (good)
- P99: 99th percentile (worst-case)

### Bridge Implementation

**Thread Model:**
- **Receiver thread**: Listens for incoming messages
- **Sender thread**: Sends outgoing messages
- **Main thread**: Orchestrates simulation logic

**Thread Safety:**
- Lock-free queues for message passing
- Atomic operations for shared state
- No blocking operations in critical path

## Architecture Diagram

```{mermaid}
graph LR
    A[Plant Server] <-->|State| B[Bridge]
    B <-->|Control| A
    B <-->|State| C[Controller Client]
    C <-->|Control| B

    B --> D[Protocol Handler]
    D --> E[TCP Handler]
    D --> F[UDP Handler]
    D --> G[Shared Mem Handler]

    B --> H[State Buffer]
    B --> I[Control Buffer]

    H --> J[Interpolator]
    I --> K[Extrapolator]

    style B fill:#9cf
    style D fill:#ff9
    style J fill:#f9f
```

**Bridge Responsibilities:**
1. **Protocol Translation**: Convert between different transport protocols
2. **State Management**: Buffer and interpolate state data
3. **Timing Coordination**: Synchronize plant and controller clocks
4. **Fault Handling**: Detect timeouts and connection failures
5. **Logging**: Record all messages for debugging

## Usage Examples

### Example 1: Basic Bridge Setup

```python
from src.interfaces.hil.simulation_bridge import SimulationBridge

# Initialize bridge
bridge = SimulationBridge(
    server_addr=("127.0.0.1", 5555),
    client_addr=("127.0.0.1", 6666),
    protocol="tcp"
)

# Start bridge
bridge.start()

# Bridge runs until shutdown
bridge.stop()
```

## Example 2: Protocol Translation

```python
from src.interfaces.hil.simulation_bridge import SimulationBridge

# TCP server, UDP client
bridge = SimulationBridge(
    server_addr=("127.0.0.1", 5555),
    client_addr=("127.0.0.1", 6666),
    server_protocol="tcp",
    client_protocol="udp"
)

bridge.start()
```

## Example 3: State Interpolation

```python
from src.interfaces.hil.simulation_bridge import SimulationBridge
import numpy as np

# Bridge with interpolation
bridge = SimulationBridge(
    server_addr=("127.0.0.1", 5555),
    client_addr=("127.0.0.1", 6666)
)

# Enable state interpolation
bridge.enable_interpolation(method="linear")

# Custom interpolation
def custom_interpolator(state_buffer, t_req):
    # Find surrounding states
    t_prev, x_prev = state_buffer.get_before(t_req)
    t_next, x_next = state_buffer.get_after(t_req)

    # Linear interpolation
    alpha = (t_req - t_prev) / (t_next - t_prev)
    x_interp = x_prev + alpha * (x_next - x_prev)

    return x_interp

bridge.set_interpolator(custom_interpolator)
bridge.start()
```

### Example 4: Fault-Tolerant Bridge

```python
# example-metadata:
# runnable: false

from src.interfaces.hil.simulation_bridge import SimulationBridge
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SimulationBridge')

# Bridge with fault tolerance
bridge = SimulationBridge(
    server_addr=("127.0.0.1", 5555),
    client_addr=("127.0.0.1", 6666),
    heartbeat_interval=1.0,  # 1 second heartbeat
    reconnect_attempts=5
)

# Monitor health
def health_callback(status):
    if status == "TIMEOUT":
        logger.warning("Connection timeout detected")
    elif status == "RECONNECTING":
        logger.info("Attempting reconnection...")
    elif status == "OK":
        logger.info("Connection healthy")

bridge.set_health_callback(health_callback)
bridge.start()
```

## Example 5: Performance Monitoring

```python
from src.interfaces.hil.simulation_bridge import SimulationBridge
import time

# Bridge with metrics
bridge = SimulationBridge(
    server_addr=("127.0.0.1", 5555),
    client_addr=("127.0.0.1", 6666)
)

# Metrics collection
metrics = {
    'throughput': [],
    'latency': [],
    'packet_loss': 0
}

# Override message handler for monitoring
original_forward = bridge._forward_message

def monitored_forward(msg, direction):
    start = time.time()
    try:
        result = original_forward(msg, direction)
        latency = (time.time() - start) * 1000
        metrics['latency'].append(latency)
        return result
    except Exception as e:
        metrics['packet_loss'] += 1
        raise

bridge._forward_message = monitored_forward
bridge.start()

# Report metrics
print(f"Mean latency: {np.mean(metrics['latency']):.2f} ms")
print(f"Packet loss: {metrics['packet_loss']} packets")
```

## Complete Source Code

```{literalinclude} ../../../src/interfaces/hil/simulation_bridge.py
:language: python
:linenos:
```



## Classes

### `BridgeMode`

**Inherits from:** `Enum`

Bridge operation mode.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/simulation_bridge.py
:language: python
:pyobject: BridgeMode
:linenos:
```



### `ModelType`

**Inherits from:** `Enum`

Simulation model type.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/simulation_bridge.py
:language: python
:pyobject: ModelType
:linenos:
```



### `BridgeConfig`

Configuration for simulation bridge.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/simulation_bridge.py
:language: python
:pyobject: BridgeConfig
:linenos:
```



### `ModelState`

State information for a simulation model.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/simulation_bridge.py
:language: python
:pyobject: ModelState
:linenos:
```



### `ModelInterface`

**Inherits from:** `ABC`

Abstract interface for simulation models.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/simulation_bridge.py
:language: python
:pyobject: ModelInterface
:linenos:
```

#### Methods (9)

##### `initialize(self, parameters)`

Initialize the model with given parameters.

[View full source →](#method-modelinterface-initialize)

##### `step(self, inputs, dt)`

Execute one simulation step.

[View full source →](#method-modelinterface-step)

##### `get_state(self)`

Get current model state.

[View full source →](#method-modelinterface-get_state)

##### `set_state(self, state)`

Set model state.

[View full source →](#method-modelinterface-set_state)

##### `reset(self)`

Reset model to initial state.

[View full source →](#method-modelinterface-reset)

##### `cleanup(self)`

Clean up model resources.

[View full source →](#method-modelinterface-cleanup)

##### `model_type(self)`

Get model type.

[View full source →](#method-modelinterface-model_type)

##### `input_names(self)`

Get list of input signal names.

[View full source →](#method-modelinterface-input_names)

##### `output_names(self)`

Get list of output signal names.

[View full source →](#method-modelinterface-output_names)



### `PlantModel`

**Inherits from:** `ModelInterface`

Base class for plant simulation models.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/simulation_bridge.py
:language: python
:pyobject: PlantModel
:linenos:
```

#### Methods (7)

##### `__init__(self, model_id)`

[View full source →](#method-plantmodel-__init__)

##### `model_type(self)`

[View full source →](#method-plantmodel-model_type)

##### `initialize(self, parameters)`

Initialize plant model.

[View full source →](#method-plantmodel-initialize)

##### `get_state(self)`

Get current plant state.

[View full source →](#method-plantmodel-get_state)

##### `set_state(self, state)`

Set plant state.

[View full source →](#method-plantmodel-set_state)

##### `reset(self)`

Reset plant to initial state.

[View full source →](#method-plantmodel-reset)

##### `cleanup(self)`

Clean up plant model.

[View full source →](#method-plantmodel-cleanup)



### `LinearPlantModel`

**Inherits from:** `PlantModel`

Linear plant model implementation.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/simulation_bridge.py
:language: python
:pyobject: LinearPlantModel
:linenos:
```

#### Methods (5)

##### `__init__(self, model_id)`

[View full source →](#method-linearplantmodel-__init__)

##### `input_names(self)`

[View full source →](#method-linearplantmodel-input_names)

##### `output_names(self)`

[View full source →](#method-linearplantmodel-output_names)

##### `initialize(self, parameters)`

Initialize linear plant model.

[View full source →](#method-linearplantmodel-initialize)

##### `step(self, inputs, dt)`

Execute linear plant simulation step.

[View full source →](#method-linearplantmodel-step)



### `SignalMapper`

Maps signals between hardware and simulation components.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/simulation_bridge.py
:language: python
:pyobject: SignalMapper
:linenos:
```

#### Methods (4)

##### `__init__(self)`

[View full source →](#method-signalmapper-__init__)

##### `add_mapping(self, source, destination, transformation, scaling, offset)`

Add signal mapping.

[View full source →](#method-signalmapper-add_mapping)

##### `map_signal(self, source, value)`

Map signal from source to destination.

[View full source →](#method-signalmapper-map_signal)

##### `get_mappings(self)`

Get all signal mappings.

[View full source →](#method-signalmapper-get_mappings)



### `SimulationBridge`

Main simulation bridge for HIL systems.

Coordinates execution between hardware components and simulation models,
ensuring proper timing, data flow, and synchronization.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/simulation_bridge.py
:language: python
:pyobject: SimulationBridge
:linenos:
```

#### Methods (17)

##### `__init__(self, config)`

Initialize simulation bridge.

[View full source →](#method-simulationbridge-__init__)

##### `initialize(self)`

Initialize simulation bridge.

[View full source →](#method-simulationbridge-initialize)

##### `start(self)`

Start simulation bridge execution.

[View full source →](#method-simulationbridge-start)

##### `stop(self)`

Stop simulation bridge execution.

[View full source →](#method-simulationbridge-stop)

##### `add_model(self, model_id, model)`

Add simulation model to bridge.

[View full source →](#method-simulationbridge-add_model)

##### `remove_model(self, model_id)`

Remove simulation model from bridge.

[View full source →](#method-simulationbridge-remove_model)

##### `add_signal_mapping(self, source, destination, transformation)`

Add signal mapping between components.

[View full source →](#method-simulationbridge-add_signal_mapping)

##### `set_hardware_interface(self, read_callback, write_callback)`

Set hardware interface callbacks.

[View full source →](#method-simulationbridge-set_hardware_interface)

##### `execute_step(self)`

Execute one simulation/HIL step.

[View full source →](#method-simulationbridge-execute_step)

##### `run_continuous(self, duration)`

Run simulation bridge continuously.

[View full source →](#method-simulationbridge-run_continuous)

##### `pause(self)`

Pause simulation bridge execution.

[View full source →](#method-simulationbridge-pause)

##### `resume(self)`

Resume simulation bridge execution.

[View full source →](#method-simulationbridge-resume)

##### `get_performance_statistics(self)`

Get performance statistics.

[View full source →](#method-simulationbridge-get_performance_statistics)

##### `_map_inputs_for_model(self, model, hardware_inputs, model_outputs)`

Map inputs for a specific model.

[View full source →](#method-simulationbridge-_map_inputs_for_model)

##### `_map_outputs_to_hardware(self, model_outputs)`

Map model outputs to hardware signals.

[View full source →](#method-simulationbridge-_map_outputs_to_hardware)

##### `_update_buffers(self, inputs, outputs)`

Update data buffers.

[View full source →](#method-simulationbridge-_update_buffers)

##### `_synchronize_real_time(self)`

Synchronize with real-time execution.

[View full source →](#method-simulationbridge-_synchronize_real_time)



## Functions

### `create_linear_plant_model(model_id, A, B, C, D)`

Create linear plant model with state-space matrices.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/simulation_bridge.py
:language: python
:pyobject: create_linear_plant_model
:linenos:
```



### `create_simulation_bridge(sample_time, real_time_factor)`

Create simulation bridge with default configuration.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/simulation_bridge.py
:language: python
:pyobject: create_simulation_bridge
:linenos:
```



## Dependencies

This module imports:

- `import asyncio`
- `import time`
- `import numpy as np`
- `from abc import ABC, abstractmethod`
- `from dataclasses import dataclass, field`
- `from typing import Dict, Any, Optional, List, Callable, Union`
- `from enum import Enum`
- `import logging`
