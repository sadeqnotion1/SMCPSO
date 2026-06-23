#!/usr/bin/env python
"""
Factory Registry Module Tests - Week 3 Session 6

PURPOSE: Unit tests for factory registry functions (pure functions, high coverage value)
COVERAGE TARGET: 80-90% of registry.py (318 lines)
STRATEGY: Test all public registry functions + critical metadata access

TEST MATRIX:
1. Registry Access Functions (get_controller_info, validate, etc.)
2. Default Gains and Bounds Retrieval (PSO integration)
3. Controller Filtering (by category, complexity)
4. Controller Normalization (alias resolution)
5. Error Handling (invalid types, unknown controllers)
6. Registry Consistency (metadata structure validation)

Author: Claude Code (Week 3 Session 6)
Date: December 2025
"""

import pytest
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Import registry functions
from src.controllers.factory.registry import (
    get_controller_info,
    get_default_gains,
    get_gain_bounds,
    canonicalize_controller_type,
    list_available_controllers,
    list_all_controllers,
    get_controllers_by_category,
    get_controllers_by_complexity,
    validate_controller_type,
    CONTROLLER_REGISTRY,
    CONTROLLER_ALIASES,
)

# ==============================================================================
# Test Registry Access Functions
# ==============================================================================

class TestGetControllerInfo:
    """Test get_controller_info function"""

    @pytest.mark.parametrize("controller_type", [
        "classical_smc",
        "sta_smc",
        "adaptive_smc",
        "hybrid_adaptive_sta_smc",
    ])
    def test_get_info_all_controllers(self, controller_type):
        """Test retrieving info for all registered controllers"""
        info = get_controller_info(controller_type)

        # Verify required keys present
        assert 'class' in info, f"{controller_type} missing 'class'"
        assert 'config_class' in info, f"{controller_type} missing 'config_class'"
        assert 'default_gains' in info, f"{controller_type} missing 'default_gains'"
        assert 'gain_count' in info, f"{controller_type} missing 'gain_count'"
        assert 'description' in info, f"{controller_type} missing 'description'"

    def test_get_info_returns_copy(self):
        """Test that get_controller_info returns a copy (not reference)"""
        info1 = get_controller_info('classical_smc')
        info2 = get_controller_info('classical_smc')

        # Modifying info1 should not affect info2
        info1['test_key'] = 'test_value'
        assert 'test_key' not in info2, "get_controller_info should return copy, not reference"

    def test_get_info_invalid_type_raises_value_error(self):
        """Test that invalid controller type raises ValueError"""
        with pytest.raises(ValueError, match="Unknown controller type"):
            get_controller_info('nonexistent_controller')

    def test_get_info_non_string_raises_type_error(self):
        """Test that non-string input raises TypeError"""
        with pytest.raises(TypeError, match="Controller type must be string"):
            get_controller_info(123)

    def test_get_info_metadata_consistency(self):
        """Test that controller info has consistent metadata structure"""
        for controller_type in CONTROLLER_REGISTRY.keys():
            info = get_controller_info(controller_type)

            # All controllers should have these fields
            assert isinstance(info['default_gains'], list), f"{controller_type} default_gains not a list"
            assert isinstance(info['gain_count'], int), f"{controller_type} gain_count not an int"
            assert isinstance(info['description'], str), f"{controller_type} description not a string"

            # Verify gain_count matches default_gains length
            assert len(info['default_gains']) == info['gain_count'], \
                f"{controller_type} gain_count mismatch: {len(info['default_gains'])} vs {info['gain_count']}"


# ==============================================================================
# Test Default Gains and Bounds
# ==============================================================================

class TestDefaultGainsAndBounds:
    """Test default gains and gain bounds retrieval"""

    @pytest.mark.parametrize("controller_type,expected_count", [
        ("classical_smc", 6),
        ("sta_smc", 6),
        ("adaptive_smc", 5),
        ("hybrid_adaptive_sta_smc", 4),
    ])
    def test_get_default_gains(self, controller_type, expected_count):
        """Test retrieving default gains for all controllers"""
        gains = get_default_gains(controller_type)

        assert isinstance(gains, list), f"{controller_type} gains not a list"
        assert len(gains) == expected_count, \
            f"{controller_type} expected {expected_count} gains, got {len(gains)}"
        assert all(isinstance(g, (int, float)) for g in gains), \
            f"{controller_type} gains contain non-numeric values"

    def test_get_default_gains_returns_copy(self):
        """Test that get_default_gains returns a copy"""
        gains1 = get_default_gains('classical_smc')
        gains2 = get_default_gains('classical_smc')

        # Modifying gains1 should not affect gains2
        gains1[0] = 999.0
        assert gains2[0] != 999.0, "get_default_gains should return copy"

    @pytest.mark.parametrize("controller_type,expected_count", [
        ("classical_smc", 6),
        ("sta_smc", 6),
        ("adaptive_smc", 5),
        ("hybrid_adaptive_sta_smc", 4),
    ])
    def test_get_gain_bounds(self, controller_type, expected_count):
        """Test retrieving gain bounds for PSO integration"""
        bounds = get_gain_bounds(controller_type)

        assert isinstance(bounds, list), f"{controller_type} bounds not a list"
        assert len(bounds) == expected_count, \
            f"{controller_type} expected {expected_count} bounds, got {len(bounds)}"

        # Each bound should be (min, max) tuple with min < max
        for i, (min_val, max_val) in enumerate(bounds):
            assert min_val < max_val, \
                f"{controller_type} bound {i}: min {min_val} >= max {max_val}"
            assert min_val > 0, \
                f"{controller_type} bound {i}: min {min_val} must be positive"

    def test_get_gain_bounds_returns_copy(self):
        """Test that get_gain_bounds returns a copy"""
        bounds1 = get_gain_bounds('classical_smc')
        bounds2 = get_gain_bounds('classical_smc')

        # Modifying bounds1 should not affect bounds2
        bounds1[0] = (999.0, 1000.0)
        assert bounds2[0] != (999.0, 1000.0), "get_gain_bounds should return copy"

    def test_default_gains_within_bounds(self):
        """Test that default gains are within bounds (sanity check)"""
        for controller_type in ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']:
            gains = get_default_gains(controller_type)
            bounds = get_gain_bounds(controller_type)

            for i, (gain, (min_val, max_val)) in enumerate(zip(gains, bounds)):
                assert min_val <= gain <= max_val, \
                    f"{controller_type} default gain {i} ({gain}) outside bounds [{min_val}, {max_val}]"


# ==============================================================================
# Test Controller Normalization
# ==============================================================================

class TestCanonicalizeControllerType:
    """Test controller type normalization and alias resolution"""

    @pytest.mark.parametrize("alias,expected", [
        ("classic_smc", "classical_smc"),
        ("smc_classical", "classical_smc"),
        ("super_twisting", "sta_smc"),
        ("sta", "sta_smc"),
        ("adaptive", "adaptive_smc"),
        ("hybrid", "hybrid_adaptive_sta_smc"),
        ("hybrid_sta", "hybrid_adaptive_sta_smc"),
    ])
    def test_canonicalize_known_aliases(self, alias, expected):
        """Test that known aliases are correctly canonicalized"""
        result = canonicalize_controller_type(alias)
        assert result == expected, f"Alias '{alias}' should resolve to '{expected}', got '{result}'"

    def test_canonicalize_canonical_name_unchanged(self):
        """Test that canonical names remain unchanged"""
        for canonical in ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']:
            result = canonicalize_controller_type(canonical)
            assert result == canonical, f"Canonical name '{canonical}' should remain unchanged"

    def test_canonicalize_case_insensitive(self):
        """Test that canonicalization is case-insensitive"""
        assert canonicalize_controller_type('CLASSICAL_SMC') == 'classical_smc'
        assert canonicalize_controller_type('Classical_SMC') == 'classical_smc'
        assert canonicalize_controller_type('classical_smc') == 'classical_smc'

    def test_canonicalize_whitespace_handling(self):
        """Test that whitespace is handled correctly"""
        assert canonicalize_controller_type('  classical_smc  ') == 'classical_smc'
        assert canonicalize_controller_type('classical smc') == 'classical_smc'

    def test_canonicalize_hyphen_to_underscore(self):
        """Test that hyphens are converted to underscores"""
        assert canonicalize_controller_type('classical-smc') == 'classical_smc'
        assert canonicalize_controller_type('hybrid-adaptive-sta-smc') == 'hybrid_adaptive_sta_smc'

    def test_canonicalize_non_string_raises_value_error(self):
        """Test that non-string input raises ValueError"""
        with pytest.raises(ValueError, match="Controller type must be string"):
            canonicalize_controller_type(123)

    def test_canonicalize_empty_string_raises_value_error(self):
        """Test that empty string raises ValueError"""
        with pytest.raises(ValueError, match="Controller type cannot be empty"):
            canonicalize_controller_type('')

        with pytest.raises(ValueError, match="Controller type cannot be empty"):
            canonicalize_controller_type('   ')


# ==============================================================================
# Test Controller Listing and Filtering
# ==============================================================================

class TestListControllers:
    """Test controller listing and filtering functions"""

    def test_list_available_controllers(self):
        """Test listing all available controllers"""
        controllers = list_available_controllers()

        assert isinstance(controllers, list), "list_available_controllers should return list"
        assert len(controllers) >= 4, "Should have at least 4 controllers (classical, sta, adaptive, hybrid)"
        assert all(isinstance(c, str) for c in controllers), "All controller names should be strings"

        # Check for expected controllers
        expected = ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']
        for controller in expected:
            assert controller in controllers, f"Expected controller '{controller}' not in list"

    def test_list_all_controllers(self):
        """Test list_all_controllers (should match list_available_controllers)"""
        available = list_available_controllers()
        all_controllers = list_all_controllers()

        assert available == all_controllers, \
            "list_available_controllers and list_all_controllers should return same result"

    def test_list_sorted_alphabetically(self):
        """Test that controller list is sorted"""
        controllers = list_available_controllers()

        assert controllers == sorted(controllers), \
            "Controller list should be sorted alphabetically"

    @pytest.mark.parametrize("category,expected_controllers", [
        ("classical", ["classical_smc"]),
        ("advanced", ["sta_smc"]),
        ("adaptive", ["adaptive_smc"]),
        ("hybrid", ["hybrid_adaptive_sta_smc"]),
    ])
    def test_get_controllers_by_category(self, category, expected_controllers):
        """Test filtering controllers by category"""
        controllers = get_controllers_by_category(category)

        assert isinstance(controllers, list), f"Category '{category}' should return list"
        for expected in expected_controllers:
            assert expected in controllers, \
                f"Controller '{expected}' should be in category '{category}'"

    @pytest.mark.parametrize("complexity,min_count", [
        ("medium", 1),      # At least classical_smc
        ("high", 2),        # At least sta_smc, adaptive_smc
        ("very_high", 1),   # At least hybrid_adaptive_sta_smc
    ])
    def test_get_controllers_by_complexity(self, complexity, min_count):
        """Test filtering controllers by complexity"""
        controllers = get_controllers_by_complexity(complexity)

        assert isinstance(controllers, list), f"Complexity '{complexity}' should return list"
        assert len(controllers) >= min_count, \
            f"Complexity '{complexity}' should have at least {min_count} controller(s)"

    def test_get_controllers_by_category_empty(self):
        """Test that non-existent category returns empty list"""
        controllers = get_controllers_by_category('nonexistent')
        assert controllers == [], "Non-existent category should return empty list"

    def test_get_controllers_by_complexity_empty(self):
        """Test that non-existent complexity returns empty list"""
        controllers = get_controllers_by_complexity('nonexistent')
        assert controllers == [], "Non-existent complexity should return empty list"


# ==============================================================================
# Test Controller Validation
# ==============================================================================

class TestValidateControllerType:
    """Test controller type validation"""

    @pytest.mark.parametrize("controller_type", [
        "classical_smc",
        "sta_smc",
        "adaptive_smc",
        "hybrid_adaptive_sta_smc",
    ])
    def test_validate_registered_controllers(self, controller_type):
        """Test that registered controllers are valid"""
        assert validate_controller_type(controller_type) is True, \
            f"Registered controller '{controller_type}' should be valid"

    @pytest.mark.parametrize("alias", [
        "classic_smc",
        "super_twisting",
        "adaptive",
        "hybrid",
    ])
    def test_validate_aliases(self, alias):
        """Test that aliases are recognized as valid"""
        assert validate_controller_type(alias) is True, \
            f"Alias '{alias}' should be valid"

    @pytest.mark.parametrize("invalid_type", [
        "nonexistent_controller",
        "invalid_smc",
        "random_name",
        "",
    ])
    def test_validate_invalid_types(self, invalid_type):
        """Test that invalid types return False"""
        assert validate_controller_type(invalid_type) is False, \
            f"Invalid type '{invalid_type}' should be invalid"

    def test_validate_non_string_returns_false(self):
        """Test that non-string input returns False (not exception)"""
        assert validate_controller_type(123) is False
        assert validate_controller_type(None) is False
        assert validate_controller_type(['classical_smc']) is False


# ==============================================================================
# Test Registry Consistency
# ==============================================================================

class TestRegistryConsistency:
    """Test registry metadata consistency and integrity"""

    def test_all_controllers_have_required_fields(self):
        """Test that all controllers have required metadata fields"""
        required_fields = [
            'class', 'config_class', 'default_gains', 'gain_count',
            'gain_structure', 'description', 'supports_dynamics',
            'required_params', 'gain_bounds', 'stability_margin',
            'category', 'complexity'
        ]

        for controller_type, info in CONTROLLER_REGISTRY.items():
            for field in required_fields:
                assert field in info, \
                    f"Controller '{controller_type}' missing required field '{field}'"

    def test_gain_count_matches_default_gains(self):
        """Test that gain_count matches length of default_gains"""
        for controller_type, info in CONTROLLER_REGISTRY.items():
            assert len(info['default_gains']) == info['gain_count'], \
                f"Controller '{controller_type}' gain_count mismatch"

    def test_gain_bounds_match_gain_count(self):
        """Test that gain_bounds length matches gain_count"""
        for controller_type, info in CONTROLLER_REGISTRY.items():
            if info['gain_count'] > 0:  # Only check controllers with gains
                assert len(info['gain_bounds']) == info['gain_count'], \
                    f"Controller '{controller_type}' gain_bounds length mismatch"

    def test_default_gains_are_positive(self):
        """Test that all default gains are positive"""
        for controller_type, info in CONTROLLER_REGISTRY.items():
            for i, gain in enumerate(info['default_gains']):
                assert gain > 0, \
                    f"Controller '{controller_type}' default gain {i} ({gain}) must be positive"

    def test_all_aliases_resolve_to_registered_controllers(self):
        """Test that all aliases resolve to registered controllers"""
        for alias, canonical in CONTROLLER_ALIASES.items():
            assert canonical in CONTROLLER_REGISTRY, \
                f"Alias '{alias}' resolves to unregistered controller '{canonical}'"

    def test_controller_classes_are_not_none(self):
        """Test that all controller classes are defined (not None)"""
        for controller_type, info in CONTROLLER_REGISTRY.items():
            # Skip MPC if not available (optional dependency)
            if controller_type == 'mpc_controller':
                continue
            assert info['class'] is not None, \
                f"Controller '{controller_type}' class is None"


# ==============================================================================
# Summary Test
# ==============================================================================

@pytest.mark.unit
def test_registry_summary():
    """Print summary of registry test coverage"""
    print("\n" + "=" * 80)
    print(" Factory Registry Tests - Week 3 Session 6")
    print("=" * 80)
    print(f" Module: src/controllers/factory/registry.py (318 lines)")
    print(f" Functions Tested: 9/9 (100% of public API)")
    print("-" * 80)
    print(" Test Suites:")
    print("   1. Registry Access Functions (get_controller_info, etc.)")
    print("   2. Default Gains and Bounds (PSO integration)")
    print("   3. Controller Normalization (alias resolution)")
    print("   4. Controller Listing and Filtering (category, complexity)")
    print("   5. Controller Validation (type checking)")
    print("   6. Registry Consistency (metadata integrity)")
    print("-" * 80)
    print(" Coverage Strategy:")
    print("   - Public API: 100% (all user-facing functions)")
    print("   - Edge cases: Empty strings, non-strings, invalid types")
    print("   - Data integrity: Gain counts, bounds, defaults")
    print("   - Metadata: Categories, complexity, required fields")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
