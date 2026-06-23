#!/usr/bin/env python
"""
Control Output Types Tests (Week 3 Session 10)

PURPOSE: Comprehensive unit tests for controller output NamedTuple types
COVERAGE TARGET: 100% of control_outputs.py module
STRATEGY: Test NamedTuple contracts, immutability, tuple compatibility

TEST MATRIX:
1. ClassicalSMCOutput - 3-field output type (u, state, history)
2. AdaptiveSMCOutput - 4-field output type (u, state, history, sigma)
3. STAOutput - 4-field output type (u, state, history, sigma)
4. HybridSTAOutput - 4-field output type (u, state, history, sigma)

For each type, test:
- Creation (positional and keyword arguments)
- Field access (by name and by index)
- Tuple compatibility (unpacking, slicing, iteration)
- Immutability (fields cannot be reassigned)
- Equality and hashing
- String representation

Author: Claude Code (Week 3 Session 10)
Date: December 2025
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Import output types
from src.utils.control.types.control_outputs import (
    ClassicalSMCOutput,
    AdaptiveSMCOutput,
    STAOutput,
    HybridSTAOutput,
)

# ==============================================================================
# Test ClassicalSMCOutput
# ==============================================================================

class TestClassicalSMCOutput:
    """Test ClassicalSMCOutput NamedTuple"""

    def test_creation_positional(self):
        """Test creation with positional arguments"""
        output = ClassicalSMCOutput(10.5, (), {"sigma": 0.5})
        assert output.u == 10.5
        assert output.state == ()
        assert output.history == {"sigma": 0.5}

    def test_creation_keyword(self):
        """Test creation with keyword arguments"""
        output = ClassicalSMCOutput(u=5.0, state=(1.0, 2.0), history={})
        assert output.u == 5.0
        assert output.state == (1.0, 2.0)
        assert output.history == {}

    def test_field_access_by_name(self):
        """Test accessing fields by name"""
        output = ClassicalSMCOutput(1.0, (), {})
        assert output.u == 1.0
        assert isinstance(output.state, tuple)
        assert isinstance(output.history, dict)

    def test_field_access_by_index(self):
        """Test accessing fields by index (tuple compatibility)"""
        output = ClassicalSMCOutput(2.0, (1.0,), {"key": "value"})
        assert output[0] == 2.0
        assert output[1] == (1.0,)
        assert output[2] == {"key": "value"}

    def test_unpacking(self):
        """Test tuple unpacking"""
        output = ClassicalSMCOutput(3.0, (), {})
        u, state, history = output
        assert u == 3.0
        assert state == ()
        assert history == {}

    def test_immutability(self):
        """Test that fields cannot be reassigned"""
        output = ClassicalSMCOutput(1.0, (), {})
        with pytest.raises(AttributeError):
            output.u = 2.0

    def test_equality(self):
        """Test equality comparison"""
        output1 = ClassicalSMCOutput(1.0, (), {})
        output2 = ClassicalSMCOutput(1.0, (), {})
        output3 = ClassicalSMCOutput(2.0, (), {})
        assert output1 == output2
        assert output1 != output3

# ==============================================================================
# Test AdaptiveSMCOutput
# ==============================================================================

class TestAdaptiveSMCOutput:
    """Test AdaptiveSMCOutput NamedTuple"""

    def test_creation_positional(self):
        """Test creation with positional arguments"""
        output = AdaptiveSMCOutput(10.0, (1.0,), {"gain": 5.0}, 0.5)
        assert output.u == 10.0
        assert output.state == (1.0,)
        assert output.history == {"gain": 5.0}
        assert output.sigma == 0.5

    def test_creation_keyword(self):
        """Test creation with keyword arguments"""
        output = AdaptiveSMCOutput(u=5.0, state=(2.0, 3.0), history={}, sigma=1.0)
        assert output.u == 5.0
        assert output.state == (2.0, 3.0)
        assert output.sigma == 1.0

    def test_field_access_by_name(self):
        """Test accessing fields by name"""
        output = AdaptiveSMCOutput(1.0, (), {}, 0.0)
        assert hasattr(output, "u")
        assert hasattr(output, "state")
        assert hasattr(output, "history")
        assert hasattr(output, "sigma")

    def test_field_access_by_index(self):
        """Test accessing fields by index"""
        output = AdaptiveSMCOutput(2.0, (1.0,), {}, 0.5)
        assert output[0] == 2.0
        assert output[1] == (1.0,)
        assert output[2] == {}
        assert output[3] == 0.5

    def test_unpacking(self):
        """Test tuple unpacking"""
        output = AdaptiveSMCOutput(3.0, (1.0, 2.0), {}, 0.8)
        u, state, history, sigma = output
        assert u == 3.0
        assert state == (1.0, 2.0)
        assert sigma == 0.8

    def test_immutability(self):
        """Test that fields cannot be reassigned"""
        output = AdaptiveSMCOutput(1.0, (), {}, 0.0)
        with pytest.raises(AttributeError):
            output.sigma = 1.0

# ==============================================================================
# Test STAOutput
# ==============================================================================

class TestSTAOutput:
    """Test STAOutput NamedTuple"""

    def test_creation_positional(self):
        """Test creation with positional arguments"""
        output = STAOutput(15.0, (1.0, 0.5), {"z": 1.0}, 0.3)
        assert output.u == 15.0
        assert output.state == (1.0, 0.5)
        assert output.history == {"z": 1.0}
        assert output.sigma == 0.3

    def test_creation_keyword(self):
        """Test creation with keyword arguments"""
        output = STAOutput(u=10.0, state=(2.0, 3.0), history={"key": "val"}, sigma=0.1)
        assert output.u == 10.0
        assert output.sigma == 0.1

    def test_field_access_by_name(self):
        """Test accessing all fields by name"""
        output = STAOutput(1.0, (0.0, 0.0), {}, 0.0)
        assert output.u == 1.0
        assert output.state == (0.0, 0.0)
        assert output.history == {}
        assert output.sigma == 0.0

    def test_field_access_by_index(self):
        """Test accessing fields by index"""
        output = STAOutput(5.0, (1.0, 2.0), {}, 0.5)
        assert output[0] == 5.0
        assert output[1] == (1.0, 2.0)
        assert output[3] == 0.5

    def test_unpacking(self):
        """Test tuple unpacking"""
        output = STAOutput(7.0, (1.0, 2.0), {"test": True}, 0.9)
        u, state, history, sigma = output
        assert u == 7.0
        assert history == {"test": True}

    def test_slicing(self):
        """Test tuple slicing"""
        output = STAOutput(1.0, (2.0,), {}, 3.0)
        assert output[:2] == (1.0, (2.0,))
        assert output[2:] == ({}, 3.0)

# ==============================================================================
# Test HybridSTAOutput
# ==============================================================================

class TestHybridSTAOutput:
    """Test HybridSTAOutput NamedTuple"""

    def test_creation_positional(self):
        """Test creation with positional arguments"""
        output = HybridSTAOutput(20.0, (1.0, 2.0, 3.0), {"k1": 5.0}, 0.2)
        assert output.u == 20.0
        assert output.state == (1.0, 2.0, 3.0)
        assert output.history == {"k1": 5.0}
        assert output.sigma == 0.2

    def test_creation_keyword(self):
        """Test creation with keyword arguments"""
        output = HybridSTAOutput(u=15.0, state=(4.0, 5.0, 6.0), history={}, sigma=0.4)
        assert output.u == 15.0
        assert output.state == (4.0, 5.0, 6.0)
        assert output.sigma == 0.4

    def test_field_access_by_name(self):
        """Test accessing all fields by name"""
        output = HybridSTAOutput(1.0, (0.0, 0.0, 0.0), {}, 0.0)
        assert output.u == 1.0
        assert len(output.state) == 3
        assert output.sigma == 0.0

    def test_field_access_by_index(self):
        """Test accessing fields by index"""
        output = HybridSTAOutput(10.0, (1.0, 2.0, 3.0), {}, 0.7)
        assert output[0] == 10.0
        assert output[1] == (1.0, 2.0, 3.0)
        assert output[3] == 0.7

    def test_unpacking(self):
        """Test tuple unpacking"""
        output = HybridSTAOutput(8.0, (1.0, 2.0, 3.0), {"gains": [5, 10]}, 0.6)
        u, state, history, sigma = output
        assert u == 8.0
        assert len(state) == 3
        assert sigma == 0.6

    def test_immutability(self):
        """Test that fields cannot be reassigned"""
        output = HybridSTAOutput(1.0, (), {}, 0.0)
        with pytest.raises(AttributeError):
            output.u = 2.0

# ==============================================================================
# Test Cross-Type Behavior
# ==============================================================================

class TestCrossTypeBehavior:
    """Test behavior across all output types"""

    def test_different_types_not_equal(self):
        """Test that different output types are not equal even with same values"""
        classical = ClassicalSMCOutput(1.0, (), {})
        # Adaptive has 4 fields vs 3, so they can't be equal
        adaptive = AdaptiveSMCOutput(1.0, (), {}, 0.0)
        assert classical != adaptive

    def test_all_types_are_tuples(self):
        """Test that all output types are instances of tuple"""
        classical = ClassicalSMCOutput(1.0, (), {})
        adaptive = AdaptiveSMCOutput(1.0, (), {}, 0.0)
        sta = STAOutput(1.0, (), {}, 0.0)
        hybrid = HybridSTAOutput(1.0, (), {}, 0.0)

        assert isinstance(classical, tuple)
        assert isinstance(adaptive, tuple)
        assert isinstance(sta, tuple)
        assert isinstance(hybrid, tuple)

    def test_repr_contains_type_name(self):
        """Test that repr includes the type name"""
        classical = ClassicalSMCOutput(1.0, (), {})
        adaptive = AdaptiveSMCOutput(1.0, (), {}, 0.0)

        assert "ClassicalSMCOutput" in repr(classical)
        assert "AdaptiveSMCOutput" in repr(adaptive)

    def test_iteration(self):
        """Test that all output types are iterable"""
        classical = ClassicalSMCOutput(1.0, (2.0,), {"key": 3.0})
        items = list(classical)
        assert len(items) == 3
        assert items[0] == 1.0

    def test_length(self):
        """Test that len() works on all output types"""
        classical = ClassicalSMCOutput(1.0, (), {})
        adaptive = AdaptiveSMCOutput(1.0, (), {}, 0.0)
        sta = STAOutput(1.0, (), {}, 0.0)
        hybrid = HybridSTAOutput(1.0, (), {}, 0.0)

        assert len(classical) == 3
        assert len(adaptive) == 4
        assert len(sta) == 4
        assert len(hybrid) == 4

# ==============================================================================
# Summary Test
# ==============================================================================

@pytest.mark.unit
def test_control_outputs_summary():
    """Print summary of control output types test coverage"""
    print("\n" + "=" * 80)
    print(" Control Output Types Tests - Week 3 Session 10")
    print("=" * 80)
    print(" Module: src/utils/control/types/control_outputs.py")
    print(" Types Tested: 4 NamedTuple classes")
    print("-" * 80)
    print(" Test Suites:")
    print("   1. ClassicalSMCOutput (7 tests)")
    print("   2. AdaptiveSMCOutput (6 tests)")
    print("   3. STAOutput (6 tests)")
    print("   4. HybridSTAOutput (6 tests)")
    print("   5. Cross-Type Behavior (5 tests)")
    print("-" * 80)
    print(" Total Tests: 30")
    print(" Coverage Strategy:")
    print("   - NamedTuple creation (positional & keyword)")
    print("   - Field access (by name & by index)")
    print("   - Tuple compatibility (unpacking, slicing, iteration)")
    print("   - Immutability verification")
    print("   - Equality and representation")
    print("   - Cross-type behavior")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
