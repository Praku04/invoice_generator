#!/usr/bin/env python3
"""
Simple email test script to verify SMTP configuration.
Run this script to test if your email settings are working.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_config():
    """Test email configuration."""
    
    # Get settings from environment
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL')
    
    print("Email Configuration:")
    print(f"SMTP Host: {smtp_host}")
    print(f"SMTP Port: {smtp_port}")
    print(f"SMTP User: {smtp_user}")
    print(f"From Email: {from_email}")
    print(f"Password Set: {'Yes' if smtp_password else 'No'}")
    print()
    
    if not all([smtp_host, smtp_user, smtp_password]):
        print("❌ Email configuration incomplete!")
        print("Please set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD in your .env file")
        return False
    
    try:
        # Create test message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Test Email from Invoice Generator"
        message["From"] = from_email
        
        # For Mailtrap, send to any email. For others, send to self
        test_email = "test@example.com" if "mailtrap" in smtp_host else smtp_user
        message["To"] = test_email
        
        # Create HTML and text content
        text = """
        Test Email
        
        This is a test email to verify your SMTP configuration is working correctly.
        
        If you receive this email, your email system is configured properly!
        """
        
        html = """
        <html>
          <body>
            <h2>Test Email</h2>
            <p>This is a test email to verify your SMTP configuration is working correctly.</p>
            <p><strong>If you receive this email, your email system is configured properly!</strong></p>
            <p><em>Provider: {}</em></p>
          </body>
        </html>
        """.format(smtp_host)
        
        # Add text and HTML parts
        text_part = MIMEText(text, "plain")
        html_part = MIMEText(html, "html")
        message.attach(text_part)
        message.attach(html_part)
        
        # Send email
        print("🔄 Attempting to send test email...")
        
        if smtp_port == 465:
            # Use SSL for port 465
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                server.login(smtp_user, smtp_password)
                server.sendmail(from_email, test_email, message.as_string())
        else:
            # Use STARTTLS for other ports
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls(context=context)
                server.login(smtp_user, smtp_password)
                server.sendmail(from_email, test_email, message.as_string())
        
        print("✅ Test email sent successfully!")
        if "mailtrap" in smtp_host:
            print("📧 Check your Mailtrap inbox at https://mailtrap.io/inboxes")
        else:
            print(f"📧 Check your inbox at {test_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print("❌ SMTP Authentication failed!")
        print("This usually means:")
        print("1. Wrong username/password")
        print("2. For Gmail: You need to use an App Password, not your regular password")
        print("3. For Gmail: 2-Step Verification must be enabled")
        print(f"Error: {e}")
        return False
        
    except smtplib.SMTPException as e:
        print("❌ SMTP Error occurred!")
        print(f"Error: {e}")
        return False
        
    except Exception as e:
        print("❌ Unexpected error occurred!")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Email Configuration...")
    print("=" * 50)
    
    success = test_email_config()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Email configuration test completed successfully!")
        print("Your application should now be able to send emails.")
    else:
        print("💡 Email configuration needs to be fixed.")
        print("\nFor Gmail users:")
        print("1. Enable 2-Step Verification in your Google Account")
        print("2. Generate an App Password:")
        print("   - Go to https://myaccount.google.com/security")
        print("   - Click 'App passwords'")
        print("   - Select 'Mail' and 'Other (Custom name)'")
        print("   - Enter 'Invoice Generator' as the name")
        print("   - Use the generated 16-character password in your .env file")
        print("3. For Hostinger: Make sure SMTP is enabled in your hosting control panel")
        print("4. Update SMTP_PASSWORD in your .env file")
        print("5. Restart your application")