#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced multi-turn conversation capabilities
of the Kiro AI Assistant with session memory and entity tracking.
"""

from agents.router_agent import RouterAgent
from memory.session_manager import SessionManager
import time

def test_enhanced_conversation_flow():
    """Test the enhanced conversation flow with session memory and context awareness"""
    
    print("🚀 Testing Enhanced Kiro AI Assistant with Session Memory")
    print("=" * 60)
    
    # Initialize components
    router = RouterAgent()
    session_manager = SessionManager()
    session_id = "test_session_001"
    session = session_manager.get_session(session_id)
    
    # Test scenarios with enhanced context awareness
    test_scenarios = [
        {
            "name": "Context-Aware Follow-ups",
            "messages": [
                "Hi, I'm Sarah",
                "I need help with order #12345",
                "When will it arrive?",  # Should use session context
                "Can I cancel it?",      # Should use session context
                "Thanks!"
            ]
        },
        {
            "name": "Wrong Item with Session Memory", 
            "messages": [
                "I ordered apples but got bananas instead",
                "My order number is ABC123",  # Should remember the wrong item context
                "I want a refund",            # Should connect to previous context
            ]
        },
        {
            "name": "Multi-Intent with Context",
            "messages": [
                "I want a refund and my delivery is delayed for order #98765",
                "How much will the refund be?",  # Should use session context
                "When will my next order arrive?" # Should remember order context
            ]
        },
        {
            "name": "Low Confidence with Context",
            "messages": [
                "I need help with my laptop order",
                "001",  # Should be interpreted as order number in context
                "track it",  # Should use session context
            ]
        },
        {
            "name": "Product Context Awareness",
            "messages": [
                "Tell me about the iPhone 14",
                "How much does it cost?",  # Should use product context
                "Is it in stock?",         # Should use product context
                "I want to buy it"         # Should use product context
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🎭 {scenario['name']}")
        print("-" * 50)
        
        # Create a new session for each scenario
        session_id = f"test_{scenario['name'].lower().replace(' ', '_').replace('-', '_')}"
        session = session_manager.get_session(session_id)
        
        for i, message in enumerate(scenario['messages']):
            print(f"\n👤 User: {message}")
            
            # Process message with enhanced context
            response_data = router.process_with_context(message, session)
            
            print(f"🤖 Kiro: {response_data['response']}")
            
            # Show enhanced session state
            if i == len(scenario['messages']) - 1:  # Last message
                print(f"\n📊 Enhanced Session Summary:")
                print(f"   User: {session.user_name or 'Anonymous'}")
                print(f"   Persistent Entities: {session.persistent_entities}")
                print(f"   Current Intents: {session.current_intents}")
                print(f"   Communication Style: {session.communication_style}")
                print(f"   User Tone: {session.user_tone}")
                print(f"   Last Agent Used: {session.last_agent_used}")
                print(f"   Conversation Length: {len(session.conversation_history)} messages")
                print(f"   Detected Intents: {response_data['intents']}")
                print(f"   Agents Used: {response_data['agents_used']}")
                print(f"   Multi-Intent: {response_data['is_multi_intent']}")
            
            time.sleep(0.3)  # Small delay for readability
    
    print(f"\n✅ Enhanced Testing Complete!")
    print(f"📈 Total Sessions Created: {session_manager.get_session_count()}")

def test_context_aware_responses():
    """Test context-aware responses with session memory"""
    
    print("\n🧠 Testing Context-Aware Response Generation")
    print("=" * 60)
    
    router = RouterAgent()
    session_manager = SessionManager()
    session = session_manager.get_session("context_test")
    
    # Simulate a conversation with context building
    conversation_flow = [
        ("Hello, I'm John", "Should learn user name"),
        ("I have order #12345", "Should remember order number"),
        ("track it", "Should use order context without asking again"),
        ("cancel order", "Should use session order number"),
        ("I also want to know about iPhone pricing", "Multi-intent with context"),
        ("how much?", "Should use product context from previous message"),
    ]
    
    for message, expectation in conversation_flow:
        print(f"\n👤 User: '{message}'")
        print(f"🎯 Expected: {expectation}")
        
        response_data = router.process_with_context(message, session)
        print(f"🤖 Kiro: {response_data['response']}")
        print(f"📋 Session Entities: {session.persistent_entities}")
        print(f"🎭 Intents: {response_data['intents']}")
        print(f"🤖 Agents: {response_data['agents_used']}")

def test_multi_intent_detection():
    """Test enhanced multi-intent detection and response merging"""
    
    print("\n🔀 Testing Multi-Intent Detection and Response Merging")
    print("=" * 60)
    
    router = RouterAgent()
    session_manager = SessionManager()
    
    multi_intent_messages = [
        "I want a refund and my delivery is delayed",
        "Track my order and tell me about iPhone pricing",
        "I need support for my account and want to cancel order #123",
        "My order is late and I want to return the wrong item I received",
    ]
    
    for i, message in enumerate(multi_intent_messages):
        session = session_manager.get_session(f"multi_intent_{i}")
        
        print(f"\n📝 Message: '{message}'")
        response_data = router.process_with_context(message, session)
        
        print(f"🎯 Detected Intents: {response_data['intents']}")
        print(f"🤖 Agents Used: {response_data['agents_used']}")
        print(f"🔄 Multi-Intent: {response_data['is_multi_intent']}")
        print(f"💬 Response: {response_data['response']}")

if __name__ == "__main__":
    test_enhanced_conversation_flow()
    test_context_aware_responses()
    test_multi_intent_detection()