# Enhanced Data Access Layer - Integrates all datasets
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

class EnhancedDataAccess:
    """
    Unified data access layer that integrates:
    1. Original customer order dataset (JSON)
    2. Customer support tickets (CSV) 
    3. Realistic customer orders India (Excel)
    """
    
    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent / "datasets"
        
        # Load all datasets
        self.orders_data = self._load_orders_json()
        self.support_tickets = self._load_support_tickets_csv()
        self.india_orders = self._load_india_orders_excel()
        
        print(f"✅ Enhanced Data Access initialized:")
        print(f"   📦 JSON Orders: {len(self.orders_data)} customers")
        print(f"   🎫 Support Tickets: {len(self.support_tickets)} tickets")
        print(f"   🇮🇳 India Orders: {len(self.india_orders)} orders")
    
    def _load_orders_json(self) -> List[Dict]:
        """Load original customer order dataset"""
        try:
            json_path = self.base_path / "customer_order_dataset.json"
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"✅ Loaded JSON orders: {len(data)} customers")
            return data
        except Exception as e:
            print(f"❌ Error loading JSON orders: {e}")
            return []
    
    def _load_support_tickets_csv(self) -> pd.DataFrame:
        """Load customer support tickets CSV"""
        try:
            csv_path = self.base_path / "customer_support_tickets.csv"
            df = pd.read_csv(csv_path)
            print(f"✅ Loaded support tickets: {len(df)} tickets")
            return df
        except Exception as e:
            print(f"❌ Error loading support tickets: {e}")
            return pd.DataFrame()
    
    def _load_india_orders_excel(self) -> pd.DataFrame:
        """Load realistic India orders Excel"""
        try:
            excel_path = self.base_path / "realistic_customer_orders_india.xlsx"
            df = pd.read_excel(excel_path)
            print(f"✅ Loaded India orders: {len(df)} orders")
            return df
        except Exception as e:
            print(f"❌ Error loading India orders: {e}")
            return pd.DataFrame()
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive customer information by customer ID
        Returns customer details with all orders, payment status, and order status
        """
        print(f"🔍 Looking up customer: {customer_id}")
        
        # Search in JSON dataset
        customer_info = self._search_customer_in_json(customer_id)
        if customer_info:
            return customer_info
        
        # Search in other datasets (India orders, support tickets)
        customer_info = self._search_customer_in_other_datasets(customer_id)
        if customer_info:
            return customer_info
        
        print(f"❌ Customer {customer_id} not found in any dataset")
        return None
    
    def _search_customer_in_json(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Search for customer in JSON dataset"""
        for customer in self.orders_data:
            if customer.get("customer_id") == customer_id:
                # Build comprehensive customer profile
                customer_profile = {
                    'customer_id': customer.get('customer_id'),
                    'customer_name': customer.get('name'),
                    'total_orders': len(customer.get('orders', [])),
                    'orders': [],
                    'order_summary': {
                        'total_amount': 0,
                        'delivered': 0,
                        'in_transit': 0,
                        'returned': 0,
                        'pending': 0
                    },
                    'payment_summary': {
                        'cod': 0,
                        'card': 0,
                        'upi': 0,
                        'wallet': 0
                    },
                    'platform_summary': {},
                    'data_source': 'json_dataset'
                }
                
                # Process each order
                for order in customer.get('orders', []):
                    order_details = {
                        'order_id': order.get('order_id'),
                        'product': order.get('product'),
                        'platform': order.get('platform'),
                        'status': order.get('status'),
                        'payment_mode': order.get('payment_mode'),
                        'amount': order.get('amount', 0)
                    }
                    customer_profile['orders'].append(order_details)
                    
                    # Update summaries
                    amount = order.get('amount', 0)
                    customer_profile['order_summary']['total_amount'] += amount
                    
                    # Status summary
                    status = order.get('status', '').lower()
                    if 'delivered' in status:
                        customer_profile['order_summary']['delivered'] += 1
                    elif 'transit' in status or 'shipping' in status:
                        customer_profile['order_summary']['in_transit'] += 1
                    elif 'returned' in status:
                        customer_profile['order_summary']['returned'] += 1
                    else:
                        customer_profile['order_summary']['pending'] += 1
                    
                    # Payment summary
                    payment = order.get('payment_mode', '').lower()
                    if 'cod' in payment:
                        customer_profile['payment_summary']['cod'] += 1
                    elif 'card' in payment:
                        customer_profile['payment_summary']['card'] += 1
                    elif 'upi' in payment:
                        customer_profile['payment_summary']['upi'] += 1
                    elif 'wallet' in payment:
                        customer_profile['payment_summary']['wallet'] += 1
                    
                    # Platform summary
                    platform = order.get('platform', 'Unknown')
                    customer_profile['platform_summary'][platform] = customer_profile['platform_summary'].get(platform, 0) + 1
                
                print(f"✅ Found customer {customer_id}: {customer_profile['customer_name']} with {customer_profile['total_orders']} orders")
                return customer_profile
        
        return None
    
    def _search_customer_in_other_datasets(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Search for customer in India orders and support tickets"""
        # This is a placeholder for searching in other datasets
        # You can extend this to search in India orders Excel and support tickets CSV
        
        # For now, return None - can be enhanced based on other dataset structures
        return None
    
    def get_order_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """
        Enhanced order lookup across all datasets
        Priority: JSON orders -> India orders -> Support tickets
        """
        print(f"🔍 Enhanced lookup for order ID: {order_id}")
        
        # 1. Search in original JSON dataset
        json_order = self._search_json_orders(order_id)
        if json_order:
            json_order['data_source'] = 'json_dataset'
            return json_order
        
        # 2. Search in India orders Excel
        india_order = self._search_india_orders(order_id)
        if india_order:
            india_order['data_source'] = 'india_dataset'
            return india_order
        
        # 3. Search in support tickets (if they have order references)
        ticket_order = self._search_support_tickets(order_id)
        if ticket_order:
            ticket_order['data_source'] = 'support_tickets'
            return ticket_order
        
        print(f"❌ Order {order_id} not found in any dataset")
        return None
    
    def _search_json_orders(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Search in original JSON dataset"""
        for customer in self.orders_data:
            for order in customer.get("orders", []):
                try:
                    order_id_str = str(order.get("order_id", ""))
                    match = re.search(r'(\d+)', order_id_str)
                    if match and int(match.group(1)) == int(order_id):
                        order_with_customer = order.copy()
                        order_with_customer['customer_name'] = customer.get('name')
                        order_with_customer['customer_id'] = customer.get('customer_id')
                        print(f"✅ Found in JSON: {order_with_customer['product']} - {order_with_customer['status']}")
                        return order_with_customer
                except (ValueError, TypeError):
                    continue
        return None
    
    def _search_india_orders(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Search in India orders Excel dataset"""
        if self.india_orders.empty:
            return None
        
        try:
            # Look for order_id in various possible column names
            order_columns = [col for col in self.india_orders.columns if 'order' in col.lower() and 'id' in col.lower()]
            
            for col in order_columns:
                matches = self.india_orders[self.india_orders[col].astype(str).str.contains(str(order_id), na=False)]
                if not matches.empty:
                    order_data = matches.iloc[0].to_dict()
                    # Standardize field names
                    standardized = self._standardize_india_order(order_data)
                    print(f"✅ Found in India dataset: {standardized.get('product', 'Unknown')} - {standardized.get('status', 'Unknown')}")
                    return standardized
        except Exception as e:
            print(f"⚠️ Error searching India orders: {e}")
        
        return None
    
    def _search_support_tickets(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Search in support tickets for order references"""
        if self.support_tickets.empty:
            return None
        
        try:
            # Search in ticket descriptions for order ID mentions
            order_pattern = f"\\b{order_id}\\b"
            matches = self.support_tickets[
                self.support_tickets['Ticket Description'].astype(str).str.contains(order_pattern, na=False, regex=True)
            ]
            
            if not matches.empty:
                ticket_data = matches.iloc[0].to_dict()
                # Convert ticket to order format
                order_data = self._ticket_to_order_format(ticket_data, order_id)
                print(f"✅ Found in support tickets: {order_data.get('product', 'Unknown')} - {order_data.get('status', 'Unknown')}")
                return order_data
        except Exception as e:
            print(f"⚠️ Error searching support tickets: {e}")
        
        return None
    
    def _standardize_india_order(self, order_data: Dict) -> Dict[str, Any]:
        """Standardize India order data to match expected format"""
        standardized = {}
        
        # Map common field variations
        field_mappings = {
            'order_id': ['order_id', 'Order_ID', 'OrderID', 'order_number'],
            'product': ['product', 'Product', 'product_name', 'Product_Name', 'item'],
            'status': ['status', 'Status', 'order_status', 'Order_Status'],
            'amount': ['amount', 'Amount', 'price', 'Price', 'total', 'Total'],
            'platform': ['platform', 'Platform', 'marketplace', 'Marketplace'],
            'customer_name': ['customer_name', 'Customer_Name', 'name', 'Name'],
            'payment_mode': ['payment_mode', 'Payment_Mode', 'payment_method', 'Payment_Method']
        }
        
        for standard_field, possible_fields in field_mappings.items():
            for field in possible_fields:
                if field in order_data and order_data[field] is not None:
                    standardized[standard_field] = order_data[field]
                    break
        
        # Set defaults if not found
        standardized.setdefault('order_id', 'Unknown')
        standardized.setdefault('product', 'Unknown Product')
        standardized.setdefault('status', 'Unknown')
        standardized.setdefault('amount', 0)
        standardized.setdefault('platform', 'India Marketplace')
        
        return standardized
    
    def _ticket_to_order_format(self, ticket_data: Dict, order_id: int) -> Dict[str, Any]:
        """Convert support ticket to order format"""
        return {
            'order_id': str(order_id),
            'product': ticket_data.get('Product Purchased', 'Unknown Product'),
            'status': self._map_ticket_status(ticket_data.get('Ticket Status', 'Unknown')),
            'amount': 0,  # Not available in tickets
            'platform': 'Support System',
            'customer_name': ticket_data.get('Customer Name', 'Unknown'),
            'ticket_type': ticket_data.get('Ticket Type', 'Unknown'),
            'ticket_subject': ticket_data.get('Ticket Subject', 'Unknown'),
            'resolution': ticket_data.get('Resolution', 'Pending')
        }
    
    def _map_ticket_status(self, ticket_status: str) -> str:
        """Map ticket status to order status"""
        status_mapping = {
            'Closed': 'Resolved',
            'Open': 'In Progress',
            'Pending Customer Response': 'Awaiting Response'
        }
        return status_mapping.get(ticket_status, ticket_status)
    
    def get_enhanced_faq_answer(self, user_question: str) -> Optional[str]:
        """
        Enhanced FAQ system using support tickets for better responses
        """
        if self.support_tickets.empty:
            return None
        
        try:
            user_question_lower = user_question.lower()
            
            # Search for similar issues in support tickets
            relevant_tickets = self.support_tickets[
                (self.support_tickets['Ticket Subject'].astype(str).str.lower().str.contains('|'.join(user_question_lower.split()), na=False)) |
                (self.support_tickets['Ticket Description'].astype(str).str.lower().str.contains('|'.join(user_question_lower.split()), na=False))
            ]
            
            if not relevant_tickets.empty:
                # Get tickets with resolutions
                resolved_tickets = relevant_tickets[
                    (relevant_tickets['Ticket Status'] == 'Closed') & 
                    (relevant_tickets['Resolution'].notna()) &
                    (relevant_tickets['Resolution'].astype(str).str.len() > 10)
                ]
                
                if not resolved_tickets.empty:
                    # Return the most relevant resolution
                    best_ticket = resolved_tickets.iloc[0]
                    resolution = best_ticket['Resolution']
                    
                    # Clean up the resolution text
                    if isinstance(resolution, str) and len(resolution) > 20:
                        return f"Based on similar cases: {resolution}"
            
            # Fallback to ticket type patterns
            return self._get_pattern_based_response(user_question_lower)
            
        except Exception as e:
            print(f"⚠️ Error in enhanced FAQ: {e}")
            return None
    
    def _get_pattern_based_response(self, question: str) -> Optional[str]:
        """Generate response based on ticket patterns"""
        if self.support_tickets.empty:
            return None
        
        # Common issue patterns
        if any(word in question for word in ['refund', 'money back']):
            refund_tickets = self.support_tickets[self.support_tickets['Ticket Type'] == 'Refund request']
            if not refund_tickets.empty:
                return "For refund requests, please provide your order details. Refunds typically take 3-5 business days to process."
        
        elif any(word in question for word in ['technical', 'not working', 'issue']):
            tech_tickets = self.support_tickets[self.support_tickets['Ticket Type'] == 'Technical issue']
            if not tech_tickets.empty:
                return "For technical issues, please try restarting the device and checking for updates. If the problem persists, contact our technical support team."
        
        elif any(word in question for word in ['billing', 'payment', 'charged']):
            billing_tickets = self.support_tickets[self.support_tickets['Ticket Type'] == 'Billing inquiry']
            if not billing_tickets.empty:
                return "For billing inquiries, please check your payment method and contact our billing department if you notice any discrepancies."
        
        return None
    
    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get comprehensive dataset statistics"""
        return {
            'json_orders': {
                'customers': len(self.orders_data),
                'total_orders': sum(len(customer.get('orders', [])) for customer in self.orders_data)
            },
            'support_tickets': {
                'total_tickets': len(self.support_tickets),
                'ticket_types': self.support_tickets['Ticket Type'].value_counts().to_dict() if not self.support_tickets.empty else {},
                'ticket_status': self.support_tickets['Ticket Status'].value_counts().to_dict() if not self.support_tickets.empty else {}
            },
            'india_orders': {
                'total_orders': len(self.india_orders),
                'columns': list(self.india_orders.columns) if not self.india_orders.empty else []
            }
        }

# Create global instance for backward compatibility
enhanced_data_access = EnhancedDataAccess()

# Backward compatible functions
def get_order_by_id(order_id: int):
    """Backward compatible order lookup function"""
    return enhanced_data_access.get_order_by_id(order_id)

def get_customer_by_id(customer_id: str):
    """Get comprehensive customer information by customer ID"""
    return enhanced_data_access.get_customer_by_id(customer_id)

def get_enhanced_faq_answer(user_question: str):
    """Enhanced FAQ function using all datasets"""
    return enhanced_data_access.get_enhanced_faq_answer(user_question)