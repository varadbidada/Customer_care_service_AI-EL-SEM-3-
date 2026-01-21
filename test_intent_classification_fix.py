#!/usr/bin/env python3
"""
Test the intent classification fix to ensure order detail queries are handled correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.dialogue_state_manager import DialogueStateManager, DialogueState, Intent

def mock_get_order_by_id(order_id):
    """Mock function that returns order details for testing"""
    if order_id == 90495:
        return {
            'order_id': 'ORD90495',
            'product': 'Burger',
            'status': 'Delivered',
            'amount': 27357,
            'platform': 'Myntra',
            'customer_name': 'Riya'
        }
    return None

def mock_get_faq_answer(question):
    """Mock FAQ function"""
    return "This is a mock FAQ answer."

def create_mock_session():
    """Create a mock session object"""
    class MockSession:
        def __init__(self):
            self.dialogue_state = None
    
    return MockSession()

def test_intent_priority_order():
    """Test that intent detection follows strict priority order"""
    print("🧪 TESTING INTENT PRIORITY ORDER")
    print("=" * 60)
    
    dialogue_manager = DialogueStateManager()
    
    # Test cases with expected intents
    test_cases = [
        # ORDER_DETAIL_QUERY should have HIGHEST PRIORITY
        ("what was the price", Intent.ORDER_DETAIL_QUERY),
        ("show me the cost", Intent.ORDER_DETAIL_QUERY),
        ("what is the amount", Intent.ORDER_DETAIL_QUERY),
        ("order details", Intent.ORDER_DETAIL_QUERY),
        ("what product did I order", Intent.ORDER_DETAIL_QUERY),
        ("show me the item", Intent.ORDER_DETAIL_QUERY),
        
        # ORDER_STATUS should be second priority
        ("track my order", Intent.ORDER_STATUS),
        ("what is the status", Intent.ORDER_STATUS),
        ("where is my delivery", Intent.ORDER_STATUS),
        
        # RETURN_ORDER should be third priority
        ("I want to return", Intent.RETURN_ORDER),
        ("exchange this item", Intent.RETURN_ORDER),
        
        # BILLING_ISSUE should be LOWEST priority (cannot override order details)
        ("I was charged twice", Intent.BILLING_ISSUE),
        ("refund my payment", Intent.BILLING_ISSUE),
        ("billing problem", Intent.BILLING_ISSUE),
        
        # Edge case: price + billing keywords - should still be ORDER_DETAIL_QUERY
        ("what was the price I was charged", Intent.ORDER_DETAIL_QUERY),  # CRITICAL TEST
    ]
    
    all_passed = True
    
    for message, expected_intent in test_cases:
        detected_intent = dialogue_manager._detect_intent(message)
        status = "✅ PASS" if detected_intent == expected_intent else "❌ FAIL"
        
        print(f"{status} '{message}' → Expected: {expected_intent}, Got: {detected_intent}")
        
        if detected_intent != expected_intent:
            all_passed = False
    
    print(f"\nIntent Priority Test: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    return all_passed

def test_order_detail_workflow():
    """Test the order detail workflow provides clean responses"""
    print("\n🔍 TESTING ORDER DETAIL WORKFLOW")
    print("=" * 60)
    
    dialogue_manager = DialogueStateManager()
    session = create_mock_session()
    
    # Test price query workflow
    print("--- Test: Price query for order 90495 ---")
    
    # Set up dialogue state with order_detail_query intent
    dialogue_state = DialogueState()
    dialogue_state.active_intent = Intent.ORDER_DETAIL_QUERY
    dialogue_state.context['order_id'] = 90495
    session.dialogue_state = dialogue_state
    
    # Process price query
    result = dialogue_manager._handle_order_detail_workflow(
        "what was the price", 
        dialogue_state, 
        session, 
        mock_get_order_by_id
    )
    
    response = result.get('response', '')
    print(f"Response: {response}")
    
    # Validate response
    success_checks = [
        ("Contains price", "₹27,357" in response),
        ("Contains order ID", "90495" in response),
        ("No billing explanation", "billing" not in response.lower()),
        ("No refund mention", "refund" not in response.lower()),
        ("Clean factual answer", len(response.split('\n')) <= 2),  # Should be concise
    ]
    
    all_checks_passed = True
    for check_name, check_result in success_checks:
        status = "✅ PASS" if check_result else "❌ FAIL"
        print(f"  {status} {check_name}")
        if not check_result:
            all_checks_passed = False
    
    return all_checks_passed

def test_validation_requirement():
    """Test the exact validation requirement from the specification"""
    print("\n✅ TESTING VALIDATION REQUIREMENT")
    print("=" * 60)
    
    dialogue_manager = DialogueStateManager()
    session = create_mock_session()
    
    # Simulate the exact conversation from requirements
    print("User: what was the price for ORD90495")
    
    # Process the message end-to-end
    result = dialogue_manager.process_message(
        "what was the price for ORD90495", 
        session, 
        mock_get_order_by_id, 
        mock_get_faq_answer
    )
    
    response = result.get('response', '')
    print(f"Bot: {response}")
    
    # Validation checks
    expected_pattern = "The price for order #90495 is ₹27,357."
    
    validation_checks = [
        ("Contains correct price", "₹27,357" in response or "27357" in response),
        ("Contains order number", "90495" in response),
        ("No billing explanations", not any(word in response.lower() for word in ["billing", "charge", "refund", "payment"])),
        ("Clean response format", "price" in response.lower()),
    ]
    
    all_valid = True
    for check_name, check_result in validation_checks:
        status = "✅ PASS" if check_result else "❌ FAIL"
        print(f"  {status} {check_name}")
        if not check_result:
            all_valid = False
    
    print(f"\nValidation Requirement: {'✅ PASSED' if all_valid else '❌ FAILED'}")
    return all_valid

def main():
    """Run all intent classification tests"""
    print("🧪 INTENT CLASSIFICATION FIX VALIDATION")
    print("Testing order_detail_query intent with strict priority rules")
    print("=" * 80)
    
    tests = [
        ("Intent Priority Order", test_intent_priority_order),
        ("Order Detail Workflow", test_order_detail_workflow),
        ("Validation Requirement", test_validation_requirement),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("🏁 INTENT CLASSIFICATION TEST RESULTS")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    all_passed = passed == len(results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ order_detail_query intent implemented correctly")
        print("✅ Strict priority order enforced")
        print("✅ Clean factual responses without billing explanations")
        print("✅ Price queries return proper order details")
    else:
        print("\n❌ SOME TESTS FAILED - Intent classification needs fixes")
    
    print("=" * 80)
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)