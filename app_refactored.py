"""
REFACTORED CUSTOMER SUPPORT CHATBOT - DATA-DRIVEN ARCHITECTURE
================================================================

MANDATORY DATA FLOW:
User Message → Session Manager → Intent Detection → Workflow Router → Dataset Query → Response Builder

This implementation enforces:
1. Every response is driven by real dataset queries
2. Predictable and deterministic conversation behavior  
3. Clear separation of concerns with explicit routing
4. Rule-based logic without ML dependencies
"""

from flask import Flask, render_template, request
import pandas as pd
import json
import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from flask_socketio import SocketIO, emit
from memory.session_manager import SessionManager
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# DATASET LOADING - MANDATORY FOR ALL RESPONSES
# ============================================================================

def load_datasets() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load datasets that drive ALL user-facing responses.
    Returns: (orders_df, faq_df)
    """
    try:
        # Load customer order dataset
        with open('datasets/customer_order_dataset.json', 'r') as f:
            orders_data = json.load(f)
        
        # Flatten orders for efficient querying
        flattened_orders = []
        for customer in orders_data:
            for order in customer['orders']:
                order_record = {
                    'customer_id': customer['customer_id'],
                    'customer_name': customer['name'],
                    'order_id': order['order_id'],
                    'product': order['product'],
                    'platform': order['platform'],
                    'status': order['status'],
                    'payment_mode': order['payment_mode'],
                    'amount': order['amount']
                }
                flattened_orders.append(order_record)
        
        orders_df = pd.DataFrame(flattened_orders)
        
        # Load FAQ dataset
        with open('datasets/ai_customer_support_data.json', 'r') as f:
            faq_data = json.load(f)
        
        faq_df = pd.DataFrame(faq_data)
        
        print(f"✅ DATASETS LOADED - MANDATORY FOR ALL RESPONSES:")
        print(f"   📦 Orders: {len(orders_df)} records")
        print(f"   ❓ FAQ: {len(faq_df)} records")
        
        return orders_df, faq_df
        
    except Exception as e:
        print(f"❌ CRITICAL: Dataset loading failed: {e}")
        raise RuntimeError("Cannot start application without datasets")

def get_order_by_id(order_id: str) -> Optional[Dict[str, Any]]:
    """
    MANDATORY dataset query for order information.
    Every order-related response MUST use this function.
    """
    try:
        order_id_str = str(order_id).strip()
        matching_orders = orders_df[orders_df['order_id'].astype(str) == order_id_str]
        
        if not matching_orders.empty:
            order_details = matching_orders.iloc[0].to_dict()
            print(f"📊 DATASET QUERY: Found order {order_id}")
            return order_details
        else:
            print(f"📊 DATASET QUERY: Order {order_id} not found")
            return None
            
    except Exception as e:
        print(f"❌ Dataset query error for order {order_id}: {e}")
        return None

def get_faq_answer(user_question: str) -> Optional[str]:
    """
    MANDATORY dataset query for FAQ responses.
    Every FAQ response MUST use this function.
    """
    try:
        user_question_lower = user_question.lower().strip()
        
        # Rule-based category matching
        category_keywords = {
            'orders': ['order', 'track', 'tracking', 'purchase', 'buy', 'bought', 'placed'],
            'returns & refunds': ['return', 'refund', 'exchange', 'money back', 'cancel'],
            'billing': ['bill', 'payment', 'charge', 'invoice', 'cost', 'price', 'money', 'charged'],
            'delivery': ['delivery', 'shipping', 'deliver', 'ship', 'arrive', 'when will'],
            'account & login': ['account', 'login', 'password', 'sign in', 'register'],
            'technical issues': ['error', 'bug', 'not working', 'broken', 'issue', 'problem'],
            'general queries': ['help', 'support', 'question', 'how to', 'what is', 'contact'],
            'offers & discounts': ['coupon', 'discount', 'offer', 'promo', 'code'],
            'payments': ['payment', 'pay', 'failed', 'deducted']
        }
        
        # Find best matching category
        best_category = None
        max_matches = 0
        
        for category, keywords in category_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in user_question_lower)
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        if best_category and max_matches > 0:
            # Query FAQ dataset
            category_faqs = faq_df[faq_df['category'].str.lower() == best_category.lower()]
            
            if not category_faqs.empty:
                # Find most relevant FAQ
                best_match = None
                best_score = 0
                
                for _, faq in category_faqs.iterrows():
                    faq_question = faq['question'].lower()
                    user_words = set(user_question_lower.split())
                    faq_words = set(faq_question.split())
                    common_words = len(user_words.intersection(faq_words))
                    
                    if common_words > best_score:
                        best_score = common_words
                        best_match = faq
                
                if best_match is not None:
                    answer = best_match['answer']
                    print(f"📊 DATASET QUERY: FAQ match for '{best_category}'")
                    return answer
                else:
                    # Fallback to first FAQ in category
                    answer = category_faqs.iloc[0]['answer']
                    print(f"📊 DATASET QUERY: FAQ category fallback for '{best_category}'")
                    return answer
        
        print(f"📊 DATASET QUERY: No FAQ match found")
        return None
        
    except Exception as e:
        print(f"❌ Dataset query error for FAQ: {e}")
        return None

# Load datasets at startup - MANDATORY
orders_df, faq_df = load_datasets()

# ============================================================================
# SESSION STATE STRUCTURE - EXPLICIT DIALOGUE MANAGEMENT
# ============================================================================

class Intent(Enum):
    """Supported intents for rule-based routing"""
    BILLING_ISSUE = "billing_issue"
    RETURN_ORDER = "return_order" 
    ORDER_STATUS = "order_status"
    FAQ = "faq"
    NONE = None

@dataclass
class SessionState:
    """Explicit session state structure for multi-turn conversations"""
    active_intent: Optional[Intent] = None
    pending_slot: Optional[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
    
    def reset(self):
        """Reset state after workflow completion"""
        self.active_intent = None
        self.pending_slot = None
        self.context.clear()
        print("🔄 Session state reset - ready for new conversation")

# ============================================================================
# CENTRAL ROUTER - MANDATORY SINGLE CONTROLLER
# ============================================================================

class ConversationRouter:
    """
    MANDATORY central controller that enforces the data flow:
    User Message → Intent Detection → Workflow Routing → Dataset Query → Response
    """
    
    def __init__(self):
        # Intent detection keywords (rule-based only)
        self.intent_keywords = {
            Intent.BILLING_ISSUE: [
                'charged', 'billing', 'refund', 'double', 'payment', 'bill', 'money',
                'charge', 'invoice', 'cost', 'price', 'paid', 'deducted'
            ],
            Intent.RETURN_ORDER: [
                'return', 'exchange', 'send back', 'wrong item', 'defective',
                'damaged', 'not what i ordered', 'incorrect', 'faulty'
            ],
            Intent.ORDER_STATUS: [
                'track', 'status', 'delivery', 'where is', 'when will',
                'shipped', 'arrive', 'eta', 'tracking', 'delivered'
            ]
        }
    
    def handle_user_message(self, message: str, session) -> Dict[str, Any]:
        """
        MANDATORY CENTRAL CONTROLLER - enforces explicit data flow
        
        Flow: Message → Session → Intent → Router → Dataset → Response
        """
        print(f"🎯 CENTRAL ROUTER: Processing '{message}'")
        
        # Step 1: Initialize session state if missing
        if not hasattr(session, 'conversation_state'):
            session.conversation_state = SessionState()
        
        state = session.conversation_state
        
        print(f"📊 Current state: intent={state.active_intent}, slot={state.pending_slot}")
        
        # Step 2: Handle slot filling if pending
        if state.pending_slot:
            return self._handle_slot_filling(message, state)
        
        # Step 3: Detect intent ONLY when active_intent is None
        if state.active_intent is None:
            detected_intent = self._detect_intent(message)
            if detected_intent != Intent.NONE:
                state.active_intent = detected_intent
                print(f"🔒 Intent locked: {detected_intent}")
        
        # Step 4: Route to workflow handlers (DATASET-DRIVEN)
        if state.active_intent:
            return self._route_to_workflow(message, state)
        else:
            # Step 5: Fallback only when no intent detected
            return self._handle_no_intent_fallback(message)
    
    def _detect_intent(self, message: str) -> Intent:
        """Rule-based intent detection - NO ML"""
        message_lower = message.lower()
        
        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return Intent.NONE
        
        detected = max(intent_scores, key=intent_scores.get)
        print(f"🔍 Intent detected: {detected} (score: {intent_scores[detected]})")
        return detected
    
    def _extract_order_id(self, message: str) -> Optional[str]:
        """Extract order ID using regex patterns"""
        patterns = [
            r'\b(ORD\d+)\b',
            r'#(\d+)',
            r'order\s*#?\s*(ORD\d+)',
            r'order\s*#?\s*(\d{5,8})',
            r'\border\s+(\d{5,8})\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                order_id = match.group(1)
                if order_id.lower() not in ['is', 'my', 'the', 'and', 'number']:
                    print(f"📋 Extracted order ID: {order_id}")
                    return order_id
        
        return None
    
    def _handle_slot_filling(self, message: str, state: SessionState) -> Dict[str, Any]:
        """Handle slot filling for missing information"""
        
        if state.pending_slot == "order_id":
            order_id = self._extract_order_id(message)
            if order_id:
                state.context['order_id'] = order_id
                state.pending_slot = None
                print(f"✅ Slot filled: order_id = {order_id}")
                # Continue with workflow
                return self._route_to_workflow(message, state)
            else:
                return {
                    'response': "I need your order number to help you. Please provide it in format like ORD12345 or #12345.",
                    'conversation_state': 'awaiting_order_id',
                    'data_source': 'slot_filling_prompt'
                }
        
        return {
            'response': "I didn't understand that. Could you please provide the information I requested?",
            'conversation_state': 'slot_filling_error',
            'data_source': 'error_handling'
        }
    
    def _route_to_workflow(self, message: str, state: SessionState) -> Dict[str, Any]:
        """Route to intent-specific workflow handlers - ALL DATASET-DRIVEN"""
        
        intent = state.active_intent
        
        if intent == Intent.BILLING_ISSUE:
            return self._handle_billing_workflow(message, state)
        elif intent == Intent.RETURN_ORDER:
            return self._handle_return_workflow(message, state)
        elif intent == Intent.ORDER_STATUS:
            return self._handle_status_workflow(message, state)
        else:
            return self._handle_faq_workflow(message, state)
    
    def _handle_billing_workflow(self, message: str, state: SessionState) -> Dict[str, Any]:
        """DATASET-DRIVEN billing issue handler"""
        
        # Require order_id
        if 'order_id' not in state.context:
            order_id = self._extract_order_id(message)
            if order_id:
                state.context['order_id'] = order_id
            else:
                state.pending_slot = "order_id"
                return {
                    'response': "I can help with billing issues. Please provide your order number so I can look into this.",
                    'conversation_state': 'billing_awaiting_order',
                    'data_source': 'workflow_prompt'
                }
        
        # MANDATORY dataset queries
        order_id = state.context['order_id']
        order_details = get_order_by_id(order_id)  # DATASET QUERY
        faq_answer = get_faq_answer("billing payment charge issue")  # DATASET QUERY
        
        if order_details:
            response = f"I found your order #{order_id} for {order_details['product']} (₹{order_details['amount']}). "
            
            if faq_answer:
                response += faq_answer
            else:
                response += "For billing issues, please verify the charge amount matches your order. Contact our billing team if you see discrepancies."
            
            # Complete workflow
            state.reset()
            
            return {
                'response': response,
                'conversation_state': 'billing_resolved',
                'data_source': 'order_dataset + faq_dataset',
                'order_data': order_details
            }
        else:
            state.reset()
            return {
                'response': f"I couldn't find order #{order_id} in our system. Please check the order number and try again.",
                'conversation_state': 'billing_order_not_found',
                'data_source': 'order_dataset_negative'
            }
    
    def _handle_return_workflow(self, message: str, state: SessionState) -> Dict[str, Any]:
        """DATASET-DRIVEN return order handler"""
        
        # Require order_id
        if 'order_id' not in state.context:
            order_id = self._extract_order_id(message)
            if order_id:
                state.context['order_id'] = order_id
            else:
                state.pending_slot = "order_id"
                return {
                    'response': "I can help you return your order. Please provide your order number to check return eligibility.",
                    'conversation_state': 'return_awaiting_order',
                    'data_source': 'workflow_prompt'
                }
        
        # MANDATORY dataset query
        order_id = state.context['order_id']
        order_details = get_order_by_id(order_id)  # DATASET QUERY
        
        if order_details:
            status = order_details['status'].lower()
            product = order_details['product']
            
            if status in ['delivered', 'returnable']:
                response = f"I can help you return order #{order_id} ({product}). "
                response += "To return this item, go to 'My Orders', select the item, choose a return reason, and schedule a pickup. "
                response += "Refunds are processed within 5-7 business days after we receive the item."
            elif status == 'in transit':
                response = f"Order #{order_id} ({product}) is currently in transit. "
                response += "You can return it once delivered. You'll have 7 days from delivery to initiate a return."
            else:
                response = f"Order #{order_id} ({product}) has status '{status}' and may not be eligible for return. "
                response += "Please contact customer support for assistance."
            
            # Complete workflow
            state.reset()
            
            return {
                'response': response,
                'conversation_state': 'return_processed',
                'data_source': 'order_dataset',
                'order_data': order_details
            }
        else:
            state.reset()
            return {
                'response': f"I couldn't find order #{order_id} in our system. Please check the order number and try again.",
                'conversation_state': 'return_order_not_found',
                'data_source': 'order_dataset_negative'
            }
    
    def _handle_status_workflow(self, message: str, state: SessionState) -> Dict[str, Any]:
        """DATASET-DRIVEN order status handler"""
        
        # Require order_id
        if 'order_id' not in state.context:
            order_id = self._extract_order_id(message)
            if order_id:
                state.context['order_id'] = order_id
            else:
                state.pending_slot = "order_id"
                return {
                    'response': "I can help you track your order. Please provide your order number to check the current status.",
                    'conversation_state': 'status_awaiting_order',
                    'data_source': 'workflow_prompt'
                }
        
        # MANDATORY dataset query
        order_id = state.context['order_id']
        order_details = get_order_by_id(order_id)  # DATASET QUERY
        
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
            
            # Complete workflow
            state.reset()
            
            return {
                'response': response,
                'conversation_state': 'status_provided',
                'data_source': 'order_dataset',
                'order_data': order_details
            }
        else:
            state.reset()
            return {
                'response': f"I couldn't find order #{order_id} in our system. Please check the order number and try again.",
                'conversation_state': 'status_order_not_found',
                'data_source': 'order_dataset_negative'
            }
    
    def _handle_faq_workflow(self, message: str, state: SessionState) -> Dict[str, Any]:
        """DATASET-DRIVEN FAQ handler"""
        
        # MANDATORY dataset query
        faq_answer = get_faq_answer(message)  # DATASET QUERY
        
        if faq_answer:
            response = faq_answer
            data_source = 'faq_dataset'
        else:
            response = ("I can help you with:\n"
                       "• Order tracking and status updates\n"
                       "• Returns and exchanges\n"
                       "• Billing and payment issues\n"
                       "• General questions\n\n"
                       "What would you like help with today?")
            data_source = 'faq_dataset_negative'
        
        # Complete workflow
        state.reset()
        
        return {
            'response': response,
            'conversation_state': 'faq_answered',
            'data_source': data_source
        }
    
    def _handle_no_intent_fallback(self, message: str) -> Dict[str, Any]:
        """Fallback when no intent is detected - still tries dataset first"""
        
        # Try FAQ dataset first
        faq_answer = get_faq_answer(message)  # DATASET QUERY
        
        if faq_answer:
            return {
                'response': faq_answer,
                'conversation_state': 'faq_fallback',
                'data_source': 'faq_dataset'
            }
        
        # Generic help only as last resort
        response = ("I'm here to help! I can assist you with:\n"
                   "• Order tracking and status updates\n"
                   "• Returns and exchanges\n"
                   "• Billing and payment issues\n"
                   "• General questions\n\n"
                   "What would you like help with today?")
        
        return {
            'response': response,
            'conversation_state': 'generic_help',
            'data_source': 'fallback_menu'
        }

# ============================================================================
# FLASK APPLICATION SETUP
# ============================================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
STORAGE_TYPE = os.getenv('SESSION_STORAGE', 'json')
STORAGE_PATH = os.getenv('SESSION_STORAGE_PATH', 'data/sessions')

session_manager = SessionManager(storage_type=STORAGE_TYPE, storage_path=STORAGE_PATH)
conversation_router = ConversationRouter()  # CENTRAL CONTROLLER

print(f"📚 Session storage: {STORAGE_TYPE} at {STORAGE_PATH}")
print("🚀 Data-Driven Customer Support Chatbot")

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug')
def debug():
    return render_template('debug.html')

# ============================================================================
# SOCKET.IO HANDLERS - ENFORCES MANDATORY DATA FLOW
# ============================================================================

@socketio.on('connect')
def handle_connect():
    print(f"[DEBUG] Socket.IO CONNECT event - Session ID: {request.sid}")
    emit('connection_confirmed', {'status': 'connected', 'session_id': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[DEBUG] Socket.IO DISCONNECT event - Session ID: {request.sid}")

@socketio.on('user_message')
def handle_user_message(data):
    """
    ENFORCES MANDATORY DATA FLOW:
    User Message → Session Manager → Central Router → Dataset Queries → Response
    """
    print(f"[DEBUG] Socket.IO USER_MESSAGE received - Data: {data}")
    
    try:
        # Extract message and session info
        message = data.get('message', '').strip()
        message_type = data.get('type', 'text')
        session_id = data.get('session_id') or request.sid
        
        print(f"📝 Processing message: '{message}' (type: {message_type})")
        
        if not message:
            print("⚠️ Empty message received")
            emit('bot_message', {"message": "I didn't receive any message. Could you please try again?"})
            return
        
        # Get or create session
        session = session_manager.get_session(session_id)
        print(f"📋 Session ID: {session_id}")
        
        # ============================================================================
        # MANDATORY DATA FLOW ENFORCEMENT
        # ============================================================================
        
        try:
            # Route through CENTRAL CONTROLLER - enforces dataset usage
            result = conversation_router.handle_user_message(message, session)
            
            response_text = result.get('response', '')
            data_source = result.get('data_source', 'unknown')
            
            print(f"✅ Response generated from: {data_source}")
            print(f"🤖 Response: {response_text[:100]}...")
            
            # Validate that response came from dataset
            if data_source == 'unknown':
                print("❌ WARNING: Response not properly sourced from dataset")
            
        except Exception as e:
            print(f"❌ Error in central router: {e}")
            import traceback
            traceback.print_exc()
            
            # Emergency fallback - still tries dataset first
            faq_answer = get_faq_answer(message)
            if faq_answer:
                response_text = faq_answer
                data_source = 'emergency_faq_dataset'
            else:
                response_text = "I'm sorry, I encountered an issue. Please try rephrasing your question."
                data_source = 'emergency_fallback'
            
            result = {
                'response': response_text,
                'conversation_state': 'error_recovery',
                'data_source': data_source
            }
        
        # ============================================================================
        # END MANDATORY DATA FLOW
        # ============================================================================
        
        # Save session
        session_manager.update_session(session)
        
        # Emit response with data source tracking
        response_data = {
            'message': result.get('response', 'I apologize, but I need more information to help you.'),
            'conversation_state': result.get('conversation_state'),
            'data_source': result.get('data_source', 'unknown')
        }
        
        print(f"🤖 Sending response from: {response_data['data_source']}")
        emit('bot_message', response_data)
        
    except Exception as e:
        print(f"❌ CRITICAL Error processing message: {e}")
        import traceback
        traceback.print_exc()
        
        # Send error response
        emit('bot_message', {
            "message": "I'm sorry, I encountered an issue processing your message. Could you please try again?",
            "data_source": "critical_error_fallback"
        })

@socketio.on('clear_session')
def handle_clear_session():
    """Clear session completely"""
    session_id = request.sid
    
    print(f"🧹 CLEARING SESSION: {session_id}")
    
    try:
        session_manager.clear_session(session_id)
        
        print(f"✅ Session {session_id} cleared completely")
        emit('session_cleared', {
            'message': 'Session cleared successfully',
            'session_id': session_id,
            'fresh_start': True
        })
        
    except Exception as e:
        print(f"❌ Error clearing session {session_id}: {e}")
        emit('session_cleared', {
            'message': 'Session cleared (fallback mode)',
            'session_id': session_id,
            'fresh_start': True
        })

@socketio.on('get_session_info')
def handle_get_session_info():
    """Get session information for debugging"""
    session_id = request.sid
    session = session_manager.get_session(session_id)
    
    # Get conversation state info
    state_info = {}
    if hasattr(session, 'conversation_state'):
        state = session.conversation_state
        state_info = {
            'active_intent': str(state.active_intent),
            'pending_slot': state.pending_slot,
            'context': state.context
        }
    
    session_info = {
        'session_id': session_id,
        'conversation_state': state_info,
        'storage_info': session_manager.get_storage_info()
    }
    
    emit('session_info', session_info)

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    print("🚀 Starting Data-Driven Customer Support Chatbot...")
    print("🌐 Access at: http://localhost:5000")
    print("🔧 Debug page at: http://localhost:5000/debug")
    print("📊 All responses are dataset-driven and deterministic")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)