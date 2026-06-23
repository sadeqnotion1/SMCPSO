# Phase 3: Visual Diagrams

This page contains visual diagrams to help understand Phase 3 concepts.

## 1. Simulation Workflow

Data flow from configuration to simulation results.

```{mermaid}
flowchart LR
    A[config.yaml] --> B[Load Parameters]
    B --> C[Create Controller]
    B --> D[Create Plant Model]

    C --> E[Run Simulation]
    D --> E

    E --> F[State Data]
    F --> G[Generate Plots]
    F --> H[Calculate Metrics]

    G --> I[Visual Results]
    H --> J[Performance Report]

    style A fill:#4ECDC4,stroke:#333,stroke-width:2px,color:#fff
    style E fill:#F59E0B,stroke:#333,stroke-width:2px,color:#fff
    style I fill:#10B981,stroke:#333,stroke-width:2px,color:#fff
    style J fill:#10B981,stroke:#333,stroke-width:2px,color:#fff
```

**Alt text**: Simulation workflow showing data flow from config.yaml through controller and plant creation, simulation execution, to plots and performance metrics.

---

## 2. Result Interpretation Guide

Reading and understanding simulation outputs.

```{mermaid}
graph TD
    A[Simulation Results] --> B[State Plots]
    A --> C[Control Plot]
    A --> D[Metrics]

    B --> B1[Cart Position]
    B --> B2[Pendulum Angles]
    B --> B3[Velocities]

    C --> C1[Force Over Time]

    D --> D1[Settling Time]
    D --> D2[Overshoot]
    D --> D3[Control Effort]
    D --> D4[Chattering Index]

    B1 -->|Should| E[Return to Zero]
    B2 -->|Should| F[Converge to Zero]
    B3 -->|Should| G[Decay to Zero]

    style A fill:#4ECDC4,stroke:#333,stroke-width:2px,color:#fff
    style E fill:#10B981,stroke:#333,stroke-width:1px
    style F fill:#10B981,stroke:#333,stroke-width:1px
    style G fill:#10B981,stroke:#333,stroke-width:1px
```

**Alt text**: Result interpretation guide showing the three main result categories (state plots, control plot, metrics) and what to expect from each.

---

## 3. Tuning Decision Tree

Guide for selecting and tuning controller parameters.

```{mermaid}
flowchart TD
    A[Need to Tune?] --> B{What's Wrong?}

    B -->|Too Slow| C[Increase Gains]
    B -->|Too Chattery| D[Decrease Gains]
    B -->|Unstable| E[Check Config]
    B -->|Good| F[Done]

    C --> G{Better?}
    D --> G
    E --> H[Fix Parameters]

    H --> I[Run Again]
    G -->|Yes| J[Save Gains]
    G -->|No| K[Try PSO]

    K --> L[Automatic Tuning]
    L --> J

    style A fill:#4ECDC4,stroke:#333,stroke-width:2px,color:#fff
    style F fill:#10B981,stroke:#333,stroke-width:2px,color:#fff
    style J fill:#10B981,stroke:#333,stroke-width:2px,color:#fff
```

**Alt text**: Decision tree for tuning controllers: identifying problems (slow, chattery, unstable), applying fixes (adjust gains), and using PSO for automatic tuning.

---

## 4. Analysis Workflow

Post-simulation analysis steps.

```{mermaid}
flowchart TD
    A[Simulation Complete] --> B[Check Metrics]
    B --> C{Good Performance?}

    C -->|Yes| D[Save Results]
    C -->|No| E[Analyze Plots]

    E --> F{Issue Type?}
    F -->|Settling Slow| G[Increase Gains]
    F -->|Overshoot High| H[Tune Gains]
    F -->|Chattering High| I[Adjust Boundary Layer]

    G --> J[Run Again]
    H --> J
    I --> J

    J --> B
    D --> K[Compare Controllers]
    K --> L[Document Findings]

    style A fill:#4ECDC4,stroke:#333,stroke-width:2px,color:#fff
    style D fill:#10B981,stroke:#333,stroke-width:2px,color:#fff
    style L fill:#10B981,stroke:#333,stroke-width:2px,color:#fff
```

**Alt text**: Analysis workflow showing the iterative process of checking metrics, analyzing plots, identifying issues, tuning parameters, and documenting results.

---

## Progress Tracker

<div class="phase-progress">
  <div class="progress-fill" style="--progress-percent: 0%;"></div>
</div>

**Phase 3 Completion**: Update this as you complete sub-phases:
- [ ] 3.1 First Simulation (8 hours)
- [ ] 3.2 Understanding Results (6 hours)
- [ ] 3.3 Comparing Controllers (5 hours)
- [ ] 3.4 Modifying Configuration (4 hours)
- [ ] 3.5 Troubleshooting (2 hours)

---

[<-- Back to Phase 3](phase-3-hands-on.md)
