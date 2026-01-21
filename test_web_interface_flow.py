#!/usr/bin/env python3
"""
Test the exact flow that happens in the web interface
"""

from agents.human_conversation_manager import HumanConversationManager
from memory.session_manager import SessionManager

def test_web_interface_flow():
    """Test the exact flow that happens in the web interface"""
    
    print("🌐 Testing Web Interface Flow")
    print("=" * 50)
    
    # This is exactly what happens in app.py
    human_conversation_manager = HumanConversationManager()
    session_manager = SessionManager(storage_type="memory")
    
    # Test the exact user messages
    session = session_manager.get_session("web_test_session")
    
    # First message - refund request
    print("Step 1: User refund request")
    message1 = "i want refund of my buds 3 order no. 1234"
    result1 = human_conversation_manager.process_human_conversation(message1, session)
    print(f"Message: {message1}")
    print(f"Response: {result1.get('response', 'No response')}")
    
    # Second message - hello
    print(f"\nStep 2: User says hello")
    message2 = "hello"
    result2 = human_conversation_manager.process_human_conversation(message2, session)
    print(f"Message: {message2}")
    print(f"Response: {result2.get('response', 'No response')}")

if __name__ == "__main__":
    test_web_interface_flow()