#!/usr/bin/env python3
"""
Demo script showing the audit and notification system in action.

This script demonstrates:
1. Creating audit logs for various actions
2. Sending notifications to users
3. Email notifications with secure download tokens
4. Admin action logging

Run this after setting up the database and environment.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.invoice import Invoice, InvoiceStatus
from app.models.notification import NotificationType
from app.models.audit_log import AuditAction
from app.models.admin_action import AdminActionType
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.services.email_service import EmailService
from app.core.security import get_password_hash


def create_demo_data(db):
    """Create demo users and data for testing."""
    
    # Create a regular user
    user = User(
        email="demo@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Demo User",
        is_active=True,
        is_verified=True,
        role=UserRole.USER
    )
    db.add(user)
    
    # Create an admin user
    admin = User(
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User",
        is_active=True,
        is_verified=True,
        role=UserRole.ADMIN
    )
    db.add(admin)
    
    db.commit()
    db.refresh(user)
    db.refresh(admin)
    
    # Create a demo invoice
    invoice = Invoice(
        user_id=user.id,
        invoice_number="INV-2026-001",
        invoice_title="Demo Invoice",
        client_name="Demo Client",
        client_email="client@example.com",
        invoice_date=datetime.now().date(),
        due_date=(datetime.now() + timedelta(days=30)).date(),
        currency="INR",
        currency_symbol="₹",
        subtotal=1000.00,
        tax_amount=180.00,
        grand_total=1180.00,
        status=InvoiceStatus.DRAFT
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    return user, admin, invoice


def demo_audit_logging(db, user, admin, invoice):
    """Demonstrate audit logging functionality."""
    
    print("🔍 AUDIT LOGGING DEMO")
    print("=" * 50)
    
    audit_service = AuditService(db)
    
    # 1. Log user actions
    print("1. Logging user actions...")
    
    # User signup
    audit_service.log_user_signup(
        user_id=user.id,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    # User login
    audit_service.log_user_login(
        user_id=user.id,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    # Invoice created
    audit_service.log_invoice_created(
        user_id=user.id,
        invoice_id=invoice.id,
        invoice_number=invoice.invoice_number,
        ip_address="192.168.1.100"
    )
    
    # Invoice finalized
    audit_service.log_invoice_finalized(
        user_id=user.id,
        invoice_id=invoice.id,
        invoice_number=invoice.invoice_number,
        ip_address="192.168.1.100"
    )
    
    print("✅ User actions logged successfully")
    
    # 2. Log admin actions
    print("\n2. Logging admin actions...")
    
    audit_service.log_admin_action(
        admin_id=admin.id,
        action_type=AdminActionType.USER_MANAGEMENT,
        action_name="View User Profile",
        description=f"Viewed profile of user {user.email}",
        target_user_id=user.id,
        target_resource_type="user",
        target_resource_id=user.id,
        ip_address="192.168.1.200",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    print("✅ Admin actions logged successfully")
    
    # 3. Query audit logs
    print("\n3. Querying audit logs...")
    
    user_logs = audit_service.get_user_audit_logs(user.id, limit=10)
    print(f"   Found {len(user_logs)} audit logs for user {user.email}")
    
    for log in user_logs:
        print(f"   - {log.action.value}: {log.description} ({log.created_at})")
    
    security_events = audit_service.get_security_events(user_id=user.id, hours_back=24)
    print(f"   Found {len(security_events)} security events in last 24 hours")
    
    print("✅ Audit log queries completed")


def demo_notifications(db, user, invoice):
    """Demonstrate notification functionality."""
    
    print("\n📢 NOTIFICATION DEMO")
    print("=" * 50)
    
    notification_service = NotificationService(db)
    
    # 1. Create various notifications
    print("1. Creating notifications...")
    
    # Invoice finalized notification
    notification1 = notification_service.notify_invoice_finalized(invoice)
    print(f"   ✅ Invoice finalized notification created (ID: {notification1.id})")
    
    # Account activity notification
    notification2 = notification_service.notify_account_activity(
        user_id=user.id,
        activity_type="Profile Updated",
        description="Your profile information has been updated successfully.",
        metadata={"updated_fields": ["full_name", "phone"]}
    )
    print(f"   ✅ Account activity notification created (ID: {notification2.id})")
    
    # Custom notification
    notification3 = notification_service.create_notification(
        user_id=user.id,
        notification_type=NotificationType.ADMIN_MESSAGE,
        title="Welcome to the Demo!",
        message="This is a demo notification to show how the system works.",
        send_email=False  # Don't send email for demo
    )
    print(f"   ✅ Custom notification created (ID: {notification3.id})")
    
    # 2. Query notifications
    print("\n2. Querying notifications...")
    
    all_notifications = notification_service.get_user_notifications(user.id, limit=10)
    print(f"   Found {len(all_notifications)} total notifications")
    
    unread_notifications = notification_service.get_user_notifications(
        user.id, limit=10, unread_only=True
    )
    print(f"   Found {len(unread_notifications)} unread notifications")
    
    unread_count = notification_service.get_unread_count(user.id)
    print(f"   Unread count: {unread_count}")
    
    # 3. Mark notifications as read
    print("\n3. Managing notification read status...")
    
    # Mark one notification as read
    notification_service.mark_notification_as_read(notification1.id, user.id)
    print(f"   ✅ Marked notification {notification1.id} as read")
    
    # Check unread count again
    new_unread_count = notification_service.get_unread_count(user.id)
    print(f"   New unread count: {new_unread_count}")
    
    print("✅ Notification demo completed")


def demo_email_service(db, user, invoice):
    """Demonstrate email service functionality."""
    
    print("\n📧 EMAIL SERVICE DEMO")
    print("=" * 50)
    
    email_service = EmailService(db)
    
    print("1. Email service capabilities...")
    print("   - Send invoice notifications to users and clients")
    print("   - Generate secure download tokens for PDFs")
    print("   - Send password reset emails")
    print("   - Send welcome emails")
    print("   - Track email delivery status")
    
    print("\n2. Secure download token generation...")
    
    # Generate a secure download token (this would normally be done when sending invoice)
    download_token = email_service._generate_secure_download_token(user.id, invoice.id)
    print(f"   ✅ Generated secure download token: {download_token.token_plain[:20]}...")
    print(f"   - Expires at: {download_token.expires_at}")
    print(f"   - Max downloads: {download_token.max_downloads}")
    print(f"   - Currently used: {download_token.download_count} times")
    
    print("\n3. Email templates available:")
    print("   - Invoice notifications (user & client)")
    print("   - Password reset")
    print("   - Email verification")
    print("   - Welcome email")
    print("   - Subscription notifications")
    
    print("✅ Email service demo completed")


def demo_integration_example(db, user, invoice):
    """Show how all services work together in a real scenario."""
    
    print("\n🔗 INTEGRATION EXAMPLE")
    print("=" * 50)
    
    print("Scenario: User finalizes and sends an invoice")
    
    audit_service = AuditService(db)
    notification_service = NotificationService(db)
    email_service = EmailService(db)
    
    # 1. Finalize invoice (this would be done in InvoiceService)
    print("\n1. Finalizing invoice...")
    invoice.status = InvoiceStatus.FINALIZED
    db.commit()
    
    # Log the action
    audit_service.log_invoice_finalized(
        user_id=user.id,
        invoice_id=invoice.id,
        invoice_number=invoice.invoice_number,
        ip_address="192.168.1.100"
    )
    
    # Send notification
    notification = notification_service.notify_invoice_finalized(invoice)
    print(f"   ✅ Invoice finalized, audit logged, notification sent (ID: {notification.id})")
    
    # 2. Send invoice (simulate)
    print("\n2. Sending invoice to client...")
    
    # Log the send action
    audit_service.log_invoice_sent(
        user_id=user.id,
        invoice_id=invoice.id,
        invoice_number=invoice.invoice_number,
        client_email=invoice.client_email,
        ip_address="192.168.1.100"
    )
    
    # Send notifications (this would also send actual emails)
    notifications = notification_service.notify_invoice_sent(invoice)
    print(f"   ✅ Invoice sent, audit logged, {len(notifications)} notifications created")
    
    # 3. Show the audit trail
    print("\n3. Complete audit trail for this invoice:")
    
    invoice_logs = audit_service.get_resource_audit_logs("invoice", invoice.id)
    for log in invoice_logs:
        print(f"   - {log.created_at.strftime('%Y-%m-%d %H:%M:%S')}: {log.action.value}")
        print(f"     Description: {log.description}")
        if log.ip_address:
            print(f"     IP: {log.ip_address}")
    
    print("✅ Integration example completed")


def main():
    """Run the complete demo."""
    
    print("🚀 AUDIT & NOTIFICATION SYSTEM DEMO")
    print("=" * 60)
    print("This demo shows the audit logging and notification system")
    print("working together to provide comprehensive tracking and")
    print("user communication capabilities.")
    print("=" * 60)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create demo data
        print("\n📊 Creating demo data...")
        user, admin, invoice = create_demo_data(db)
        print(f"✅ Created demo user: {user.email}")
        print(f"✅ Created admin user: {admin.email}")
        print(f"✅ Created demo invoice: {invoice.invoice_number}")
        
        # Run demos
        demo_audit_logging(db, user, admin, invoice)
        demo_notifications(db, user, invoice)
        demo_email_service(db, user, invoice)
        demo_integration_example(db, user, invoice)
        
        print("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("Key features demonstrated:")
        print("✅ Comprehensive audit logging for all user and admin actions")
        print("✅ Real-time notifications with email integration")
        print("✅ Secure download tokens for invoice PDFs")
        print("✅ Complete audit trails for compliance and debugging")
        print("✅ Seamless integration between all services")
        print("\nThe system is ready for production use!")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    main()