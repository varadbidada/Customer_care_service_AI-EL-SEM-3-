#!/usr/bin/env python3
"""
Test script to demonstrate multi-turn dialogue state management
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.dialogue_state_manager import DialogueStateManager, DialogueState
from app import get_order_by_id, get_faq_answer

class MockSession:
    """Mock session for testing"""
    def __init__(self):
        self.dialogue_state = None

def test_multi_turn_conversations():
    """Test multi-turn conversation scenarios"""
    
    print("=" * 80)
    print("🧪 TESTING MULTI-TURN DIALOGUE STATE MANAGEMENT")
    print("=" * 80)
    
    dialogue_manager = DialogueStateManager()
    
    # Test scenarios
    scenarios = [
        {
            "name": "Billing Issue - Multi-turn",
            "messages": [
                "I was charged twice for my order",
                "ORD54582",
                "Thank you, that helps!"
            ]
        },
        {
            "name": "Order Status - Multi-turn", 
            "messages": [
                "I want to track my order",
                "ORD63640",
                "Great, thanks!"
            ]
        },
        {
            "name": "Return Order - Multi-turn",
            "messages": [
                "I need to return an item",
                "ORD90495",
                "Perfect, that's all I needed"
            ]
        },
        {
            "name": "Single-turn FAQ",
            "messages": [
                "How do I apply a coupon code?"
            ]
        },
        {
            "name": "Intent Persistence Test",
            "messages": [
                "I have a billing problem",
                "What do you need from me?",
                "ORD54582"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎭 SCENARIO: {scenario['name']}")
        print("-" * 60)
        
        # Create fresh session for each scenario
        session = MockSession()
        
        for i, message in enumerate(scenario['messages']):
            print(f"\n👤 User: {message}")
            
            # Process message through dialogue manager
            result = dialogue_manager.process_message(
                message, session, get_order_by_id, get_faq_answer
            )
            
            response = result.get('response', 'No response')
            state = result.get('conversation_state', 'unknown')
            
            print(f"🤖 Bot: {response}")
            print(f"📊 State: {state}")
            
            # Show dialogue state info
            if hasattr(session, 'dialogue_state') and session.dialogue_state:
                ds = session.dialogue_state
                print(f"🎯 Intent: {ds.active_intent}")
                print(f"🔄 Pending Slot: {ds.pending_slot}")
                print(f"📋 Context: {ds.context}")
        
        print(f"\n✅ Scenario '{scenario['name']}' completed")
    
    print("\n" + "=" * 80)
    print("✅ ALL DIALOGUE STATE TESTS COMPLETED")
    print("=" * 80)

def test_intent_detection():
    """Test intent detection logic"""
    
    print("\n🔍 TESTING INTENT DETECTION")
    print("-" * 40)
    
    dialogue_manager = DialogueStateManager()
    
    test_messages = [
        ("I was charged twice", "billing_issue"),
        ("Need to return my order", "return_order"), 
        ("Where is my package", "order_status"),
        ("Track my delivery", "order_status"),
        ("Refund my payment", "billing_issue"),
        ("Exchange this item", "return_order"),
        ("How do I contact support", "faq"),
        ("Random message", "faq")
    ]
    
    for message, expected in test_messages:
        detected = dialogue_manager._detect_intent(message)
        status = "✅" if str(detected).split('.')[-1].lower() == expected else "❌"
        print(f"{status} '{message}' → {detected} (expected: {expected})")

def test_slot_extraction():
    """Test order ID extraction"""
    
    print("\n📋 TESTING ORDER ID EXTRACTION")
    print("-" * 40)
    
    dialogue_manager = DialogueStateManager()
    
    test_messages = [
        ("My order number is ORD54582", "ORD54582"),
        ("Order #63640", "63640"),
        ("It's order ORD90495", "ORD90495"),
        ("#12345", "12345"),
        ("The order is 54582", "54582"),
        ("No order number here", None)
    ]
    
    for message, expected in test_messages:
        extracted = dialogue_manager._extract_order_id(message)
        status = "✅" if extracted == expected else "❌"
        print(f"{status} '{message}' → {extracted} (expected: {expected})")

if __name__ == "__main__":
    test_intent_detection()
    test_slot_extraction()
    test_multi_turn_conversations()