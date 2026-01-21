#!/usr/bin/env python3
"""
Quick test to verify subscription query intent detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.dialogue_state_manager import DialogueStateManager, Intent

def test_subscription_intent():
    """Test that subscription query is detected as FAQ"""
    print("🧪 TESTING SUBSCRIPTION INTENT DETECTION")
    print("=" * 50)
    
    dialogue_manager = DialogueStateManager()
    
    # The exact query from the user
    test_message = "I have an issue related to subscription in Food Delivery"
    
    print(f"Testing message: '{test_message}'")
    
    detected_intent = dialogue_manager._detect_intent(test_message)
    
    print(f"Detected intent: {detected_intent}")
    
    if detected_intent == Intent.FAQ:
        print("✅ SUCCESS: Correctly detected as FAQ")
        return True
    else:
        print(f"❌ FAILED: Expected FAQ, got {detected_intent}")
        
        # Debug: check which keywords are matching
        message_lower = test_message.lower()
        print("\nDEBUG - Keyword matching:")
        
        # Check FAQ keywords
        faq_keywords = dialogue_manager.intent_keywords[Intent.FAQ]
        faq_matches = [kw for kw in faq_keywords if kw in message_lower]
        print(f"FAQ matches: {faq_matches}")
        
        # Check ORDER_STATUS keywords  
        status_keywords = dialogue_manager.intent_keywords[Intent.ORDER_STATUS]
        status_matches = [kw for kw in status_keywords if kw in message_lower]
        print(f"ORDER_STATUS matches: {status_matches}")
        
        return False

if __name__ == "__main__":
    success = test_subscription_intent()
    if success:
        print("\n🎉 SUBSCRIPTION INTENT FIX WORKING!")
    else:
        print("\n❌ SUBSCRIPTION INTENT STILL BROKEN")
    
    sys.exit(0 if success else 1)