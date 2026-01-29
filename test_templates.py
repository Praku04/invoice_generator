#!/usr/bin/env python3
"""
Test all template routes to ensure they're working.
"""

import requests

def test_all_templates():
    """Test all template routes."""
    
    base_url = "http://72.60.222.154:8090"  # Frontend port
    
    print("🧪 Testing All Template Routes")
    print("=" * 50)
    
    # Public routes (should work without authentication)
    public_routes = [
        "/",
        "/login", 
        "/register",
        "/pricing",
        "/about",
        "/contact",
        "/terms",
        "/privacy"
    ]
    
    print("1. Testing public routes...")
    for route in public_routes:
        try:
            response = requests.get(f"{base_url}{route}", timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {route} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {route} - Error: {e}")
    
    # Protected routes (will require authentication)
    protected_routes = [
        "/dashboard",
        "/invoices", 
        "/invoices/create",
        "/settings",
        "/subscription"
    ]
    
    print("\n2. Testing protected routes (expect 401/403 without auth)...")
    for route in protected_routes:
        try:
            response = requests.get(f"{base_url}{route}", timeout=10)
            # These should redirect to login or show 401/403
            status = "✅" if response.status_code in [200, 302, 401, 403] else "❌"
            print(f"   {status} {route} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {route} - Error: {e}")
    
    print("\n" + "=" * 50)
    print("Template test complete!")
    print("\nIf you see mostly ✅ marks, templates are working correctly.")
    print("❌ marks indicate missing templates or server errors.")
    
    return True

if __name__ == "__main__":
    test_all_templates()