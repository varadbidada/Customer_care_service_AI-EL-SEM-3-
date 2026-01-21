#!/usr/bin/env python3
"""
Test dataset normalization and integer-to-integer order lookups
"""

import sys
import os
import pandas as pd
import json
import re

def load_and_normalize_datasets():
    """Test the dataset loading and normalization logic"""
    print("🧪 TESTING DATASET NORMALIZATION")
    print("=" * 50)
    
    try:
        # Load customer order dataset
        with open('datasets/customer_order_dataset.json', 'r') as f:
            orders_data = json.load(f)
        
        # Flatten the orders data
        flattened_orders = []
        for customer in orders_data:
            for order in customer['orders']:
                order_record = {
                    'customer_id': customer['customer_id'],
                    'customer_name': customer['name'],
                    'order_id': order['order_id'],
                    'product': order['product'],
                    'platform': order['platform'],
                    'status': order['status'],
                    'payment_mode': order['payment_mode'],
                    'amount': order['amount']
                }
                flattened_orders.append(order_record)
        
        orders_df = pd.DataFrame(flattened_orders)
        
        print(f"📊 Original dataset: {len(orders_df)} orders")
        print(f"📋 Sample order_ids: {orders_df['order_id'].head().tolist()}")
        
        # Normalize order_id column to integer
        def extract_numeric_order_id(order_id_str):
            """Extract numeric portion from order_id"""
            match = re.search(r'(\d+)', str(order_id_str))
            if match:
                return int(match.group(1))
            else:
                try:
                    return int(order_id_str)
                except (ValueError, TypeError):
                    return None
        
        # Add normalized integer order_id column
        orders_df['order_id_normalized'] = orders_df['order_id'].apply(extract_numeric_order_id)
        
        # Check normalization results
        print(f"🔢 Normalized order_ids: {orders_df['order_id_normalized'].head().tolist()}")
        print(f"📈 Data types:")
        print(f"   Original order_id: {orders_df['order_id'].dtype}")
        print(f"   Normalized order_id: {orders_df['order_id_normalized'].dtype}")
        
        # Remove any rows where normalization failed
        initial_count = len(orders_df)
        orders_df = orders_df.dropna(subset=['order_id_normalized'])
        orders_df['order_id_normalized'] = orders_df['order_id_normalized'].astype(int)
        final_count = len(orders_df)
        
        print(f"✅ Normalization complete: {final_count}/{initial_count} orders processed")
        
        return orders_df
        
    except Exception as e:
        print(f"❌ Error in normalization: {e}")
        return None

def test_integer_lookups(orders_df):
    """Test integer-to-integer order lookups"""
    print("\n🔍 TESTING INTEGER-TO-INTEGER LOOKUPS")
    print("=" * 50)
    
    def lookup_order_by_id(order_id, orders_df):
        """Test lookup function with integer comparison"""
        try:
            # Convert input to integer
            if isinstance(order_id, str):
                match = re.search(r'(\d+)', order_id)
                if match:
                    order_id_int = int(match.group(1))
                else:
                    order_id_int = int(order_id)
            else:
                order_id_int = order_id
            
            # Integer-to-integer comparison
            matching_orders = orders_df[orders_df['order_id_normalized'] == order_id_int]
            
            if not matching_orders.empty:
                return matching_orders.iloc[0].to_dict()
            else:
                return None
                
        except Exception as e:
            print(f"❌ Lookup error: {e}")
            return None
    
    # Test cases
    test_cases = [
        ("54582", "String input with numeric value"),
        (54582, "Integer input"),
        ("ORD54582", "String input with ORD prefix"),
        ("#54582", "String input with # prefix"),
        ("order 54582", "String input with 'order' prefix"),
        (99999, "Non-existent order ID"),
        ("invalid", "Invalid input")
    ]
    
    print("Test Input       | Type    | Found | Status")
    print("-" * 50)
    
    success_count = 0
    
    for test_input, description in test_cases:
        try:
            result = lookup_order_by_id(test_input, orders_df)
            found = result is not None
            
            if test_input in ["54582", 54582, "ORD54582", "#54582", "order 54582"]:
                # These should all find the same order
                expected = True
                status = "✅ PASS" if found == expected else "❌ FAIL"
                if found == expected:
                    success_count += 1
            elif test_input == 99999:
                # This should not be found
                expected = False
                status = "✅ PASS" if found == expected else "❌ FAIL"
                if found == expected:
                    success_count += 1
            elif test_input == "invalid":
                # This should handle gracefully
                expected = False
                status = "✅ PASS" if found == expected else "❌ FAIL"
                if found == expected:
                    success_count += 1
            else:
                status = "❓ INFO"
            
            input_type = type(test_input).__name__
            print(f"{str(test_input):<16} | {input_type:<7} | {found:<5} | {status}")
            
        except Exception as e:
            print(f"{str(test_input):<16} | ERROR   | False | ❌ EXCEPTION: {e}")
    
    print(f"\n✅ Lookup tests passed: {success_count}/6")
    return success_count == 6

def test_type_consistency():
    """Test that all comparisons are integer-to-integer"""
    print("\n🔢 TESTING TYPE CONSISTENCY")
    print("=" * 50)
    
    # Sample data
    sample_data = {
        'order_id': ['ORD12345', 'ORD67890', 'ORD11111'],
        'product': ['Product A', 'Product B', 'Product C']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Apply normalization
    def extract_numeric_order_id(order_id_str):
        match = re.search(r'(\d+)', str(order_id_str))
        return int(match.group(1)) if match else None
    
    df['order_id_normalized'] = df['order_id'].apply(extract_numeric_order_id)
    df['order_id_normalized'] = df['order_id_normalized'].astype(int)
    
    print(f"Original types: {df['order_id'].dtype}")
    print(f"Normalized types: {df['order_id_normalized'].dtype}")
    
    # Test lookup
    lookup_id = 12345
    result = df[df['order_id_normalized'] == lookup_id]
    
    found = not result.empty
    print(f"Lookup {lookup_id} (int) in normalized column: {'✅ FOUND' if found else '❌ NOT FOUND'}")
    
    return found

def main():
    """Run all normalization tests"""
    print("🧪 DATASET NORMALIZATION AND INTEGER LOOKUP VALIDATION")
    print("=" * 70)
    
    # Test 1: Dataset normalization
    orders_df = load_and_normalize_datasets()
    if orders_df is None:
        print("❌ Dataset normalization failed")
        return False
    
    # Test 2: Integer lookups
    lookups_passed = test_integer_lookups(orders_df)
    
    # Test 3: Type consistency
    types_consistent = test_type_consistency()
    
    # Summary
    print("\n" + "=" * 70)
    print("🏁 NORMALIZATION TEST RESULTS")
    print("=" * 70)
    
    print(f"✅ Dataset normalization: {'PASS' if orders_df is not None else 'FAIL'}")
    print(f"✅ Integer-to-integer lookups: {'PASS' if lookups_passed else 'FAIL'}")
    print(f"✅ Type consistency: {'PASS' if types_consistent else 'FAIL'}")
    
    all_passed = orders_df is not None and lookups_passed and types_consistent
    
    if all_passed:
        print("\n🎉 ALL NORMALIZATION TESTS PASSED!")
        print("✅ Order IDs normalized to integers on load")
        print("✅ All lookups use integer-to-integer comparison")
        print("✅ No string-integer type mismatches")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)