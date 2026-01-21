# Main_EL_3/data/order_data_access.py
import json
from pathlib import Path

DATASET_PATH = Path(__file__).resolve().parent.parent / "datasets" / "customer_order_dataset.json"

print(f"🔍 Loading dataset from: {DATASET_PATH}")

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    ORDERS = json.load(f)

print(f"✅ Dataset loaded: {len(ORDERS)} customers")

def get_order_by_id(order_id: int):
    print(f"🔍 Looking up order ID: {order_id}")
    
    for customer in ORDERS:
        for order in customer.get("orders", []):
            try:
                # Extract numeric portion from order_id (e.g., "ORD54582" -> 54582)
                order_id_str = str(order.get("order_id", ""))
                import re
                match = re.search(r'(\d+)', order_id_str)
                if match:
                    order_numeric_id = int(match.group(1))
                    if order_numeric_id == int(order_id):
                        # Add customer info to the order
                        order_with_customer = order.copy()
                        order_with_customer['customer_name'] = customer.get('name')
                        order_with_customer['customer_id'] = customer.get('customer_id')
                        print(f"✅ Found order {order_id}: {order_with_customer['product']} - {order_with_customer['status']}")
                        return order_with_customer
            except (ValueError, TypeError):
                continue
    
    print(f"❌ Order {order_id} not found in dataset")
    return None