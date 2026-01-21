#!/usr/bin/env python3
"""
Test the enhanced dataset integration
"""

import sys
import os

def test_basic_imports():
    """Test if basic imports work"""
    print("🧪 Testing basic imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import openpyxl
        print("✅ openpyxl imported successfully")
    except ImportError as e:
        print(f"❌ openpyxl import failed: {e}")
        return False
    
    return True

def test_dataset_files():
    """Test if dataset files exist"""
    print("\n🧪 Testing dataset files...")
    
    datasets = [
        "datasets/customer_order_dataset.json",
        "datasets/customer_support_tickets.csv", 
        "datasets/realistic_customer_orders_india.xlsx"
    ]
    
    all_exist = True
    for dataset in datasets:
        if os.path.exists(dataset):
            print(f"✅ {dataset} exists")
        else:
            print(f"❌ {dataset} missing")
            all_exist = False
    
    return all_exist

def test_enhanced_data_access():
    """Test the enhanced data access layer"""
    print("\n🧪 Testing enhanced data access...")
    
    try:
        from data.enhanced_data_access import enhanced_data_access, get_order_by_id
        print("✅ Enhanced data access imported successfully")
        
        # Test order lookup
        test_order = get_order_by_id(54582)
        if test_order:
            print(f"✅ Order lookup works: {test_order.get('product', 'Unknown')} - {test_order.get('status', 'Unknown')}")
            print(f"   Data source: {test_order.get('data_source', 'Unknown')}")
        else:
            print("⚠️ Order 54582 not found (this might be expected)")
        
        # Test stats
        stats = enhanced_data_access.get_dataset_stats()
        print(f"✅ Dataset stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced data access failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 TESTING ENHANCED DATASET INTEGRATION")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Dataset Files", test_dataset_files),
        ("Enhanced Data Access", test_enhanced_data_access)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("🏁 TEST RESULTS")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED - INTEGRATION READY!")
    else:
        print("\n⚠️ SOME TESTS FAILED - CHECK DEPENDENCIES")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)