# VULTURE Dead Code Detection - 20251006_191744

## Summary Statistics

- **Total items found**: 16
- **High confidence (>=90%)**: 16 (100.0%)
- **Medium confidence (70-89%)**: 0 (0.0%)
- **Low confidence (<70%)**: 0 (0.0%)

## Category Breakdown

| Category | Count | Percentage |
|----------|-------|------------|
| unknown | 11 | 68.8% |
| variable | 4 | 25.0% |
| unreachable | 1 | 6.2% |

## High-Confidence Findings (>=90%)

- **variable** `dt` (scripts\analysis\fdi_threshold_calibration.py:31) - 100%
- **variable** `u` (scripts\analysis\fdi_threshold_calibration.py:31) - 100%
- **variable** `new_theory` (scripts\docs\enhance_plant_docs.py:200) - 100%
- **variable** `new_theory` (scripts\docs\enhance_plant_docs.py:200) - 100%
- **unreachable** `if` (scripts\test_session_continuity.py:343) - 100%
- **unknown** `shutil` (scripts\coverage\coverage_report.py:31) - 90%
- **unknown** `defaultdict` (scripts\coverage\quick_baseline.py:6) - 90%
- **unknown** `Tuple` (scripts\docs\enhance_api_docs.py:26) - 90%
- **unknown** `inspect` (scripts\docs\generate_code_docs.py:36) - 90%
- **unknown** `Any` (scripts\docs\generate_code_docs.py:39) - 90%
- **unknown** `Tuple` (scripts\docs\generate_code_docs.py:39) - 90%
- **unknown** `inspect` (scripts\docs\generate_code_docs.py:36) - 90%
- **unknown** `Set` (scripts\docs\validate_code_docs.py:20) - 90%
- **unknown** `Tuple` (scripts\docs\validate_code_docs.py:20) - 90%
- **unknown** `tempfile` (scripts\pytest_automation.py:20) - 90%
- **unknown** `CoverageMetrics` (scripts\pytest_automation.py:29) - 90%

## Phase Breakdown

### Phase 4: Scripts & Utilities

- Files analyzed: 69
- Dead code items: 16
- Duration: 0h 0m

