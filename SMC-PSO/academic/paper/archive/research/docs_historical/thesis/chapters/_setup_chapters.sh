#!/bin/bash
# Link presentation files to expected chapter structure

ln -sf ../../presentation/introduction.md 00_introduction.md
ln -sf ../../presentation/problem-statement.md 01_problem_statement.md
ln -sf ../../presentation/previous-works.md 02_literature_review.md
ln -sf "../../presentation/3-System Modling.md" 03_system_modeling.md
ln -sf ../../presentation/4-0-SMC.md 04_sliding_mode_control.md
ln -sf ../../presentation/chattering-mitigation.md 05_chattering_mitigation.md
ln -sf ../../presentation/pso-optimization.md 06_pso_optimization.md
ln -sf "../../presentation/7-Simulation Setup.md" 07_simulation_setup.md
# Results chapter - need to find
ln -sf ../../presentation/conclusion.md 09_conclusion.md
ln -sf ../../presentation/appendix-a-lyapunov.md appendix_a_proofs.md
ln -sf ../../presentation/references.md references.md

echo "[OK] Chapter links created"
