# utils.monitoring.stability

**Source:** `src\utils\monitoring\stability.py`

## Module Overview Lyapunov

Decrease Ratio (LDR) and stability monitoring for control systems

. Implements the stability monitoring solution from Issue #1 resolution plan,


including LDR monitoring, saturation tracking, and dynamics conditioning. ## Complete Source Code ```{literalinclude} ../../../src/utils/monitoring/stability.py
:language: python
:linenos:
```

---

## Classes

### `LyapunovDecreaseMonitor`

Monitor Lyapunov Decrease Ratio for stability assessment. Implements LDR monitoring as specified in Issue #1 resolution:
- Alert when LDR < 95% over 200-500ms rolling window (post-transient)
- Track sigma*sigma_dot for sliding surface analysis #### Source Code ```{literalinclude} ../../../src/utils/monitoring/stability.py
:language: python
:pyobject: LyapunovDecreaseMonitor
:linenos:
``` #### Methods (4) ##### `__init__(self, window_size_ms, dt, ldr_threshold, transient_time)` Initialize LDR monitor. [View full source →](#method-lyapunovdecreasemonitor-__init__) ##### `update(self, sigma)` Update monitor with new sliding surface values. [View full source →](#method-lyapunovdecreasemonitor-update) ##### `_compute_ldr(self)` Compute Lyapunov Decrease Ratio over the rolling window. [View full source →](#method-lyapunovdecreasemonitor-_compute_ldr) ##### `reset(self)` Reset all monitoring state. [View full source →](#method-lyapunovdecreasemonitor-reset)

---

## `SaturationMonitor`

Monitor actuator saturation duty and rate-limit violations. Implements saturation monitoring as specified in Issue #1 resolution:

- Alert when duty > 20-30% or rate hits > 1% beyond transient #### Source Code ```{literalinclude} ../../../src/utils/monitoring/stability.py
:language: python
:pyobject: SaturationMonitor
:linenos:
``` #### Methods (3) ##### `__init__(self, max_force, dt, duty_threshold, rate_hit_threshold, transient_time, window_size_ms)` Initialize saturation monitor. [View full source →](#method-saturationmonitor-__init__) ##### `update(self, force)` Update monitor with new control force. [View full source →](#method-saturationmonitor-update) ##### `reset(self)` Reset monitoring state. [View full source →](#method-saturationmonitor-reset)

---

### `DynamicsConditioningMonitor`

Monitor dynamics matrix conditioning and inversion health. Implements conditioning monitoring as specified in Issue #1 resolution:
- Alert on sustained κ(M(q)) above threshold or spike in fallback inversions #### Source Code ```{literalinclude} ../../../src/utils/monitoring/stability.py
:language: python
:pyobject: DynamicsConditioningMonitor
:linenos:
``` #### Methods (3) ##### `__init__(self, condition_threshold, spike_threshold, fallback_threshold, window_size_ms, dt)` Initialize conditioning monitor. [View full source →](#method-dynamicsconditioningmonitor-__init__) ##### `update(self, mass_matrix, used_fallback)` Update monitor with dynamics matrix info. [View full source →](#method-dynamicsconditioningmonitor-update) ##### `reset(self)` Reset monitoring state. [View full source →](#method-dynamicsconditioningmonitor-reset)

### `StabilityMonitoringSystem`

Integrated stability monitoring system for Issue #1 resolution. Combines LDR, saturation, and conditioning monitors for stability assessment as specified in the resolution plan.

#### Source Code ```

{literalinclude} ../../../src/utils/monitoring/stability.py

:language: python
:pyobject: StabilityMonitoringSystem
:linenos:
``` #### Methods (5) ##### `__init__(self, config)` Initialize integrated monitoring system. [View full source →](#method-stabilitymonitoringsystem-__init__) ##### `update(self, sigma, control_force, mass_matrix, used_fallback)` Update all monitors with current simulation data. [View full source →](#method-stabilitymonitoringsystem-update) ##### `get_stability_report(self)` Generate stability report. [View full source →](#method-stabilitymonitoringsystem-get_stability_report) ##### `start_new_episode(self)` Start monitoring a new episode. [View full source →](#method-stabilitymonitoringsystem-start_new_episode) ##### `reset(self)` Reset entire monitoring system. [View full source →](#method-stabilitymonitoringsystem-reset)

---

## Dependencies This module imports: - `from __future__ import annotations`
- `import time`
- `from typing import List, Tuple, Dict, Any, Optional`
- `import numpy as np`
- `from collections import deque` ## Advanced Mathematical Theory ### Monitoring Utilities Theory (Detailed mathematical theory for monitoring utilities to be added...) **Key concepts:**
- Mathematical foundations
- Algorithmic principles
- Performance characteristics
- Integration patterns ## Architecture Diagram \`\`\`{mermaid}
graph TD A[Component] --> B[Subcomponent 1] A --> C[Subcomponent 2] B --> D[Output] C --> D style A fill:#e1f5ff style D fill:#e8f5e9
\`\`\` ## Usage Examples ### Example 1: Basic Usage \`\`\`python
from src.utils.monitoring_stability import Component component = Component()
result = component.process(data)
\`\`\` ### Example 2: Advanced Configuration \`\`\`python
component = Component( option1=value1, option2=value2
)
\`\`\` ### Example 3: Integration with Simulation \`\`\`python
# Integration example
for k in range(num_steps): result = component.process(x) x = update(x, result)
\`\`\` ### Example 4: Performance Optimization \`\`\`python
component = Component(enable_caching=True)
\`\`\` ### Example 5: Error Handling \`\`\`python
try: result = component.process(data)
except ComponentError as e: print(f"Error: {e}")
\`\`\` 
