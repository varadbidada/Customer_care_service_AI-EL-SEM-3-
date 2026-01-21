#!/usr/bin/env python3
"""
Setup script for the refactored data-driven chatbot system
"""

import os
import shutil
import sys

def setup_refactored_system():
    """Setup the refactored system"""
    print("🚀 Setting up refactored data-driven chatbot system...")
    
    # Step 1: Backup original app.py
    if os.path.exists('app.py'):
        print("📋 Backing up original app.py...")
        shutil.copy('app.py', 'app_original_backup.py')
        print("✅ Original app.py backed up as app_original_backup.py")
    
    # Step 2: Replace with refactored version
    if os.path.exists('app_refactored.py'):
        print("🔄 Replacing app.py with refactored version...")
        shutil.copy('app_refactored.py', 'app.py')
        print("✅ app.py replaced with refactored version")
    else:
        print("❌ app_refactored.py not found!")
        return False
    
    # Step 3: Verify datasets exist
    required_datasets = [
        'datasets/customer_order_dataset.json',
        'datasets/ai_customer_support_data.json'
    ]
    
    print("📊 Checking datasets...")
    for dataset in required_datasets:
        if os.path.exists(dataset):
            print(f"✅ {dataset} found")
        else:
            print(f"❌ {dataset} missing!")
            return False
    
    # Step 4: Check .gitignore
    if os.path.exists('.gitignore'):
        print("✅ .gitignore found")
    else:
        print("⚠️ .gitignore missing - create one to exclude .venv/ and __pycache__/")
    
    # Step 5: Display next steps
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run tests: python test_data_driven_system.py")
    print("3. Start application: python app.py")
    print("4. Access at: http://localhost:5000")
    print("\n📊 The system is now fully data-driven and deterministic!")
    
    return True

def validate_system():
    """Quick validation of the system"""
    print("\n🧪 Running quick validation...")
    
    try:
        # Test imports
        sys.path.append('.')
        from app import ConversationRouter, get_order_by_id, get_faq_answer
        
        print("✅ Core imports successful")
        
        # Test dataset functions
        test_order = get_order_by_id("ORD54582")
        if test_order:
            print(f"✅ Order lookup: Found {test_order['product']}")
        
        test_faq = get_faq_answer("How do I track my order?")
        if test_faq:
            print("✅ FAQ lookup: Found answer")
        
        # Test router
        router = ConversationRouter()
        print("✅ Conversation router initialized")
        
        print("🎉 System validation successful!")
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 REFACTORED CHATBOT SETUP")
    print("=" * 40)
    
    if setup_refactored_system():
        if validate_system():
            print("\n✅ Setup and validation complete!")
            print("🚀 Your chatbot is ready to run!")
        else:
            print("\n⚠️ Setup complete but validation failed")
            print("Check dependencies and try running: python app.py")
    else:
        print("\n❌ Setup failed!")
        print("Check that all required files are present")