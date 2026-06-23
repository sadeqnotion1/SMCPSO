# Visual Documentation Map

Interactive visual navigation for the DIP_SMC_PSO documentation.

**[CORE]** [Master Navigation Hub](NAVIGATION.md) - Complete documentation mapping across all 985 files and 11 navigation systems.

## Documentation Structure Mindmap

```{mermaid}
mindmap
  root((DIP SMC PSO<br/>Documentation))
    [CORE] Navigation Hub
      NAVIGATION.md
      Master Hub
      985 Files
      11 Systems
    Getting Started
      Installation Guide
      Quick Start Tutorial
      First Simulation
      Dashboard Guide
    User Guides
      Running Simulations
      PSO Optimization
      Testing Workflows
      Configuration
    API Reference
      Controllers
        Classical SMC
        Super-Twisting
        Adaptive SMC
        Hybrid SMC
      Optimization
        PSO Tuner
        Convergence
        Bounds Validation
      Simulation
        Engine
        Orchestrator
        Safety Monitors
      Plant Dynamics
        Full Model
        Simplified
        Configurations
    Theory & Math
      SMC Theory
      PSO Algorithm
      Lyapunov Stability
      Pendulum Dynamics
    Testing & Validation
      Test Standards
      Benchmarks
      Coverage Analysis
      Quality Gates
    Deployment
      Docker Setup
      Production Guide
      Streamlit Deploy
      Cloud Platforms
    Project Docs
      Changelog
      Contributing
      Dependencies
      Citations
```

## Architecture Overview Flowchart

```{mermaid}
flowchart TB
    Start([User Starts Here]) --> Navigation[NAVIGATION.md<br/>Master Hub]
    Navigation --> Choice{What do you need?}

    Choice -->|Learn Basics| GettingStarted[Getting Started Guide]
    Choice -->|Run Simulations| Simulations[User Guides]
    Choice -->|API Reference| API[API Documentation]
    Choice -->|Deploy| Deploy[Deployment Guides]

    GettingStarted --> Install[Installation]
    GettingStarted --> FirstSim[First Simulation]
    GettingStarted --> Dashboard[Dashboard Tutorial]

    Simulations --> RunSim[Running Simulations]
    Simulations --> PSO[PSO Optimization]
    Simulations --> Testing[Testing Workflows]

    API --> Controllers[Controllers API]
    API --> Optimization[Optimization API]
    API --> Plant[Plant Models API]
    API --> Utils[Utilities API]

    Controllers --> ClassicalSMC[Classical SMC]
    Controllers --> STASMC[Super-Twisting]
    Controllers --> AdaptiveSMC[Adaptive SMC]
    Controllers --> HybridSMC[Hybrid SMC]

    Deploy --> Docker[Docker Setup]
    Deploy --> Streamlit[Streamlit Deploy]
    Deploy --> Production[Production Guide]

    Install --> FirstSim
    FirstSim --> RunSim
    RunSim --> PSO
    PSO --> Testing
    Testing --> Production

    style Start fill:#0b2763,stroke:#0b2763,color:#fff
    style GettingStarted fill:#10b981,stroke:#059669,color:#fff
    style Simulations fill:#3b82f6,stroke:#2563eb,color:#fff
    style API fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style Deploy fill:#f59e0b,stroke:#d97706,color:#fff
```

## Documentation Categories Graph

```{mermaid}
graph LR
    Root((DIP SMC PSO)) --> A[📚 Getting Started]
    Root --> B[📖 User Guides]
    Root --> C[🔧 API Reference]
    Root --> D[📐 Theory & Math]
    Root --> E[✅ Testing]
    Root --> F[🚀 Deployment]
    Root --> G[📋 Project Docs]

    A --> A1[Installation]
    A --> A2[Quick Start]
    A --> A3[Dashboard]

    B --> B1[Simulations]
    B --> B2[Optimization]
    B --> B3[Configuration]

    C --> C1[Controllers]
    C --> C2[Optimization]
    C --> C3[Simulation]
    C --> C4[Plant Models]
    C --> C5[Analysis]
    C --> C6[Utilities]

    C1 --> C1A[Classical SMC]
    C1 --> C1B[Super-Twisting]
    C1 --> C1C[Adaptive SMC]
    C1 --> C1D[Hybrid SMC]

    D --> D1[SMC Theory]
    D --> D2[PSO Algorithm]
    D --> D3[Stability Analysis]

    E --> E1[Test Standards]
    E --> E2[Benchmarks]
    E --> E3[Coverage]

    F --> F1[Docker]
    F --> F2[Production]
    F --> F3[Streamlit]

    G --> G1[Changelog]
    G --> G2[Contributing]
    G --> G3[Dependencies]

    style Root fill:#0b2763,stroke:#0b2763,color:#fff
    style A fill:#10b981,stroke:#059669,color:#fff
    style B fill:#3b82f6,stroke:#2563eb,color:#fff
    style C fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style D fill:#ec4899,stroke:#db2777,color:#fff
    style E fill:#14b8a6,stroke:#0d9488,color:#fff
    style F fill:#f59e0b,stroke:#d97706,color:#fff
    style G fill:#6b7280,stroke:#4b5563,color:#fff
```

## User Journey Map

```{mermaid}
journey
    title Documentation User Journey
    section New User
      Read README: 5: User
      Install dependencies: 4: User
      Run first simulation: 5: User
      Explore dashboard: 5: User
    section Active Developer
      Read API docs: 4: Developer
      Implement controller: 3: Developer
      Run PSO optimization: 4: Developer
      Write tests: 3: Developer
    section Researcher
      Study theory: 5: Researcher
      Review benchmarks: 4: Researcher
      Analyze results: 5: Researcher
      Write paper: 4: Researcher
    section DevOps
      Setup Docker: 4: DevOps
      Configure production: 3: DevOps
      Deploy to cloud: 4: DevOps
      Monitor system: 5: DevOps
```

## Quick Navigation

**Click any node in the diagrams above to explore that section!**

For detailed text navigation, see {doc}`documentation_structure`
