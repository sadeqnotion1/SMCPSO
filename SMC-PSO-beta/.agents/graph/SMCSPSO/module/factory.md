---
id: "factory"
label: "Factory"
type: "module"
community: "module"
location: "src/controllers/factory.py"
degree: 8
---

# Factory

> [!abstract] Description
> Type-safe controller factory

> [!info] Metadata
> - **Kind/Type**: `module`
> - **Location**: `src/controllers/factory.py` ([open file](file:///E:/Projects/University/SMC-PSO-beta/src/controllers/factory.py))
> - **Degree**: `8`

## Outgoing Connections

- [[smc_classical|SMC Classical]] (relation: `instantiates`)
- [[smc_sta|SMC STA]] (relation: `instantiates`)
- [[smc_adaptive|SMC Adaptive]] (relation: `instantiates`)
- [[smc_hybrid|SMC Hybrid]] (relation: `instantiates`)
- [[pso|PSO]] (relation: `tuned_by`)

## Incoming Connections

- [[cli|CLI]] (relation: `creates`)
- [[web|Web]] (relation: `creates`)
- [[config|Config]] (relation: `configures`)