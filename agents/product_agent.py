from .base_agent import BaseAgent

class ProductAgent(BaseAgent):
    def __init__(self):
        super().__init__("product")
    
    def process(self, message: str, context: dict) -> str:
        message_lower = message.lower()
        
        # Get entities from current message and session
        current_entities = context.get("detected_entities", {})
        session_entities = context.get("persistent_entities", {})
        personalization = context.get("personalization", {})
        is_multi_intent = context.get("is_multi_intent", False)
        
        # Extract personalization details
        user_name = personalization.get("user_name")
        user_tone = personalization.get("user_tone", "neutral")
        empathy_level = personalization.get("empathy_level", "standard")
        communication_style = personalization.get("communication_style", "friendly")
        
        # Try to get product name from current message or session
        product_name = None
        if "product_name" in current_entities and current_entities["product_name"]:
            product_name = current_entities["product_name"][0]
        elif "product_name" in session_entities:
            product_name = session_entities["product_name"]
        
        # Enhanced context-aware product detection
        if not product_name:
            # Check for follow-up patterns like "it", "that product", "this item"
            if any(word in message_lower for word in ["it", "that", "this", "the product", "the item"]):
                # User is referring to a previous product - check session
                if "product_name" in session_entities:
                    product_name = session_entities["product_name"]
        
        # Personalize greeting based on context
        greeting = self._get_personalized_greeting(user_name, user_tone, empathy_level, is_multi_intent)
        
        if product_name:
            # We have a product name - provide specific information
            if any(word in message_lower for word in ["price", "cost", "how much"]):
                return f"{greeting}The {product_name} is currently priced at $299.99. We have a special promotion running - use code SAVE10 for 10% off! Would you like me to check for any other current discounts?"
            
            elif any(word in message_lower for word in ["available", "stock", "in stock"]):
                return f"{greeting}Great news! The {product_name} is currently in stock with 25+ units available. We can ship it today if you place your order before 3 PM EST. Would you like to proceed with the purchase?"
            
            elif any(word in message_lower for word in ["specs", "specifications", "features", "details"]):
                return f"{greeting}Here are the key specifications for {product_name}: Premium build quality, latest technology, 2-year warranty included, free shipping. It's one of our most popular items! Would you like detailed technical specifications or have specific questions about features?"
            
            elif any(word in message_lower for word in ["reviews", "rating", "feedback"]):
                return f"{greeting}The {product_name} has excellent customer reviews with a 4.8/5 star rating! Customers love its reliability and performance. Would you like me to share some recent customer feedback?"
            
            elif any(word in message_lower for word in ["buy", "purchase", "order"]):
                return f"{greeting}I'd be happy to help you purchase the {product_name}! It's $299.99 with free shipping and a 2-year warranty. You can add it to your cart on our website, or I can guide you through the ordering process. Would you like me to check for any current promotions first?"
            
            else:
                # General product info
                return f"{greeting}Here's what I know about {product_name}: It's priced at $299.99, currently in stock, and has excellent reviews (4.8/5 stars). What specific information would you like to know about this product?"
        
        else:
            # No specific product mentioned - provide context-aware assistance
            conversation_history = context.get("conversation_history", [])
            has_previous_product_context = any("product" in msg.get("intents", []) for msg in conversation_history[-3:])
            
            if any(word in message_lower for word in ["price", "cost", "how much"]):
                if has_previous_product_context:
                    return f"{greeting}I can help you find pricing information! Which specific product were you asking about? Please provide the product name or model number and I'll get you the current price and any available discounts."
                else:
                    return f"{greeting}I can help you find pricing information! Which specific product are you interested in? Please provide the product name or model number and I'll get you the current price and any available discounts."
            
            elif any(word in message_lower for word in ["available", "stock", "in stock"]):
                return f"{greeting}I'll check product availability for you! What product are you looking for? Please share the product name and I'll verify current stock levels and shipping options."
            
            elif any(word in message_lower for word in ["specs", "specifications", "features", "details"]):
                return f"{greeting}I'd be happy to provide detailed product specifications! Which product would you like to know more about? I can share features, dimensions, technical details, and warranty information."
            
            elif any(word in message_lower for word in ["compare", "difference", "vs", "versus"]):
                return f"{greeting}I can help you compare products! Which products are you considering? Please tell me the specific models you'd like me to compare and I'll highlight the key differences."
            
            elif any(word in message_lower for word in ["recommend", "suggestion", "best"]):
                return f"{greeting}I'd love to recommend the perfect product for you! What are you looking for? Please tell me your needs, budget, or the type of product you're interested in, and I'll suggest the best options."
            
            elif any(word in message_lower for word in ["buy", "purchase", "order"]):
                return f"{greeting}I'd be happy to help you make a purchase! What product are you interested in buying? Once you let me know, I can provide pricing, availability, and guide you through the ordering process."
            
            else:
                return f"{greeting}I'm here to help with product information! I can provide details about pricing, availability, specifications, reviews, and recommendations. What product are you interested in learning about?"
    
    def _get_personalized_greeting(self, user_name: str, user_tone: str, empathy_level: str, is_multi_intent: bool) -> str:
        """Generate a personalized greeting based on user context"""
        if is_multi_intent:
            # For multi-intent, keep greeting minimal
            if user_name:
                return f"{user_name}, for the product question: "
            else:
                return "For the product question: "
        
        # Single intent greetings
        if user_tone == "frustrated" and empathy_level == "high":
            if user_name:
                return f"{user_name}, I'm sorry you're having trouble, and I want to help you find the right product information. "
            else:
                return "I'm sorry you're having trouble, and I want to help you find the right product information. "
        
        elif user_tone == "urgent":
            if user_name:
                return f"{user_name}, I understand this is urgent. Let me help you with product information right away. "
            else:
                return "I understand this is urgent. Let me help you with product information right away. "
        
        elif user_name:
            return f"{user_name}, "
        
        else:
            return ""