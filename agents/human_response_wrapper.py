from typing import Dict, Any
import random

class HumanResponseWrapper:
    def __init__(self):
        self.acknowledgments = [
            "I understand",
            "I see",
            "Got it",
            "I can help with that",
            "Let me check that for you"
        ]
        
        self.empathy_phrases = {
            "frustrated": [
                "I completely understand your frustration",
                "I know this can be really frustrating",
                "I'm sorry you're experiencing this issue"
            ],
            "urgent": [
                "I understand this is urgent for you",
                "Let me help you right away",
                "I'll get this sorted out quickly"
            ],
            "confused": [
                "No worries, I'm here to help clarify",
                "Let me explain this clearly",
                "I'm happy to walk you through this"
            ],
            "concerned": [
                "I understand your concern",
                "Let me look into this for you",
                "I can see why you'd be worried about this"
            ]
        }
        
        self.transitions = [
            "Here's what I found:",
            "Let me update you:",
            "Here's the current status:",
            "I can confirm that:",
            "The good news is:"
        ]
        
        self.closings = [
            "Is there anything else I can help you with?",
            "Let me know if you need any other assistance.",
            "Feel free to reach out if you have more questions.",
            "I'm here if you need anything else."
        ]
    
    def wrap(self, canonical_response: str, context: Dict[str, Any]) -> str:
        try:
            # Ensure canonical_response is a string
            if not isinstance(canonical_response, str):
                canonical_response = str(canonical_response) if canonical_response else "I'm here to help."
            
            personalization = context.get("personalization", {})
            user_name = personalization.get("user_name", "")
            user_tone = personalization.get("user_tone", "neutral")
            empathy_level = personalization.get("empathy_level", "standard")
            
            # Build humanized response
            parts = []
            
            # Add greeting with name if available
            if user_name:
                parts.append(f"Hi {user_name},")
            
            # Add empathy based on user tone
            if user_tone in self.empathy_phrases and empathy_level in ["high", "supportive"]:
                empathy = random.choice(self.empathy_phrases[user_tone])
                parts.append(f"{empathy}.")
            
            # Add transition phrase
            if len(parts) > 0:
                transition = random.choice(self.transitions)
                parts.append(transition)
            
            # Add the canonical response (unchanged)
            parts.append(canonical_response)
            
            # Add closing for longer conversations
            conversation_length = context.get("conversation_length", 0)
            if conversation_length > 2 and random.random() < 0.3:
                closing = random.choice(self.closings)
                parts.append(closing)
            
            # Join parts with appropriate spacing
            final_response = " ".join(parts)
            
            # Clean up spacing and formatting
            final_response = self._clean_formatting(final_response)
            
            # Ensure we return a string
            return str(final_response) if final_response else canonical_response
            
        except Exception as e:
            print(f"❌ HumanResponseWrapper error: {e}")
            # Fallback to canonical response
            return str(canonical_response) if canonical_response else "I'm here to help you."
    
    def _clean_formatting(self, text: str) -> str:
        # Fix double spaces
        text = " ".join(text.split())
        
        # Ensure proper spacing after periods
        text = text.replace(". ", ". ").replace("...", ".")
        
        # Fix spacing around colons
        text = text.replace(" :", ":").replace(": ", ": ")
        
        return text.strip()