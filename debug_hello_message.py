#!/usr/bin/env python3
"""
Debug why hello message is asking for order number
"""

from agents.router_agent import RouterAgent
from memory.session_manager import SessionManager

def debug_hello_after_refund():
    """Debug the hello message after refund"""
    
    print("🔍 Debugging Hello Message After Refund")
    print("=" * 50)
    
    router = RouterAgent()
    session_manager = SessionManager(storage_type="memory")
    session = session_manager.get_session("debug_hello_session")
    
    # First message - refund request
    print("Step 1: Refund request")
    message1 = "i want refund of my buds 3 order no. 1234"
    result1 = router.process_with_context(message1, session)
    print(f"Message: {message1}")
    print(f"Response: {result1['response']}")
    print(f"Session active order: {session.active_order_id}")
    print(f"Session resolution lock: {session.active_resolution_lock}")
    
    # Second message - hello
    print(f"\nStep 2: Hello message")
    message2 = "hello"
    result2 = router.process_with_context(message2, session)
    print(f"Message: {message2}")
    print(f"Response: {result2['response']}")
    print(f"Session active order: {session.active_order_id}")
    print(f"Session resolution lock: {session.active_resolution_lock}")

if __name__ == "__main__":
    debug_hello_after_refund()