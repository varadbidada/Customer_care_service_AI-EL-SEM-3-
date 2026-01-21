#!/usr/bin/env python3
"""
Test the clear session functionality to ensure no context carryover
"""

from agents.human_conversation_manager import HumanConversationManager
from memory.session_manager import SessionManager
import os

def test_clear_session_no_context_carryover():
    """Test that clearing session completely removes all context"""
    
    print("🧪 TESTING CLEAR SESSION - NO CONTEXT CARRYOVER")
    print("=" * 60)
    
    # Initialize components
    STORAGE_TYPE = "memory"  # Use memory for testing
    STORAGE_PATH = "data/sessions"
    
    human_conversation_manager = HumanConversationManager()
    session_manager = SessionManager(storage_type=STORAGE_TYPE, storage_path=STORAGE_PATH)
    
    session_id = "test_clear_session"
    
    print("📝 PHASE 1: Build up context")
    print("-" * 30)
    
    # Build up some context in the session
    context_messages = [
        "Hi, my name is John",
        "I want to track my order 4457",
        "I ordered shampoo but got soap instead"
    ]
    
    session = session_manager.get_session(session_id)
    
    for i, message in enumerate(context_messages):
        print(f"Message {i+1}: '{message}'")
        result = human_conversation_manager.process_human_conversation(message, session)
        response = result.get('response', '')
        print(f"Response: {response[:100]}...")
        
        # Update session
        session_manager.update_session(session)
    
    # Check that context was built up
    print(f"\n📊 Context built up:")
    print(f"  User name: {session.user_name}")
    print(f"  Conversation history: {len(session.conversation_history)} messages")
    print(f"  Order states: {len(session.order_states)} orders")
    print(f"  Persistent entities: {len(session.persistent_entities)} entities")
    print(f"  Active order ID: {session.active_order_id}")
    print(f"  Last entities: {len(session.last_entities)} entity types")
    
    # Verify context exists
    has_context = (
        session.user_name is not None or
        len(session.conversation_history) > 0 or
        len(session.order_states) > 0 or
        len(session.persistent_entities) > 0 or
        session.active_order_id is not None or
        len(session.last_entities) > 0
    )
    
    if has_context:
        print("✅ Context successfully built up")
    else:
        print("❌ Failed to build up context")
        return
    
    print(f"\n🧹 PHASE 2: Clear session")
    print("-" * 30)
    
    # Clear the session
    session_manager.clear_session(session_id)
    
    print(f"\n🔍 PHASE 3: Test fresh session")
    print("-" * 30)
    
    # Get a "new" session with the same ID (should be completely fresh)
    fresh_session = session_manager.get_session(session_id)
    
    print(f"📊 Fresh session state:")
    print(f"  User name: {fresh_session.user_name}")
    print(f"  Conversation history: {len(fresh_session.conversation_history)} messages")
    print(f"  Order states: {len(fresh_session.order_states)} orders")
    print(f"  Persistent entities: {len(fresh_session.persistent_entities)} entities")
    print(f"  Active order ID: {fresh_session.active_order_id}")
    print(f"  Last entities: {len(fresh_session.last_entities)} entity types")
    print(f"  Communication style: {fresh_session.communication_style}")
    print(f"  User tone: {fresh_session.user_tone}")
    print(f"  Resolved state: {fresh_session.resolved}")
    
    # Check conversation history before adding new message
    initial_history_length = len(fresh_session.conversation_history)
    
    # Test with a new message to ensure no context carryover
    test_message = "track order 1234"
    print(f"\nTest message: '{test_message}'")
    
    result = human_conversation_manager.process_human_conversation(test_message, fresh_session)
    response = result.get('response', '')
    print(f"Response: {response}")
    
    # Validation checks
    print(f"\n🔍 VALIDATION CHECKS:")
    print("-" * 30)
    
    checks = {
        "No user name": fresh_session.user_name is None,
        "Empty conversation history initially": initial_history_length == 0,  # Check before new message
        "No order states from before": len([oid for oid in fresh_session.order_states.keys() if oid != "1234"]) == 0,
        "No persistent entities from before": len(fresh_session.persistent_entities) <= 1,  # Only new order number
        "No active context from before": fresh_session.active_order_id != "4457",  # Should not remember old order
        "Default communication style": fresh_session.communication_style == "friendly",
        "Default user tone": fresh_session.user_tone == "neutral",
        "Not resolved": not fresh_session.resolved,
        "Response mentions new order": "1234" in response,
        "Response doesn't mention old order": "4457" not in response,
        "Response doesn't mention old name": "John" not in response.lower()
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}: {passed}")
        if not passed:
            all_passed = False
    
    print(f"\n🎯 FINAL RESULT:")
    print("=" * 60)
    
    if all_passed:
        print("🎉 SUCCESS: Clear session works perfectly!")
        print("✅ No context carryover detected")
        print("✅ Fresh session behaves like a new conversation")
        print("✅ All validation checks passed")
    else:
        print("❌ FAILED: Context carryover detected!")
        print("❌ Clear session is not working properly")
        print("❌ Some validation checks failed")
    
    return all_passed

if __name__ == "__main__":
    success = test_clear_session_no_context_carryover()
    exit(0 if success else 1)