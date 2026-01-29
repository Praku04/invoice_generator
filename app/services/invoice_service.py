"""Invoice service for invoice management and calculations."""

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
import os

from app.models.user import User
from app.models.invoice import Invoice, InvoiceStatus
from app.models.invoice_item import InvoiceItem
from app.models.invoice_settings import InvoiceSettings
from app.models.company_profile import CompanyProfile
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.schemas.invoice_item import InvoiceItemCreate
from app.services.subscription_service import SubscriptionService
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService


class InvoiceService:
    """Service class for invoice operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.subscription_service = SubscriptionService(db)
        self.audit_service = AuditService(db)
        self.notification_service = NotificationService(db)
    
    def create_invoice(self, user_id: int, invoice_data: InvoiceCreate) -> Optional[Invoice]:
        """Create a new invoice."""
        # Check invoice limit
        can_create, current_count, limit = self.subscription_service.check_invoice_limit(user_id)
        if not can_create:
            raise ValueError(f"Invoice limit exceeded. Current: {current_count}, Limit: {limit}")
        
        # Get user settings
        settings = self.get_or_create_invoice_settings(user_id)
        
        # Generate invoice number
        invoice_number = self._generate_invoice_number(settings)
        
        # Create invoice
        invoice = Invoice(
            user_id=user_id,
            invoice_number=invoice_number,
            invoice_title=invoice_data.invoice_title,
            client_name=invoice_data.client_name,
            client_email=invoice_data.client_email,
            client_phone=invoice_data.client_phone,
            client_address_line1=invoice_data.client_address_line1,
            client_address_line2=invoice_data.client_address_line2,
            client_city=invoice_data.client_city,
            client_state=invoice_data.client_state,
            client_postal_code=invoice_data.client_postal_code,
            client_country=invoice_data.client_country,
            client_gstin=invoice_data.client_gstin,
            invoice_date=invoice_data.invoice_date,
            due_date=invoice_data.due_date,
            notes=invoice_data.notes,
            terms=invoice_data.terms,
            footer_message=invoice_data.footer_message,
            currency=settings.currency,
            currency_symbol=settings.currency_symbol,
            discount_percentage=invoice_data.discount_percentage or Decimal('0.00'),
            discount_amount=invoice_data.discount_amount or Decimal('0.00')
        )
        
        self.db.add(invoice)
        self.db.flush()  # Get invoice ID
        
        # Add items
        for item_data in invoice_data.items:
            self.add_invoice_item(invoice.id, item_data)
        
        # Calculate totals
        self._calculate_invoice_totals(invoice)
        
        self.db.commit()
        self.db.refresh(invoice)
        
        # Log audit event
        self.audit_service.log_invoice_created(
            user_id=user_id,
            invoice_id=invoice.id,
            invoice_number=invoice.invoice_number
        )
        
        return invoice
    
    def update_invoice(self, invoice_id: int, user_id: int, invoice_data: InvoiceUpdate) -> Optional[Invoice]:
        """Update an existing invoice."""
        invoice = self.get_invoice_by_id(invoice_id, user_id)
        if not invoice:
            return None
        
        # Only allow updates to draft invoices
        if invoice.status != InvoiceStatus.DRAFT:
            raise ValueError("Can only update draft invoices")
        
        # Update fields
        update_data = invoice_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(invoice, field):
                setattr(invoice, field, value)
        
        # Recalculate totals
        self._calculate_invoice_totals(invoice)
        
        self.db.commit()
        self.db.refresh(invoice)
        
        # Log audit event
        self.audit_service.log_invoice_updated(
            user_id=user_id,
            invoice_id=invoice.id,
            invoice_number=invoice.invoice_number,
            changes=update_data
        )
        
        return invoice
    
    def get_invoice_by_id(self, invoice_id: int, user_id: int) -> Optional[Invoice]:
        """Get invoice by ID for specific user."""
        return self.db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.user_id == user_id
        ).first()
    
    def get_user_invoices(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get all invoices for a user."""
        return self.db.query(Invoice).filter(
            Invoice.user_id == user_id
        ).order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
    
    def delete_invoice(self, invoice_id: int, user_id: int) -> bool:
        """Delete an invoice (only drafts)."""
        invoice = self.get_invoice_by_id(invoice_id, user_id)
        if not invoice:
            return False
        
        if invoice.status != InvoiceStatus.DRAFT:
            raise ValueError("Can only delete draft invoices")
        
        # Delete PDF file if exists
        if invoice.pdf_file_path and os.path.exists(invoice.pdf_file_path):
            os.remove(invoice.pdf_file_path)
        
        self.db.delete(invoice)
        self.db.commit()
        return True
    
    def finalize_invoice(self, invoice_id: int, user_id: int) -> bool:
        """Finalize an invoice (make it immutable)."""
        invoice = self.get_invoice_by_id(invoice_id, user_id)
        if not invoice:
            return False
        
        if invoice.status != InvoiceStatus.DRAFT:
            raise ValueError("Can only finalize draft invoices")
        
        invoice.status = InvoiceStatus.FINALIZED
        self.db.commit()
        
        # Log audit event
        self.audit_service.log_invoice_finalized(
            user_id=user_id,
            invoice_id=invoice.id,
            invoice_number=invoice.invoice_number
        )
        
        # Send notification
        self.notification_service.notify_invoice_finalized(invoice)
        
        return True
    
    def add_invoice_item(self, invoice_id: int, item_data: InvoiceItemCreate) -> InvoiceItem:
        """Add an item to an invoice."""
        # Get company profile for GST calculation
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        company_profile = self.db.query(CompanyProfile).filter(
            CompanyProfile.user_id == invoice.user_id
        ).first()
        
        # Calculate GST rates based on company and client state
        cgst_rate, sgst_rate, igst_rate = self._calculate_gst_rates(
            item_data.gst_rate,
            company_profile.state if company_profile else None,
            invoice.client_state
        )
        
        # Calculate amounts
        line_total = item_data.quantity * item_data.rate
        discount_amount = item_data.discount_amount or Decimal('0.00')
        if item_data.discount_percentage:
            discount_amount = line_total * (item_data.discount_percentage / 100)
        
        taxable_amount = line_total - discount_amount
        cgst_amount = taxable_amount * (cgst_rate / 100)
        sgst_amount = taxable_amount * (sgst_rate / 100)
        igst_amount = taxable_amount * (igst_rate / 100)
        total_amount = taxable_amount + cgst_amount + sgst_amount + igst_amount
        
        item = InvoiceItem(
            invoice_id=invoice_id,
            item_name=item_data.item_name,
            description=item_data.description,
            hsn_code=item_data.hsn_code,
            quantity=item_data.quantity,
            unit=item_data.unit,
            rate=item_data.rate,
            discount_amount=discount_amount,
            discount_percentage=item_data.discount_percentage or Decimal('0.00'),
            gst_rate=item_data.gst_rate,
            cgst_rate=cgst_rate,
            sgst_rate=sgst_rate,
            igst_rate=igst_rate,
            line_total=line_total,
            taxable_amount=taxable_amount,
            cgst_amount=cgst_amount,
            sgst_amount=sgst_amount,
            igst_amount=igst_amount,
            total_amount=total_amount
        )
        
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        
        return item
    
    def get_or_create_invoice_settings(self, user_id: int) -> InvoiceSettings:
        """Get or create invoice settings for user."""
        settings = self.db.query(InvoiceSettings).filter(
            InvoiceSettings.user_id == user_id
        ).first()
        
        if not settings:
            settings = InvoiceSettings(user_id=user_id)
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        
        return settings
    
    def _generate_invoice_number(self, settings: InvoiceSettings) -> str:
        """Generate next invoice number."""
        invoice_number = settings.invoice_number_format.format(
            prefix=settings.invoice_prefix,
            number=settings.next_invoice_number
        )
        
        # Increment next number
        settings.next_invoice_number += 1
        self.db.commit()
        
        return invoice_number
    
    def _calculate_gst_rates(self, gst_rate: Decimal, company_state: str, client_state: str) -> tuple[Decimal, Decimal, Decimal]:
        """Calculate CGST, SGST, IGST rates based on states."""
        if not company_state or not client_state:
            # If states are unknown, use IGST
            return Decimal('0.00'), Decimal('0.00'), gst_rate
        
        if company_state.lower() == client_state.lower():
            # Same state - CGST + SGST
            half_rate = gst_rate / 2
            return half_rate, half_rate, Decimal('0.00')
        else:
            # Different state - IGST
            return Decimal('0.00'), Decimal('0.00'), gst_rate
    
    def _calculate_invoice_totals(self, invoice: Invoice) -> None:
        """Calculate invoice totals from items."""
        items = self.db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
        
        subtotal = sum(item.line_total for item in items)
        
        # Apply invoice-level discount
        if invoice.discount_percentage > 0:
            invoice.discount_amount = subtotal * (invoice.discount_percentage / 100)
        
        taxable_amount = subtotal - invoice.discount_amount
        
        # Calculate taxes
        cgst_amount = sum(item.cgst_amount for item in items)
        sgst_amount = sum(item.sgst_amount for item in items)
        igst_amount = sum(item.igst_amount for item in items)
        total_tax = cgst_amount + sgst_amount + igst_amount
        
        # Calculate grand total
        grand_total = taxable_amount + total_tax
        
        # Round off to nearest rupee
        rounded_total = grand_total.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        round_off = rounded_total - grand_total
        
        # Update invoice
        invoice.subtotal = subtotal
        invoice.taxable_amount = taxable_amount
        invoice.cgst_amount = cgst_amount
        invoice.sgst_amount = sgst_amount
        invoice.igst_amount = igst_amount
        invoice.total_tax = total_tax
        invoice.round_off = round_off
        invoice.grand_total = rounded_total