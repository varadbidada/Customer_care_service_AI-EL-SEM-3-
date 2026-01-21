#!/usr/bin/env python3
"""
Simple validation script for order ID extraction fix
"""

import re

def extract_order_id_fixed(message: str):
    """
    FIXED: Extract order ID using the MANDATORY regex pattern.
    Accept ALL formats: "45", "ORD45", "#45", "order 45"
    Extract ONLY the numeric portion and return as integer.
    """
    # STRICT RULE: Extract FIRST numeric sequence from ANY format
    match = re.search(r'(\d+)', message)
    if match:
        order_id = int(match.group(1))
        print(f"📋 Extracted order ID: {order_id} from input: '{message}'")
        return order_id
    
    print(f"❌ No numeric order ID found in: '{message}'")
    return None

def test_extraction():
    """Test the mandatory order ID extraction patterns"""
    print("🧪 TESTING ORDER ID EXTRACTION FIX")
    print("=" * 50)
    
    # Test cases as specified in requirements
    test_cases = [
        ("45", 45),
        ("ORD45", 45),
        ("#45", 45),
        ("order 45", 45),
        ("My order number is 123", 123),
        ("It's #123", 123),
        ("ORD123", 123),
        ("no numbers here", None),
        ("", None)
    ]
    
    all_passed = True
    
    for input_text, expected in test_cases:
        result = extract_order_id_fixed(input_text)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} Input: '{input_text}' → Expected: {expected}, Got: {result}")
        
        if result != expected:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL ORDER ID EXTRACTION TESTS PASSED!")
        print("✅ Regex pattern r'(\\d+)' works correctly")
        print("✅ Accepts: '45', 'ORD45', '#45', 'order 45'")
        print("✅ Extracts numeric portion only")
    else:
        print("❌ SOME TESTS FAILED")
    
    return all_passed

if __name__ == "__main__":
    test_extraction()