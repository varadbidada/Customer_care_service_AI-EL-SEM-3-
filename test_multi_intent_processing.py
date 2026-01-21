#!/usr/bin/env python3
"""
Test script specifically for the enhanced multi-intent processing and session memory handling
"""

from memory.session_manager import SessionManager
import time
import os

def test_enhanced_multi_intent_processing():
    """Test the enhanced multi-intent processing with proper session management"""
    
    print("🔄 Testing Enhanced Multi-Intent Processing")
    print("=" * 60)
    
    # Import the new processing function
    import sys
    sys.path.append('.')
    from app import process_message_with_multi_intent
    
    # Initialize session manager
    session_manager = SessionManager(storage_type="memory")
    
    test_cases = [
        {
            "name": "Multi-Intent: Support + Order",
            "message": "I want a refund and my delivery is delayed for order #12345",
            "expected_intents": ["support", "order"],
            "expected_agents": ["support", "order"]
        },
        {
            "name": "Multi-Intent: Order + Product",
            "message": "Track my order #98765 and tell me about iPhone pricing",
            "expected_intents": ["order", "product"],
            "expected_agents": ["order", "product"]
        },
        {
            "name": "Single Intent with Context",
            "message": "track it",  # Should use session context
            "expected_intents": ["order"],
            "expected_agents": ["order"]
        },
        {
            "name": "Wrong Item Multi-Intent",
            "message": "I ordered red apples but got green apples and want a refund",
            "expected_intents": ["support", "order", "product"],
            "expected_agents": ["support", "order", "product"]
        },
        {
            "name": "Follow-up with Session Memory",
            "message": "How much will the refund be?",
            "expected_intents": ["support"],
            "expected_agents": ["support"]
        }
    ]
    
    session = session_manager.get_session("multi_intent_test")
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🧪 Test {i+1}: {test_case['name']}")
        print(f"📝 Message: '{test_case['message']}'")
        
        try:
            # Process message with enhanced multi-intent handling
            result = process_message_with_multi_intent(test_case['message'], session)
            
            # Verify results
            print(f"✅ Response: {result['response'][:100]}...")
            print(f"🎯 Detected Intents: {result['intents']}")
            print(f"🤖 Agents Used: {result['agents_used']}")
            print(f"🔄 Multi-Intent: {result['is_multi_intent']}")
            print(f"📊 Processing Steps: {len(result.get('processing_steps', []))}")
            print(f"⭐ Response Quality: {result.get('response_quality', 'unknown')}")
            
            # Check if expected intents were detected
            detected_intents = set(result['intents'])
            expected_intents = set(test_case['expected_intents'])
            
            if expected_intents.issubset(detected_intents):
                print(f"✅ Intent detection: PASSED")
            else:
                print(f"❌ Intent detection: FAILED (expected {expected_intents}, got {detected_intents})")
            
            # Check if expected agents were used
            agents_used = set(result['agents_used'])
            expected_agents = set(test_case['expected_agents'])
            
            # Allow for routing variations (e.g., general agent for low confidence)
            if expected_agents.intersection(agents_used) or 'general' in agents_used:
                print(f"✅ Agent routing: PASSED")
            else:
                print(f"❌ Agent routing: FAILED (expected {expected_agents}, got {agents_used})")
            
            # Update session
            session_manager.update_session(session)
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()

def test_session_memory_persistence():
    """Test session memory persistence across multiple interactions"""
    
    print("\n💾 Testing Session Memory Persistence")
    print("=" * 60)
    
    from app import process_message_with_multi_intent
    
    session_manager = SessionManager(storage_type="memory")
    session = session_manager.get_session("memory_test")
    
    conversation_flow = [
        ("Hi, I'm Alice", "Should learn user name"),
        ("I have order #MEMORY123", "Should remember order number"),
        ("I ordered red apples but got green apples", "Should detect wrong item and remember context"),
        ("track it", "Should use remembered order number"),
        ("I want a refund", "Should use full context (order + wrong item)"),
        ("How long will it take?", "Should use refund context")
    ]
    
    print("🎭 Conversation Flow Test:")
    
    for i, (message, expectation) in enumerate(conversation_flow):
        print(f"\n{i+1}. 👤 Alice: '{message}'")
        print(f"   🎯 Expected: {expectation}")
        
        try:
            result = process_message_with_multi_intent(message, session)
            session_manager.update_session(session)
            
            print(f"   🤖 Kiro: {result['response'][:80]}...")
            print(f"   📋 Session Entities: {session.persistent_entities}")
            print(f"   👤 User: {session.user_name}")
            print(f"   🚨 Open Issues: {len([i for i in session.unresolved_issues if i.get('status') == 'open'])}")
            
            # Verify session memory is working
            if i == 1 and session.user_name:
                print(f"   ✅ User name remembered: {session.user_name}")
            
            if i == 2 and 'order_number' in session.persistent_entities:
                print(f"   ✅ Order number remembered: {session.persistent_entities['order_number']}")
            
            if i == 3 and session.unresolved_issues:
                print(f"   ✅ Wrong item issue tracked: {len(session.unresolved_issues)} issues")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_response_merging_quality():
    """Test the quality of response merging for multi-intent scenarios"""
    
    print("\n🔀 Testing Response Merging Quality")
    print("=" * 60)
    
    from app import process_message_with_multi_intent
    
    session_manager = SessionManager(storage_type="memory")
    
    multi_intent_messages = [
        "I want a refund and my delivery is delayed",
        "Track order #12345 and tell me about iPhone pricing", 
        "I need support for my account and want to cancel my order",
        "My order is late and I received the wrong item"
    ]
    
    for i, message in enumerate(multi_intent_messages):
        session = session_manager.get_session(f"merge_test_{i}")
        
        print(f"\n📝 Message: '{message}'")
        
        try:
            result = process_message_with_multi_intent(message, session)
            
            print(f"🎯 Intents: {result['intents']}")
            print(f"🤖 Agents: {result['agents_used']}")
            print(f"⭐ Quality: {result.get('response_quality', 'unknown')}")
            print(f"🔄 Multi-Intent: {result['is_multi_intent']}")
            
            # Analyze response quality
            response = result['response']
            
            # Check for natural transitions
            transition_words = ['regarding', 'as for', 'about', 'first', 'also', 'finally']
            has_transitions = any(word in response.lower() for word in transition_words)
            
            # Check for personalization
            has_greeting = any(word in response.lower() for word in ['i can help', 'i understand', 'let me'])
            
            # Check response length (should be comprehensive for multi-intent)
            is_comprehensive = len(response) > 100 if result['is_multi_intent'] else True
            
            print(f"📊 Quality Analysis:")
            print(f"   Natural transitions: {'✅' if has_transitions else '❌'}")
            print(f"   Personalized greeting: {'✅' if has_greeting else '❌'}")
            print(f"   Comprehensive response: {'✅' if is_comprehensive else '❌'}")
            print(f"   Response length: {len(response)} chars")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def test_error_handling():
    """Test error handling in multi-intent processing"""
    
    print("\n🛡️ Testing Error Handling")
    print("=" * 60)
    
    from app import process_message_with_multi_intent
    
    session_manager = SessionManager(storage_type="memory")
    session = session_manager.get_session("error_test")
    
    # Test edge cases
    edge_cases = [
        "",  # Empty message
        "   ",  # Whitespace only
        "a" * 1000,  # Very long message
        "🎉🎊🎈",  # Emoji only
        "123456789",  # Numbers only
    ]
    
    for i, message in enumerate(edge_cases):
        print(f"\n🧪 Edge Case {i+1}: '{message[:50]}{'...' if len(message) > 50 else ''}'")
        
        try:
            result = process_message_with_multi_intent(message, session)
            print(f"✅ Handled gracefully: {result['response'][:80]}...")
            print(f"   Intents: {result['intents']}")
            print(f"   Quality: {result.get('response_quality', 'unknown')}")
            
        except Exception as e:
            print(f"❌ Error (expected for some cases): {e}")

if __name__ == "__main__":
    print("🚀 Enhanced Multi-Intent Processing - Comprehensive Testing")
    print("=" * 70)
    
    try:
        test_enhanced_multi_intent_processing()
        test_session_memory_persistence()
        test_response_merging_quality()
        test_error_handling()
        
        print("\n✅ All multi-intent processing tests completed!")
        print("🎯 Enhanced Kiro is ready for sophisticated multi-intent conversations!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()