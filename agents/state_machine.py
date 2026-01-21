from enum import Enum
from typing import Dict, Set, Optional
from datetime import datetime

class OrderStatus(Enum):
    UNKNOWN = "unknown"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    REPLACEMENT_SENT = "replacement_sent"

class ConversationFlow(Enum):
    GREETING = "greeting"
    ORDER_INQUIRY = "order_inquiry"
    TRACKING_REQUEST = "tracking_request"
    CANCELLATION_REQUEST = "cancellation_request"
    DELIVERY_ISSUE = "delivery_issue"
    REFUND_REQUEST = "refund_request"

class StateMachine:
    ORDER_TRANSITIONS: Dict[OrderStatus, Set[OrderStatus]] = {
        OrderStatus.UNKNOWN: {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
        OrderStatus.PROCESSING: {OrderStatus.SHIPPED, OrderStatus.CANCELLED, OrderStatus.REPLACEMENT_SENT},
        OrderStatus.SHIPPED: {OrderStatus.DELIVERED, OrderStatus.REFUNDED, OrderStatus.REPLACEMENT_SENT},
        OrderStatus.DELIVERED: {OrderStatus.REFUNDED, OrderStatus.REPLACEMENT_SENT},
        OrderStatus.CANCELLED: set(),
        OrderStatus.REFUNDED: set(),
        OrderStatus.REPLACEMENT_SENT: {OrderStatus.DELIVERED}
    }
    
    CONVERSATION_TRANSITIONS: Dict[ConversationFlow, Set[ConversationFlow]] = {
        ConversationFlow.GREETING: {ConversationFlow.ORDER_INQUIRY, ConversationFlow.TRACKING_REQUEST, 
                                   ConversationFlow.CANCELLATION_REQUEST, ConversationFlow.DELIVERY_ISSUE},
        ConversationFlow.ORDER_INQUIRY: {ConversationFlow.TRACKING_REQUEST, ConversationFlow.CANCELLATION_REQUEST},
        ConversationFlow.TRACKING_REQUEST: {ConversationFlow.DELIVERY_ISSUE, ConversationFlow.CANCELLATION_REQUEST},
        ConversationFlow.CANCELLATION_REQUEST: {ConversationFlow.REFUND_REQUEST},
        ConversationFlow.DELIVERY_ISSUE: {ConversationFlow.REFUND_REQUEST, ConversationFlow.CANCELLATION_REQUEST},
        ConversationFlow.REFUND_REQUEST: set()
    }
    
    @classmethod
    def can_transition_order(cls, from_status: OrderStatus, to_status: OrderStatus) -> bool:
        return to_status in cls.ORDER_TRANSITIONS.get(from_status, set())
    
    @classmethod
    def can_transition_conversation(cls, from_flow: ConversationFlow, to_flow: ConversationFlow) -> bool:
        return to_flow in cls.CONVERSATION_TRANSITIONS.get(from_flow, set())
    
    @classmethod
    def is_order_cancellable(cls, status: OrderStatus) -> bool:
        return status in {OrderStatus.UNKNOWN, OrderStatus.PROCESSING}
    
    @classmethod
    def is_order_shipped(cls, status: OrderStatus) -> bool:
        return status in {OrderStatus.SHIPPED, OrderStatus.DELIVERED}
    
    @classmethod
    def validate_order_state(cls, status: OrderStatus, shipped: bool, cancellable: bool) -> bool:
        if cls.is_order_shipped(status) and cancellable:
            return False
        if not cls.is_order_shipped(status) and shipped:
            return False
        if cls.is_order_cancellable(status) != cancellable:
            return False
        return True

class OrderState:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.status = OrderStatus.UNKNOWN
        self.delivery_eta = None
        self.tracking_number = None
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
    
    @property
    def shipped(self) -> bool:
        return StateMachine.is_order_shipped(self.status)
    
    @property
    def cancellable(self) -> bool:
        return StateMachine.is_order_cancellable(self.status)
    
    def transition_to(self, new_status: OrderStatus) -> bool:
        if StateMachine.can_transition_order(self.status, new_status):
            self.status = new_status
            self.last_updated = datetime.now()
            return True
        return False
    
    def update_tracking(self, tracking_number: str, delivery_eta: str = None):
        self.tracking_number = tracking_number
        if delivery_eta:
            self.delivery_eta = delivery_eta
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "order_id": self.order_id,
            "status": self.status.value,
            "shipped": self.shipped,
            "cancellable": self.cancellable,
            "delivery_eta": self.delivery_eta,
            "tracking_number": self.tracking_number,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'OrderState':
        order_state = cls(data["order_id"])
        order_state.status = OrderStatus(data.get("status", "unknown"))
        order_state.delivery_eta = data.get("delivery_eta")
        order_state.tracking_number = data.get("tracking_number")
        order_state.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        order_state.last_updated = datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        return order_state

class ConversationState:
    def __init__(self):
        self.flow = ConversationFlow.GREETING
        self.order_context = {}
        self.last_updated = datetime.now()
    
    def transition_to(self, new_flow: ConversationFlow) -> bool:
        if StateMachine.can_transition_conversation(self.flow, new_flow):
            self.flow = new_flow
            self.last_updated = datetime.now()
            return True
        return False
    
    def add_context(self, key: str, value: str):
        self.order_context[key] = value
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "flow": self.flow.value,
            "order_context": self.order_context,
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationState':
        conv_state = cls()
        conv_state.flow = ConversationFlow(data.get("flow", "greeting"))
        conv_state.order_context = data.get("order_context", {})
        conv_state.last_updated = datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        return conv_state