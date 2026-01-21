import os
from typing import Dict, Any, Optional
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class LLMService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        self.is_available = False
        
        print(f"🔍 Gemini API Status: {'✅ Connected' if self.api_key and self.api_key != 'your_gemini_api_key_here' else '❌ Not configured'}")
        
        if GEMINI_AVAILABLE and self.api_key and self.api_key != 'your_gemini_api_key_here':
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('models/gemini-2.5-flash')
                # Test the connection with a simple prompt
                test_response = self.model.generate_content("Hello")
                if test_response and test_response.text:
                    self.is_available = True
                    print("✅ Google Gemini API initialized successfully")
                else:
                    print("❌ Failed to get response from Gemini API")
                    self.is_available = False
            except Exception as e:
                print(f"❌ Failed to initialize Gemini API: {e}")
                self.is_available = False
        else:
            if not GEMINI_AVAILABLE:
                print("⚠️ Google GenerativeAI package not available.")
            elif not self.api_key:
                print("⚠️ Gemini API key not found in environment variables.")
            elif self.api_key == 'your_gemini_api_key_here':
                print("⚠️ Gemini API key is still set to placeholder value.")
            print("⚠️ Using fallback responses.")
    
    def analyze_conversation_context(self, message: str, conversation_state: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to analyze conversation context and extract information"""
        
        if not self.is_available:
            return self._fallback_analysis(message, conversation_state)
        
        try:
            # Build context-aware analysis prompt
            prompt = self._build_analysis_prompt(message, conversation_state)
            
            # Generate analysis using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=300,
                    temperature=0.3,  # Lower temperature for more consistent analysis
                    top_p=0.8,
                    top_k=40
                )
            )
            
            if response and response.text:
                return self._parse_analysis_response(response.text.strip())
            else:
                return self._fallback_analysis(message, conversation_state)
                
        except Exception as e:
            error_str = str(e)
            if "quota" in error_str.lower() or "429" in error_str:
                print(f"⚠️ Gemini API quota exceeded, using fallback analysis")
                self.is_available = False  # Temporarily disable to avoid repeated quota errors
            else:
                print(f"Error in conversation analysis: {e}")
            return self._fallback_analysis(message, conversation_state)
    
    def _build_analysis_prompt(self, message: str, conversation_state: Dict[str, Any]) -> str:
        """Build prompt for conversation context analysis"""
        
        current_state = conversation_state.get('current_state', 'greeting')
        situation_context = conversation_state.get('situation_context', {})
        missing_info = conversation_state.get('missing_info', [])
        
        prompt = f"""You are analyzing a customer service conversation to understand the situation and extract key information.

CURRENT CONVERSATION STATE: {current_state}
EXISTING CONTEXT: {situation_context}
MISSING INFORMATION: {missing_info}

CUSTOMER MESSAGE: "{message}"

Please analyze this message and respond with ONLY a JSON object containing:

{{
    "detected_situation": "wrong_item|delivery_issue|refund_request|order_inquiry|product_question|general_chat",
    "extracted_info": {{
        "order_number": "if mentioned",
        "expected_item": "what they ordered",
        "received_item": "what they got instead", 
        "expected_date": "when they expected delivery",
        "product_name": "product they're asking about",
        "resolution_preference": "refund|replacement|exchange"
    }},
    "is_contextual_response": true/false,
    "emotional_tone": "frustrated|disappointed|neutral|happy",
    "topic_switch": true/false
}}

Only include fields in extracted_info that are clearly mentioned. Use null for missing values.

Examples:
"I ordered apples but got bananas" → {{"detected_situation": "wrong_item", "extracted_info": {{"expected_item": "apples", "received_item": "bananas"}}, "emotional_tone": "disappointed"}}

"Order 123" → {{"is_contextual_response": true, "extracted_info": {{"order_number": "123"}}}}

"I want a refund" → {{"detected_situation": "refund_request", "extracted_info": {{"resolution_preference": "refund"}}}}"""

        return prompt
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM analysis response"""
        try:
            import json
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                analysis = json.loads(json_str)
                
                # Clean up the analysis
                extracted_info = analysis.get('extracted_info', {})
                # Remove null values
                extracted_info = {k: v for k, v in extracted_info.items() if v is not None and v != "null"}
                analysis['extracted_info'] = extracted_info
                
                return analysis
            else:
                return self._fallback_analysis_result()
                
        except Exception as e:
            print(f"Error parsing LLM analysis: {e}")
            return self._fallback_analysis_result()
    
    def _fallback_analysis(self, message: str, conversation_state: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when LLM is not available"""
        message_lower = message.lower()
        
        # Basic situation detection
        detected_situation = "general_chat"
        extracted_info = {}
        
        # Wrong item detection
        if any(phrase in message_lower for phrase in [
            "wrong item", "got the wrong", "received wrong", "not what i ordered",
            "ordered", "but got", "instead of"
        ]):
            detected_situation = "wrong_item"
            
        # Delivery issue detection
        elif any(phrase in message_lower for phrase in [
            "delivery", "not arrived", "where is", "late", "delayed"
        ]):
            detected_situation = "delivery_issue"
            
        # Refund detection
        elif any(phrase in message_lower for phrase in [
            "refund", "money back", "cancel", "return"
        ]):
            detected_situation = "refund_request"
            
        # Order number extraction
        words = message.split()
        for word in words:
            if word.isdigit() and len(word) >= 3:
                extracted_info['order_number'] = word
                break
        
        return {
            'detected_situation': detected_situation,
            'extracted_info': extracted_info,
            'is_contextual_response': len(message.strip()) < 10,
            'emotional_tone': 'neutral',
            'topic_switch': False
        }
    
    def _fallback_analysis_result(self) -> Dict[str, Any]:
        """Default analysis result"""
        return {
            'detected_situation': 'general_chat',
            'extracted_info': {},
            'is_contextual_response': False,
            'emotional_tone': 'neutral',
            'topic_switch': False
        }
    
    def generate_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate a response using the LLM service - alias for generate_human_like_response"""
        return self.generate_human_like_response(message, context)
    
    def generate_human_like_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate a human-like response using Google Gemini or fallback"""
        
        if not self.is_available:
            return self._fallback_response(message, context)
        
        try:
            # Build context-aware prompt
            prompt = self._build_human_like_prompt(message, context)
            
            # Generate response using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=200,
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40
                )
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return self._fallback_response(message, context)
                
        except Exception as e:
            print(f"Error generating Gemini response: {e}")
            return self._fallback_response(message, context)
    
    def _build_human_like_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """Build a human-like, empathetic prompt for Gemini"""
        
        # Get user context
        user_name = context.get('user_name', '')
        conversation_history = context.get('conversation_history', [])
        entities = context.get('persistent_entities', {})
        communication_style = context.get('communication_style', 'friendly')
        
        # Build conversation context
        recent_context = ""
        if conversation_history:
            recent_messages = []
            for msg in conversation_history[-3:]:
                if msg['sender'] == 'user':
                    recent_messages.append(f"User: {msg['message']}")
                else:
                    recent_messages.append(f"Kiro: {msg['message']}")
            
            if recent_messages:
                recent_context = f"\nRecent conversation:\n" + "\n".join(recent_messages)
        
        # Build entity context
        entity_context = ""
        if entities:
            entity_parts = []
            if 'order_number' in entities:
                entity_parts.append(f"Order: {entities['order_number']}")
            if 'product_name' in entities:
                entity_parts.append(f"Product: {entities['product_name']}")
            if 'email' in entities:
                entity_parts.append(f"Email: {entities['email']}")
            
            if entity_parts:
                entity_context = f"\nKnown context: {', '.join(entity_parts)}"
        
        # Determine tone based on message content and user style
        tone_guidance = self._get_tone_guidance(message, communication_style)
        
        # Build the complete prompt for Gemini
        prompt = f"""You are Kiro, a highly empathetic and intelligent AI customer service assistant. You have a warm, human-like personality and genuinely care about helping customers.

PERSONALITY TRAITS:
- Warm, friendly, and approachable
- Empathetic and understanding, especially with complaints or frustrations
- Professional but not robotic
- Proactive in offering help
- Remember and use personal details when appropriate

COMMUNICATION STYLE:
- Use natural, conversational language
- Be concise but thorough (1-3 sentences typically)
- Show empathy for problems or frustrations
- Use the user's name when you know it: {user_name}
- Adapt tone: {tone_guidance}

CAPABILITIES:
- Help with orders, products, and customer support
- Provide technical assistance and troubleshooting
- Answer general questions and engage in appropriate small talk
- If asked about orders/products/support, suggest they provide specific details

IMPORTANT RULES:
- Don't make up specific order numbers, prices, or account details
- If you don't know something specific, be honest about it
- Always try to be helpful and offer next steps
- Keep responses conversational and human-like
- Respond in a helpful, empathetic manner{entity_context}{recent_context}

Current user message: {message}

Please respond as Kiro would, keeping it natural and helpful:"""
        
        return prompt
    
    def _get_tone_guidance(self, message: str, communication_style: str) -> str:
        """Determine appropriate tone based on message content and user style"""
        message_lower = message.lower()
        
        # Detect emotional context
        if any(word in message_lower for word in ["frustrated", "angry", "upset", "disappointed", "terrible", "awful", "hate"]):
            return "empathetic and apologetic, acknowledge their frustration"
        elif any(word in message_lower for word in ["urgent", "asap", "immediately", "emergency", "critical"]):
            return "responsive and action-oriented, show urgency"
        elif any(word in message_lower for word in ["thank", "appreciate", "great", "awesome", "perfect"]):
            return "warm and positive, match their enthusiasm"
        elif any(word in message_lower for word in ["confused", "don't understand", "help", "lost"]):
            return "patient and explanatory, offer clear guidance"
        else:
            return f"{communication_style} and helpful"
    
    def _fallback_response(self, message: str, context: Dict[str, Any]) -> str:
        """Provide human-like fallback responses when Gemini is not available"""
        
        message_lower = message.lower()
        user_name = context.get('user_name', '')
        name_prefix = f"{user_name}, " if user_name else ""
        
        # Technical issues with empathy
        if any(word in message_lower for word in ["internet", "wifi", "connection", "not working", "broken"]):
            return f"{name_prefix}I understand how frustrating connectivity issues can be! Let's try a few quick fixes: restart your router, check all cables are secure, and try connecting a different device. If the problem persists, your internet service provider can run diagnostics. What specific device or service isn't working?"
        
        # Password/login issues with patience
        elif any(word in message_lower for word in ["password", "login", "sign in", "access", "locked out"]):
            return f"{name_prefix}I can definitely help you get back into your account! Try these steps: use the 'Forgot Password' link on the login page, check if Caps Lock is on, or clear your browser cache. If you're still having trouble, I can guide you through account recovery. What's the specific issue you're seeing?"
        
        # General how-to with encouragement
        elif any(word in message_lower for word in ["how to", "how do i", "how can i"]):
            return f"{name_prefix}I'd love to help you figure that out! Could you be more specific about what you're trying to accomplish? I can provide step-by-step guidance once I understand exactly what you need to do."
        
        # Problems with empathy
        elif any(word in message_lower for word in ["problem", "issue", "trouble", "error", "bug", "frustrated"]):
            return f"{name_prefix}I'm really sorry you're experiencing this issue. I want to help you resolve it as quickly as possible. Can you describe exactly what's happening? The more details you can share, the better I can assist you in finding a solution."
        
        # Compliments with warmth
        elif any(word in message_lower for word in ["great", "awesome", "amazing", "perfect", "excellent"]):
            return f"{name_prefix}Thank you so much for the kind words! It really makes my day to hear that. Is there anything else I can help you with today?"
        
        # General questions with enthusiasm
        elif any(word in message_lower for word in ["what is", "tell me about", "explain"]):
            return f"{name_prefix}I'd be happy to explain that! While I specialize in helping with orders, products, and customer support, I'll do my best to provide useful information. Could you be more specific about what you'd like to know?"
        
        # Default with personality
        else:
            return f"{name_prefix}I'm here to help with whatever you need! I can assist with orders, products, support questions, or just about anything else. What's on your mind today?"