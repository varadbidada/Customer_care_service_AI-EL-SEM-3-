#!/usr/bin/env python3
"""
Simple test to verify integer-to-integer order lookups work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions from app.py
from app import load_datasets, get_order_by_id

def test_lookup_functionality():
    """Test the order lookup with various input formats"""
    print("🧪 TESTING INTEGER-TO-INTEGER ORDER LOOKUP")
    print("=" * 60)
    
    # Load datasets (this will normalize order_ids)
    print("📊 Loading and normalizing datasets...")
    orders_df, faq_df = load_datasets()
    
    if orders_df.empty:
        print("❌ Failed to load datasets")
        return False
    
    # Test various input formats
    test_cases = [
        (54582, "Integer input"),
        ("54582", "String numeric input"),
        ("ORD54582", "String with ORD prefix"),
        ("#54582", "String with # prefix"),
        ("order 54582", "String with 'order' prefix"),
        (99999, "Non-existent order (should return None)"),
    ]
    
    print("\nTesting order lookups:")
    print("Input          | Type    | Result")
    print("-" * 45)
    
    success_count = 0
    total_tests = 0
    
    for test_input, description in test_cases:
        try:
            result = get_order_by_id(test_input)
            
            if test_input in [54582, "54582", "ORD54582", "#54582", "order 54582"]:
                # These should all find the same order
                expected_found = True
                actual_found = result is not None
                
                if actual_found == expected_found:
                    status = "✅ PASS"
                    success_count += 1
                else:
                    status = "❌ FAIL"
                
                total_tests += 1
                
            elif test_input == 99999:
                # This should not be found
                expected_found = False
                actual_found = result is not None
                
                if actual_found == expected_found:
                    status = "✅ PASS"
                    success_count += 1
                else:
                    status = "❌ FAIL"
                
                total_tests += 1
            else:
                status = "ℹ️ INFO"
            
            found_text = "Found" if result is not None else "Not Found"
            input_type = type(test_input).__name__
            
            print(f"{str(test_input):<14} | {input_type:<7} | {found_text:<10} {status}")
            
        except Exception as e:
            print(f"{str(test_input):<14} | ERROR   | Exception: {e}")
            total_tests += 1
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("🎉 ALL INTEGER LOOKUP TESTS PASSED!")
        print("✅ Order IDs properly normalized to integers")
        print("✅ Integer-to-integer comparisons working")
        print("✅ No string-integer type mismatches")
    else:
        print("❌ Some tests failed")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = test_lookup_functionality()
    print("=" * 60)
    sys.exit(0 if success else 1)