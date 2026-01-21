#!/usr/bin/env python3
"""
Demo script showing customer lookup functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.dialogue_state_manager import DialogueStateManager
from data.enhanced_data_access import get_order_by_id, get_enhanced_faq_answer
from memory.session_manager import SessionManager

def demo_customer_lookup():
    """Demo the customer lookup functionality with various scenarios"""
    
    print("🎯 CUSTOMER LOOKUP FUNCTIONALITY DEMO")
    print("=" * 60)
    
    # Initialize components
    dialogue_manager = DialogueStateManager()
    session_manager = SessionManager(storage_type='memory')
    
    # Test scenarios
    scenarios = [
        {
            "name": "Direct Customer ID Query",
            "message": "i want details regarding customer_id CUST000714",
            "expected": "Should provide comprehensive customer details"
        },
        {
            "name": "Customer Details Request",
            "message": "show me customer details for CUST000714",
            "expected": "Should provide customer information"
        },
        {
            "name": "Invalid Customer ID",
            "message": "customer details for CUST999999",
            "expected": "Should ask for valid customer ID"
        },
        {
            "name": "Customer Query Without ID",
            "message": "I need customer information",
            "expected": "Should ask for customer ID"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 Scenario {i}: {scenario['name']}")
        print("-" * 40)
        print(f"📝 Message: '{scenario['message']}'")
        print(f"🎯 Expected: {scenario['expected']}")
        
        # Create fresh session for each scenario
        session = session_manager.get_session(f'demo_session_{i}')
        
        try:
            result = dialogue_manager.process_message(
                scenario['message'], 
                session, 
                get_order_by_id, 
                get_enhanced_faq_answer
            )
            
            print(f"🤖 Response:")
            response = result.get('response', 'No response')
            # Truncate long responses for demo
            if len(response) > 200:
                print(f"{response[:200]}...")
            else:
                print(response)
            
            print(f"📊 State: {result.get('conversation_state', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

def show_sample_customers():
    """Show some sample customers available for testing"""
    
    print("👥 SAMPLE CUSTOMERS FOR TESTING")
    print("=" * 60)
    
    from data.enhanced_data_access import enhanced_data_access
    
    # Show first few customers
    sample_customers = enhanced_data_access.orders_data[:5]
    
    for customer in sample_customers:
        customer_id = customer.get('customer_id')
        name = customer.get('name')
        order_count = len(customer.get('orders', []))
        
        print(f"🆔 {customer_id} - {name} ({order_count} orders)")
        
        # Show first order as example
        if customer.get('orders'):
            first_order = customer['orders'][0]
            print(f"   📦 Sample Order: {first_order.get('product')} - ₹{first_order.get('amount', 0):,} ({first_order.get('status')})")
    
    print(f"\n💡 Try asking: 'customer details for CUST000714' or 'show me customer CUST0001'")

if __name__ == "__main__":
    show_sample_customers()
    demo_customer_lookup()