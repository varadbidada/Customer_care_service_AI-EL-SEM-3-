#!/usr/bin/env python3
"""
Test script to demonstrate dataset functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_order_by_id, get_faq_answer, orders_df, faq_df

def test_datasets():
    """Test the dataset loading and helper functions"""
    
    print("=" * 60)
    print("🧪 TESTING DATASET FUNCTIONALITY")
    print("=" * 60)
    
    # Test dataset loading
    print(f"\n📊 DATASET STATISTICS:")
    print(f"   📦 Orders loaded: {len(orders_df)} records")
    print(f"   ❓ FAQ entries loaded: {len(faq_df)} records")
    
    # Test order lookup function
    print(f"\n🔍 TESTING ORDER LOOKUP:")
    test_orders = ["ORD54582", "ORD63640", "ORD99999", "123"]
    
    for order_id in test_orders:
        print(f"\n   Testing order: {order_id}")
        result = get_order_by_id(order_id)
        if result:
            print(f"   ✅ Found: {result['customer_name']} - {result['product']} ({result['status']})")
        else:
            print(f"   ❌ Not found")
    
    # Test FAQ function
    print(f"\n❓ TESTING FAQ LOOKUP:")
    test_questions = [
        "How can I track my order?",
        "I want to return an item",
        "Payment failed but money was deducted",
        "The app keeps crashing",
        "How do I apply a coupon?",
        "Random question that won't match"
    ]
    
    for question in test_questions:
        print(f"\n   Question: {question}")
        answer = get_faq_answer(question)
        if answer:
            print(f"   ✅ Answer: {answer[:100]}...")
        else:
            print(f"   ❌ No answer found")
    
    # Show sample data
    print(f"\n📋 SAMPLE ORDER DATA:")
    sample_orders = orders_df.head(3)
    for _, order in sample_orders.iterrows():
        print(f"   {order['order_id']}: {order['customer_name']} - {order['product']} ({order['status']})")
    
    print(f"\n📋 SAMPLE FAQ DATA:")
    sample_faqs = faq_df.head(3)
    for _, faq in sample_faqs.iterrows():
        print(f"   Q: {faq['question']}")
        print(f"   A: {faq['answer'][:80]}...")
        print()
    
    print("=" * 60)
    print("✅ DATASET TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_datasets()