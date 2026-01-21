from .base_agent import BaseAgent

class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__("support")
    
    def process(self, message: str, context: dict) -> str:
        message_lower = message.lower()
        
        # Get entities from current message and session
        current_entities = context.get("detected_entities", {})
        session_entities = context.get("persistent_entities", {})
        personalization = context.get("personalization", {})
        is_multi_intent = context.get("is_multi_intent", False)
        issue_context = context.get("issue_context", {})
        
        # Extract personalization details
        user_name = personalization.get("user_name")
        user_tone = personalization.get("user_tone", "neutral")
        empathy_level = personalization.get("empathy_level", "standard")
        communication_style = personalization.get("communication_style", "friendly")
        
        # Get relevant entities
        order_number = None
        email = None
        
        if "order_number" in current_entities and current_entities["order_number"]:
            order_number = current_entities["order_number"][0]
        elif "order_number" in session_entities:
            order_number = session_entities["order_number"]
        
        if "email" in current_entities and current_entities["email"]:
            email = current_entities["email"][0]
        elif "email" in session_entities:
            email = session_entities["email"]
        
        # Personalize response based on user state and communication style
        greeting = self._get_empathetic_greeting(user_name, user_tone, empathy_level, is_multi_intent)
        
        # Handle wrong item scenarios with enhanced empathy and specific solutions
        if "wrong_item" in issue_context:
            return self._handle_wrong_item_scenario(issue_context["wrong_item"], order_number, user_name, user_tone, empathy_level, greeting)
        
        # Handle different support queries with enhanced empathy
        elif any(word in message_lower for word in ["refund", "money back"]):
            if order_number:
                if user_tone == "frustrated":
                    return f"{greeting}I completely understand your frustration, and I want to make this right for you immediately. I can process a refund for order #{order_number}. Let me check the details... This order is eligible for a full refund of $89.99. I'll process this to your original payment method within 3-5 business days. What happened that made you want to return this?"
                else:
                    return f"{greeting}I'd be happy to help you with a refund for order #{order_number}. Let me check the order details... This order is eligible for a full refund of $89.99. The refund will be processed to your original payment method within 3-5 business days. What's the reason for the return?"
            else:
                if user_tone == "frustrated":
                    return f"{greeting}I'm really sorry you're not satisfied with your purchase. I want to help you get your money back as quickly as possible. To process a refund, I'll need your order number. Refunds are typically processed within 3-5 business days. What's your order number?"
                else:
                    return f"{greeting}I can help you with refunds! To process a refund, I'll need your order number. Refunds are typically processed within 3-5 business days to your original payment method. What's your order number?"
        
        elif any(word in message_lower for word in ["return", "exchange"]):
            if order_number:
                return f"{greeting}I'll help you return items from order #{order_number}. Our return policy allows returns within 30 days of delivery. All items appear to be in returnable condition. Which specific items would you like to return, and would you prefer a refund or exchange?"
            else:
                return f"{greeting}I'll assist you with returns and exchanges. Please provide your order number and let me know which items you'd like to return. Our return policy allows returns within 30 days of delivery."
        
        elif any(word in message_lower for word in ["account", "login", "password", "reset"]):
            if email:
                if user_tone == "frustrated":
                    return f"{greeting}I know how frustrating login issues can be. I can help with your account associated with {email} right away. I can send a password reset link to this email address immediately, or help you with other account issues. What specific problem are you experiencing?"
                else:
                    return f"{greeting}I can help with your account associated with {email}. I can send a password reset link to this email address right now, or help you with other account issues. What specific help do you need?"
            else:
                return f"{greeting}I can help with account issues! Are you having trouble logging in, need to reset your password, or update account information? Please provide your email address so I can assist you properly."
        
        elif any(word in message_lower for word in ["billing", "payment", "charge", "card"]):
            if order_number:
                if user_tone == "frustrated":
                    return f"{greeting}I understand billing concerns can be really stressful. Let me look into order #{order_number} right away... The charge was $89.99 processed 2 days ago. I want to make sure everything is correct. What specific billing concern do you have about this order?"
                else:
                    return f"{greeting}I can help with billing questions for order #{order_number}. Let me check the billing details... The charge was $89.99 processed 2 days ago. Is there a specific billing concern you have about this order?"
            else:
                return f"{greeting}I'm here to help with billing and payment questions. Are you seeing an unexpected charge, need to update payment methods, or have questions about a specific bill? Please provide your order number if this relates to a purchase."
        
        elif any(word in message_lower for word in ["technical", "problem", "issue", "not working", "error", "bug"]):
            if user_tone == "frustrated":
                return f"{greeting}I'm really sorry you're experiencing technical difficulties. That's so frustrating! I want to help you resolve this as quickly as possible. Please describe exactly what's not working - is it our website, mobile app, checkout process, or a specific feature? The more details you can share, the faster I can get this fixed for you."
            else:
                return f"{greeting}I can help troubleshoot technical issues! Please describe what's not working - is it our website, mobile app, checkout process, or a specific feature? The more details you provide about the error, the better I can assist you."
        
        else:
            # General support with context awareness and empathy
            context_info = []
            if order_number:
                context_info.append(f"order #{order_number}")
            if email:
                context_info.append(f"account {email}")
            
            if context_info:
                if user_tone == "frustrated":
                    return f"{greeting}I can see you need help with {' and '.join(context_info)}, and I'm here to make sure we resolve everything for you. I can assist with refunds, returns, account issues, billing questions, and technical problems. What's the most important thing I can help you with right now?"
                else:
                    return f"{greeting}I'm here to help with support for {' and '.join(context_info)}! I can assist with refunds, returns, account issues, billing questions, and technical problems. What specific help do you need?"
            else:
                if user_tone == "frustrated":
                    return f"{greeting}I can see you're having some trouble, and I really want to help you resolve this. I'm your support specialist and I can help with refunds, returns, account issues, billing questions, and technical problems. What's going on that I can help you with?"
                else:
                    return f"{greeting}I'm your support specialist! I can help with refunds, returns, account issues, billing questions, and technical problems. What can I assist you with today?"
    
    def _handle_wrong_item_scenario(self, wrong_item_info: Dict[str, Any], order_number: str, user_name: str, user_tone: str, empathy_level: str, greeting: str) -> str:
        """Enhanced handling of wrong item scenarios with context awareness"""
        
        ordered_item = wrong_item_info.get("ordered", "correct item")
        received_item = wrong_item_info.get("received", "wrong item")
        confidence = wrong_item_info.get("confidence", "medium")
        
        # Handle specific wrong item patterns
        if wrong_item_info.get("type") == "wrong_item_delivery":
            if order_number:
                # We have order number - provide comprehensive solution
                if user_tone in ["frustrated", "angry"]:
                    return self._generate_frustrated_wrong_item_response(
                        greeting, ordered_item, received_item, order_number, user_name
                    )
                else:
                    return self._generate_standard_wrong_item_response(
                        greeting, ordered_item, received_item, order_number, user_name
                    )
            else:
                # No order number - ask for it while acknowledging the issue
                return self._generate_wrong_item_no_order_response(
                    greeting, ordered_item, received_item, user_tone
                )
        
        elif wrong_item_info.get("type") == "wrong_item_general":
            # General wrong item case (like "I got wrong apples")
            if order_number:
                return f"{greeting}I'm sorry to hear you received the wrong item with order #{order_number}. I want to resolve this immediately. Could you tell me what you ordered versus what you received? I can then arrange for the correct item to be sent and handle the return."
            else:
                return f"{greeting}I'm sorry you received the wrong item! That's really frustrating. To help fix this quickly, could you please share: 1) Your order number, 2) What you ordered, and 3) What you received instead? I'll make sure you get the right item as soon as possible."
        
        # Fallback for other wrong item cases
        return f"{greeting}I understand there's an issue with your order. I'm here to help resolve this quickly. Could you provide more details about what happened?"
    
    def _generate_frustrated_wrong_item_response(self, greeting: str, ordered: str, received: str, order_number: str, user_name: str) -> str:
        """Generate empathetic response for frustrated users with wrong items"""
        name_part = f" {user_name}" if user_name else ""
        
        return f"{greeting}I'm so sorry this happened{name_part}! I can see you ordered {ordered} but received {received} instead. This is completely unacceptable, and I want to make this right immediately. For order #{order_number}, I can offer you: 1) A full refund ($89.99) processed today, 2) Send you the correct {ordered} with expedited shipping at no charge, or 3) Both - keep the {received} as an apology and get your {ordered} too. What would work best for you?"
    
    def _generate_standard_wrong_item_response(self, greeting: str, ordered: str, received: str, order_number: str, user_name: str) -> str:
        """Generate standard response for wrong item cases"""
        name_part = f" {user_name}" if user_name else ""
        
        return f"{greeting}I see you ordered {ordered} but received {received} instead{name_part}. I sincerely apologize for this mix-up with order #{order_number}. Let me make this right for you. I can: 1) Process a full refund ($89.99), 2) Send the correct {ordered} with free expedited shipping, or 3) If you'd like to keep the {received}, I can send your {ordered} and give you a discount. Which option would you prefer?"
    
    def _generate_wrong_item_no_order_response(self, greeting: str, ordered: str, received: str, user_tone: str) -> str:
        """Generate response when we know about wrong item but need order number"""
        if user_tone in ["frustrated", "angry"]:
            return f"{greeting}I'm really sorry you received {received} instead of the {ordered} you ordered! This kind of mix-up is incredibly frustrating, and I want to resolve it immediately. Could you please provide your order number? I'll then arrange for the correct item to be sent with expedited shipping and handle the return of the wrong item right away."
        else:
            return f"{greeting}I'm sorry you received {received} instead of the {ordered} you ordered! To help resolve this quickly, could you please provide your order number? I'll then arrange for the correct item to be sent with expedited shipping and handle the return of the wrong item."
    
    def _get_empathetic_greeting(self, user_name: str, user_tone: str, empathy_level: str, is_multi_intent: bool) -> str:
        """Generate an empathetic greeting based on user emotional state"""
        if is_multi_intent:
            # For multi-intent, keep greeting minimal but empathetic
            if user_tone == "frustrated":
                if user_name:
                    return f"{user_name}, I'm sorry you're having trouble. For the support issue: "
                else:
                    return "I'm sorry you're having trouble. For the support issue: "
            elif user_name:
                return f"{user_name}, regarding support: "
            else:
                return "For support: "
        
        # Single intent greetings with high empathy
        if user_tone == "frustrated" and empathy_level == "high":
            if user_name:
                return f"{user_name}, I'm really sorry you're going through this frustration. "
            else:
                return "I'm really sorry you're going through this frustration. "
        
        elif user_tone == "urgent":
            if user_name:
                return f"{user_name}, I understand this is urgent and I'm here to help immediately. "
            else:
                return "I understand this is urgent and I'm here to help immediately. "
        
        elif user_tone == "confused":
            if user_name:
                return f"{user_name}, I can see this is confusing, and I'm here to help clarify everything. "
            else:
                return "I can see this is confusing, and I'm here to help clarify everything. "
        
        elif user_name:
            return f"{user_name}, "
        
        else:
            return ""