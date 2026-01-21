"""
Deterministic Resolution Engine - NO loops, NO questions, NO LLM for final responses
"""

from typing import Dict, Any
from .response_templates import ResponsePolicyLayer
from .state_machine import OrderStatus

class DeterministicResolver:
    """
    Handles complete requests with deterministic, final responses.
    NO routing, NO status probing, NO clarification questions.
    """
    
    def __init__(self):
        self.response_policy = ResponsePolicyLayer()
    
    def resolve_complete_request(self, order_id: str, issue: str, resolution: str, session) -> Dict[str, Any]:
        """
        CRITICAL: Handle complete request with deterministic response.
        STOP routing, STOP questions, SELECT final response, END flow.
        """
        print(f"🎯 DETERMINISTIC RESOLUTION: order={order_id}, issue={issue}, resolution={resolution}")
        
        # Get or create order state
        order_state = session.get_or_create_order_state(order_id)
        
        # Get current order status
        current_status = order_state.status.value if order_state.status else "unknown"
        
        # Apply business logic for state transitions
        new_status = self._apply_business_logic(current_status, resolution)
        
        # TRACKING SPECIAL CASE: Don't change status, just return tracking info
        if resolution == "tracking":
            # Set default state if unknown
            if current_status == "unknown":
                new_status = "shipped"
                session.transition_order_status(order_id, OrderStatus.SHIPPED, 
                                              tracking_number=f"TRK{order_id}789",
                                              delivery_eta="tomorrow")
            
            # Get tracking response from Response Policy Layer
            response = self.response_policy.get_response("tracking", current_status, order_id)
        else:
            # Update order state if needed
            if new_status != current_status:
                try:
                    new_order_status = OrderStatus(new_status)
                    session.transition_order_status(order_id, new_order_status)
                    print(f"📊 Order status updated: {current_status} → {new_status}")
                except Exception as e:
                    print(f"⚠️ Status transition failed: {e}")
            
            # Get deterministic response from Response Policy Layer
            response = self.response_policy.get_response(resolution, current_status, order_id)
        
        # VALIDATION: Ensure response meets requirements
        if not self.response_policy.validate_response(response, order_id):
            print(f"❌ Response validation failed, using fallback")
            response = f"I've processed your {resolution} request for order #{order_id}. You'll receive confirmation shortly."
        
        # HARD FLOW TERMINATION
        session.resolved = True
        session.last_resolved_order_id = order_id
        session.last_resolution_type = resolution
        
        # Clear active context to prevent loops
        session.clear_active_context()
        
        print(f"✅ RESOLUTION COMPLETE: {response}")
        
        return {
            'response': response,
            'intents': ["resolution_complete"],
            'entities': {"order_number": [order_id]},
            'confidence_scores': {"resolution_complete": 1.0},
            'agents_used': ["deterministic_resolver"],
            'is_multi_intent': False,
            'issue_context': {
                "deterministic_resolution": True,
                "flow_terminated": True,
                "no_further_routing": True
            },
            'session_summary': f"Resolved {resolution} for order #{order_id}"
        }
    
    def handle_missing_info(self, missing_info: str) -> Dict[str, Any]:
        """
        Handle requests with missing information - ask ONLY for what's missing
        """
        response = self.response_policy.get_missing_info_response(missing_info)
        
        return {
            'response': response,
            'intents': ["missing_info"],
            'entities': {},
            'confidence_scores': {"missing_info": 1.0},
            'agents_used': ["deterministic_resolver"],
            'is_multi_intent': False,
            'issue_context': {
                "missing_info": missing_info,
                "deterministic_flow": True
            },
            'session_summary': f"Requesting missing {missing_info}"
        }
    
    def handle_post_resolution(self) -> Dict[str, Any]:
        """
        Handle messages after resolution is complete
        """
        response = self.response_policy.get_post_resolution_response()
        
        return {
            'response': response,
            'intents': ["post_resolution"],
            'entities': {},
            'confidence_scores': {"post_resolution": 1.0},
            'agents_used': ["deterministic_resolver"],
            'is_multi_intent': False,
            'issue_context': {
                "post_resolution": True,
                "flow_complete": True
            },
            'session_summary': "Post-resolution assistance"
        }
    
    def _apply_business_logic(self, current_status: str, resolution: str) -> str:
        """
        Apply business logic to determine new order status
        """
        if resolution == "tracking":
            # For tracking, don't change status unless it's unknown
            if current_status == "unknown":
                return "shipped"  # Default to shipped for tracking
            return current_status
        
        elif resolution == "refund":
            if current_status in ["processing", "unknown"]:
                return "refunded"
            # If already shipped/delivered, status stays same (refund not allowed)
            return current_status
        
        elif resolution == "replacement":
            if current_status in ["processing", "unknown", "shipped", "delivered"]:
                return "replacement_sent"
            return current_status
        
        elif resolution == "cancel":
            if current_status in ["processing", "unknown"]:
                return "cancelled"
            # If already shipped/delivered, status stays same (cancel not allowed)
            return current_status
        
        return current_status
    
    def validate_complete_request(self, order_id: str, issue: str, resolution: str) -> bool:
        """
        Validate that request is truly complete
        """
        # Must have order_id
        if not order_id or len(order_id.strip()) < 3:
            return False
        
        # TRACKING SHORT-CIRCUIT: If both issue and resolution are "tracking", it's valid
        if issue == "tracking" and resolution == "tracking":
            return True
        
        # Must have resolution
        if resolution not in ["refund", "replacement", "cancel", "tracking"]:
            return False
        
        # For cancel, issue can be "cancel" 
        if resolution == "cancel":
            return True
        
        # For refund/replacement, must have issue
        if not issue or issue not in ["wrong_item", "delivery", "damaged", "general", "cancel", "tracking"]:
            return False
        
        return True