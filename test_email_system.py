#!/usr/bin/env python3
"""
Test the complete email system functionality.
"""

import requests
import json

def test_email_system():
    """Test the email system end-to-end."""
    
    base_url = "http://72.60.222.154:8000"
    
    print("🧪 Testing Email System Functionality")
    print("=" * 50)
    
    # Test 1: Check email configuration
    print("1. Checking email configuration...")
    try:
        response = requests.get(f"{base_url}/test/email-config")
        config = response.json()
        print(f"   ✅ SMTP Host: {config['smtp_host']}")
        print(f"   ✅ SMTP User: {config['smtp_user']}")
        print(f"   ✅ From Email: {config['from_email']}")
        print(f"   ✅ Configured: {config['configured']}")
        
        if not config['configured']:
            print("   ❌ Email not properly configured!")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to check configuration: {e}")
        return False
    
    # Test 2: Send test email
    print("\n2. Sending test email...")
    try:
        response = requests.post(f"{base_url}/test/send-email?email=support@themanagementgurus.in")
        result = response.json()
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        
        if result['status'] != 'success':
            print(f"   ❌ Test email failed: {result.get('error', 'Unknown error')}")
            return False
        else:
            print("   ✅ Test email sent successfully!")
            
    except Exception as e:
        print(f"   ❌ Failed to send test email: {e}")
        return False
    
    # Test 3: Check email logs
    print("\n3. Checking email logs...")
    try:
        response = requests.get(f"{base_url}/test/emails")
        logs = response.json()
        print(f"   Total emails in log: {logs['count']}")
        
        if logs['count'] > 0:
            latest = logs['emails'][0]
            print(f"   Latest email:")
            print(f"     To: {latest['to_email']}")
            print(f"     Subject: {latest['subject']}")
            print(f"     Status: {latest['status']}")
            print(f"     Sent: {latest['created_at']}")
            
            if latest['status'] == 'SENT':
                print("   ✅ Latest email was sent successfully!")
            else:
                print(f"   ❌ Latest email failed: {latest.get('error_message', 'Unknown error')}")
                
    except Exception as e:
        print(f"   ❌ Failed to check email logs: {e}")
        return False
    
    # Test 4: Test password reset flow
    print("\n4. Testing password reset email flow...")
    try:
        # This will trigger a password reset email
        reset_data = {
            "email": "ranjanprakash4u@gmail.com"
        }
        response = requests.post(f"{base_url}/api/auth/forgot-password", json=reset_data)
        result = response.json()
        
        if response.status_code == 200:
            print("   ✅ Password reset email triggered successfully!")
            print(f"   Message: {result['message']}")
        else:
            print(f"   ⚠️  Password reset response: {result}")
            
    except Exception as e:
        print(f"   ❌ Failed to test password reset: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Email System Test Complete!")
    print("\nWhat to check:")
    print("1. Check inbox at support@themanagementgurus.in for test email")
    print("2. Check inbox at ranjanprakash4u@gmail.com for password reset email")
    print("3. Both emails should be from support@themanagementgurus.in")
    print("4. Password reset email should have a working reset link")
    
    return True

if __name__ == "__main__":
    test_email_system()