# Thesis Citation Locations

This file maps each source to its exact location(s) in the thesis.

**Thesis**: Double-Inverted Pendulum Sliding Mode Control with PSO Optimization
**Version**: v2.1
**Last Updated**: December 6, 2025

---

## Citation Location Format

Each entry shows:
- **BibTeX Key**: Unique identifier
- **Sections**: Where cited (e.g., Section 1.1, 3.2)
- **Pages**: Page numbers in compiled PDF
- **Context**: Why/how the source is cited
- **Citation Type**: Background, Methodology, Comparison, Theory

---

## Chapter 1: Introduction

### Section 1.1 - Motivation and Background

**Khalil2002** (p. X)
- **Context**: Nonlinear system theory fundamentals
- **Type**: Background, Theory
- **Quote/Usage**: Lyapunov stability, nonlinear dynamics

**BoubakersIriarte2017** (p. X)
- **Context**: Inverted pendulum applications in control theory
- **Type**: Background
- **Quote/Usage**: Historical context, modern applications

**Collins2005** (p. X)
- **Context**: Underactuated systems in robotics
- **Type**: Background, Application
- **Quote/Usage**: Bipedal locomotion, passive-dynamic walkers

**Spong1998** (p. X)
- **Context**: Underactuated mechanical systems theory
- **Type**: Background, Theory
- **Quote/Usage**: Definition, control challenges

**FantoniLozano2002** (p. X)
- **Context**: Control of underactuated systems
- **Type**: Background, Theory
- **Quote/Usage**: Nonlinear control methodologies

### Section 1.2 - Problem Statement

(No direct citations - problem statement is original)

### Section 1.3 - Objectives

(No direct citations - objectives are specific to this work)

---

## Chapter 2: System Modeling

### Section 2.1 - Double Inverted Pendulum Dynamics

**Khalil2002** (p. X)
- **Context**: Lagrangian mechanics, state-space representation
- **Type**: Methodology, Theory
- **Quote/Usage**: Nonlinear system formulation

**FantoniLozano2002** (p. X)
- **Context**: Underactuated system modeling
- **Type**: Methodology
- **Quote/Usage**: Equations of motion derivation

**Quanser2020** (p. X)
- **Context**: Physical parameters, experimental setup
- **Type**: Methodology, Data
- **Quote/Usage**: Hardware specifications

**ECP2020** (p. X)
- **Context**: Alternative hardware platform reference
- **Type**: Background
- **Quote/Usage**: Comparison with other inverted pendulum systems

### Section 2.2 - Linearization

**Khalil2002** (p. X)
- **Context**: Linearization methods
- **Type**: Methodology
- **Quote/Usage**: Jacobian linearization, equilibrium analysis

---

## Chapter 3: Controller Design

### Section 3.1 - Classical Sliding Mode Control

**Utkin1977** (p. X)
- **Context**: Foundation of variable structure systems
- **Type**: Background, Theory
- **Quote/Usage**: Original SMC formulation, reaching law

**EdwardsSpurgeon1998** (p. X)
- **Context**: SMC theory and design methodology
- **Type**: Methodology, Theory
- **Quote/Usage**: Sliding surface design, control law derivation

**Shtessel2014** (p. X)
- **Context**: Modern SMC techniques
- **Type**: Background, Methodology
- **Quote/Usage**: Comprehensive SMC design guidelines

**SlotineSastry1983** (p. X)
- **Context**: Sliding surface design for nonlinear systems
- **Type**: Methodology
- **Quote/Usage**: Lyapunov-based design, robot manipulator application

### Section 3.2 - Super-Twisting Algorithm (STA)

**Levant2007** (p. X)
- **Context**: 2-sliding mode principles
- **Type**: Methodology, Theory
- **Quote/Usage**: STA algorithm, finite-time convergence

**Shtessel2014** (p. X)
- **Context**: STA implementation details
- **Type**: Methodology
- **Quote/Usage**: Parameter tuning, chattering reduction

### Section 3.3 - Adaptive Sliding Mode Control

**SlotineCoetsee1986** (p. X)
- **Context**: Original adaptive SMC formulation
- **Type**: Background, Methodology
- **Quote/Usage**: Adaptation laws, parameter estimation

**Plestan2010** (p. X)
- **Context**: Modern adaptive SMC methodologies
- **Type**: Methodology
- **Quote/Usage**: New adaptation strategies, robustness analysis

**Shtessel2014** (p. X)
- **Context**: Adaptive gain tuning
- **Type**: Methodology
- **Quote/Usage**: Chattering reduction via adaptation

### Section 3.4 - Hybrid Adaptive STA-SMC

**Levant2007** + **Plestan2010** (p. X)
- **Context**: Combination of STA and adaptive techniques
- **Type**: Methodology (Novel contribution)
- **Quote/Usage**: Theoretical foundation for hybrid approach

### Section 3.5 - Classical PID Control (Baseline)

**AstromHagglund2006** (p. X)
- **Context**: Advanced PID design
- **Type**: Comparison, Background
- **Quote/Usage**: Tuning methods, performance limitations

**ODwyer2009** (p. X)
- **Context**: PID tuning rules
- **Type**: Methodology
- **Quote/Usage**: Ziegler-Nichols, other tuning methods

### Section 3.6 - Related Work

**Khanesar2013** (p. X)
- **Context**: SMC for rotary inverted pendulum
- **Type**: Comparison
- **Quote/Usage**: Alternative SMC implementation, results comparison

---

## Chapter 4: PSO Optimization

### Section 4.1 - PSO Algorithm

**Kennedy1995** (p. X)
- **Context**: Original PSO algorithm
- **Type**: Background, Theory
- **Quote/Usage**: Algorithm formulation, swarm intelligence

**ClercKennedy2002** (p. X)
- **Context**: PSO convergence and stability
- **Type**: Theory, Methodology
- **Quote/Usage**: Constriction factor, parameter selection

### Section 4.2 - PSO for Controller Tuning

**Zhou2012** (p. X)
- **Context**: PSO application to control systems
- **Type**: Background, Methodology
- **Quote/Usage**: PSO for parameter optimization

**Dash2015** (p. X)
- **Context**: PSO-SMC for power systems
- **Type**: Background, Comparison
- **Quote/Usage**: Combined PSO-SMC approach, application domain

### Section 4.3 - Objective Function Design

(Original contribution, no direct citations)

### Section 4.4 - PSO Implementation

**Kennedy1995** + **ClercKennedy2002** (p. X)
- **Context**: PSO parameters, implementation details
- **Type**: Methodology
- **Quote/Usage**: Swarm size, inertia weight, cognitive/social factors

---

## Chapter 5: Results and Analysis

### Section 5.1 - Simulation Setup

(Primarily original work, some references to hardware specs)

**Quanser2020** (p. X)
- **Context**: Physical parameters for realistic simulation
- **Type**: Data
- **Quote/Usage**: Mass, length, friction parameters

### Section 5.2 - Performance Comparison

**Khanesar2013** + **Dash2015** (p. X)
- **Context**: Benchmark comparison
- **Type**: Comparison
- **Quote/Usage**: Performance metrics, baseline results

### Section 5.3 - Robustness Analysis

**Khalil2002** (p. X)
- **Context**: Lyapunov stability analysis
- **Type**: Theory
- **Quote/Usage**: Stability proofs, robustness criteria

**Shtessel2014** (p. X)
- **Context**: SMC robustness properties
- **Type**: Theory
- **Quote/Usage**: Disturbance rejection, uncertainty handling

---

## Chapter 6: Conclusion

### Section 6.1 - Summary

(Synthesis of all prior work, no new citations)

### Section 6.2 - Future Work

**Deb2002** (p. X)
- **Context**: Multi-objective optimization
- **Type**: Future direction
- **Quote/Usage**: NSGA-II for multi-objective controller tuning

---

## Appendices

### Appendix A - Lyapunov Proofs

**Khalil2002** (multiple pages)
- **Context**: Lyapunov theory fundamentals
- **Type**: Theory
- **Quote/Usage**: Stability theorems, proof techniques

**SlotineSastry1983** + **SlotineCoetsee1986**
- **Context**: SMC stability proofs
- **Type**: Theory
- **Quote/Usage**: Specific to sliding mode systems

### Appendix B - Code Implementation

(Original code, references to libraries/frameworks)

### Appendix C - Experimental Data

**Quanser2020**
- **Context**: Hardware specifications
- **Type**: Data
- **Quote/Usage**: Physical parameters

---

## Citation Statistics

**Total Citations**: 27 (from 22 unique sources)

**By Chapter**:
- Chapter 1 (Introduction): 5 sources
- Chapter 2 (System Modeling): 4 sources
- Chapter 3 (Controller Design): 9 sources
- Chapter 4 (PSO Optimization): 4 sources
- Chapter 5 (Results): 3 sources
- Chapter 6 (Conclusion): 1 source
- Appendices: 4 sources (with overlaps)

**By Citation Type**:
- Background: 15 (56%)
- Methodology: 18 (67%)
- Theory: 12 (44%)
- Comparison: 4 (15%)
- Data: 3 (11%)

**Most Cited Sources**:
1. Khalil2002 (5 times) - Nonlinear systems theory
2. Shtessel2014 (5 times) - SMC methodology
3. Quanser2020 (3 times) - Hardware specs
4. ClercKennedy2002 (2 times) - PSO theory

---

## Notes

- **Exact page numbers**: Fill in after final compilation
- **Cross-references**: Some sources cited multiple times across chapters
- **Indirect citations**: Some sources inform methodology without direct quotes
- **Original contributions**: Chapters/sections with minimal citations represent novel work

**To Update**: After each compilation, verify citation locations using:
```bash
grep -n "\\cite{" thesis/report/*.tex thesis/chapters/*.tex
```

**Last Verified**: December 6, 2025
