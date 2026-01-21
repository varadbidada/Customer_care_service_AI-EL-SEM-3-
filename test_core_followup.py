#!/usr/bin/env python3
"""
Test the core follow-up functionality as specified in requirements
"""

from agents.human_conversation_manager import HumanConversationManager
from memory.session_manager import SessionManager
import os

def test_core_followup_requirements():
    """Test the exact requirements from the bug report"""
    
    print("🧪 TESTING CORE FOLLOW-UP REQUIREMENTS")
    print("=" * 60)
    
    # Initialize components
    STORAGE_TYPE = "memory"
    STORAGE_PATH = "data/sessions"
    
    human_conversation_manager = HumanConversationManager()
    session_manager = SessionManager(storage_type=STORAGE_TYPE, storage_path=STORAGE_PATH)
    
    # Test the exact examples from the requirements
    test_cases = [
        {
            "name": "Basic Follow-up (Requirement Example 1)",
            "conversation": [
                ("track my order 1236", ["Order #1236", "shipped"]),
                ("when will it reach", ["Order #1236"])  # Must reference same order
            ]
        },
        {
            "name": "Processing Order Follow-up (Requirement Example 2)", 
            "conversation": [
                ("where is my order 5555", ["Order #5555"]),
                ("eta?", ["Order #5555"])  # Must reference same order
            ]
        },
        {
            "name": "Multiple Follow-ups",
            "conversation": [
                ("track my shirt order no. 1236", ["Order #1236"]),
                ("when will it reach", ["Order #1236"]),
                ("delivery date?", ["Order #1236"])
            ]
        }
    ]
    
    all_tests_passed = True
    
    for test_case in test_cases:
        session_id = f"test_{test_case['name'].lower().replace(' ', '_').replace('(', '').replace(')', '')}"
        session = session_manager.get_session(session_id)
        
        print(f"\n📝 {test_case['name']}")
        print("-" * 40)
        
        test_passed = True
        
        for i, (message_input, expected_contains) in enumerate(test_case['conversation']):
            print(f"\nMessage {i+1}: '{message_input}'")
            
            # Check follow-up detection for non-first messages
            if i > 0:
                is_followup = session.is_follow_up_message(message_input)
                print(f"  Follow-up detected: {is_followup}")
                if not is_followup:
                    print(f"  ❌ FAILED: Should be detected as follow-up")
                    test_passed = False
                    continue
            
            # Process the message
            try:
                result = human_conversation_manager.process_human_conversation(message_input, session)
                response = result.get('response', '')
                
                print(f"  Response: {response}")
                
                # Core validation checks
                checks = {
                    "Contains expected content": all(content in response for content in expected_contains),
                    "No greeting fallback": not any(phrase in response.lower() for phrase in ["hello", "i'm kiro", "how can i help"]),
                    "No order ID request": "order number" not in response.lower() or "provide" not in response.lower(),
                    "References order": any("#" in content for content in expected_contains) and any(content in response for content in expected_contains if "#" in content)
                }
                
                message_passed = True
                for check_name, passed in checks.items():
                    status = "✅" if passed else "❌"
                    print(f"    {status} {check_name}: {passed}")
                    if not passed:
                        message_passed = False
                        test_passed = False
                
                # Check conversation memory state
                if i == 0:  # First message should set memory
                    if session.last_intent == "tracking" and session.last_order_id:
                        print(f"    ✅ Conversation memory set: intent={session.last_intent}, order={session.last_order_id}")
                    else:
                        print(f"    ❌ Conversation memory not set properly")
                        test_passed = False
                
                if message_passed:
                    print(f"  🎯 Message {i+1} PASSED")
                else:
                    print(f"  ❌ Message {i+1} FAILED")
                
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
                test_passed = False
        
        if test_passed:
            print(f"\n✅ {test_case['name']} - PASSED")
        else:
            print(f"\n❌ {test_case['name']} - FAILED")
            all_tests_passed = False
    
    print(f"\n🎯 CORE REQUIREMENTS VALIDATION")
    print("=" * 60)
    
    # Test specific requirements
    session = session_manager.get_session("requirements_test")
    
    print("\n1. Testing conversation memory persistence...")
    result1 = human_conversation_manager.process_human_conversation("track my order 1236", session)
    print(f"   First message: {result1.get('response', '')[:50]}...")
    print(f"   Memory set - Intent: {session.last_intent}, Order: {session.last_order_id}")
    
    result2 = human_conversation_manager.process_human_conversation("when will it reach", session)
    print(f"   Follow-up: {result2.get('response', '')[:50]}...")
    
    memory_persisted = session.last_intent == "tracking" and session.last_order_id == "1236"
    print(f"   ✅ Memory persisted: {memory_persisted}")
    
    print("\n2. Testing follow-up detection...")
    followup_detected = session.is_follow_up_message("when will it reach")
    print(f"   ✅ Follow-up detected: {followup_detected}")
    
    print("\n3. Testing order context preservation...")
    order_preserved = "1236" in result2.get('response', '')
    print(f"   ✅ Order context preserved: {order_preserved}")
    
    print("\n4. Testing no greeting fallback...")
    no_greeting = not any(phrase in result2.get('response', '').lower() for phrase in ["hello", "i'm kiro", "how can i help"])
    print(f"   ✅ No greeting fallback: {no_greeting}")
    
    core_requirements_met = memory_persisted and followup_detected and order_preserved and no_greeting
    
    if all_tests_passed and core_requirements_met:
        print(f"\n🎉 SUCCESS: All core follow-up requirements met!")
        print("✅ Conversation memory working")
        print("✅ Follow-up detection working") 
        print("✅ Order context preserved")
        print("✅ No greeting fallbacks")
        print("✅ No conversation resets")
    else:
        print(f"\n❌ FAILED: Some core requirements not met!")
    
    return all_tests_passed and core_requirements_met

if __name__ == "__main__":
    success = test_core_followup_requirements()
    exit(0 if success else 1)