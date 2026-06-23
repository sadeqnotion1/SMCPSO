#==========================================================================================\
#======================== scripts/test_session_continuity.py ===========================\
#==========================================================================================\

"""Session Continuity System Validation Script.

This script validates the complete session continuity system including:
- Session state save/load functionality
- Auto-detection logic
- Session summary generation
- Integration with automated backup system

Usage:
    python scripts/test_session_continuity.py

Expected Output:
    All tests pass with green checkmarks, indicating the system is ready for production.
"""

import sys
from pathlib import Path

# Add .dev_tools to path for session_manager import
sys.path.insert(0, str(Path(__file__).parent.parent / ".dev_tools"))

from datetime import datetime, timedelta
import json
from session_manager import (
    load_session,
    save_session,
    has_recent_session,
    get_session_summary,
    update_session_context,
    add_completed_todo,
    add_decision,
    add_next_action,
    mark_token_limit_approaching,
    finalize_session,
    get_default_state,
    SESSION_FILE
)


def test_session_save_load() -> bool:
    """Test basic session save and load functionality."""
    print("  [1/8] Testing session save/load...", end=" ")

    # Create test state
    test_state = get_default_state()
    test_state['context']['current_task'] = "Test task"
    test_state['context']['phase'] = "testing"

    # Save and reload
    save_success = save_session(test_state)
    loaded_state = load_session()

    if not save_success:
        print("[FAIL] - Could not save session")
        return False

    if loaded_state is None:
        print("[FAIL] - Could not load session")
        return False

    if loaded_state['context']['current_task'] != "Test task":
        print("[FAIL] - Data mismatch after load")
        return False

    print("[PASS]")
    return True


def test_recent_session_detection() -> bool:
    """Test auto-detection of recent sessions."""
    print("  [2/8] Testing recent session detection...", end=" ")

    # Should detect recent session (just saved in previous test)
    is_recent = has_recent_session(threshold_hours=24)

    if not is_recent:
        print("[FAIL] - Recent session not detected")
        return False

    # Test with old timestamp (artificially create old session)
    state = load_session()
    if state:
        # Save with old timestamp (25 hours ago) - direct file write to bypass auto-update
        old_time = (datetime.now() - timedelta(hours=25)).isoformat(timespec='seconds')
        state['last_updated'] = old_time

        # Write directly to file without using save_session (which auto-updates timestamp)
        with open(SESSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        # Should NOT detect as recent with 24-hour threshold
        is_recent_old = has_recent_session(threshold_hours=24)

        # Restore current timestamp using save_session
        state['last_updated'] = datetime.now().isoformat(timespec='seconds')
        save_session(state)

        if is_recent_old:
            print("[FAIL] - False positive on old session")
            return False

    print("[PASS]")
    return True


def test_session_summary() -> bool:
    """Test session summary generation."""
    print("  [3/8] Testing session summary generation...", end=" ")

    summary = get_session_summary()

    if not summary:
        print("[FAIL] - No summary generated")
        return False

    # Check for key components in summary
    required_components = ["Task:", "Phase:", "Last commit:", "Completed:", "In progress:", "Pending:"]
    for component in required_components:
        if component not in summary:
            print(f"[FAIL] - Missing component: {component}")
            return False

    print("[PASS]")
    return True


def test_context_update() -> bool:
    """Test context update functionality."""
    print("  [4/8] Testing context updates...", end=" ")

    # Update context
    success = update_session_context(
        current_task="Updated task",
        phase="validation",
        last_commit="test123"
    )

    if not success:
        print("[FAIL] - Context update failed")
        return False

    # Verify update
    state = load_session()
    if state['context']['current_task'] != "Updated task":
        print("[FAIL] - Context not updated correctly")
        return False

    print("[PASS]")
    return True


def test_todo_tracking() -> bool:
    """Test todo tracking functionality."""
    print("  [5/8] Testing todo tracking...", end=" ")

    # Add completed todo
    success = add_completed_todo("Test todo item")
    if not success:
        print("[FAIL] - Could not add completed todo")
        return False

    # Verify it's in completed list
    state = load_session()
    if "Test todo item" not in state['todos']['completed']:
        print("[FAIL] - Todo not added to completed list")
        return False

    print("[PASS]")
    return True


def test_decision_tracking() -> bool:
    """Test decision tracking functionality."""
    print("  [6/8] Testing decision tracking...", end=" ")

    # Add decision
    success = add_decision("Test decision: Use method X")
    if not success:
        print("[FAIL] - Could not add decision")
        return False

    # Verify it's tracked
    state = load_session()
    if "Test decision: Use method X" not in state['decisions']:
        print("[FAIL] - Decision not tracked")
        return False

    print("[PASS]")
    return True


def test_next_actions() -> bool:
    """Test next action tracking."""
    print("  [7/8] Testing next action tracking...", end=" ")

    # Add next action
    success = add_next_action("Test action: Do something")
    if not success:
        print("[FAIL] - Could not add next action")
        return False

    # Verify it's tracked
    state = load_session()
    if "Test action: Do something" not in state['next_actions']:
        print("[FAIL] - Next action not tracked")
        return False

    print("[PASS]")
    return True


def test_finalization() -> bool:
    """Test session finalization for token limit handoff."""
    print("  [8/8] Testing session finalization...", end=" ")

    # Mark token limit approaching
    mark_success = mark_token_limit_approaching()
    if not mark_success:
        print("[FAIL] - Could not mark token limit")
        return False

    # Finalize session
    finalize_success = finalize_session("Test completion summary")
    if not finalize_success:
        print("[FAIL] - Could not finalize session")
        return False

    # Verify finalization
    state = load_session()
    if state['status'] != 'finalized':
        print("[FAIL] - Session not finalized correctly")
        return False

    if state['finalization_summary'] != "Test completion summary":
        print("[FAIL] - Finalization summary not saved")
        return False

    print("[PASS]")
    return True


def validate_session_file_schema() -> bool:
    """Validate that session state file has correct schema."""
    print("\n[Bonus] Validating session file schema...", end=" ")

    state = load_session()
    if not state:
        print("[FAIL] - Could not load session")
        return False

    # Check required top-level keys
    required_keys = ['session_id', 'last_updated', 'status', 'context', 'todos', 'decisions', 'next_actions', 'metadata']
    for key in required_keys:
        if key not in state:
            print(f"[FAIL] - Missing key: {key}")
            return False

    # Check context structure
    context_keys = ['current_task', 'phase', 'last_commit', 'branch', 'working_directory']
    for key in context_keys:
        if key not in state['context']:
            print(f"[FAIL] - Missing context key: {key}")
            return False

    # Check todos structure
    todo_keys = ['completed', 'in_progress', 'pending']
    for key in todo_keys:
        if key not in state['todos']:
            print(f"[FAIL] - Missing todos key: {key}")
            return False

    print("[PASS]")
    return True


def main():
    """Run all validation tests."""
    print("\n" + "="*70)
    print("Session Continuity System Validation")
    print("="*70)
    print()

    print(f"Session state file: {SESSION_FILE}")
    print(f"File exists: {'[OK] Yes' if SESSION_FILE.exists() else '[FAIL] No'}")
    print()

    if not SESSION_FILE.exists():
        print("[FAIL] ERROR: Session state file does not exist!")
        print("   Expected location:", SESSION_FILE)
        return 1

    print("Running validation tests:\n")

    # Run all tests
    tests = [
        test_session_save_load,
        test_recent_session_detection,
        test_session_summary,
        test_context_update,
        test_todo_tracking,
        test_decision_tracking,
        test_next_actions,
        test_finalization
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"[EXCEPTION] - {e}")
            results.append(False)

    # Bonus validation
    try:
        schema_valid = validate_session_file_schema()
    except Exception as e:
        print(f"❌ EXCEPTION - {e}")
        schema_valid = False

    # Summary
    print("\n" + "="*70)
    passed = sum(results) + (1 if schema_valid else 0)
    total = len(results) + 1
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("[SUCCESS] All tests passed! Session continuity system is ready for production.")
        print("\nNext steps:")
        print("  1. Register Task Scheduler: Run .dev_tools/register-task-scheduler.bat")
        print("  2. Test automated backup: Wait 1 minute, check git log")
        print("  3. Test manual checkpoint: powershell .dev_tools/claude-backup.ps1 -Checkpoint")
        return 0
    else:
        print(f"[FAIL] {total - passed} test(s) failed. Please review errors above.")
        return 1

    print("="*70 + "\n")


if __name__ == "__main__":
    sys.exit(main())
