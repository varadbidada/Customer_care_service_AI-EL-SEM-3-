#!/usr/bin/env python3
"""
Test script to verify the tracking bug fix
"""

from agents.router_agent import RouterAgent
from agents.nlp_processor import NLPProcessor
from memory.session_manager import SessionMemory
import sys

def test_tracking_queries():
    """Test that tracking queries work correctly without resolution prompts"""
    
    print("🧪 TESTING TRACKING BUG FIX")
    print("=" * 50)
    
    # Initialize components
    router = RouterAgent()
    nlp = NLPProcessor()
    session = SessionMemory("test_session")
    
    # Test cases that should trigger tracking short-circuit
    test_cases = [
        "i want to track my order of shampoo 4457",
        "track 1234",
        "where is my order 8899",
        "order 5555 status",
        "when will order 7777 arrive",
        "delivery status for 9999"
    ]
    
    print("🔍 Testing NLP Complete Request Detection:")
    print("-" * 40)
    
    for test_message in test_cases:
        print(f"\nInput: '{test_message}'")
        
        # Test NLP detection
        complete_request = nlp.detect_complete_request(test_message)
        print(f"  Order ID: {complete_request['order_id']}")
        print(f"  Issue: {complete_request['issue']}")
        print(f"  Resolution: {complete_request['resolution']}")
        print(f"  Is Complete: {complete_request['is_complete']}")
        print(f"  Is Tracking: {complete_request.get('is_tracking', False)}")
        
        # Verify tracking detection
        if complete_request.get('is_tracking') and complete_request['order_id']:
            print("  ✅ TRACKING SHORT-CIRCUIT DETECTED")
        else:
            print("  ❌ TRACKING SHORT-CIRCUIT FAILED")
    
    print("\n🤖 Testing Router Agent Processing:")
    print("-" * 40)
    
    for test_message in test_cases:
        print(f"\nInput: '{test_message}'")
        
        # Test router processing
        try:
            result = router.process_with_context(test_message, session)
            response = result['response']
            intents = result.get('intents', [])
            agents_used = result.get('agents_used', [])
            
            print(f"  Response: {response}")
            print(f"  Intents: {intents}")
            print(f"  Agents Used: {agents_used}")
            
            # Validation checks
            has_order_id = "#" in response and any(char.isdigit() for char in response)
            has_status = any(word in response.lower() for word in ["shipped", "processing", "delivered", "being processed", "on the way"])
            has_question = "?" in response
            has_resolution_prompt = any(phrase in response.lower() for phrase in ["refund", "replacement", "cancellation", "how would you like"])
            
            print(f"  ✅ Contains order ID: {has_order_id}")
            print(f"  ✅ Contains order status: {has_status}")
            print(f"  ❌ Contains question: {has_question}")
            print(f"  ❌ Contains resolution prompt: {has_resolution_prompt}")
            
            if has_order_id and has_status and not has_question and not has_resolution_prompt:
                print("  🎯 TRACKING FIX SUCCESS")
            else:
                print("  ❌ TRACKING FIX FAILED")
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🔍 Testing Non-Tracking Queries (Should Still Work):")
    print("-" * 40)
    
    non_tracking_cases = [
        "refund order 1234",
        "cancel my order 5678", 
        "i got wrong item in order 9999"
    ]
    
    for test_message in non_tracking_cases:
        print(f"\nInput: '{test_message}'")
        
        complete_request = nlp.detect_complete_request(test_message)
        print(f"  Is Tracking: {complete_request.get('is_tracking', False)}")
        print(f"  Is Complete: {complete_request['is_complete']}")
        
        if not complete_request.get('is_tracking', False):
            print("  ✅ NON-TRACKING CORRECTLY IDENTIFIED")
        else:
            print("  ❌ NON-TRACKING INCORRECTLY IDENTIFIED AS TRACKING")

if __name__ == "__main__":
    test_tracking_queries()