from .base_agent import BaseAgent
from .llm_service import LLMService

class GeneralAgent(BaseAgent):
    def __init__(self):
        super().__init__("general")
        self.llm_service = LLMService()
    
    def process(self, message: str, context: dict) -> str:
        message_lower = message.lower()
        confidence_scores = context.get("confidence_scores", {})
        entities = context.get("persistent_entities", {})
        personalization = context.get("personalization", {})
        conversation_history = context.get("conversation_history", [])
        detected_intent = context.get("detected_intent", "general")
        
        # Extract personalization details
        user_name = personalization.get("user_name")
        user_tone = personalization.get("user_tone", "neutral")
        empathy_level = personalization.get("empathy_level", "standard")
        communication_style = personalization.get("communication_style", "friendly")
        
        # Check if this is truly a low-confidence scenario or should be routed to LLM
        max_confidence = max(confidence_scores.values()) if confidence_scores else 0.0
        is_low_confidence = max_confidence < 0.4
        
        # Handle greetings with personality
        if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            if user_name:
                return f"Hello {user_name}! Great to see you again. I'm Kiro, your AI assistant. How can I help you today?"
            else:
                return "Hello! I'm Kiro, your AI assistant. I can help you with orders, products, support issues, and general questions. What would you like to know about today?"
        
        # Handle thanks with warmth
        elif any(word in message_lower for word in ["thank", "thanks", "appreciate"]):
            responses = [
                f"You're very welcome{', ' + user_name if user_name else ''}! Is there anything else I can help you with?",
                f"My pleasure{', ' + user_name if user_name else ''}! I'm here whenever you need assistance.",
                f"Happy to help{', ' + user_name if user_name else ''}! What else can I do for you today?"
            ]
            # Choose response based on communication style
            if communication_style == "formal":
                return responses[0]
            elif communication_style == "casual":
                return responses[1]
            else:
                return responses[2]
        
        # Handle goodbye with personality
        elif any(word in message_lower for word in ["bye", "goodbye", "see you", "later"]):
            if user_name:
                return f"Goodbye, {user_name}! It was great helping you today. Feel free to come back anytime if you need assistance with orders, products, or support. Have a wonderful day!"
            else:
                return "Goodbye! Feel free to come back anytime if you need help with orders, products, or support. Have a great day!"
        
        # Handle name introduction with enthusiasm
        elif any(phrase in message_lower for phrase in ["my name is", "i'm", "i am", "call me"]):
            if user_name:
                return f"Nice to meet you, {user_name}! I'll remember that for our conversation. How can I help you today? I can assist with orders, products, support questions, or just about anything else you'd like to know!"
            else:
                return "Nice to meet you! I'll remember your name for our conversation. How can I help you today? I can assist with orders, products, support questions, or general information!"
        
        # Check if this should be handled by LLM (technical, general knowledge, or complex queries)
        should_use_llm = self._should_use_llm(message, confidence_scores, context)
        
        if should_use_llm:
            # Use LLM for general knowledge, technical issues, and complex queries
            return self._handle_with_llm(message, context)
        
        # Handle low confidence cases with smart suggestions based on session context
        elif is_low_confidence:
            return self._handle_low_confidence_with_context(message, entities, user_name, empathy_level, conversation_history, detected_intent)
        
        # Handle unclear or vague queries with context awareness
        elif len(message_lower.split()) <= 2:
            return self._handle_vague_query_with_context(message, user_name, entities, conversation_history)
        
        # Default to LLM for other queries
        else:
            return self._handle_with_llm(message, context)
    
    def _should_use_llm(self, message: str, confidence_scores: dict, context: dict) -> bool:
        """Determine if query should be handled by LLM"""
        message_lower = message.lower()
        
        # Technical issues - always use LLM
        technical_keywords = [
            "internet", "wifi", "connection", "not working", "broken", "error", "bug",
            "password", "login", "reset", "technical", "problem", "issue", "troubleshoot",
            "fix", "repair", "setup", "install", "configure", "network", "computer",
            "phone", "device", "app", "website", "browser", "email", "software"
        ]
        
        if any(keyword in message_lower for keyword in technical_keywords):
            return True
        
        # General knowledge questions - use LLM
        knowledge_keywords = [
            "how to", "how do i", "how can i", "what is", "what are", "tell me about",
            "explain", "why", "when", "where", "who", "which", "joke", "story",
            "weather", "time", "date", "calculate", "convert", "translate"
        ]
        
        if any(keyword in message_lower for keyword in knowledge_keywords):
            return True
        
        # Low confidence scores - use LLM for better handling
        if confidence_scores and max(confidence_scores.values()) < 0.4:
            return True
        
        # Complex or long queries - use LLM
        if len(message.split()) > 10:
            return True
        
        return False
    
    def _handle_with_llm(self, message: str, context: dict) -> str:
        """Handle query using LLM with full context"""
        try:
            # Enhance context for LLM
            enhanced_context = self._prepare_llm_context(context)
            
            # Generate response using LLM
            llm_response = self.llm_service.generate_response(message, enhanced_context)
            
            # Post-process LLM response
            return self._post_process_llm_response(llm_response, context)
            
        except Exception as e:
            print(f"Error in LLM processing: {e}")
            # Fallback to empathetic response
            user_name = context.get("personalization", {}).get("user_name")
            name_prefix = f"{user_name}, " if user_name else ""
            return f"{name_prefix}I'd love to help you with that! While I'm having a small technical issue right now, I can still assist with orders, products, and support questions. Could you let me know if this relates to any of those areas, or would you like to try asking your question again?"
    
    def _prepare_llm_context(self, context: dict) -> dict:
        """Prepare enhanced context for LLM"""
        enhanced_context = context.copy()
        
        # Add agent capabilities information
        enhanced_context["agent_capabilities"] = {
            "order_agent": "Track orders, check delivery status, handle cancellations, provide shipping information",
            "product_agent": "Product information, pricing, availability, specifications, recommendations",
            "support_agent": "Refunds, returns, account issues, billing questions, technical support",
            "general_agent": "General questions, technical help, explanations, and conversation"
        }
        
        # Add conversation summary
        conversation_history = context.get("conversation_history", [])
        if conversation_history:
            recent_topics = []
            for msg in conversation_history[-3:]:
                if msg.get("intents"):
                    recent_topics.extend(msg["intents"])
            
            enhanced_context["recent_topics"] = list(set(recent_topics))
        
        # Add user context summary
        personalization = context.get("personalization", {})
        enhanced_context["user_summary"] = {
            "name": personalization.get("user_name"),
            "tone": personalization.get("user_tone", "neutral"),
            "style": personalization.get("communication_style", "friendly"),
            "empathy_needed": personalization.get("empathy_level", "standard")
        }
        
        return enhanced_context
    
    def _post_process_llm_response(self, llm_response: str, context: dict) -> str:
        """Post-process LLM response for consistency"""
        personalization = context.get("personalization", {})
        user_name = personalization.get("user_name")
        
        # Ensure response is personalized if we have a name
        if user_name and not llm_response.startswith(user_name) and not user_name.lower() in llm_response.lower():
            # Add name naturally if it doesn't already include it
            if llm_response.startswith(("I ", "Let ", "You ", "Try ", "Here ")):
                llm_response = f"{user_name}, {llm_response.lower()}"
        
        # Add helpful suggestion for specialized services if not already mentioned
        if not any(word in llm_response.lower() for word in ["order", "product", "support", "refund", "track"]):
            if len(llm_response) < 200:  # Only for shorter responses
                llm_response += f"\n\nIf you need help with orders, products, or support issues, just let me know{', ' + user_name if user_name else ''}!"
        
        return llm_response
    
    def _handle_low_confidence(self, message: str, entities: dict, user_name: str, empathy_level: str) -> str:
        """Handle low confidence queries with smart suggestions"""
        name_greeting = f"{user_name}, " if user_name else ""
        
        # Analyze what entities we found to give better suggestions
        suggestions = []
        if entities.get("order_number"):
            suggestions.append("• Track or manage your order")
        if entities.get("product_name"):
            suggestions.append("• Get product information")
        if entities.get("email"):
            suggestions.append("• Account or support assistance")
        
        if suggestions:
            suggestion_text = "\n".join(suggestions)
            if empathy_level == "high":
                return f"{name_greeting}I can see you're trying to get help, and I want to make sure I understand exactly what you need. Based on what I found in your message, I can help you with:\n{suggestion_text}\n\nCould you please clarify what you'd like to do?"
            else:
                return f"{name_greeting}I detected some information in your message but I'm not quite sure what you need help with. Based on what I found, I can help you with:\n{suggestion_text}\n\nCould you please clarify what you'd like to do?"
        else:
            if empathy_level == "high":
                return f"{name_greeting}I really want to help you with the right thing! I can assist with:\n• Order tracking and delivery\n• Product information and pricing\n• Returns, refunds, and account issues\n• General questions and technical help\n\nWhat would you like help with?"
            else:
                return f"{name_greeting}I want to make sure I help you with the right thing! I can assist with:\n• Order tracking and delivery\n• Product information and pricing\n• Returns, refunds, and account issues\n• General questions and technical help\n\nWhat would you like help with?"
    
    def _handle_low_confidence_with_context(self, message: str, entities: dict, user_name: str, empathy_level: str, conversation_history: list, detected_intent: str) -> str:
        """Handle low confidence queries with enhanced context awareness"""
        name_greeting = f"{user_name}, " if user_name else ""
        
        # Check conversation history for context clues
        recent_intents = []
        for msg in conversation_history[-3:]:
            if msg.get("intents"):
                recent_intents.extend(msg["intents"])
        
        # Analyze what entities we found to give better suggestions
        suggestions = []
        if entities.get("order_number"):
            suggestions.append("• Track or manage your order")
        if entities.get("product_name"):
            suggestions.append("• Get product information")
        if entities.get("email"):
            suggestions.append("• Account or support assistance")
        
        # Add context-based suggestions
        if "order" in recent_intents:
            suggestions.append("• Continue with your order inquiry")
        if "product" in recent_intents:
            suggestions.append("• Get more product details")
        if "support" in recent_intents:
            suggestions.append("• Continue with support assistance")
        
        # Provide context-aware response
        if suggestions:
            suggestion_text = "\n".join(list(set(suggestions)))  # Remove duplicates
            if empathy_level == "high":
                return f"{name_greeting}I can see you're trying to get help, and I want to make sure I understand exactly what you need. Based on our conversation and what I found in your message, I can help you with:\n{suggestion_text}\n\nCould you please clarify what you'd like to do?"
            else:
                return f"{name_greeting}I'm not quite sure what you need help with, but based on our conversation, I can help you with:\n{suggestion_text}\n\nCould you please clarify what you'd like to do?"
        else:
            # Provide general guidance with context
            if recent_intents:
                context_hint = f"We were just discussing {', '.join(set(recent_intents))}. "
            else:
                context_hint = ""
            
            if empathy_level == "high":
                return f"{name_greeting}{context_hint}I really want to help you with the right thing! I can assist with:\n• Order tracking and delivery\n• Product information and pricing\n• Returns, refunds, and account issues\n• General questions and technical help\n\nWhat would you like help with?"
            else:
                return f"{name_greeting}{context_hint}I can assist with:\n• Order tracking and delivery\n• Product information and pricing\n• Returns, refunds, and account issues\n• General questions and technical help\n\nWhat would you like help with?"
    
    def _handle_vague_query_with_context(self, message: str, user_name: str, entities: dict, conversation_history: list) -> str:
        """Handle vague queries with conversation context"""
        name_greeting = f"{user_name}, " if user_name else ""
        
        # Check if this might be a follow-up to previous conversation
        recent_intents = []
        for msg in conversation_history[-3:]:
            if msg.get("intents"):
                recent_intents.extend(msg["intents"])
        
        # Check for context clues in entities
        if entities.get("order_number"):
            return f"{name_greeting}I can see you mentioned an order. Would you like to track it, check delivery status, or make changes to order #{entities['order_number']}?"
        elif entities.get("product_name"):
            return f"{name_greeting}I can see you're asking about {entities['product_name']}. Would you like pricing, availability, specifications, or ordering information?"
        elif recent_intents:
            intent_context = recent_intents[-1]  # Most recent intent
            if intent_context == "order":
                return f"{name_greeting}Are you asking about your order? I can help with tracking, delivery status, or cancellations."
            elif intent_context == "product":
                return f"{name_greeting}Are you asking about a product? I can help with pricing, availability, or specifications."
            elif intent_context == "support":
                return f"{name_greeting}Do you need more support assistance? I can help with refunds, returns, or account issues."
        
        # Default vague response
        return f"{name_greeting}I'd be happy to help! Could you please provide a bit more detail about what you're looking for? I can assist with orders, products, support questions, or general information."