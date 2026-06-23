# simulation.results.__init__

**Source:** `src\simulation\results\__init__.py`

## Module Overview

Result processing and management for simulation framework.

## Complete Source Code

```{literalinclude} ../../../src/simulation/results/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .containers import StandardResultContainer, BatchResultContainer`
- `from .processors import ResultProcessor`
- `from .exporters import CSVExporter, HDF5Exporter`
- `from .validators import ResultValidator`


## Advanced Mathematical Theory

### Result Processing Infrastructure

The results subsystem provides structured data management for simulation output with validation, processing, and export .
#### Result Container Hierarchy

$$
\text{ResultContainer} = \begin{cases}
\text{Standard} & \text{(Single simulation)} \\
\text{Batch} & \text{(Multiple trials)} \\
\text{TimeSeries} & \text{(Temporal data)}
\end{cases}
$$

#### Data Aggregation Theory

**Batch mean aggregation:**
$$
\mu_{\text{batch}} = \frac{1}{N} \sum_{i=1}^N \mu_i
$$

**Variance pooling** (combining variances from multiple trials):
$$
\sigma_{\text{pooled}}^2 = \frac{\sum_{i=1}^N (n_i - 1) \sigma_i^2}{\sum_{i=1}^N (n_i - 1)}
$$

**Standard error of the mean:**
$$
\text{SEM} = \frac{\sigma_{\text{pooled}}}{\sqrt{N}}
$$

#### Result Validation

**Completeness check:**
$$
\text{Complete} = \begin{cases}
\text{True} & \text{if } \forall_{\text{required fields}} : \text{field is present} \\
\text{False} & \text{otherwise}
\end{cases}
$$

**Range validation:**
$$
\text{Valid}(x) = (x_{\min} \leq x \leq x_{\max})
$$

**Consistency check** (time series):
$$
\text{Consistent} = (t_{i+1} - t_i = \Delta t \pm \epsilon) \quad \forall i
$$

## Architecture Diagram

\`\`\`{mermaid}
graph TD
    A[Results Package] --> B[Containers]
    A --> C[Processors]
    A --> D[Validators]
    A --> E[Exporters]

    B --> F[StandardResultContainer]
    B --> G[BatchResultContainer]
    B --> H[TimeSeriesContainer]

    C --> I[Aggregation]
    C --> J[Transformation]
    C --> K[Statistical Analysis]

    D --> L[Completeness Check]
    D --> M[Range Validation]
    D --> N[Consistency Check]

    E --> O[CSV Exporter]
    E --> P[HDF5 Exporter]
    E --> Q[JSON Exporter]

    R[Simulation Results] --> B
    B --> C
    C --> D
    D --> E
    E --> S[Export Files]

    style A fill:#e1f5ff
    style D fill:#fff4e1
    style S fill:#e8f5e9
\`\`\`

## Usage Examples

### Example 1: Basic Result Container

\`\`\`python
from src.simulation.results import StandardResultContainer

# Create result container

result = StandardResultContainer()

# Store simulation data

result.set_time_series('state', t, x)
result.set_time_series('control', t, u)
result.set_metadata('controller_type', 'classical_smc')
result.set_metadata('gains', [10, 8, 15, 12, 50, 5])

# Access data

state_data = result.get_time_series('state')
metadata = result.get_metadata()

print(f"Simulation duration: {result.duration}s")
print(f"Number of steps: {result.num_steps}")
\`\`\`

## Example 2: Batch Result Aggregation

\`\`\`python
from src.simulation.results import BatchResultContainer
from src.simulation.results import ResultProcessor

# Create batch container

batch = BatchResultContainer()

# Add multiple trial results

for i in range(100):
    trial_result = run_single_simulation(seed=i)
    batch.add_result(trial_result)

# Aggregate results

processor = ResultProcessor()
aggregated = processor.aggregate_batch(batch)

print(f"Mean ISE: {aggregated['ise']['mean']:.4f} ± {aggregated['ise']['sem']:.4f}")
print(f"95% CI: [{aggregated['ise']['ci_lower']:.4f}, {aggregated['ise']['ci_upper']:.4f}]")
print(f"Min/Max: [{aggregated['ise']['min']:.4f}, {aggregated['ise']['max']:.4f}]")
\`\`\`

## Example 3: Result Validation

\`\`\`python
from src.simulation.results import ResultValidator

# Create validator

validator = ResultValidator(
    required_fields=['time', 'state', 'control'],
    state_bounds=(-10.0, 10.0),
    control_bounds=(-100.0, 100.0)
)

# Validate result

is_valid, errors = validator.validate(result)

if not is_valid:
    print("Validation failed:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✓ Result is valid")
\`\`\`

## Example 4: Export to Multiple Formats

\`\`\`python
from src.simulation.results import CSVExporter, HDF5Exporter, JSONExporter

# Export to CSV

csv_exporter = CSVExporter()
csv_exporter.export(result, 'simulation_result.csv')

# Export to HDF5 (with compression)

hdf5_exporter = HDF5Exporter(compression='gzip', compression_opts=9)
hdf5_exporter.export(result, 'simulation_result.h5')

# Export to JSON

json_exporter = JSONExporter(indent=2)
json_exporter.export(result, 'simulation_result.json')

print("Results exported to 3 formats")
\`\`\`

## Example 5: Result Processing Pipeline

\`\`\`python
from src.simulation.results import (
    ResultValidator,
    ResultProcessor,
    CSVExporter
)

# Define processing pipeline

def process_results_pipeline(raw_results, output_path):
    # 1. Validate
    validator = ResultValidator()
    valid_results = []

    for result in raw_results:
        is_valid, errors = validator.validate(result)
        if is_valid:
            valid_results.append(result)
        else:
            print(f"Skipping invalid result: {errors[0]}")

    # 2. Process
    processor = ResultProcessor()
    processed = processor.batch_process(valid_results)

    # 3. Export
    exporter = CSVExporter()
    exporter.export(processed, output_path)

    print(f"Processed {len(valid_results)}/{len(raw_results)} results")
    return processed

# Run pipeline

results_batch = [run_simulation(i) for i in range(100)]
processed = process_results_pipeline(results_batch, 'output/batch_results.csv')
\`\`\`


## Architecture Diagram

\`\`\`{mermaid}
graph TD
    A[Component] --> B[Subcomponent 1]
    A --> C[Subcomponent 2]
    B --> D[Output]
    C --> D

    style A fill:#e1f5ff
    style D fill:#e8f5e9
\`\`\`


## Usage Examples

### Example 1: Basic Usage

\`\`\`python
# Basic usage example

from src.simulation.results import Component

component = Component()
result = component.process(data)
\`\`\`

## Example 2: Advanced Configuration

\`\`\`python
# Advanced configuration

component = Component(
    option1=value1,
    option2=value2
)
\`\`\`

## Example 3: Integration with Framework

\`\`\`python
# Integration example

from src.simulation import SimulationRunner

runner = SimulationRunner()
runner.use_component(component)
\`\`\`

## Example 4: Performance Optimization

\`\`\`python
# Performance-optimized usage

component = Component(enable_caching=True)
\`\`\`

## Example 5: Error Handling

\`\`\`python
# Error handling

try:
    result = component.process(data)
except ComponentError as e:
    print(f"Error: {e}")
\`\`\`
