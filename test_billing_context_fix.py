#!/usr/bin/env python3
"""
Test script to validate the billing context preservation fix.
This test ensures that order_id context is preserved across billing discussions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.dialogue_state_manager import DialogueStateManager, DialogueState, Intent
from memory.session_manager import SessionManager
import json

def mock_get_order_by_id(order_id):
    """Mock function that returns order details for valid IDs"""
    valid_orders = {
        16399: {
            'order_id': '16399',
            'product': 'Wireless Headphones',
            'status': 'refunded',
            'amount': 2999,
            'platform': 'Amazon'
        },
        45: {
            'order_id': '45',
            'product': 'Smartphone',
            'status': 'delivered',
            'amount': 15999,
            'platform': 'Flipkart'
        }
    }
    
    try:
        order_id_int = int(order_id)
        return valid_orders.get(order_id_int)
    except (ValueError, TypeError):
        return None

def mock_get_faq_answer(question):
    """Mock FAQ function"""
    return "For billing issues, please check if the charge matches your order amount."

def create_mock_session():
    """Create a mock session object with persistent entities"""
    class MockSession:
        def __init__(self):
            self.dialogue_state = None
            self.user_name = "test_user"
            self.conversation_history = []
            self.persistent_entities = {}  # This is key for the fix
    
    return MockSession()

def test_billing_context_preservation():
    """Test the main scenario: billing issue with existing order context"""
    print("=" * 80)
    print("🧪 TESTING BILLING CONTEXT PRESERVATION FIX")
    print("=" * 80)
    
    dialogue_manager = DialogueStateManager()
    session = create_mock_session()
    
    print("\n📋 SCENARIO: User discusses billing issue for known order")
    print("Expected: Bot should NOT ask for order number again")
    
    # Step 1: Simulate that order 16399 is already known in session
    session.persistent_entities['order_number'] = '16399'
    print(f"✅ Setup: Order 16399 already in session persistent entities")
    
    # Step 2: User mentions billing/refund issue
    print(f"\n👤 User: 'I didn't get refund but it shows it is refunded'")
    result1 = dialogue_manager.process_message(
        "I didn't get refund but it shows it is refunded", 
        session, 
        mock_get_order_by_id, 
        mock_get_faq_answer
    )
    
    print(f"🤖 Bot: {result1.get('response', '')}")
    
    # Check if bot used existing order_id without asking
    response1 = result1.get('response', '')
    used_existing_order = '16399' in response1
    asked_for_order = 'order number' in response1.lower() or 'provide' in response1.lower()
    
    print(f"\n📊 Analysis:")
    print(f"   ✅ Used existing order 16399: {used_existing_order}")
    print(f"   ❌ Asked for order number: {asked_for_order}")
    
    # Step 3: User responds to follow-up question
    print(f"\n👤 User: 'no'")
    result2 = dialogue_manager.process_message(
        "no", 
        session, 
        mock_get_order_by_id, 
        mock_get_faq_answer
    )
    
    print(f"🤖 Bot: {result2.get('response', '')}")
    
    # Check if bot still remembers the order context
    response2 = result2.get('response', '')
    still_has_context = 'refund' in response2.lower() and ('3-5' in response2 or 'business days' in response2)
    asked_for_order_again = 'order number' in response2.lower()
    
    print(f"\n📊 Follow-up Analysis:")
    print(f"   ✅ Provided refund timeline: {still_has_context}")
    print(f"   ❌ Asked for order again: {asked_for_order_again}")
    
    # Final validation
    test_passed = (
        used_existing_order and 
        not asked_for_order and 
        still_has_context and 
        not asked_for_order_again
    )
    
    print(f"\n🏁 TEST RESULT: {'✅ PASSED' if test_passed else '❌ FAILED'}")
    
    if test_passed:
        print("✅ Context preservation working correctly!")
        print("✅ No infinite loop - order_id reused from session")
        print("✅ Multi-turn billing conversation flows smoothly")
    else:
        print("❌ Context preservation failed!")
        if asked_for_order:
            print("❌ Bot asked for order number despite it being in session")
        if asked_for_order_again:
            print("❌ Bot lost context during follow-up")
    
    return test_passed

def test_new_billing_issue():
    """Test that new billing issues still work correctly"""
    print("\n" + "=" * 80)
    print("🧪 TESTING NEW BILLING ISSUE (NO EXISTING CONTEXT)")
    print("=" * 80)
    
    dialogue_manager = DialogueStateManager()
    session = create_mock_session()  # Fresh session, no persistent entities
    
    print("\n📋 SCENARIO: User mentions billing issue without existing order context")
    print("Expected: Bot should ask for order number")
    
    # User mentions billing issue without order context
    print(f"\n👤 User: 'I was charged twice'")
    result = dialogue_manager.process_message(
        "I was charged twice", 
        session, 
        mock_get_order_by_id, 
        mock_get_faq_answer
    )
    
    print(f"🤖 Bot: {result.get('response', '')}")
    
    # Check if bot correctly asks for order number
    response = result.get('response', '')
    asked_for_order = 'order number' in response.lower() or 'provide' in response.lower()
    
    print(f"\n📊 Analysis:")
    print(f"   ✅ Asked for order number: {asked_for_order}")
    
    test_passed = asked_for_order
    
    print(f"\n🏁 TEST RESULT: {'✅ PASSED' if test_passed else '❌ FAILED'}")
    
    return test_passed

def run_comprehensive_test():
    """Run all billing context tests"""
    print("🚀 COMPREHENSIVE BILLING CONTEXT PRESERVATION TEST")
    print("Testing the fix for the infinite loop bug")
    
    test_results = []
    
    # Run tests
    test_results.append(("Context Preservation", test_billing_context_preservation()))
    test_results.append(("New Billing Issue", test_new_billing_issue()))
    
    # Summary
    print("\n" + "=" * 80)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED - BILLING LOOP BUG FIXED!")
        print("✅ Order context preserved across billing discussions")
        print("✅ No infinite loops asking for order number")
        print("✅ Multi-turn conversations work smoothly")
        print("✅ New billing issues still work correctly")
    else:
        print("❌ SOME TESTS FAILED - BUG NOT FULLY FIXED")
        print("Please review the failed tests and adjust the implementation.")
    
    print("=" * 80)
    return all_passed

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)