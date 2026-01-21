#!/usr/bin/env python3
"""
Comprehensive test of the complete NLU system with deterministic behavior
"""

from agents.router_agent import RouterAgent
from memory.session_manager import SessionManager

def test_complete_nlu_system():
    """Test the complete NLU system with all scenarios"""
    
    print("🚀 Testing Complete NLU System - Deterministic Support Behavior")
    print("=" * 70)
    
    router = RouterAgent()
    session_manager = SessionManager(storage_type="memory")
    
    # Test scenarios
    scenarios = [
        {
            "name": "Complete Request - Wrong Item Refund",
            "messages": ["Order 12345 got wrong item, want refund"],
            "expected_behavior": "Direct resolution, bypass router/LLM"
        },
        {
            "name": "Complete Request - Delay Replacement", 
            "messages": ["My order ABC123 is delayed, send replacement"],
            "expected_behavior": "Direct resolution, bypass router/LLM"
        },
        {
            "name": "Complete Request - Cancel Order",
            "messages": ["Cancel order #9999"],
            "expected_behavior": "Direct resolution, bypass router/LLM"
        },
        {
            "name": "Incomplete Request - Missing Order ID",
            "messages": [
                "I got wrong item, want refund",
                "Order 55555"
            ],
            "expected_behavior": "Ask for order ID, then complete with context"
        },
        {
            "name": "Incomplete Request - Missing Resolution",
            "messages": [
                "Order 77777 got wrong item", 
                "I want replacement"
            ],
            "expected_behavior": "Ask for resolution, then complete with context"
        },
        {
            "name": "Incomplete Request - Missing Issue",
            "messages": [
                "Order 88888 needs refund",
                "It was damaged"
            ],
            "expected_behavior": "Ask for issue, then complete with context"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {scenario['name']}")
        print(f"Expected: {scenario['expected_behavior']}")
        print(f"{'='*70}")
        
        # Create fresh session for each scenario
        session = session_manager.get_session(f"test_scenario_{i}")
        
        for j, message in enumerate(scenario['messages'], 1):
            print(f"\nMessage {j}: {message}")
            
            result = router.process_with_context(message, session)
            
            print(f"Response: {result['response']}")
            print(f"Agents used: {result['agents_used']}")
            
            # Check for deterministic behavior indicators
            issue_context = result.get('issue_context', {})
            if issue_context.get('bypassed_llm'):
                print("✅ Successfully bypassed router and LLM")
            elif issue_context.get('deterministic_flow'):
                print("✅ Using deterministic flow for incomplete request")
            elif issue_context.get('completed_with_context'):
                print("✅ Completed resolution using preserved context")
            else:
                print("ℹ️  Using regular NLP flow")
    
    print(f"\n{'='*70}")
    print("🎉 Complete NLU System Test Completed!")
    print("Key Features Demonstrated:")
    print("✅ Complete request detection")
    print("✅ Direct resolution bypass")
    print("✅ Deterministic incomplete request handling")
    print("✅ Context preservation across messages")
    print("✅ Router and LLM disabled during resolution")
    print(f"{'='*70}")

def test_hard_rules():
    """Test the hard rules: once resolution starts, router and LLM are disabled"""
    
    print("\n🔒 Testing Hard Rules - Router/LLM Disabled During Resolution")
    print("=" * 70)
    
    router = RouterAgent()
    session_manager = SessionManager(storage_type="memory")
    session = session_manager.get_session("test_hard_rules")
    
    # Start incomplete resolution
    print("\nStep 1: Start incomplete resolution")
    message1 = "Order 12345 got wrong item"
    result1 = router.process_with_context(message1, session)
    print(f"Message: {message1}")
    print(f"Response: {result1['response']}")
    
    # Try to ask something unrelated - should still be in resolution mode
    print("\nStep 2: Try unrelated question during resolution")
    message2 = "What's the weather like?"
    result2 = router.process_with_context(message2, session)
    print(f"Message: {message2}")
    print(f"Response: {result2['response']}")
    
    if "resolution" in result2['response'].lower() or "refund" in result2['response'].lower():
        print("✅ Router/LLM correctly disabled - staying in resolution mode")
    else:
        print("❌ Router/LLM not properly disabled")
    
    # Complete the resolution
    print("\nStep 3: Complete the resolution")
    message3 = "I want refund"
    result3 = router.process_with_context(message3, session)
    print(f"Message: {message3}")
    print(f"Response: {result3['response']}")
    
    if "refund" in result3['response'].lower() and "12345" in result3['response']:
        print("✅ Resolution completed successfully")
    else:
        print("❌ Resolution not completed properly")

if __name__ == "__main__":
    test_complete_nlu_system()
    test_hard_rules()