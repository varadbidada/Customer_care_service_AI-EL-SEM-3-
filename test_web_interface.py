#!/usr/bin/env python3
"""
Test the tracking fix through the web interface flow
"""

from agents.human_conversation_manager import HumanConversationManager
from memory.session_manager import SessionManager
import os

def test_web_interface_flow():
    """Test the tracking fix through the complete web interface flow"""
    
    print("🌐 TESTING WEB INTERFACE FLOW")
    print("=" * 50)
    
    # Initialize components like the web app does
    STORAGE_TYPE = os.getenv('SESSION_STORAGE', 'memory')  # Use memory for testing
    STORAGE_PATH = os.getenv('SESSION_STORAGE_PATH', 'data/sessions')
    
    human_conversation_manager = HumanConversationManager()
    session_manager = SessionManager(storage_type=STORAGE_TYPE, storage_path=STORAGE_PATH)
    
    # Test the exact failing case
    test_message = "i want to track my order of shampoo 4457"
    session_id = "test_web_session"
    
    print(f"Input: '{test_message}'")
    print("Testing through HumanConversationManager...")
    print("-" * 40)
    
    try:
        # Get session like the web app does
        session = session_manager.get_session(session_id)
        
        # Process through human conversation manager
        result = human_conversation_manager.process_human_conversation(test_message, session)
        
        response_text = result.get('response', '')
        conversation_state = result.get('conversation_state', '')
        is_human_flow = result.get('is_human_flow', False)
        
        print(f"✅ Response: {response_text}")
        print(f"✅ Conversation State: {conversation_state}")
        print(f"✅ Is Human Flow: {is_human_flow}")
        
        # Validate the response
        has_refund_replacement_prompt = any(phrase in response_text.lower() for phrase in [
            "refund", "replacement", "how would you like me to help", 
            "refund, replacement, cancellation"
        ])
        
        has_order_info_error = "cannot access order information" in response_text.lower()
        
        has_tracking_info = any(word in response_text.lower() for word in [
            "shipped", "on the way", "delivered", "processing"
        ])
        
        has_order_id = "#4457" in response_text
        
        print("\n🔍 WEB INTERFACE VALIDATION:")
        print(f"  ❌ Has refund/replacement prompt: {has_refund_replacement_prompt}")
        print(f"  ❌ Has 'Cannot access order information' error: {has_order_info_error}")
        print(f"  ✅ Has tracking information: {has_tracking_info}")
        print(f"  ✅ Has order ID: {has_order_id}")
        print(f"  ✅ Response is string: {isinstance(response_text, str)}")
        
        if (not has_refund_replacement_prompt and 
            not has_order_info_error and 
            has_tracking_info and 
            has_order_id and
            isinstance(response_text, str)):
            print("\n🎯 WEB INTERFACE FIX SUCCESSFUL!")
            print("✅ No resolution prompts")
            print("✅ No crashes")
            print("✅ Direct tracking response")
            print("✅ Proper response format")
        else:
            print("\n❌ WEB INTERFACE FIX FAILED!")
            
        # Test a few more tracking cases
        print("\n🔄 Testing additional tracking cases...")
        additional_cases = [
            "track 1234",
            "where is order 5678",
            "order 9999 status"
        ]
        
        for case in additional_cases:
            print(f"\nTesting: '{case}'")
            session = session_manager.get_session(f"test_{case}")
            result = human_conversation_manager.process_human_conversation(case, session)
            response = result.get('response', '')
            
            has_tracking = any(word in response.lower() for word in ["shipped", "processing", "delivered", "on the way"])
            has_resolution_prompt = any(phrase in response.lower() for phrase in ["refund", "replacement", "how would you like"])
            
            if has_tracking and not has_resolution_prompt:
                print(f"  ✅ SUCCESS: {response}")
            else:
                print(f"  ❌ FAILED: {response}")
                
    except Exception as e:
        print(f"❌ WEB INTERFACE CRASH: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ WEB INTERFACE FIX FAILED - System still crashes!")

if __name__ == "__main__":
    test_web_interface_flow()