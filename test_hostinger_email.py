#!/usr/bin/env python3
"""
Test Hostinger email configuration directly.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_hostinger_email():
    """Test Hostinger email configuration."""
    
    # Hostinger SMTP settings
    smtp_host = "smtp.hostinger.com"
    smtp_port = 587
    smtp_user = "support@themanagementgurus.in"
    smtp_password = "Metasploit@8080"
    from_email = "support@themanagementgurus.in"
    to_email = "support@themanagementgurus.in"  # Send to self for testing
    
    print("Hostinger Email Configuration Test")
    print("=" * 40)
    print(f"SMTP Host: {smtp_host}")
    print(f"SMTP Port: {smtp_port}")
    print(f"SMTP User: {smtp_user}")
    print(f"From Email: {from_email}")
    print(f"To Email: {to_email}")
    print()
    
    try:
        # Create test message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Test Email from Invoice Generator"
        message["From"] = from_email
        message["To"] = to_email
        
        # Create HTML and text content
        text = """
        Test Email from Invoice Generator
        
        This is a test email to verify your Hostinger SMTP configuration is working correctly.
        
        If you receive this email, your email system is configured properly!
        
        Sent from: Invoice Generator SaaS Application
        """
        
        html = """
        <html>
          <body>
            <h2>Test Email from Invoice Generator</h2>
            <p>This is a test email to verify your <strong>Hostinger SMTP</strong> configuration is working correctly.</p>
            <p><strong>If you receive this email, your email system is configured properly!</strong></p>
            <hr>
            <p><em>Sent from: Invoice Generator SaaS Application</em></p>
          </body>
        </html>
        """
        
        # Add text and HTML parts
        text_part = MIMEText(text, "plain")
        html_part = MIMEText(html, "html")
        message.attach(text_part)
        message.attach(html_part)
        
        # Send email
        print("🔄 Attempting to send test email via Hostinger...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            print("📡 Connecting to Hostinger SMTP server...")
            server.starttls(context=context)
            print("🔐 Starting TLS encryption...")
            server.login(smtp_user, smtp_password)
            print("✅ Authentication successful!")
            server.sendmail(from_email, to_email, message.as_string())
            print("📧 Email sent successfully!")
        
        print("\n" + "=" * 40)
        print("🎉 SUCCESS! Hostinger email is working!")
        print(f"📬 Check your inbox at {to_email}")
        print("\nYour Invoice Generator app can now send emails!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print("❌ SMTP Authentication failed!")
        print("Possible issues:")
        print("1. Wrong username or password")
        print("2. SMTP not enabled in Hostinger control panel")
        print("3. Email account suspended or locked")
        print(f"Error details: {e}")
        return False
        
    except smtplib.SMTPConnectError as e:
        print("❌ Cannot connect to Hostinger SMTP server!")
        print("Possible issues:")
        print("1. Wrong SMTP host or port")
        print("2. Firewall blocking connection")
        print("3. Hostinger SMTP service down")
        print(f"Error details: {e}")
        return False
        
    except smtplib.SMTPException as e:
        print("❌ SMTP Error occurred!")
        print(f"Error details: {e}")
        return False
        
    except Exception as e:
        print("❌ Unexpected error occurred!")
        print(f"Error details: {e}")
        return False

if __name__ == "__main__":
    success = test_hostinger_email()
    
    if success:
        print("\n🚀 Next steps:")
        print("1. Your email configuration is working!")
        print("2. Restart your Docker application to pick up the new settings")
        print("3. Test user registration to receive welcome emails")
        print("4. Test password reset to receive reset emails")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Check Hostinger control panel - ensure SMTP is enabled")
        print("2. Verify email account is active and not suspended")
        print("3. Try logging into webmail with the same credentials")
        print("4. Contact Hostinger support if issues persist")