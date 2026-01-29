#!/usr/bin/env python3
"""
Test the authentication flow with cookies.
"""

import requests

def test_auth_flow():
    """Test login and dashboard access with cookies."""
    
    base_url = "http://72.60.222.154:8000"
    
    print("🧪 Testing Authentication Flow")
    print("=" * 40)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Test 1: Login
    print("1. Testing login...")
    login_data = {
        "email": "ranjanprakash4u@gmail.com",
        "password": "your-password-here"  # Replace with actual password
    }
    
    try:
        response = session.post(f"{base_url}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Login successful!")
            print(f"   Token received: {result['access_token'][:20]}...")
            print(f"   Cookies set: {list(session.cookies.keys())}")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    # Test 2: Access dashboard with cookie
    print("\n2. Testing dashboard access with cookie...")
    try:
        response = session.get(f"{base_url}/dashboard")
        
        if response.status_code == 200:
            print("   ✅ Dashboard accessible with cookie!")
            print(f"   Response length: {len(response.text)} characters")
        else:
            print(f"   ❌ Dashboard access failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Dashboard access error: {e}")
        return False
    
    # Test 3: Logout
    print("\n3. Testing logout...")
    try:
        response = session.post(f"{base_url}/api/auth/logout")
        
        if response.status_code == 200:
            print("   ✅ Logout successful!")
            print(f"   Cookies after logout: {list(session.cookies.keys())}")
        else:
            print(f"   ❌ Logout failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Logout error: {e}")
    
    # Test 4: Try dashboard after logout
    print("\n4. Testing dashboard access after logout...")
    try:
        response = session.get(f"{base_url}/dashboard")
        
        if response.status_code == 401 or response.status_code == 403:
            print("   ✅ Dashboard properly protected after logout!")
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Dashboard test error: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Authentication flow test complete!")
    
    return True

if __name__ == "__main__":
    test_auth_flow()