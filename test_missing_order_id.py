#!/usr/bin/env python3
"""
Test the fix for tracking requests without order IDs
"""

from agents.router_agent import RouterAgent
from memory.session_manager import SessionMemory

def test_tracking_without_order_id():
    """Test tracking requests without order numbers"""
    
    print("🧪 TESTING TRACKING WITHOUT ORDER ID")
    print("=" * 50)
    
    router = RouterAgent()
    
    # Test cases that should ask for order number (not crash)
    test_cases = [
        "i want to track my order of shampoo",  # The failing case
        "track my order",
        "where is my order",
        "order status",
        "delivery status",
        "when will my order arrive"
    ]
    
    for test_message in test_cases:
        session = SessionMemory(f"test_{hash(test_message)}")
        
        print(f"\nInput: '{test_message}'")
        
        try:
            result = router.process_with_context(test_message, session)
            response = result['response']
            intents = result.get('intents', [])
            agents_used = result.get('agents_used', [])
            
            print(f"Response: {response}")
            print(f"Intents: {intents}")
            print(f"Agents: {agents_used}")
            
            # Check if it asks for order number instead of crashing
            asks_for_order = any(phrase in response.lower() for phrase in [
                "order number", "provide", "please", "track your order"
            ])
            
            has_error = "system error" in response.lower() or "cannot access" in response.lower()
            
            if asks_for_order and not has_error:
                print("✅ SUCCESS: Asks for order number")
            elif has_error:
                print("❌ FAILED: Still showing system error")
            else:
                print("❌ FAILED: Unexpected response")
                
        except Exception as e:
            print(f"❌ CRASH: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_tracking_without_order_id()