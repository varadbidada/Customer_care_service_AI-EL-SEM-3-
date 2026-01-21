#!/usr/bin/env python3
"""
Test the complete dataset integration with OrderAgent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.order_data_access import get_order_by_id, get_order_data_access
from agents.order_agent import OrderAgent

def test_data_access_layer():
    """Test the data access layer functionality"""
    print("🧪 TESTING DATA ACCESS LAYER")
    print("=" * 50)
    
    # Get data access instance
    data_access = get_order_data_access()
    stats = data_access.get_dataset_stats()
    
    print(f"📊 Dataset loaded: {stats['loaded']}")
    print(f"📦 Total orders: {stats['total_orders']}")
    
    if stats['loaded']:
        print(f"🏪 Platforms: {', '.join(stats['platforms'])}")
        print(f"📈 Order ID range: {stats['order_id_range']['min']} - {stats['order_id_range']['max']}")
        print(f"📊 Status counts: {stats['status_counts']}")
    
    return stats['loaded']

def test_order_lookup():
    """Test order lookup functionality"""
    print("\n🔍 TESTING ORDER LOOKUP")
    print("=" * 50)
    
    # Test with a known order ID from the dataset
    test_order_ids = [54582, 63640, 90495, 99999]  # Last one should not exist
    
    results = []
    
    for order_id in test_order_ids:
        print(f"\n--- Testing order ID: {order_id} ---")
        order_details = get_order_by_id(order_id)
        
        if order_details:
            print(f"✅ Found: {order_details['product']} - {order_details['status']}")
            print(f"   Customer: {order_details['customer_name']}")
            print(f"   Platform: {order_details['platform']}")
            print(f"   Amount: ₹{order_details['amount']:,}")
            results.append(True)
        else:
            print(f"❌ Order not found")
            results.append(False)
    
    # Expect first 3 to be found, last one not found
    expected = [True, True, True, False]
    success = results == expected
    
    print(f"\n📊 Lookup test: {'✅ PASSED' if success else '❌ FAILED'}")
    return success

def test_order_agent_integration():
    """Test OrderAgent with real dataset integration"""
    print("\n🤖 TESTING ORDER AGENT INTEGRATION")
    print("=" * 50)
    
    # Create OrderAgent instance
    order_agent = OrderAgent()
    
    # Mock context for testing
    class MockSessionMemory:
        def __init__(self):
            self.active_order_id = None
        
        def get_active_order_id(self):
            return self.active_order_id
        
        def update_conversation_memory(self, **kwargs):
            pass
    
    mock_context = {
        "session_memory": MockSessionMemory(),
        "detected_entities": {},
        "persistent_entities": {},
        "personalization": {},
        "conversation_history": []
    }
    
    # Test cases
    test_cases = [
        ("54582", "Valid order ID - should return real order details"),
        ("track order 63640", "Tracking request with valid order"),
        ("99999", "Invalid order ID - should return 'order not found'"),
        ("status of ORD90495", "Status request with ORD prefix"),
    ]
    
    success_count = 0
    
    for message, description in test_cases:
        print(f"\n--- {description} ---")
        print(f"Input: '{message}'")
        
        try:
            # Add order number to detected entities for this test
            if any(char.isdigit() for char in message):
                import re
                match = re.search(r'(\d+)', message)
                if match:
                    order_num = match.group(1)
                    mock_context["detected_entities"] = {"order_number": [order_num]}
            
            response = order_agent.process(message, mock_context)
            print(f"Response: {response[:100]}...")
            
            # Validate response characteristics
            if "99999" in message:
                # Should contain "not found" or similar
                if "not found" in response.lower() or "couldn't find" in response.lower():
                    print("✅ Correctly returned 'order not found'")
                    success_count += 1
                else:
                    print("❌ Should have returned 'order not found'")
            else:
                # Should contain real product information or order details
                if any(keyword in response.lower() for keyword in ["groceries", "shoes", "burger", "product", "status", "delivered", "transit"]):
                    print("✅ Contains real order information")
                    success_count += 1
                else:
                    print("❌ Should contain real order information")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📊 Agent integration test: {success_count}/{len(test_cases)} passed")
    return success_count == len(test_cases)

def test_no_placeholder_responses():
    """Verify no placeholder responses are used"""
    print("\n🚫 TESTING NO PLACEHOLDER RESPONSES")
    print("=" * 50)
    
    order_agent = OrderAgent()
    
    # Mock context
    class MockSessionMemory:
        def __init__(self):
            self.active_order_id = None
        
        def get_active_order_id(self):
            return self.active_order_id
        
        def update_conversation_memory(self, **kwargs):
            pass
    
    mock_context = {
        "session_memory": MockSessionMemory(),
        "detected_entities": {"order_number": ["54582"]},  # Valid order
        "persistent_entities": {},
        "personalization": {},
        "conversation_history": []
    }
    
    response = order_agent.process("track my order 54582", mock_context)
    
    # Check for placeholder text
    placeholder_keywords = [
        "placeholder", "example", "sample", "test order", 
        "mock", "dummy", "fake", "simulated"
    ]
    
    has_placeholders = any(keyword in response.lower() for keyword in placeholder_keywords)
    
    print(f"Response: {response}")
    print(f"Contains placeholders: {'❌ YES' if has_placeholders else '✅ NO'}")
    
    return not has_placeholders

def main():
    """Run all integration tests"""
    print("🧪 DATASET INTEGRATION VALIDATION")
    print("Testing complete integration of order dataset with runtime logic")
    print("=" * 70)
    
    # Run all tests
    tests = [
        ("Data Access Layer", test_data_access_layer),
        ("Order Lookup", test_order_lookup),
        ("OrderAgent Integration", test_order_agent_integration),
        ("No Placeholder Responses", test_no_placeholder_responses),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("🏁 INTEGRATION TEST RESULTS")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    all_passed = passed == len(results)
    
    print(f"\n📊 Overall: {passed}/{len(results)} tests passed")
    
    if all_passed:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Data access layer working")
        print("✅ Real dataset lookups functional")
        print("✅ OrderAgent using real data")
        print("✅ No placeholder responses")
        print("✅ 'Order not found' only when lookup fails")
    else:
        print("\n❌ SOME TESTS FAILED - Integration incomplete")
    
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)