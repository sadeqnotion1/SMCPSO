# Week 4 Diagram Placement Guide: Exact Locations & Specifications

**Implementation Reference** for placement of all 22-25 diagrams

---

## Phase 1: Foundations (6 Diagrams)

### Diagram 1.1A: Computing Basics - File Navigation Flowchart
**Location**: `phase-1-foundations.md` → Section 1.1 (Computing Basics)
**Placement**: After "Learning Path" header, before "Step 1"
**Estimated Line**: ~45 (after existing content)

**Specification**:
- Type: Flowchart (Top-Down)
- Nodes: pwd → ls → cd → File found / Not found
- Colors: Phase 1 Blue (#2563eb)
- Size: Max 400px width
- Wrapper: Dropdown with `:color: info`, `:icon: octicon-terminal`
- Label: "Visualize: File Navigation Workflow"

**Why This Helps**: Beginners struggle with "where am I?" - visual flowchart makes pwd/ls/cd intuitive

**Code Template**:
```markdown
:::{dropdown} Visualize: File Navigation Workflow
:color: info
:icon: octicon-terminal
:animate: fade-in-slide-down

```{mermaid}
flowchart TD
    A["Start<br/>pwd"] --> B["See current location"]
    B --> C["List files<br/>ls"]
    C --> D{"File exists?"}
    D -->|Yes| E["Navigate to it<br/>cd file-path"]
    D -->|No| F["Create it or check path"]
    E --> G["Success"]
    F --> A
    style A fill:#e0f2fe
    style G fill:#dbeafe
```

What to Try: In your terminal, type pwd, then ls, then cd to a folder and repeat.
:::
```

---

### Diagram 1.1B: File System Tree Diagram
**Location**: `phase-1-foundations.md` → Section 1.1 (Computing Basics)
**Placement**: After "Practice Exercise", before "Resources"
**Estimated Line**: ~80

**Specification**:
- Type: Tree diagram
- Depth: 4-5 levels (C: → Users → YourName → Documents → project)
- Colors: Phase 1 Blue with gradient
- Wrapper: Dropdown with `:color: primary`
- Label: "Visualize: Your Computer's File Structure"

**Why This Helps**: File systems are highly abstract - tree visualization makes hierarchy concrete

**Code Template**:
```markdown
:::{dropdown} Visualize: Your Computer's File Structure
:color: primary
:icon: octicon-file-tree

```{mermaid}
flowchart TB
    A["C:\<br/>Root Drive"]
    B["Users/"]
    C["YourName/"]
    D["Documents/"]
    E["Desktop/"]
    F["coding-practice/<br/>← You create this"]

    A --> B
    B --> C
    C --> D
    C --> E
    D --> F

    style A fill:#dbeafe
    style F fill:#f0fdf4
    style B fill:#eff6ff
    style C fill:#eff6ff
    style D fill:#eff6ff
```

What to Try: Open File Explorer and navigate to your Documents folder. Can you find the path?
:::
```

---

### Diagram 1.2: Python Data Types - Concept Map
**Location**: `phase-1-foundations.md` → Section 1.2 (Python Fundamentals)
**Placement**: Start of section, after overview table, before "Step 1: Variables and Data Types"
**Estimated Line**: ~265

**Specification**:
- Type: Concept/Mind map
- Center: "Python Data Types"
- Branches: Numbers, Strings, Booleans, Collections
- Colors: Phase 1 Blue hierarchy
- Wrapper: Collapsible dropdown
- Label: "Overview: Python Data Types Relationships"

**Why This Helps**: Beginners see isolated topics - concept map shows how they connect

**Code Template**:
```markdown
:::{dropdown} Overview: Python Data Types Relationships
:color: primary
:icon: octicon-branch
:animate: fade-in-slide-down

```{mermaid}
mindmap
    root((Python Data<br/>Types))
        Numbers
            int
                Whole numbers
                No decimal
            float
                Decimals
                1.5, 3.14
        Strings
            Text
            "Hello World"
            Quoted text
        Booleans
            True/False
            Only 2 values
        Collections
            Lists [1,2,3]
            Dictionaries {key: value}
            Tuples (immutable)
```

This diagram shows how Python organizes data types into categories. Notice:
- **Numbers** split into int vs float
- **Strings** are for text only
- **Booleans** are special (True or False)
- **Collections** group multiple values

Why This Matters: Every Python program uses these 4 categories. Understanding them makes code readable.
:::
```

---

### Diagram 1.3: Error Diagnosis - Decision Flowchart
**Location**: `phase-1-foundations.md` → Section 1.3 (Setting Up Environment) → Troubleshooting Dropdowns
**Placement**: As visual summary before/after troubleshooting section
**Estimated Line**: ~900

**Specification**:
- Type: Flowchart (Decision tree)
- Start: "Python Error Occurred"
- Paths: NameError, ImportError, SyntaxError, IndentationError
- Colors: Warning orange (#f59e0b) for main flow
- Wrapper: Info dropdown
- Label: "Diagnose: Python Errors Quick Guide"

**Why This Helps**: Beginners panic at errors - flowchart guides them to solutions systematically

**Code Template**:
```markdown
:::{dropdown} Diagnose: Python Errors Quick Guide
:color: warning
:icon: octicon-bug

```{mermaid}
flowchart TD
    A["Error Message"] --> B{"What type?"}
    B -->|NameError| C["Variable not<br/>defined yet"]
    B -->|ImportError| D["Module not<br/>installed"]
    B -->|SyntaxError| E["Typo in code<br/>syntax"]
    B -->|IndentationError| F["Wrong spacing<br/>at start"]

    C --> C1["Check variable<br/>spelling"]
    D --> D1["pip install<br/>module-name"]
    E --> E1["Review code<br/>for typos"]
    F --> F1["Fix spaces/tabs<br/>at line start"]

    C1 --> G["Retry"]
    D1 --> G
    E1 --> G
    F1 --> G

    style A fill:#fef3c7
    style B fill:#fef3c7
    style G fill:#dbeafe
```

This decision tree helps you:
1. Read the error message type
2. Find matching solution
3. Apply fix
4. Retry
:::
```

---

### Diagram 1.4A: Pendulum Physics - Simple State Diagram
**Location**: `phase-1-foundations.md` → Section 1.4 (Basic Physics)
**Placement**: After "What You'll Learn", before "Learning Path"
**Estimated Line**: ~1060

**Specification**:
- Type: State machine diagram
- States: Upright, Falling, Swinging, At Rest
- Transitions: Gravity, Control force, Friction
- Colors: Physics blue (#3b82f6) with motion indicators
- Wrapper: Dropdown with educational color
- Label: "Visualize: Pendulum States and Transitions"

**Why This Helps**: Physics concepts are invisible - visualization makes state changes tangible

**Code Template**:
```markdown
:::{dropdown} Visualize: Pendulum States and Transitions
:color: info
:icon: octicon-mortar-board
:animate: fade-in-slide-down

```{mermaid}
stateDiagram-v2
    [*] --> Upright

    Upright --> Falling: Gravity pulls
    Falling --> Swinging: Max speed at bottom
    Swinging --> Upright: Momentum carries up
    Swinging --> Falling: Not enough momentum
    Swinging --> AtRest: Friction dissipates energy

    AtRest --> [*]

    note right of Upright
        Unstable equilibrium
        Small push falls
    end note

    note right of Swinging
        Continuous motion
        Energy decreases
    end note

    note right of AtRest
        Stable equilibrium
        No motion
    end note

    style Upright fill:#fef3c7
    style Falling fill:#fed7aa
    style Swinging fill:#dbeafe
    style AtRest fill:#d1fae5
```

What's Happening:
- Upright: Natural resting position (unstable)
- Falling: Gravity pulls pendulum down
- Swinging: Momentum carries it up other side
- At Rest: Friction eventually stops motion
:::
```

---

### Diagram 1.4B: Physics Forces - Vector Diagram
**Location**: `phase-1-foundations.md` → Section 1.4 (Basic Physics) → Step 1 subsection
**Placement**: After "Forces and Newton's Laws" introductory text
**Estimated Line**: ~1150

**Specification**:
- Type: Block/vector diagram
- Forces shown: Gravity (down), Control (left/right), Friction (opposite motion)
- Colors: Arrows with phase colors for different forces
- Wrapper: Dropdown within Step 1
- Label: "Visualize: Forces Acting on a Pendulum"

**Why This Helps**: Force interactions are abstract - vector diagram makes them concrete and visual

**Code Template**:
```markdown
:::{dropdown} Visualize: Forces Acting on a Pendulum
:color: info
:icon: octicon-arrow-switch

```{mermaid}
graph TB
    subgraph "Forces on Pendulum"
        direction TB
        P["Pendulum<br/>at angle θ"]
        G["↓ Gravity<br/>F_g = mg<br/>Always down"]
        C["← Control Force<br/>F_u = u(t)<br/>Applied by motor"]
        F["← Friction<br/>F_friction = -bv<br/>Opposes motion"]
    end

    P --> G
    P --> C
    P --> F

    style P fill:#fef3c7
    style G fill:#fee2e2
    style C fill:#dbeafe
    style F fill:#e0e7ff
```

Understanding Forces:
- **Gravity (red)**: Always pulls downward, even when pendulum is at an angle
- **Control (blue)**: Applied by motor, can push left or right
- **Friction (purple)**: Always opposes motion, causes energy loss

Together, these three forces determine the pendulum's motion!
:::
```

---

## Phase 2: Core Concepts (7 Diagrams)

### Diagram 2.1: Control Loop - Circular Feedback
**Location**: `phase-2-core-concepts.md` → Section 2.1 (What is Control Theory?)
**Placement**: After "What You'll Learn", before "Learning Path"
**Estimated Line**: ~50

**Specification**:
- Type: Circular flowchart
- Flow: Setpoint → Error → Controller → Plant → Feedback → Loop
- Colors: Phase 2 Green (#10b981)
- Wrapper: Dropdown with success color
- Label: "Core Concept: The Control Loop"

**Why This Helps**: Control theory is built on feedback loops - circular diagram is the perfect metaphor

**Code Template**:
```markdown
:::{dropdown} Core Concept: The Control Loop
:color: success
:icon: octicon-git-compare
:animate: fade-in-slide-down

```{mermaid}
graph TB
    S["Setpoint<br/>(Desired)<br/>T = 70°F"]
    P["Plant<br/>(System)<br/>House + Heat"]
    M["Measurement<br/>(Sensor)<br/>Thermometer"]
    E["Error<br/>Calculation<br/>e = desired - actual"]
    C["Controller<br/>(Decision)<br/>Turn up/down heat"]

    S --> E
    M --> E
    E --> C
    C --> P
    P --> M
    M -.Feedback.-> E

    style S fill:#d1fae5
    style P fill:#f0fdf4
    style M fill:#d1fae5
    style E fill:#a7f3d0
    style C fill:#86efac
```

This is the **thermostat example**:
1. You want room at 70°F (Setpoint)
2. Thermometer measures actual temp (Measurement)
3. Compare desired vs actual (Error)
4. Decide to heat or cool (Controller)
5. Heater/AC changes room temp (Plant)
6. Loop repeats every few seconds (Feedback)

This **feedback loop** is in every control system!
:::
```

---

### Diagram 2.2: Feedback vs Open-Loop - Comparison
**Location**: `phase-2-core-concepts.md` → Section 2.2 (Feedback Control)
**Placement**: After "Open-Loop vs Closed-Loop Control" header, before detailed explanation
**Estimated Line**: ~150

**Specification**:
- Type: Comparison flowchart (side-by-side)
- Left: Open-Loop (Toaster), Right: Closed-Loop (Oven)
- Colors: Phase 2 Green for closed-loop, Gray for open-loop
- Wrapper: Tabs or side-by-side divs
- Label: "Compare: Open-Loop vs Closed-Loop Control"

**Code Template**:
```markdown
:::{dropdown} Compare: Open-Loop vs Closed-Loop Control
:color: success
:icon: octicon-git-compare

```{mermaid}
graph TB
    subgraph open["Open-Loop (Toaster)"]
        T1["You set<br/>Timer = 2 min"]
        T2["Toaster runs<br/>for 2 minutes"]
        T3["Toaster stops<br/>regardless of color"]
        T1 --> T2 --> T3
    end

    subgraph closed["Closed-Loop (Smart Oven)"]
        O1["You want<br/>Temperature = 350°F"]
        O2["Sensor measures<br/>current temperature"]
        O3["Compare desired<br/>vs actual"]
        O4["Turn heating on/off<br/>to reach target"]
        O5["Maintain 350°F<br/>automatically"]
        O1 --> O3
        O2 --> O3
        O3 --> O4
        O4 --> O5
        O5 -.Feedback.-> O3
    end

    style T3 fill:#fee2e2
    style O5 fill:#d1fae5
    style O3 fill:#a7f3d0
```

**Key Difference**:
- **Open-Loop**: No feedback. Set and forget. Works only if conditions are known.
- **Closed-Loop**: Measures result, adjusts continuously. Handles unexpected changes.

Real-world: Every safe control system is closed-loop (feedback-based).
:::
```

---

### Diagram 2.3: SMC Intuitive - Concept Map
**Location**: `phase-2-core-concepts.md` → Section 2.3 (Intro to Sliding Mode Control)
**Placement**: After section intro, before "What is Sliding Mode Control?"
**Estimated Line**: ~280

**Specification**:
- Type: Concept map (mind map)
- Center: "Sliding Mode Control"
- Branches: Surface Design, Forcing, Sliding, Convergence, Stability
- Colors: Phase 2 Green hierarchy
- Wrapper: Dropdown
- Label: "Concept: How Sliding Mode Control Works"

**Why This Helps**: SMC theory is confusing - concept map breaks it into intuitive pieces

**Code Template**:
```markdown
:::{dropdown} Concept: How Sliding Mode Control Works (Intuitive)
:color: success
:icon: octicon-mortar-board
:animate: fade-in-slide-down

```{mermaid}
mindmap
    root((Sliding Mode<br/>Control))
        1. Design Surface
            Choose a path in state space
            s(x) = 0
            Like drawing a target line
        2. Force onto Surface
            Apply control to push states
            toward surface
            u = control action
        3. Slide Along Surface
            Once on surface,
            states follow it
            s = 0 always
        4. Reach Goal
            States converge to
            desired value
            Stable equilibrium
        5. Robustness
            Works even with
            disturbances
            Insensitive to uncertainty
```

**Intuitive Explanation**:
1. **Surface**: Imagine a line on a map (your desired path)
2. **Force**: Control pushes system toward the line
3. **Slide**: Once on the line, system slides along it
4. **Converge**: System reaches your goal reliably
5. **Robust**: Even if obstacles appear, it stays on track!

Compare to: Sliding down a target line on paper, even with turbulence.
:::
```

---

### Diagram 2.4: Optimization Problem Space - Landscape
**Location**: `phase-2-core-concepts.md` → Section 2.4 (What is Optimization?)
**Placement**: After "Why Optimization?" header, before PSO introduction
**Estimated Line**: ~410

**Specification**:
- Type: Contour/landscape diagram
- Shows: 2D problem space with optimal point highlighted
- Colors: Phase 2 Green valley/mountain
- Wrapper: Dropdown
- Label: "Visualize: Optimization Problem Space"

**Why This Helps**: Optimization is abstract - landscape diagram makes it visual

**Code Template**:
```markdown
:::{dropdown} Visualize: Optimization Problem Space
:color: success
:icon: octicon-location

```{mermaid}
graph TB
    subgraph landscape["Imagine a Landscape"]
        A["⛰️ Hilly terrain"]
        B["🎯 Golden valley = Best solution"]
        C["High peaks = Bad solutions"]
    end

    subgraph problem["PSO Particles Search"]
        P1["🕊️ Particle 1: On peak"]
        P2["🕊️ Particle 2: In valley"]
        P3["🕊️ Particle 3: On slope"]
        P4["They explore terrain<br/>toward best spot"]
    end

    landscape --> problem

    A --> A1["High cost = Bad performance"]
    B --> B1["Low cost = Good performance"]
    C --> C1["Need to find valley"]

    style B fill:#d1fae5
    style A fill:#fee2e2
    style C fill:#fee2e2
    style B1 fill:#a7f3d0
```

**The Optimization Problem**:
- **Landscape**: Each point is a different controller gain setting
- **Height**: How good is this setting (lower is better)?
- **Valley**: The optimal gains (what PSO is searching for)
- **Particles**: Try different settings, learn from each other, converge to valley

PSO is like birds flocking toward the best feeding ground!
:::
```

---

### Diagram 2.5A: DIP System - Block Diagram
**Location**: `phase-2-core-concepts.md` → Section 2.5 (Understanding the DIP System)
**Placement**: After "What is a Double-Inverted Pendulum?" header
**Estimated Line**: ~550

**Specification**:
- Type: Block diagram
- Shows: Cart + Pendulum 1 + Pendulum 2 relationships
- Colors: Phase 2 Green with component distinction
- Wrapper: Dropdown
- Label: "System Overview: Double-Inverted Pendulum Components"

**Code Template**:
```markdown
:::{dropdown} System Overview: Double-Inverted Pendulum Components
:color: success
:icon: octicon-cpu

```{mermaid}
graph TB
    subgraph DIP["Physical System"]
        Cart["🚗 Cart<br/>Moves left/right<br/>x(t)"]
        P1["⚙️ Pendulum 1<br/>Attached to cart<br/>θ₁(t)"]
        P2["⚙️ Pendulum 2<br/>On top of P1<br/>θ₂(t)"]
        Motor["⚡ Motor<br/>Applies force to cart<br/>u(t)"]
    end

    subgraph Control["Control System"]
        Sensors["📍 Sensors<br/>Measure x, θ₁, θ₂"]
        Controller["🧠 Controller<br/>Computes u(t)"]
    end

    Motor --> Cart
    Cart --> P1
    P1 --> P2

    Cart --> Sensors
    P1 --> Sensors
    P2 --> Sensors
    Sensors --> Controller
    Controller --> Motor

    style Cart fill:#d1fae5
    style P1 fill:#f0fdf4
    style P2 fill:#f0fdf4
    style Motor fill:#a7f3d0
    style Controller fill:#86efac
```

**The System Has**:
1. **Cart**: Heavy base that moves left/right
2. **Pendulum 1**: Lighter pole, balanced on cart
3. **Pendulum 2**: Another pole on top of pendulum 1 (harder to control!)
4. **Motor**: Pushes cart to keep both poles upright
5. **Sensors**: Measure positions constantly
6. **Controller**: Decides where to push cart to keep system stable

**Why It's Hard**: Push one way, top pendulum goes the opposite way!
:::
```

---

### Diagram 2.5B: Energy Flow in DIP - Sankey Diagram
**Location**: `phase-2-core-concepts.md` → Section 2.5 (Understanding the DIP System)
**Placement**: After DIP components section, in subsection about energy
**Estimated Line**: ~650

**Specification**:
- Type: Flow/Sankey diagram
- Flow: Motor → Kinetic Energy → Potential Energy → Friction Losses
- Colors: Phase 2 Green to gray gradient
- Wrapper: Dropdown
- Label: "Energy Journey: From Motor to Friction"

**Code Template**:
```markdown
:::{dropdown} Energy Journey: From Motor to Friction
:color: success
:icon: octicon-zap

```{mermaid}
graph LR
    A["⚡ Motor<br/>Electrical Energy<br/>P = u·i<br/>Input Power"]
    B["🏃 Motion<br/>Kinetic Energy<br/>T = ½mv²<br/>Cart & pendulum velocity"]
    C["📏 Position<br/>Potential Energy<br/>V = mgh<br/>Height of pendulums"]
    D["🔥 Heat<br/>Friction Losses<br/>P_friction = bv²<br/>Lost to air & bearings"]
    E["🎯 Control<br/>Work Done by Motor<br/>W = ∫u·v dt<br/>Maintains motion"]

    A --> B
    A --> E
    B --> C
    C --> D
    B --> D

    style A fill:#a7f3d0
    style B fill:#d1fae5
    style C fill:#d1fae5
    style D fill:#fee2e2
    style E fill:#86efac
```

**Energy Flow**:
1. **Motor input**: Electrical energy pushes cart
2. **Kinetic Energy**: Movement of cart and pendulums (velocity = speed)
3. **Potential Energy**: Height of pendulums (higher = more PE)
4. **Friction losses**: Bearings and air resistance convert energy to heat
5. **Control work**: Motor must continuously do work to overcome friction and maintain motion

Key insight: Without the motor, friction dissipates all energy and system stops. With PSO, we optimize the motor's work to minimize energy waste while keeping system stable!
:::
```

---

### Diagram 2.3B: Sliding Surface Visualization (Optional - Optional Advanced)
**Location**: `phase-2-core-concepts.md` → Section 2.3 (Intro to Sliding Mode Control) → Advanced subsection
**Placement**: After "How Does SMC Force onto the Surface?" section
**Estimated Line**: ~380

**Specification**:
- Type: State space trajectory plot
- Shows: 2D state space with sliding surface line and state trajectories
- Colors: Phase 2 Green surface, blue trajectories
- Wrapper: Dropdown marked "Advanced (Optional)"
- Label: "Advanced: Visualizing Convergence to Sliding Surface"

**Code Template**:
```markdown
:::{dropdown} Advanced: Visualizing Convergence to Sliding Surface (Optional)
:color: info
:icon: octicon-graph

**Note**: This is an optional advanced visualization. Understand the concept first!

```{mermaid}
graph TB
    subgraph StateSpace["2D State Space"]
        S["Sliding Surface: s(x) = 0<br/>Target line (green)"]
        T1["Trajectory 1<br/>Starts above surface<br/>Converges down"]
        T2["Trajectory 2<br/>Starts below surface<br/>Converges up"]
        Conv["Both reach surface<br/>and slide along it"]
    end

    T1 --> Conv
    T2 --> Conv
    S --> Conv

    style S fill:#d1fae5
    style Conv fill:#a7f3d0
```

**What's Happening**:
- **Green line**: The sliding surface (your target)
- **Blue path**: State trajectories (actual system motion)
- **Convergence**: Both reach the surface from different starting points
- **Sliding**: Once on surface, states slide along it toward the goal

This proves SMC is **robust**: No matter where you start, you reach the target!
:::
```

---

## Phase 3: Hands-On Learning (4 Diagrams)

### Diagram 3.1: Simulation Workflow - Process Flowchart
**Location**: `phase-3-hands-on.md` → Section 3.1 (Running Your First Simulation)
**Placement**: After "What You'll Learn", before "Step 1"
**Estimated Line**: ~50

**Specification**:
- Type: Simple process flowchart
- Flow: Start → Config → Run → Analyze → Save → End
- Colors: Phase 3 Orange (#f59e0b)
- Wrapper: Dropdown
- Label: "Workflow: Running a Simulation Start to Finish"

**Code Template**:
```markdown
:::{dropdown} Workflow: Running a Simulation Start to Finish
:color: warning
:icon: octicon-play

```{mermaid}
flowchart TD
    A["Start<br/>python simulate.py"]
    B["Choose Controller<br/>--ctrl classical_smc"]
    C["(Optional) Load Gains<br/>--load gains.json"]
    D["Run Simulation<br/>ODE integration ~2 sec"]
    E["Simulation Complete<br/>State data generated"]
    F["Plot Results<br/>--plot shows graphs"]
    G{"Satisfied?"}
    G -->|No| H["Modify Parameters<br/>config.yaml"]
    H --> A
    G -->|Yes| I["Save Results<br/>--save output.json"]
    I --> J["End"]

    A --> B --> C --> D --> E --> F --> G --> I --> J

    style A fill:#fef3c7
    style F fill:#dbeafe
    style J fill:#dbeafe
```

**The Workflow**:
1. **Start**: Run Python command
2. **Configure**: Choose controller type
3. **Load**: (Optional) Use previous gains
4. **Execute**: Simulation runs (takes ~2 seconds)
5. **Analyze**: Plot results appear
6. **Decide**: Satisfied or try again?
7. **Save**: Store good results

This is your **experimental loop**: Try → Observe → Modify → Repeat
:::
```

---

### Diagram 3.2A: Result Interpretation - Decision Flowchart
**Location**: `phase-3-hands-on.md` → Section 3.2 (Understanding Simulation Results)
**Placement**: After "What You'll Learn", before "Learning Path"
**Estimated Line**: ~150

**Specification**:
- Type: Decision tree flowchart
- Questions: Is system stable? Oscillating? Overshoot? Settling time?
- Colors: Phase 3 Orange with red/green success/failure
- Wrapper: Dropdown
- Label: "Diagnose: Interpreting Simulation Plots"

**Code Template**:
```markdown
:::{dropdown} Diagnose: Interpreting Simulation Plots
:color: warning
:icon: octicon-alert

```{mermaid}
flowchart TD
    A["Plot Shows<br/>State over time"]
    B{"System stable?<br/>No wild oscillations?"}
    B -->|No| C["❌ System unstable<br/>Increase gains"]
    B -->|Yes| D{"Smooth convergence?<br/>No ringing?"}
    D -->|No| E["⚠️ Overshoot/oscillation<br/>Decrease gains or increase damping"]
    D -->|Yes| F{"Reaches goal?<br/>Within tolerance?"}
    F -->|No| G["❌ Poor tracking<br/>Adjust control law"]
    F -->|Yes| H["Settling time ok?<br/>Within 2 seconds?"]
    H -->|No| I["⚠️ Slow response<br/>Increase controller speed"]
    H -->|Yes| J["✅ Good control!<br/>Keep these gains"]

    style J fill:#d1fae5
    style C fill:#fee2e2
    style E fill:#fef3c7
    style G fill:#fee2e2
    style I fill:#fef3c7
```

**How to Read Your Plots**:
1. **Stable**: No diverging oscillations (system doesn't blow up)
2. **Smooth**: Minimal ripple or ringing (clean approach to goal)
3. **Accurate**: Reaches desired value (tracks reference)
4. **Fast**: Settles in reasonable time (responds quickly)

Use this flowchart to diagnose what's wrong when control looks bad!
:::
```

---

### Diagram 3.2B: Performance Metrics - Relationship Diagram
**Location**: `phase-3-hands-on.md` → Section 3.2 (Understanding Simulation Results) → Metrics subsection
**Placement**: After "Key Metrics to Understand" header
**Estimated Line**: ~280

**Specification**:
- Type: Relationship/concept diagram
- Metrics: Response Time, Overshoot, Settling Time, Steady-State Error
- Colors: Phase 3 Orange with metric colors
- Wrapper: Dropdown
- Label: "Metrics: Understanding Control Performance"

**Code Template**:
```markdown
:::{dropdown} Metrics: Understanding Control Performance
:color: warning
:icon: octicon-graph

```{mermaid}
graph TB
    subgraph metrics["Performance Metrics"]
        RT["⏱️ Response Time<br/>How fast system reacts<br/>Faster = Better control<br/>Trade-off: May cause overshoot"]
        OS["📈 Overshoot<br/>Peak above target<br/>High overshoot = Oscillation<br/>Should be < 5-20%"]
        ST["📊 Settling Time<br/>Time to stabilize at goal<br/>Typically 1-3 seconds<br/>Depends on system speed"]
        SSE["📍 Steady-State Error<br/>Final difference from goal<br/>Should be < 1% of range<br/>Zero with integral action"]
    end

    subgraph tradeoffs["Trade-offs"]
        T1["Fast response<br/>→ More overshoot"]
        T2["Low overshoot<br/>→ Slower response"]
        T3["Balance needed<br/>through tuning"]
    end

    RT --> T1
    OS --> T2
    ST --> T3
    SSE --> T3

    style RT fill:#fef3c7
    style OS fill:#fed7aa
    style ST fill:#dbeafe
    style SSE fill:#d1fae5
```

**What Each Metric Means**:
- **Response Time**: Delay before system reacts (want small)
- **Overshoot**: Peak above target (want small, <5-10%)
- **Settling Time**: Time to reach steady state (want small, 1-3 sec)
- **Steady-State Error**: Final error (want zero or very small)

Key: You can't optimize all metrics simultaneously. Tuning is about balancing trade-offs!
:::
```

---

### Diagram 3.4: Parameter Tuning - Feedback Loop
**Location**: `phase-3-hands-on.md` → Section 3.4 (Modifying Configuration)
**Placement**: After "Tuning Gains" introduction
**Estimated Line**: ~420

**Specification**:
- Type: Circular feedback loop
- Flow: Measure → Compare → Adjust → Measure (repeat)
- Colors: Phase 3 Orange with learning cycle indicators
- Wrapper: Dropdown
- Label: "Learning: Parameter Tuning Feedback Loop"

**Code Template**:
```markdown
:::{dropdown} Learning: Parameter Tuning Feedback Loop
:color: warning
:icon: octicon-sync

```{mermaid}
flowchart TD
    A["Current Gains<br/>K = [k1, k2, k3, ...]"]
    B["Run Simulation<br/>with current gains"]
    C["Measure Performance<br/>response time, overshoot, error"]
    D["Compare to Goals<br/>Is it good enough?"]
    E{"Acceptable?"}
    E -->|Yes| F["✅ Keep these gains<br/>Excellent control!"]
    E -->|No| G{"What's wrong?"}
    G -->|Unstable| H["🔴 Decrease gains"]
    G -->|Slow| I["🟢 Increase gains"]
    G -->|Oscillating| J["🟡 Smooth transitions<br/>Increase damping"]
    H --> K["Adjust K values<br/>in config.yaml"]
    I --> K
    J --> K
    K --> A

    style F fill:#d1fae5
    style A fill:#fef3c7
    style D fill:#fef3c7
```

**This is the Experimental Loop**:
1. **Set**: Initial gain values
2. **Run**: Simulation
3. **Measure**: How well does it perform?
4. **Diagnose**: What's the problem?
5. **Adjust**: Modify gains
6. **Repeat**: Until satisfied

This loop is how real engineers tune controllers!
:::
```

---

## Phase 4: Advancing Skills (3 Diagrams)

### Diagram 4.1: Source Code Navigation - Tree
**Location**: `phase-4-advancing-skills.md` → Section 4.1 (Reading the Source Code)
**Placement**: After section intro, before "File Structure" explanation
**Estimated Line**: ~80

**Specification**:
- Type: Tree diagram showing src/ structure
- Depth: 3-4 levels, key directories highlighted
- Colors: Phase 4 Purple (#8b5cf6)
- Wrapper: Dropdown
- Label: "Navigate: Project Source Code Structure"

**Code Template**:
```markdown
:::{dropdown} Navigate: Project Source Code Structure
:color: secondary
:icon: octicon-file-tree

```{mermaid}
flowchart TB
    A["src/<br/>Source code root"]

    B["controllers/<br/>All control laws"]
    C["core/<br/>Simulation engine"]
    D["optimizer/<br/>PSO tuning"]
    E["utils/<br/>Helpers & tools"]
    F["plant/<br/>Physical models"]
    G["hil/<br/>Hardware interface"]

    H["classic_smc.py"]
    I["sta_smc.py"]
    J["hybrid_smc.py"]

    K["simulation_runner.py"]
    L["dynamics.py"]

    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G

    B --> H
    B --> I
    B --> J

    C --> K
    C --> L

    style A fill:#ede9fe
    style B fill:#f5f3ff
    style C fill:#f5f3ff
    style D fill:#f5f3ff
    style E fill:#f5f3ff
    style F fill:#f5f3ff
    style G fill:#f5f3ff
```

**Source Code Organization**:
- **controllers/**: All SMC variants (where control algorithms live)
- **core/**: Simulation engine (ODE integration, state updates)
- **optimizer/**: PSO parameter tuning (gain optimization)
- **utils/**: Helper functions (plotting, validation, analysis)
- **plant/**: Dynamics models (physics equations)
- **hil/**: Hardware-in-loop interface (experimental setup)

When reading code, this tree helps you navigate!
:::
```

---

### Diagram 4.2: Mathematical Notation - Glossary Map
**Location**: `phase-4-advancing-skills.md` → Section 4.2 (Reading Mathematical Code)
**Placement**: After "Mathematical Notation" introduction
**Estimated Line**: ~200

**Specification**:
- Type: Concept map (glossary style)
- Terms: Variables, derivatives, matrices, norms
- Colors: Phase 4 Purple with term categories
- Wrapper: Dropdown
- Label: "Reference: Mathematical Notation Used in Code"

**Code Template**:
```markdown
:::{dropdown} Reference: Mathematical Notation Used in Code
:color: secondary
:icon: octicon-sigma

```{mermaid}
mindmap
    root((Mathematical<br/>Notation))
        Variables
            x, y, z
                State variables
            t
                Time
            u, v
                Control/velocity
        Operators
            Dot (ẋ)
                Time derivative
                dx/dt
            Prime (x')
                Discrete derivative
            Hat (x̂)
                Estimate/approximation
        Matrices
            M, C, G
                Inertia, Coriolis, gravity
            A, B, C
                State-space matrices
        Norms & Functions
            ||x||
                Vector length
            |x|
                Absolute value
            sat(x)
                Saturation function
```

**Common Notation**:
- **ẋ**: Time derivative of x (how fast x changes)
- **x̂**: Estimated value of x
- **||x||**: Length of vector x
- **sat()**: Saturation (limits value to range)

When reading code, this reference helps decode math symbols!
:::
```

---

### Diagram 4.3: Controller Comparison - Matrix
**Location**: `phase-4-advancing-skills.md` → Section 4.3 (Comparing Controllers)
**Placement**: After comparison introduction
**Estimated Line**: ~350

**Specification**:
- Type: Feature/property table with diagram overlay
- Compares: Classical, Adaptive, Super-Twisting, Hybrid SMC
- Colors: Phase 4 Purple with feature ratings
- Wrapper: Could be table + dropdown diagram
- Label: "Compare: SMC Controller Variants at a Glance"

**Code Template**:
```markdown
:::{dropdown} Compare: SMC Controller Variants at a Glance
:color: secondary
:icon: octicon-checklist

```{mermaid}
graph TB
    subgraph properties["Controller Properties"]
        P1["Robustness<br/>Classical: High<br/>Adaptive: Very High<br/>STA: Very High<br/>Hybrid: Excellent"]
        P2["Chattering<br/>Classical: High<br/>Adaptive: Medium<br/>STA: Low<br/>Hybrid: Low"]
        P3["Complexity<br/>Classical: Low<br/>Adaptive: Medium<br/>STA: High<br/>Hybrid: High"]
        P4["Speed<br/>Classical: Fast<br/>Adaptive: Fast<br/>STA: Slow (Smooth)<br/>Hybrid: Medium"]
    end

    style P1 fill:#d1fae5
    style P2 fill:#d1fae5
    style P3 fill:#fef3c7
    style P4 fill:#d1fae5
```

| Controller | Robustness | Chattering | Complexity | When to Use |
|------------|-----------|-----------|-----------|------------|
| Classical | High | High | Low | Simple systems |
| Adaptive | Very High | Medium | Medium | Uncertain parameters |
| Super-Twisting | Very High | Low | High | High precision needed |
| Hybrid | Excellent | Low | High | Best overall performance |

Choose based on your requirements:
- **Want simple and fast?** → Classical
- **Need robustness?** → Adaptive
- **Smooth control?** → Super-Twisting
- **Best of everything?** → Hybrid
:::
```

---

## Phase 5: Mastery (2 Diagrams)

### Diagram 5: Specialization Decision Tree
**Location**: `phase-5-mastery.md` → Opening section before sub-phases
**Placement**: After "Phase 5 Overview" header, before phase table
**Estimated Line**: ~60

**Specification**:
- Type: Decision tree / Flowchart
- Questions: Guide learner to specialization path
- Colors: Phase 5 Red (#ef4444)
- Wrapper: Dropdown
- Label: "Choose: Your Specialization Path"

**Code Template**:
```markdown
:::{dropdown} Choose: Your Specialization Path
:color: danger
:icon: octicon-git-branch

```{mermaid}
flowchart TD
    A["Where are you<br/>in your journey?"]
    B{"Interested in<br/>Theory?"}
    C{"Prefer Practical<br/>Applications?"}

    B -->|Yes| D["5.1: Deep Dive<br/>Lyapunov Stability"]
    B -->|No| C

    C -->|Yes| E{"Want to<br/>Optimize?"}
    E -->|Yes| F["5.2: Advanced PSO<br/>Parameter Tuning"]
    E -->|No| G["5.3: Robustness<br/>Analysis"]

    D --> H["Go to Phase 5.1"]
    F --> I["Go to Phase 5.2"]
    G --> J["Go to Phase 5.3"]

    style H fill:#fee2e2
    style I fill:#fee2e2
    style J fill:#fee2e2
```

**Specialization Options**:
- **5.1 Theory Path**: Understand mathematical foundations deeply
- **5.2 Optimization Path**: Master PSO and parameter tuning
- **5.3 Robustness Path**: Learn to handle real-world uncertainties
- **5.4 Research Path**: Contribute to open problems
- **5.5 Implementation Path**: Build hardware systems

Choose based on your interests and career goals!
:::
```

---

## Progress Visualization Locations

### Progress Bar System
**Location**: Each phase overview section
**Example Placement**: `phase-1-foundations.md` → Top of content, after breadcrumbs

**HTML/CSS**:
```html
<div class="progress-container phase-1">
  <div class="progress-label">Your Progress: Phase 1</div>
  <div class="progress-bar">
    <div class="progress-fill" style="width: 40%">
      <span class="progress-text">40% (16/40 hours)</span>
    </div>
  </div>
</div>
```

### Completion Badges
**Location**: End of each sub-phase section
**Example**: After completing 1.1, badge shows "✓ Computing Basics (4 hours)"

**Format**:
```markdown
::::{grid}
:::{grid-item}
✓ **1.1 Computing Basics** (4/40 hours)
:::
:::{grid-item}
✓ **1.2 Python Fundamentals** (20/40 hours)
:::
:::{grid-item}
○ **1.3 Environment Setup** (3/40 hours)
:::
::::
```

### Timeline Visualization
**Location**: `beginner-roadmap.md` → After introduction
**Format**: Mermaid Gantt or custom timeline HTML

```markdown
:::{dropdown} Timeline: Your 4-6 Month Learning Journey
:color: primary
:icon: octicon-calendar

```{mermaid}
timeline
    title Beginner Roadmap Timeline (125-150 hours)
    section Phase 1: Foundations (40h)
        Computing Basics: 4h
        Python Fundamentals: 20h
        Environment Setup: 3h
        Physics Foundation: 8h
        Math Fundamentals: 5h
    section Phase 2: Core Concepts (30h)
        Control Theory: 6h
        Feedback Systems: 5h
        SMC Theory: 8h
        Optimization: 6h
        DIP System: 5h
    section Phase 3: Hands-On (25h)
        Running Simulations: 8h
        Analyzing Results: 6h
        Comparing Controllers: 5h
        Tuning Parameters: 4h
        Troubleshooting: 2h
```

:::
```

---

## Summary: Diagram Placement Statistics

**Total Diagrams**: 22 (without Phase 5.2 research path)

| Phase | Count | Primary Location | CSS Color | Agent |
|-------|-------|------------------|-----------|-------|
| Phase 1 | 6 | phase-1-foundations.md | Blue #2563eb | Agent 1 |
| Phase 2 | 7 | phase-2-core-concepts.md | Green #10b981 | Agent 2 |
| Phase 3 | 4 | phase-3-hands-on.md | Orange #f59e0b | Agent 1 |
| Phase 4 | 3 | phase-4-advancing-skills.md | Purple #8b5cf6 | Agent 2 |
| Phase 5 | 1 | phase-5-mastery.md | Red #ef4444 | Either |
| Progress Viz | 4 | beginner-roadmap.md + phases | Multi-color | Both |
| **TOTAL** | **25** | **All 5 phases** | **5 colors** | **Both** |

---

**End of Placement Guide**
