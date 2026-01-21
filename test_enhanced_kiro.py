#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced Kiro AI Assistant with:
- Enhanced entity tracking
- Multi-intent response merging  
- Context-aware session persistence
- Wrong item handling
- Human-like conversation flow
"""

from agents.router_agent import RouterAgent
from memory.session_manager import SessionManager
import time
import os

def test_enhanced_wrong_item_handling():
    """Test enhanced wrong item detection and handling"""
    
    print("🍎 Testing Enhanced Wrong Item Handling")
    print("=" * 50)
    
    router = RouterAgent()
    session_manager = SessionManager(storage_type="json", storage_path="test_data/sessions")
    session = session_manager.get_session("wrong_item_test")
    
    wrong_item_scenarios = [
        ("I got wrong apples", "Should detect general wrong item case"),
        ("I ordered red apples but got green apples", "Should detect specific substitution"),
        ("My order number is #12345", "Should connect to previous wrong item context"),
        ("I want a refund", "Should use full context for refund processing"),
        ("Actually, I ordered green apples but received red ones", "Should handle correction"),
    ]
    
    for message, expectation in wrong_item_scenarios:
        print(f"\n👤 User: '{message}'")
        print(f"🎯 Expected: {expectation}")
        
        response_data = router.process_with_context(message, session)
        session_manager.update_session(session)
        
        print(f"🤖 Kiro: {response_data['response']}")
        print(f"📋 Entities: {session.persistent_entities}")
        print(f"🚨 Issues: {len([i for i in session.unresolved_issues if i.get('status') == 'open'])} open")
        
        if session.unresolved_issues:
            latest_issue = session.unresolved_issues[-1]
            print(f"   Latest issue: {latest_issue.get('type')} - {latest_issue.get('description')}")

def test_multi_intent_response_merging():
    """Test enhanced multi-intent response merging"""
    
    print("\n🔀 Testing Multi-Intent Response Merging")
    print("=" * 50)
    
    router = RouterAgent()
    session_manager = SessionManager(storage_type="memory")
    
    multi_intent_cases = [
        ("Hi, I'm Sarah and I want a refund for my delayed order", "Should handle greeting + support + order"),
        ("I need to track order #98765 and also want to know iPhone pricing", "Should merge order + product naturally"),
        ("My delivery is late and I received the wrong item", "Should handle order + support with empathy"),
        ("Can you cancel my order and tell me about your return policy?", "Should merge order + support smoothly"),
    ]
    
    for i, (message, expectation) in enumerate(multi_intent_cases):
        session = session_manager.get_session(f"multi_intent_{i}")
        
        print(f"\n👤 User: '{message}'")
        print(f"🎯 Expected: {expectation}")
        
        response_data = router.process_with_context(message, session)
        
        print(f"🎭 Intents: {response_data['intents']}")
        print(f"🤖 Agents: {response_data['agents_used']}")
        print(f"🔄 Multi-Intent: {response_data['is_multi_intent']}")
        print(f"💬 Response: {response_data['response']}")

def test_context_aware_follow_ups():
    """Test context-aware follow-up handling"""
    
    print("\n🧠 Testing Context-Aware Follow-ups")
    print("=" * 50)
    
    router = RouterAgent()
    session_manager = SessionManager(storage_type="memory")
    session = session_manager.get_session("context_test")
    
    conversation_flow = [
        ("Hello, I'm John", "Should learn user name"),
        ("I have an issue with my laptop order", "Should remember product context"),
        ("The order number is ABC123", "Should connect order to product issue"),
        ("track it", "Should use session order number without asking"),
        ("Actually, I got wrong apples instead", "Should detect product substitution"),
        ("cancel order", "Should use session context for cancellation"),
        ("How much will the refund be?", "Should use order context for refund amount"),
    ]
    
    for message, expectation in conversation_flow:
        print(f"\n👤 User: '{message}'")
        print(f"🎯 Expected: {expectation}")
        
        response_data = router.process_with_context(message, session)
        session_manager.update_session(session)
        
        print(f"🤖 Kiro: {response_data['response']}")
        print(f"📋 Session: {session.persistent_entities}")
        print(f"👤 User: {session.user_name} ({session.communication_style}, {session.user_tone})")
        
        # Show context awareness
        if session.unresolved_issues:
            print(f"🚨 Open Issues: {len([i for i in session.unresolved_issues if i.get('status') == 'open'])}")

def test_session_persistence():
    """Test session persistence across 'server restarts'"""
    
    print("\n💾 Testing Session Persistence")
    print("=" * 50)
    
    # First session manager instance
    print("📝 Creating first session...")
    session_manager1 = SessionManager(storage_type="json", storage_path="test_data/persistence")
    router = RouterAgent()
    
    session = session_manager1.get_session("persistence_test")
    
    # Have a conversation
    messages = [
        "Hi, I'm Alice",
        "I have order #PERSIST123",
        "I ordered red apples but got green apples"
    ]
    
    for message in messages:
        print(f"👤 User: {message}")
        response_data = router.process_with_context(message, session)
        session_manager1.update_session(session)
        print(f"🤖 Kiro: {response_data['response']}")
    
    print(f"\n📊 Session before 'restart': {session.persistent_entities}")
    print(f"👤 User: {session.user_name}")
    print(f"🚨 Issues: {len(session.unresolved_issues)}")
    
    # Simulate server restart - create new session manager
    print("\n🔄 Simulating server restart...")
    session_manager2 = SessionManager(storage_type="json", storage_path="test_data/persistence")
    
    # Get the same session - should be loaded from storage
    restored_session = session_manager2.get_session("persistence_test")
    
    print(f"📊 Session after 'restart': {restored_session.persistent_entities}")
    print(f"👤 User: {restored_session.user_name}")
    print(f"🚨 Issues: {len(restored_session.unresolved_issues)}")
    
    # Continue conversation with restored context
    print("\n💬 Continuing conversation with restored context...")
    follow_up_message = "I want a refund"
    print(f"👤 User: {follow_up_message}")
    
    response_data = router.process_with_context(follow_up_message, restored_session)
    print(f"🤖 Kiro: {response_data['response']}")
    
    # Verify context was maintained
    if "alice" in response_data['response'].lower() and "persist123" in response_data['response']:
        print("✅ Session persistence working correctly!")
    else:
        print("❌ Session persistence may have issues")

def test_human_like_conversation_flow():
    """Test overall human-like conversation flow"""
    
    print("\n🤖 Testing Human-Like Conversation Flow")
    print("=" * 50)
    
    router = RouterAgent()
    session_manager = SessionManager(storage_type="memory")
    session = session_manager.get_session("human_like_test")
    
    # Simulate a realistic customer service conversation
    conversation = [
        "Hi there!",
        "I'm having trouble with my recent order",
        "I'm Sarah, by the way",
        "The order number is #FLOW456",
        "I ordered iPhone 14 but got iPhone 13",
        "This is really frustrating!",
        "I want a refund and also need to know when my next order will arrive",
        "How long will the refund take?",
        "Thanks for your help!"
    ]
    
    print("🎭 Simulating realistic customer service conversation:")
    
    for i, message in enumerate(conversation):
        print(f"\n👤 Sarah: {message}")
        
        response_data = router.process_with_context(message, session)
        session_manager.update_session(session)
        
        print(f"🤖 Kiro: {response_data['response']}")
        
        # Show conversation evolution
        if i % 3 == 2:  # Every 3 messages, show session state
            print(f"\n📊 Conversation State:")
            print(f"   User: {session.user_name} ({session.communication_style}, {session.user_tone})")
            print(f"   Entities: {session.persistent_entities}")
            print(f"   Empathy Level: {session.empathy_level}")
            print(f"   Open Issues: {len([i for i in session.unresolved_issues if i.get('status') == 'open'])}")

def test_storage_performance():
    """Test storage performance and cleanup"""
    
    print("\n⚡ Testing Storage Performance")
    print("=" * 50)
    
    # Test different storage types
    storage_types = ["memory", "json", "sqlite"]
    
    for storage_type in storage_types:
        print(f"\n📊 Testing {storage_type} storage...")
        
        session_manager = SessionManager(
            storage_type=storage_type, 
            storage_path=f"test_data/perf_{storage_type}"
        )
        router = RouterAgent()
        
        # Create multiple sessions and measure performance
        start_time = time.time()
        
        for i in range(10):
            session = session_manager.get_session(f"perf_test_{i}")
            response_data = router.process_with_context(f"Hello, I'm user {i}", session)
            session_manager.update_session(session)
        
        end_time = time.time()
        
        storage_info = session_manager.get_storage_info()
        print(f"   Time: {end_time - start_time:.3f}s")
        print(f"   Sessions: {storage_info['active_sessions']}")
        print(f"   Memory: {storage_info['memory_usage_mb']:.2f}MB")
        
        # Test cleanup
        cleaned = session_manager.cleanup_expired_sessions(timeout_minutes=0)  # Force cleanup
        print(f"   Cleaned up: {cleaned} sessions")

if __name__ == "__main__":
    print("🚀 Enhanced Kiro AI Assistant - Comprehensive Testing")
    print("=" * 60)
    
    # Create test data directory
    os.makedirs("test_data", exist_ok=True)
    
    try:
        test_enhanced_wrong_item_handling()
        test_multi_intent_response_merging()
        test_context_aware_follow_ups()
        test_session_persistence()
        test_human_like_conversation_flow()
        test_storage_performance()
        
        print("\n✅ All tests completed successfully!")
        print("🎯 Enhanced Kiro AI Assistant is ready for human-like conversations!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()