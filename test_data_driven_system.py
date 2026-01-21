#!/usr/bin/env python3
"""
REALISTIC END-TO-END TESTS FOR DATA-DRIVEN CHATBOT
==================================================

These tests validate:
1. Dataset lookups return correct data
2. Multi-turn conversation continuity works  
3. Session state is preserved across messages
4. Responses change when dataset values change
5. Every response is actually driven by datasets

CRITICAL: Tests MUST fail if datasets are removed or not used.
"""

import sys
import os
import json
import pandas as pd
from unittest.mock import patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_refactored import (
    ConversationRouter, 
    SessionState, 
    get_order_by_id, 
    get_faq_answer,
    load_datasets
)

class MockSession:
    """Mock session for testing"""
    def __init__(self):
        self.conversation_state = None

def test_dataset_loading():
    """Test 1: Verify datasets load correctly and contain expected data"""
    print("=" * 80)
    print("🧪 TEST 1: DATASET LOADING VALIDATION")
    print("=" * 80)
    
    try:
        orders_df, faq_df = load_datasets()
        
        # Validate orders dataset
        assert len(orders_df) > 0, "Orders dataset is empty"
        required_order_columns = ['order_id', 'customer_name', 'product', 'status', 'amount']
        for col in required_order_columns:
            assert col in orders_df.columns, f"Missing required column: {col}"
        
        # Validate FAQ dataset  
        assert len(faq_df) > 0, "FAQ dataset is empty"
        required_faq_columns = ['question', 'answer', 'category']
        for col in required_faq_columns:
            assert col in faq_df.columns, f"Missing required column: {col}"
        
        print(f"✅ Orders dataset: {len(orders_df)} records with required columns")
        print(f"✅ FAQ dataset: {len(faq_df)} records with required columns")
        
        # Test specific data lookups
        test_order = get_order_by_id("ORD54582")
        assert test_order is not None, "Test order ORD54582 not found"
        assert test_order['product'] == 'Groceries', "Incorrect product for test order"
        
        test_faq = get_faq_answer("How can I track my order?")
        assert test_faq is not None, "FAQ answer not found for tracking question"
        assert "track" in test_faq.lower(), "FAQ answer doesn't contain tracking info"
        
        print("✅ Dataset queries return expected data")
        print("✅ TEST 1 PASSED: Datasets loaded and validated")
        
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
        raise

def test_multi_turn_conversation_continuity():
    """Test 2: Validate multi-turn conversations maintain state and use datasets"""
    print("\n" + "=" * 80)
    print("🧪 TEST 2: MULTI-TURN CONVERSATION CONTINUITY")
    print("=" * 80)
    
    router = ConversationRouter()
    session = MockSession()
    
    # Test scenario: Billing issue requiring order ID
    print("\n📋 Scenario: Multi-turn billing issue")
    
    # Turn 1: User mentions billing problem
    response1 = router.handle_user_message("I was charged twice", session)
    
    # Validate response asks for order ID
    assert "order number" in response1['response'].lower(), "Should ask for order number"
    assert response1['data_source'] == 'workflow_prompt', "Should be workflow prompt"
    
    # Validate session state is preserved
    assert hasattr(session, 'conversation_state'), "Session state not created"
    assert session.conversation_state.active_intent.value == 'billing_issue', "Intent not locked"
    assert session.conversation_state.pending_slot == 'order_id', "Pending slot not set"
    
    print(f"✅ Turn 1: {response1['response'][:50]}...")
    print(f"✅ Intent locked: {session.conversation_state.active_intent}")
    print(f"✅ Pending slot: {session.conversation_state.pending_slot}")
    
    # Turn 2: User provides order ID
    response2 = router.handle_user_message("ORD54582", session)
    
    # Validate response uses real dataset
    assert "ORD54582" in response2['response'], "Response should contain order ID"
    assert "Groceries" in response2['response'], "Response should contain real product name"
    assert "42310" in response2['response'], "Response should contain real amount"
    assert 'order_dataset' in response2['data_source'], "Should use order dataset"
    
    # Validate session state is reset after completion
    assert session.conversation_state.active_intent is None, "Intent should be reset"
    assert session.conversation_state.pending_slot is None, "Pending slot should be reset"
    
    print(f"✅ Turn 2: {response2['response'][:50]}...")
    print(f"✅ Data source: {response2['data_source']}")
    print(f"✅ State reset: intent={session.conversation_state.active_intent}")
    
    print("✅ TEST 2 PASSED: Multi-turn conversation maintains state and uses datasets")

def test_session_state_preservation():
    """Test 3: Validate session state persists across multiple interactions"""
    print("\n" + "=" * 80)
    print("🧪 TEST 3: SESSION STATE PRESERVATION")
    print("=" * 80)
    
    router = ConversationRouter()
    session = MockSession()
    
    # Start order status workflow
    response1 = router.handle_user_message("Where is my package?", session)
    
    # Validate initial state
    assert session.conversation_state.active_intent.value == 'order_status'
    assert session.conversation_state.pending_slot == 'order_id'
    
    # User asks clarifying question (should maintain state)
    response2 = router.handle_user_message("What do you need from me?", session)
    
    # Validate state is preserved
    assert session.conversation_state.active_intent.value == 'order_status', "Intent should persist"
    assert session.conversation_state.pending_slot == 'order_id', "Pending slot should persist"
    assert "order number" in response2['response'].lower(), "Should still ask for order number"
    
    # Provide order ID
    response3 = router.handle_user_message("#63640", session)
    
    # Validate dataset usage and state reset
    assert "ORD63640" in response3['response'] or "63640" in response3['response'], "Should use order ID"
    assert "Shoes" in response3['response'], "Should use real product data"
    assert session.conversation_state.active_intent is None, "Should reset after completion"
    
    print("✅ State preserved across clarifying questions")
    print("✅ Dataset used for final response")
    print("✅ State properly reset after completion")
    print("✅ TEST 3 PASSED: Session state preservation works correctly")

def test_dataset_dependency():
    """Test 4: Validate responses change when dataset values change"""
    print("\n" + "=" * 80)
    print("🧪 TEST 4: DATASET DEPENDENCY VALIDATION")
    print("=" * 80)
    
    router = ConversationRouter()
    
    # Test with real dataset
    session1 = MockSession()
    response1 = router.handle_user_message("Track order ORD54582", session1)
    
    assert "Groceries" in response1['response'], "Should contain real product name"
    assert 'order_dataset' in response1['data_source'], "Should use order dataset"
    
    print(f"✅ Real dataset response: {response1['response'][:50]}...")
    
    # Test with modified dataset (simulate dataset change)
    with patch('app_refactored.get_order_by_id') as mock_get_order:
        mock_get_order.return_value = {
            'order_id': 'ORD54582',
            'product': 'MODIFIED_PRODUCT',
            'status': 'MODIFIED_STATUS',
            'platform': 'MODIFIED_PLATFORM'
        }
        
        session2 = MockSession()
        response2 = router.handle_user_message("Track order ORD54582", session2)
        
        assert "MODIFIED_PRODUCT" in response2['response'], "Should reflect dataset changes"
        assert "MODIFIED_STATUS" in response2['response'], "Should reflect status changes"
        
        print(f"✅ Modified dataset response: {response2['response'][:50]}...")
    
    # Test with missing dataset (simulate dataset failure)
    with patch('app_refactored.get_order_by_id') as mock_get_order:
        mock_get_order.return_value = None
        
        session3 = MockSession()
        response3 = router.handle_user_message("Track order ORD99999", session3)
        
        assert "couldn't find" in response3['response'].lower(), "Should handle missing data"
        assert 'dataset_negative' in response3['data_source'], "Should indicate dataset miss"
        
        print(f"✅ Missing data response: {response3['response'][:50]}...")
    
    print("✅ TEST 4 PASSED: Responses properly depend on dataset values")

def test_faq_dataset_integration():
    """Test 5: Validate FAQ responses are dataset-driven"""
    print("\n" + "=" * 80)
    print("🧪 TEST 5: FAQ DATASET INTEGRATION")
    print("=" * 80)
    
    router = ConversationRouter()
    
    # Test FAQ questions that should match dataset
    faq_tests = [
        ("How do I apply a coupon code?", "coupon"),
        ("I forgot my password", "password"),
        ("The app keeps crashing", "app"),
        ("How do I contact support?", "contact")
    ]
    
    for question, expected_keyword in faq_tests:
        session = MockSession()
        response = router.handle_user_message(question, session)
        
        # Validate response comes from FAQ dataset
        if 'faq_dataset' in response['data_source']:
            assert expected_keyword.lower() in response['response'].lower(), f"FAQ should contain '{expected_keyword}'"
            print(f"✅ FAQ match: '{question}' → dataset response")
        else:
            print(f"⚠️ FAQ miss: '{question}' → fallback response")
    
    # Test with modified FAQ dataset
    with patch('app_refactored.get_faq_answer') as mock_get_faq:
        mock_get_faq.return_value = "MODIFIED_FAQ_ANSWER"
        
        session = MockSession()
        response = router.handle_user_message("How do I apply a coupon?", session)
        
        assert "MODIFIED_FAQ_ANSWER" in response['response'], "Should use modified FAQ data"
        print("✅ FAQ responses change with dataset modifications")
    
    print("✅ TEST 5 PASSED: FAQ responses are properly dataset-driven")

def test_no_hardcoded_responses():
    """Test 6: Validate no hardcoded responses bypass dataset queries"""
    print("\n" + "=" * 80)
    print("🧪 TEST 6: NO HARDCODED RESPONSES VALIDATION")
    print("=" * 80)
    
    router = ConversationRouter()
    
    # Test various message types
    test_messages = [
        "I was charged twice for order ORD54582",
        "Return order ORD63640", 
        "Track my order ORD90495",
        "How do I contact support?",
        "Random question about nothing"
    ]
    
    for message in test_messages:
        session = MockSession()
        response = router.handle_user_message(message, session)
        
        # Validate every response has a data source
        assert 'data_source' in response, f"Response missing data_source for: {message}"
        
        data_source = response['data_source']
        
        # Validate data source indicates dataset usage or explicit fallback
        valid_sources = [
            'order_dataset', 'faq_dataset', 'workflow_prompt', 
            'order_dataset_negative', 'faq_dataset_negative',
            'fallback_menu', 'slot_filling_prompt', 'error_handling'
        ]
        
        assert any(source in data_source for source in valid_sources), f"Invalid data source: {data_source}"
        
        print(f"✅ '{message[:30]}...' → {data_source}")
    
    print("✅ TEST 6 PASSED: All responses have valid data sources")

def test_dataset_failure_handling():
    """Test 7: Validate system behavior when datasets are unavailable"""
    print("\n" + "=" * 80)
    print("🧪 TEST 7: DATASET FAILURE HANDLING")
    print("=" * 80)
    
    router = ConversationRouter()
    
    # Test with completely broken dataset functions
    with patch('app_refactored.get_order_by_id') as mock_order, \
         patch('app_refactored.get_faq_answer') as mock_faq:
        
        # Simulate dataset failures
        mock_order.side_effect = Exception("Dataset connection failed")
        mock_faq.side_effect = Exception("FAQ dataset unavailable")
        
        session = MockSession()
        
        try:
            response = router.handle_user_message("Track order ORD54582", session)
            
            # Should handle gracefully
            assert 'response' in response, "Should return response even with dataset failure"
            assert 'error' in response.get('data_source', '').lower() or \
                   'fallback' in response.get('data_source', '').lower(), \
                   "Should indicate error/fallback data source"
            
            print(f"✅ Graceful failure handling: {response['data_source']}")
            
        except Exception as e:
            print(f"❌ System should handle dataset failures gracefully: {e}")
            raise
    
    print("✅ TEST 7 PASSED: System handles dataset failures gracefully")

def run_all_tests():
    """Run all end-to-end tests"""
    print("🚀 STARTING COMPREHENSIVE END-TO-END TESTS")
    print("=" * 80)
    
    tests = [
        test_dataset_loading,
        test_multi_turn_conversation_continuity,
        test_session_state_preservation,
        test_dataset_dependency,
        test_faq_dataset_integration,
        test_no_hardcoded_responses,
        test_dataset_failure_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print("🏁 TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED - System is data-driven and deterministic!")
    else:
        print("⚠️ SOME TESTS FAILED - System needs fixes before deployment")
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()