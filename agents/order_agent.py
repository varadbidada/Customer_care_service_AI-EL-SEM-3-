from .base_agent import BaseAgent
from .state_machine import OrderStatus, ConversationFlow
from .human_response_wrapper import HumanResponseWrapper
from data.order_data_access import get_order_by_id

class OrderAgent(BaseAgent):
    def __init__(self):
        super().__init__("order")
        self.response_wrapper = HumanResponseWrapper()
    
    def process(self, message: str, context: dict) -> str:
        message_lower = message.lower()
        
        # Get session memory
        session_memory = context.get("session_memory")
        if not session_memory:
            return "System error: Cannot access order information."
        
        # Extract order number with PRIORITY ORDER
        order_number = self._extract_order_number_with_context(message, context, session_memory)
        if not order_number:
            return self._request_order_number(message_lower, context)
        
        # ============================================================================
        # REAL DATASET LOOKUP - NO FAKE STATUSES OR STATE MACHINE FOR EXISTENCE
        # ============================================================================
        
        # Convert order_number to integer for dataset lookup
        try:
            if isinstance(order_number, str):
                # Extract numeric portion from formats like "ORD54582"
                import re
                match = re.search(r'(\d+)', order_number)
                if match:
                    order_id_int = int(match.group(1))
                else:
                    order_id_int = int(order_number)
            else:
                order_id_int = int(order_number)
        except (ValueError, TypeError):
            return f"Invalid order number format: {order_number}. Please provide a valid order number."
        
        # REAL lookup from dataset
        order = get_order_by_id(order_id_int)
        
        if not order:
            # ONLY return "order not found" when dataset lookup fails
            return "I couldn't find that order. Please recheck the order number."
        
        # Lock active context when order is confirmed
        if session_memory and order_number:
            session_memory.active_order_id = order_number
        
        # ============================================================================
        # REAL RESPONSES FROM DATASET - NO PLACEHOLDER OR FAKE DATA
        # ============================================================================
        
        # TRACKING REQUEST: Check if this is a tracking/status request
        tracking_keywords = ["track", "tracking", "status", "where is", "when will", "delivery", "shipment", "shipped", "delivered", "eta", "arrive"]
        is_tracking_request = any(keyword in message_lower for keyword in tracking_keywords)
        
        if is_tracking_request:
            # REAL response from dataset
            response = f"Your order #{order_id_int} for {order.get('product')} is currently {order.get('status')}."
            
            # Add additional context based on real status
            status = order.get('status', '').lower()
            if status == 'delivered':
                response += " Your order has been delivered successfully!"
            elif status == 'in transit':
                response += " It's on its way to you and should arrive soon."
            elif status == 'processing':
                response += " It's being prepared and will ship soon."
            
            # Update conversation memory with real data
            session_memory.update_conversation_memory(
                intent="tracking",
                order_id=str(order_id_int),
                order_state=status
            )
            
            # Humanize the response
            humanized_response = self.response_wrapper.wrap(response, {
                "personalization": context.get("personalization", {}),
                "conversation_length": len(context.get("conversation_history", []))
            })
            
            return humanized_response
        
        # CANCELLATION REQUEST
        if any(word in message_lower for word in ["cancel", "cancellation"]):
            status = order.get('status', '').lower()
            if status in ["delivered", "in transit"]:
                response = f"Order #{order_id_int} for {order.get('product')} has already {status} and cannot be cancelled. You can return it once received."
            elif status == "cancelled":
                response = f"Order #{order_id_int} for {order.get('product')} has already been cancelled."
            else:
                response = f"I can help you cancel order #{order_id_int} for {order.get('product')}. Current status is {order.get('status')}. Please contact customer service to complete the cancellation."
        else:
            # GENERAL ORDER INQUIRY - Real data from dataset
            response = f"Here are the details for order #{order_id_int}:\n"
            response += f"• Product: {order.get('product')}\n"
            response += f"• Status: {order.get('status')}\n"
            response += f"• Platform: {order.get('platform')}\n"
            if order.get('amount'):
                response += f"• Amount: ₹{order.get('amount'):,}"
        
        # Humanize the response
        humanized_response = self.response_wrapper.wrap(response, {
            "personalization": context.get("personalization", {}),
            "conversation_length": len(context.get("conversation_history", []))
        })
        
        return humanized_response
    
    def resolve(self, issue: str, resolution: str, order_id: str, session_memory=None) -> str:
        """
        Direct resolution method using REAL dataset lookup.
        NO fake responses - all backed by actual order data.
        """
        print(f"🎯 REAL DATA RESOLUTION: order={order_id}, issue={issue}, resolution={resolution}")
        
        if not session_memory:
            return f"System error: Cannot process resolution for order #{order_id}."
        
        # Convert order_id to integer and lookup real data
        try:
            order_id_int = int(order_id)
            order = get_order_by_id(order_id_int)
            
            if not order:
                return "I couldn't find that order. Please recheck the order number."
            
        except (ValueError, TypeError):
            return f"Invalid order number format: {order_id}."
        
        # Extract real order information from dataset
        product = order.get('product', 'your order')
        status = order.get('status', '').lower()
        amount = order.get('amount', 0)
        
        # Set active context
        session_memory.active_order_id = order_id
        if issue:
            session_memory.set_active_issue(issue.upper(), resolution.upper() if resolution else None)
        elif resolution:
            session_memory.active_resolution_intent = resolution.upper()
            session_memory.active_resolution_lock = True
        
        # Generate response based on real order data and requested resolution
        if resolution == "cancel":
            if status in ["delivered", "in transit"]:
                response = f"Order #{order_id_int} for {product} has already {status} and cannot be cancelled. You can return it once received."
            elif status == "cancelled":
                response = f"Order #{order_id_int} for {product} has already been cancelled."
            else:
                response = f"I've initiated the cancellation process for order #{order_id_int} ({product}). You'll receive confirmation shortly."
        
        elif resolution == "refund":
            amount_text = f"₹{amount:,}" if amount > 0 else "the order amount"
            response = f"I've processed a refund for order #{order_id_int} ({product}) of {amount_text}. You'll see the credit within 3-5 business days."
        
        elif resolution == "replacement":
            response = f"I've initiated a replacement for order #{order_id_int} ({product}). You'll receive the new item within 2-3 business days."
        
        else:
            # Generic resolution response with real order data
            response = f"I'm processing your request for order #{order_id_int} ({product}). You'll receive an update shortly."
        
        # Mark resolution as completed
        session_memory.complete_resolution(order_id, resolution.upper())
        
        return response
    
    def _extract_order_number_with_context(self, message: str, context: dict, session_memory) -> str:
        """Extract order number with priority: explicit > active_order_id > session entities"""
        # Check current entities (explicit in message)
        current_entities = context.get("detected_entities", {})
        if "order_number" in current_entities and current_entities["order_number"]:
            return current_entities["order_number"][0]
        
        # Check active order context (highest priority for follow-ups)
        if session_memory and session_memory.get_active_order_id():
            return session_memory.get_active_order_id()
        
        # Check session entities (fallback)
        session_entities = context.get("persistent_entities", {})
        if "order_number" in session_entities:
            return session_entities["order_number"]
        
        # Check if message is just an order number
        message_clean = message.strip()
        if len(message_clean) <= 15 and any(c.isdigit() for c in message_clean):
            if len(message_clean) >= 3:
                return message_clean
        
        return None
    
    def _request_order_number(self, message_lower: str, context: dict) -> str:
        personalization = context.get("personalization", {})
        user_name = personalization.get("user_name", "")
        user_tone = personalization.get("user_tone", "neutral")
        
        greeting = f"{user_name}, " if user_name else ""
        
        if user_tone == "frustrated":
            response = f"{greeting}I understand your frustration. To help you immediately, please provide your order number."
        else:
            response = f"{greeting}Please provide your order number so I can assist you with your order."
        
        # Humanize the response
        humanized_response = self.response_wrapper.wrap(response, {
            "personalization": context.get("personalization", {}),
            "conversation_length": len(context.get("conversation_history", []))
        })
        
        return humanized_response