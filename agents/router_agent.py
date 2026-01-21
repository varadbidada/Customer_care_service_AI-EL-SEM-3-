from .base_agent import BaseAgent
from .nlp_processor import NLPProcessor
from .deterministic_resolver import DeterministicResolver
from memory.session_manager import SessionMemory
from agents.state_machine import OrderStatus
from typing import Dict, List, Any, Tuple

class RouterAgent(BaseAgent):
    def __init__(self):
        super().__init__("router")
        self.nlp = NLPProcessor()
        self.deterministic_resolver = DeterministicResolver()
        
        # Import agents here to avoid circular imports
        from .order_agent import OrderAgent
        from .product_agent import ProductAgent
        from .support_agent import SupportAgent
        from .general_agent import GeneralAgent
        
        self.agents = {
            "order_tracking": OrderAgent(),  # Handle informational tracking requests
            "order_resolution": SupportAgent(),  # Handle resolution requests
            "product": ProductAgent(),
            "support": SupportAgent(),
            "general": GeneralAgent()
        }
    
    def process_with_context(self, message: str, session: SessionMemory) -> Dict[str, Any]:
        """
        DETERMINISTIC RESPONSE POLICY LAYER
        NO loops, NO repeated questions, NO status probing after complete detection
        """
        
        # HARD RULE: If session is already resolved, only give post-resolution response
        if session.is_resolved():
            print(f"🔒 SESSION ALREADY RESOLVED - Post-resolution response only")
            return self.deterministic_resolver.handle_post_resolution()
        
        # FOLLOW-UP DETECTION (CRITICAL FOR CONVERSATION CONTINUITY)
        if session.is_follow_up_message(message):
            print(f"🔄 FOLLOW-UP MESSAGE DETECTED - Using conversation memory")
            
            # Generate follow-up response using stored context
            follow_up_response = session.get_follow_up_response()
            
            # Update session with message
            session.add_message(message, "user")
            session.add_message(follow_up_response, "bot")
            
            return {
                'response': follow_up_response,
                'intents': ["tracking_followup"],
                'entities': {"order_number": [session.last_order_id] if session.last_order_id else []},
                'confidence_scores': {"tracking_followup": 1.0},
                'agents_used': ["conversation_memory"],
                'is_multi_intent': False,
                'issue_context': {
                    "follow_up": True,
                    "last_intent": session.last_intent,
                    "last_order_id": session.last_order_id
                },
                'session_summary': f"Follow-up response for order #{session.last_order_id}"
            }
        
        # STEP 1: COMPLETE REQUEST DETECTION (CRITICAL)
        complete_request = self.nlp.detect_complete_request(message)
        
        print(f"🔍 COMPLETE REQUEST CHECK:")
        print(f"   Order ID: {complete_request['order_id']}")
        print(f"   Issue: {complete_request['issue']}")
        print(f"   Resolution: {complete_request['resolution']}")
        print(f"   Is Complete: {complete_request['is_complete']}")
        print(f"   Is Tracking: {complete_request.get('is_tracking', False)}")
        
        # TRACKING SHORT-CIRCUIT (VERY IMPORTANT)
        if complete_request.get("is_tracking") and complete_request["order_id"]:
            print(f"🚀 TRACKING SHORT-CIRCUIT - Order: {complete_request['order_id']}")
            
            # Get or create order state
            order_state = session.get_or_create_order_state(complete_request["order_id"])
            
            # Set default state if unknown
            if order_state.status == OrderStatus.UNKNOWN:
                # First transition to PROCESSING, then to SHIPPED (following state machine rules)
                session.transition_order_status(complete_request["order_id"], OrderStatus.PROCESSING)
                session.transition_order_status(
                    complete_request["order_id"], 
                    OrderStatus.SHIPPED, 
                    tracking_number=f"TRK{complete_request['order_id']}789",
                    delivery_eta="tomorrow"
                )
                # Refresh order state after update
                order_state = session.get_order_state(complete_request["order_id"])
            
            # Generate canonical tracking response (NO LLM)
            tracking_response = self._get_canonical_tracking_response(complete_request["order_id"], order_state)
            
            # UPDATE CONVERSATION MEMORY AFTER STATE IS SET (CRITICAL FOR FOLLOW-UPS)
            # Get the current status value properly
            current_status = order_state.status.value if hasattr(order_state.status, 'value') else str(order_state.status)
            session.update_conversation_memory(
                intent="tracking",
                order_id=complete_request["order_id"],
                order_state=current_status
            )
            
            # Update session with message
            session.add_message(message, "user")
            session.add_message(tracking_response, "bot")
            
            return {
                'response': tracking_response,
                'intents': ["order_tracking"],
                'entities': {"order_number": [complete_request["order_id"]]},
                'confidence_scores': {"order_tracking": 1.0},
                'agents_used': ["tracking_shortcut"],
                'is_multi_intent': False,
                'issue_context': {
                    "tracking_shortcut": True,
                    "no_resolution_prompt": True
                },
                'session_summary': f"Tracking status for order #{complete_request['order_id']}"
            }
        
        if complete_request["is_complete"]:
            # VALIDATION: Ensure request is truly complete
            if self.deterministic_resolver.validate_complete_request(
                complete_request["order_id"], 
                complete_request["issue"], 
                complete_request["resolution"]
            ):
                print(f"🎯 COMPLETE REQUEST VALIDATED - DETERMINISTIC RESOLUTION")
                
                # STOP routing, STOP questions, SELECT final response, END flow
                result = self.deterministic_resolver.resolve_complete_request(
                    complete_request["order_id"],
                    complete_request["issue"], 
                    complete_request["resolution"],
                    session
                )
                
                # Update session with message
                session.add_message(message, "user")
                session.add_message(result['response'], "bot")
                
                return result
        
        # STEP 2: INCOMPLETE REQUEST HANDLING
        # Check what's missing and ask ONLY for that
        missing_info = []
        
        if not complete_request["order_id"]:
            missing_info.append("order_id")
        if not complete_request["resolution"]:
            missing_info.append("resolution")
        if not complete_request["issue"] and complete_request["resolution"] not in ["cancel"]:
            missing_info.append("issue")
        
        # SPECIAL CASE: Tracking request without order ID
        if (complete_request.get("is_tracking", False) or 
            any(keyword in message.lower() for keyword in ["track", "tracking", "status", "where is", "delivery"])) and not complete_request["order_id"]:
            print(f"🔍 TRACKING REQUEST WITHOUT ORDER ID")
            
            # Clear conversation memory since we need new order ID
            session.clear_conversation_memory()
            
            result = {
                'response': "I can help you track your order. Please provide your order number so I can check the status for you.",
                'intents': ["order_tracking"],
                'entities': {},
                'confidence_scores': {"order_tracking": 1.0},
                'agents_used': ["tracking_request"],
                'is_multi_intent': False,
                'issue_context': {
                    "tracking_request": True,
                    "missing_order_id": True
                },
                'session_summary': "Tracking request - asking for order number"
            }
            
            # Update session with message
            session.add_message(message, "user")
            session.add_message(result['response'], "bot")
            
            return result
        
        # If we have partial information, ask for what's missing
        if missing_info and (complete_request["order_id"] or complete_request["resolution"] or complete_request["issue"]):
            print(f"🔍 INCOMPLETE REQUEST - Missing: {missing_info}")
            
            # Prioritize asking for resolution first, then order_id, then issue
            if "resolution" in missing_info:
                ask_for = "resolution"
            elif "order_id" in missing_info:
                ask_for = "order_id"
            else:
                ask_for = missing_info[0]
            
            result = self.deterministic_resolver.handle_missing_info(ask_for)
            
            # Update session with message
            session.add_message(message, "user")
            session.add_message(result['response'], "bot")
            
            return result
        
        # STEP 3: FALLBACK TO REGULAR NLP (for non-support messages)
        print(f"🔄 FALLBACK TO REGULAR NLP PROCESSING")
        
        # Clear conversation memory for new intents (unless it's tracking)
        if session.last_intent and session.last_intent != "general":
            session.clear_conversation_memory()
        
        # Use regular NLP processing for general conversation
        nlp_result = self.nlp.process_message(message)
        
        intents = nlp_result["intents"]
        entities = nlp_result["entities"]
        confidence_scores = nlp_result["confidence_scores"]
        is_multi_intent = nlp_result["is_multi_intent"]
        issue_context = nlp_result["issue_context"]
        
        # Update session with new information
        session.add_message(message, "user", intents, entities, confidence_scores)
        
        print(f"🧠 NLP Analysis:")
        print(f"   Intents: {intents} (multi-intent: {is_multi_intent})")
        print(f"   Confidence scores: {confidence_scores}")
        print(f"   Entities: {self.nlp.get_entity_summary(entities)}")
        
        # Handle multi-intent scenarios
        if is_multi_intent and len(intents) > 1:
            response_text, agents_used = self._handle_multi_intent_structured(message, intents, confidence_scores, session, issue_context)
        else:
            # Single intent processing
            primary_intent = intents[0] if intents else "general"
            response_text, agents_used = self._handle_single_intent_structured(message, primary_intent, confidence_scores.get(primary_intent, 0.5), session, issue_context)
        
        # Update session with response
        session.add_message(response_text, "bot")
        
        return {
            'response': response_text,
            'intents': intents,
            'entities': entities,
            'confidence_scores': confidence_scores,
            'agents_used': agents_used,
            'is_multi_intent': is_multi_intent,
            'issue_context': issue_context,
            'session_summary': session.get_conversation_summary()
        }
    
    def process(self, message: str, session: SessionMemory) -> str:
        """
        Legacy method for backward compatibility - returns just the response text
        """
        result = self.process_with_context(message, session)
        return result['response']
    
    def _handle_multi_intent_human_like(self, message: str, intents: List[str], confidence_scores: Dict[str, float], session: SessionMemory, issue_context: Dict[str, Any]) -> str:
        """
        Handle messages with multiple intents in a natural, human-like way
        """
        print(f"🔀 Processing multi-intent message: {intents}")
        
        # Get personalization context
        personalization = session.get_personalization_context()
        user_name = personalization["user_name"]
        empathy_level = personalization["empathy_level"]
        
        responses = []
        intent_responses = {}
        
        # Process each intent and collect responses
        for intent in intents:
            if intent == "general":
                continue  # Skip general intent in multi-intent scenarios
            
            confidence = confidence_scores.get(intent, 0.5)
            
            # Get agent context
            agent_context = session.get_context_for_agent(intent)
            agent_context.update({
                "current_message": message,
                "detected_intents": intents,
                "detected_entities": session.last_entities,
                "confidence": confidence,
                "is_multi_intent": True,
                "other_intents": [i for i in intents if i != intent],
                "personalization": personalization,
                "issue_context": issue_context,
                "session_memory": session  # CRITICAL: Pass session memory to agent
            })
            
            # Route to appropriate agent
            if intent in self.agents:
                selected_agent = self.agents[intent]
                response = selected_agent.process(message, agent_context)
                intent_responses[intent] = response
                
                # Update session with agent context
                session.set_agent_context(intent, agent_context)
        
        # Combine responses in a natural, human-like way
        return self._merge_responses_naturally(intent_responses, user_name, empathy_level)
    
    def _handle_multi_intent_structured(self, message: str, intents: List[str], confidence_scores: Dict[str, float], session: SessionMemory, issue_context: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Handle messages with multiple intents and return response with agents used
        """
        print(f"🔀 Processing multi-intent message: {intents}")
        
        # Get personalization context
        personalization = session.get_personalization_context()
        user_name = personalization["user_name"]
        empathy_level = personalization["empathy_level"]
        
        responses = []
        intent_responses = {}
        agents_used = []
        
        # Process each intent and collect responses
        for intent in intents:
            if intent == "general":
                continue  # Skip general intent in multi-intent scenarios
            
            confidence = confidence_scores.get(intent, 0.5)
            
            # Get agent context
            agent_context = session.get_context_for_agent(intent)
            agent_context.update({
                "current_message": message,
                "detected_intents": intents,
                "detected_entities": session.last_entities,
                "confidence": confidence,
                "is_multi_intent": True,
                "other_intents": [i for i in intents if i != intent],
                "personalization": personalization,
                "issue_context": issue_context,
                "session_memory": session  # CRITICAL: Pass session memory to agent
            })
            
            # Route to appropriate agent
            if intent in self.agents:
                selected_agent = self.agents[intent]
                response = selected_agent.process(message, agent_context)
                intent_responses[intent] = response
                agents_used.append(intent)
                
                # Update session with agent context
                session.set_agent_context(intent, agent_context)
        
        # Combine responses in a natural, human-like way
        merged_response = self._merge_responses_naturally(intent_responses, user_name, empathy_level)
        return merged_response, agents_used
    
    def _merge_responses_naturally(self, intent_responses: Dict[str, str], user_name: str, empathy_level: str) -> str:
        """
        Enhanced natural response merging with better flow and context awareness
        """
        if not intent_responses:
            return "I'd be happy to help you with that! Could you provide a bit more detail about what you need?"
        
        # Personalized greeting based on empathy level
        greeting = self._get_contextual_greeting(user_name, empathy_level, len(intent_responses))
        
        if len(intent_responses) == 1:
            # Single response - add appropriate greeting
            intent, response = list(intent_responses.items())[0]
            return f"{greeting}{response}"
        
        elif len(intent_responses) == 2:
            # Two responses - merge with natural transitions
            return self._merge_two_responses(intent_responses, greeting)
        
        else:
            # Multiple responses - create structured but natural flow
            return self._merge_multiple_responses(intent_responses, greeting)
    
    def _get_contextual_greeting(self, user_name: str, empathy_level: str, response_count: int) -> str:
        """Generate contextual greeting based on user state and response complexity"""
        name_prefix = f"{user_name}, " if user_name else ""
        
        if response_count == 1:
            return name_prefix
        
        # Multi-intent greetings
        if empathy_level == "high":
            return f"{name_prefix}I understand you have multiple concerns, and I want to help with all of them. "
        elif empathy_level == "supportive":
            return f"{name_prefix}I can see you need help with several things. Let me address each one: "
        else:
            return f"{name_prefix}I can help you with both of those things. "
    
    def _merge_two_responses(self, intent_responses: Dict[str, str], greeting: str) -> str:
        """Merge two responses with natural transitions"""
        intents = list(intent_responses.keys())
        responses = list(intent_responses.values())
        
        # Create natural transitions based on intent combinations
        if "order" in intents and "support" in intents:
            order_response = intent_responses.get("order", "")
            support_response = intent_responses.get("support", "")
            
            # Clean up responses to remove redundant prefixes
            order_response = self._clean_response_prefix(order_response)
            support_response = self._clean_response_prefix(support_response)
            
            return f"{greeting}Regarding your order: {order_response} As for the support issue: {support_response}"
        
        elif "order" in intents and "product" in intents:
            order_response = self._clean_response_prefix(intent_responses.get("order", ""))
            product_response = self._clean_response_prefix(intent_responses.get("product", ""))
            
            return f"{greeting}About your order: {order_response} And for the product question: {product_response}"
        
        elif "product" in intents and "support" in intents:
            product_response = self._clean_response_prefix(intent_responses.get("product", ""))
            support_response = self._clean_response_prefix(intent_responses.get("support", ""))
            
            return f"{greeting}For the product inquiry: {product_response} Regarding support: {support_response}"
        
        else:
            # Generic two-response merge
            response1 = self._clean_response_prefix(responses[0])
            response2 = self._clean_response_prefix(responses[1])
            return f"{greeting}First, {response1} Also, {response2}"
    
    def _merge_multiple_responses(self, intent_responses: Dict[str, str], greeting: str) -> str:
        """Merge multiple responses with structured flow"""
        response_parts = []
        intent_list = list(intent_responses.items())
        
        for i, (intent, response) in enumerate(intent_list):
            clean_response = self._clean_response_prefix(response)
            
            if i == 0:
                response_parts.append(f"First, regarding {intent}: {clean_response}")
            elif i == len(intent_list) - 1:
                response_parts.append(f"Finally, for {intent}: {clean_response}")
            else:
                response_parts.append(f"Also, for {intent}: {clean_response}")
        
        return f"{greeting}" + " ".join(response_parts)
    
    def _clean_response_prefix(self, response: str) -> str:
        """Clean up response prefixes that are redundant in merged responses"""
        if not response:
            return response
        
        # Remove common prefixes that don't work well in merged responses
        prefixes_to_remove = [
            "For your order: ",
            "For the product question: ",
            "For support: ",
            "Regarding support: ",
            "For the order: ",
            "About the product: "
        ]
        
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):]
                break
        
        # Ensure response starts with appropriate capitalization
        if response and not response[0].isupper():
            response = response[0].upper() + response[1:]
        
        return response
    
    def _handle_single_intent_human_like(self, message: str, intent: str, confidence: float, session: SessionMemory, issue_context: Dict[str, Any]) -> str:
        """
        Handle messages with a single intent in a human-like way
        """
        # Determine routing based on confidence and context
        target_intent = self._determine_routing_with_context(intent, confidence, session)
        
        # Get personalization context
        personalization = session.get_personalization_context()
        
        # Get agent context including session memory
        agent_context = session.get_context_for_agent(target_intent)
        agent_context.update({
            "current_message": message,
            "detected_intent": intent,
            "detected_entities": session.last_entities,
            "confidence": confidence,
            "is_multi_intent": False,
            "personalization": personalization,
            "issue_context": issue_context
        })
        
        # Route to appropriate agent
        selected_agent = self.agents[target_intent]
        response = selected_agent.process(message, agent_context)
        
        # Update session with response and track agent usage
        session.set_agent_context(target_intent, agent_context)
        session.last_agent_used = target_intent  # Track which agent was used
        
        print(f"🤖 Agent {selected_agent.name} responded")
        return response
    
    def _handle_single_intent_structured(self, message: str, intent: str, confidence: float, session: SessionMemory, issue_context: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Handle messages with a single intent and return response with agents used
        """
        # Determine routing based on confidence and context
        target_intent = self._determine_routing_with_context(intent, confidence, session)
        
        # Get personalization context
        personalization = session.get_personalization_context()
        
        # Get agent context including session memory
        agent_context = session.get_context_for_agent(target_intent)
        agent_context.update({
            "current_message": message,
            "detected_intent": intent,
            "detected_entities": session.last_entities,
            "confidence": confidence,
            "is_multi_intent": False,
            "personalization": personalization,
            "issue_context": issue_context,
            "session_memory": session  # CRITICAL: Pass session memory to agent
        })
        
        # Route to appropriate agent
        selected_agent = self.agents[target_intent]
        response = selected_agent.process(message, agent_context)
        
        # Update session with response and track agent usage
        session.set_agent_context(target_intent, agent_context)
        session.last_agent_used = target_intent  # Track which agent was used
        
        print(f"🤖 Agent {selected_agent.name} responded")
        return response, [target_intent]
    
    def _determine_routing_with_context(self, intent: str, confidence: float, session: SessionMemory) -> str:
        """
        Determine which agent to route to based on intent, confidence, session context, and user state
        """
        # Check for unresolved issues that might affect routing
        if session.unresolved_issues:
            open_issues = [issue for issue in session.unresolved_issues if issue["status"] == "open"]
            if open_issues:
                # If user has open issues, be more likely to route to support
                if intent in ["support", "general"] or confidence < 0.6:
                    return "support"
        
        # High confidence - route directly
        if confidence >= 0.7:
            return intent
        
        # Medium confidence - check session context and user state
        elif confidence >= 0.4:
            # If user is frustrated, route to support for better handling
            if session.user_tone == "frustrated" and intent != "general":
                return "support"
            
            # If we have a current intent in session and new intent is similar, continue with current
            if intent in session.current_intents:
                return intent
            
            # If we have relevant entities for this intent, boost confidence
            if intent == "order" and session.get_entity_value("order_number"):
                return "order"
            elif intent == "product" and session.get_entity_value("product_name"):
                return "product"
            elif intent == "support" and (session.get_entity_value("email") or session.get_entity_value("order_number")):
                return "support"
            
            return intent
        
        # Low confidence - route to general for clarification, but consider user state
        else:
            # If user seems frustrated or confused, route to general for empathetic handling
            return "general"
    
    def _resolve_implicit_entities(self, message: str, entities: Dict[str, List[str]], session: SessionMemory) -> Dict[str, List[str]]:
        """
        Resolve implicit entity references from session memory for follow-up queries
        """
        message_lower = message.lower()
        
        # Check if message contains order-related keywords but no explicit order number
        order_keywords = ["status", "cancel", "refund", "track", "tracking", "shipped", "delivery"]
        has_order_keyword = any(keyword in message_lower for keyword in order_keywords)
        has_explicit_order = "order_number" in entities and entities["order_number"]
        
        # PRIORITY ORDER: 1) Explicit order_id 2) active_order_id 3) Ask user
        if not has_explicit_order:
            # Check for wrong item patterns
            wrong_item_patterns = [
                "got", "received", "instead of", "wrong item", "ordered", "but got", 
                "expected", "supposed to get", "different", "not what i ordered"
            ]
            has_wrong_item = any(pattern in message_lower for pattern in wrong_item_patterns)
            
            # Use active order ID for order keywords OR wrong item reports
            if (has_order_keyword or has_wrong_item) and session.get_active_order_id():
                print(f"🔗 Using active order context: {session.get_active_order_id()}")
                entities = entities.copy()  # Don't modify original
                entities["order_number"] = [session.get_active_order_id()]
                
                # Set issue type for wrong item reports
                if has_wrong_item:
                    session.set_active_issue("WRONG_ITEM")
        
        return entities
    
    def _get_canonical_tracking_response(self, order_id: str, order_state) -> str:
        """
        CANONICAL TRACKING RESPONSE (NO LLM)
        Create deterministic responses based on order state
        """
        if not order_state:
            return f"I couldn't find order #{order_id}. Please double-check the order number."
        
        status = order_state.status.value
        
        if status == "processing":
            return f"Order #{order_id} is currently being processed and will ship soon."
        elif status == "shipped":
            eta_text = f" You should receive it by {order_state.delivery_eta}." if order_state.delivery_eta else ""
            return f"Order #{order_id} has been shipped and is on the way.{eta_text}"
        elif status == "delivered":
            return f"Order #{order_id} has been delivered successfully."
        elif status == "cancelled":
            return f"Order #{order_id} has been cancelled."
        elif status == "refunded":
            return f"Order #{order_id} has been refunded."
        else:
            return f"Order #{order_id} has been shipped and is on the way."