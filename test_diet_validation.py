#!/usr/bin/env python3
"""
Test script to verify the new diet validation logic.
Tests that the system now validates user foods instead of auto-completing.
"""

import sys
import os
sys.path.append('/app/backend')

from diet_service import validate_user_foods

def test_insufficient_foods():
    """Test that validation fails when user has insufficient foods"""
    print("🧪 Testing insufficient foods...")
    
    # Test with only protein, missing other categories
    preferred = {"frango"}  # Only protein
    restrictions = []
    
    available, is_valid, error_msg = validate_user_foods(preferred, restrictions)
    
    print(f"Available foods: {available}")
    print(f"Is valid: {is_valid}")
    print(f"Error message: {error_msg}")
    
    assert not is_valid, "Should be invalid with insufficient foods"
    assert "CARBOIDRATO" in error_msg, "Should mention missing carbs"
    assert "GORDURA" in error_msg, "Should mention missing fats"
    assert "FRUTA" in error_msg, "Should mention missing fruits"
    
    print("✅ Test passed: Correctly identifies insufficient foods\n")

def test_sufficient_foods():
    """Test that validation passes when user has sufficient foods"""
    print("🧪 Testing sufficient foods...")
    
    # Test with all required categories
    preferred = {
        "frango",        # protein
        "arroz_branco",  # carb
        "azeite",        # fat
        "banana"         # fruit
    }
    restrictions = []
    
    available, is_valid, error_msg = validate_user_foods(preferred, restrictions)
    
    print(f"Available foods: {available}")
    print(f"Is valid: {is_valid}")
    print(f"Error message: {error_msg}")
    
    assert is_valid, "Should be valid with sufficient foods"
    assert error_msg is None, "Should have no error message"
    
    print("✅ Test passed: Correctly validates sufficient foods\n")

def test_with_restrictions():
    """Test that validation works with dietary restrictions"""
    print("🧪 Testing with dietary restrictions...")
    
    # Test vegetarian restriction
    preferred = {
        "frango",        # protein (will be excluded)
        "ovos",          # protein (allowed)
        "arroz_branco",  # carb
        "azeite",        # fat
        "banana"         # fruit
    }
    restrictions = ["Vegetariano"]
    
    available, is_valid, error_msg = validate_user_foods(preferred, restrictions)
    
    print(f"Available foods: {available}")
    print(f"Is valid: {is_valid}")
    print(f"Error message: {error_msg}")
    
    # Should still be valid because eggs are allowed for vegetarians
    assert is_valid, "Should be valid with eggs as protein for vegetarians"
    assert "frango" not in available, "Chicken should be excluded for vegetarians"
    assert "ovos" in available, "Eggs should be allowed for vegetarians"
    
    print("✅ Test passed: Correctly handles dietary restrictions\n")

if __name__ == "__main__":
    print("🚀 Starting diet validation tests...\n")
    
    try:
        test_insufficient_foods()
        test_sufficient_foods()
        test_with_restrictions()
        
        print("🎉 All tests passed! The new validation logic is working correctly.")
        print("✅ System now validates user foods instead of auto-completing.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)