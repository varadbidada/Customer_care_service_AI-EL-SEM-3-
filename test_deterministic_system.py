#!/usr/bin/env python3
"""
Test the complete deterministic Response Policy Layer
"""

from agents.human_conversation_manager import HumanConversationManager
from memory.session_manager import SessionManager

def test_deterministic_system():
    """Test the deterministic system with the exact user scenario"""
    
    print("🎯 Testing Deterministic Response Policy Layer")
    print("=" * 60)
    
    # This is exactly what happens in the web interface
    human_conversation_manager = HumanConversationManager()
    session_manager = SessionManager(storage_type="memory")
    
    # Test the exact user message
    session = session_manager.get_session("deterministic_test")
    
    print("🔍 Test Case: User refund request")
    message = "i want refund of my buds 3 order no. 1234"
    print(f"Input: '{message}'")
    
    result = human_conversation_manager.process_human_conversation(message, session)
    
    print(f"\nOutput: '{result.get('response', 'No response')}'")
    print(f"Issue Context: {result.get('issue_context', {})}")
    print(f"Session Resolved: {getattr(session, 'resolved', False)}")
    
    # Test follow-up message
    print(f"\n🔍 Test Case: Follow-up message after resolution")
    message2 = "hello"
    print(f"Input: '{message2}'")
    
    result2 = human_conversation_manager.process_human_conversation(message2, session)
    
    print(f"Output: '{result2.get('response', 'No response')}'")
    
    # Expected behavior validation
    print(f"\n✅ VALIDATION:")
    response1 = result.get('response', '')
    response2 = result2.get('response', '')
    
    # Check first response
    if "1234" in response1 and ("refund" in response1.lower() or "credit" in response1.lower()):
        print("✅ First response: Contains order ID and refund confirmation")
    else:
        print("❌ First response: Missing order ID or refund confirmation")
    
    # Check no loops
    if "?" not in response1 or "provide" not in response1.lower():
        print("✅ First response: No questions asked")
    else:
        print("❌ First response: Still asking questions")
    
    # Check post-resolution
    if response2 == "Is there anything else I can help you with?":
        print("✅ Second response: Correct post-resolution response")
    else:
        print("❌ Second response: Not using post-resolution template")

def test_missing_info_scenarios():
    """Test scenarios with missing information"""
    
    print(f"\n🔍 Testing Missing Information Scenarios")
    print("=" * 60)
    
    human_conversation_manager = HumanConversationManager()
    session_manager = SessionManager(storage_type="memory")
    
    scenarios = [
        {
            "name": "Missing Order ID",
            "message": "i want refund",
            "expected_ask": "order number"
        },
        {
            "name": "Missing Resolution",
            "message": "order 1234 has issue",
            "expected_ask": "resolution"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📝 Scenario: {scenario['name']}")
        session = session_manager.get_session(f"test_{scenario['name'].lower().replace(' ', '_')}")
        
        result = human_conversation_manager.process_human_conversation(scenario['message'], session)
        
        print(f"Input: '{scenario['message']}'")
        print(f"Output: '{result.get('response', 'No response')}'")
        
        # Validation
        response = result.get('response', '').lower()
        if scenario['expected_ask'] in response:
            print(f"✅ Correctly asking for {scenario['expected_ask']}")
        else:
            print(f"❌ Not asking for {scenario['expected_ask']}")

if __name__ == "__main__":
    test_deterministic_system()
    test_missing_info_scenarios()
    
    print(f"\n🎉 Deterministic System Testing Complete!")
    print("Expected behavior:")
    print("- Complete requests: Immediate deterministic response")
    print("- Incomplete requests: Ask for missing info only")
    print("- Post-resolution: Standard follow-up response")
    print("- NO loops, NO repeated questions, NO status probing")