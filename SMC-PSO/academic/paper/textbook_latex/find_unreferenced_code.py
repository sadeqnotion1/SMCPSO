"""
Find Python modules that are NOT referenced in the textbook chapters.
This helps identify missing documentation or implementation-only modules.
"""

import os
from pathlib import Path

# Get all referenced files from chapters (from analyze_code_links.py results)
referenced_files = set([
    'src/controllers/smc/algorithms/classical/controller.py',
    'src/controllers/smc/core/sliding_surface.py',
    'src/controllers/smc/classic_smc.py',
    'src/controllers/smc/sta_smc.py',
    'src/controllers/smc/adaptive_smc.py',
    'src/controllers/smc/hybrid_adaptive_sta_smc.py',
    'src/optimization/algorithms/pso_optimizer.py',
    'src/optimization/algorithms/robust_pso_optimizer.py',
    'src/benchmarks/core/trial_runner.py',
    'src/benchmarks/analysis/accuracy_metrics.py',
    'src/plant/models/full/dynamics.py',
    'src/plant/core/physics_matrices.py',
    'src/plant/core/dynamics.py',
    'src/utils/model_uncertainty.py',
    'src/interfaces/hil/plant_server.py',
    'src/interfaces/hil/controller_client.py',
    'src/controllers/factory/core.py',
    'src/simulation/engines/simulation_runner.py',
    'src/simulation/engines/vector_sim.py',
    'src/config.py',
    'simulate.py',
    'streamlit_app.py',
    'tests/test_controllers/test_classical_smc.py',
    'tests/test_integration/test_stability.py'
])

# Find all Python files in key directories
important_dirs = [
    'src/controllers',
    'src/optimization',
    'src/plant',
    'src/benchmarks',
    'src/simulation',
    'src/interfaces',
    'src/utils'
]

all_files = []
for dir_path in important_dirs:
    if os.path.exists(dir_path):
        for root, dirs, files in os.walk(dir_path):
            # Skip __pycache__
            if '__pycache__' in root:
                continue
            for f in files:
                if f.endswith('.py') and f != '__init__.py':
                    rel_path = os.path.relpath(os.path.join(root, f))
                    # Normalize path separators
                    rel_path = rel_path.replace(os.sep, '/')
                    all_files.append(rel_path)

# Find unreferenced files
unreferenced = sorted([f for f in all_files if f not in referenced_files])

print('=' * 80)
print('UNREFERENCED PYTHON MODULES - GAP ANALYSIS')
print('=' * 80)
print(f'Total Python files in important dirs: {len(all_files)}')
print(f'Referenced in textbook chapters:      {len(referenced_files)}')
print(f'Unreferenced (potential gaps):        {len(unreferenced)}')
print(f'Coverage:                              {len(referenced_files)/len(all_files)*100:.1f}%')
print()

# Group by category
categories = {
    'Controllers': [],
    'Optimization': [],
    'Plant/Dynamics': [],
    'Benchmarking': [],
    'Simulation': [],
    'HIL/Interfaces': [],
    'Utils/Support': []
}

for f in unreferenced:
    if 'controllers' in f:
        categories['Controllers'].append(f)
    elif 'optimization' in f:
        categories['Optimization'].append(f)
    elif 'plant' in f:
        categories['Plant/Dynamics'].append(f)
    elif 'benchmarks' in f:
        categories['Benchmarking'].append(f)
    elif 'simulation' in f:
        categories['Simulation'].append(f)
    elif 'interfaces' in f:
        categories['HIL/Interfaces'].append(f)
    elif 'utils' in f:
        categories['Utils/Support'].append(f)

# Identify HIGH PRIORITY gaps (core functionality not documented)
high_priority = []
medium_priority = []
low_priority = []

for f in unreferenced:
    # High priority: Core controller algorithms not referenced
    if any(x in f for x in ['controller', 'smc', 'mpc', 'swing']):
        high_priority.append(f)
    # Medium priority: Important utilities, optimization variants
    elif any(x in f for x in ['optimizer', 'dynamics', 'validation', 'monitoring']):
        medium_priority.append(f)
    # Low priority: Infrastructure, testing, utilities
    else:
        low_priority.append(f)

print('HIGH PRIORITY GAPS (Core algorithms not documented):')
print('-' * 80)
if high_priority:
    for f in high_priority:
        print(f'  [!] {f}')
else:
    print('  [OK] No high-priority gaps')
print()

print('MEDIUM PRIORITY GAPS (Important features not documented):')
print('-' * 80)
if medium_priority:
    for f in medium_priority[:15]:
        print(f'  [~] {f}')
    if len(medium_priority) > 15:
        print(f'  ... and {len(medium_priority)-15} more')
else:
    print('  [OK] No medium-priority gaps')
print()

print('BREAKDOWN BY CATEGORY:')
print('-' * 80)
for category, files in categories.items():
    if files:
        print(f'{category}: {len(files)} unreferenced files')
        for f in files[:5]:
            print(f'  - {f}')
        if len(files) > 5:
            print(f'  ... and {len(files)-5} more')
        print()

print('=' * 80)
print('RECOMMENDATIONS:')
print('=' * 80)
print()
if high_priority:
    print('[ACTION] Consider adding references for HIGH PRIORITY modules:')
    for f in high_priority[:5]:
        # Suggest which chapter
        if 'swing' in f:
            print(f'  - {f} -> Ch10 (Advanced Topics) or Ch12 (Case Studies)')
        elif 'mpc' in f:
            print(f'  - {f} -> Ch10 (Advanced Topics)')
        else:
            print(f'  - {f} -> Relevant controller chapter')
    print()

if len(low_priority) > 50:
    print(f'[INFO] {len(low_priority)} low-priority infrastructure files unreferenced (expected)')
    print('       These are typically internal utilities, configs, and helpers.')
print()
print('[OK] Analysis complete. Use this to identify documentation gaps.')
