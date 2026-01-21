"""
Response Policy Layer - Fixed, human-written responses for deterministic behavior
NO LLM generation for final answers. Templates selected ONLY by order_state + resolution type.
"""

from typing import Dict, Any
from .state_machine import OrderStatus

class ResponsePolicyLayer:
    """
    Deterministic response selection based on order state and resolution type.
    NO LLM involvement, NO dynamic generation, NO loops.
    """
    
    # FIXED HUMAN-WRITTEN RESPONSE TEMPLATES
    RESPONSE_TEMPLATES = {
        # REFUND RESPONSES
        ("refund", "processing"): "I'm sorry for the inconvenience. I've successfully initiated a refund for order #{order_id}. The amount will be credited within 3–5 business days.",
        ("refund", "unknown"): "I'm sorry for the inconvenience. I've successfully initiated a refund for order #{order_id}. The amount will be credited within 3–5 business days.",
        ("refund", "shipped"): "I'm sorry for the inconvenience. Order #{order_id} has already been shipped, so a refund isn't possible right now. I can help with a replacement or return after delivery.",
        ("refund", "delivered"): "I'm sorry for the inconvenience. Order #{order_id} has already been delivered, so a refund isn't possible right now. I can help with a return process instead.",
        ("refund", "cancelled"): "Order #{order_id} has already been cancelled and a refund is being processed. You'll receive the credit within 3–5 business days.",
        ("refund", "refunded"): "Order #{order_id} has already been refunded. The credit should appear in your account within 3–5 business days.",
        
        # REPLACEMENT RESPONSES  
        ("replacement", "processing"): "Sorry about the mix-up. I've initiated a replacement for order #{order_id}. The correct item will be delivered within 2–3 business days.",
        ("replacement", "unknown"): "Sorry about the mix-up. I've initiated a replacement for order #{order_id}. The correct item will be delivered within 2–3 business days.",
        ("replacement", "shipped"): "Sorry about the mix-up. Since order #{order_id} has already shipped, I've arranged for a replacement to be sent. You'll receive the correct item within 2–3 business days.",
        ("replacement", "delivered"): "Sorry about the mix-up. I've initiated a replacement for order #{order_id}. The correct item will be delivered within 2–3 business days.",
        ("replacement", "cancelled"): "I apologize for the inconvenience. Order #{order_id} has been cancelled, so I can't arrange a replacement. I can help process a new order instead.",
        ("replacement", "refunded"): "I apologize for the inconvenience. Order #{order_id} has been refunded, so I can't arrange a replacement. I can help you place a new order instead.",
        
        # CANCELLATION RESPONSES
        ("cancel", "processing"): "Your order #{order_id} has been successfully cancelled. A full refund will be processed within 3–5 business days.",
        ("cancel", "unknown"): "Your order #{order_id} has been successfully cancelled. A full refund will be processed within 3–5 business days.",
        ("cancel", "shipped"): "I'm sorry, but order #{order_id} has already been shipped and cannot be cancelled. I can help arrange a return after delivery.",
        ("cancel", "delivered"): "I'm sorry, but order #{order_id} has already been delivered and cannot be cancelled. I can help with the return process instead.",
        ("cancel", "cancelled"): "Order #{order_id} has already been cancelled. A full refund will be processed within 3–5 business days.",
        ("cancel", "refunded"): "Order #{order_id} has already been cancelled and refunded. The credit should appear in your account within 3–5 business days.",
        
        # GENERAL ISSUE RESPONSES (for requests without specific issue type)
        ("general", "processing"): "I've successfully processed your request for order #{order_id}. You'll receive confirmation and updates shortly.",
        ("general", "unknown"): "I've successfully processed your request for order #{order_id}. You'll receive confirmation and updates shortly.",
        ("general", "shipped"): "I understand your concern about order #{order_id}. Since it has already shipped, I've noted your request and our team will follow up with you shortly.",
        ("general", "delivered"): "I understand your concern about order #{order_id}. Since it has been delivered, I've noted your request and our team will follow up with you shortly.",
        ("general", "cancelled"): "Order #{order_id} has already been cancelled. If you need further assistance, please let me know.",
        ("general", "refunded"): "Order #{order_id} has already been refunded. The credit should appear in your account within 3–5 business days.",
        
        # TRACKING RESPONSES (NO RESOLUTION PROMPTS)
        ("tracking", "processing"): "Order #{order_id} is currently being processed and will ship soon.",
        ("tracking", "unknown"): "Order #{order_id} is currently being processed and will ship soon.",
        ("tracking", "shipped"): "Order #{order_id} has been shipped and is on the way. You should receive it by tomorrow.",
        ("tracking", "delivered"): "Order #{order_id} has been delivered successfully.",
        ("tracking", "cancelled"): "Order #{order_id} has been cancelled.",
        ("tracking", "refunded"): "Order #{order_id} has been refunded.",
    }
    
    # MISSING INFORMATION RESPONSES (ONLY when truly missing)
    MISSING_INFO_RESPONSES = {
        "order_id": "I can help with that. Please share your order number so I can proceed.",
        "issue": "I can help with your order. Could you tell me what the issue is? (wrong item, delivery problem, or general concern)",
        "resolution": "I understand there's an issue with your order. How would you like me to help? (refund, replacement, or cancellation)"
    }
    
    # POST-RESOLUTION RESPONSE (after flow is complete)
    POST_RESOLUTION_RESPONSE = "Is there anything else I can help you with?"
    
    @classmethod
    def get_response(cls, resolution_type: str, order_status: str, order_id: str) -> str:
        """
        Get deterministic response based on resolution type and order status.
        NO LLM, NO dynamic generation, NO loops.
        """
        # Normalize inputs
        resolution_type = resolution_type.lower() if resolution_type else "general"
        order_status = order_status.lower() if order_status else "unknown"
        
        # Get template key
        template_key = (resolution_type, order_status)
        
        # Get response template
        template = cls.RESPONSE_TEMPLATES.get(template_key)
        
        # Fallback to general if specific combination not found
        if not template:
            fallback_key = ("general", order_status)
            template = cls.RESPONSE_TEMPLATES.get(fallback_key)
        
        # Final fallback
        if not template:
            template = "I've processed your request for order #{order_id}. You'll receive confirmation shortly."
        
        # Format with order ID
        return template.format(order_id=order_id)
    
    @classmethod
    def get_missing_info_response(cls, missing_info_type: str) -> str:
        """Get response for missing information"""
        return cls.MISSING_INFO_RESPONSES.get(missing_info_type, 
            "I need a bit more information to help you with your request.")
    
    @classmethod
    def get_post_resolution_response(cls) -> str:
        """Get response after resolution is complete"""
        return cls.POST_RESOLUTION_RESPONSE
    
    @classmethod
    def validate_response(cls, response: str, order_id: str) -> bool:
        """
        Validate response meets requirements:
        - Contains order_id
        - Does NOT ask new questions (except post-resolution)
        - Is deterministic and final
        """
        if not response or not order_id:
            return False
        
        # Must contain order ID (except for post-resolution response)
        if order_id not in response and response != cls.POST_RESOLUTION_RESPONSE:
            return False
        
        # Must NOT ask questions (except allowed ones)
        question_indicators = ["?", "could you", "can you", "please provide", "what", "how", "when", "where"]
        has_questions = any(indicator in response.lower() for indicator in question_indicators)
        
        # Only allow questions for missing info or post-resolution
        allowed_questions = [
            cls.POST_RESOLUTION_RESPONSE,
            *cls.MISSING_INFO_RESPONSES.values()
        ]
        
        if has_questions and response not in allowed_questions:
            return False
        
        return True