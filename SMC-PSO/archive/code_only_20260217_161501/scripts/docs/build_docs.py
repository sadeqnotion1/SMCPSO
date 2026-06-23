#!/usr/bin/env python3
"""
Build automation script for split documentation projects.

Usage:
    python scripts/build_docs.py                    # Auto-detect changes
    python scripts/build_docs.py --all             # Build all 3 projects
    python scripts/build_docs.py --project user    # Build user docs only
    python scripts/build_docs.py --parallel        # Parallel builds
    python scripts/build_docs.py --clean --all     # Full clean rebuild
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed

# Project definitions
PROJECTS = {
    'user': {
        'name': 'User Documentation',
        'dir': 'docs-user',
        'desc': 'Guides, tutorials, controller usage',
        'files': 138,
    },
    'api': {
        'name': 'API Reference',
        'dir': 'docs-api',
        'desc': 'Autodoc, source links, technical details',
        'files': 408,
    },
    'dev': {
        'name': 'Developer Documentation',
        'dir': 'docs-dev',
        'desc': 'Testing, plans, reports, internal docs',
        'files': 222,
    }
}

def get_repo_root() -> Path:
    """Get repository root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent.resolve()

def detect_changed_projects() -> List[str]:
    """
    Auto-detect which projects need rebuilding based on git diff.

    Returns:
        List of project keys ('user', 'api', 'dev')
    """
    repo_root = get_repo_root()

    try:
        # Get list of changed files from git
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD'],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            print("[!] Git not available or not in a git repo - defaulting to 'all'")
            return ['user', 'api', 'dev']

        changed_files = result.stdout.strip().split('\n')
        if not changed_files or changed_files == ['']:
            print("[i] No uncommitted changes detected")
            return []

        # Determine which projects are affected
        projects = set()
        for file in changed_files:
            if file.startswith('docs-user/'):
                projects.add('user')
            elif file.startswith('docs-api/'):
                projects.add('api')
            elif file.startswith('docs-dev/'):
                projects.add('dev')
            elif file.startswith('src/controllers/'):
                # Controller changes affect both user (guides) and API (autodoc)
                projects.add('user')
                projects.add('api')
            elif file.startswith('src/'):
                # Other source changes affect API only
                projects.add('api')
            elif file in ['README.md', 'CHANGELOG.md', 'CONTRIBUTING.md']:
                # Root files copied to user docs
                projects.add('user')

        return sorted(projects)

    except Exception as e:
        print(f"[!] Error detecting changes: {e}")
        return []

def build_project(project: str, clean: bool = False) -> Tuple[str, bool, float]:
    """
    Build a single documentation project.

    Args:
        project: Project key ('user', 'api', 'dev')
        clean: If True, force full rebuild (sphinx-build -E)

    Returns:
        Tuple of (project, success, duration_seconds)
    """
    repo_root = get_repo_root()
    project_info = PROJECTS[project]
    project_dir = repo_root / project_info['dir']
    build_dir = project_dir / '_build' / 'html'

    print(f"\n{'='*80}")
    print(f"Building: {project_info['name']}")
    print(f"Directory: {project_dir}")
    print(f"Files: ~{project_info['files']} files")
    print(f"Clean build: {'Yes' if clean else 'No (incremental)'}")
    print(f"{'='*80}\n")

    # Build command
    cmd = ['sphinx-build', '-b', 'html']
    if clean:
        cmd.append('-E')  # Force full rebuild (clear doctrees)
    cmd.extend(['.', '_build/html'])

    # Run build
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=project_dir,
            capture_output=False,  # Show output in real-time
            check=False
        )
        duration = time.time() - start_time
        success = result.returncode == 0

        # Print summary
        status = "[OK]" if success else "[FAIL]"
        print(f"\n{status} {project_info['name']} build {'succeeded' if success else 'failed'}")
        print(f"Duration: {duration:.1f}s ({duration/60:.1f} minutes)")
        print(f"Output: {build_dir / 'index.html'}")

        return (project, success, duration)

    except Exception as e:
        duration = time.time() - start_time
        print(f"\n[ERROR] Build failed: {e}")
        return (project, False, duration)

def build_projects_sequential(projects: List[str], clean: bool = False) -> List[Tuple[str, bool, float]]:
    """Build projects sequentially."""
    results = []
    for project in projects:
        result = build_project(project, clean)
        results.append(result)
    return results

def build_projects_parallel(projects: List[str], clean: bool = False) -> List[Tuple[str, bool, float]]:
    """Build projects in parallel using multiprocessing."""
    print(f"[i] Building {len(projects)} projects in parallel...")

    results = []
    with ProcessPoolExecutor(max_workers=len(projects)) as executor:
        futures = {executor.submit(build_project, p, clean): p for p in projects}

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    return results

def print_summary(results: List[Tuple[str, bool, float]]):
    """Print build summary."""
    print("\n" + "="*80)
    print("BUILD SUMMARY")
    print("="*80)

    total_duration = sum(r[2] for r in results)
    success_count = sum(1 for r in results if r[1])

    for project, success, duration in sorted(results):
        status = "[OK]" if success else "[FAIL]"
        project_info = PROJECTS[project]
        print(f"{status} {project_info['name']:30s} {duration:6.1f}s")

    print("-"*80)
    print(f"Total: {success_count}/{len(results)} successful")
    print(f"Total time: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
    print("="*80)

    # Exit code
    if success_count < len(results):
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Build documentation projects',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/build_docs.py                    # Auto-detect changes
  python scripts/build_docs.py --all             # Build all 3 projects
  python scripts/build_docs.py --project user    # Build user docs only
  python scripts/build_docs.py --parallel        # Parallel builds
  python scripts/build_docs.py --clean --all     # Full clean rebuild

Projects:
  user - User Documentation (guides, tutorials, workflows)
  api  - API Reference (autodoc, source code links)
  dev  - Developer Documentation (testing, plans, reports)
        """
    )

    parser.add_argument(
        '--project',
        choices=['user', 'api', 'dev'],
        help='Build specific project'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Build all 3 projects'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Force full rebuild (clear doctrees)'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Build projects in parallel'
    )

    args = parser.parse_args()

    # Determine which projects to build
    if args.all:
        projects = ['user', 'api', 'dev']
    elif args.project:
        projects = [args.project]
    else:
        # Auto-detect
        projects = detect_changed_projects()
        if not projects:
            print("[i] No changes detected. Use --all or --project to build anyway.")
            print("    Or: make changes and commit/stage them for detection.")
            return
        print(f"[i] Auto-detected projects: {', '.join(projects)}")

    # Build
    if args.parallel and len(projects) > 1:
        results = build_projects_parallel(projects, args.clean)
    else:
        results = build_projects_sequential(projects, args.clean)

    # Summary
    print_summary(results)

if __name__ == '__main__':
    main()
