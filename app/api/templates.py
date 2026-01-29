"""Template API endpoints for managing invoice and receipt templates."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_admin_user
from app.models.user import User
from app.models.template import Template, TemplateCategory
from app.services.template_service import TemplateService
from app.services.audit_service import AuditService
from app.schemas.template import (
    TemplateResponse,
    TemplateListResponse,
    TemplateGalleryResponse,
    TemplatePreferenceRequest,
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplatePreviewRequest
)

router = APIRouter()


@router.get("/gallery/{category}", response_model=TemplateGalleryResponse)
def get_template_gallery(
    category: TemplateCategory,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get template gallery for a specific category."""
    
    template_service = TemplateService(db)
    
    # Get available templates
    templates = template_service.get_available_templates(
        category=category,
        user_id=current_user.id,
        include_premium=True
    )
    
    # Get user's current default template
    current_default = template_service.get_user_default_template(
        user_id=current_user.id,
        category=category
    )
    
    # Build gallery data
    gallery_items = []
    for template in templates:
        gallery_items.append({
            'id': template.id,
            'template_id': template.template_id,
            'name': template.name,
            'description': template.description,
            'is_premium': template.is_premium,
            'is_default': current_default and current_default.id == template.id,
            'features': template.get_features_list(),
            'preview_url': template_service.get_template_preview_url(template),
            'supports_logo': template.supports_logo,
            'supports_signature': template.supports_signature,
            'supports_watermark': template.supports_watermark
        })
    
    return TemplateGalleryResponse(
        category=category,
        templates=gallery_items,
        current_default_id=current_default.id if current_default else None
    )


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get template details."""
    
    template_service = TemplateService(db)
    template = template_service.get_template_by_id(template_id)
    
    if not template or not template.is_available:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check if user has access to premium template
    if template.is_premium:
        if not template_service._user_has_premium_access(current_user.id):
            raise HTTPException(status_code=403, detail="Premium template requires subscription")
    
    return TemplateResponse.from_orm(template)


@router.post("/set-default")
def set_default_template(
    preference: TemplatePreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set user's default template for a category."""
    
    template_service = TemplateService(db)
    
    success = template_service.set_user_default_template(
        user_id=current_user.id,
        template_id=preference.template_id,
        category=preference.category
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to set default template")
    
    return {"message": "Default template updated successfully"}


@router.get("/{template_id}/preview", response_class=HTMLResponse)
def get_template_preview(
    template_id: int,
    preview_data: TemplatePreviewRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get HTML preview of template with sample data."""
    
    template_service = TemplateService(db)
    template = template_service.get_template_by_id(template_id)
    
    if not template or not template.is_available:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check premium access
    if template.is_premium:
        if not template_service._user_has_premium_access(current_user.id):
            raise HTTPException(status_code=403, detail="Premium template requires subscription")
    
    # Generate sample data based on template category
    if template.category == TemplateCategory.INVOICE:
        sample_data = _get_sample_invoice_data()
    else:
        sample_data = _get_sample_receipt_data()
    
    # Generate preview HTML
    preview_html = template_service.generate_template_preview(template, sample_data)
    
    return HTMLResponse(content=preview_html)


# Admin endpoints
@router.get("/admin/all", response_model=TemplateListResponse)
def get_all_templates_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[TemplateCategory] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all templates for admin management."""
    
    query = db.query(Template)
    
    if category:
        query = query.filter(Template.category == category)
    
    if is_active is not None:
        query = query.filter(Template.is_active == is_active)
    
    templates = query.order_by(Template.category, Template.sort_order).offset(skip).limit(limit).all()
    
    return TemplateListResponse(
        templates=[TemplateResponse.from_orm(t) for t in templates],
        total_count=len(templates),
        has_more=len(templates) == limit
    )


@router.post("/admin/create", response_model=TemplateResponse)
def create_template_admin(
    template_data: TemplateCreateRequest,
    html_file: UploadFile = File(...),
    css_file: UploadFile = File(...),
    preview_image: Optional[UploadFile] = File(None),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new template (admin only)."""
    
    template_service = TemplateService(db)
    
    # Read file contents
    html_content = html_file.file.read().decode('utf-8')
    css_content = css_file.file.read().decode('utf-8')
    preview_image_bytes = preview_image.file.read() if preview_image else None
    
    # Create template
    template = template_service.create_template(
        template_data=template_data.dict(),
        html_content=html_content,
        css_content=css_content,
        preview_image=preview_image_bytes,
        admin_user_id=current_admin.id
    )
    
    return TemplateResponse.from_orm(template)


@router.put("/admin/{template_id}", response_model=TemplateResponse)
def update_template_admin(
    template_id: int,
    template_data: TemplateUpdateRequest,
    html_file: Optional[UploadFile] = File(None),
    css_file: Optional[UploadFile] = File(None),
    preview_image: Optional[UploadFile] = File(None),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update a template (admin only)."""
    
    template_service = TemplateService(db)
    
    # Read file contents if provided
    html_content = html_file.file.read().decode('utf-8') if html_file else None
    css_content = css_file.file.read().decode('utf-8') if css_file else None
    preview_image_bytes = preview_image.file.read() if preview_image else None
    
    # Update template
    template = template_service.update_template(
        template_id=template_id,
        template_data=template_data.dict(exclude_unset=True),
        html_content=html_content,
        css_content=css_content,
        preview_image=preview_image_bytes,
        admin_user_id=current_admin.id
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return TemplateResponse.from_orm(template)


@router.delete("/admin/{template_id}")
def delete_template_admin(
    template_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a template (admin only)."""
    
    template_service = TemplateService(db)
    
    success = template_service.delete_template(template_id, current_admin.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"message": "Template deleted successfully"}


@router.post("/admin/initialize-defaults")
def initialize_default_templates_admin(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Initialize default templates (admin only)."""
    
    template_service = TemplateService(db)
    template_service.initialize_default_templates()
    
    return {"message": "Default templates initialized successfully"}


def _get_sample_invoice_data() -> dict:
    """Get sample data for invoice template preview."""
    from datetime import datetime, timedelta
    from decimal import Decimal
    
    return {
        'invoice': {
            'invoice_number': 'INV-2026-001',
            'invoice_date': datetime.now().date(),
            'due_date': (datetime.now() + timedelta(days=30)).date(),
            'client_name': 'Sample Client Company',
            'client_email': 'client@example.com',
            'client_phone': '+91-9876543210',
            'client_address_line1': '123 Client Street',
            'client_city': 'Mumbai',
            'client_state': 'Maharashtra',
            'client_postal_code': '400001',
            'client_country': 'India',
            'client_gstin': '27AAAAA0000A1Z5',
            'subtotal': Decimal('10000.00'),
            'tax_amount': Decimal('1800.00'),
            'grand_total': Decimal('11800.00'),
            'currency_symbol': '₹',
            'notes': 'Thank you for your business!',
            'terms': 'Payment due within 30 days.',
            'status': type('Status', (), {'value': 'finalized'})()
        },
        'items': [
            {
                'description': 'Web Development Services',
                'quantity': 1,
                'rate': Decimal('8000.00'),
                'amount': Decimal('8000.00'),
                'notes': 'Custom website development',
                'cgst_amount': Decimal('720.00'),
                'sgst_amount': Decimal('720.00'),
                'igst_amount': Decimal('0.00')
            },
            {
                'description': 'SEO Optimization',
                'quantity': 1,
                'rate': Decimal('2000.00'),
                'amount': Decimal('2000.00'),
                'notes': 'Search engine optimization',
                'cgst_amount': Decimal('180.00'),
                'sgst_amount': Decimal('180.00'),
                'igst_amount': Decimal('0.00')
            }
        ],
        'company': {
            'company_name': 'Sample Company Ltd',
            'address': '456 Business Street',
            'city': 'Delhi',
            'state': 'Delhi',
            'postal_code': '110001',
            'country': 'India',
            'phone': '+91-11-12345678',
            'gstin': '07AAAAA0000A1Z5',
            'pan': 'AAAAA0000A'
        },
        'generated_at': datetime.now(),
        'format_currency': lambda amount, symbol: f"{symbol}{amount:,.2f}",
        'format_date': lambda date: date.strftime('%d/%m/%Y') if date else '',
        'number_to_words': lambda amount: 'Eleven Thousand Eight Hundred Rupees Only'
    }


def _get_sample_receipt_data() -> dict:
    """Get sample data for receipt template preview."""
    from datetime import datetime
    from decimal import Decimal
    
    return {
        'receipt': {
            'receipt_number': '202601001',
            'formatted_receipt_number': 'RCP-202601001',
            'receipt_date': datetime.now(),
            'payment_date': datetime.now(),
            'receipt_type': type('ReceiptType', (), {'value': 'subscription_payment'})(),
            'customer_name': 'John Customer',
            'customer_email': 'john@example.com',
            'customer_phone': '+91-9876543210',
            'customer_address': '789 Customer Lane, Mumbai, Maharashtra 400001',
            'customer_gstin': '27BBBBB1111B2Z6',
            'company_name': 'Invoice Generator SaaS',
            'company_address': '123 Business Street, Delhi, Delhi 110001, India',
            'company_gstin': '07AAAAA0000A1Z5',
            'company_pan': 'AAAAA0000A',
            'amount': Decimal('83.90'),
            'tax_amount': Decimal('15.10'),
            'total_amount': Decimal('99.00'),
            'currency_symbol': '₹',
            'payment_method': 'Credit Card',
            'transaction_id': 'TXN123456789',
            'razorpay_payment_id': 'pay_demo123456789',
            'title': 'Pro Plan Subscription Payment',
            'description': 'Monthly subscription for Pro Plan',
            'notes': 'Thank you for subscribing to our Pro Plan!'
        },
        'generated_at': datetime.now(),
        'format_currency': lambda amount, symbol: f"{symbol}{amount:,.2f}",
        'format_date': lambda date: date.strftime('%d/%m/%Y') if date else '',
        'number_to_words': lambda amount: 'Ninety Nine Rupees Only'
    }