# Visual Assets Catalog for Beautiful.ai Phase 1 Presentations
**Purpose:** Reference guide for all visual elements needed in Phase 1 slide decks (E001-E005)

**Source:** Extracted from podcast cheatsheet PDFs and episode markdown descriptions

---

## Asset Organization

```
visual_assets/
├── VISUAL_ASSETS_CATALOG.md (this file)
├── descriptions/            (text descriptions for Beautiful.ai prompts)
│   ├── E001_diagrams.md
│   ├── E002_diagrams.md
│   ├── E003_diagrams.md
│   ├── E004_diagrams.md
│   └── E005_diagrams.md
└── source_references/       (references to LaTeX PDF sources)
    ├── phase1_foundational_pdfs.md
    └── extraction_notes.md
```

---

## E001: Project Overview - Visual Assets

### ASSET 1.1: Double Inverted Pendulum System Diagram
**Slide:** E001 Slide 2
**Type:** Technical schematic
**Description:**
- Cart on horizontal track (blue rectangle)
- Pendulum 1 (bottom link, green line from cart to joint)
- Pendulum 2 (top link, orange line from joint to tip)
- Angle labels: θ₁ (pendulum 1 from vertical), θ₂ (pendulum 2 from vertical)
- Force arrow F (horizontal, on cart, orange)
- Coordinate system (x-axis horizontal, vertical reference line)
**Beautiful.ai Prompt:** "System diagram with cart, two connected pendulums, angle labels, force arrow"
**Source:** E001 PDF page 1, Figure: DIP System Schematic

### ASSET 1.2: SpaceX Rocket Landing Comparison
**Slide:** E001 Slide 2, E002 Slide 1
**Type:** Real-world photo/icon
**Description:** SpaceX Falcon 9 booster in vertical landing phase (stock photo or simplified icon)
**Beautiful.ai Prompt:** "Rocket in vertical position with engines firing downward, stability control"
**Source:** Public domain rocket landing image or simplified vector icon

### ASSET 1.3: Controller Hierarchy Pyramid
**Slide:** E001 Slide 4
**Type:** Organizational diagram
**Description:**
- 4-tier pyramid showing sophistication levels
- Tier 1 (bottom, largest): Classical SMC (blue box)
- Tier 2: Super-Twisting (green box, medium)
- Tier 3: Adaptive + Hybrid + Conditional (3 orange boxes)
- Tier 4 (top): Swing-Up + MPC (2 purple boxes)
- Arrows labeled "increasing sophistication"
- Performance metric callouts (e.g., "+21.4%" for Hybrid)
**Beautiful.ai Prompt:** "Pyramid diagram with 4 tiers, color-coded boxes, performance labels"
**Source:** E001 PDF page 2, derived from text descriptions

### ASSET 1.4: Model Quality Settings Comparison
**Slide:** E001 Slide 5
**Type:** Comparison table/icons
**Description:**
- 3 columns: Simplified, Full, Low-Rank
- Icons: Speedometer (fast), Trophy (accurate), Lightning (balanced)
- Star ratings: Accuracy (★★☆, ★★★★★, ★★★☆)
- Speed ratings: ⚡⚡⚡⚡⚡, ⚡, ⚡⚡⚡⚡
**Beautiful.ai Prompt:** "Three-column comparison with icons and star ratings"
**Source:** E001 PDF page 2, model comparison section

### ASSET 1.5: PSO Swarm Visualization
**Slide:** E001 Slide 6
**Type:** Animated diagram
**Description:**
- 30-50 blue dots (particles) in 3D search space
- Contour map background showing "cost function landscape" (hills/valleys)
- Arrows from each particle showing movement direction
- Golden dot showing "global best" location
- Convergence arrows showing particles clustering
**Beautiful.ai Prompt:** "Particle swarm in 3D cost landscape with convergence arrows"
**Source:** E001 PDF page 3, PSO visualization concept

### ASSET 1.6: Workflow Timeline
**Slide:** E001 Slide 7
**Type:** Process timeline
**Description:**
- 5 connected boxes (left to right)
- Phase 1 (blue): "Getting Lab Ready, 15 min"
- Phase 2 (green): "First Experiments, 30 min"
- Phase 3 (orange): "Intelligent Tuning, 2-4 hrs"
- Phase 4 (purple): "Serious Benchmarking, 1-2 days"
- Phase 5 (red): "Research & Publication, weeks-months"
- Arrows connecting phases
- Cumulative timeline at bottom: 15m → 4h → 2d → weeks → publication
**Beautiful.ai Prompt:** "5-phase timeline with duration estimates and cumulative progress bar"
**Source:** E001 PDF page 4, workflow section

---

## E001 EXTENDED: Additional Visual Assets (Slides 8-11)

*These assets are used exclusively in the Extended version (E001_project_overview_extended_slides.md)*

### ASSET 1.7: Analysis Workflow Diagram
**Slide:** E001 Extended Slide 8
**Type:** Four-quadrant dashboard / flow diagram
**Description:**
- 2x2 grid layout with 4 capability panels, each in a distinct card
- Panel 1 (top-left, blue): Performance Metrics
  - Speedometer or gauge icon
  - Labels: "Settling time", "Overshoot", "Steady-state error", "Lyapunov monitoring"
- Panel 2 (top-right, green): Real-Time Visualization
  - Monitor/screen icon
  - Small animation frame showing pendulum
  - Labels: "State trajectories", "Control effort plots", "Phase portraits"
- Panel 3 (bottom-left, orange): Statistical Validation
  - Scatter plot dots with confidence intervals
  - Labels: "Monte Carlo (1000+ sims)", "Bootstrap CI", "t-test / ANOVA"
- Panel 4 (bottom-right, purple): Publication Output
  - Journal paper icon or matplotlib-style chart
  - Labels: "14 figures", "Comparative plots", "Research paper v2.1"
- Center title: "Analysis & Visualization Toolkit"
- Color coding: Blue (metrics), Green (visualization), Orange (stats), Purple (publication)
**Beautiful.ai Prompt:** "Four-quadrant dashboard with icons for metrics, visualization, statistics, and publication output"
**Source:** E001 podcast source lines 133-148, analysis section

### ASSET 1.8: Testing Pyramid
**Slide:** E001 Extended Slide 9
**Type:** Pyramid diagram
**Description:**
- Triangle divided into 3 horizontal tiers
- Bottom tier (largest, blue): "Unit Tests" - tests individual functions, fastest
  - Label: "180+ tests, 85% overall coverage target"
- Middle tier (medium, green): "Integration Tests" - tests component interactions
  - Label: "50+ tests, 95% critical coverage"
- Top tier (smallest, orange): "System / Benchmark Tests" - end-to-end performance
  - Label: "20+ tests, 100% safety-critical"
- Right side annotation: "Total: 250+ tests"
- Left side annotation: "~90% overall coverage"
- At peak: "Submission-ready research outputs"
- Arrow on right showing "increasing complexity / fewer tests" from bottom to top
**Beautiful.ai Prompt:** "Testing pyramid with three tiers showing unit, integration, and system tests with coverage percentages"
**Source:** E001 podcast source lines 245-258, quality section

### ASSET 1.9: Technology Stack Layers
**Slide:** E001 Extended Slide 10
**Type:** Layered architecture stack (horizontal bands)
**Description:**
- 4 stacked horizontal bands (widest at bottom, narrowing toward top)
- Band 1 (bottom, widest, blue): "Core Scientific Computing"
  - NumPy logo/icon, SciPy logo/icon, Matplotlib logo/icon
  - Subtitle: "Array operations, ODE integration, visualization"
- Band 2 (medium-wide, green): "Optimization Toolkit"
  - PySwarms icon (particle swarm), Optuna icon (funnel/curve)
  - Subtitle: "PSO and Bayesian optimization"
- Band 3 (medium, orange): "Quality Assurance"
  - pytest icon (test tube), Hypothesis icon (question mark), Coverage icon (percentage)
  - Subtitle: "250+ tests, property testing, coverage measurement"
- Band 4 (top, narrowest, purple): "Configuration and Interface"
  - Pydantic icon (shield/validation), PyYAML icon (file), Streamlit icon (dashboard)
  - Subtitle: "Type-safe config, file parsing, interactive UI"
- Right side: Brief role description per band
- Tagline at bottom: "Battle-tested scientific Python ecosystem"
**Beautiful.ai Prompt:** "4-layer technology stack diagram with logos/icons and role descriptions per layer"
**Source:** E001 podcast source lines 209-224, technology section

### ASSET 1.10: Use Case Workflow Comparison
**Slide:** E001 Extended Slide 11
**Type:** Three-column persona comparison
**Description:**
- 3 side-by-side vertical panels (equal width)
- Panel 1 (blue): Student / Learner
  - Top: Graduation cap icon, "Student Path"
  - Learning progression (4 numbered steps, arrows between):
    1. Classical SMC (basics)
    2. Super-Twisting (smooth control)
    3. Adaptive SMC (self-tuning)
    4. Research benchmarks
  - Bottom: "Hands-on Projects" callout
- Panel 2 (green): Researcher / Academic
  - Top: Microscope icon, "Researcher Path"
  - Research workflow (4 numbered steps):
    1. Implement controller variant
    2. PSO optimization (2-4 hrs)
    3. Monte Carlo validation (1000+ sims)
    4. Publication-ready figures
  - Bottom: "Reproducible outputs" callout
- Panel 3 (orange): Engineer / Practitioner
  - Top: Hard hat or wrench icon, "Engineer Path"
  - Deployment pipeline (4 numbered steps):
    1. PSO optimization (simplified model)
    2. Validate (full nonlinear model)
    3. HIL testing (pre-hardware)
    4. Safety validation + deployment
  - Bottom: "Production-ready" callout
- Bottom tagline: "Three audiences, one framework"
**Beautiful.ai Prompt:** "Three-column persona cards with numbered workflow steps, icons, and callout labels"
**Source:** E001 podcast source lines 259-294, use cases section

---

## E002: Control Theory Fundamentals - Visual Assets

### ASSET 2.1: State Vector Dashboard
**Slide:** E002 Slide 2
**Type:** Infographic
**Description:**
- 6 dashboard gauges/indicators arranged in grid
- Cart position (meter, horizontal position)
- Cart velocity (speedometer, m/s)
- θ₁ angle (protractor, radians)
- θ₁' angular velocity (tachometer, rad/s)
- θ₂ angle (protractor)
- θ₂' angular velocity (tachometer)
- Each with current value display and units
**Beautiful.ai Prompt:** "Dashboard with 6 gauges showing state variables"
**Source:** E002 PDF page 1, state-space section

### ASSET 2.2: Lyapunov Marble-in-Bowl 3D Plot
**Slide:** E002 Slide 3
**Type:** 3D visualization
**Description:**
- Bowl-shaped surface (blue gradient, darker at bottom)
- Marble (orange sphere) at various positions
- Trajectory spiral showing marble rolling inward
- Gravity vector (downward arrow)
- Energy contour lines on bowl surface
- Labels: "Equilibrium (V=0)" at bottom, "Higher energy" at rim
**Beautiful.ai Prompt:** "3D bowl surface with marble trajectory spiraling to bottom center"
**Source:** E002 PDF page 2, Lyapunov stability visualization

### ASSET 2.3: Sliding Surface Guard Rail Mountain
**Slide:** E002 Slide 4
**Type:** Conceptual diagram
**Description:**
- Mountain slope (gray) in profile view
- Guardrail path (golden line) from top to cabin at bottom
- Hiker icon at 3 positions:
  1. Off-path (red marker, "Reaching phase")
  2. Approaching path (yellow marker, arrow toward path)
  3. On path sliding down (green marker, "Sliding phase")
- Wind gust icons (disturbances)
- Cabin at bottom (equilibrium/target)
**Beautiful.ai Prompt:** "Mountain profile with guardrail path, hiker positions, wind icons"
**Source:** E002 PDF page 3, SMC analogy illustration

### ASSET 2.4: Chattering Waveform Comparison
**Slide:** E002 Slide 6
**Type:** Side-by-side waveforms
**Description:**
- Left: Classical SMC control signal (jagged, rapid oscillations)
  - High-frequency switching visible
  - Red color indicating problem
  - Label: "Harsh buzzing sound"
- Right: Continuous approximation (smooth curve)
  - Green color indicating solution
  - Label: "Smooth, continuous"
- Time axis (0-5 seconds)
- Amplitude axis (-50 to +50 N)
**Beautiful.ai Prompt:** "Two waveform plots side-by-side, left jagged, right smooth"
**Source:** E002 PDF page 4, chattering section

### ASSET 2.5: Super-Twisting Phase Plane
**Slide:** E002 Slide 7
**Type:** Phase plane trajectory plot
**Description:**
- 2D plot: sliding surface s (horizontal) vs. ṡ (vertical)
- Classical SMC trajectory (red, oscillating approach to origin)
- Super-Twisting trajectory (green, smooth spiral to origin)
- Origin (0,0) marked with star (equilibrium)
- Grid background
- Legend distinguishing Classical vs. STA
**Beautiful.ai Prompt:** "Phase plane with two trajectories converging to origin, one jagged, one smooth"
**Source:** E002 PDF page 4, STA visualization

### ASSET 2.6: Adaptive Gain Evolution
**Slide:** E002 Slide 8
**Type:** Time-series plot
**Description:**
- Plot showing gain value over time (0-10 seconds)
- Gain starts low, increases when error is large, decreases when error is small
- Dead zone regions shaded (gray)
- Annotations: "Large error → increase", "Small error → decrease"
**Beautiful.ai Prompt:** "Line plot showing adaptive gain changing over time with annotations"
**Source:** E002 PDF page 5, adaptive SMC section

### ASSET 2.7: Matched vs. Unmatched Uncertainty Paths
**Slide:** E002 Slide 9
**Type:** Split pathway diagram
**Description:**
- Left path (green, thick): Matched uncertainty entering through control channel
  - Equation block: ẋ = f(x) + (B₀ + ΔB)u + Bd
  - Large green checkmark labeled "SMC cancels completely"
- Right path (red, dashed): Unmatched uncertainty entering outside control channel
  - Equation block: ẋ = f(x) + d_unmatched + Bu
  - Orange warning icon labeled "SMC attenuates (not cancels)"
- Center: System block diagram showing controller, plant, disturbance entry points
- Bottom: 3x3 performance table (Classical/STA/Adaptive SMC vs. Nominal/Perturbed/Degradation)
**Beautiful.ai Prompt:** "Split pathway diagram with green checkmark for matched uncertainty and orange warning for unmatched"
**Source:** E002 episode markdown, robustness properties section

### ASSET 2.8: Finite-Time vs. Exponential Convergence Timelines
**Slide:** E002 Slide 10
**Type:** Parallel timeline comparison
**Description:**
- Top timeline (red): Exponential convergence curve Ce^(-αt), asymptotic, never reaches zero
  - Dotted epsilon ball line showing "only gets within tolerance"
- Bottom timeline (green): SMC finite-time curve, linear drop then flat zero
  - Vertical line at T_f: "Guaranteed zero at finite time"
  - Formula boxes: Classical T_f = |s(0)|/η, STA: T_f ≤ 2|s(0)|^(1/2)/K₂
- Right panel: Numerical example (s(0)=0.5, η=2.0, T_f=0.25 seconds)
**Beautiful.ai Prompt:** "Two parallel timelines comparing exponential (red, never zero) vs. SMC finite-time (green, reaches zero)"
**Source:** E002 episode markdown, convergence time analysis section

### ASSET 2.9: Pitfalls and Implementation Tips Cards
**Slide:** E002 Slide 11
**Type:** Card grid (3+2 layout)
**Description:**
- Top row: 3 red pitfall cards
  - Card 1: Warning icon + "Derivative Explosion" + code snippet
  - Card 2: Warning icon + "Gain Over-Tuning" + config comparison
  - Card 3: Warning icon + "Ignoring Saturation" + consequence note
- Bottom row: 2 wider green tip cards
  - Card 1: Lightbulb icon + "Use Simplified Model First" + command
  - Card 2: Lightbulb icon + "Visualize Sliding Surface" + plot description
- Header: "Learn from These Mistakes Before You Make Them"
**Beautiful.ai Prompt:** "3+2 card grid with red pitfall cards (warning icons) and green tip cards (lightbulb icons)"
**Source:** E002 episode markdown, practical pitfalls section

---

## E003: Plant Models and Dynamics - Visual Assets

### ASSET 3.1: Lagrangian Energy Surfaces
**Slide:** E003 Slide 2
**Type:** 3D energy plot
**Description:**
- Kinetic energy surface T (blue, increasing with velocity)
- Potential energy surface V (red, increasing with height)
- Lagrangian L = T - V (purple, combined surface)
- Axes: generalized coordinates q, velocities q̇, energy
**Beautiful.ai Prompt:** "3D surface plots showing kinetic, potential, and Lagrangian energy"
**Source:** E003 PDF page 1, Lagrangian mechanics

### ASSET 3.2: Small Angle Approximation Graph
**Slide:** E003 Slide 3
**Type:** Function comparison plot
**Description:**
- X-axis: angle θ (degrees, -10° to +10°)
- Y-axis: function value
- Two curves:
  - sin(θ) actual (blue curve)
  - θ linear approximation (red straight line)
- Shaded region showing valid approximation range (±5°)
- Divergence beyond ±10° visible
**Beautiful.ai Prompt:** "Graph comparing sin(θ) curve to linear θ approximation, highlighting valid range"
**Source:** E003 PDF page 2, simplified model section

### ASSET 3.3: Complete Force Diagram (Full Nonlinear)
**Slide:** E003 Slide 4
**Type:** Free-body diagram
**Description:**
- Cart with mass M, force F (horizontal)
- Pendulum 1 with mass m₁, length L₁, angle θ₁
  - Gravity m₁g (down)
  - Joint reaction forces Fx₁, Fy₁
  - Coriolis force (curved arrow)
  - Centrifugal force (outward arrow)
- Pendulum 2 similar forces labeled
- Coupling arrows showing interaction between pendulums
- Color-coded: Gravity (green), reactions (blue), inertial (red)
**Beautiful.ai Prompt:** "Detailed force diagram with all forces labeled and color-coded"
**Source:** E003 PDF page 3, full dynamics section

### ASSET 3.4: Mass Matrix Structure
**Slide:** E003 Slide 6
**Type:** Matrix visualization
**Description:**
- 3×3 matrix M(θ) with elements labeled
- Diagonal elements highlighted (inertia terms)
- Off-diagonal elements (coupling terms)
- Angle-dependence indicated (θ₁, θ₂ in elements)
- Color gradient showing magnitude (darker = larger influence)
**Beautiful.ai Prompt:** "3x3 matrix with labeled elements and color gradient"
**Source:** E003 PDF page 3, mass matrix section

### ASSET 3.5: Model Speed Comparison Bar Chart
**Slide:** E003 Slide 7
**Type:** Horizontal bar chart
**Description:**
- 3 bars showing relative speed:
  - Simplified: 100x (green, longest bar)
  - Low-Rank: 10x (orange, medium bar)
  - Full Nonlinear: 1x (blue, baseline bar)
- Annotations with actual times (e.g., "1 second", "10 seconds", "100 seconds")
**Beautiful.ai Prompt:** "Horizontal bar chart comparing model computation speeds"
**Source:** E003 PDF page 4, performance comparison

### ASSET 3.6: Singularities and Numerical Stability Cards
**Slide:** E003 Slide 8
**Type:** Warning diagram with strategy cards
**Description:**
- Top: Physical analogy - arm at full extension (locked), DIP pendulums at critical angle
- Condition number health gauge: 1-100 (green), 100k-1M (yellow), >1M (red)
- Three horizontal strategy cards:
  - Card 1 (green): Shield icon + "Condition Number Monitoring" + `cond = np.linalg.cond(M)`
  - Card 2 (yellow): Plus icon + "Regularized Inversion" + `M_reg = M + epsilon * eye(3)`
  - Card 3 (blue): Pinv icon + "Pseudoinverse" + `np.linalg.pinv(M, rcond=1e-6)`
- Bottom: Note "Normal operation stays in green zone"
**Beautiful.ai Prompt:** "Shield warning diagram with condition number gauge and three strategy cards with code snippets"
**Source:** E003 episode markdown, singularities section

### ASSET 3.7: Plant Model Pitfalls and Validation Cards
**Slide:** E003 Slide 9
**Type:** Card grid (3+2 layout, matching E002 style)
**Description:**
- Top row: 3 red pitfall cards
  - Card 1: Warning icon + "Wrong Angle Convention" + sign error example
  - Card 2: Warning icon + "Inconsistent Units" + rad vs. degree trap
  - Card 3: Warning icon + "Ignoring Parameter Bounds" + negative mass example
- Bottom row: 2 wider green tip cards
  - Card 1: Lightbulb icon + "Validate with Energy Conservation" + test code snippet
  - Card 2: Lightbulb icon + "Cross-Check Models" + comparison workflow
- Header: "Common Mistakes and How to Catch Them"
**Beautiful.ai Prompt:** "3+2 card grid matching E002 pitfalls style, red warning cards with code examples, green tip cards"
**Source:** E003 episode markdown, practical pitfalls section

### ASSET 3.8: E003 Key Takeaways and E004 Preview
**Slide:** E003 Slide 10
**Type:** Summary checklist with preview panel
**Description:**
- Top (70%): 5 key learning checkpoints with distinct icons
  - Color-coded: blue for models, orange for dynamics, green for validation
  - Brief descriptions under each checkpoint
- Bottom (30%): E004 preview panel
  - PSO particle swarm icon
  - "From physics to intelligent tuning" transition text
- Background: Gradient from physics blue to optimization orange
**Beautiful.ai Prompt:** "5-point checklist with icons and color-coded topics, E004 preview panel with gradient background"
**Source:** E003 episode markdown, key takeaways section

---

## E004: PSO Optimization - Visual Assets

### ASSET 4.1: Bird Flock Seeking Food
**Slide:** E004 Slide 2
**Type:** Nature illustration
**Description:**
- Flock of birds (10-15 silhouettes) moving together
- Food source (target) at one location
- Motion arrows showing birds converging
- Individual birds exploring different areas
- Annotations: "Personal best", "Global best"
**Beautiful.ai Prompt:** "Bird flock illustration with movement arrows converging to target"
**Source:** E004 PDF page 1, PSO metaphor

### ASSET 4.2: Particle Velocity/Position Update Diagram
**Slide:** E004 Slide 3
**Type:** Vector diagram
**Description:**
- Current particle position (blue dot)
- Current velocity vector (black arrow)
- Personal best direction (green arrow)
- Global best direction (gold arrow)
- New velocity (purple arrow, weighted combination)
- New position (blue dot moved)
- Equations overlaid: v_{new} = w·v + c₁·(p_best-x) + c₂·(g_best-x)
**Beautiful.ai Prompt:** "Vector diagram showing particle movement with velocity components"
**Source:** E004 PDF page 2, PSO mechanics

### ASSET 4.3: Multi-Objective Trade-Off Triangle
**Slide:** E004 Slide 4
**Type:** Trade-off diagram
**Description:**
- Triangle with 3 vertices:
  - Top: "Fast convergence" (minimize state error)
  - Bottom-left: "Low energy" (minimize control effort)
  - Bottom-right: "Smooth control" (minimize chattering)
- Center point: "Optimal balance" (PSO solution)
- Arrows showing cannot maximize all three simultaneously
**Beautiful.ai Prompt:** "Triangle diagram with three competing objectives and optimal balance point"
**Source:** E004 PDF page 2, multi-objective section

### ASSET 4.4: PSO Convergence Curve
**Slide:** E004 Slide 6
**Type:** Line plot
**Description:**
- X-axis: Iteration number (0-50)
- Y-axis: Best cost (log scale, 1-1000)
- Cost curve showing typical convergence:
  - Iteration 0: Cost ~500 (random initialization)
  - Iterations 1-20: Rapid drop to ~20 (exploration)
  - Iterations 20-40: Gradual decrease to ~5 (exploitation)
  - Iterations 40-50: Plateau at ~2 (convergence)
- Phases labeled: Exploration, Exploitation, Convergence
**Beautiful.ai Prompt:** "Line plot showing cost decreasing over iterations with phases labeled"
**Source:** E004 PDF page 3, convergence behavior

### ASSET 4.5: Before/After Performance Table
**Slide:** E004 Slide 7
**Type:** Comparison table
**Description:**
- Rows: 7 controllers (Classical, STA, Adaptive, Hybrid, Conditional, Swing-Up, MPC)
- Columns: Manual Gains (cost), PSO Gains (cost), Improvement (%)
- Color-coded: Green for improvements >20%, Yellow for 5-20%, White for <5%
- Hybrid row highlighted (21.4% improvement)
**Beautiful.ai Prompt:** "Performance comparison table with color-coded improvement percentages"
**Source:** E004 PDF page 4, results section

### ASSET 4.6: Standard PSO vs. Robust PSO Comparison
**Slide:** E004 Slide 8
**Type:** Two-column comparison with performance chart
**Description:**
- Left column (red): "Standard PSO" - single nominal scenario diagram
  - One pendulum configuration, good nominal score, fails on variations
- Right column (blue): "Robust PSO" - multiple scenario diagrams
  - Nominal + light/heavy mass + disturbances diagrams
  - Good nominal AND good across all variations
- Bottom: Line chart comparing performance over variation scenarios
  - X-axis: mass +0%, +10%, +20%, disturbance
  - Standard PSO line (red): crashes at +20% mass
  - Robust PSO line (blue): degrades gracefully
**Beautiful.ai Prompt:** "Two-column comparison (standard=red fragile vs. robust=blue resilient) with degradation curve chart"
**Source:** E004 episode markdown, robust PSO section

### ASSET 4.7: Optimizer Comparison Table and Decision Flowchart
**Slide:** E004 Slide 9
**Type:** Table + flowchart split
**Description:**
- Top (50%): 4-column comparison table
  - Columns: PSO (highlighted blue), Grid Search, Gradient-Based, Bayesian Optimization
  - Rows: No gradient needed, Global search, Speed, When to use
- Bottom (50%): Decision flowchart with diamond nodes
  - "< 20 parameters?" → Yes → PSO | No → CMA-ES
  - "Need <0.1% precision?" → Yes → Gradient | No → PSO
  - "Very few evaluations?" → Yes → Bayesian | No → PSO
**Beautiful.ai Prompt:** "Optimizer comparison table (PSO highlighted blue) with decision flowchart below"
**Source:** E004 episode markdown, algorithm comparison section

### ASSET 4.8: Human vs. Algorithm Race Results
**Slide:** E004 Slide 10
**Type:** Race comparison infographic
**Description:**
- Left (amber): Three engineer cards
  - Engineer A: clock icon 28 min, score badge J=8.1
  - Engineer B: clock icon 30 min, score badge J=8.5
  - Engineer C: clock icon 30 min, score badge J=9.2
- Right (blue): PSO card with lightning bolt, 5 minutes, score J=7.89 (WINNER)
- Center: Comparison line with winner crown on PSO side
- Bottom: Lesson box "Experience helps. But PSO is consistent."
**Beautiful.ai Prompt:** "Race comparison with three engineer cards (amber) vs. PSO card (blue), winner crown, time and score badges"
**Source:** E004 episode markdown, human vs. algorithm experiment

### ASSET 4.9: 80/20 Rule Pie Chart and Troubleshooting Grid
**Slide:** E004 Slide 11
**Type:** Pie chart + problem-solution card grid
**Description:**
- Top (50%): Pie chart with two slices
  - Large slice (80%, blue): "Cost function and bounds design"
  - Small slice (20%, gray): "PSO hyperparameters (w, c1, c2)"
  - Caption: "Performance comes from what you optimize, not optimizer tuning"
- Bottom (50%): 4 red problem cards with green solution arrows
  - "PSO stalls early", "Many unstable particles", "Premature convergence", "Too slow"
**Beautiful.ai Prompt:** "80/20 pie chart above, four red problem cards with green solution arrows below"
**Source:** E004 episode markdown, practical wisdom and troubleshooting section

### ASSET 4.10: E004 Key Takeaways and E005 Preview
**Slide:** E004 Slide 12
**Type:** Summary checklist with preview panel
**Description:**
- Top (60%): 6 learning points with checkmark icons
  - Brief descriptions under each point
- Bottom (40%): E005 preview panel
  - Three-tier architecture teaser diagram (small)
  - "33x speedup" badge/callout
  - SpaceX closing connection image
- Background: Gradient from orange (optimization) to blue (simulation)
**Beautiful.ai Prompt:** "6-point checklist, E005 preview with three-tier teaser and 33x speedup badge, orange-to-blue gradient"
**Source:** E004 episode markdown, key takeaways section

---

## E005: Simulation Engine - Visual Assets

### ASSET 5.1: Three-Tier Engine Diagram
**Slide:** E005 Slide 1
**Type:** Architecture diagram
**Description:**
- 3 connected tiers with gear icons:
  - Tier 1 (bottom): "Simulation Runner" (blue, single-threaded icon)
  - Tier 2 (middle): "Vectorized Simulator" (green, parallel arrows icon)
  - Tier 3 (top): "Simulation Context" (purple, config file icon)
- Data flow arrows between tiers
- Speed callout: "1500 sims in 2-4 hours"
**Beautiful.ai Prompt:** "Three-tier architecture with gears and data flow arrows"
**Source:** E005 PDF page 1, architecture overview

### ASSET 5.2: Integration Method Comparison
**Slide:** E005 Slide 3
**Type:** Accuracy vs. speed scatter plot
**Description:**
- X-axis: Speed (fast → slow)
- Y-axis: Accuracy (low → high)
- 3 points:
  - Euler (top-left: fast, low accuracy)
  - RK4 (center: moderate speed, high accuracy)
  - RK45 (top-right: adaptive, high accuracy)
- Point sizes indicating computational cost
**Beautiful.ai Prompt:** "Scatter plot comparing integration methods on speed vs. accuracy axes"
**Source:** E005 PDF page 2, integration section

### ASSET 5.3: Sequential vs. Vectorized Timeline
**Slide:** E005 Slide 4
**Type:** Timeline comparison
**Description:**
- Top: Sequential execution (100 sims, one after another)
  - 100 small boxes in a long line
  - Duration: 1000 seconds
- Bottom: Vectorized execution (100 sims simultaneously)
  - 100 small boxes stacked vertically
  - Duration: 30 seconds
- Arrow showing "33x faster"
**Beautiful.ai Prompt:** "Two timelines comparing sequential vs. parallel execution with speedup arrow"
**Source:** E005 PDF page 3, vectorization section

### ASSET 5.4: NumPy Broadcasting Visualization
**Slide:** E005 Slide 5
**Type:** Array dimension diagram
**Description:**
- Single state array: [6] (1D, blue)
- Batch state array: [100, 6] (2D grid, green)
- Operation applied element-wise shown with arrows
- Annotations: "Same operation to all 100 rows simultaneously"
**Beautiful.ai Prompt:** "Array dimension visualization showing 1D to 2D broadcasting"
**Source:** E005 PDF page 3, NumPy section

### ASSET 5.5: Performance Benchmark Bar Chart
**Slide:** E005 Slide 7
**Type:** Horizontal bar chart
**Description:**
- 4 bars showing execution times:
  - Single sim: 10 seconds
  - Vectorized 100 sims: 30 seconds
  - Vectorized 1000 sims: 300 seconds (5 min)
  - PSO 1500 sims: 7200 seconds (2 hours)
- Color gradient: Green (fast) to red (slow)
- Speedup annotations
**Beautiful.ai Prompt:** "Bar chart comparing execution times for different simulation scales"
**Source:** E005 PDF page 4, performance section

### ASSET 5.6: Phase 1 Journey Timeline
**Slide:** E005 Slide 10
**Type:** Episode progression visual
**Description:**
- 5 connected circles (E001 → E002 → E003 → E004 → E005)
- Icons for each episode:
  - E001: Project overview (building blocks)
  - E002: Control theory (equations)
  - E003: Physics (pendulum)
  - E004: Optimization (swarm)
  - E005: Computation (gears)
- Arc labeled "From overview to mastery"
- Color gradient: Blue → purple progression
**Beautiful.ai Prompt:** "Timeline with 5 episode icons connected by arc showing progression"
**Source:** E005 PDF page 5, summary section

### ASSET 5.7: Performance Benchmark Bar Charts
**Slide:** E005 Slide 8
**Type:** Dual bar chart comparison
**Description:**
- Top left: Single simulation bars (3 bars: Pure Python slow, Vectorized medium, Vectorized+Numba fast)
- Top right: PSO optimization bars (3 bars: Slow 4.2 hrs, Vectorized 12 min, Vectorized+Numba 5 min)
- Bottom: Use case comparison table (Single sim / PSO run / MT-5 benchmark)
- Color gradient: red (slow), orange (medium), green (fast)
- Time values labeled on each bar
**Beautiful.ai Prompt:** "Dual bar charts comparing Python vs. vectorized vs. Numba speeds, color gradient red-to-green"
**Source:** E005 episode markdown, performance benchmarks section

### ASSET 5.8: Reproducibility Demonstration Diagram
**Slide:** E005 Slide 9
**Type:** Researcher comparison diagram
**Description:**
- Top (reproducible): Two researcher icons at computers, same code + seed=42, identical matching graphs output, green checkmark
- Bottom (non-reproducible): Two researcher icons, same code but different seeds, different graphs, red X mark
- Side panel: "What Can Break Reproducibility" list (unseeded RNG, floating point non-determinism, different hardware)
- Green checkmark for reproducible case, red X for non-reproducible
**Beautiful.ai Prompt:** "Two scenarios: researchers with same seed producing identical graphs (green checkmark) vs. different seeds (red X)"
**Source:** E005 episode markdown, reproducibility section

### ASSET 5.9: Memory Management Visualization
**Slide:** E005 Slide 10
**Type:** Memory usage diagram with strategy cards
**Description:**
- Top: Memory calculation chain: 1,000 sims x 10,000 timesteps x 6 states x 8 bytes = 480 MB
- Bar showing RAM filling up, red danger zone when exceeding RAM
- Two strategy cards:
  - Pre-allocation card: "Reserve memory first, fill in place" (fast indicator)
  - Streaming to disk card: "Write batch results to disk, reload for analysis"
- Bottom table: Small (<100 sims) = RAM, Medium (100-1,000) = Pre-allocate, Large (>1,000) = Stream
**Beautiful.ai Prompt:** "Memory calculation chain, RAM bar with red danger zone, two strategy cards, guidance table"
**Source:** E005 episode markdown, memory management section

### ASSET 5.10: SpaceX vs. DIP Parallel Comparison
**Slide:** E005 Slide 11
**Type:** Side-by-side comparison infographic
**Description:**
- Left (45%, dark blue/silver): SpaceX Falcon 9 diagram with control force vectors
  - Computational requirement: thousands of scenarios
  - Real-time gain update needs
  - Label: "Same engineering problem, larger scale"
- Right (45%, orange/green): DIP cart-pendulum diagram
  - Performance: 1,500 sims in 5 minutes
  - Optimization: PSO on simplified model
  - Label: "Same principles, educational scale"
- Bottom: Key principle "Vectorization and JIT compilation scale from student projects to aerospace"
- Bridge element (gold) connecting both sides
**Beautiful.ai Prompt:** "Parallel comparison: Falcon 9 (dark blue) left vs. DIP pendulum (orange) right, gold bridge connection"
**Source:** E005 episode markdown, SpaceX connection section

### ASSET 5.11: E005 Takeaways and Phase 1 Journey Timeline
**Slide:** E005 Slide 12
**Type:** Summary checklist with journey timeline
**Description:**
- Top (40%): 6 E005 learning points with checkmark icons
- Middle (35%): Horizontal timeline with 5 milestones (E001-E005)
  - Descriptors: Overview, Theory, Physics, Optimization, Computation
  - Arc above: "From project overview to computational mastery"
- Bottom (25%): Phase 2 preview panel
- Gradient from beginner blue to advanced gold
**Beautiful.ai Prompt:** "6-point checklist, horizontal 5-milestone timeline (E001-E005), Phase 2 preview, blue-to-gold gradient"
**Source:** E005 episode markdown, Phase 1 completion section

---

## Asset Usage Guidelines

### For Beautiful.ai Users:
1. Use text descriptions as prompts for Beautiful.ai's smart template system
2. Adapt colors to match Beautiful.ai's color palette
3. Add animations where suggested (particle movement, convergence, etc.)
4. Use Beautiful.ai's icon library for symbols (speedometer, trophy, etc.)

### For Manual Creation:
1. Descriptions provide enough detail to recreate in tools like:
   - PowerPoint/Keynote (manual diagramming)
   - Draw.io/Lucidchart (technical diagrams)
   - matplotlib/seaborn (data visualizations)
   - TikZ (LaTeX users)

### Color Palette Consistency:
- **Classical SMC / Foundation:** Blue (#2196F3)
- **Super-Twisting / Smooth:** Green (#4CAF50)
- **Adaptive / Intelligent:** Orange (#FF9800)
- **Advanced / Experimental:** Purple (#9C27B0)
- **Problems / Warnings:** Red (#F44336)
- **Solutions / Success:** Green (#4CAF50)

### Icon Recommendations:
- **Speed:** Speedometer, lightning bolt, rocket
- **Accuracy:** Target, trophy, checkmark
- **Balance:** Scales, triangle, slider
- **Optimization:** Swarm, flock, particles
- **Computation:** Gears, CPU, assembly line
- **Control:** Steering wheel, joystick, dial

---

## Source References

**LaTeX PDF Cheatsheets (Phase 1 Foundational):**
- E001_project_overview_and_introduction.pdf (5 pages, 400 KB)
- E002_control_theory_fundamentals.pdf (6 pages, 420 KB)
- E003_plant_models_and_dynamics.pdf (5 pages, 390 KB)
- E004_pso_optimization_fundamentals.pdf (7 pages, 480 KB)
- E005_simulation_engine_architecture.pdf (6 pages, 450 KB)

**Location:** `D:/Projects/main/academic/paper/presentations/podcasts/cheatsheets/phase1_foundational/`

**Extraction Method:** Text descriptions derived from PDF visual elements and markdown source episodes

---

**Total Visual Assets Cataloged:** 45 assets across 5 episodes
- 6 assets for E001 Standard version (Assets 1.1-1.6)
- 4 assets for E001 Extended version (Assets 1.7-1.10)
- 9 assets for E002 (Assets 2.1-2.9, slides 2-11)
- 8 assets for E003 (Assets 3.1-3.8, slides 2-10)
- 10 assets for E004 (Assets 4.1-4.10, slides 2-12)
- 11 assets for E005 (Assets 5.1-5.11, slides 1-12)

**New assets added (Feb 2025):** 16 assets covering new slides across E002 (slides 9-11), E003 (slides 8-10), E004 (slides 8-12), E005 (slides 8-12)

**Estimated Creation Time (all 45 assets):** 12-16 hours (manual creation) | 5-7 hours (Beautiful.ai prompts)
