import re
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta

class NLPProcessor:
    def __init__(self):
        self.intent_patterns = {
            # SPLIT: INFORMATIONAL ORDER INTENTS (NO RESOLUTION)
            "order_tracking": {
                "keywords": ["track", "tracking", "status", "where is", "when will", "delivery", "shipment", "shipped", "delivered", "eta", "arrive"],
                "patterns": [
                    r"track.*order",
                    r"order.*status",
                    r"where.*is.*order",
                    r"delivery.*status",
                    r"shipment.*info",
                    r"when.*will.*arrive",
                    r"tracking.*number",
                    r"order.*arrive"
                ],
                "weight": 1.0
            },
            # SPLIT: RESOLUTION ORDER INTENTS (PROBLEMS)
            "order_resolution": {
                "keywords": ["cancel", "refund", "return", "replacement", "wrong", "damaged", "broken", "delayed", "late", "problem", "issue"],
                "patterns": [
                    r"cancel.*order",
                    r"refund.*order",
                    r"return.*order",
                    r"wrong.*item",
                    r"damaged.*order",
                    r"delayed.*delivery",
                    r"late.*package",
                    r"problem.*order"
                ],
                "weight": 1.0
            },
            "product": {
                "keywords": ["product", "item", "buy", "purchase", "price", "cost", "available", "stock", "specs", "features", "compare"],
                "patterns": [
                    r"how much.*cost",
                    r"price.*of",
                    r"buy.*product",
                    r"product.*info",
                    r"in.*stock",
                    r"available.*product"
                ],
                "weight": 1.0
            },
            "support": {
                "keywords": ["refund", "return", "account", "billing", "payment", "technical", "problem", "issue", "help", "support", "login", "password", "reset", "exchange", "wrong", "incorrect", "damaged", "broken"],
                "patterns": [
                    r"need.*help",
                    r"technical.*problem",
                    r"account.*issue",
                    r"billing.*question",
                    r"refund.*request",
                    r"return.*item",
                    r"want.*refund",
                    r"money.*back",
                    r"wrong.*item",
                    r"got.*wrong",
                    r"received.*wrong"
                ],
                "weight": 1.0
            },
            "general": {
                "keywords": ["hello", "hi", "hey", "thanks", "thank you", "goodbye", "bye", "what", "how", "why", "when", "internet", "wifi"],
                "patterns": [
                    r"^(hi|hello|hey)",
                    r"thank.*you",
                    r"good.*(morning|afternoon|evening)",
                    r"how.*are.*you",
                    r"internet.*not.*working",
                    r"wifi.*problem"
                ],
                "weight": 0.8
            }
        }
        
        self.entity_patterns = {
            "order_number": [
                r"#(\d{3,8})",  # #12345 - only digits after #
                r"order\s*#?\s*(\d{3,8})",  # order 12345 or order #12345 - only digits
                r"\border\s+(\d{3,8})\b",  # order 12345 - only digits, word boundary
                r"\b([A-Z]{2,3}\d{4,6})\b"  # ABC1234 format - letters followed by digits
            ],
            "product_name": [
                r"product\s+([A-Za-z0-9\s]+?)(?:\s|$)",
                r"item\s+([A-Za-z0-9\s]+?)(?:\s|$)",
                r"([A-Za-z]+\s*\d+[A-Za-z]*)",  # iPhone14, MacBook Pro
                r"(apples?|bananas?|oranges?|grapes?|strawberr(?:y|ies)|laptop|phone|tablet|headphones?|shoes?|shirt|dress|book|chair|table)",  # Common products
            ],
            "ordered_product": [
                r"ordered\s+([A-Za-z\s]+?)(?:\s|$)",
                r"bought\s+([A-Za-z\s]+?)(?:\s|$)",
                r"purchased\s+([A-Za-z\s]+?)(?:\s|$)",
                r"supposed\s+to\s+get\s+([A-Za-z\s]+?)(?:\s|$)",
                r"expected\s+([A-Za-z\s]+?)(?:\s|$)",
                r"wanted\s+([A-Za-z\s]+?)(?:\s|$)",
            ],
            "received_product": [
                r"got\s+([A-Za-z\s]+?)(?:\s|$)",
                r"received\s+([A-Za-z\s]+?)(?:\s|$)",
                r"delivered\s+([A-Za-z\s]+?)(?:\s|$)",
                r"sent\s+me\s+([A-Za-z\s]+?)(?:\s|$)",
                r"came\s+with\s+([A-Za-z\s]+?)(?:\s|$)",
                r"instead\s+of\s+.*got\s+([A-Za-z\s]+?)(?:\s|$)",
            ],
            "delivery_issue": [
                r"(delayed|late|missing|lost|damaged|broken|wrong|incorrect)",
                r"(not.*delivered|never.*arrived|still.*waiting)",
            ],
            "date": [
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",  # 12/25/2023
                r"(today|tomorrow|yesterday)",
                r"(\d{1,2}\s+(days?|weeks?|months?)\s+ago)",
                r"(next\s+week|last\s+week|this\s+week)"
            ],
            "email": [
                r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
            ],
            "phone": [
                r"(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})"
            ],
            "issue_type": [
                r"(refund|return|exchange|replacement|cancel|billing|account|technical|login|password)"
            ]
        }
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a message and return multiple intents, entities, and confidence scores
        """
        message_lower = message.lower().strip()
        
        # Extract entities first
        entities = self.extract_entities(message)
        
        # Calculate intent scores for all intents
        intent_scores = self.calculate_intent_scores(message_lower)
        
        # Determine multiple intents and their confidence scores
        detected_intents, confidence_scores = self.determine_multiple_intents(intent_scores, entities)
        
        # Detect specific issue patterns
        issue_context = self.detect_issue_context(message_lower, entities)
        
        return {
            "intents": detected_intents,
            "entities": entities,
            "confidence_scores": confidence_scores,
            "raw_scores": intent_scores,
            "is_multi_intent": len(detected_intents) > 1,
            "issue_context": issue_context
        }
    
    def extract_entities(self, message: str) -> Dict[str, List[str]]:
        """
        Extract entities from the message using regex patterns
        """
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, message, re.IGNORECASE)
                if found:
                    # Flatten nested matches and clean up
                    for match in found:
                        if isinstance(match, tuple):
                            match = match[0] if match[0] else match[1] if len(match) > 1 else ""
                        if match and match.strip():
                            clean_match = match.strip().lower()
                            # Filter out common words that aren't actually entities
                            if entity_type in ["product_name", "ordered_product", "received_product"]:
                                if len(clean_match) > 2 and clean_match not in ["the", "and", "but", "got", "item", "product"]:
                                    matches.append(clean_match)
                            else:
                                matches.append(match.strip())
            
            if matches:
                entities[entity_type] = list(set(matches))  # Remove duplicates
        
        return entities
    
    def detect_issue_context(self, message: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Detect specific issue contexts like wrong item delivery with enhanced pattern matching
        """
        issue_context = {}
        message_lower = message.lower()
        
        # Enhanced wrong item detection with more sophisticated patterns
        wrong_item_patterns = [
            r"ordered\s+([A-Za-z\s]+?)\s+but\s+got\s+([A-Za-z\s]+?)(?:\s|$|\.)",
            r"ordered\s+([A-Za-z\s]+?)\s+received\s+([A-Za-z\s]+?)(?:\s|$|\.)",
            r"expected\s+([A-Za-z\s]+?)\s+but\s+got\s+([A-Za-z\s]+?)(?:\s|$|\.)",
            r"wanted\s+([A-Za-z\s]+?)\s+instead\s+got\s+([A-Za-z\s]+?)(?:\s|$|\.)",
            r"supposed\s+to\s+get\s+([A-Za-z\s]+?)\s+but\s+received\s+([A-Za-z\s]+?)(?:\s|$|\.)",
            r"([A-Za-z\s]+?)\s+instead\s+of\s+([A-Za-z\s]+?)(?:\s|$|\.)",
            r"got\s+wrong\s+([A-Za-z\s]+?)(?:\s|$|\.)",
            r"wrong\s+([A-Za-z\s]+?)\s+delivered(?:\s|$|\.)",
            r"incorrect\s+([A-Za-z\s]+?)\s+sent(?:\s|$|\.)",
            # Handle "I got wrong apples" type cases
            r"got\s+wrong\s+([A-Za-z\s]+?)(?:\s|$|\.)",
            r"received\s+wrong\s+([A-Za-z\s]+?)(?:\s|$|\.)",
            r"delivered\s+wrong\s+([A-Za-z\s]+?)(?:\s|$|\.)",
            # Handle substitution cases like "red apples instead of green apples"
            r"([A-Za-z\s]+?)\s+instead\s+of\s+([A-Za-z\s]+?)(?:\s|$|\.)",
            r"sent\s+([A-Za-z\s]+?)\s+not\s+([A-Za-z\s]+?)(?:\s|$|\.)",
        ]
        
        wrong_item_detected = False
        for pattern in wrong_item_patterns:
            match = re.search(pattern, message_lower)
            if match:
                groups = match.groups()
                
                if len(groups) == 2:
                    # Two-item patterns (ordered X but got Y)
                    item1, item2 = groups
                    item1, item2 = item1.strip(), item2.strip()
                    
                    # Determine which is ordered vs received based on pattern
                    if "instead of" in pattern:
                        ordered_item, received_item = item2, item1  # Reversed for "instead of"
                    else:
                        ordered_item, received_item = item1, item2
                    
                elif len(groups) == 1:
                    # Single-item patterns (got wrong X)
                    received_item = groups[0].strip()
                    ordered_item = "correct item"  # Generic placeholder
                else:
                    continue
                
                # Filter out common words and validate
                if self._is_valid_product_name(received_item) and (len(groups) == 1 or self._is_valid_product_name(ordered_item)):
                    issue_context["wrong_item"] = {
                        "ordered": ordered_item,
                        "received": received_item,
                        "type": "wrong_item_delivery",
                        "confidence": "high",
                        "pattern_matched": pattern,
                        "detection_method": "pattern_matching"
                    }
                    wrong_item_detected = True
                    break
        
        # Fallback to entity-based detection if pattern matching didn't work
        if not wrong_item_detected and any(word in message_lower for word in ["wrong", "incorrect", "got", "received", "but", "instead"]):
            ordered = entities.get("ordered_product", [])
            received = entities.get("received_product", [])
            
            if ordered and received:
                issue_context["wrong_item"] = {
                    "ordered": ordered[0],
                    "received": received[0],
                    "type": "wrong_item_delivery",
                    "confidence": "medium"
                }
                wrong_item_detected = True
            elif "wrong" in message_lower or "incorrect" in message_lower:
                issue_context["wrong_item"] = {
                    "type": "wrong_item_general",
                    "confidence": "low"
                }
        
        # Detect delivery issues
        delivery_issues = entities.get("delivery_issue", [])
        if delivery_issues:
            issue_context["delivery_problem"] = {
                "type": delivery_issues[0],
                "severity": "high" if delivery_issues[0] in ["missing", "lost", "damaged"] else "medium"
            }
        
        # Detect refund/return requests with urgency
        if any(word in message_lower for word in ["refund", "return", "money back"]):
            urgency_indicators = ["urgent", "asap", "immediately", "right now", "frustrated", "angry"]
            urgency = "high" if any(word in message_lower for word in urgency_indicators) else "normal"
            
            issue_context["refund_request"] = {
                "type": "refund" if "refund" in message_lower else "return",
                "urgency": urgency,
                "reason": "wrong_item" if wrong_item_detected else "general"
            }
        
        # Detect customer satisfaction indicators
        satisfaction_indicators = {
            "very_negative": ["terrible", "awful", "worst", "hate", "disgusted"],
            "negative": ["bad", "poor", "disappointed", "frustrated", "unhappy"],
            "neutral": ["okay", "fine", "alright"],
            "positive": ["good", "nice", "satisfied", "happy"],
            "very_positive": ["excellent", "amazing", "perfect", "love", "fantastic"]
        }
        
        for level, words in satisfaction_indicators.items():
            if any(word in message_lower for word in words):
                issue_context["satisfaction_level"] = level
                break
        
        return issue_context
    
    def _is_valid_product_name(self, product: str) -> bool:
        """Validate if a string is likely a valid product name"""
        if not product or len(product.strip()) < 2:
            return False
        
        product = product.strip().lower()
        
        # Filter out common words that aren't products
        invalid_words = {
            "the", "and", "but", "got", "item", "product", "thing", "stuff", 
            "it", "that", "this", "what", "when", "where", "how", "why",
            "instead", "received", "delivered", "sent", "ordered", "bought"
        }
        
        # Check if it's just a common word
        if product in invalid_words:
            return False
        
        # Check if it contains at least one letter
        if not any(c.isalpha() for c in product):
            return False
        
        # Check if it's not too long (likely not a product name)
        if len(product) > 50:
            return False
        
        return True
    
    def calculate_intent_scores(self, message: str) -> Dict[str, float]:
        """
        Calculate scores for each intent based on keywords and patterns
        """
        scores = {}
        message_words = message.split()
        message_length = len(message_words)
        
        for intent, config in self.intent_patterns.items():
            score = 0.0
            
            # Keyword matching with position weighting
            keyword_matches = 0
            for i, word in enumerate(message_words):
                if word in config["keywords"]:
                    keyword_matches += 1
                    # Give higher weight to keywords at the beginning
                    position_weight = 1.0 - (i / len(message_words)) * 0.3
                    score += config["weight"] * position_weight
            
            # Pattern matching
            pattern_matches = 0
            for pattern in config["patterns"]:
                if re.search(pattern, message, re.IGNORECASE):
                    pattern_matches += 1
                    score += config["weight"] * 1.5  # Patterns get higher weight
            
            # Normalize by message length to handle short vs long messages
            if message_length > 0:
                score = score / max(1, message_length / 5)  # Normalize by message length
            
            scores[intent] = max(0.0, min(1.0, score))  # Clamp between 0 and 1
        
        return scores
    
    def determine_multiple_intents(self, scores: Dict[str, float], entities: Dict[str, List[str]]) -> Tuple[List[str], Dict[str, float]]:
        """
        Determine multiple intents and their confidence scores
        """
        # Entity-based intent boosting
        entity_boosts = {
            "order_number": "order",
            "product_name": "product",
            "ordered_product": "support",  # Usually indicates an issue
            "received_product": "support",  # Usually indicates an issue
            "delivery_issue": "order",
            "email": "support",
            "phone": "support",
            "issue_type": "support"
        }
        
        # Apply entity boosts
        boosted_scores = scores.copy()
        for entity_type, entity_values in entities.items():
            if entity_type in entity_boosts and entity_values:
                target_intent = entity_boosts[entity_type]
                boosted_scores[target_intent] = min(1.0, boosted_scores.get(target_intent, 0) + 0.3)
        
        # Find intents above threshold
        threshold = 0.3
        high_confidence_threshold = 0.6
        
        detected_intents = []
        confidence_scores = {}
        
        # Sort intents by score
        sorted_intents = sorted(boosted_scores.items(), key=lambda x: x[1], reverse=True)
        
        for intent, score in sorted_intents:
            if score >= threshold:
                detected_intents.append(intent)
                confidence_scores[intent] = score
                
                # For multi-intent detection, only include additional intents if they're reasonably high
                if len(detected_intents) > 1 and score < high_confidence_threshold:
                    # Only keep if the score is within 0.4 of the highest score
                    if score < sorted_intents[0][1] - 0.4:
                        detected_intents.pop()
                        del confidence_scores[intent]
                        break
        
        # If no intents detected or all are very low confidence, default to general
        if not detected_intents or max(confidence_scores.values()) < 0.2:
            detected_intents = ["general"]
            confidence_scores = {"general": 0.3}
        
        return detected_intents, confidence_scores
    
    def get_entity_summary(self, entities: Dict[str, List[str]]) -> str:
        """
        Create a human-readable summary of extracted entities
        """
        if not entities:
            return "No specific entities detected."
        
        summary_parts = []
        for entity_type, values in entities.items():
            if values:
                entity_name = entity_type.replace("_", " ").title()
                if len(values) == 1:
                    summary_parts.append(f"{entity_name}: {values[0]}")
                else:
                    summary_parts.append(f"{entity_name}: {', '.join(values)}")
        
        return "; ".join(summary_parts)
    
    def detect_complete_request(self, message: str) -> Dict[str, Any]:
        """
        CRITICAL: Detect if message contains COMPLETE support request.
        COMPLETE = order_id + issue + resolution ALL present.
        If COMPLETE = true: STOP routing, STOP questions, SELECT final response.
        
        TRACKING SHORT-CIRCUIT: If intent == TRACKING and order_id exists:
        - DO NOT ask refund/replacement/cancel
        - DO NOT route to SupportAgent  
        - DIRECTLY return tracking response
        """
        message_lower = message.lower()
        
        # TRACKING SHORT-CIRCUIT LOGIC (VERY IMPORTANT)
        tracking_keywords = ["track", "tracking", "status", "where is", "when will", "delivery", "shipment", "shipped", "delivered", "eta", "arrive"]
        is_tracking_request = any(keyword in message_lower for keyword in tracking_keywords)
        
        if is_tracking_request:
            # Extract order_id for tracking
            order_id = None
            order_patterns = [
                r"order\s*#?\s*([A-Z0-9]{3,8})",  # order 12345 or order #ABC123
                r"#([A-Z0-9]{3,8})",  # #12345
                r"\b(\d{4,8})\b",  # 4-8 digit numbers as standalone words
                r"\b([A-Z]{2,3}\d{4,6})\b"  # ABC1234 format
            ]
            
            for pattern in order_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    potential_id = match.group(1)
                    # Validate it's not a common word and is actually numeric or alphanumeric ID
                    if (potential_id.lower() not in ["is", "my", "the", "and", "but", "got", "want", "need", "status", "arrive", "delivery", "order", "track", "where", "when", "will"] and
                        (potential_id.isdigit() or (len(potential_id) >= 3 and any(c.isdigit() for c in potential_id)))):
                        order_id = potential_id
                        break
            
            if order_id:
                # TRACKING SHORT-CIRCUIT: Return tracking-specific response
                return {
                    "order_id": order_id,
                    "issue": "tracking",  # Special tracking issue type
                    "resolution": "tracking",  # Special tracking resolution type
                    "is_complete": True,  # SHORT-CIRCUIT: Complete for tracking
                    "is_tracking": True  # Flag for tracking flow
                }
        
        # Only process if message contains clear support indicators (NOT tracking)
        support_indicators = ["refund", "replacement", "cancel", "wrong", "damaged", "delayed", "broken", "return"]
        if not any(indicator in message_lower for indicator in support_indicators):
            return {
                "order_id": None,
                "issue": None,
                "resolution": None,
                "is_complete": False,
                "is_tracking": False
            }
        
        # 1. Extract order_id via regex patterns
        order_id = None
        order_patterns = [
            r"order\s*#?\s*([A-Z0-9]{3,8})",  # order 12345 or order #ABC123
            r"#([A-Z0-9]{3,8})",  # #12345
            r"\b(\d{4,8})\b",  # 4-8 digit numbers as standalone words
            r"\b([A-Z]{2,3}\d{4,6})\b"  # ABC1234 format
        ]
        
        for pattern in order_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                potential_id = match.group(1)
                # Validate it's not a common word and is actually numeric or alphanumeric ID
                if (potential_id.lower() not in ["is", "my", "the", "and", "but", "got", "want", "need", "status", "arrive", "delivery", "order", "track", "where", "when", "will"] and
                    (potential_id.isdigit() or (len(potential_id) >= 3 and any(c.isdigit() for c in potential_id)))):
                    order_id = potential_id
                    break
        
        # 2. Detect issue type - SIMPLIFIED (wrong item / delivery / refund / cancel)
        issue = None
        
        # Wrong item detection
        if any(keyword in message_lower for keyword in ["got wrong", "received wrong", "wrong item", "instead of", "but got", "sent wrong", "incorrect"]):
            issue = "wrong_item"
        
        # Delivery issue detection  
        elif any(keyword in message_lower for keyword in ["delayed", "late", "not arrived", "hasn't arrived", "delivery", "shipping"]):
            issue = "delivery"
        
        # Damaged item detection
        elif any(keyword in message_lower for keyword in ["damaged", "broken", "defective", "not working"]):
            issue = "damaged"
        
        # 3. Detect resolution intent - EXPLICIT ONLY
        resolution = None
        
        # Refund detection
        if any(keyword in message_lower for keyword in ["refund", "money back", "want refund", "need refund"]):
            resolution = "refund"
        
        # Replacement detection
        elif any(keyword in message_lower for keyword in ["replacement", "replace", "new one", "send another"]):
            resolution = "replacement"
        
        # Cancellation detection
        elif any(keyword in message_lower for keyword in ["cancel", "cancellation", "cancel order"]):
            resolution = "cancel"
        
        # 4. CRITICAL: Determine if request is COMPLETE
        # For refund/replacement: need order_id + resolution (issue can be inferred)
        # For cancel: need order_id + resolution only
        if resolution in ["refund", "replacement"]:
            # If no explicit issue but refund/replacement requested, infer general issue
            if not issue and order_id and resolution:
                issue = "general"
            is_complete = bool(order_id and issue and resolution)
        elif resolution == "cancel":
            is_complete = bool(order_id and resolution)
            issue = "cancel"  # Cancel is both issue and resolution
        else:
            is_complete = False
        
        return {
            "order_id": order_id,
            "issue": issue,
            "resolution": resolution,
            "is_complete": is_complete,
            "is_tracking": False
        }
    
    def detect_conjunctions(self, message: str) -> List[str]:
        """
        Detect conjunction words that indicate multiple intents
        """
        conjunctions = ["and", "also", "plus", "additionally", "furthermore", "moreover", "besides"]
        found_conjunctions = []
        
        message_lower = message.lower()
        for conj in conjunctions:
            if f" {conj} " in message_lower:
                found_conjunctions.append(conj)
        
        return found_conjunctions