from enum import Enum
from typing import Dict, Any, Optional
import time

class ConversationState(Enum):
    GREETING = "greeting"
    WRONG_ITEM_REPORTED = "wrong_item_reported"
    DELIVERY_DELAY = "delivery_delay"
    REFUND_IN_PROGRESS = "refund_in_progress"
    ORDER_TRACKING = "order_tracking"
    GENERAL_CHAT = "general_chat"
    PRODUCT_INQUIRY = "product_inquiry"
    ACCOUNT_ISSUE = "account_issue"

class ConversationStateManager:
    def __init__(self):
        self.current_state = ConversationState.GREETING
        self.situation_context = {}
        self.missing_info = []
        self.last_state_change = time.time()
        self.conversation_history = []
        
    def detect_situation(self, message: str, llm_analysis: Dict[str, Any]) -> ConversationState:
        """Detect the user's situation from natural language"""
        message_lower = message.lower()
        
        # Wrong item situations
        if any(phrase in message_lower for phrase in [
            "wrong item", "got the wrong", "received wrong", "not what i ordered",
            "ordered apples but got", "different product", "incorrect item",
            "this isn't what", "sent me the wrong"
        ]):
            return ConversationState.WRONG_ITEM_REPORTED
            
        # Delivery delay situations  
        if any(phrase in message_lower for phrase in [
            "delivery delay", "not arrived", "where is my order", "still waiting",
            "hasn't arrived", "late delivery", "expected yesterday", "taking too long"
        ]):
            return ConversationState.DELIVERY_DELAY
            
        # Order tracking situations
        if any(phrase in message_lower for phrase in [
            "track my order", "order status", "where is order", "check my order",
            "order number", "shipping status", "delivery status"
        ]):
            return ConversationState.ORDER_TRACKING
            
        # Refund situations
        if any(phrase in message_lower for phrase in [
            "want a refund", "refund please", "money back", "cancel order",
            "return this", "get my money"
        ]):
            return ConversationState.REFUND_IN_PROGRESS
            
        # Product inquiry
        if any(phrase in message_lower for phrase in [
            "tell me about", "product info", "what is", "how much",
            "available", "in stock", "price"
        ]):
            return ConversationState.PRODUCT_INQUIRY
            
        # Use LLM analysis as fallback
        if llm_analysis.get('detected_situation'):
            situation_map = {
                'wrong_item': ConversationState.WRONG_ITEM_REPORTED,
                'delivery_issue': ConversationState.DELIVERY_DELAY,
                'refund_request': ConversationState.REFUND_IN_PROGRESS,
                'order_inquiry': ConversationState.ORDER_TRACKING,
                'product_question': ConversationState.PRODUCT_INQUIRY
            }
            return situation_map.get(llm_analysis['detected_situation'], ConversationState.GENERAL_CHAT)
            
        return ConversationState.GENERAL_CHAT
    
    def should_change_state(self, new_state: ConversationState, message: str) -> bool:
        """Determine if we should change conversation state"""
        
        # Always allow initial state setting
        if self.current_state == ConversationState.GREETING:
            return True
            
        # Don't change state for short contextual responses
        if len(message.strip()) < 10 and not any(word in message.lower() for word in [
            "new", "different", "another", "switch", "change"
        ]):
            return False
            
        # Allow state change if user explicitly switches topics
        topic_switch_phrases = [
            "actually", "wait", "instead", "new issue", "different problem",
            "something else", "another question", "also need help"
        ]
        
        if any(phrase in message.lower() for phrase in topic_switch_phrases):
            return True
            
        # Allow state change if current issue seems resolved
        resolution_phrases = [
            "thanks", "that's all", "problem solved", "all good", "perfect"
        ]
        
        if any(phrase in message.lower() for phrase in resolution_phrases):
            return True
            
        # Don't change state if we're in the middle of resolving an issue
        if self.current_state in [
            ConversationState.WRONG_ITEM_REPORTED,
            ConversationState.DELIVERY_DELAY,
            ConversationState.REFUND_IN_PROGRESS
        ] and self.missing_info:
            return False
            
        return new_state != self.current_state
    
    def update_state(self, new_state: ConversationState, context: Dict[str, Any] = None):
        """Update conversation state and context"""
        if self.should_change_state(new_state, context.get('message', '')):
            self.current_state = new_state
            self.last_state_change = time.time()
            
            # Update situation context based on new state
            if context:
                self.situation_context.update(context)
                
            # Set missing info requirements for each state
            self._set_missing_info_requirements()
    
    def _set_missing_info_requirements(self):
        """Set what information is needed for current situation"""
        info_requirements = {
            ConversationState.WRONG_ITEM_REPORTED: ['order_number', 'resolution_preference'],
            ConversationState.DELIVERY_DELAY: ['order_number', 'expected_date'],
            ConversationState.REFUND_IN_PROGRESS: ['order_number', 'refund_reason'],
            ConversationState.ORDER_TRACKING: ['order_number'],
            ConversationState.PRODUCT_INQUIRY: ['product_name'],
        }
        
        required_info = info_requirements.get(self.current_state, [])
        self.missing_info = [info for info in required_info 
                           if info not in self.situation_context]
    
    def get_next_question(self) -> Optional[str]:
        """Get the next question to ask based on missing information"""
        if not self.missing_info:
            return None
            
        next_info = self.missing_info[0]
        
        question_templates = {
            'order_number': "Could you share your order number so I can look this up?",
            'resolution_preference': "Would you like a replacement or a refund?",
            'expected_date': "When were you expecting this to arrive?",
            'refund_reason': "Could you tell me what happened with your order?",
            'product_name': "Which product are you interested in?"
        }
        
        return question_templates.get(next_info)
    
    def add_information(self, info_type: str, value: Any):
        """Add information to situation context"""
        self.situation_context[info_type] = value
        if info_type in self.missing_info:
            self.missing_info.remove(info_type)
    
    def is_contextual_response(self, message: str) -> bool:
        """Check if message is a contextual response to current situation"""
        message_lower = message.strip().lower()
        
        # Short responses that depend on context
        short_responses = ['yes', 'no', 'ok', 'sure', 'please']
        if message_lower in short_responses:
            return True
            
        # Order numbers
        if len(message.strip()) <= 10 and (message.strip().isdigit() or 
                                         message.strip().isalnum()):
            return True
            
        # Resolution preferences
        resolution_words = ['refund', 'replacement', 'exchange', 'cancel']
        if any(word in message_lower for word in resolution_words) and len(message) < 20:
            return True
            
        return False
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get current state summary for debugging"""
        return {
            'current_state': self.current_state.value,
            'situation_context': self.situation_context,
            'missing_info': self.missing_info,
            'time_in_state': time.time() - self.last_state_change
        }