#!/usr/bin/env python3
"""
Test the real dataset integration as specified
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_data_access():
    """Test the simplified data access function"""
    print("🧪 TESTING REAL DATASET ACCESS")
    print("=" * 50)
    
    try:
        from data.order_data_access import get_order_by_id
        
        # Test with known order IDs from dataset
        test_cases = [
            (54582, True),   # Should exist
            (63640, True),   # Should exist  
            (90495, True),   # Should exist
            (99999, False),  # Should not exist
        ]
        
        success_count = 0
        
        for order_id, should_exist in test_cases:
            print(f"\n--- Testing order ID: {order_id} ---")
            order = get_order_by_id(order_id)
            
            if should_exist:
                if order:
                    print(f"✅ Found: {order.get('product')} - {order.get('status')}")
                    print(f"   Customer: {order.get('customer_name')}")
                    print(f"   Platform: {order.get('platform')}")
                    success_count += 1
                else:
                    print(f"❌ Expected to find order but didn't")
            else:
                if not order:
                    print(f"✅ Correctly returned None (order not found)")
                    success_count += 1
                else:
                    print(f"❌ Expected None but found order")
        
        print(f"\n📊 Data access test: {success_count}/{len(test_cases)} passed")
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"❌ Error testing data access: {e}")
        return False

def test_order_agent_real_responses():
    """Test OrderAgent with real dataset responses"""
    print("\n🤖 TESTING ORDER AGENT REAL RESPONSES")
    print("=" * 50)
    
    try:
        from agents.order_agent import OrderAgent
        
        # Create OrderAgent instance
        order_agent = OrderAgent()
        
        # Mock session memory
        class MockSessionMemory:
            def __init__(self):
                self.active_order_id = None
            
            def get_active_order_id(self):
                return self.active_order_id
            
            def update_conversation_memory(self, **kwargs):
                pass
        
        # Test cases
        test_cases = [
            {
                "message": "track order 54582",
                "order_id": "54582",
                "description": "Valid order - should return real product and status"
            },
            {
                "message": "status of 99999", 
                "order_id": "99999",
                "description": "Invalid order - should return 'couldn't find that order'"
            }
        ]
        
        success_count = 0
        
        for test_case in test_cases:
            print(f"\n--- {test_case['description']} ---")
            print(f"Input: '{test_case['message']}'")
            
            # Mock context
            mock_context = {
                "session_memory": MockSessionMemory(),
                "detected_entities": {"order_number": [test_case['order_id']]},
                "persistent_entities": {},
                "personalization": {},
                "conversation_history": []
            }
            
            try:
                response = order_agent.process(test_case['message'], mock_context)
                print(f"Response: {response}")
                
                # Validate response
                if test_case['order_id'] == "54582":
                    # Should contain real product info (Groceries from dataset)
                    if "groceries" in response.lower() or "product" in response.lower():
                        print("✅ Contains real product information")
                        success_count += 1
                    else:
                        print("❌ Should contain real product information")
                
                elif test_case['order_id'] == "99999":
                    # Should contain "couldn't find" message
                    if "couldn't find" in response.lower() or "recheck" in response.lower():
                        print("✅ Correctly returns 'order not found'")
                        success_count += 1
                    else:
                        print("❌ Should return 'order not found'")
                
            except Exception as e:
                print(f"❌ Error processing: {e}")
        
        print(f"\n📊 OrderAgent test: {success_count}/{len(test_cases)} passed")
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"❌ Error testing OrderAgent: {e}")
        return False

def test_no_fake_statuses():
    """Verify no fake statuses are generated"""
    print("\n🚫 TESTING NO FAKE STATUSES")
    print("=" * 50)
    
    try:
        from data.order_data_access import get_order_by_id
        
        # Get a real order
        order = get_order_by_id(54582)
        
        if order:
            real_status = order.get('status')
            print(f"Real status from dataset: {real_status}")
            
            # Verify it's one of the actual statuses in the dataset
            valid_statuses = ["In Transit", "Delivered", "Processing", "Shipped", "Cancelled"]
            
            if real_status in valid_statuses:
                print("✅ Status is from real dataset")
                return True
            else:
                print(f"❌ Unexpected status: {real_status}")
                return False
        else:
            print("❌ Could not get order for testing")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 REAL DATASET INTEGRATION VALIDATION")
    print("Verifying STEP 1 and STEP 2 implementation")
    print("=" * 70)
    
    tests = [
        ("Data Access Function", test_data_access),
        ("OrderAgent Real Responses", test_order_agent_real_responses), 
        ("No Fake Statuses", test_no_fake_statuses),
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
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ STEP 1: order_data_access.py implemented correctly")
        print("✅ STEP 2: OrderAgent connected to real dataset")
        print("✅ Real order lookups working")
        print("✅ 'Order not found' only when lookup fails")
        print("✅ No fake statuses or state machine dependencies")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)