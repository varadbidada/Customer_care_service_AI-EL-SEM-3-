#!/usr/bin/env python3
"""
Test script to verify chat widget functionality
"""

import requests
import time
from bs4 import BeautifulSoup

def test_chat_widget_elements():
    """Test that all chat widget elements are present"""
    try:
        print("🧪 Testing chat widget elements...")
        
        # Test e-commerce page
        response = requests.get("http://localhost:5000/ecommerce")
        print(f"✅ E-commerce page status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for critical chat elements
            critical_elements = [
                ("Chat button", soup.find('div', id='chatButton')),
                ("Chat panel", soup.find('div', id='chatPanel')),
                ("Chat messages", soup.find('div', id='chatMessages')),
                ("Chat input", soup.find('textarea', id='chatInput')),
                ("Send button", soup.find('button', id='chatSendBtn')),
                ("Chat header", soup.find('div', class_='chat-header')),
                ("Quick actions", soup.find('div', id='quickActions')),
            ]
            
            # Check for drag/resize elements
            optional_elements = [
                ("Drag handle", soup.find('div', id='chatDragHandle')),
                ("Reset button", soup.find('button', id='chatResetSizeBtn')),
                ("Resize handles", soup.find_all('div', class_='resize-handle')),
            ]
            
            print("\n🔍 Critical element checks:")
            all_critical_passed = True
            for name, element in critical_elements:
                if element:
                    print(f"  ✅ {name}: Found")
                else:
                    print(f"  ❌ {name}: Missing")
                    all_critical_passed = False
            
            print("\n🔍 Optional element checks:")
            for name, element in optional_elements:
                if element:
                    if isinstance(element, list):
                        print(f"  ✅ {name}: Found ({len(element)} elements)")
                    else:
                        print(f"  ✅ {name}: Found")
                else:
                    print(f"  ⚠️ {name}: Missing (optional)")
            
            # Check JavaScript files
            js_files = [
                soup.find('script', src=lambda x: x and 'ecommerce.js' in x),
                soup.find('script', src=lambda x: x and 'socket.io' in x),
            ]
            
            print("\n🔍 JavaScript file checks:")
            for i, js_file in enumerate(js_files):
                file_names = ['ecommerce.js', 'socket.io']
                if js_file:
                    print(f"  ✅ {file_names[i]}: Loaded")
                else:
                    print(f"  ❌ {file_names[i]}: Missing")
            
            if all_critical_passed:
                print("\n🎉 All critical elements found!")
                print("💡 If chat still doesn't open, check browser console for JavaScript errors")
                return True
            else:
                print("\n⚠️ Some critical elements are missing")
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
    """Test that JavaScript files are accessible and valid"""
    try:
        print("\n🧪 Testing JavaScript files...")
        
        js_files = [
            ("/static/ecommerce.js", "EcommerceChatWidget"),
            ("/static/chat.js", "KiroChat"),
        ]
        
        for file_path, expected_class in js_files:
            response = requests.get(f"http://localhost:5000{file_path}")
            if response.status_code == 200:
                content = response.text
                if expected_class in content:
                    print(f"  ✅ {file_path}: Available and contains {expected_class}")
                else:
                    print(f"  ⚠️ {file_path}: Available but missing {expected_class}")
            else:
                print(f"  ❌ {file_path}: Status {response.status_code}")
                
    except Exception as e:
        print(f"❌ JavaScript file test failed: {e}")

def provide_troubleshooting_tips():
    """Provide troubleshooting tips for common issues"""
    print("\n🔧 TROUBLESHOOTING TIPS:")
    print("=" * 50)
    print("1. 🌐 Open browser and go to: http://localhost:5000/ecommerce")
    print("2. 🔍 Press F12 to open Developer Tools")
    print("3. 📋 Check Console tab for JavaScript errors")
    print("4. 🎯 Look for the orange chat button in bottom-right corner")
    print("5. 🖱️ Click the chat button to test opening")
    print("\n📝 Common Issues:")
    print("   • If button doesn't appear: Check CSS loading")
    print("   • If button doesn't click: Check JavaScript errors")
    print("   • If panel doesn't open: Check element IDs match")
    print("   • If drag/resize fails: Feature will gracefully degrade")
    print("\n🔄 Quick Fixes:")
    print("   • Refresh the page (Ctrl+F5)")
    print("   • Clear browser cache")
    print("   • Check server is running on port 5000")
    print("   • Restart Flask server if needed")

if __name__ == "__main__":
    print("🚀 Starting Chat Widget Functionality Tests")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    success = test_chat_widget_elements()
    test_static_files()
    provide_troubleshooting_tips()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Chat widget elements are properly loaded!")
        print("🎯 If chat still doesn't work, check browser console for errors.")
    else:
        print("❌ Chat widget has missing elements.")
        print("🔧 Please check the troubleshooting tips above.")