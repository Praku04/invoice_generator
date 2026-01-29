#!/usr/bin/env python3
"""
Test the date calculation fix.
"""

import requests

def test_date_calculation():
    """Test if the date calculation is now correct."""
    
    base_url = "http://72.60.222.154:8000"
    
    print("🧪 Testing Date Calculation Fix")
    print("=" * 40)
    
    # Test 1: Check subscription usage
    print("1. Checking subscription usage...")
    try:
        # You'll need to be logged in for this to work
        headers = {
            'Authorization': 'Bearer your-token-here'  # Replace with actual token
        }
        
        response = requests.get(f"{base_url}/api/subscriptions/usage", headers=headers)
        
        if response.status_code == 200:
            usage = response.json()
            print(f"   ✅ Current month invoices: {usage['current_count']}")
            print(f"   ✅ Invoice limit: {usage['limit']}")
            print(f"   ✅ Can create more: {usage['can_create']}")
        else:
            print(f"   ❌ Failed to get usage: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Check current date
    from datetime import datetime
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    
    print(f"\n2. Date calculation verification:")
    print(f"   Current UTC time: {now}")
    print(f"   Current month start: {month_start}")
    print(f"   Current month: {now.strftime('%B %Y')}")
    print(f"   Should show: January 2026")
    
    return True

if __name__ == "__main__":
    test_date_calculation()