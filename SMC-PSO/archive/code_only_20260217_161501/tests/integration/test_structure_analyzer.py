#======================================================================================\\\
#============================= test_structure_analyzer.py =============================\\\
#======================================================================================\\\

"""Analyze and optimize test directory structure to mirror src/ layout."""

import os
from pathlib import Path
from typing import Dict, List

def analyze_directory_structure() -> Dict[str, any]:
    """Analyze current directory structure for test organization."""

    src_structure = {}
    test_structure = {}

    # Analyze src/ directory structure
    src_path = Path('./src')
    if src_path.exists():
        for root, dirs, files in os.walk(src_path):
            relative_path = os.path.relpath(root, src_path)
            if relative_path == '.':
                relative_path = ''

            py_files = [f for f in files if f.endswith('.py') and f != '__init__.py']
            if py_files or relative_path == '':
                src_structure[relative_path] = py_files

    # Analyze tests/ directory structure
    test_path = Path('./tests')
    if test_path.exists():
        for root, dirs, files in os.walk(test_path):
            relative_path = os.path.relpath(root, test_path)
            if relative_path == '.':
                relative_path = ''

            py_files = [f for f in files if f.endswith('.py') and f != '__init__.py']
            if py_files or relative_path == '':
                test_structure[relative_path] = py_files

    return {
        'src_structure': src_structure,
        'test_structure': test_structure
    }

def find_missing_test_directories(src_structure: Dict[str, List[str]],
                                test_structure: Dict[str, List[str]]) -> List[str]:
    """Find src directories that don't have corresponding test directories."""
    missing_dirs = []

    for src_dir in src_structure.keys():
        if src_dir == '':  # Root src directory
            continue

        # Expected test directory name
        expected_test_dir = f"test_{src_dir.replace('/', '_').replace(os.sep, '_')}"

        # Check if any test directory matches this pattern
        found = False
        for test_dir in test_structure.keys():
            if expected_test_dir in test_dir or src_dir.replace('/', '_') in test_dir:
                found = True
                break

        if not found and src_structure[src_dir]:  # Only if src dir has Python files
            missing_dirs.append(src_dir)

    return missing_dirs

def find_missing_test_files() -> Dict[str, List[str]]:
    """Find source files that don't have corresponding test files."""
    missing_tests = {}

    # Get all source files
    for root, dirs, files in os.walk('./src'):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                src_file_path = os.path.join(root, file)
                relative_src_path = os.path.relpath(src_file_path, './src')

                # Generate expected test file name
                module_name = file[:-3]  # Remove .py
                expected_test_name = f"test_{module_name}.py"

                # Look for corresponding test file
                found = False
                for test_root, test_dirs, test_files in os.walk('./tests'):
                    if expected_test_name in test_files:
                        found = True
                        break

                if not found:
                    src_dir = os.path.dirname(relative_src_path)
                    if src_dir not in missing_tests:
                        missing_tests[src_dir] = []
                    missing_tests[src_dir].append(file)

    return missing_tests

def analyze_test_coverage_structure() -> Dict[str, any]:
    """Analyze test coverage from a structural perspective."""

    # Count source files vs test files
    src_files = 0
    test_files = 0

    for root, dirs, files in os.walk('./src'):
        src_files += len([f for f in files if f.endswith('.py') and f != '__init__.py'])

    for root, dirs, files in os.walk('./tests'):
        test_files += len([f for f in files if f.endswith('.py') and f != '__init__.py' and f != 'conftest.py'])

    return {
        'src_files': src_files,
        'test_files': test_files,
        'test_ratio': test_files / src_files if src_files > 0 else 0
    }

def generate_test_structure_recommendations() -> Dict[str, any]:
    """Generate recommendations for test structure optimization."""

    analysis = analyze_directory_structure()
    missing_dirs = find_missing_test_directories(
        analysis['src_structure'],
        analysis['test_structure']
    )
    missing_files = find_missing_test_files()
    coverage_stats = analyze_test_coverage_structure()

    # Organize recommendations by priority
    recommendations = {
        'high_priority': [],
        'medium_priority': [],
        'low_priority': [],
        'statistics': coverage_stats
    }

    # High priority: Missing test directories for major components
    critical_dirs = ['controllers', 'optimization', 'plant', 'core', 'simulation']
    for missing_dir in missing_dirs:
        if any(critical in missing_dir for critical in critical_dirs):
            recommendations['high_priority'].append({
                'type': 'missing_directory',
                'src_dir': missing_dir,
                'suggested_test_dir': f"test_{missing_dir.replace('/', '_').replace(os.sep, '_')}",
                'reason': 'Critical component missing test structure'
            })

    # Medium priority: Missing test files for important modules
    for src_dir, files in missing_files.items():
        if any(critical in src_dir for critical in critical_dirs):
            for file in files:
                recommendations['medium_priority'].append({
                    'type': 'missing_test_file',
                    'src_file': os.path.join(src_dir, file),
                    'suggested_test_file': f"test_{file}",
                    'suggested_location': f"tests/test_{src_dir.replace('/', '_').replace(os.sep, '_')}",
                    'reason': 'Important module missing test file'
                })

    # Low priority: Other missing components
    for missing_dir in missing_dirs:
        if not any(critical in missing_dir for critical in critical_dirs):
            recommendations['low_priority'].append({
                'type': 'missing_directory',
                'src_dir': missing_dir,
                'suggested_test_dir': f"test_{missing_dir.replace('/', '_').replace(os.sep, '_')}",
                'reason': 'Supporting component missing test structure'
            })

    return recommendations

def create_test_structure_improvement_plan() -> Dict[str, any]:
    """Create a comprehensive test structure improvement plan."""

    recommendations = generate_test_structure_recommendations()

    # Create action plan
    plan = {
        'immediate_actions': [],
        'short_term_actions': [],
        'long_term_actions': [],
        'summary': {}
    }

    # Immediate actions (high priority)
    for rec in recommendations['high_priority'][:5]:  # Top 5 high priority
        plan['immediate_actions'].append({
            'action': f"Create {rec['suggested_test_dir']} directory",
            'description': f"Add test structure for {rec['src_dir']}",
            'impact': 'High - Critical component testing'
        })

    # Short-term actions (medium priority)
    for rec in recommendations['medium_priority'][:10]:  # Top 10 medium priority
        plan['short_term_actions'].append({
            'action': f"Create {rec['suggested_test_file']}",
            'description': f"Add test file for {rec['src_file']}",
            'location': rec['suggested_location'],
            'impact': 'Medium - Important module testing'
        })

    # Long-term actions (comprehensive coverage)
    plan['long_term_actions'].append({
        'action': 'Complete test structure mirroring',
        'description': 'Ensure every src/ directory has corresponding test structure',
        'impact': 'High - Complete structural coverage'
    })

    # Summary statistics
    plan['summary'] = {
        'total_recommendations': len(recommendations['high_priority']) + len(recommendations['medium_priority']) + len(recommendations['low_priority']),
        'high_priority_count': len(recommendations['high_priority']),
        'medium_priority_count': len(recommendations['medium_priority']),
        'current_test_ratio': recommendations['statistics']['test_ratio'],
        'target_test_ratio': 1.5  # 1.5 test files per source file
    }

    return plan

if __name__ == "__main__":
    print("Test Structure Analysis and Optimization")
    print("=" * 50)

    # Analyze current structure
    structure = analyze_directory_structure()

    print(f"Source directories: {len(structure['src_structure'])}")
    print(f"Test directories: {len(structure['test_structure'])}")

    # Generate recommendations
    recommendations = generate_test_structure_recommendations()

    print("\nStructural Coverage Statistics:")
    print(f"  Source files: {recommendations['statistics']['src_files']}")
    print(f"  Test files: {recommendations['statistics']['test_files']}")
    print(f"  Test ratio: {recommendations['statistics']['test_ratio']:.2f}")

    print("\nRecommendations Summary:")
    print(f"  High priority: {len(recommendations['high_priority'])}")
    print(f"  Medium priority: {len(recommendations['medium_priority'])}")
    print(f"  Low priority: {len(recommendations['low_priority'])}")

    # Show high priority recommendations
    print("\nHigh Priority Recommendations:")
    for i, rec in enumerate(recommendations['high_priority'][:5], 1):
        print(f"  {i}. Create test structure for '{rec['src_dir']}'")
        print(f"     Suggested: {rec['suggested_test_dir']}")

    # Show medium priority recommendations
    print("\nMedium Priority Test Files Needed:")
    for i, rec in enumerate(recommendations['medium_priority'][:5], 1):
        print(f"  {i}. {rec['src_file']} -> {rec['suggested_test_file']}")

    # Create improvement plan
    plan = create_test_structure_improvement_plan()

    print("\nTest Structure Improvement Plan:")
    print(f"  Immediate actions: {len(plan['immediate_actions'])}")
    print(f"  Short-term actions: {len(plan['short_term_actions'])}")
    print(f"  Long-term actions: {len(plan['long_term_actions'])}")
    print(f"  Current test ratio: {plan['summary']['current_test_ratio']:.2f}")
    print(f"  Target test ratio: {plan['summary']['target_test_ratio']:.2f}")