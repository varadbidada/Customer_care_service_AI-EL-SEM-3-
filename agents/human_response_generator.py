from typing import Dict, Any, Optional
from .conversation_state import ConversationState, ConversationStateManager

class HumanResponseGenerator:
    def __init__(self):
        self.empathy_phrases = {
            ConversationState.WRONG_ITEM_REPORTED: [
                "That's really frustrating — I'm so sorry about the mix-up.",
                "Oh no, that's definitely not what you ordered. I'm really sorry about that.",
                "I can imagine how disappointing that must be. Let me help fix this right away.",
                "That's not acceptable at all — I'm sorry you received the wrong item."
            ],
            ConversationState.DELIVERY_DELAY: [
                "I understand how frustrating it is when your order doesn't arrive on time.",
                "I'm really sorry your order is running late — that's not the experience we want for you.",
                "I know waiting for a delayed order can be really annoying. Let me check what's happening.",
                "I'm sorry about the delay — I'd be frustrated too if I were waiting for my order."
            ],
            ConversationState.REFUND_IN_PROGRESS: [
                "I completely understand wanting a refund.",
                "Of course, I'd be happy to help you with a refund.",
                "I'm sorry things didn't work out with your order.",
                "No problem at all — let me get that refund started for you."
            ]
        }
        
        self.acknowledgment_phrases = {
            ConversationState.WRONG_ITEM_REPORTED: [
                "So you ordered {expected_item} but received {received_item} instead.",
                "Let me make sure I understand — you were expecting {expected_item} but got {received_item}.",
                "I see the issue — {received_item} instead of the {expected_item} you ordered."
            ],
            ConversationState.DELIVERY_DELAY: [
                "Your order was supposed to arrive by {expected_date} but hasn't shown up yet.",
                "So your order is running late from the expected delivery date of {expected_date}.",
                "I can see your order should have been delivered by {expected_date}."
            ]
        }
        
        self.solution_offers = {
            ConversationState.WRONG_ITEM_REPORTED: [
                "I can send you a replacement {correct_item} right away, or process a full refund — whichever you prefer.",
                "Would you like me to send the correct {correct_item} as a replacement, or would you prefer a refund?",
                "I can either get the right {correct_item} sent out to you today, or process a refund. What works better for you?"
            ],
            ConversationState.DELIVERY_DELAY: [
                "Let me track down exactly where your order is and get you an updated delivery estimate.",
                "I'll check with our shipping team to see what's causing the delay and when you can expect it.",
                "Let me look into this delay and see if we can expedite your order or offer other options."
            ],
            ConversationState.REFUND_IN_PROGRESS: [
                "I can process that refund for you right away.",
                "No problem — I'll get your refund started immediately.",
                "I'll take care of the refund for you. It should appear in your account within 3-5 business days."
            ]
        }
    
    def generate_empathetic_response(self, state_manager: ConversationStateManager, 
                                   user_message: str, extracted_info: Dict[str, Any]) -> str:
        """Generate a human-like, empathetic response based on conversation state"""
        
        current_state = state_manager.current_state
        situation_context = state_manager.situation_context
        
        # Handle contextual responses (short answers in context)
        if state_manager.is_contextual_response(user_message):
            return self._handle_contextual_response(state_manager, user_message, extracted_info)
        
        # Generate initial empathetic response for new situations
        if current_state in self.empathy_phrases:
            response_parts = []
            
            # 1. Emotional acknowledgment
            empathy = self._select_empathy_phrase(current_state)
            response_parts.append(empathy)
            
            # 2. Problem summary (if we have enough info)
            if self._can_summarize_problem(current_state, situation_context, extracted_info):
                summary = self._generate_problem_summary(current_state, situation_context, extracted_info)
                response_parts.append(summary)
            
            # 3. Solution offer or next question
            if state_manager.missing_info:
                next_question = state_manager.get_next_question()
                if next_question:
                    response_parts.append(next_question)
            else:
                solution = self._generate_solution_offer(current_state, situation_context)
                response_parts.append(solution)
            
            return " ".join(response_parts)
        
        # Fallback for general chat
        return self._generate_general_response(user_message, extracted_info)
    
    def _handle_contextual_response(self, state_manager: ConversationStateManager, 
                                  user_message: str, extracted_info: Dict[str, Any]) -> str:
        """Handle short contextual responses based on current state"""
        
        message_lower = user_message.strip().lower()
        current_state = state_manager.current_state
        
        # Handle order number responses
        if self._looks_like_order_number(user_message) and 'order_number' in state_manager.missing_info:
            order_num = user_message.strip()
            state_manager.add_information('order_number', order_num)
            
            responses = {
                ConversationState.WRONG_ITEM_REPORTED: f"Thanks! I found order #{order_num}. Would you like a replacement or a refund?",
                ConversationState.DELIVERY_DELAY: f"Perfect, I'm looking up order #{order_num} now. Let me check the shipping status for you.",
                ConversationState.ORDER_TRACKING: f"Great! Let me pull up the details for order #{order_num}.",
                ConversationState.REFUND_IN_PROGRESS: f"Got it — I'm processing the refund for order #{order_num} right now."
            }
            
            return responses.get(current_state, f"Thanks! I'm looking up order #{order_num} for you.")
        
        # Handle resolution preference responses
        if current_state == ConversationState.WRONG_ITEM_REPORTED and 'resolution_preference' in state_manager.missing_info:
            if any(word in message_lower for word in ['refund', 'money back', 'cancel']):
                state_manager.add_information('resolution_preference', 'refund')
                return "Perfect! I'm processing your refund now. You should see it in your account within 3-5 business days."
            elif any(word in message_lower for word in ['replacement', 'exchange', 'correct item', 'right one']):
                state_manager.add_information('resolution_preference', 'replacement')
                return "Excellent! I'm arranging for the correct item to be sent out to you today. You should receive it within 2-3 business days."
        
        # Handle yes/no responses
        if message_lower in ['yes', 'yeah', 'sure', 'ok', 'please']:
            if current_state == ConversationState.WRONG_ITEM_REPORTED:
                return "Great! I'll get that sorted out for you right away."
            elif current_state == ConversationState.REFUND_IN_PROGRESS:
                return "Perfect! Your refund is being processed now."
        
        # Default contextual response
        return "I understand. Let me help you with that."
    
    def _looks_like_order_number(self, message: str) -> bool:
        """Check if message looks like an order number"""
        cleaned = message.strip()
        return (len(cleaned) <= 10 and 
                (cleaned.isdigit() or cleaned.isalnum()) and 
                len(cleaned) >= 3)
    
    def _select_empathy_phrase(self, state: ConversationState) -> str:
        """Select appropriate empathy phrase for the situation"""
        phrases = self.empathy_phrases.get(state, ["I understand how you're feeling."])
        return phrases[0]  # For now, use first phrase. Could randomize later.
    
    def _can_summarize_problem(self, state: ConversationState, context: Dict[str, Any], 
                             extracted_info: Dict[str, Any]) -> bool:
        """Check if we have enough info to summarize the problem"""
        if state == ConversationState.WRONG_ITEM_REPORTED:
            return 'received_item' in extracted_info or 'expected_item' in extracted_info
        elif state == ConversationState.DELIVERY_DELAY:
            return 'expected_date' in extracted_info or 'order_date' in extracted_info
        return False
    
    def _generate_problem_summary(self, state: ConversationState, context: Dict[str, Any], 
                                extracted_info: Dict[str, Any]) -> str:
        """Generate a summary of the user's problem"""
        if state == ConversationState.WRONG_ITEM_REPORTED:
            expected = extracted_info.get('expected_item', 'your item')
            received = extracted_info.get('received_item', 'something else')
            return f"So you ordered {expected} but received {received} instead."
        elif state == ConversationState.DELIVERY_DELAY:
            expected_date = extracted_info.get('expected_date', 'the expected date')
            return f"Your order was supposed to arrive by {expected_date} but hasn't shown up yet."
        return ""
    
    def _generate_solution_offer(self, state: ConversationState, context: Dict[str, Any]) -> str:
        """Generate solution offer based on state"""
        offers = self.solution_offers.get(state, [])
        if offers:
            return offers[0]
        return "Let me see how I can help you with this."
    
    def _generate_general_response(self, user_message: str, extracted_info: Dict[str, Any]) -> str:
        """Generate response for general chat"""
        message_lower = user_message.lower()
        
        # Greeting responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return "Hi there! I'm here to help with any questions about your orders, deliveries, or products. What can I assist you with today?"
        
        # Thank you responses
        if any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
            return "You're very welcome! Is there anything else I can help you with?"
        
        # Default helpful response
        return "I'd be happy to help you with that. Could you tell me a bit more about what you need assistance with?"