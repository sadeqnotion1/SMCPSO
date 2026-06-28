---
id: "runner"
label: "Runner"
type: "module"
community: "module"
location: "src/simulation/"
degree: 11
---

# Runner

> [!abstract] Description
> Simulation runner / orchestrator / context

> [!info] Metadata
> - **Kind/Type**: `module`
> - **Location**: `src/simulation/` ([open file](file:///E:/Projects/University/SMC-PSO-beta/src/simulation))
> - **Degree**: `11`

## Outgoing Connections

- [[plant_models|Plant Models]] (relation: `simulates`)
- [[vector_sim|Vector Sim]] (relation: `uses`)
- [[safety_guards|Safety Guards]] (relation: `uses`)
- [[analysis|Analysis]] (relation: `feeds`)
- [[hil|HIL]] (relation: `optional`)
- [[utils|Utils]] (relation: `uses`)

## Incoming Connections

- [[smc_classical|SMC Classical]] (relation: `runs_in`)
- [[smc_sta|SMC STA]] (relation: `runs_in`)
- [[smc_adaptive|SMC Adaptive]] (relation: `runs_in`)
- [[smc_hybrid|SMC Hybrid]] (relation: `runs_in`)
- [[pso|PSO]] (relation: `drives`)