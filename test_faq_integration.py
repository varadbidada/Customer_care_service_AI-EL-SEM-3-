#!/usr/bin/env python3
"""
Test the FAQ integration to ensure subscription and food delivery queries work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.dialogue_state_manager import DialogueStateManager, DialogueState, Intent

def mock_get_order_by_id(order_id):
    """Mock function - not needed for FAQ tests"""
    return None

def create_mock_session():
    """Create a mock session object"""
    class MockSession:
        def __init__(self):
            self.dialogue_state = None
    
    return MockSession()

def test_faq_intent_detection():
    """Test that FAQ queries are properly detected"""
    print("🧪 TESTING FAQ INTENT DETECTION")
    print("=" * 60)
    
    dialogue_manager = DialogueStateManager()
    
    # Test cases that should be detected as FAQ
    faq_test_cases = [
        "I have an issue related to subscription in Food Delivery",
        "I'm not able to connect to my internet",
        "The app keeps crashing",
        "How do I contact customer support",
        "What are your business hours",
        "How do I apply a coupon code",
        "My food is taking too long",
        "Can I modify my food order",
        "Payment failed but money was deducted",
        "The food quality was poor"
    ]
    
    all_passed = True
    
    for message in faq_test_cases:
        detected_intent = dialogue_manager._detect_intent(message)
        status = "✅ PASS" if detected_intent == Intent.FAQ else "❌ FAIL"
        
        print(f"{status} '{message}' → {detected_intent}")
        
        if detected_intent != Intent.FAQ:
            all_passed = False
    
    print(f"\nFAQ Intent Detection: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    return all_passed

def test_faq_matching():
    """Test that FAQ matching works with the dataset"""
    print("\n🔍 TESTING FAQ MATCHING")
    print("=" * 60)
    
    # Import the FAQ function
    try:
        from app import get_faq_answer, faq_df
        
        print(f"FAQ dataset loaded: {len(faq_df)} entries")
        
        # Test cases
        test_cases = [
            ("I have an issue related to subscription in Food Delivery", "subscription"),
            ("I'm not able to connect to my internet", "technical"),
            ("The app keeps crashing", "app"),
            ("How do I contact customer support", "contact"),
            ("My food is taking too long", "food"),
            ("Can I modify my food order", "modify"),
        ]
        
        success_count = 0
        
        for query, expected_keyword in test_cases:
            print(f"\n--- Testing: '{query}' ---")
            answer = get_faq_answer(query)
            
            if answer:
                print(f"✅ Got answer: {answer[:100]}...")
                success_count += 1
            else:
                print(f"❌ No answer found")
        
        print(f"\nFAQ Matching: {success_count}/{len(test_cases)} successful")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error testing FAQ matching: {e}")
        return False

def test_end_to_end_faq():
    """Test end-to-end FAQ workflow"""
    print("\n🎯 TESTING END-TO-END FAQ WORKFLOW")
    print("=" * 60)
    
    try:
        from app import get_faq_answer
        
        dialogue_manager = DialogueStateManager()
        session = create_mock_session()
        
        # Test the exact user query from the problem
        user_query = "I have an issue related to subscription in Food Delivery"
        
        print(f"User query: '{user_query}'")
        
        # Process the message end-to-end
        result = dialogue_manager.process_message(
            user_query, 
            session, 
            mock_get_order_by_id, 
            get_faq_answer
        )
        
        response = result.get('response', '')
        print(f"Bot response: {response}")
        
        # Validation checks
        validation_checks = [
            ("Got a response", len(response) > 0),
            ("Not asking for order number", "order number" not in response.lower()),
            ("Not about tracking", "track" not in response.lower()),
            ("Contains helpful info", any(word in response.lower() for word in ["subscription", "support", "help", "contact"])),
        ]
        
        all_valid = True
        for check_name, check_result in validation_checks:
            status = "✅ PASS" if check_result else "❌ FAIL"
            print(f"  {status} {check_name}")
            if not check_result:
                all_valid = False
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Error in end-to-end test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all FAQ integration tests"""
    print("🧪 FAQ INTEGRATION VALIDATION")
    print("Testing AI customer support dataset integration")
    print("=" * 80)
    
    tests = [
        ("FAQ Intent Detection", test_faq_intent_detection),
        ("FAQ Matching", test_faq_matching),
        ("End-to-End FAQ", test_end_to_end_faq),
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
    print("🏁 FAQ INTEGRATION TEST RESULTS")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    all_passed = passed == len(results)
    
    if all_passed:
        print("\n🎉 FAQ INTEGRATION WORKING!")
        print("✅ FAQ intent detection working")
        print("✅ AI customer support dataset integrated")
        print("✅ Subscription and food delivery queries handled")
        print("✅ No more incorrect order tracking routing")
    else:
        print("\n❌ FAQ INTEGRATION NEEDS FIXES")
    
    print("=" * 80)
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)