#!/usr/bin/env python3
"""
Test the specific bug case mentioned in the request
"""

from agents.router_agent import RouterAgent
from memory.session_manager import SessionMemory

def test_specific_bug_case():
    """Test the exact case mentioned in the bug report"""
    
    print("🐛 TESTING SPECIFIC BUG CASE")
    print("=" * 50)
    
    # Initialize components
    router = RouterAgent()
    session = SessionMemory("test_session")
    
    # The exact failing case from the bug report
    test_message = "i want to track my order of shampoo 4457"
    
    print(f"Input: '{test_message}'")
    print("Expected: Direct tracking response")
    print("Expected: NO refund/replacement prompts")
    print("Expected: NO crashes")
    print("-" * 40)
    
    try:
        result = router.process_with_context(test_message, session)
        response = result['response']
        intents = result.get('intents', [])
        agents_used = result.get('agents_used', [])
        
        print(f"✅ Response: {response}")
        print(f"✅ Intents: {intents}")
        print(f"✅ Agents Used: {agents_used}")
        
        # Check for the specific issues mentioned in the bug report
        has_refund_replacement_prompt = any(phrase in response.lower() for phrase in [
            "refund", "replacement", "how would you like me to help", 
            "refund, replacement, cancellation"
        ])
        
        has_order_info_error = "cannot access order information" in response.lower()
        
        has_tracking_info = any(word in response.lower() for word in [
            "shipped", "on the way", "delivered", "processing"
        ])
        
        has_order_id = "#4457" in response
        
        print("\n🔍 BUG FIX VALIDATION:")
        print(f"  ❌ Has refund/replacement prompt: {has_refund_replacement_prompt}")
        print(f"  ❌ Has 'Cannot access order information' error: {has_order_info_error}")
        print(f"  ✅ Has tracking information: {has_tracking_info}")
        print(f"  ✅ Has order ID: {has_order_id}")
        
        if (not has_refund_replacement_prompt and 
            not has_order_info_error and 
            has_tracking_info and 
            has_order_id):
            print("\n🎯 BUG FIX SUCCESSFUL!")
            print("✅ No resolution prompts")
            print("✅ No crashes")
            print("✅ Direct tracking response")
        else:
            print("\n❌ BUG FIX FAILED!")
            if has_refund_replacement_prompt:
                print("❌ Still showing resolution prompts")
            if has_order_info_error:
                print("❌ Still showing order access errors")
            if not has_tracking_info:
                print("❌ Missing tracking information")
            if not has_order_id:
                print("❌ Missing order ID in response")
                
    except Exception as e:
        print(f"❌ CRASH DETECTED: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ BUG FIX FAILED - System still crashes!")

if __name__ == "__main__":
    test_specific_bug_case()