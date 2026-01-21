#!/usr/bin/env python3
"""
Test the conversation memory and follow-up functionality
"""

from agents.human_conversation_manager import HumanConversationManager
from memory.session_manager import SessionManager
import os

def test_conversation_memory_followups():
    """Test that follow-up messages work correctly with conversation memory"""
    
    print("🧪 TESTING CONVERSATION MEMORY & FOLLOW-UPS")
    print("=" * 60)
    
    # Initialize components
    STORAGE_TYPE = "memory"
    STORAGE_PATH = "data/sessions"
    
    human_conversation_manager = HumanConversationManager()
    session_manager = SessionManager(storage_type=STORAGE_TYPE, storage_path=STORAGE_PATH)
    
    # Test cases from the requirements
    test_conversations = [
        {
            "name": "Basic Follow-up Test",
            "messages": [
                {
                    "input": "track my order 1236",
                    "expected_contains": ["Order #1236", "shipped"],
                    "should_update_memory": True
                },
                {
                    "input": "when will it reach",
                    "expected_contains": ["Order #1236", "delivered", "expected", "tomorrow"],
                    "should_be_followup": True
                }
            ]
        },
        {
            "name": "Processing Order Follow-up",
            "messages": [
                {
                    "input": "where is my order 5555",
                    "expected_contains": ["Order #5555"],
                    "should_update_memory": True
                },
                {
                    "input": "eta?",
                    "expected_contains": ["Order #5555", "estimate", "available", "ships"],
                    "should_be_followup": True
                }
            ]
        },
        {
            "name": "Multiple Follow-ups",
            "messages": [
                {
                    "input": "track my shirt order no. 1236",
                    "expected_contains": ["Order #1236", "shipped"],
                    "should_update_memory": True
                },
                {
                    "input": "when will it reach",
                    "expected_contains": ["Order #1236", "delivered", "tomorrow"],
                    "should_be_followup": True
                },
                {
                    "input": "delivery date?",
                    "expected_contains": ["Order #1236"],
                    "should_be_followup": True
                }
            ]
        },
        {
            "name": "New Order Resets Memory",
            "messages": [
                {
                    "input": "track order 1111",
                    "expected_contains": ["Order #1111"],
                    "should_update_memory": True
                },
                {
                    "input": "track order 2222",  # New order should reset memory
                    "expected_contains": ["Order #2222"],
                    "should_update_memory": True,
                    "should_be_followup": False
                },
                {
                    "input": "when will it arrive",
                    "expected_contains": ["Order #2222"],  # Should reference new order
                    "should_be_followup": True
                }
            ]
        }
    ]
    
    all_tests_passed = True
    
    for conversation in test_conversations:
        session_id = f"test_{conversation['name'].lower().replace(' ', '_')}"
        session = session_manager.get_session(session_id)
        
        print(f"\n📝 {conversation['name']}")
        print("-" * 40)
        
        conversation_passed = True
        
        for i, test_message in enumerate(conversation['messages']):
            message_input = test_message['input']
            expected_contains = test_message['expected_contains']
            should_update_memory = test_message.get('should_update_memory', False)
            should_be_followup = test_message.get('should_be_followup', False)
            
            print(f"\nMessage {i+1}: '{message_input}'")
            
            # Check if it's detected as follow-up
            is_followup = session.is_follow_up_message(message_input)
            print(f"  Detected as follow-up: {is_followup}")
            
            # Process the message
            try:
                result = human_conversation_manager.process_human_conversation(message_input, session)
                response = result.get('response', '')
                
                print(f"  Response: {response}")
                
                # Check conversation memory state
                print(f"  Memory - Last intent: {session.last_intent}")
                print(f"  Memory - Last order ID: {session.last_order_id}")
                print(f"  Memory - Last order state: {session.last_order_state}")
                
                # Validation checks
                checks = {
                    "Follow-up detection correct": is_followup == should_be_followup,
                    "Contains expected content": all(content in response for content in expected_contains),
                    "References correct order": any(content in response for content in expected_contains if "Order #" in content),
                    "No greeting fallback": not any(phrase in response.lower() for phrase in ["hello", "i'm kiro", "how can i help"]),
                    "Memory updated correctly": (session.last_intent is not None) if should_update_memory else True
                }
                
                message_passed = True
                for check_name, passed in checks.items():
                    status = "✅" if passed else "❌"
                    print(f"    {status} {check_name}: {passed}")
                    if not passed:
                        message_passed = False
                        conversation_passed = False
                
                if message_passed:
                    print(f"  🎯 Message {i+1} PASSED")
                else:
                    print(f"  ❌ Message {i+1} FAILED")
                
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
                import traceback
                traceback.print_exc()
                conversation_passed = False
        
        if conversation_passed:
            print(f"\n✅ {conversation['name']} - ALL TESTS PASSED")
        else:
            print(f"\n❌ {conversation['name']} - SOME TESTS FAILED")
            all_tests_passed = False
    
    print(f"\n🎯 FINAL RESULTS")
    print("=" * 60)
    
    if all_tests_passed:
        print("🎉 SUCCESS: All conversation memory tests passed!")
        print("✅ Follow-up detection working correctly")
        print("✅ Conversation memory maintained properly")
        print("✅ No greeting fallbacks for follow-ups")
        print("✅ Order context preserved between messages")
    else:
        print("❌ FAILED: Some conversation memory tests failed!")
        print("❌ Follow-up functionality needs fixes")
    
    return all_tests_passed

if __name__ == "__main__":
    success = test_conversation_memory_followups()
    exit(0 if success else 1)