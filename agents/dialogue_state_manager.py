"""
Dialogue State Manager for Multi-turn Conversation Handling
Implements rule-based intent persistence and slot filling without ML
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class Intent(Enum):
    """Supported intents for the chatbot"""
    CUSTOMER_LOOKUP = "customer_lookup"  # NEW: Customer ID lookup
    ORDER_DETAIL_QUERY = "order_detail_query"  # NEW: HIGHEST PRIORITY
    BILLING_ISSUE = "billing_issue"
    RETURN_ORDER = "return_order"
    ORDER_STATUS = "order_status"
    FAQ = "faq"
    NONE = None

@dataclass
class DialogueState:
    """Session state structure for multi-turn conversations"""
    active_intent: Optional[Intent] = None
    pending_slot: Optional[str] = None
    context: Dict[str, Any] = None
    workflow_completed: bool = False
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
    
    def reset(self):
        """Reset dialogue state for new conversation"""
        self.active_intent = None
        self.pending_slot = None
        self.context.clear()
        self.workflow_completed = False
        print("🔄 Dialogue state reset - ready for new conversation")

class DialogueStateManager:
    """
    Manages dialogue state and intent persistence for multi-turn conversations.
    Uses simple rule-based logic without ML or external NLP libraries.
    """
    
    def __init__(self):
        # ============================================================================
        # INTENT KEYWORDS WITH STRICT PRIORITY RULES (EXACT DEFINITIONS)
        # ============================================================================
        
        # HIGHEST PRIORITY: Customer lookup queries
        self.CUSTOMER_LOOKUP_KEYWORDS = [
            "customer", "customer id", "customer details", "customer information",
            "cust", "details regarding customer", "customer profile"
        ]
        
        # SECOND PRIORITY: Order detail queries (READ-ONLY information)
        self.ORDER_DETAIL_KEYWORDS = [
            "price", "cost", "amount",
            "details", "detail", 
            "product", "item",
            "ordered", "order details"
        ]
        
        # Billing issue keywords (MUST NOT overlap with order details)
        self.BILLING_ISSUE_KEYWORDS = [
            "charged", "double", "refund",
            "payment", "billing", "debited", 
            "money deducted"
        ]
        
        # Intent detection keywords (rule-based) with STRICT PRIORITY ORDER
        self.intent_keywords = {
            # 1. HIGHEST PRIORITY: customer_lookup
            Intent.CUSTOMER_LOOKUP: self.CUSTOMER_LOOKUP_KEYWORDS,
            
            # 2. SECOND PRIORITY: order_detail_query
            Intent.ORDER_DETAIL_QUERY: self.ORDER_DETAIL_KEYWORDS,
            
            # 2. Return/Cancel orders (MUST include "cancel" keyword)
            Intent.RETURN_ORDER: [
                'return', 'exchange', 'send back', 'wrong item', 'defective',
                'damaged', 'not what i ordered', 'incorrect', 'faulty',
                'cancel', 'cancellation', 'cancel my order'  # ADDED CANCEL KEYWORDS
            ],
            
            # 3. Order status tracking (MORE SPECIFIC - removed "delivery" to avoid conflicts)
            Intent.ORDER_STATUS: [
                'track', 'status', 'where is', 'when will',
                'shipped', 'arrive', 'eta', 'tracking', 'delivered'
            ],
            
            # 4. Billing issues (LOWER PRIORITY - must not override order details)
            Intent.BILLING_ISSUE: self.BILLING_ISSUE_KEYWORDS,
            
            # 5. FAQ - General queries (LOWEST PRIORITY for order-related queries)
            Intent.FAQ: [
                'subscription', 'food delivery', 'internet', 'connection', 'issue',
                'problem', 'help', 'support', 'question', 'how to', 'what is',
                'contact', 'hours', 'business', 'app', 'crashing', 'technical',
                'coupon', 'discount', 'offer', 'promo', 'food', 'restaurant'
            ]
        }
        
        # Required slots for each intent
        self.required_slots = {
            Intent.CUSTOMER_LOOKUP: ['customer_id'],  # NEW: Customer ID lookup
            Intent.ORDER_DETAIL_QUERY: ['order_id'],  # NEW
            Intent.BILLING_ISSUE: ['order_id'],
            Intent.RETURN_ORDER: ['order_id'],
            Intent.ORDER_STATUS: ['order_id'],
            Intent.FAQ: []  # FAQ doesn't require order_id
        }
    
    def get_dialogue_state(self, session) -> DialogueState:
        """Get or create dialogue state for session"""
        if not hasattr(session, 'dialogue_state') or session.dialogue_state is None:
            session.dialogue_state = DialogueState()
        return session.dialogue_state
    
    def process_message(self, message: str, session, get_order_by_id_func, get_faq_answer_func) -> Dict[str, Any]:
        """
        Process user message with dialogue state tracking.
        
        Args:
            message: User's message
            session: Session object
            get_order_by_id_func: Function to lookup orders
            get_faq_answer_func: Function to get FAQ answers
            
        Returns:
            Dict with response and state information
        """
        dialogue_state = self.get_dialogue_state(session)
        
        print(f"🎯 Processing message with dialogue state:")
        print(f"   Active intent: {dialogue_state.active_intent}")
        print(f"   Pending slot: {dialogue_state.pending_slot}")
        print(f"   Context: {dialogue_state.context}")
        
        # Handle slot filling if we're waiting for specific information
        if dialogue_state.pending_slot:
            return self._handle_slot_filling(message, dialogue_state, session, get_order_by_id_func, get_faq_answer_func)
        
        # Detect intent only if no active intent exists
        if dialogue_state.active_intent is None:
            detected_intent = self._detect_intent(message)
            if detected_intent != Intent.NONE:
                dialogue_state.active_intent = detected_intent
                print(f"🔒 Intent locked: {detected_intent}")
        
        # Route message based on active intent
        if dialogue_state.active_intent:
            return self._route_workflow(message, dialogue_state, session, get_order_by_id_func, get_faq_answer_func)
        else:
            # Fallback behavior - no intent detected
            return self._handle_fallback(message, get_faq_answer_func)
    
    def _detect_intent(self, message: str) -> Intent:
        """
        Detect intent using rule-based keyword matching with STRICT PRIORITY ORDER.
        MANDATORY: order_detail_query has HIGHEST PRIORITY and MUST NOT be overridden.
        """
        message_lower = message.lower()
        
        # ============================================================================
        # STRICT PRIORITY ORDER (NON-NEGOTIABLE)
        # ============================================================================
        
        # 1. HIGHEST PRIORITY: customer_lookup
        if any(keyword in message_lower for keyword in self.CUSTOMER_LOOKUP_KEYWORDS):
            print(f"🔍 Intent detected: CUSTOMER_LOOKUP (HIGHEST PRIORITY)")
            return Intent.CUSTOMER_LOOKUP
        
        # 2. SECOND PRIORITY: order_detail_query (READ-ONLY information)
        if any(keyword in message_lower for keyword in self.ORDER_DETAIL_KEYWORDS):
            print(f"🔍 Intent detected: ORDER_DETAIL_QUERY (SECOND PRIORITY)")
            return Intent.ORDER_DETAIL_QUERY
        
        # 2. Return/Cancel orders (MUST be checked before FAQ to catch cancellations)
        if any(keyword in message_lower for keyword in self.intent_keywords[Intent.RETURN_ORDER]):
            print(f"🔍 Intent detected: RETURN_ORDER")
            return Intent.RETURN_ORDER
        
        # 3. Order status tracking
        if any(keyword in message_lower for keyword in self.intent_keywords[Intent.ORDER_STATUS]):
            print(f"🔍 Intent detected: ORDER_STATUS")
            return Intent.ORDER_STATUS
        
        # 4. Billing issues (LOWER PRIORITY - cannot override order details)
        if any(keyword in message_lower for keyword in self.BILLING_ISSUE_KEYWORDS):
            print(f"🔍 Intent detected: BILLING_ISSUE")
            return Intent.BILLING_ISSUE
        
        # 5. FAQ - General queries (ONLY for non-order related queries)
        if any(keyword in message_lower for keyword in self.intent_keywords[Intent.FAQ]):
            print(f"🔍 Intent detected: FAQ")
            return Intent.FAQ
        
        # 6. Fallback - if no specific keywords, treat as FAQ
        print(f"🔍 No specific intent detected - defaulting to FAQ")
        return Intent.FAQ
    
    def _extract_order_id(self, message: str) -> Optional[int]:
        """
        Extract order ID from message using regex patterns.
        MANDATORY: Accept ALL formats: "45", "ORD45", "#45", "order 45"
        Extract ONLY the numeric portion and return as integer.
        """
        # STRICT RULE: Extract FIRST numeric sequence from ANY format
        match = re.search(r'(\d+)', message)
        if match:
            order_id = int(match.group(1))
            print(f"📋 Extracted order ID: {order_id} from input: '{message}'")
            return order_id
        
        print(f"❌ No numeric order ID found in: '{message}'")
        return None
    
    def _extract_customer_id(self, message: str) -> Optional[str]:
        """
        Extract customer ID from message using regex patterns.
        Supports formats: "CUST0001", "CUST000714", "customer CUST0001", etc.
        """
        # Look for CUST followed by numbers
        match = re.search(r'CUST\d+', message.upper())
        if match:
            customer_id = match.group(0)
            print(f"👤 Extracted customer ID: {customer_id} from input: '{message}'")
            return customer_id
        
        print(f"❌ No customer ID found in message: '{message}'")
        return None
    
    def _handle_slot_filling(self, message: str, dialogue_state: DialogueState, session, get_order_by_id_func, get_faq_answer_func) -> Dict[str, Any]:
        """
        Handle slot filling when waiting for specific information.
        CRITICAL: NEVER reset intent on lookup failure - preserve state across retries.
        """
        
        if dialogue_state.pending_slot == "order_id":
            order_id = self._extract_order_id(message)
            if order_id:
                # Store order ID in dialogue context and session persistent entities
                dialogue_state.context['order_id'] = order_id
                # Also save to session persistent entities for future use across workflows
                if hasattr(session, 'persistent_entities'):
                    session.persistent_entities['order_number'] = str(order_id)
                
                dialogue_state.pending_slot = None
                print(f"✅ Slot filled - order_id: {order_id} (saved to both dialogue context and session)")
                
                # Continue with the workflow
                return self._route_workflow(message, dialogue_state, session, get_order_by_id_func, get_faq_answer_func)
            else:
                # Still need order ID - DO NOT reset intent
                print(f"⚠️ Invalid order ID input: '{message}' - asking again")
                return {
                    'response': "I need your order number to help you. Please provide your order number (e.g., 45, ORD45, or #45).",
                    'conversation_state': 'awaiting_order_id',
                    'is_human_flow': True
                }
        
        elif dialogue_state.pending_slot == "customer_id":
            customer_id = self._extract_customer_id(message)
            if customer_id:
                # Store customer ID in dialogue context
                dialogue_state.context['customer_id'] = customer_id
                dialogue_state.pending_slot = None
                print(f"✅ Slot filled - customer_id: {customer_id}")
                
                # Continue with the workflow
                return self._route_workflow(message, dialogue_state, session, get_order_by_id_func, get_faq_answer_func)
            else:
                # Still need customer ID
                print(f"⚠️ Invalid customer ID input: '{message}' - asking again")
                return {
                    'response': "I need a valid customer ID to help you. Please provide your customer ID (e.g., CUST0001, CUST000714).",
                    'conversation_state': 'awaiting_customer_id',
                    'is_human_flow': True
                }
        
        # Handle other potential slots here
        return {
            'response': "I didn't understand that. Could you please provide the information I requested?",
            'conversation_state': 'slot_filling_error',
            'is_human_flow': True
        }
    
    def _route_workflow(self, message: str, dialogue_state: DialogueState, session, get_order_by_id_func, get_faq_answer_func) -> Dict[str, Any]:
        """Route message based on active intent with STRICT PRIORITY ORDER"""
        
        intent = dialogue_state.active_intent
        
        # HIGHEST PRIORITY: Customer lookup
        if intent == Intent.CUSTOMER_LOOKUP:
            return self._handle_customer_lookup_workflow(message, dialogue_state, session, get_order_by_id_func)
        # SECOND PRIORITY: Order detail queries (READ-ONLY information)
        elif intent == Intent.ORDER_DETAIL_QUERY:
            return self._handle_order_detail_workflow(message, dialogue_state, session, get_order_by_id_func)
        elif intent == Intent.ORDER_STATUS:
            return self._handle_status_workflow(message, dialogue_state, session, get_order_by_id_func)
        elif intent == Intent.RETURN_ORDER:
            return self._handle_return_workflow(message, dialogue_state, session, get_order_by_id_func)
        elif intent == Intent.BILLING_ISSUE:
            return self._handle_billing_workflow(message, dialogue_state, session, get_order_by_id_func, get_faq_answer_func)
        else:
            # FAQ fallback
            return self._handle_faq_workflow(message, dialogue_state, get_faq_answer_func)
    
    def _handle_customer_lookup_workflow(self, message: str, dialogue_state: DialogueState, session, get_order_by_id_func) -> Dict[str, Any]:
        """
        Handle customer lookup queries - comprehensive customer information.
        """
        
        # Check if we need customer ID
        if 'customer_id' not in dialogue_state.context:
            customer_id = self._extract_customer_id(message)
            if customer_id:
                dialogue_state.context['customer_id'] = customer_id
            else:
                # Ask for customer ID
                dialogue_state.pending_slot = "customer_id"
                return {
                    'response': "Please provide the customer ID you want to look up (e.g., CUST0001, CUST000714).",
                    'conversation_state': 'customer_lookup_awaiting_id',
                    'is_human_flow': True
                }
        
        # We have customer ID, lookup customer details
        customer_id = dialogue_state.context['customer_id']
        
        # Import the customer lookup function
        try:
            from data.enhanced_data_access import get_customer_by_id
            customer_details = get_customer_by_id(customer_id)
        except ImportError:
            return {
                'response': "Customer lookup feature is not available at the moment. Please try again later.",
                'conversation_state': 'customer_lookup_error',
                'is_human_flow': True
            }
        
        if customer_details:
            # Generate comprehensive customer information response
            response = f"📋 Customer Details for {customer_id}:\n\n"
            response += f"👤 Name: {customer_details.get('customer_name', 'Unknown')}\n"
            response += f"📦 Total Orders: {customer_details.get('total_orders', 0)}\n"
            response += f"💰 Total Amount: ₹{customer_details.get('order_summary', {}).get('total_amount', 0):,}\n\n"
            
            # Order status summary
            order_summary = customer_details.get('order_summary', {})
            response += f"📊 Order Status Summary:\n"
            response += f"• Delivered: {order_summary.get('delivered', 0)}\n"
            response += f"• In Transit: {order_summary.get('in_transit', 0)}\n"
            response += f"• Returned: {order_summary.get('returned', 0)}\n"
            response += f"• Pending: {order_summary.get('pending', 0)}\n\n"
            
            # Payment method summary
            payment_summary = customer_details.get('payment_summary', {})
            response += f"💳 Payment Methods Used:\n"
            response += f"• COD: {payment_summary.get('cod', 0)} orders\n"
            response += f"• Card: {payment_summary.get('card', 0)} orders\n"
            response += f"• UPI: {payment_summary.get('upi', 0)} orders\n"
            response += f"• Wallet: {payment_summary.get('wallet', 0)} orders\n\n"
            
            # Platform summary
            platform_summary = customer_details.get('platform_summary', {})
            if platform_summary:
                response += f"🛒 Platform Usage:\n"
                for platform, count in platform_summary.items():
                    response += f"• {platform}: {count} orders\n"
                response += "\n"
            
            # Recent orders (show first 3)
            orders = customer_details.get('orders', [])
            if orders:
                response += f"📋 Recent Orders:\n"
                for i, order in enumerate(orders[:3]):
                    response += f"{i+1}. Order #{order.get('order_id')}: {order.get('product')} - ₹{order.get('amount', 0):,} ({order.get('status')})\n"
                
                if len(orders) > 3:
                    response += f"... and {len(orders) - 3} more orders\n"
            
            # Mark workflow as completed
            dialogue_state.workflow_completed = True
            self._complete_workflow(dialogue_state)
            
            return {
                'response': response,
                'conversation_state': 'customer_lookup_provided',
                'is_human_flow': True
            }
        else:
            # Customer not found - ask for retry
            dialogue_state.context.pop('customer_id', None)
            dialogue_state.pending_slot = "customer_id"
            
            print(f"⚠️ Customer {customer_id} not found - staying in customer_lookup intent for retry")
            
            return {
                'response': f"I couldn't find customer {customer_id} in our records. Please check the customer ID and try again.",
                'conversation_state': 'customer_lookup_not_found_retry',
                'is_human_flow': True
            }
    
    def _handle_order_detail_workflow(self, message: str, dialogue_state: DialogueState, session, get_order_by_id_func) -> Dict[str, Any]:
        """
        Handle order detail queries (READ-ONLY information).
        MANDATORY: Provide clean, factual answers without billing explanations.
        """
        
        # Check if we need order ID
        if 'order_id' not in dialogue_state.context:
            order_id = self._extract_order_id(message)
            if order_id:
                dialogue_state.context['order_id'] = order_id
            else:
                # Ask for order ID
                dialogue_state.pending_slot = "order_id"
                return {
                    'response': "Please provide your order number so I can get the details for you.",
                    'conversation_state': 'order_detail_awaiting_order',
                    'is_human_flow': True
                }
        
        # We have order ID, lookup order details
        order_id = dialogue_state.context['order_id']
        order_details = get_order_by_id_func(order_id)
        
        if order_details:
            # Generate clean, factual response based on what user asked for
            message_lower = message.lower()
            
            # Determine what specific detail was requested
            if any(word in message_lower for word in ["price", "cost", "amount"]):
                amount = order_details.get('amount', 0)
                response = f"The price for order #{order_id} is ₹{amount:,}."
            
            elif any(word in message_lower for word in ["product", "item", "ordered"]):
                product = order_details.get('product', 'Unknown')
                response = f"Order #{order_id} is for {product}."
            
            elif any(word in message_lower for word in ["details", "detail"]):
                # Full order details
                product = order_details.get('product', 'Unknown')
                amount = order_details.get('amount', 0)
                platform = order_details.get('platform', 'Unknown')
                status = order_details.get('status', 'Unknown')
                
                response = f"Order #{order_id} details:\n"
                response += f"• Product: {product}\n"
                response += f"• Amount: ₹{amount:,}\n"
                response += f"• Platform: {platform}\n"
                response += f"• Status: {status}"
            
            else:
                # Generic order information
                product = order_details.get('product', 'Unknown')
                amount = order_details.get('amount', 0)
                response = f"Order #{order_id} is for {product} with amount ₹{amount:,}."
            
            # Mark workflow as completed
            dialogue_state.workflow_completed = True
            self._complete_workflow(dialogue_state)
            
            return {
                'response': response,
                'conversation_state': 'order_detail_provided',
                'is_human_flow': True
            }
        else:
            # Order not found - ask for retry
            dialogue_state.context.pop('order_id', None)
            dialogue_state.pending_slot = "order_id"
            
            print(f"⚠️ Order {order_id} not found - staying in order_detail_query intent for retry")
            
            return {
                'response': "I couldn't find that order. Please recheck the order number.",
                'conversation_state': 'order_detail_not_found_retry',
                'is_human_flow': True
            }
    
    def _handle_billing_workflow(self, message: str, dialogue_state: DialogueState, session, get_order_by_id_func, get_faq_answer_func) -> Dict[str, Any]:
        """
        Handle billing issue workflow.
        CRITICAL: Preserve context across billing discussions - DO NOT reset session context.
        """
        
        # CRITICAL FIX: Check BOTH dialogue context AND session persistent entities for order_id
        order_id = None
        
        # First check dialogue context
        if 'order_id' in dialogue_state.context:
            order_id = dialogue_state.context['order_id']
        # Then check session persistent entities (survives workflow resets)
        elif hasattr(session, 'persistent_entities') and 'order_number' in session.persistent_entities:
            order_id_str = session.persistent_entities['order_number']
            # Extract numeric portion from order number
            import re
            match = re.search(r'(\d+)', str(order_id_str))
            if match:
                order_id = int(match.group(1))
                # Store in dialogue context for this workflow
                dialogue_state.context['order_id'] = order_id
                print(f"🔄 Reusing order_id {order_id} from session persistent entities")
        
        # If no order_id found, try to extract from current message or ask for it
        if not order_id:
            order_id = self._extract_order_id(message)
            if order_id:
                dialogue_state.context['order_id'] = order_id
                # Also save to session persistent entities for future use
                if hasattr(session, 'persistent_entities'):
                    session.persistent_entities['order_number'] = str(order_id)
            else:
                # Ask for order ID
                dialogue_state.pending_slot = "order_id"
                return {
                    'response': "I can help you with billing issues. Please provide your order number so I can look into this for you.",
                    'conversation_state': 'billing_awaiting_order',
                    'is_human_flow': True
                }
        
        # We have order ID, lookup order details
        order_details = get_order_by_id_func(order_id)
        
        if order_details:
            message_lower = message.lower()
            
            # Handle follow-up responses about refund status
            if any(word in message_lower for word in ['no', 'not yet', 'haven\'t received', 'still waiting']):
                # User indicates they haven't received the refund yet
                response = "Refunds can take 3–5 business days to appear in your account. If it has been longer than that, I will escalate this to our billing team for immediate review."
                
                # Keep context for potential further follow-ups
                dialogue_state.pending_slot = None
                
                return {
                    'response': response,
                    'conversation_state': 'billing_refund_escalation',
                    'is_human_flow': True
                }
            
            # Handle initial refund inquiries
            elif any(word in message_lower for word in ['refund', 'refunded', 'money back', 'didn\'t get']):
                status = order_details.get('status', '').lower()
                if 'refund' in status or status == 'refunded':
                    response = f"I see order #{order_id} shows as refunded. Has the amount reached your bank account yet?"
                else:
                    response = f"I found your order #{order_id} for {order_details['product']} (₹{order_details['amount']}). Let me help you with the refund process. What specific issue are you experiencing?"
                
                # Keep context and don't set pending_slot - we want to handle follow-ups
                dialogue_state.pending_slot = None
                
                return {
                    'response': response,
                    'conversation_state': 'billing_refund_inquiry',
                    'is_human_flow': True
                }
            
            # Handle double charging issues
            elif any(word in message_lower for word in ['charged twice', 'double charge', 'charged multiple']):
                response = f"I found your order #{order_id} for {order_details['product']} (₹{order_details['amount']}). Double charges usually occur as temporary authorization holds that get released automatically within 3-5 business days. If you see multiple permanent charges, I can escalate this immediately."
                
                dialogue_state.pending_slot = None
                
                return {
                    'response': response,
                    'conversation_state': 'billing_double_charge',
                    'is_human_flow': True
                }
            
            else:
                # General billing issue response - provide specific billing help instead of FAQ
                response = f"I found your order #{order_id} for {order_details['product']} (₹{order_details['amount']:,}). "
                response += "I can help you with billing issues such as:\n"
                response += "• Refund requests and status\n"
                response += "• Double charges or incorrect amounts\n"
                response += "• Payment method issues\n"
                response += "• Billing disputes\n\n"
                response += "What specific billing issue are you experiencing with this order?"
                
                dialogue_state.pending_slot = None
                
                return {
                    'response': response,
                    'conversation_state': 'billing_general_inquiry',
                    'is_human_flow': True
                }
            
        else:
            # CRITICAL: Order not found - DO NOT reset session, ask for retry
            # Clear the invalid order_id but keep intent and ask again
            dialogue_state.context.pop('order_id', None)
            # Also clear from session persistent entities if it was invalid
            if hasattr(session, 'persistent_entities') and 'order_number' in session.persistent_entities:
                if str(order_id) == str(session.persistent_entities['order_number']):
                    session.persistent_entities.pop('order_number', None)
            
            dialogue_state.pending_slot = "order_id"
            
            print(f"⚠️ Order {order_id} not found - staying in billing_issue intent for retry")
            
            return {
                'response': "I couldn't find that order. Please recheck the order number.",
                'conversation_state': 'billing_order_not_found_retry',
                'is_human_flow': True
            }
    
    def _handle_return_workflow(self, message: str, dialogue_state: DialogueState, session, get_order_by_id_func) -> Dict[str, Any]:
        """
        Handle return order workflow.
        CRITICAL: Preserve intent across retries - DO NOT reset on lookup failure.
        """
        
        # Check if we need order ID
        if 'order_id' not in dialogue_state.context:
            order_id = self._extract_order_id(message)
            if order_id:
                dialogue_state.context['order_id'] = order_id
            else:
                # Ask for order ID
                dialogue_state.pending_slot = "order_id"
                return {
                    'response': "I can help you return your order. Please provide your order number so I can check the return eligibility.",
                    'conversation_state': 'return_awaiting_order',
                    'is_human_flow': True
                }
        
        # We have order ID, lookup order details
        order_id = dialogue_state.context['order_id']
        order_details = get_order_by_id_func(order_id)
        
        if order_details:
            status = order_details['status'].lower()
            
            if status in ['delivered', 'returnable']:
                response = f"I can help you return order #{order_id} ({order_details['product']}). "
                response += "To return this item, go to 'My Orders', select the item, choose a return reason, and schedule a pickup. "
                response += "Refunds are processed within 5-7 business days after we receive the item."
            elif status == 'in transit':
                response = f"Order #{order_id} is currently in transit. You can return it once it's delivered. "
                response += "You'll have 7 days from delivery to initiate a return."
            else:
                response = f"Order #{order_id} has status '{status}' and may not be eligible for return. "
                response += "Please contact customer support for assistance with this order."
            
            # Mark workflow as completed ONLY on successful resolution
            dialogue_state.workflow_completed = True
            self._complete_workflow(dialogue_state)
            
            return {
                'response': response,
                'conversation_state': 'return_processed',
                'is_human_flow': True
            }
        else:
            # CRITICAL: Order not found - DO NOT reset session, ask for retry
            # Clear the invalid order_id but keep intent and ask again
            dialogue_state.context.pop('order_id', None)
            dialogue_state.pending_slot = "order_id"
            
            print(f"⚠️ Order {order_id} not found - staying in return_order intent for retry")
            
            return {
                'response': "I couldn't find that order. Please recheck the order number.",
                'conversation_state': 'return_order_not_found_retry',
                'is_human_flow': True
            }
    
    def _handle_status_workflow(self, message: str, dialogue_state: DialogueState, session, get_order_by_id_func) -> Dict[str, Any]:
        """
        Handle order status workflow.
        CRITICAL: Preserve intent across retries - DO NOT reset on lookup failure.
        """
        
        # Check if we need order ID
        if 'order_id' not in dialogue_state.context:
            order_id = self._extract_order_id(message)
            if order_id:
                dialogue_state.context['order_id'] = order_id
            else:
                # Ask for order ID
                dialogue_state.pending_slot = "order_id"
                return {
                    'response': "I can help you track your order. Please provide your order number to check the current status.",
                    'conversation_state': 'status_awaiting_order',
                    'is_human_flow': True
                }
        
        # We have order ID, lookup order details
        order_id = dialogue_state.context['order_id']
        order_details = get_order_by_id_func(order_id)
        
        if order_details:
            status = order_details['status']
            product = order_details['product']
            platform = order_details['platform']
            
            if status.lower() == 'delivered':
                response = f"Great news! Your order #{order_id} for {product} has been delivered."
            elif status.lower() == 'in transit':
                response = f"Your order #{order_id} for {product} is currently in transit and on its way to you. "
                response += "You should receive it within 1-2 business days."
            elif status.lower() == 'processing':
                response = f"Your order #{order_id} for {product} is being processed and will ship soon. "
                response += "You'll receive tracking information once it ships."
            elif status.lower() == 'shipped':
                response = f"Your order #{order_id} for {product} has shipped and is on its way to you."
            else:
                response = f"Your order #{order_id} for {product} has status: {status}."
            
            response += f" (Ordered from {platform})"
            
            # Mark workflow as completed ONLY on successful resolution
            dialogue_state.workflow_completed = True
            self._complete_workflow(dialogue_state)
            
            return {
                'response': response,
                'conversation_state': 'status_provided',
                'is_human_flow': True
            }
        else:
            # CRITICAL: Order not found - DO NOT reset session, ask for retry
            # Clear the invalid order_id but keep intent and ask again
            dialogue_state.context.pop('order_id', None)
            dialogue_state.pending_slot = "order_id"
            
            print(f"⚠️ Order {order_id} not found - staying in order_status intent for retry")
            
            return {
                'response': "I couldn't find that order. Please recheck the order number.",
                'conversation_state': 'status_order_not_found_retry',
                'is_human_flow': True
            }
    
    def _handle_faq_workflow(self, message: str, dialogue_state: DialogueState, get_faq_answer_func) -> Dict[str, Any]:
        """Handle FAQ workflow"""
        
        faq_answer = get_faq_answer_func(message)
        
        if faq_answer:
            response = faq_answer
        else:
            response = "I can help you with orders, returns, billing issues, and general questions. What would you like assistance with?"
        
        # Mark workflow as completed
        dialogue_state.workflow_completed = True
        self._complete_workflow(dialogue_state)
        
        return {
            'response': response,
            'conversation_state': 'faq_answered',
            'is_human_flow': True
        }
    
    def _handle_fallback(self, message: str, get_faq_answer_func) -> Dict[str, Any]:
        """Handle fallback when no intent is detected"""
        
        # Try FAQ first
        faq_answer = get_faq_answer_func(message)
        
        if faq_answer:
            return {
                'response': faq_answer,
                'conversation_state': 'faq_fallback',
                'is_human_flow': True
            }
        
        # Generic help message
        response = ("I'm here to help! I can assist you with:\n"
                   "• Order tracking and status updates\n"
                   "• Returns and exchanges\n"
                   "• Billing and payment issues\n"
                   "• General questions\n\n"
                   "What would you like help with today?")
        
        return {
            'response': response,
            'conversation_state': 'generic_help',
            'is_human_flow': True
        }
    
    def _complete_workflow(self, dialogue_state: DialogueState):
        """Complete current workflow and reset state"""
        print(f"✅ Workflow completed for intent: {dialogue_state.active_intent}")
        dialogue_state.reset()
    
    def check_completion_keywords(self, message: str, dialogue_state: DialogueState) -> bool:
        """Check if user indicates task completion"""
        completion_keywords = [
            'thank you', 'thanks', 'that helps', 'perfect', 'great',
            'solved', 'resolved', 'done', 'that\'s all', 'no more questions'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in completion_keywords)
    
    def handle_completion(self, message: str, dialogue_state: DialogueState) -> Dict[str, Any]:
        """Handle workflow completion confirmation"""
        if self.check_completion_keywords(message, dialogue_state):
            dialogue_state.reset()
            return {
                'response': "You're welcome! Feel free to reach out if you need any more help.",
                'conversation_state': 'conversation_completed',
                'is_human_flow': True
            }
        return None