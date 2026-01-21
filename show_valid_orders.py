#!/usr/bin/env python3
"""
Show what order IDs actually exist in the dataset
"""

import json
import re
from pathlib import Path

# Load the dataset
dataset_path = Path(__file__).resolve().parent / "datasets" / "customer_order_dataset.json"

try:
    with open(dataset_path, "r", encoding="utf-8") as f:
        orders = json.load(f)
    
    print("📋 VALID ORDER IDs IN DATASET:")
    print("=" * 50)
    
    for customer in orders:
        customer_name = customer.get('name')
        print(f"\n👤 Customer: {customer_name}")
        
        for order in customer.get('orders', []):
            order_id = order.get('order_id')
            product = order.get('product')
            status = order.get('status')
            
            # Extract numeric portion
            match = re.search(r'(\d+)', order_id)
            if match:
                numeric_id = match.group(1)
                print(f"   📦 {order_id} → {numeric_id} | {product} | {status}")
    
    print("\n" + "=" * 50)
    print("💡 TESTING INSTRUCTIONS:")
    print("Try these order IDs in the chatbot:")
    print("- 54582 (should find Groceries)")
    print("- 63640 (should find Shoes)")  
    print("- 90495 (should find Burger)")
    print("- 99999 (should return 'order not found')")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()