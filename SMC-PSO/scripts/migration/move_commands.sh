#!/bin/bash
# Auto-generated migration commands for scripts reorganization
# Generated: 2025-12-19

set -e  # Exit on first error

git mv scripts\documentation\analyze_cross_references.py scripts\docs\analyze_cross_references.py
git mv scripts\documentation\extract_doc_examples.py scripts\docs\extract_doc_examples.py
git mv scripts\documentation\tag_conceptual_examples.py scripts\docs\tag_conceptual_examples.py
# Remove empty directory: documentation
rmdir scripts/documentation
git mv scripts\docs_organization\detect_redundancy.py scripts\docs\detect_redundancy.py
git mv scripts\docs_organization\enforce_naming_conventions.py scripts\docs\enforce_naming_conventions.py
git mv scripts\docs_organization\generate_structure_report.py scripts\docs\generate_structure_report.py
git mv scripts\docs_organization\validate_ascii_headers.py scripts\docs\validate_ascii_headers.py
git mv scripts\docs_organization\validate_links.py scripts\docs\validate_links.py
# Remove empty directory: docs_organization
rmdir scripts/docs_organization
mkdir -p scripts/testing
mkdir -p scripts/infrastructure
mkdir -p scripts/utils
git mv scripts/build_docs.py scripts/docs/build_docs.py
git mv scripts/categorize_docs.py scripts/docs/categorize_docs.py
git mv scripts/check_docs.py scripts/docs/check_docs.py
git mv scripts/find_orphaned_docs.py scripts/docs/find_orphaned_docs.py
git mv scripts/fix_horizontal_rules.py scripts/docs/fix_horizontal_rules.py
git mv scripts/validate_documentation.py scripts/docs/validate_documentation.py
git mv scripts/test_baseline_chattering.py scripts/testing/test_baseline_chattering.py
git mv scripts/test_session_continuity.py scripts/testing/test_session_continuity.py
git mv scripts/check_coverage_gates.py scripts/validation/check_coverage_gates.py
git mv scripts/validate_memory_optimization.py scripts/validation/validate_memory_optimization.py
git mv scripts/validate_memory_pool.py scripts/validation/validate_memory_pool.py
git mv scripts/diagnose_pytest_unicode.py scripts/infrastructure/diagnose_pytest_unicode.py
git mv scripts/lt6_model_uncertainty.py scripts/research/lt6_model_uncertainty.py
git mv scripts/debug_pso_fitness.py scripts/optimization/debug_pso_fitness.py
git mv scripts/monitor_pso_streamlit.py scripts/monitoring/monitor_pso_streamlit.py
