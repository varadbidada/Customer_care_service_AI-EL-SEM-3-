#!/usr/bin/env python3
"""
Comprehensive test to validate ALL intent detection fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.dialogue_state_manager import DialogueStateManager, Intent

def test_all_intents():
    """Test all intent detection scenarios"""
    print("🧪 COMPREHENSIVE INTENT DETECTION TEST")
    print("=" * 70)
    
    dialogue_manager = DialogueStateManager()
    
    # Test cases with expected intents
    test_cases = [
        # ORDER_DETAIL_QUERY (highest priority)
        ("what was the price", Intent.ORDER_DETAIL_QUERY),
        ("show me the cost", Intent.ORDER_DETAIL_QUERY),
        ("order details", Intent.ORDER_DETAIL_QUERY),
        
        # RETURN_ORDER (should catch cancellations)
        ("i want to cancel my order ORD16399", Intent.RETURN_ORDER),
        ("cancel my order", Intent.RETURN_ORDER),
        ("I want to return this", Intent.RETURN_ORDER),
        ("exchange this item", Intent.RETURN_ORDER),
        
        # ORDER_STATUS (tracking)
        ("track my order", Intent.ORDER_STATUS),
        ("what is the status", Intent.ORDER_STATUS),
        ("where is my order", Intent.ORDER_STATUS),
        
        # BILLING_ISSUE
        ("I was charged twice", Intent.BILLING_ISSUE),
        ("refund my payment", Intent.BILLING_ISSUE),
        
        # FAQ (general queries)
        ("I have an issue related to subscription in Food Delivery", Intent.FAQ),
        ("I'm not able to connect to my internet", Intent.FAQ),
        ("The app keeps crashing", Intent.FAQ),
        ("How do I contact support", Intent.FAQ),
    ]
    
    print("Testing Intent Detection:")
    print("-" * 70)
    
    all_passed = True
    
    for message, expected_intent in test_cases:
        detected_intent = dialogue_manager._detect_intent(message)
        status = "✅ PASS" if detected_intent == expected_intent else "❌ FAIL"
        
        print(f"{status} '{message[:40]}...' → Expected: {expected_intent.value if expected_intent else 'None'}, Got: {detected_intent.value if detected_intent else 'None'}")
        
        if detected_intent != expected_intent:
            all_passed = False
    
    print(f"\nIntent Detection Test: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    return all_passed

def test_critical_scenarios():
    """Test the specific scenarios that were failing"""
    print("\n🎯 TESTING CRITICAL SCENARIOS")
    print("=" * 70)
    
    dialogue_manager = DialogueStateManager()
    
    critical_tests = [
        {
            "message": "i want to cancel my order ORD16399",
            "expected_intent": Intent.RETURN_ORDER,
            "description": "Cancellation request should be RETURN_ORDER, not FAQ"
        },
        {
            "message": "I have an issue related to subscription in Food Delivery",
            "expected_intent": Intent.FAQ,
            "description": "Subscription query should be FAQ"
        },
        {
            "message": "what was the price for order 90495",
            "expected_intent": Intent.ORDER_DETAIL_QUERY,
            "description": "Price query should be ORDER_DETAIL_QUERY, not BILLING_ISSUE"
        }
    ]
    
    all_passed = True
    
    for test in critical_tests:
        message = test["message"]
        expected = test["expected_intent"]
        description = test["description"]
        
        print(f"\n--- {description} ---")
        print(f"Message: '{message}'")
        
        detected = dialogue_manager._detect_intent(message)
        
        if detected == expected:
            print(f"✅ PASS: Correctly detected as {detected.value}")
        else:
            print(f"❌ FAIL: Expected {expected.value}, got {detected.value}")
            all_passed = False
    
    print(f"\nCritical Scenarios: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    return all_passed

def main():
    """Run comprehensive tests"""
    print("🔧 COMPREHENSIVE INTENT DETECTION FIX VALIDATION")
    print("Testing all intent detection issues at once")
    print("=" * 80)
    
    tests = [
        ("All Intent Detection", test_all_intents),
        ("Critical Scenarios", test_critical_scenarios),
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
    print("🏁 COMPREHENSIVE FIX RESULTS")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    all_passed = passed == len(results)
    
    if all_passed:
        print("\n🎉 ALL INTENT DETECTION ISSUES FIXED!")
        print("✅ Cancellation requests → RETURN_ORDER")
        print("✅ Subscription queries → FAQ")
        print("✅ Price queries → ORDER_DETAIL_QUERY")
        print("✅ Tracking requests → ORDER_STATUS")
        print("✅ Billing issues → BILLING_ISSUE")
    else:
        print("\n❌ SOME ISSUES REMAIN")
    
    print("=" * 80)
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)