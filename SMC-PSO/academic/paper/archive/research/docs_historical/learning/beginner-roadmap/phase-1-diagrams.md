# Phase 1: Visual Diagrams

This page contains visual diagrams to help understand Phase 1 concepts.

## 1. File System Tree

Understanding directory structure is fundamental to working with code projects.

```{mermaid}
graph TD
    A[Computer Drive C:]
    A --> B[Users]
    A --> C[Program Files]
    A --> D[Windows]

    B --> E[YourName]
    E --> F[Documents]
    E --> G[Desktop]
    E --> H[Downloads]

    F --> I[Projects]
    I --> J[dip-smc-pso]
    J --> K[src/]
    J --> L[docs/]
    J --> M[config.yaml]

    style A fill:#FF6B35,stroke:#333,stroke-width:2px,color:#fff
    style J fill:#FF6B35,stroke:#333,stroke-width:2px,color:#fff
    style K fill:#FFE5DB,stroke:#333,stroke-width:1px
    style L fill:#FFE5DB,stroke:#333,stroke-width:1px
    style M fill:#FFE5DB,stroke:#333,stroke-width:1px
```

**Alt text**: File system tree showing the hierarchy from C: drive down to the dip-smc-pso project folder with src, docs, and config.yaml files.

---

## 2. Computing Basics Flowchart

Learn how computers process your commands.

```{mermaid}
flowchart TD
    A[You Type Command] --> B{Valid Command?}
    B -->|Yes| C[CPU Processes]
    B -->|No| D[Error Message]

    C --> E{Need Memory?}
    E -->|Yes| F[Allocate RAM]
    E -->|No| G[Execute]

    F --> G
    G --> H[Store Result]
    H --> I[Display Output]

    D --> J[Try Again]

    style A fill:#FF6B35,stroke:#333,stroke-width:2px,color:#fff
    style I fill:#4ECDC4,stroke:#333,stroke-width:2px,color:#fff
    style D fill:#EF4444,stroke:#333,stroke-width:2px,color:#fff
```

**Alt text**: Flowchart showing the process of command execution: from user input through validation, CPU processing, memory allocation, and output display.

---

## 3. Error Diagnosis Flowchart

Step-by-step guide to debugging Python errors.

```{mermaid}
flowchart TD
    A[Error Occurs] --> B[Read Error Message]
    B --> C{Error Type?}

    C -->|SyntaxError| D[Check Code Syntax]
    C -->|NameError| E[Check Variable Names]
    C -->|TypeError| F[Check Data Types]
    C -->|ImportError| G[Check Package Install]

    D --> H{Fixed?}
    E --> H
    F --> H
    G --> H

    H -->|No| I[Search Online]
    H -->|Yes| J[Run Again]

    I --> K[Apply Solution]
    K --> J

    style A fill:#EF4444,stroke:#333,stroke-width:2px,color:#fff
    style J fill:#4ECDC4,stroke:#333,stroke-width:2px,color:#fff
```

**Alt text**: Error diagnosis flowchart showing how to identify error types (Syntax, Name, Type, Import) and steps to fix them.

---

## 4. Python Data Types Concept Map

Overview of basic Python data types and when to use them.

```{mermaid}
graph TB
    A[Python Data Types]

    A --> B[Numbers]
    A --> C[Text]
    A --> D[Collections]
    A --> E[Boolean]

    B --> B1[int: 42]
    B --> B2[float: 3.14]

    C --> C1[str: Hello]

    D --> D1[list: ordered]
    D --> D2[dict: key-value]

    E --> E1[True/False]

    style A fill:#FF6B35,stroke:#333,stroke-width:2px,color:#fff
    style B fill:#FFE5DB,stroke:#333,stroke-width:1px
    style C fill:#FFE5DB,stroke:#333,stroke-width:1px
    style D fill:#FFE5DB,stroke:#333,stroke-width:1px
    style E fill:#FFE5DB,stroke:#333,stroke-width:1px
```

**Alt text**: Concept map of Python data types: Numbers (int, float), Text (str), Collections (list, dict), and Boolean (True/False).

---

## 5. Installing Software Flowchart

Step-by-step guide to installing Python packages.

```{mermaid}
flowchart TD
    A[Need Package] --> B[Open Terminal]
    B --> C{Virtual Env Active?}

    C -->|No| D[Activate venv]
    C -->|Yes| E[Run pip install]

    D --> E
    E --> F{Success?}

    F -->|Yes| G[Import Package]
    F -->|No| H{Error Type?}

    H -->|Permission| I[Use --user flag]
    H -->|Not Found| J[Check package name]
    H -->|Network| K[Check internet]

    I --> E
    J --> E
    K --> E

    G --> L[Ready to Use]

    style A fill:#FF6B35,stroke:#333,stroke-width:2px,color:#fff
    style L fill:#4ECDC4,stroke:#333,stroke-width:2px,color:#fff
```

**Alt text**: Flowchart for installing Python packages: checking virtual environment, running pip install, handling errors, and verifying success.

---

## 6. Environment Setup Diagram

Understanding Python virtual environments and PATH.

```{mermaid}
graph LR
    A[System Python] -->|DON'T USE| B[Global Packages]

    C[Project 1] --> D[venv1]
    D --> E[Isolated Packages]

    F[Project 2] --> G[venv2]
    G --> H[Different Packages]

    I[Your DIP Project] --> J[venv]
    J --> K[numpy, scipy, etc.]

    style A fill:#EF4444,stroke:#333,stroke-width:2px,color:#fff
    style D fill:#4ECDC4,stroke:#333,stroke-width:2px,color:#fff
    style G fill:#4ECDC4,stroke:#333,stroke-width:2px,color:#fff
    style J fill:#FF6B35,stroke:#333,stroke-width:2px,color:#fff
```

**Alt text**: Diagram showing the separation between system Python (avoid) and project-specific virtual environments (recommended) for clean package management.

---

## Progress Tracker

<div class="phase-progress">
  <div class="progress-fill" style="--progress-percent: 0%;"></div>
</div>

**Phase 1 Completion**: Update this as you complete sub-phases:
- [ ] 1.1 Computing Basics (4 hours)
- [ ] 1.2 Python Fundamentals (20 hours)
- [ ] 1.3 Project Environment (3 hours)
- [ ] 1.4 Basic Physics (8 hours)
- [ ] 1.5 Basic Math (5 hours)

---

[<-- Back to Phase 1](phase-1-foundations.md)
