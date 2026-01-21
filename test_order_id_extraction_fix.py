#!/usr/bin/env python3
"""
Test script to validate the order ID extraction and state handling fixes.
This test ensures all STRICT RULES are followed exactly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.dialogue_state_manager import DialogueStateManager, DialogueState, Intent
from memory.session_manager import SessionManager
import json

def mock_get_order_by_id(order_id):
    """Mock function that returns order details for valid IDs, None for invalid"""
    valid_orders = {
        45: {
            'order_id': '45',
            'product': 'Wireless Headphones',
            'status': 'delivered',
            'amount': 2999,
            'platform': 'Amazon'
        },
        123: {
            'order_id': '123',
            'product': 'Smartphone',
            'status': 'in transit',
            'amount': 15999,
            'platform': 'Flipkart'
        }
    }
    
    # Convert to int for lookup
    try:
        order_id_int = int(order_id)
        return valid_orders.get(order_id_int)
    except (ValueError, TypeError):
        return None

def mock_get_faq_answer(question):
    """Mock FAQ function"""
    return "This is a mock FAQ answer for billing issues."

def create_mock_session():
    """Create a mock session object"""
    class MockSession:
        def __init__(self):
            self.dialogue_state = None
            self.user_name = "test_user"
            self.conversation_history = []
    
    return MockSession()

def test_order_id_extraction():
    """Test Rule 1: ORDER ID EXTRACTION (MANDATORY)"""
    print("=" * 60)
    print("TEST 1: ORDER ID EXTRACTION")
    print("=" * 60)
    
    dialogue_manager = DialogueStateManager()
    
    # Test cases as specified in requirements
    test_cases = [
        ("45", 45),
        ("ORD45", 45),
        ("#45", 45),
        ("order 45", 45),
        ("My order number is 123", 123),
        ("It's #123", 123),
        ("ORD123", 123),
        ("no numbers here", None),
        ("", None)
    ]
    
    all_passed = True
    
    for input_text, expected in test_cases:
        result = dialogue_manager._extract_order_id(input_text)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} Input: '{input_text}' → Expected: {expected}, Got: {result}")
        
        if result != expected:
            all_passed = False
    
    print(f"\nOrder ID Extraction Test: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    return all_passed

def test_slot_filling_rules():
    """Test Rule 2: SLOT FILLING RULES (NON-NEGOTIABLE)"""
    print("\n" + "=" * 60)
    print("TEST 2: SLOT FILLING RULES")
    print("=" * 60)
    
    dialogue_manager = DialogueStateManager()
    session = create_mock_session()
    
    # Set up initial state - billing issue detected, waiting for order ID
    dialogue_state = DialogueState()
    dialogue_state.active_intent = Intent.BILLING_ISSUE
    dialogue_state.pending_slot = "order_id"
    session.dialogue_state = dialogue_state
    
    print("Initial state: billing_issue intent, pending order_id slot")
    
    # Test successful extraction
    print("\n--- Test: Valid order ID input '45' ---")
    result = dialogue_manager.process_message("45", session, mock_get_order_by_id, mock_get_faq_answer)
    
    # Check that order_id was saved and pending_slot cleared
    final_state = dialogue_manager.get_dialogue_state(session)
    
    order_id_saved = final_state.context.get('order_id') == 45
    pending_slot_cleared = final_state.pending_slot is None
    
    print(f"✅ Order ID saved: {order_id_saved} (order_id = {final_state.context.get('order_id')})")
    print(f"✅ Pending slot cleared: {pending_slot_cleared} (pending_slot = {final_state.pending_slot})")
    
    # Test unsuccessful extraction - should ask again without resetting intent
    session2 = create_mock_session()
    dialogue_state2 = DialogueState()
    dialogue_state2.active_intent = Intent.BILLING_ISSUE
    dialogue_state2.pending_slot = "order_id"
    session2.dialogue_state = dialogue_state2
    
    print("\n--- Test: Invalid order ID input 'hello' ---")
    result2 = dialogue_manager.process_message("hello", session2, mock_get_order_by_id, mock_get_faq_answer)
    
    final_state2 = dialogue_manager.get_dialogue_state(session2)
    
    intent_preserved = final_state2.active_intent == Intent.BILLING_ISSUE
    still_pending = final_state2.pending_slot == "order_id"
    
    print(f"✅ Intent preserved: {intent_preserved} (active_intent = {final_state2.active_intent})")
    print(f"✅ Still asking for order ID: {still_pending} (pending_slot = {final_state2.pending_slot})")
    
    slot_filling_passed = order_id_saved and pending_slot_cleared and intent_preserved and still_pending
    print(f"\nSlot Filling Test: {'✅ ALL PASSED' if slot_filling_passed else '❌ SOME FAILED'}")
    return slot_filling_passed

def test_intent_preservation():
    """Test Rule 3: INTENT PRESERVATION (CRITICAL)"""
    print("\n" + "=" * 60)
    print("TEST 3: INTENT PRESERVATION")
    print("=" * 60)
    
    dialogue_manager = DialogueStateManager()
    session = create_mock_session()
    
    # Start with billing issue
    print("--- Step 1: Detect billing issue ---")
    result1 = dialogue_manager.process_message("I was charged twice for my order", session, mock_get_order_by_id, mock_get_faq_answer)
    
    state = dialogue_manager.get_dialogue_state(session)
    initial_intent = state.active_intent
    print(f"Intent detected: {initial_intent}")
    
    # Provide invalid order ID - intent should be preserved
    print("\n--- Step 2: Provide invalid order ID (999) ---")
    result2 = dialogue_manager.process_message("999", session, mock_get_order_by_id, mock_get_faq_answer)
    
    state_after_failure = dialogue_manager.get_dialogue_state(session)
    intent_after_failure = state_after_failure.active_intent
    
    print(f"Intent after lookup failure: {intent_after_failure}")
    print(f"Response: {result2.get('response', '')[:100]}...")
    
    # Provide valid order ID - should work now
    print("\n--- Step 3: Provide valid order ID (45) ---")
    result3 = dialogue_manager.process_message("45", session, mock_get_order_by_id, mock_get_faq_answer)
    
    intent_preserved = (initial_intent == Intent.BILLING_ISSUE and 
                       intent_after_failure == Intent.BILLING_ISSUE)
    
    successful_resolution = "found your order #45" in result3.get('response', '').lower()
    
    print(f"✅ Intent preserved across failure: {intent_preserved}")
    print(f"✅ Eventually resolved successfully: {successful_resolution}")
    
    preservation_passed = intent_preserved and successful_resolution
    print(f"\nIntent Preservation Test: {'✅ ALL PASSED' if preservation_passed else '❌ SOME FAILED'}")
    return preservation_passed

def test_retry_behavior():
    """Test Rule 4: RETRY BEHAVIOR"""
    print("\n" + "=" * 60)
    print("TEST 4: RETRY BEHAVIOR")
    print("=" * 60)
    
    dialogue_manager = DialogueStateManager()
    session = create_mock_session()
    
    # Set up billing issue with valid order ID that doesn't exist in dataset
    dialogue_state = DialogueState()
    dialogue_state.active_intent = Intent.BILLING_ISSUE
    dialogue_state.context['order_id'] = 999  # Invalid order ID
    session.dialogue_state = dialogue_state
    
    print("Setup: billing_issue intent with invalid order_id = 999")
    
    # This should trigger the "order not found" scenario
    result = dialogue_manager._handle_billing_workflow("", dialogue_state, session, mock_get_order_by_id, mock_get_faq_answer)
    
    # Check the response and state
    response = result.get('response', '')
    final_state = dialogue_manager.get_dialogue_state(session)
    
    correct_response = "couldn't find that order" in response.lower() and "recheck" in response.lower()
    intent_still_active = final_state.active_intent == Intent.BILLING_ISSUE
    asking_for_retry = final_state.pending_slot == "order_id"
    order_id_cleared = 'order_id' not in final_state.context
    
    print(f"✅ Correct retry message: {correct_response}")
    print(f"✅ Intent still active: {intent_still_active} (active_intent = {final_state.active_intent})")
    print(f"✅ Asking for order ID again: {asking_for_retry} (pending_slot = {final_state.pending_slot})")
    print(f"✅ Invalid order ID cleared: {order_id_cleared}")
    print(f"Response: {response}")
    
    retry_passed = correct_response and intent_still_active and asking_for_retry and order_id_cleared
    print(f"\nRetry Behavior Test: {'✅ ALL PASSED' if retry_passed else '❌ SOME FAILED'}")
    return retry_passed

def test_session_reset_rules():
    """Test Rule 5: SESSION RESET (ONLY ALLOWED HERE)"""
    print("\n" + "=" * 60)
    print("TEST 5: SESSION RESET RULES")
    print("=" * 60)
    
    dialogue_manager = DialogueStateManager()
    session = create_mock_session()
    
    # Test that session resets on completion keywords
    dialogue_state = DialogueState()
    dialogue_state.active_intent = Intent.BILLING_ISSUE
    dialogue_state.context['order_id'] = 45
    session.dialogue_state = dialogue_state
    
    print("Setup: Active billing_issue intent with order_id = 45")
    
    # Test completion
    completion_result = dialogue_manager.handle_completion("thanks", dialogue_state)
    
    reset_on_completion = completion_result is not None
    state_cleared = dialogue_state.active_intent is None
    
    print(f"✅ Resets on 'thanks': {reset_on_completion}")
    print(f"✅ State cleared after completion: {state_cleared}")
    
    # Test that session does NOT reset on lookup failure (already tested above)
    reset_rules_passed = reset_on_completion and state_cleared
    print(f"\nSession Reset Rules Test: {'✅ ALL PASSED' if reset_rules_passed else '❌ SOME FAILED'}")
    return reset_rules_passed

def run_comprehensive_test():
    """Run all tests and provide final validation"""
    print("🧪 COMPREHENSIVE ORDER ID EXTRACTION AND STATE HANDLING TEST")
    print("Testing compliance with all STRICT RULES")
    print("=" * 80)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Order ID Extraction", test_order_id_extraction()))
    test_results.append(("Slot Filling Rules", test_slot_filling_rules()))
    test_results.append(("Intent Preservation", test_intent_preservation()))
    test_results.append(("Retry Behavior", test_retry_behavior()))
    test_results.append(("Session Reset Rules", test_session_reset_rules()))
    
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
        print("🎉 ALL TESTS PASSED - REQUIREMENTS SATISFIED")
        print("✅ Order ID extraction works for: '45', 'ORD45', '#45', 'order 45'")
        print("✅ Intent preserved across lookup failures")
        print("✅ No session reset on order not found")
        print("✅ Proper retry behavior implemented")
        print("✅ Session reset only on completion")
    else:
        print("❌ SOME TESTS FAILED - REQUIREMENTS NOT MET")
        print("Please review the failed tests and fix the implementation.")
    
    print("=" * 80)
    return all_passed

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)