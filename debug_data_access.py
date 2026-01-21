#!/usr/bin/env python3
"""
Debug the data access function to see what's happening
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_data_access():
    """Test the data access function with actual order IDs"""
    print("🔍 DEBUGGING DATA ACCESS FUNCTION")
    print("=" * 50)
    
    try:
        from data.order_data_access import get_order_by_id
        
        # Test with actual order IDs from the dataset
        test_order_ids = [
            54582,  # Should exist (ORD54582)
            63640,  # Should exist (ORD63640) 
            90495,  # Should exist (ORD90495)
            89,     # User tried this - should not exist
            654,    # User tried this - should not exist
        ]
        
        for order_id in test_order_ids:
            print(f"\n--- Testing order ID: {order_id} ---")
            try:
                order = get_order_by_id(order_id)
                if order:
                    print(f"✅ FOUND: {order}")
                else:
                    print(f"❌ NOT FOUND: None returned")
            except Exception as e:
                print(f"💥 ERROR: {e}")
                import traceback
                traceback.print_exc()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ General error: {e}")
        import traceback
        traceback.print_exc()

def test_dataset_loading():
    """Test if the dataset loads correctly"""
    print("\n📊 TESTING DATASET LOADING")
    print("=" * 50)
    
    try:
        import json
        from pathlib import Path
        
        dataset_path = Path(__file__).resolve().parent / "datasets" / "customer_order_dataset.json"
        print(f"Dataset path: {dataset_path}")
        print(f"File exists: {dataset_path.exists()}")
        
        if dataset_path.exists():
            with open(dataset_path, "r", encoding="utf-8") as f:
                orders = json.load(f)
            
            print(f"Dataset loaded: {len(orders)} customers")
            
            # Show first few orders
            for i, customer in enumerate(orders[:2]):
                print(f"\nCustomer {i+1}: {customer.get('name')}")
                for order in customer.get('orders', [])[:2]:
                    order_id = order.get('order_id')
                    product = order.get('product')
                    status = order.get('status')
                    print(f"  Order: {order_id} - {product} - {status}")
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dataset_loading()
    test_data_access()