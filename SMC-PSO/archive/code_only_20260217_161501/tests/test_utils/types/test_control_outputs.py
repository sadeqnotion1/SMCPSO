#======================================================================================\\
#==================== tests/test_utils/types/test_control_outputs.py ==================\\
#======================================================================================\\

"""
Comprehensive tests for structured controller return types.

Tests cover:
- ClassicalSMCOutput - Classical SMC return type (u, state, history)
- AdaptiveSMCOutput - Adaptive SMC return type (u, state, history, sigma)
- STAOutput - Super-twisting algorithm return type
- HybridSTAOutput - Hybrid adaptive STA-SMC return type
- NamedTuple properties (immutability, tuple compatibility, field access)
"""

import pytest
from typing import Tuple, Dict, Any
from src.utils.control.types.control_outputs import (
    ClassicalSMCOutput,
    AdaptiveSMCOutput,
    STAOutput,
    HybridSTAOutput
)


# =====================================================================================
# Tests for ClassicalSMCOutput
# =====================================================================================

class TestClassicalSMCOutput:
    """Test ClassicalSMCOutput NamedTuple."""

    def test_creation_with_all_fields(self):
        """Test creating ClassicalSMCOutput with all fields."""
        output = ClassicalSMCOutput(
            u=10.5,
            state=(),
            history={'sigma': [0.1, 0.2]}
        )

        assert output.u == 10.5
        assert output.state == ()
        assert output.history == {'sigma': [0.1, 0.2]}

    def test_field_access_by_name(self):
        """Test accessing fields by name."""
        output = ClassicalSMCOutput(u=5.0, state=(), history={})

        assert output.u == 5.0
        assert output.state == ()
        assert isinstance(output.history, dict)

    def test_field_access_by_index(self):
        """Test tuple-like access by index."""
        output = ClassicalSMCOutput(u=3.0, state=(), history={'key': 'value'})

        # Tuple compatibility
        assert output[0] == 3.0
        assert output[1] == ()
        assert output[2] == {'key': 'value'}

    def test_immutability(self):
        """Test that ClassicalSMCOutput is immutable."""
        output = ClassicalSMCOutput(u=2.0, state=(), history={})

        with pytest.raises(AttributeError):
            output.u = 10.0  # Should raise AttributeError

    def test_empty_state_validation(self):
        """Test that classical SMC has empty state."""
        output = ClassicalSMCOutput(u=1.0, state=(), history={})

        assert output.state == ()
        assert len(output.state) == 0

    def test_negative_control_value(self):
        """Test with negative control value."""
        output = ClassicalSMCOutput(u=-15.0, state=(), history={})

        assert output.u == -15.0

    def test_unpacking(self):
        """Test unpacking ClassicalSMCOutput as tuple."""
        output = ClassicalSMCOutput(u=7.0, state=(), history={'test': 1})

        u, state, history = output

        assert u == 7.0
        assert state == ()
        assert history == {'test': 1}


# =====================================================================================
# Tests for AdaptiveSMCOutput
# =====================================================================================

class TestAdaptiveSMCOutput:
    """Test AdaptiveSMCOutput NamedTuple."""

    def test_creation_with_all_fields(self):
        """Test creating AdaptiveSMCOutput with all fields."""
        output = AdaptiveSMCOutput(
            u=5.0,
            state=(0.5, 1.0, 2.0),
            history={'integral': [0.1, 0.2]},
            sigma=0.3
        )

        assert output.u == 5.0
        assert output.state == (0.5, 1.0, 2.0)
        assert output.history == {'integral': [0.1, 0.2]}
        assert output.sigma == 0.3

    def test_field_access_by_name(self):
        """Test accessing fields by name."""
        output = AdaptiveSMCOutput(
            u=3.0,
            state=(1.0,),
            history={},
            sigma=0.1
        )

        assert output.u == 3.0
        assert output.state == (1.0,)
        assert output.sigma == 0.1

    def test_field_access_by_index(self):
        """Test tuple-like access by index."""
        output = AdaptiveSMCOutput(
            u=2.0,
            state=(0.5,),
            history={},
            sigma=0.2
        )

        assert output[0] == 2.0
        assert output[1] == (0.5,)
        assert output[2] == {}
        assert output[3] == 0.2

    def test_immutability(self):
        """Test that AdaptiveSMCOutput is immutable."""
        output = AdaptiveSMCOutput(u=1.0, state=(0.1,), history={}, sigma=0.5)

        with pytest.raises(AttributeError):
            output.sigma = 1.0

    def test_state_with_multiple_values(self):
        """Test adaptive state with multiple values."""
        output = AdaptiveSMCOutput(
            u=10.0,
            state=(0.1, 0.2, 0.3, 0.4),
            history={},
            sigma=0.0
        )

        assert len(output.state) == 4
        assert output.state[0] == 0.1
        assert output.state[3] == 0.4

    def test_negative_sigma(self):
        """Test with negative sigma value."""
        output = AdaptiveSMCOutput(u=5.0, state=(0.0,), history={}, sigma=-0.5)

        assert output.sigma == -0.5

    def test_unpacking(self):
        """Test unpacking AdaptiveSMCOutput as tuple."""
        output = AdaptiveSMCOutput(u=8.0, state=(1.0,), history={'x': 1}, sigma=0.4)

        u, state, history, sigma = output

        assert u == 8.0
        assert state == (1.0,)
        assert history == {'x': 1}
        assert sigma == 0.4


# =====================================================================================
# Tests for STAOutput
# =====================================================================================

class TestSTAOutput:
    """Test STAOutput NamedTuple."""

    def test_creation_with_all_fields(self):
        """Test creating STAOutput with all fields."""
        output = STAOutput(
            u=12.0,
            state=(0.5, 0.3),
            history={'z': [0.1, 0.2]},
            sigma=0.2
        )

        assert output.u == 12.0
        assert output.state == (0.5, 0.3)
        assert output.history == {'z': [0.1, 0.2]}
        assert output.sigma == 0.2

    def test_field_access_by_name(self):
        """Test accessing fields by name."""
        output = STAOutput(u=4.0, state=(0.1, 0.2), history={}, sigma=0.0)

        assert output.u == 4.0
        assert output.state == (0.1, 0.2)
        assert output.sigma == 0.0

    def test_field_access_by_index(self):
        """Test tuple-like access by index."""
        output = STAOutput(u=6.0, state=(0.2, 0.3), history={'a': 1}, sigma=0.1)

        assert output[0] == 6.0
        assert output[1] == (0.2, 0.3)
        assert output[2] == {'a': 1}
        assert output[3] == 0.1

    def test_immutability(self):
        """Test that STAOutput is immutable."""
        output = STAOutput(u=3.0, state=(0.0, 0.0), history={}, sigma=0.5)

        with pytest.raises(AttributeError):
            output.u = 20.0

    def test_state_tuple_structure(self):
        """Test state tuple structure for STA."""
        output = STAOutput(u=5.0, state=(0.8, 0.9), history={}, sigma=0.3)

        # STA typically has 2-element state (z, sigma_int)
        assert len(output.state) == 2
        assert output.state[0] == 0.8
        assert output.state[1] == 0.9

    def test_zero_sigma(self):
        """Test with zero sigma (on sliding surface)."""
        output = STAOutput(u=10.0, state=(0.0, 0.0), history={}, sigma=0.0)

        assert output.sigma == 0.0

    def test_unpacking(self):
        """Test unpacking STAOutput as tuple."""
        output = STAOutput(u=7.5, state=(0.4, 0.5), history={}, sigma=0.2)

        u, state, history, sigma = output

        assert u == 7.5
        assert state == (0.4, 0.5)
        assert sigma == 0.2


# =====================================================================================
# Tests for HybridSTAOutput
# =====================================================================================

class TestHybridSTAOutput:
    """Test HybridSTAOutput NamedTuple."""

    def test_creation_with_all_fields(self):
        """Test creating HybridSTAOutput with all fields."""
        output = HybridSTAOutput(
            u=8.0,
            state=(0.5, 0.6, 0.7),
            history={'k1': [1.0, 1.1], 'k2': [2.0, 2.1]},
            sigma=0.15
        )

        assert output.u == 8.0
        assert output.state == (0.5, 0.6, 0.7)
        assert output.history == {'k1': [1.0, 1.1], 'k2': [2.0, 2.1]}
        assert output.sigma == 0.15

    def test_field_access_by_name(self):
        """Test accessing fields by name."""
        output = HybridSTAOutput(
            u=6.0,
            state=(1.0, 2.0, 3.0),
            history={},
            sigma=0.25
        )

        assert output.u == 6.0
        assert output.state == (1.0, 2.0, 3.0)
        assert output.sigma == 0.25

    def test_field_access_by_index(self):
        """Test tuple-like access by index."""
        output = HybridSTAOutput(
            u=9.0,
            state=(0.1, 0.2, 0.3),
            history={'test': 1},
            sigma=0.5
        )

        assert output[0] == 9.0
        assert output[1] == (0.1, 0.2, 0.3)
        assert output[2] == {'test': 1}
        assert output[3] == 0.5

    def test_immutability(self):
        """Test that HybridSTAOutput is immutable."""
        output = HybridSTAOutput(
            u=4.0,
            state=(0.0, 0.0, 0.0),
            history={},
            sigma=0.0
        )

        with pytest.raises(AttributeError):
            output.state = (1.0, 1.0, 1.0)

    def test_state_with_three_elements(self):
        """Test hybrid state with k1, k2, u_int."""
        output = HybridSTAOutput(
            u=12.0,
            state=(5.0, 10.0, 0.5),
            history={},
            sigma=0.1
        )

        # Hybrid typically has 3-element state (k1, k2, u_int)
        assert len(output.state) == 3
        k1, k2, u_int = output.state
        assert k1 == 5.0
        assert k2 == 10.0
        assert u_int == 0.5

    def test_large_adaptive_gains(self):
        """Test with large adaptive gain values."""
        output = HybridSTAOutput(
            u=15.0,
            state=(100.0, 200.0, 1.0),
            history={},
            sigma=0.0
        )

        assert output.state[0] == 100.0
        assert output.state[1] == 200.0

    def test_unpacking(self):
        """Test unpacking HybridSTAOutput as tuple."""
        output = HybridSTAOutput(
            u=11.0,
            state=(3.0, 4.0, 5.0),
            history={'data': [1, 2]},
            sigma=0.3
        )

        u, state, history, sigma = output

        assert u == 11.0
        assert state == (3.0, 4.0, 5.0)
        assert history == {'data': [1, 2]}
        assert sigma == 0.3


# =====================================================================================
# Integration Tests
# =====================================================================================

class TestControlOutputsIntegration:
    """Test integration scenarios and common properties."""

    def test_isinstance_namedtuple(self):
        """Test that all outputs are NamedTuples."""
        classical = ClassicalSMCOutput(u=1.0, state=(), history={})
        adaptive = AdaptiveSMCOutput(u=2.0, state=(0.0,), history={}, sigma=0.0)
        sta = STAOutput(u=3.0, state=(0.0, 0.0), history={}, sigma=0.0)
        hybrid = HybridSTAOutput(u=4.0, state=(0.0, 0.0, 0.0), history={}, sigma=0.0)

        # All should be tuples
        assert isinstance(classical, tuple)
        assert isinstance(adaptive, tuple)
        assert isinstance(sta, tuple)
        assert isinstance(hybrid, tuple)

    def test_length_consistency(self):
        """Test that each output type has consistent length."""
        classical = ClassicalSMCOutput(u=1.0, state=(), history={})
        adaptive = AdaptiveSMCOutput(u=2.0, state=(0.0,), history={}, sigma=0.0)
        sta = STAOutput(u=3.0, state=(0.0, 0.0), history={}, sigma=0.0)
        hybrid = HybridSTAOutput(u=4.0, state=(0.0, 0.0, 0.0), history={}, sigma=0.0)

        # Classical has 3 fields, others have 4
        assert len(classical) == 3
        assert len(adaptive) == 4
        assert len(sta) == 4
        assert len(hybrid) == 4

    def test_asdict_conversion(self):
        """Test _asdict() method for dictionary conversion."""
        output = AdaptiveSMCOutput(u=5.0, state=(1.0,), history={}, sigma=0.2)

        output_dict = output._asdict()

        assert output_dict == {
            'u': 5.0,
            'state': (1.0,),
            'history': {},
            'sigma': 0.2
        }

    def test_equality_comparison(self):
        """Test equality comparison between outputs."""
        output1 = ClassicalSMCOutput(u=10.0, state=(), history={})
        output2 = ClassicalSMCOutput(u=10.0, state=(), history={})
        output3 = ClassicalSMCOutput(u=5.0, state=(), history={})

        # Same values should be equal
        assert output1 == output2

        # Different values should not be equal
        assert output1 != output3

    def test_string_representation(self):
        """Test string representation of outputs."""
        output = STAOutput(u=7.0, state=(0.5, 0.6), history={}, sigma=0.3)

        str_repr = str(output)

        assert 'STAOutput' in str_repr
        assert '7.0' in str_repr
        assert '0.5' in str_repr

    def test_field_names_attribute(self):
        """Test _fields attribute for field names."""
        classical = ClassicalSMCOutput(u=1.0, state=(), history={})
        adaptive = AdaptiveSMCOutput(u=2.0, state=(0.0,), history={}, sigma=0.0)

        assert classical._fields == ('u', 'state', 'history')
        assert adaptive._fields == ('u', 'state', 'history', 'sigma')

    def test_make_constructor(self):
        """Test _make() constructor from iterable."""
        data = [10.0, (0.1, 0.2), {'key': 'value'}, 0.5]
        output = AdaptiveSMCOutput._make(data)

        assert output.u == 10.0
        assert output.state == (0.1, 0.2)
        assert output.history == {'key': 'value'}
        assert output.sigma == 0.5

    def test_replace_method(self):
        """Test _replace() method for creating modified copies."""
        original = ClassicalSMCOutput(u=5.0, state=(), history={})

        # Create modified copy
        modified = original._replace(u=10.0)

        assert original.u == 5.0  # Original unchanged
        assert modified.u == 10.0  # Modified copy changed
        assert modified.state == ()
        assert modified.history == {}
