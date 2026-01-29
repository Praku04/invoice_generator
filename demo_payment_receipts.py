#!/usr/bin/env python3
"""
Demo script for the Payment Receipt System.

This script demonstrates:
1. Creating payment receipts from subscription payments
2. Creating payment receipts from invoice payments
3. Generating PDF receipts
4. Sending receipt emails with secure download links
5. Admin CRM management of receipts
6. Integration with audit logging

Run this after setting up the database and environment.
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.plan import Plan
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.invoice import Invoice, InvoiceStatus
from app.models.company_profile import CompanyProfile
from app.models.payment_receipt import PaymentReceipt, ReceiptType, ReceiptStatus
from app.services.payment_receipt_service import PaymentReceiptService
from app.services.audit_service import AuditService
from app.core.security import get_password_hash


def create_demo_data(db):
    """Create demo data for payment receipt testing."""
    
    print("📊 Creating demo data...")
    
    # Create users
    user = User(
        email="customer@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="John Customer",
        is_active=True,
        is_verified=True,
        role=UserRole.USER
    )
    db.add(user)
    
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
    
    # Create company profile
    company_profile = CompanyProfile(
        user_id=user.id,
        company_name="Customer Business Ltd",
        address="123 Business Street",
        city="Business City",
        state="Business State",
        postal_code="12345",
        country="India",
        phone="+91-9876543210",
        gstin="22AAAAA0000A1Z5",
        pan="AAAAA0000A"
    )
    db.add(company_profile)
    
    # Create plan
    plan = Plan(
        name="Pro Plan",
        description="Professional plan with all features",
        price=9900,  # ₹99 in paise
        currency="INR",
        interval="monthly",
        invoice_limit=None,
        features='["Unlimited invoices", "PDF download", "Custom branding"]',
        is_active=True
    )
    db.add(plan)
    
    db.commit()
    db.refresh(plan)
    
    # Create subscription
    subscription = Subscription(
        user_id=user.id,
        plan_id=plan.id,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30)
    )
    db.add(subscription)
    
    db.commit()
    db.refresh(subscription)
    
    # Create successful payment
    payment = Payment(
        subscription_id=subscription.id,
        razorpay_payment_id="pay_demo123456789",
        razorpay_order_id="order_demo123456789",
        amount=Decimal('99.00'),
        currency="INR",
        status=PaymentStatus.SUCCESS,
        method=PaymentMethod.CARD,
        description="Pro Plan subscription payment",
        payment_date=datetime.utcnow()
    )
    db.add(payment)
    
    # Create invoice for invoice payment demo
    invoice = Invoice(
        user_id=user.id,
        invoice_number="INV-2026-001",
        invoice_title="Consulting Services",
        client_name="Client Company",
        client_email="client@company.com",
        client_phone="+91-9876543210",
        client_address_line1="456 Client Street",
        client_city="Client City",
        client_state="Client State",
        client_postal_code="54321",
        client_country="India",
        client_gstin="33BBBBB1111B2Z6",
        invoice_date=datetime.now().date(),
        due_date=(datetime.now() + timedelta(days=30)).date(),
        currency="INR",
        currency_symbol="₹",
        subtotal=Decimal('5000.00'),
        tax_amount=Decimal('900.00'),
        grand_total=Decimal('5900.00'),
        status=InvoiceStatus.PAID
    )
    db.add(invoice)
    
    db.commit()
    db.refresh(payment)
    db.refresh(invoice)
    
    print(f"✅ Created demo user: {user.email}")
    print(f"✅ Created admin user: {admin.email}")
    print(f"✅ Created subscription payment: ₹{payment.amount}")
    print(f"✅ Created invoice: {invoice.invoice_number} (₹{invoice.grand_total})")
    
    return user, admin, payment, invoice, subscription


def demo_subscription_receipt(db, user, admin, payment):
    """Demonstrate subscription payment receipt creation."""
    
    print("\n💳 SUBSCRIPTION PAYMENT RECEIPT DEMO")
    print("=" * 60)
    
    receipt_service = PaymentReceiptService(db)
    
    # 1. Create receipt from payment
    print("1. Creating receipt from subscription payment...")
    
    receipt = receipt_service.create_receipt_from_payment(
        payment_id=payment.id,
        created_by_user_id=user.id,
        admin_notes="Automatically generated from successful payment"
    )
    
    print(f"   ✅ Receipt created: {receipt.formatted_receipt_number}")
    print(f"   - Type: {receipt.receipt_type.value}")
    print(f"   - Amount: {receipt.display_amount}")
    print(f"   - Status: {receipt.status.value}")
    print(f"   - Customer: {receipt.customer_name}")
    
    # 2. Generate PDF
    print("\n2. Generating PDF...")
    
    pdf_path = receipt_service.generate_receipt_pdf(receipt.id, user.id)
    print(f"   ✅ PDF generated: {pdf_path}")
    print(f"   - PDF available: {receipt.is_pdf_available}")
    
    # 3. Admin review
    print("\n3. Admin review...")
    
    reviewed_receipt = receipt_service.admin_review_receipt(
        receipt_id=receipt.id,
        admin_user_id=admin.id,
        notes="Receipt reviewed and approved for customer",
        approved=True
    )
    
    print(f"   ✅ Receipt reviewed by admin")
    print(f"   - Reviewed: {reviewed_receipt.admin_reviewed}")
    print(f"   - Status: {reviewed_receipt.status.value}")
    print(f"   - Admin notes: {reviewed_receipt.admin_notes}")
    
    # 4. Send email (simulate)
    print("\n4. Sending receipt email...")
    
    try:
        success = receipt_service.send_receipt_email(
            receipt_id=receipt.id,
            to_email=receipt.customer_email,
            user_id=user.id
        )
        print(f"   ✅ Email sent: {success}")
        print(f"   - Email sent to: {receipt.customer_email}")
        print(f"   - Email status: {receipt.email_sent}")
    except Exception as e:
        print(f"   ⚠️  Email simulation (SMTP not configured): {e}")
    
    return receipt


def demo_invoice_receipt(db, user, admin, invoice):
    """Demonstrate invoice payment receipt creation."""
    
    print("\n📄 INVOICE PAYMENT RECEIPT DEMO")
    print("=" * 60)
    
    receipt_service = PaymentReceiptService(db)
    
    # 1. Create receipt from invoice payment
    print("1. Creating receipt from invoice payment...")
    
    payment_details = {
        'method': 'Bank Transfer',
        'transaction_id': 'TXN123456789',
        'payment_date': datetime.utcnow()
    }
    
    receipt = receipt_service.create_receipt_from_invoice_payment(
        invoice_id=invoice.id,
        payment_details=payment_details,
        created_by_user_id=user.id
    )
    
    print(f"   ✅ Receipt created: {receipt.formatted_receipt_number}")
    print(f"   - Type: {receipt.receipt_type.value}")
    print(f"   - Amount: {receipt.display_amount}")
    print(f"   - Invoice: {invoice.invoice_number}")
    print(f"   - Client: {receipt.customer_name}")
    
    # 2. Generate PDF and send
    print("\n2. Generating PDF and preparing for send...")
    
    pdf_path = receipt_service.generate_receipt_pdf(receipt.id, user.id)
    print(f"   ✅ PDF generated: {pdf_path}")
    
    # 3. Get secure download URL
    print("\n3. Creating secure download link...")
    
    download_token = receipt_service._generate_secure_download_token(
        user.id, 
        receipt_id=receipt.id
    )
    download_url = f"/api/receipts/download/{download_token.token_plain}"
    
    print(f"   ✅ Secure download link created")
    print(f"   - URL: {download_url}")
    print(f"   - Expires: {download_token.expires_at}")
    print(f"   - Max downloads: {download_token.max_downloads}")
    
    return receipt


def demo_admin_crm_management(db, admin, receipts):
    """Demonstrate admin CRM management of receipts."""
    
    print("\n👨‍💼 ADMIN CRM MANAGEMENT DEMO")
    print("=" * 60)
    
    receipt_service = PaymentReceiptService(db)
    
    # 1. Get all receipts for admin
    print("1. Admin viewing all receipts...")
    
    all_receipts = receipt_service.get_all_receipts_for_admin(limit=10)
    print(f"   ✅ Found {len(all_receipts)} receipts in system")
    
    for receipt in all_receipts:
        print(f"   - {receipt.formatted_receipt_number}: {receipt.display_amount} ({receipt.status.value})")
    
    # 2. Receipt statistics
    print("\n2. Receipt statistics...")
    
    total_receipts = db.query(PaymentReceipt).count()
    total_amount = db.query(db.func.sum(PaymentReceipt.total_amount)).scalar() or 0
    
    # Count by type
    subscription_receipts = db.query(PaymentReceipt).filter(
        PaymentReceipt.receipt_type == ReceiptType.SUBSCRIPTION_PAYMENT
    ).count()
    
    invoice_receipts = db.query(PaymentReceipt).filter(
        PaymentReceipt.receipt_type == ReceiptType.INVOICE_PAYMENT
    ).count()
    
    print(f"   ✅ Total receipts: {total_receipts}")
    print(f"   - Total amount: ₹{total_amount}")
    print(f"   - Subscription receipts: {subscription_receipts}")
    print(f"   - Invoice receipts: {invoice_receipts}")
    
    # 3. Admin actions on receipts
    print("\n3. Admin management actions...")
    
    for receipt in receipts:
        if not receipt.admin_reviewed:
            # Review receipt
            receipt_service.admin_review_receipt(
                receipt_id=receipt.id,
                admin_user_id=admin.id,
                notes=f"Reviewed receipt {receipt.formatted_receipt_number} - all details verified",
                approved=True
            )
            print(f"   ✅ Reviewed receipt: {receipt.formatted_receipt_number}")
    
    # 4. Audit trail
    print("\n4. Audit trail for receipts...")
    
    audit_service = AuditService(db)
    
    for receipt in receipts:
        audit_logs = audit_service.get_resource_audit_logs("receipt", receipt.id)
        print(f"   📋 Audit trail for {receipt.formatted_receipt_number}:")
        
        for log in audit_logs:
            print(f"      - {log.created_at.strftime('%Y-%m-%d %H:%M:%S')}: {log.action}")
            print(f"        {log.description}")


def demo_receipt_matching(db, user, receipts):
    """Demonstrate receipt and account matching."""
    
    print("\n🔗 RECEIPT & ACCOUNT MATCHING DEMO")
    print("=" * 60)
    
    print("1. Verifying receipt-to-user matching...")
    
    for receipt in receipts:
        # Verify receipt belongs to correct user
        assert receipt.user_id == user.id, f"Receipt {receipt.id} user mismatch!"
        
        # Verify payment/subscription matching
        if receipt.payment_id:
            payment = db.query(Payment).filter(Payment.id == receipt.payment_id).first()
            assert payment.subscription.user_id == user.id, "Payment user mismatch!"
            print(f"   ✅ {receipt.formatted_receipt_number} → Payment {payment.razorpay_payment_id}")
        
        if receipt.invoice_id:
            invoice = db.query(Invoice).filter(Invoice.id == receipt.invoice_id).first()
            assert invoice.user_id == user.id, "Invoice user mismatch!"
            print(f"   ✅ {receipt.formatted_receipt_number} → Invoice {invoice.invoice_number}")
    
    print("\n2. Account verification...")
    
    # Get user's subscription
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if subscription:
        print(f"   ✅ User subscription: {subscription.plan.name} ({subscription.status.value})")
        
        # Find related receipt
        subscription_receipt = db.query(PaymentReceipt).filter(
            PaymentReceipt.subscription_id == subscription.id
        ).first()
        
        if subscription_receipt:
            print(f"   ✅ Subscription receipt: {subscription_receipt.formatted_receipt_number}")
            print(f"      - Amount matches plan price: {subscription_receipt.total_amount == (subscription.plan.price / 100)}")
    
    print("\n3. Financial reconciliation...")
    
    # Calculate total payments vs receipts
    user_receipts = db.query(PaymentReceipt).filter(PaymentReceipt.user_id == user.id).all()
    total_receipt_amount = sum(r.total_amount for r in user_receipts)
    
    user_payments = db.query(Payment).join(Subscription).filter(
        Subscription.user_id == user.id,
        Payment.status == PaymentStatus.SUCCESS
    ).all()
    total_payment_amount = sum(p.amount for p in user_payments)
    
    print(f"   ✅ Total receipts amount: ₹{total_receipt_amount}")
    print(f"   ✅ Total payments amount: ₹{total_payment_amount}")
    print(f"   ✅ Amounts match: {total_receipt_amount == total_payment_amount}")


def main():
    """Run the complete payment receipt demo."""
    
    print("🧾 PAYMENT RECEIPT SYSTEM DEMO")
    print("=" * 70)
    print("This demo shows the complete payment receipt system including:")
    print("• Automatic receipt generation from payments")
    print("• PDF generation with professional templates")
    print("• Email notifications with secure download links")
    print("• Admin CRM management and review")
    print("• Account matching and financial reconciliation")
    print("• Complete audit trails")
    print("=" * 70)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create demo data
        user, admin, payment, invoice, subscription = create_demo_data(db)
        
        # Run demos
        subscription_receipt = demo_subscription_receipt(db, user, admin, payment)
        invoice_receipt = demo_invoice_receipt(db, user, admin, invoice)
        
        receipts = [subscription_receipt, invoice_receipt]
        
        demo_admin_crm_management(db, admin, receipts)
        demo_receipt_matching(db, user, receipts)
        
        print("\n🎉 PAYMENT RECEIPT SYSTEM DEMO COMPLETED!")
        print("=" * 70)
        print("✅ Key features demonstrated:")
        print("  • Automatic receipt generation from successful payments")
        print("  • Professional PDF receipts with tax breakdowns")
        print("  • Secure download links with expiration")
        print("  • Email notifications to customers")
        print("  • Admin CRM for receipt management and review")
        print("  • Complete audit trails for compliance")
        print("  • Account matching and financial reconciliation")
        print("  • Support for both subscription and invoice payments")
        print("\n🚀 The payment receipt system is ready for production!")
        print("\nAPI Endpoints available:")
        print("  • GET /api/receipts/ - User receipts")
        print("  • GET /api/receipts/{id} - Specific receipt")
        print("  • POST /api/receipts/{id}/generate-pdf - Generate PDF")
        print("  • POST /api/receipts/{id}/send-email - Send via email")
        print("  • GET /api/receipts/download/{token} - Secure download")
        print("  • GET /api/receipts/admin/all - Admin: All receipts")
        print("  • PUT /api/receipts/admin/{id}/review - Admin: Review receipt")
        print("  • GET /api/receipts/admin/stats - Admin: Statistics")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    main()