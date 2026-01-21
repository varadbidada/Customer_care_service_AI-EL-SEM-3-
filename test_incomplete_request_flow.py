#!/usr/bin/env python3
"""
Test the incomplete request flow - asking for missing information only
"""

from agents.router_agent import RouterAgent
from memory.session_manager import SessionManager

def test_incomplete_request_flow():
    """Test that incomplete requests ask for ONLY the missing part"""
    
    print("🧪 Testing Incomplete Request Flow")
    print("=" * 50)
    
    # Create router and session
    router = RouterAgent()
    session_manager = SessionManager(storage_type="memory")
    session = session_manager.get_session("test_incomplete")
    
    # Test scenarios
    scenarios = [
        {
            "name": "Missing Order ID",
            "message": "I got wrong item, want refund",
            "expected_ask": "order"
        },
        {
            "name": "Missing Issue Type", 
            "message": "Order 12345 needs refund",
            "expected_ask": "issue"
        },
        {
            "name": "Missing Resolution",
            "message": "Order 12345 got wrong item",
            "expected_ask": "resolution"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📝 Scenario: {scenario['name']}")
        print(f"Message: {scenario['message']}")
        
        # Create fresh session for each test
        session = session_manager.get_session(f"test_{scenario['name'].lower().replace(' ', '_')}")
        
        result = router.process_with_context(scenario['message'], session)
        
        print(f"Response: {result['response']}")
        
        # Check if it's asking for the right missing information
        response_lower = result['response'].lower()
        
        if scenario['expected_ask'] == "order":
            if "order number" in response_lower:
                print("✅ Correctly asking for order number")
            else:
                print("❌ Should ask for order number")
        
        elif scenario['expected_ask'] == "issue":
            if "issue" in response_lower or "problem" in response_lower:
                print("✅ Correctly asking for issue type")
            else:
                print("❌ Should ask for issue type")
        
        elif scenario['expected_ask'] == "resolution":
            if "resolved" in response_lower or "refund" in response_lower or "replacement" in response_lower:
                print("✅ Correctly asking for resolution")
            else:
                print("❌ Should ask for resolution")

def test_never_reset_context():
    """Test that context is never reset during incomplete request flow"""
    
    print("\n🔒 Testing Context Preservation")
    print("=" * 50)
    
    router = RouterAgent()
    session_manager = SessionManager(storage_type="memory")
    session = session_manager.get_session("test_context")
    
    # Step 1: Incomplete request
    print("\nStep 1: Incomplete request")
    message1 = "Order 12345 got wrong item"
    result1 = router.process_with_context(message1, session)
    print(f"Message: {message1}")
    print(f"Response: {result1['response']}")
    
    # Check that order ID is preserved
    if session.active_order_id == "12345":
        print("✅ Order ID preserved in context")
    else:
        print(f"❌ Order ID not preserved: {session.active_order_id}")
    
    # Step 2: Provide missing resolution
    print("\nStep 2: Provide missing resolution")
    message2 = "I want a refund"
    result2 = router.process_with_context(message2, session)
    print(f"Message: {message2}")
    print(f"Response: {result2['response']}")
    
    # Should now complete the resolution
    if "refund" in result2['response'].lower() and "12345" in result2['response']:
        print("✅ Successfully completed resolution with preserved context")
    else:
        print("❌ Failed to complete resolution with preserved context")

if __name__ == "__main__":
    print("🚀 Testing Incomplete Request Flow and Context Preservation")
    
    test_incomplete_request_flow()
    test_never_reset_context()
    
    print("\n🎉 Incomplete request flow tests completed!")