#!/usr/bin/env python3
"""
Test script for customer lookup functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.dialogue_state_manager import DialogueStateManager, DialogueState
from data.enhanced_data_access import get_order_by_id, get_enhanced_faq_answer
from memory.session_manager import SessionManager

def test_customer_lookup():
    """Test the complete customer lookup workflow"""
    
    print("🧪 Testing Customer Lookup Functionality")
    print("=" * 50)
    
    # Initialize components
    dialogue_manager = DialogueStateManager()
    session_manager = SessionManager(storage_type='memory')
    
    # Create a test session
    session = session_manager.get_session('test_session_001')
    
    # Test message from user
    test_message = "i want details regarding customer_id CUST000714"
    
    print(f"📝 Test Message: '{test_message}'")
    print()
    
    # Process the message through dialogue manager
    try:
        result = dialogue_manager.process_message(
            test_message, 
            session, 
            get_order_by_id, 
            get_enhanced_faq_answer
        )
        
        print("✅ Dialogue Manager Response:")
        print(f"Response: {result.get('response', 'No response')}")
        print(f"Conversation State: {result.get('conversation_state', 'Unknown')}")
        print(f"Is Human Flow: {result.get('is_human_flow', False)}")
        print()
        
        # Check dialogue state
        dialogue_state = dialogue_manager.get_dialogue_state(session)
        print("📊 Dialogue State:")
        print(f"Active Intent: {dialogue_state.active_intent}")
        print(f"Pending Slot: {dialogue_state.pending_slot}")
        print(f"Context: {dialogue_state.context}")
        print(f"Workflow Completed: {dialogue_state.workflow_completed}")
        
    except Exception as e:
        print(f"❌ Error in dialogue processing: {e}")
        import traceback
        traceback.print_exc()

def test_customer_lookup_direct():
    """Test direct customer lookup"""
    
    print("\n🔍 Testing Direct Customer Lookup")
    print("=" * 50)
    
    from data.enhanced_data_access import get_customer_by_id
    
    customer_id = "CUST000714"
    customer_details = get_customer_by_id(customer_id)
    
    if customer_details:
        print(f"✅ Found customer {customer_id}:")
        print(f"Name: {customer_details.get('customer_name')}")
        print(f"Total Orders: {customer_details.get('total_orders')}")
        print(f"Total Amount: ₹{customer_details.get('order_summary', {}).get('total_amount', 0):,}")
        
        print("\n📋 Orders:")
        for i, order in enumerate(customer_details.get('orders', []), 1):
            print(f"{i}. Order #{order.get('order_id')}: {order.get('product')} - ₹{order.get('amount', 0):,} ({order.get('status')})")
    else:
        print(f"❌ Customer {customer_id} not found")

if __name__ == "__main__":
    test_customer_lookup_direct()
    test_customer_lookup()