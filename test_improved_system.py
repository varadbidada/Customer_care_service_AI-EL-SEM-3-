#!/usr/bin/env python3
"""
Test the improved system that handles both normal conversation and deterministic support
"""

from agents.router_agent import RouterAgent
from memory.session_manager import SessionManager

def test_normal_conversations():
    """Test that normal conversations work properly"""
    
    print("🗣️ Testing Normal Conversations")
    print("=" * 50)
    
    router = RouterAgent()
    session_manager = SessionManager(storage_type="memory")
    
    normal_messages = [
        "Hello, how are you?",
        "What's the weather like?", 
        "Can you help me with something?",
        "I need information about your products",
        "What are your business hours?",
        "Thank you for your help"
    ]
    
    for i, message in enumerate(normal_messages, 1):
        print(f"\nTest {i}: {message}")
        
        session = session_manager.get_session(f"normal_test_{i}")
        result = router.process_with_context(message, session)
        
        print(f"Response: {result['response'][:100]}...")
        print(f"Agents used: {result['agents_used']}")
        
        # Check that it's NOT using deterministic flow
        issue_context = result.get('issue_context', {})
        if issue_context.get('deterministic_flow') or issue_context.get('bypassed_llm'):
            print("❌ Incorrectly using deterministic flow for normal conversation")
        else:
            print("✅ Using normal conversation flow")

def test_support_conversations():
    """Test that clear support requests use deterministic flow"""
    
    print("\n🛠️ Testing Support Conversations")
    print("=" * 50)
    
    router = RouterAgent()
    session_manager = SessionManager(storage_type="memory")
    
    support_messages = [
        "Order 12345 got wrong item, want refund",
        "My order ABC123 is delayed, need replacement", 
        "Cancel order #9999",
        "Order 5555 arrived damaged, want refund"
    ]
    
    for i, message in enumerate(support_messages, 1):
        print(f"\nTest {i}: {message}")
        
        session = session_manager.get_session(f"support_test_{i}")
        result = router.process_with_context(message, session)
        
        print(f"Response: {result['response'][:100]}...")
        print(f"Agents used: {result['agents_used']}")
        
        # Check that it IS using deterministic flow
        issue_context = result.get('issue_context', {})
        if issue_context.get('complete_request') or issue_context.get('bypassed_llm'):
            print("✅ Correctly using deterministic flow for support request")
        else:
            print("❌ Should use deterministic flow for clear support request")

def test_topic_switching():
    """Test that users can switch from support to normal conversation"""
    
    print("\n🔄 Testing Topic Switching")
    print("=" * 50)
    
    router = RouterAgent()
    session_manager = SessionManager(storage_type="memory")
    session = session_manager.get_session("topic_switch_test")
    
    # Start with incomplete support request
    print("\nStep 1: Start incomplete support request")
    message1 = "Order 12345 got wrong item"
    result1 = router.process_with_context(message1, session)
    print(f"Message: {message1}")
    print(f"Response: {result1['response']}")
    
    # Switch to normal conversation
    print("\nStep 2: Switch to normal conversation")
    message2 = "Actually, what are your business hours?"
    result2 = router.process_with_context(message2, session)
    print(f"Message: {message2}")
    print(f"Response: {result2['response']}")
    
    # Check if it switched properly
    issue_context2 = result2.get('issue_context', {})
    if not issue_context2.get('resolution_in_progress'):
        print("✅ Successfully switched from support to normal conversation")
    else:
        print("❌ Failed to switch topics - still stuck in support mode")
    
    # Try another normal message
    print("\nStep 3: Continue normal conversation")
    message3 = "Thank you for the information"
    result3 = router.process_with_context(message3, session)
    print(f"Message: {message3}")
    print(f"Response: {result3['response']}")

if __name__ == "__main__":
    print("🚀 Testing Improved NLU System")
    
    test_normal_conversations()
    test_support_conversations() 
    test_topic_switching()
    
    print("\n🎉 Testing completed!")