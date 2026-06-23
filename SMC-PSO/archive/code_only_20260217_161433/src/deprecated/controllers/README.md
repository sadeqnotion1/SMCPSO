# Deprecated Controller Compatibility Shims

**Status**: DEPRECATED (Moved December 19, 2025)
**Removal Timeline**: 4 weeks from deprecation (January 16, 2026)

## What's Here

This directory contains backward-compatibility shim files that re-exported controllers from their legacy locations. These shims were created during the Phase 1 modularization (September 27, 2025) to maintain compatibility during the transition period.

## Deprecated Files

1. `classic_smc.py` - Re-exported ClassicalSMC from src.controllers.smc.classic_smc
2. `adaptive_smc.py` - Re-exported AdaptiveSMC from src.controllers.smc.adaptive_smc
3. `sta_smc.py` - Re-exported SuperTwistingSMC from src.controllers.smc.sta_smc
4. `mpc_controller.py` - Re-exported MPCController from src.controllers.mpc.mpc_controller
5. `swing_up_smc.py` - Re-exported SwingUpSMC from src.controllers.specialized.swing_up_smc

## Migration Guide

### Old Import (Deprecated)
```python
from src.controllers.classic_smc import ClassicalSMC
from src.controllers.adaptive_smc import AdaptiveSMC
from src.controllers.sta_smc import SuperTwistingSMC
from src.controllers.mpc_controller import MPCController
from src.controllers.swing_up_smc import SwingUpSMC
```

### New Import (Correct)
```python
from src.controllers.smc.classic_smc import ClassicalSMC
from src.controllers.smc.adaptive_smc import AdaptiveSMC
from src.controllers.smc.sta_smc import SuperTwistingSMC
from src.controllers.mpc.mpc_controller import MPCController
from src.controllers.specialized.swing_up_smc import SwingUpSMC
```

### Or Use Factory (Recommended)
```python
from src.controllers.factory import create_controller

controller = create_controller('classical_smc', gains=[...])
```

## Verification

All imports have been updated as of December 19, 2025:
- 12 source/test files updated
- 1 documentation file updated
- Zero remaining usage of deprecated paths

Verification command:
```bash
grep -r "from src.controllers.classic_smc import" --include="*.py" .
# Should return no results (except these deprecated shims)
```

## Timeline

- **September 27, 2025**: Shims created during Phase 1 modularization
- **December 19, 2025**: Shims moved to deprecated/ after 4-week grace period
- **January 16, 2026**: Scheduled for permanent removal

## Why Deprecated

These shims added unnecessary indirection and maintenance burden:
1. Extra import layer slows IDE autocomplete
2. Confuses newcomers about canonical locations
3. Increases coupling between modules
4. Prevents clean circular dependency detection

The new structure is clearer and follows standard Python packaging conventions.
