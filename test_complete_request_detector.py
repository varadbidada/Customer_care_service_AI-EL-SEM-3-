#!/usr/bin/env python3
"""
Test the complete request detector functionality
"""

from agents.nlp_processor import NLPProcessor
from agents.router_agent import RouterAgent
from memory.session_manager import SessionManager
import json

def test_complete_request_detection():
    """Test the complete request detector with various scenarios"""
    
    nlp = NLPProcessor()
    
    # Test cases: [message, expected_result]
    test_cases = [
        # Complete requests (should return is_complete=True)
        ("Order 12345 got wrong item, want refund", {
            "is_complete": True,
            "order_id": "12345",
            "issue": "wrong_item",
            "resolution": "refund"
        }),
        ("I received wrong apples instead of bananas for order #67890, please send replacement", {
            "is_complete": True,
            "order_id": "67890",
            "issue": "wrong_item", 
            "resolution": "replacement"
        }),
        ("Order ABC123 is delayed, I want my money back", {
            "is_complete": True,
            "order_id": "ABC123",
            "issue": "delay",
            "resolution": "refund"
        }),
        ("My order 9999 arrived damaged, need replacement", {
            "is_complete": True,
            "order_id": "9999",
            "issue": "damaged",
            "resolution": "replacement"
        }),
        ("Cancel order #5555", {
            "is_complete": True,
            "order_id": "5555",
            "issue": None,  # Cancel doesn't need issue
            "resolution": "cancel"
        }),
        
        # Incomplete requests (should return is_complete=False)
        ("Order 12345 got wrong item", {
            "is_complete": False,
            "order_id": "12345",
            "issue": "wrong_item",
            "resolution": None
        }),
        ("I want a refund", {
            "is_complete": False,
            "order_id": None,
            "issue": None,
            "resolution": "refund"
        }),
        ("My order is delayed", {
            "is_complete": False,
            "order_id": None,
            "issue": "delay",
            "resolution": None
        }),
        ("Hello, I need help", {
            "is_complete": False,
            "order_id": None,
            "issue": None,
            "resolution": None
        })
    ]
    
    print("🧪 Testing Complete Request Detector")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for i, (message, expected) in enumerate(test_cases, 1):
        print(f"\nTest {i}: {message}")
        
        result = nlp.detect_complete_request(message)
        
        # Check each field
        success = True
        for key, expected_value in expected.items():
            actual_value = result.get(key)
            if actual_value != expected_value:
                print(f"  ❌ {key}: expected {expected_value}, got {actual_value}")
                success = False
        
        if success:
            print(f"  ✅ PASS")
            passed += 1
        else:
            print(f"  ❌ FAIL")
            print(f"     Expected: {expected}")
            print(f"     Actual:   {result}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0

def test_router_integration():
    """Test that the router properly uses the complete request detector"""
    
    print("\n🔄 Testing Router Integration")
    print("=" * 50)
    
    # Create router and session
    router = RouterAgent()
    session_manager = SessionManager(storage_type="memory")
    session = session_manager.get_session("test_session")
    
    # Test complete request
    message = "Order 12345 got wrong item, want refund"
    print(f"\nTesting: {message}")
    
    result = router.process_with_context(message, session)
    
    print(f"Response: {result['response']}")
    print(f"Agents used: {result['agents_used']}")
    print(f"Issue context: {result['issue_context']}")
    
    # Check if it bypassed LLM
    if result['issue_context'].get('bypassed_llm'):
        print("✅ Successfully bypassed router and LLM")
        return True
    else:
        print("❌ Failed to bypass router and LLM")
        return False

if __name__ == "__main__":
    print("🚀 Testing Complete Request Detector Implementation")
    
    # Test the detector
    detector_success = test_complete_request_detection()
    
    # Test router integration
    router_success = test_router_integration()
    
    if detector_success and router_success:
        print("\n🎉 All tests passed! Complete request detector is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the implementation.")