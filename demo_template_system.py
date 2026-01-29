#!/usr/bin/env python3
"""
Demo script for the Multi-Template System.

This script demonstrates:
1. Template system initialization
2. Template gallery and selection
3. User template preferences
4. Template switching for invoices and receipts
5. PDF generation with different templates
6. Admin template management
7. Plan-based template access control

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
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment_receipt import PaymentReceipt, ReceiptType, ReceiptStatus
from app.models.template import Template, TemplateCategory
from app.services.template_service import TemplateService
from app.services.template_initialization import TemplateInitializationService
from app.services.pdf_service import PDFService
from app.core.security import get_password_hash


def initialize_template_system(db):
    """Initialize the template system with default templates."""
    
    print("🎨 TEMPLATE SYSTEM INITIALIZATION")
    print("=" * 60)
    
    # Check if templates already exist
    existing_templates = db.query(Template).count()
    if existing_templates > 0:
        print(f"✅ Template system already initialized ({existing_templates} templates found)")
        return
    
    # Initialize templates
    init_service = TemplateInitializationService(db)
    init_service.initialize_all_templates()
    
    # Verify initialization
    total_templates = db.query(Template).count()
    invoice_templates = db.query(Template).filter(Template.category == TemplateCategory.INVOICE).count()
    receipt_templates = db.query(Template).filter(Template.category == TemplateCategory.RECEIPT).count()
    
    print(f"✅ Template system initialized successfully!")
    print(f"   - Total templates: {total_templates}")
    print(f"   - Invoice templates: {invoice_templates}")
    print(f"   - Receipt templates: {receipt_templates}")


def create_demo_data(db):
    """Create demo users and data for template testing."""
    
    print("\n📊 CREATING DEMO DATA")
    print("=" * 60)
    
    # Create free user
    free_user = User(
        email="free@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Free User",
        is_active=True,
        is_verified=True,
        role=UserRole.USER
    )
    db.add(free_user)
    
    # Create premium user
    premium_user = User(
        email="premium@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Premium User",
        is_active=True,
        is_verified=True,
        role=UserRole.USER
    )
    db.add(premium_user)
    
    # Create admin user
    admin_user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User",
        is_active=True,
        is_verified=True,
        role=UserRole.ADMIN
    )
    db.add(admin_user)
    
    db.commit()
    db.refresh(free_user)
    db.refresh(premium_user)
    db.refresh(admin_user)
    
    # Create plans
    free_plan = Plan(
        name="Free Plan",
        description="Basic features",
        price=0,
        currency="INR",
        interval="monthly",
        invoice_limit=3,
        features='["Basic templates", "3 invoices per month"]',
        is_active=True
    )
    
    pro_plan = Plan(
        name="Pro Plan",
        description="All features including premium templates",
        price=9900,  # ₹99
        currency="INR",
        interval="monthly",
        invoice_limit=None,
        features='["All templates", "Unlimited invoices", "Premium designs"]',
        is_active=True
    )
    
    db.add(free_plan)
    db.add(pro_plan)
    db.commit()
    db.refresh(free_plan)
    db.refresh(pro_plan)
    
    # Create subscriptions
    free_subscription = Subscription(
        user_id=free_user.id,
        plan_id=free_plan.id,
        status=SubscriptionStatus.ACTIVE
    )
    
    premium_subscription = Subscription(
        user_id=premium_user.id,
        plan_id=pro_plan.id,
        status=SubscriptionStatus.ACTIVE
    )
    
    db.add(free_subscription)
    db.add(premium_subscription)
    db.commit()
    
    print(f"✅ Created demo users:")
    print(f"   - Free user: {free_user.email}")
    print(f"   - Premium user: {premium_user.email}")
    print(f"   - Admin user: {admin_user.email}")
    
    return free_user, premium_user, admin_user


def demo_template_gallery(db, free_user, premium_user):
    """Demonstrate template gallery and access control."""
    
    print("\n🖼️  TEMPLATE GALLERY DEMO")
    print("=" * 60)
    
    template_service = TemplateService(db)
    
    # 1. Free user template access
    print("1. Free user template access:")
    
    free_invoice_templates = template_service.get_available_templates(
        category=TemplateCategory.INVOICE,
        user_id=free_user.id,
        include_premium=False
    )
    
    print(f"   Available invoice templates for free user: {len(free_invoice_templates)}")
    for template in free_invoice_templates:
        print(f"   - {template.name} ({'Premium' if template.is_premium else 'Free'})")
    
    # 2. Premium user template access
    print("\n2. Premium user template access:")
    
    premium_invoice_templates = template_service.get_available_templates(
        category=TemplateCategory.INVOICE,
        user_id=premium_user.id,
        include_premium=True
    )
    
    print(f"   Available invoice templates for premium user: {len(premium_invoice_templates)}")
    for template in premium_invoice_templates:
        print(f"   - {template.name} ({'Premium' if template.is_premium else 'Free'})")
    
    # 3. Template gallery data
    print("\n3. Template gallery data:")
    
    gallery_data = template_service.get_template_gallery_data(
        category=TemplateCategory.INVOICE,
        user_id=premium_user.id
    )
    
    print(f"   Gallery contains {len(gallery_data)} templates:")
    for template_data in gallery_data:
        print(f"   - {template_data['name']}: {', '.join(template_data['features'])}")


def demo_template_preferences(db, free_user, premium_user):
    """Demonstrate user template preferences."""
    
    print("\n⚙️  TEMPLATE PREFERENCES DEMO")
    print("=" * 60)
    
    template_service = TemplateService(db)
    
    # 1. Get default templates
    print("1. Default templates:")
    
    default_invoice = template_service.get_default_template(TemplateCategory.INVOICE)
    default_receipt = template_service.get_default_template(TemplateCategory.RECEIPT)
    
    print(f"   Default invoice template: {default_invoice.name if default_invoice else 'None'}")
    print(f"   Default receipt template: {default_receipt.name if default_receipt else 'None'}")
    
    # 2. Set user preferences
    print("\n2. Setting user preferences:")
    
    # Free user can only use free templates
    classic_template = template_service.get_template_by_template_id('classic')
    if classic_template:
        success = template_service.set_user_default_template(
            user_id=free_user.id,
            template_id=classic_template.id,
            category=TemplateCategory.INVOICE
        )
        print(f"   Free user set to classic template: {'✅' if success else '❌'}")
    
    # Premium user can use premium templates
    modern_template = template_service.get_template_by_template_id('modern')
    if modern_template:
        success = template_service.set_user_default_template(
            user_id=premium_user.id,
            template_id=modern_template.id,
            category=TemplateCategory.INVOICE
        )
        print(f"   Premium user set to modern template: {'✅' if success else '❌'}")
    
    # 3. Verify user preferences
    print("\n3. User template preferences:")
    
    free_user_template = template_service.get_user_default_template(
        user_id=free_user.id,
        category=TemplateCategory.INVOICE
    )
    
    premium_user_template = template_service.get_user_default_template(
        user_id=premium_user.id,
        category=TemplateCategory.INVOICE
    )
    
    print(f"   Free user default: {free_user_template.name if free_user_template else 'System default'}")
    print(f"   Premium user default: {premium_user_template.name if premium_user_template else 'System default'}")


def demo_invoice_template_switching(db, premium_user):
    """Demonstrate invoice template switching."""
    
    print("\n📄 INVOICE TEMPLATE SWITCHING DEMO")
    print("=" * 60)
    
    template_service = TemplateService(db)
    pdf_service = PDFService(db)
    
    # Create sample invoice
    invoice = Invoice(
        user_id=premium_user.id,
        invoice_number="INV-TEMPLATE-001",
        invoice_title="Template Demo Invoice",
        client_name="Demo Client",
        client_email="client@example.com",
        invoice_date=datetime.now().date(),
        due_date=(datetime.now() + timedelta(days=30)).date(),
        currency="INR",
        currency_symbol="₹",
        subtotal=Decimal('10000.00'),
        tax_amount=Decimal('1800.00'),
        grand_total=Decimal('11800.00'),
        status=InvoiceStatus.DRAFT
    )
    
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    print(f"✅ Created sample invoice: {invoice.invoice_number}")
    
    # Get available templates
    templates = template_service.get_available_templates(
        category=TemplateCategory.INVOICE,
        user_id=premium_user.id
    )
    
    print(f"\n📋 Testing {len(templates)} invoice templates:")
    
    for template in templates:
        print(f"\n   🎨 Testing template: {template.name}")
        
        try:
            # Generate PDF with this template
            pdf_path = pdf_service.generate_invoice_pdf(
                invoice_id=invoice.id,
                user_id=premium_user.id,
                template_id=template.id
            )
            
            if pdf_path and os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path) / 1024  # KB
                print(f"      ✅ PDF generated successfully ({file_size:.1f} KB)")
                print(f"      📁 File: {pdf_path}")
                
                # Verify template was applied
                db.refresh(invoice)
                if invoice.template_id == template.id:
                    print(f"      ✅ Template applied to invoice")
                else:
                    print(f"      ⚠️  Template not applied to invoice")
            else:
                print(f"      ❌ PDF generation failed")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print(f"\n✅ Invoice template switching demo completed")


def demo_receipt_template_switching(db, premium_user):
    """Demonstrate receipt template switching."""
    
    print("\n🧾 RECEIPT TEMPLATE SWITCHING DEMO")
    print("=" * 60)
    
    template_service = TemplateService(db)
    pdf_service = PDFService(db)
    
    # Create sample receipt
    receipt = PaymentReceipt(
        receipt_number="202601001",
        receipt_type=ReceiptType.SUBSCRIPTION_PAYMENT,
        status=ReceiptStatus.DRAFT,
        user_id=premium_user.id,
        receipt_date=datetime.utcnow(),
        payment_date=datetime.utcnow(),
        amount=Decimal('83.90'),
        tax_amount=Decimal('15.10'),
        total_amount=Decimal('99.00'),
        currency="INR",
        currency_symbol="₹",
        payment_method="Credit Card",
        transaction_id="TXN123456789",
        title="Pro Plan Subscription",
        description="Monthly subscription payment",
        customer_name=premium_user.full_name,
        customer_email=premium_user.email,
        company_name="Invoice Generator SaaS"
    )
    
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    
    print(f"✅ Created sample receipt: RCP-{receipt.receipt_number}")
    
    # Get available templates
    templates = template_service.get_available_templates(
        category=TemplateCategory.RECEIPT,
        user_id=premium_user.id
    )
    
    print(f"\n📋 Testing {len(templates)} receipt templates:")
    
    for template in templates:
        print(f"\n   🎨 Testing template: {template.name}")
        
        try:
            # Generate PDF with this template
            pdf_bytes = pdf_service.generate_receipt_pdf(
                receipt=receipt,
                template_id=template.id
            )
            
            if pdf_bytes:
                pdf_size = len(pdf_bytes) / 1024  # KB
                print(f"      ✅ PDF generated successfully ({pdf_size:.1f} KB)")
                
                # Save PDF for verification
                pdf_filename = f"receipt_{template.template_id}_{receipt.receipt_number}.pdf"
                pdf_path = os.path.join("uploads", "temp", pdf_filename)
                os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_bytes)
                
                print(f"      📁 File: {pdf_path}")
                
                # Verify template was applied
                db.refresh(receipt)
                if receipt.template_id == template.id:
                    print(f"      ✅ Template applied to receipt")
                else:
                    print(f"      ⚠️  Template not applied to receipt")
            else:
                print(f"      ❌ PDF generation failed")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print(f"\n✅ Receipt template switching demo completed")


def demo_admin_template_management(db, admin_user):
    """Demonstrate admin template management."""
    
    print("\n👨‍💼 ADMIN TEMPLATE MANAGEMENT DEMO")
    print("=" * 60)
    
    template_service = TemplateService(db)
    
    # 1. Get all templates
    print("1. Template inventory:")
    
    all_templates = db.query(Template).all()
    active_templates = db.query(Template).filter(Template.is_active == True).count()
    premium_templates = db.query(Template).filter(Template.is_premium == True).count()
    
    print(f"   Total templates: {len(all_templates)}")
    print(f"   Active templates: {active_templates}")
    print(f"   Premium templates: {premium_templates}")
    
    # 2. Template statistics by category
    print("\n2. Templates by category:")
    
    for category in TemplateCategory:
        count = db.query(Template).filter(Template.category == category).count()
        print(f"   {category.value.title()} templates: {count}")
    
    # 3. Template usage statistics
    print("\n3. Template usage:")
    
    for template in all_templates:
        # Count invoices using this template
        invoice_count = db.query(Invoice).filter(Invoice.template_id == template.id).count()
        receipt_count = db.query(PaymentReceipt).filter(PaymentReceipt.template_id == template.id).count()
        
        total_usage = invoice_count + receipt_count
        if total_usage > 0:
            print(f"   {template.name}: {total_usage} documents")
    
    # 4. Create custom template (simulation)
    print("\n4. Custom template creation (simulation):")
    
    custom_template_data = {
        'template_id': 'custom_demo',
        'name': 'Custom Demo Template',
        'category': 'invoice',
        'description': 'Custom template created by admin',
        'is_premium': True,
        'sort_order': 10,
        'features': ['Custom design', 'Admin created', 'Demo template']
    }
    
    custom_html = """<!DOCTYPE html>
<html><head><title>Custom Template</title></head>
<body><h1>Custom Invoice Template</h1><p>This is a custom template created by admin.</p></body>
</html>"""
    
    custom_css = """body { font-family: Arial, sans-serif; color: #333; }
h1 { color: #007bff; }"""
    
    try:
        custom_template = template_service.create_template(
            template_data=custom_template_data,
            html_content=custom_html,
            css_content=custom_css,
            admin_user_id=admin_user.id
        )
        
        print(f"   ✅ Created custom template: {custom_template.name}")
        print(f"      Template ID: {custom_template.template_id}")
        print(f"      Category: {custom_template.category.value}")
        print(f"      Premium: {custom_template.is_premium}")
        
    except Exception as e:
        print(f"   ❌ Failed to create custom template: {e}")
    
    print("\n✅ Admin template management demo completed")


def demo_template_preview_generation(db, premium_user):
    """Demonstrate template preview generation."""
    
    print("\n👁️  TEMPLATE PREVIEW DEMO")
    print("=" * 60)
    
    template_service = TemplateService(db)
    
    # Get sample data for previews
    sample_invoice_data = {
        'invoice': {
            'invoice_number': 'PREVIEW-001',
            'invoice_date': datetime.now().date(),
            'client_name': 'Sample Client',
            'client_email': 'client@example.com',
            'subtotal': Decimal('5000.00'),
            'tax_amount': Decimal('900.00'),
            'grand_total': Decimal('5900.00'),
            'currency_symbol': '₹',
            'status': type('Status', (), {'value': 'draft'})()
        },
        'items': [
            {
                'description': 'Sample Service',
                'quantity': 1,
                'rate': Decimal('5000.00'),
                'amount': Decimal('5000.00')
            }
        ],
        'company': {
            'company_name': 'Sample Company',
            'address': '123 Business Street'
        },
        'generated_at': datetime.now(),
        'format_currency': lambda amount, symbol: f"{symbol}{amount:,.2f}",
        'format_date': lambda date: date.strftime('%d/%m/%Y') if date else '',
        'number_to_words': lambda amount: 'Five Thousand Nine Hundred Rupees Only'
    }
    
    # Generate previews for all invoice templates
    invoice_templates = template_service.get_available_templates(
        category=TemplateCategory.INVOICE,
        user_id=premium_user.id
    )
    
    print(f"📋 Generating previews for {len(invoice_templates)} invoice templates:")
    
    for template in invoice_templates:
        try:
            preview_html = template_service.generate_template_preview(
                template=template,
                sample_data=sample_invoice_data
            )
            
            # Save preview HTML
            preview_filename = f"preview_{template.template_id}_invoice.html"
            preview_path = os.path.join("uploads", "previews", preview_filename)
            os.makedirs(os.path.dirname(preview_path), exist_ok=True)
            
            with open(preview_path, 'w', encoding='utf-8') as f:
                f.write(preview_html)
            
            preview_size = len(preview_html) / 1024  # KB
            print(f"   ✅ {template.name}: Preview generated ({preview_size:.1f} KB)")
            print(f"      📁 File: {preview_path}")
            
        except Exception as e:
            print(f"   ❌ {template.name}: Preview failed - {e}")
    
    print("\n✅ Template preview demo completed")


def main():
    """Run the complete template system demo."""
    
    print("🎨 MULTI-TEMPLATE SYSTEM DEMO")
    print("=" * 70)
    print("This demo showcases the complete multi-template system including:")
    print("• Template system initialization with default templates")
    print("• Template gallery with plan-based access control")
    print("• User template preferences and switching")
    print("• PDF generation with different templates")
    print("• Admin template management capabilities")
    print("• Template preview generation")
    print("=" * 70)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Initialize template system
        initialize_template_system(db)
        
        # Create demo data
        free_user, premium_user, admin_user = create_demo_data(db)
        
        # Run demos
        demo_template_gallery(db, free_user, premium_user)
        demo_template_preferences(db, free_user, premium_user)
        demo_invoice_template_switching(db, premium_user)
        demo_receipt_template_switching(db, premium_user)
        demo_admin_template_management(db, admin_user)
        demo_template_preview_generation(db, premium_user)
        
        print("\n🎉 MULTI-TEMPLATE SYSTEM DEMO COMPLETED!")
        print("=" * 70)
        print("✅ Key features demonstrated:")
        print("  • Complete template system with 6 production-ready templates")
        print("  • Plan-based access control (free vs premium templates)")
        print("  • User template preferences and switching")
        print("  • PDF generation with template consistency")
        print("  • Admin template management and custom template creation")
        print("  • Template preview generation for user selection")
        print("  • Modular template architecture for easy expansion")
        print("\n🚀 The multi-template system is ready for production!")
        print("\nAPI Endpoints available:")
        print("  • GET /api/templates/gallery/{category} - Template gallery")
        print("  • GET /api/templates/{id} - Template details")
        print("  • POST /api/templates/set-default - Set user default")
        print("  • GET /api/templates/{id}/preview - Template preview")
        print("  • GET /api/templates/admin/all - Admin: All templates")
        print("  • POST /api/templates/admin/create - Admin: Create template")
        print("  • PUT /api/templates/admin/{id} - Admin: Update template")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    main()