#!/usr/bin/env python3
"""
Test script to verify e-commerce page integration
"""

import requests
import time
from bs4 import BeautifulSoup

def test_ecommerce_page():
    """Test that the e-commerce page loads correctly"""
    try:
        print("🧪 Testing e-commerce page integration...")
        
        # Test main page
        response = requests.get("http://localhost:5000/")
        print(f"✅ Main page status: {response.status_code}")
        
        # Test e-commerce page
        response = requests.get("http://localhost:5000/ecommerce")
        print(f"✅ E-commerce page status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for key elements
            checks = [
                ("Shop at RVCE title", soup.find('title')),
                ("Header", soup.find('header', class_='header')),
                ("Navigation", soup.find('nav', class_='navigation')),
                ("Hero banner", soup.find('section', class_='hero-banner')),
                ("Categories section", soup.find('section', class_='categories-section')),
                ("Products section", soup.find('section', class_='products-section')),
                ("Chat widget", soup.find('div', class_='chat-widget')),
                ("Chat button", soup.find('div', id='chatButton')),
                ("Chat panel", soup.find('div', id='chatPanel')),
                ("E-commerce CSS", soup.find('link', href=lambda x: x and 'ecommerce_simple.css' in x)),
                ("E-commerce JS", soup.find('script', src=lambda x: x and 'ecommerce_simple.js' in x)),
                ("Socket.IO", soup.find('script', src=lambda x: x and 'socket.io' in x)),
            ]
            
            print("\n🔍 Element checks:")
            all_passed = True
            for name, element in checks:
                if element:
                    print(f"  ✅ {name}: Found")
                else:
                    print(f"  ❌ {name}: Missing")
                    all_passed = False
            
            if all_passed:
                print("\n🎉 All integration tests passed!")
                print("🌐 E-commerce page available at: http://localhost:5000/ecommerce")
                return True
            else:
                print("\n⚠️ Some elements are missing")
                return False
        else:
            print(f"❌ E-commerce page failed to load: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask app is running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_static_files():
    """Test that static files are accessible"""
    try:
        print("\n🧪 Testing static files...")
        
        static_files = [
            "/static/ecommerce_simple.css",
            "/static/ecommerce_simple.js",
            "/static/chat.js"
        ]
        
        for file_path in static_files:
            response = requests.get(f"http://localhost:5000{file_path}")
            if response.status_code == 200:
                print(f"  ✅ {file_path}: Available")
            else:
                print(f"  ❌ {file_path}: Status {response.status_code}")
                
    except Exception as e:
        print(f"❌ Static file test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting E-commerce Integration Tests")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    success = test_ecommerce_page()
    test_static_files()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Integration complete! E-commerce page with chatbot widget is ready.")
        print("🎯 Next steps:")
        print("   1. Visit http://localhost:5000/ecommerce")
        print("   2. Click the chat button in bottom-right corner")
        print("   3. Test chatbot functionality")
        print("   4. Verify responsive design on mobile")
    else:
        print("❌ Integration has issues. Please check the logs above.")