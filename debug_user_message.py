#!/usr/bin/env python3
"""
Debug the exact user message to see what's happening
"""

from agents.nlp_processor import NLPProcessor
from agents.router_agent import RouterAgent
from memory.session_manager import SessionManager

def debug_user_message():
    """Debug the exact message the user sent"""
    
    print("🔍 Debugging User Message")
    print("=" * 50)
    
    # The exact message from user
    message = "i want refund of my buds 3 order no. 1234"
    
    print(f"User message: '{message}'")
    
    # Test complete request detection
    nlp = NLPProcessor()
    complete_request = nlp.detect_complete_request(message)
    
    print(f"\nComplete request detection:")
    print(f"  Order ID: {complete_request['order_id']}")
    print(f"  Issue: {complete_request['issue']}")
    print(f"  Resolution: {complete_request['resolution']}")
    print(f"  Is Complete: {complete_request['is_complete']}")
    
    # Test full NLP processing
    nlp_result = nlp.process_message(message)
    print(f"\nFull NLP processing:")
    print(f"  Intents: {nlp_result['intents']}")
    print(f"  Entities: {nlp_result['entities']}")
    print(f"  Confidence: {nlp_result['confidence_scores']}")
    
    # Test router processing
    router = RouterAgent()
    session_manager = SessionManager(storage_type="memory")
    session = session_manager.get_session("debug_session")
    
    print(f"\nRouter processing:")
    result = router.process_with_context(message, session)
    print(f"  Response: {result['response']}")
    print(f"  Agents used: {result['agents_used']}")
    print(f"  Issue context: {result['issue_context']}")

if __name__ == "__main__":
    debug_user_message()