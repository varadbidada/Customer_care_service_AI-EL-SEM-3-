from typing import Dict, Any, Optional
from .conversation_state import ConversationState, ConversationStateManager
from .human_response_generator import HumanResponseGenerator
from .llm_service import LLMService
from .state_machine import ConversationFlow
from .human_response_wrapper import HumanResponseWrapper

class HumanConversationManager:
    def __init__(self):
        self.llm_service = LLMService()
        self.response_generator = HumanResponseGenerator()
        self.response_wrapper = HumanResponseWrapper()
        
    def process_human_conversation(self, message: str, session) -> Dict[str, Any]:
        """
        DETERMINISTIC RESPONSE POLICY LAYER - NO loops, NO repeated questions
        """
        
        print(f"🔍 DEBUG: Processing message: '{message}'")
        
        # HARD RULE: If session is resolved, only post-resolution responses
        if hasattr(session, 'resolved') and session.resolved:
            print(f"🔒 SESSION RESOLVED - Post-resolution response only")
            from .deterministic_resolver import DeterministicResolver
            resolver = DeterministicResolver()
            return resolver.handle_post_resolution()
        
        # Use RouterAgent with deterministic resolver
        from .router_agent import RouterAgent
        router = RouterAgent()
        
        try:
            # Process through deterministic router
            result = router.process_with_context(message, session)
            
            print(f"🔍 DEBUG: Router result - deterministic: {result.get('issue_context', {}).get('deterministic_resolution', False)}")
            
            # If deterministic resolution occurred, mark session as resolved
            if result.get('issue_context', {}).get('deterministic_resolution'):
                session.mark_resolved(
                    result.get('entities', {}).get('order_number', ['unknown'])[0],
                    result.get('intents', ['unknown'])[0]
                )
            
            print(f"🔍 DEBUG: Final response: '{result.get('response', '')[:100]}...'")
            return result
            
        except Exception as e:
            print(f"⚠️ Router processing failed: {e}")
            # Fallback response
            return {
                'response': "I'm here to help. Could you please provide your order number and let me know how I can assist you?",
                'conversation_state': 'error_fallback',
                'is_human_flow': False
            }
        
        # Get or create conversation state manager for this session
        if not hasattr(session, 'conversation_state_manager'):
            session.conversation_state_manager = ConversationStateManager()
        
        state_manager = session.conversation_state_manager
        
        print(f"🧠 Current conversation state: {state_manager.current_state.value}")
        print(f"📋 Missing info: {state_manager.missing_info}")
        print(f"🎯 Situation context: {state_manager.situation_context}")
        
        # Use LLM to analyze the conversation context (NO AUTHORITY OVER ORDER STATE)
        conversation_context = {
            'current_state': state_manager.current_state.value,
            'situation_context': state_manager.situation_context,
            'missing_info': state_manager.missing_info
        }
        
        llm_analysis = self.llm_service.analyze_conversation_context(message, conversation_context)
        print(f"🤖 LLM Analysis: {llm_analysis}")
        
        # Extract information from the message (NO ORDER STATE CHANGES)
        extracted_info = llm_analysis.get('extracted_info', {})
        
        # Add extracted information to state manager
        for info_type, value in extracted_info.items():
            if value and value.strip():
                state_manager.add_information(info_type, value)
                print(f"📝 Added {info_type}: {value}")
        
        # Detect situation if not contextual response
        if not llm_analysis.get('is_contextual_response', False):
            detected_situation = state_manager.detect_situation(message, llm_analysis)
            
            # Update conversation state
            state_manager.update_state(detected_situation, {
                'message': message,
                'llm_analysis': llm_analysis,
                **extracted_info
            })
            
            print(f"🔄 Updated state to: {state_manager.current_state.value}")
        
        # Generate human-like response (NO ORDER STATE AUTHORITY)
        response = self.response_generator.generate_empathetic_response(
            state_manager, message, extracted_info
        )
        
        # Handle specific actions based on state (READ-ONLY ORDER ACCESS)
        action_result = self._handle_state_actions(state_manager, session)
        if action_result:
            response += f" {action_result}"
        
        # Validate response against order state machine
        if 'order_number' in extracted_info or 'order_number' in state_manager.situation_context:
            order_num = extracted_info.get('order_number') or state_manager.situation_context.get('order_number')
            if order_num and not session.validate_response_against_state(order_num, response):
                # Use canonical response from state machine
                response = session.get_canonical_order_response(order_num, "status")
        
        # FALLBACK: Original conversation manager logic for incomplete requests
        return self._process_incomplete_request(message, session)
    
    def _process_incomplete_request(self, message: str, session) -> Dict[str, Any]:
        """Process incomplete requests using original conversation manager logic"""
        
        # Get or create conversation state manager for this session
        if not hasattr(session, 'conversation_state_manager'):
            session.conversation_state_manager = ConversationStateManager()
        
        state_manager = session.conversation_state_manager
        
        print(f"🧠 Current conversation state: {state_manager.current_state.value}")
        print(f"📋 Missing info: {state_manager.missing_info}")
        print(f"🎯 Situation context: {state_manager.situation_context}")
        
        # Use LLM to analyze the conversation context (NO AUTHORITY OVER ORDER STATE)
        conversation_context = {
            'current_state': state_manager.current_state.value,
            'situation_context': state_manager.situation_context,
            'missing_info': state_manager.missing_info
        }
        
        llm_analysis = self.llm_service.analyze_conversation_context(message, conversation_context)
        print(f"🤖 LLM Analysis: {llm_analysis}")
        
        # Extract information from the message (NO ORDER STATE CHANGES)
        extracted_info = llm_analysis.get('extracted_info', {})
        
        # Add extracted information to state manager
        for info_type, value in extracted_info.items():
            if value and value.strip():
                state_manager.add_information(info_type, value)
                print(f"📝 Added {info_type}: {value}")
        
        # Detect situation if not contextual response
        if not llm_analysis.get('is_contextual_response', False):
            detected_situation = state_manager.detect_situation(message, llm_analysis)
            
            # Update conversation state
            state_manager.update_state(detected_situation, {
                'message': message,
                'llm_analysis': llm_analysis,
                **extracted_info
            })
            
            print(f"🔄 Updated state to: {state_manager.current_state.value}")
        
        # Generate human-like response (NO ORDER STATE AUTHORITY)
        response = self.response_generator.generate_empathetic_response(
            state_manager, message, extracted_info
        )
        
        # Handle specific actions based on state (READ-ONLY ORDER ACCESS)
        action_result = self._handle_state_actions(state_manager, session)
        if action_result:
            response += f" {action_result}"
        
        # Validate response against order state machine
        if 'order_number' in extracted_info or 'order_number' in state_manager.situation_context:
            order_num = extracted_info.get('order_number') or state_manager.situation_context.get('order_number')
            if order_num and not session.validate_response_against_state(order_num, response):
                # Use canonical response from state machine
                response = session.get_canonical_order_response(order_num, "status")
        
        # VALIDATION LAYER: Prevent status checks when resolution intent exists
        if self._has_resolution_intent(extracted_info, state_manager) and "check status" in response.lower():
            print("🚫 Blocked status check - resolution intent detected")
            order_num = extracted_info.get('order_number') or state_manager.situation_context.get('order_number')
            if order_num:
                response = f"I understand you need help with order #{order_num}. Let me assist you directly."
        
        # Humanize the final response
        humanized_response = self.response_wrapper.wrap(response, {
            "personalization": session.get_personalization_context(),
            "conversation_length": len(session.conversation_history)
        })
        
        # Update session memory
        session.add_message(message, "user")
        session.add_message(humanized_response, "bot")
        
        return {
            'response': humanized_response,
            'conversation_state': state_manager.current_state.value,
            'situation_context': state_manager.situation_context,
            'missing_info': state_manager.missing_info,
            'extracted_info': extracted_info,
            'is_human_flow': True
        }
    
    def _has_resolution_intent(self, extracted_info: Dict[str, Any], state_manager) -> bool:
        """Check if request contains resolution intent"""
        resolution_keywords = ['replacement', 'refund', 'cancel', 'return']
        
        # Check extracted info
        for key, value in extracted_info.items():
            if isinstance(value, str) and any(keyword in value.lower() for keyword in resolution_keywords):
                return True
        
        # Check state manager context
        context_str = str(state_manager.situation_context).lower()
        return any(keyword in context_str for keyword in resolution_keywords)
    
    def _generate_canonical_resolution(self, session) -> str:
        """Generate canonical resolution response when validation fails"""
        if not hasattr(session, 'active_order_id') or not session.active_order_id:
            return "I understand you need help. Could you provide your order number?"
        
        order_id = session.active_order_id
        resolution = getattr(session, 'active_resolution', 'help')
        
        if resolution == 'REPLACEMENT':
            return f"Replacement for order #{order_id} has been initiated. You'll receive the correct item shortly."
        elif resolution == 'REFUND':
            return f"Refund for order #{order_id} has been initiated. You should see the credit within 3-5 business days."
        elif resolution == 'CANCEL':
            order_state = session.get_order_state(order_id)
            if order_state and not order_state.cancellable:
                return f"Order #{order_id} has already shipped and cannot be cancelled."
            else:
                return f"Order #{order_id} has been successfully cancelled."
        else:
            return f"I'm processing your request for order #{order_id}."
        
        # Update session memory
        session.add_message(message, "user")
        session.add_message(humanized_response, "bot")
        
        return {
            'response': humanized_response,
            'conversation_state': state_manager.current_state.value,
            'situation_context': state_manager.situation_context,
            'missing_info': state_manager.missing_info,
            'extracted_info': extracted_info,
            'is_human_flow': True
        }
    
    def _handle_state_actions(self, state_manager: ConversationStateManager, session) -> Optional[str]:
        """Handle specific actions based on conversation state - READ ONLY"""
        
        current_state = state_manager.current_state
        context = state_manager.situation_context
        
        # Wrong item resolution - READ ONLY
        if (current_state == ConversationState.WRONG_ITEM_REPORTED and 
            'order_number' in context and 'resolution_preference' in context):
            
            order_num = context['order_number']
            preference = context['resolution_preference']
            
            # READ ONLY - get current state
            order_state = session.get_order_state(order_num)
            if order_state:
                canonical_response = ""
                if preference == 'refund':
                    canonical_response = f"Based on order #{order_num} status, I can process your refund request."
                elif preference == 'replacement':
                    canonical_response = f"Based on order #{order_num} status, I can arrange a replacement."
                
                return self.response_wrapper.wrap(canonical_response, {
                    "personalization": session.get_personalization_context(),
                    "conversation_length": len(session.conversation_history)
                })
        
        # Order tracking - READ ONLY
        elif (current_state == ConversationState.ORDER_TRACKING and 
              'order_number' in context):
            
            order_num = context['order_number']
            order_state = session.get_order_state(order_num)
            if order_state:
                canonical_response = session.get_canonical_order_response(order_num, "tracking")
                return self.response_wrapper.wrap(canonical_response, {
                    "personalization": session.get_personalization_context(),
                    "conversation_length": len(session.conversation_history)
                })
        
        # Delivery delay resolution - READ ONLY
        elif (current_state == ConversationState.DELIVERY_DELAY and 
              'order_number' in context):
            
            order_num = context['order_number']
            order_state = session.get_order_state(order_num)
            if order_state:
                canonical_response = session.get_canonical_order_response(order_num, "status")
                return self.response_wrapper.wrap(canonical_response, {
                    "personalization": session.get_personalization_context(),
                    "conversation_length": len(session.conversation_history)
                })
        
        return None
    
    def get_conversation_summary(self, session) -> Dict[str, Any]:
        """Get summary of current conversation state"""
        if hasattr(session, 'conversation_state'):
            return session.conversation_state.get_state_summary()
        return {'current_state': 'greeting', 'situation_context': {}, 'missing_info': []}