#!/usr/bin/env python3
"""
Final validation test for follow-up functionality with correct order states
"""

from agents.human_conversation_manager import HumanConversationManager
from memory.session_manager import SessionManager

def test_final_followup_validation():
    """Test that follow-ups work with correct order states"""
    
    print("🎯 FINAL FOLLOW-UP VALIDATION")
    print("=" * 50)
    
    # Initialize components
    human_conversation_manager = HumanConversationManager()
    session_manager = SessionManager(storage_type="memory")
    
    # Test case: Complete follow-up flow with state verification
    session = session_manager.get_session("final_validation")
    
    print("\n1. Initial tracking request")
    result1 = human_conversation_manager.process_human_conversation("track my order 1236", session)
    print(f"   Response: {result1.get('response', '')}")
    print(f"   Conversation memory - Intent: {session.last_intent}")
    print(f"   Conversation memory - Order ID: {session.last_order_id}")
    print(f"   Conversation memory - Order State: {session.last_order_state}")
    
    # Verify order state in session
    order_state = session.get_order_state("1236")
    print(f"   Actual order status: {order_state.status.value if order_state else 'None'}")
    print(f"   Order ETA: {order_state.delivery_eta if order_state else 'None'}")
    
    print("\n2. Follow-up question")
    result2 = human_conversation_manager.process_human_conversation("when will it reach", session)
    print(f"   Response: {result2.get('response', '')}")
    print(f"   Follow-up detected: {session.is_follow_up_message('when will it reach')}")
    
    print("\n3. Another follow-up")
    result3 = human_conversation_manager.process_human_conversation("eta?", session)
    print(f"   Response: {result3.get('response', '')}")
    
    print("\n4. Validation checks")
    checks = {
        "Order state is shipped": session.last_order_state == "shipped",
        "Order ID preserved": session.last_order_id == "1236",
        "Intent preserved": session.last_intent == "tracking",
        "Follow-up responses include ETA": "tomorrow" in result2.get('response', '').lower(),
        "No greeting fallbacks": not any(phrase in result2.get('response', '').lower() for phrase in ["hello", "i'm kiro"]),
        "Order context preserved": "1236" in result2.get('response', '') and "1236" in result3.get('response', '')
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}: {passed}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print(f"\n🎉 FINAL VALIDATION PASSED!")
        print("✅ Order states are correctly set to 'shipped'")
        print("✅ Conversation memory preserves correct state")
        print("✅ Follow-up responses include delivery ETA")
        print("✅ All context is preserved between messages")
    else:
        print(f"\n❌ FINAL VALIDATION FAILED!")
    
    return all_passed

if __name__ == "__main__":
    success = test_final_followup_validation()
    exit(0 if success else 1)