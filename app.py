from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import json
from flask_socketio import SocketIO, emit
from agents.human_conversation_manager import HumanConversationManager
from memory.session_manager import SessionManager
import time
import os
from dotenv import load_dotenv
import threading
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# TEXT-TO-SPEECH INTEGRATION
# ============================================================================

# Import TTS engine
import tts_engine

# Initialize TTS at startup (non-blocking)
def initialize_tts_async():
    """Initialize TTS in background to avoid blocking app startup"""
    def _init():
        try:
            success = tts_engine.initialize_tts()
            if success:
                print("🎤 TTS engine ready for voice responses")
            else:
                print("⚠️ TTS engine not available - text-only mode")
        except Exception as e:
            print(f"⚠️ TTS initialization error: {e}")
    
    # Start TTS initialization in background
    init_thread = threading.Thread(target=_init, daemon=True)
    init_thread.start()

# Store audio paths for serving
audio_cache = {}

# ============================================================================
# ENHANCED DATA ACCESS LAYER INTEGRATION
# ============================================================================

# Try to import enhanced data access, fallback to original if dependencies missing
try:
    from data.enhanced_data_access import enhanced_data_access, get_order_by_id, get_enhanced_faq_answer
    
    print(f"✅ Enhanced Data Access Layer loaded:")
    stats = enhanced_data_access.get_dataset_stats()
    print(f"   📦 JSON Orders: {stats['json_orders']['total_orders']} orders from {stats['json_orders']['customers']} customers")
    print(f"   🎫 Support Tickets: {stats['support_tickets']['total_tickets']} tickets")
    print(f"   🇮🇳 India Orders: {stats['india_orders']['total_orders']} orders")
    
    ENHANCED_MODE = True
    
except ImportError as e:
    print(f"⚠️ Enhanced data access not available (missing dependencies): {e}")
    print("📦 Falling back to original data access layer")
    
    # Fallback to original data access
    from data.order_data_access import get_order_by_id
    
    def get_enhanced_faq_answer(user_question):
        """Fallback - no enhancement available"""
        return None
    
    ENHANCED_MODE = False

# ============================================================================
# DATASET LOADING AND HELPER FUNCTIONS (LEGACY - REPLACED BY ENHANCED DATA ACCESS)
# ============================================================================

def load_datasets():
    """
    Load FAQ dataset only - order dataset is now handled by data access layer.
    Returns: tuple of (orders_df, faq_df) for backward compatibility
    """
    try:
        # Order dataset is now handled by OrderDataAccess
        # This function only loads FAQ data for backward compatibility
        
        # Load AI customer support dataset (FAQ-like data)
        with open('datasets/ai_customer_support_data.json', 'r') as f:
            faq_data = json.load(f)
        
        faq_df = pd.DataFrame(faq_data)
        
        print(f"✅ Datasets loaded successfully:")
        print(f"   📦 Orders: Loaded via data access layer")
        print(f"   ❓ FAQ entries: {len(faq_df)} records")
        
        # Return empty DataFrame for orders (handled by data access layer)
        return pd.DataFrame(), faq_df
        
    except Exception as e:
        print(f"❌ Error loading FAQ dataset: {e}")
        # Return empty DataFrames as fallback
        return pd.DataFrame(), pd.DataFrame()

# Legacy function - now delegates to data access layer
def get_order_by_id_legacy(order_id):
    """
    Legacy order lookup function - delegates to data access layer.
    Maintained for backward compatibility.
    """
    try:
        # Convert input to integer (handles both int and str inputs)
        if isinstance(order_id, str):
            # Extract numeric portion if it's a string like "ORD54582"
            import re
            match = re.search(r'(\d+)', order_id)
            if match:
                order_id_int = int(match.group(1))
            else:
                try:
                    order_id_int = int(order_id)
                except ValueError:
                    print(f"❌ Invalid order ID format: {order_id}")
                    return None
        elif isinstance(order_id, int):
            order_id_int = order_id
        else:
            print(f"❌ Invalid order ID type: {type(order_id)}")
            return None
        
        # Delegate to data access layer
        return get_order_by_id(order_id_int)
        
    except Exception as e:
        print(f"❌ Error in legacy order lookup for {order_id}: {e}")
        return None

def get_faq_answer(user_question):
    """
    Enhanced FAQ system that uses multiple data sources when available:
    1. Original FAQ dataset (ai_customer_support_data.json)
    2. Support tickets dataset for real resolution patterns (if available)
    3. Improved keyword matching with domain awareness
    
    Args:
        user_question (str): The user's question
        
    Returns:
        str: FAQ answer if found, None if no match
    """
    try:
        user_question_lower = user_question.lower().strip()
        
        print(f"🔍 {'Enhanced' if ENHANCED_MODE else 'Standard'} FAQ search for: '{user_question}'")
        
        # First, try the enhanced FAQ system using support tickets (if available)
        if ENHANCED_MODE:
            enhanced_answer = get_enhanced_faq_answer(user_question)
            if enhanced_answer:
                # Validate the enhanced answer quality
                if _is_good_enhanced_answer(enhanced_answer):
                    print(f"✅ Enhanced FAQ answer found from support tickets")
                    return enhanced_answer
                else:
                    print(f"⚠️ Enhanced answer quality poor, using fallback")
        
        # Product-specific responses for common issues
        product_response = _get_product_specific_response(user_question_lower)
        if product_response:
            return product_response
        
        # Fallback to original FAQ dataset with improved matching
        domain_keywords = {
            'Food Delivery': ['food', 'delivery', 'restaurant', 'meal', 'subscription'],
            'E-commerce': ['order', 'product', 'shopping', 'purchase', 'coupon', 'discount'],
            'General': ['support', 'help', 'contact', 'technical', 'app', 'issue', 'problem']
        }
        
        # Find matching domain
        matched_domain = None
        for domain, keywords in domain_keywords.items():
            if any(keyword in user_question_lower for keyword in keywords):
                matched_domain = domain
                break
        
        # Filter FAQs by domain if found
        if matched_domain:
            domain_faqs = faq_df[faq_df['domain'] == matched_domain]
            print(f"🎯 Found {len(domain_faqs)} FAQs in domain: {matched_domain}")
        else:
            domain_faqs = faq_df
            print(f"🔍 Searching all {len(faq_df)} FAQs")
        
        if domain_faqs.empty:
            print("❌ No FAQs found in filtered domain")
            domain_faqs = faq_df
        
        # Try to find the most relevant FAQ by matching question keywords
        best_match = None
        best_score = 0
        
        for _, faq in domain_faqs.iterrows():
            faq_question = str(faq['question']).lower()
            faq_answer = str(faq['answer'])
            
            # Count common words between user question and FAQ question
            user_words = set(user_question_lower.split())
            faq_words = set(faq_question.split())
            common_words = len(user_words.intersection(faq_words))
            
            # Also check if user question contains key terms from FAQ
            keyword_matches = sum(1 for word in user_words if word in faq_question)
            
            total_score = common_words + keyword_matches
            
            if total_score > best_score:
                best_score = total_score
                best_match = faq
        
        if best_match is not None and best_score > 0:
            answer = best_match['answer']
            question = best_match['question']
            category = best_match['category']
            print(f"✅ Original FAQ match found: '{question}' (category: {category}, score: {best_score})")
            return answer
        
        # Enhanced fallback responses based on question patterns
        if 'subscription' in user_question_lower and 'food' in user_question_lower:
            return "For subscription-related issues with food delivery services, please contact our support team directly. We can help you manage your subscription, billing, or delivery preferences."
        
        if 'food' in user_question_lower and 'delivery' in user_question_lower:
            return "For food delivery issues, please contact our support team. We can help with orders, delivery problems, payment issues, and food quality concerns."
        
        # Generic fallback for any unmatched query
        return "I can help you with orders, returns, billing, delivery, and technical issues. Could you please provide more specific details about what you need assistance with?"
        
    except Exception as e:
        print(f"❌ Error in FAQ search for '{user_question}': {e}")
        import traceback
        traceback.print_exc()
        return None

def _is_good_enhanced_answer(answer: str) -> bool:
    """Check if enhanced answer is of good quality"""
    if not answer or len(answer) < 20:
        return False
    
    answer_lower = answer.lower()
    
    # Filter out gibberish responses
    bad_patterns = [
        'case maybe show recently my computer follow',
        'measure tonight surface feel forward',
        'west decision evidence bit',
        'try capital clearly never color',
        'soldier we such inside',
        'firm sort voice above which site arrive'
    ]
    
    # Check for bad patterns
    for pattern in bad_patterns:
        if pattern in answer_lower:
            return False
    
    return True

def _get_product_specific_response(question: str) -> Optional[str]:
    """Generate product-specific responses based on question content"""
    
    # GoPro/Camera setup issues
    if any(word in question for word in ['gopro', 'camera', 'setup', 'hero']):
        return "For GoPro setup issues: 1) Ensure the device is fully charged, 2) Download the latest GoPro app, 3) Enable Bluetooth and WiFi on your phone, 4) Follow the in-app pairing instructions. If issues persist, try resetting the camera by holding the mode button for 10 seconds."
    
    # TV/Smart TV issues
    elif any(word in question for word in ['tv', 'smart tv', 'lg', 'peripheral', 'compatibility']):
        return "For Smart TV compatibility issues: 1) Check that all devices are on the same WiFi network, 2) Update your TV's firmware, 3) Restart both the TV and connected devices, 4) Try different HDMI ports if using wired connections. For intermittent issues, check for interference from other wireless devices."
    
    # Dell/Laptop power issues
    elif any(word in question for word in ['dell', 'xps', 'laptop', 'won\'t turn on', 'power', 'charging']):
        return "For Dell XPS power issues: 1) Try a different power outlet, 2) Remove the battery and hold power button for 15 seconds, then reconnect, 3) Check if the power adapter LED is lit, 4) Try powering on without the battery (AC only). If the charger isn't working, ensure you're using the original Dell adapter."
    
    # Microsoft Office/Software issues (ONLY when Microsoft/Office is explicitly mentioned)
    elif ('microsoft' in question.lower() or 'office' in question.lower()) and any(word in question.lower() for word in ['account', 'access', 'billing', 'subscription']):
        return "For Microsoft Office account issues: 1) Try signing out and back in, 2) Clear your browser cache and cookies, 3) Use the Microsoft Account recovery tool, 4) For billing issues, check your subscription status in your Microsoft account dashboard. Contact Microsoft support if the problem persists."
    
    # General technical issues (ONLY for specific technical products, not general issues)
    elif any(word in question for word in ['device not working', 'hardware failure', 'software crash', 'system error']) and not any(word in question for word in ['billing', 'order', 'payment', 'refund']):
        return "For technical issues: 1) Restart the device, 2) Check for software updates, 3) Ensure all connections are secure, 4) Try using the device in safe mode if available, 5) Contact technical support if the issue continues."
    
    return None

# Load datasets at startup
orders_df, faq_df = load_datasets()

# ============================================================================
# DIALOGUE STATE MANAGEMENT
# ============================================================================

# Import the dialogue state manager
from agents.dialogue_state_manager import DialogueStateManager

# Initialize dialogue state manager
dialogue_manager = DialogueStateManager()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize TTS engine in background
initialize_tts_async()

# Initialize components with human conversation flow
STORAGE_TYPE = os.getenv('SESSION_STORAGE', 'json')
STORAGE_PATH = os.getenv('SESSION_STORAGE_PATH', 'data/sessions')

human_conversation_manager = HumanConversationManager()
session_manager = SessionManager(storage_type=STORAGE_TYPE, storage_path=STORAGE_PATH)

print(f"📚 Session storage: {STORAGE_TYPE} at {STORAGE_PATH}")
if STORAGE_TYPE != "memory":
    storage_info = session_manager.get_storage_info()
    print(f"💾 Storage info: {storage_info}")

print("🚀 Kiro AI Assistant with Human Conversation Flow")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ecommerce')
def ecommerce():
    return render_template('ecommerce_simple.html')

@app.route('/chat-debug')
def chat_debug():
    return render_template('chat_debug.html')

@app.route('/debug')
def debug():
    return render_template('debug.html')

@app.route('/audio/<audio_id>')
def serve_audio(audio_id):
    """Serve generated audio files"""
    try:
        if audio_id in audio_cache:
            audio_path = audio_cache[audio_id]
            if os.path.exists(audio_path):
                return send_file(audio_path, mimetype='audio/wav')
        
        # If not in cache, try to find in audio directory
        audio_dir = Path("static/audio")
        audio_file = audio_dir / f"{audio_id}.wav"
        
        if audio_file.exists():
            return send_file(str(audio_file), mimetype='audio/wav')
        
        return jsonify({"error": "Audio not found"}), 404
        
    except Exception as e:
        print(f"❌ Error serving audio {audio_id}: {e}")
        return jsonify({"error": "Audio serving failed"}), 500

@app.route('/tts/status')
def tts_status():
    """Check TTS engine status"""
    return jsonify({
        "available": tts_engine.is_tts_available(),
        "model_loaded": tts_engine._model_loaded
    })

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    print(f"[DEBUG] Socket.IO CONNECT event - Session ID: {request.sid}")
    emit('connection_confirmed', {'status': 'connected', 'session_id': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[DEBUG] Socket.IO DISCONNECT event - Session ID: {request.sid}")

@socketio.on('connect_error')
def handle_connect_error(error):
    print(f"[DEBUG] Socket.IO CONNECT_ERROR event - Error: {error}")

@socketio.on('user_message')
def handle_user_message(data):
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
        # NEW DIALOGUE STATE MANAGEMENT - RULE-BASED MULTI-TURN CONVERSATIONS
        # ============================================================================
        
        try:
            # Use dialogue state manager for multi-turn conversation handling
            result = dialogue_manager.process_message(message, session, get_order_by_id, get_faq_answer)
            
            # Check if user indicates completion
            dialogue_state = dialogue_manager.get_dialogue_state(session)
            completion_result = dialogue_manager.handle_completion(message, dialogue_state)
            if completion_result:
                result = completion_result
            
            response_text = result.get('response', '')
            
            print(f"🎯 Dialogue Manager Response: {response_text[:100]}...")
            
        except Exception as e:
            print(f"❌ Error in dialogue manager: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to simple FAQ lookup
            faq_answer = get_faq_answer(message)
            if faq_answer:
                response_text = faq_answer
            else:
                response_text = "I'm here to help! I can assist with order tracking, returns, billing issues, and general questions. What would you like help with?"
            
            result = {
                'response': response_text,
                'conversation_state': 'fallback',
                'is_human_flow': True
            }
        
        # ============================================================================
        # END DIALOGUE STATE MANAGEMENT
        # ============================================================================
        
        # Save session
        session_manager.update_session(session)
        
        # Final safety check
        final_response = result.get('response', 'I apologize, but I need more information to help you.')
        if not isinstance(final_response, str):
            final_response = str(final_response)
        
        # ============================================================================
        # TEXT-TO-SPEECH INTEGRATION
        # ============================================================================
        
        # Prepare response data
        response_data = {
            'message': final_response,
            'conversation_state': result.get('conversation_state'),
            'is_human_flow': result.get('is_human_flow', True),
            'audio_available': False,
            'audio_url': None
        }
        
        # Send text response immediately (non-blocking)
        print(f"🤖 Sending text response: {final_response[:100]}...")
        emit('bot_message', response_data)
        
        # Generate audio asynchronously (non-blocking)
        if tts_engine.is_tts_available() and tts_engine.should_speak_text(final_response):
            def audio_callback(audio_path):
                try:
                    # Generate unique audio ID
                    audio_id = f"msg_{int(time.time())}_{session_id[-8:]}"
                    
                    # Store in cache for serving
                    audio_cache[audio_id] = audio_path
                    
                    # Send audio notification to client
                    audio_url = f"/audio/{audio_id}"
                    
                    print(f"🎤 Audio ready: {audio_url}")
                    
                    # Emit audio ready event
                    socketio.emit('audio_ready', {
                        'audio_url': audio_url,
                        'session_id': session_id
                    }, room=session_id)
                    
                except Exception as e:
                    print(f"❌ Audio callback error: {e}")
            
            # Start async audio generation
            print(f"🎤 Starting async audio generation...")
            tts_engine.speak_async(final_response, callback=audio_callback)
        
        # ============================================================================
        # END TEXT-TO-SPEECH INTEGRATION
        # ============================================================================
        
    except Exception as e:
        print(f"❌ CRITICAL Error processing message: {e}")
        import traceback
        traceback.print_exc()
        
        # Send error response
        emit('bot_message', {
            "message": "I'm sorry, I encountered an issue processing your message. Could you please try again?"
        })

@socketio.on('clear_session')
def handle_clear_session():
    """Allow users to clear their session completely - no context carryover"""
    session_id = request.sid
    
    print(f"🧹 CLEARING SESSION: {session_id}")
    
    try:
        # Step 1: Clear from session manager (handles persistent storage too)
        session_manager.clear_session(session_id)
        
        # Step 2: Ensure no context leakage by creating a fresh session
        # This forces complete reinitialization
        fresh_session = session_manager.get_session(session_id)
        
        print(f"✅ Session {session_id} cleared completely - fresh start")
        emit('session_cleared', {
            'message': 'Session cleared successfully',
            'session_id': session_id,
            'fresh_start': True
        })
        
    except Exception as e:
        print(f"❌ Error clearing session {session_id}: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback: Force clear from memory at minimum
        if session_id in session_manager.sessions:
            del session_manager.sessions[session_id]
        
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
    
    session_info = {
        'session_id': session_id,
        'user_name': session.user_name,
        'persistent_entities': session.persistent_entities,
        'conversation_length': len(session.conversation_history),
        'communication_style': session.communication_style,
        'user_tone': session.user_tone,
        'unresolved_issues': len([i for i in session.unresolved_issues if i.get('status') == 'open']),
        'storage_info': session_manager.get_storage_info()
    }
    
    emit('session_info', session_info)

# Periodic cleanup of expired sessions and audio files
def cleanup_sessions():
    """Clean up expired sessions periodically"""
    while True:
        time.sleep(300)  # Clean up every 5 minutes
        expired_count = session_manager.cleanup_expired_sessions()
        if expired_count > 0:
            print(f"🧹 Cleaned up {expired_count} expired sessions")
        
        # Also cleanup old audio files
        try:
            tts_engine.cleanup_old_audio_files(max_age_minutes=30)
        except Exception as e:
            print(f"⚠️ Audio cleanup error: {e}")

if __name__ == '__main__':
    print("🚀 Starting Kiro AI Assistant...")
    print("🌐 Access at: http://localhost:5000")
    print("🔧 Debug page at: http://localhost:5000/debug")
    
    # Start session cleanup in background (in production, use proper task queue)
    import threading
    cleanup_thread = threading.Thread(target=cleanup_sessions, daemon=True)
    cleanup_thread.start()
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)