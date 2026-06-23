# interfaces.hil.__init__

**Source:** `src\interfaces\hil\__init__.py`

## Module Overview Enhanced

Hardware-in-the-Loop (HIL) system for control engineering

.


This module provides advanced HIL features including real-time simulation,
hardware integration, fault injection, and testing frameworks
for control system validation and verification. ## Mathematical Foundation ### HIL Package Architecture The HIL package provides hardware-in-the-loop testing: ```{math}
\text{HIL System} = (\text{Server}, \text{Client}, \text{Bridge}, \text{Sync}, \text{Logging})
``` ### System Integration **Component Interaction:**
```{math}

\begin{align}
\text{Server} &\xrightarrow{\vec{x}(t)} \text{Bridge} \xrightarrow{\vec{x}(t)} \text{Client} \\
\text{Client} &\xrightarrow{u(t)} \text{Bridge} \xrightarrow{u(t)} \text{Server}
\end{align}
``` ### End-to-End Latency **Total System Latency:**
```{math}

T_{\text{e2e}} = T_{\text{server}} + T_{\text{bridge}} + T_{\text{network}} + T_{\text{client}}
``` **Latency Budget:**
- Server: 1 ms (dynamics computation)
- Bridge: 0.5 ms (serialization/routing)
- Network: 5 ms (configurable)
- Client: 2 ms (control computation)
- **Total**: ~8.5 ms per cycle ### Quality of Service **Reliability Metrics:**
1. **Availability**: $A = \frac{T_{\text{uptime}}}{T_{\text{total}}}$
2. **Packet Loss Rate**: $P_{\text{loss}} = \frac{N_{\text{lost}}}{N_{\text{sent}}}$
3. **Mean Time Between Failures**: MTBF **Performance Metrics:**
1. **Throughput**: Messages/second
2. **Latency**: Round-trip time
3. **Jitter**: Variance in latency ### Configuration Management **System Configuration:**
```{math}

\mathcal{C}_{\text{system}} = \{C_{\text{server}}, C_{\text{client}}, C_{\text{bridge}}, C_{\text{sync}}\}
``` **Validation:**
```{math}

\text{Valid}(\mathcal{C}) \Leftrightarrow \bigwedge_{i} \text{Constraint}_i(\mathcal{C})
``` ### Usage Patterns **1. Local HIL Testing:**
- Same machine
- Shared memory or localhost TCP
- Minimal latency **2. Distributed HIL Testing:**
- Different machines
- Network TCP
- Realistic latency **3. Hybrid Testing:**
- Some components local, others remote
- Mixed latency profiles ## Architecture Diagram ```{mermaid}
graph TB subgraph HIL System A[Plant Server] <--> B[Simulation Bridge] B <--> C[Controller Client] D[Real-Time Sync] --> A D --> C E[Fault Injection] --> A E --> C F[Data Logging] --> A F --> C G[Test Automation] --> A G --> C H[Enhanced HIL] --> A H --> C end I[Configuration Manager] --> A I --> B I --> C I --> D I --> E I --> F I --> G I --> H J[Results Storage] <-- F J <-- G style A fill:#9cf style C fill:#9cf style B fill:#ff9 style I fill:#f9f
``` **System Components:**

- **Core**: Server, Client, Bridge
- **Timing**: Real-Time Sync
- **Testing**: Fault Injection, Test Automation
- **Logging**: Data Logging
- **Advanced**: Enhanced HIL features
- **Management**: Configuration Manager ## Usage Examples ### Example 1: Complete HIL Setup ```python
from src.interfaces import hil # Complete HIL system setup
config = hil.load_config("config.yaml") # Start plant server
server = hil.PlantServer( cfg=config, bind_addr=("127.0.0.1", 5555), dt=0.01
) # Start controller client
client = hil.HILControllerClient( cfg=config, plant_addr=("127.0.0.1", 5555), bind_addr=("127.0.0.1", 0), dt=0.01, steps=5000
) # Run HIL simulation
server.start() # Blocks until client connects
``` ### Example 2: Distributed HIL Testing ```python
from src.interfaces import hil
from threading import Thread # Server on one thread
def run_server(): server = hil.PlantServer( cfg=config, bind_addr=("0.0.0.0", 5555), dt=0.01 ) server.start() # Client on another thread
def run_client(): time.sleep(1.0) # Wait for server to start client = hil.HILControllerClient( cfg=config, plant_addr=("127.0.0.1", 5555), bind_addr=("127.0.0.1", 0), dt=0.01, steps=5000 ) client.run() # Run distributed
t1 = Thread(target=run_server)
t2 = Thread(target=run_client)
t1.start()
t2.start()
t1.join()
t2.join()
``` ### Example 3: HIL with Fault Injection ```python

from src.interfaces import hil # Setup with fault injection
server = hil.PlantServer(cfg=config, bind_addr=("127.0.0.1", 5555), dt=0.01) # Add fault injector
injector = hil.FaultInjector()
injector.add_fault( fault_type=hil.FaultType.SENSOR_BIAS, target="theta1", bias=0.1, start_time=5.0
) # Attach to server
server.set_fault_injector(injector) server.start()
``` ### Example 4: HIL with Data Logging ```python
from src.interfaces import hil # Setup with logging
server = hil.PlantServer(cfg=config, bind_addr=("127.0.0.1", 5555), dt=0.01)
client = hil.HILControllerClient( cfg=config, plant_addr=("127.0.0.1", 5555), bind_addr=("127.0.0.1", 0), dt=0.01, steps=5000
) # Add logger
logger = hil.DataLogger("hil_results.h5", format="hdf5") # Attach to client
client.set_logger(logger) # Run with logging
server.start()
``` ### Example 5: Automated HIL Test Suite ```python

from src.interfaces import hil # Create test suite
suite = hil.TestSuite(name="Controller_Validation") # Add test cases
suite.add_test( name="stability", initial_state=[0.0, 0.1, -0.05, 0.0, 0.0, 0.0], pass_criteria={"settling_time": 3.0}
) suite.add_test( name="robustness", initial_state=[0.0, 0.2, -0.1, 0.0, 0.0, 0.0], disturbance={"type": "step", "magnitude": 10.0}, pass_criteria={"recovery_time": 2.0}
) # Run all tests
results = suite.run_all() # Generate report
suite.save_report("test_report.json")
print(f"Tests passed: {results.pass_count}/{results.total_count}")
``` ## Complete Source Code ```{literalinclude} ../../../src/interfaces/hil/__init__.py
:language: python
:linenos:
```

---

## Dependencies This module imports: - `from .enhanced_hil import EnhancedHILSystem, HILConfig, HILMode, TestScenario`

- `from .real_time_sync import RealTimeScheduler, TimingConstraints, DeadlineMissHandler`
- `from .fault_injection import FaultInjector, FaultType, FaultScenario`
- `from .test_automation import HILTestFramework, TestSuite, TestCase`
- `from .data_logging import HILDataLogger, LoggingConfig`
- `from .simulation_bridge import SimulationBridge, ModelInterface`
- `from .controller_client import HILControllerClient, run_client`
- `from .plant_server import PlantServer`
