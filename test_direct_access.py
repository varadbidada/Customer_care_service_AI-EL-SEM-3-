#!/usr/bin/env python3
"""
Test the data access function directly
"""

import json
from pathlib import Path

# Test the exact same code as in order_data_access.py
DATASET_PATH = Path(__file__).resolve().parent / "datasets" / "customer_order_dataset.json"

print(f"Dataset path: {DATASET_PATH}")
print(f"File exists: {DATASET_PATH.exists()}")

try:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        ORDERS = json.load(f)
    
    print(f"Loaded {len(ORDERS)} customers")
    
    def get_order_by_id(order_id: int):
        print(f"Looking for order ID: {order_id}")
        for customer in ORDERS:
            print(f"  Checking customer: {customer.get('name')}")
            for order in customer.get("orders", []):
                print(f"    Checking order: {order.get('order_id')}")
                try:
                    # Extract numeric portion from order_id (e.g., "ORD54582" -> 54582)
                    order_id_str = str(order.get("order_id", ""))
                    import re
                    match = re.search(r'(\d+)', order_id_str)
                    if match:
                        order_numeric_id = int(match.group(1))
                        print(f"      Extracted numeric ID: {order_numeric_id}")
                        if order_numeric_id == int(order_id):
                            print(f"      MATCH FOUND!")
                            # Add customer info to the order
                            order_with_customer = order.copy()
                            order_with_customer['customer_name'] = customer.get('name')
                            order_with_customer['customer_id'] = customer.get('customer_id')
                            return order_with_customer
                except (ValueError, TypeError) as e:
                    print(f"      Error: {e}")
                    continue
        print("  No match found")
        return None
    
    # Test with actual order IDs
    test_ids = [54582, 63640, 89, 654]
    
    for test_id in test_ids:
        print(f"\n=== Testing order ID: {test_id} ===")
        result = get_order_by_id(test_id)
        if result:
            print(f"✅ FOUND: {result['product']} - {result['status']}")
        else:
            print(f"❌ NOT FOUND")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()