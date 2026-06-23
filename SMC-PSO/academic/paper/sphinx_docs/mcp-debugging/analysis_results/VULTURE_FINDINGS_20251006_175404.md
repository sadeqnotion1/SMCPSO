# VULTURE Dead Code Detection - 20251006_175404

## Summary Statistics

- **Total items found**: 15
- **High confidence (>=90%)**: 15 (100.0%)
- **Medium confidence (70-89%)**: 0 (0.0%)
- **Low confidence (<70%)**: 0 (0.0%)

## Category Breakdown

| Category | Count | Percentage |
|----------|-------|------------|
| variable | 13 | 86.7% |
| unknown | 2 | 13.3% |

## High-Confidence Findings (>=90%)

- **variable** `config_hash` (src\controllers\factory\optimization.py:35) - 100%
- **variable** `operation_id` (src\controllers\factory\thread_safety.py:223) - 100%
- **variable** `dynamics` (src\controllers\smc\algorithms\adaptive\controller.py:39) - 100%
- **variable** `dynamics` (src\controllers\smc\algorithms\hybrid\controller.py:77) - 100%
- **variable** `controller_configs` (src\controllers\smc\algorithms\hybrid\controller.py:590) - 100%
- **variable** `dynamics` (src\controllers\smc\algorithms\super_twisting\controller.py:42) - 100%
- **variable** `args` (src\core\dynamics.py:22) - 100%
- **variable** `args` (src\plant\core\numerical_stability.py:25) - 100%
- **variable** `args` (src\plant\core\physics_matrices.py:23) - 100%
- **variable** `error_msg` (src\plant\models\full\dynamics.py:518) - 100%
- **variable** `error_msg` (src\plant\models\full\dynamics.py:554) - 100%
- **variable** `args` (src\plant\models\full\physics.py:20) - 100%
- **variable** `args` (src\plant\models\simplified\physics.py:20) - 100%
- **unknown** `BaseModel` (src\controllers\smc\algorithms\classical\config.py:14) - 90%
- **unknown** `Field` (src\controllers\smc\algorithms\classical\config.py:14) - 90%

## Phase Breakdown

### Phase 1: Critical Controllers & Core

- Files analyzed: 89
- Dead code items: 15
- Duration: 0h 0m

