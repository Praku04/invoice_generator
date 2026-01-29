"""Payment receipt service for managing payment receipts and PDF generation."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
import os
import secrets
import hashlib

from app.models.payment_receipt import PaymentReceipt, ReceiptStatus, ReceiptType
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.invoice import Invoice
from app.models.user import User
from app.models.company_profile import CompanyProfile
from app.models.secure_download_token import SecureDownloadToken
from app.services.pdf_service import PDFService
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.services.email_service import EmailService
from app.schemas.payment_receipt import PaymentReceiptCreate, PaymentReceiptUpdate
from app.config import settings


class PaymentReceiptService:
    """Service class for payment receipt operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.pdf_service = PDFService()
        self.audit_service = AuditService(db)
        self.notification_service = NotificationService(db)
        self.email_service = EmailService(db)
    
    def create_receipt_from_payment(
        self,
        payment_id: int,
        created_by_user_id: int = None,
        admin_notes: str = None
    ) -> PaymentReceipt:
        """Create a payment receipt from a successful payment."""
        
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError("Payment not found")
        
        if payment.status != "success":
            raise ValueError("Can only create receipts for successful payments")
        
        # Check if receipt already exists
        existing_receipt = self.db.query(PaymentReceipt).filter(
            PaymentReceipt.payment_id == payment_id
        ).first()
        if existing_receipt:
            return existing_receipt
        
        # Get user and subscription details
        subscription = payment.subscription
        user = subscription.user
        company_profile = self.db.query(CompanyProfile).filter(
            CompanyProfile.user_id == user.id
        ).first()
        
        # Generate receipt number
        receipt_number = self._generate_receipt_number()
        
        # Calculate tax (18% GST on subscription)
        tax_rate = Decimal('0.18')  # 18% GST
        amount_before_tax = payment.amount / (1 + tax_rate)
        tax_amount = payment.amount - amount_before_tax
        
        # Create receipt
        receipt = PaymentReceipt(
            receipt_number=receipt_number,
            receipt_type=ReceiptType.SUBSCRIPTION_PAYMENT,
            status=ReceiptStatus.DRAFT,
            user_id=user.id,
            payment_id=payment.id,
            subscription_id=subscription.id,
            receipt_date=datetime.utcnow(),
            payment_date=payment.payment_date or payment.created_at,
            amount=amount_before_tax,
            tax_amount=tax_amount,
            total_amount=payment.amount,
            currency=payment.currency,
            currency_symbol="₹",
            payment_method=payment.method.value if payment.method else "Online",
            transaction_id=payment.razorpay_payment_id,
            razorpay_payment_id=payment.razorpay_payment_id,
            title=f"{subscription.plan.name} Subscription Payment",
            description=f"Payment for {subscription.plan.name} subscription plan",
            customer_name=user.full_name,
            customer_email=user.email,
            customer_phone=company_profile.phone if company_profile else None,
            customer_address=self._format_address(company_profile) if company_profile else None,
            customer_gstin=company_profile.gstin if company_profile else None,
            company_name=settings.app_name,
            company_address=self._get_company_address(),
            company_gstin=self._get_company_gstin(),
            company_pan=self._get_company_pan(),
            admin_notes=admin_notes,
            created_by=created_by_user_id
        )
        
        self.db.add(receipt)
        self.db.commit()
        self.db.refresh(receipt)
        
        # Log audit event
        self.audit_service.log_action(
            action="RECEIPT_CREATED",
            user_id=created_by_user_id or user.id,
            description=f"Created payment receipt {receipt.receipt_number}",
            resource_type="receipt",
            resource_id=receipt.id,
            metadata={
                "receipt_number": receipt.receipt_number,
                "payment_id": payment.id,
                "amount": str(payment.amount)
            }
        )
        
        return receipt
    
    def create_receipt_from_invoice_payment(
        self,
        invoice_id: int,
        payment_details: Dict[str, Any],
        created_by_user_id: int = None
    ) -> PaymentReceipt:
        """Create a payment receipt from invoice payment."""
        
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError("Invoice not found")
        
        user = invoice.user
        company_profile = self.db.query(CompanyProfile).filter(
            CompanyProfile.user_id == user.id
        ).first()
        
        # Generate receipt number
        receipt_number = self._generate_receipt_number()
        
        # Create receipt
        receipt = PaymentReceipt(
            receipt_number=receipt_number,
            receipt_type=ReceiptType.INVOICE_PAYMENT,
            status=ReceiptStatus.DRAFT,
            user_id=user.id,
            invoice_id=invoice.id,
            receipt_date=datetime.utcnow(),
            payment_date=payment_details.get('payment_date', datetime.utcnow()),
            amount=invoice.subtotal,
            tax_amount=invoice.tax_amount,
            total_amount=invoice.grand_total,
            currency=invoice.currency,
            currency_symbol=invoice.currency_symbol,
            payment_method=payment_details.get('method', 'Cash'),
            transaction_id=payment_details.get('transaction_id'),
            title=f"Payment for Invoice {invoice.invoice_number}",
            description=f"Payment received for invoice {invoice.invoice_number}",
            customer_name=invoice.client_name,
            customer_email=invoice.client_email,
            customer_phone=invoice.client_phone,
            customer_address=self._format_invoice_client_address(invoice),
            customer_gstin=invoice.client_gstin,
            company_name=company_profile.company_name if company_profile else user.full_name,
            company_address=self._format_address(company_profile) if company_profile else None,
            company_gstin=company_profile.gstin if company_profile else None,
            company_pan=company_profile.pan if company_profile else None,
            created_by=created_by_user_id
        )
        
        self.db.add(receipt)
        self.db.commit()
        self.db.refresh(receipt)
        
        # Log audit event
        self.audit_service.log_action(
            action="RECEIPT_CREATED",
            user_id=created_by_user_id or user.id,
            description=f"Created payment receipt {receipt.receipt_number} for invoice {invoice.invoice_number}",
            resource_type="receipt",
            resource_id=receipt.id,
            metadata={
                "receipt_number": receipt.receipt_number,
                "invoice_id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "amount": str(invoice.grand_total)
            }
        )
        
        return receipt
    
    def generate_receipt_pdf(self, receipt_id: int, user_id: int = None) -> str:
        """Generate PDF for payment receipt."""
        
        receipt = self.get_receipt_by_id(receipt_id, user_id)
        if not receipt:
            raise ValueError("Receipt not found")
        
        # Generate PDF using template
        pdf_content = self.pdf_service.generate_receipt_pdf(receipt)
        
        # Save PDF file
        pdf_filename = f"receipt_{receipt.receipt_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(settings.upload_dir, "receipts", pdf_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        
        # Write PDF content
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        # Update receipt
        receipt.pdf_generated = True
        receipt.pdf_file_path = pdf_path
        receipt.pdf_generated_at = datetime.utcnow()
        receipt.status = ReceiptStatus.GENERATED
        
        self.db.commit()
        
        # Log audit event
        self.audit_service.log_action(
            action="RECEIPT_PDF_GENERATED",
            user_id=user_id or receipt.user_id,
            description=f"Generated PDF for receipt {receipt.receipt_number}",
            resource_type="receipt",
            resource_id=receipt.id,
            metadata={
                "receipt_number": receipt.receipt_number,
                "pdf_path": pdf_path
            }
        )
        
        return pdf_path
    
    def send_receipt_email(
        self,
        receipt_id: int,
        to_email: str = None,
        user_id: int = None
    ) -> bool:
        """Send receipt via email."""
        
        receipt = self.get_receipt_by_id(receipt_id, user_id)
        if not receipt:
            raise ValueError("Receipt not found")
        
        # Generate PDF if not already generated
        if not receipt.is_pdf_available:
            self.generate_receipt_pdf(receipt_id, user_id)
            self.db.refresh(receipt)
        
        # Use customer email if not specified
        email_to = to_email or receipt.customer_email
        
        # Generate secure download token
        download_token = self._generate_secure_download_token(
            receipt.user_id, 
            receipt_id=receipt.id
        )
        download_url = f"{settings.app_base_url}/api/receipts/download/{download_token.token_plain}"
        
        # Send email
        email_log = self.email_service.send_receipt_notification(
            receipt=receipt,
            to_email=email_to,
            download_url=download_url
        )
        
        # Update receipt
        receipt.mark_as_sent(email_to)
        self.db.commit()
        
        # Log audit event
        self.audit_service.log_action(
            action="RECEIPT_SENT",
            user_id=user_id or receipt.user_id,
            description=f"Sent receipt {receipt.receipt_number} to {email_to}",
            resource_type="receipt",
            resource_id=receipt.id,
            metadata={
                "receipt_number": receipt.receipt_number,
                "email_to": email_to,
                "email_log_id": email_log.id
            }
        )
        
        return email_log.status == "sent"
    
    def get_receipt_by_id(self, receipt_id: int, user_id: int = None) -> Optional[PaymentReceipt]:
        """Get receipt by ID."""
        query = self.db.query(PaymentReceipt).filter(PaymentReceipt.id == receipt_id)
        
        if user_id:
            query = query.filter(PaymentReceipt.user_id == user_id)
        
        return query.first()
    
    def get_receipt_by_number(self, receipt_number: str, user_id: int = None) -> Optional[PaymentReceipt]:
        """Get receipt by receipt number."""
        query = self.db.query(PaymentReceipt).filter(PaymentReceipt.receipt_number == receipt_number)
        
        if user_id:
            query = query.filter(PaymentReceipt.user_id == user_id)
        
        return query.first()
    
    def get_user_receipts(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        receipt_type: ReceiptType = None,
        status: ReceiptStatus = None
    ) -> List[PaymentReceipt]:
        """Get receipts for a user."""
        
        query = self.db.query(PaymentReceipt).filter(PaymentReceipt.user_id == user_id)
        
        if receipt_type:
            query = query.filter(PaymentReceipt.receipt_type == receipt_type)
        
        if status:
            query = query.filter(PaymentReceipt.status == status)
        
        return query.order_by(PaymentReceipt.created_at.desc()).offset(offset).limit(limit).all()
    
    def get_all_receipts_for_admin(
        self,
        limit: int = 50,
        offset: int = 0,
        receipt_type: ReceiptType = None,
        status: ReceiptStatus = None,
        user_id: int = None,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> List[PaymentReceipt]:
        """Get all receipts for admin management."""
        
        query = self.db.query(PaymentReceipt)
        
        if receipt_type:
            query = query.filter(PaymentReceipt.receipt_type == receipt_type)
        
        if status:
            query = query.filter(PaymentReceipt.status == status)
        
        if user_id:
            query = query.filter(PaymentReceipt.user_id == user_id)
        
        if date_from:
            query = query.filter(PaymentReceipt.created_at >= date_from)
        
        if date_to:
            query = query.filter(PaymentReceipt.created_at <= date_to)
        
        return query.order_by(PaymentReceipt.created_at.desc()).offset(offset).limit(limit).all()
    
    def admin_review_receipt(
        self,
        receipt_id: int,
        admin_user_id: int,
        notes: str = None,
        approved: bool = True
    ) -> PaymentReceipt:
        """Admin review of receipt."""
        
        receipt = self.get_receipt_by_id(receipt_id)
        if not receipt:
            raise ValueError("Receipt not found")
        
        receipt.admin_review(admin_user_id, notes)
        
        if approved and receipt.status == ReceiptStatus.DRAFT:
            receipt.status = ReceiptStatus.GENERATED
        
        self.db.commit()
        
        # Log admin action
        self.audit_service.log_admin_action(
            admin_id=admin_user_id,
            action_type="RECEIPT_MANAGEMENT",
            action_name="Receipt Review",
            description=f"Reviewed receipt {receipt.receipt_number}",
            target_resource_type="receipt",
            target_resource_id=receipt.id,
            operation_data={
                "approved": approved,
                "notes": notes
            }
        )
        
        return receipt
    
    def update_receipt(
        self,
        receipt_id: int,
        receipt_data: PaymentReceiptUpdate,
        user_id: int = None,
        admin_user_id: int = None
    ) -> Optional[PaymentReceipt]:
        """Update receipt details."""
        
        receipt = self.get_receipt_by_id(receipt_id, user_id)
        if not receipt:
            return None
        
        # Only allow updates to draft receipts
        if receipt.status != ReceiptStatus.DRAFT:
            raise ValueError("Can only update draft receipts")
        
        # Update fields
        update_data = receipt_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(receipt, field):
                setattr(receipt, field, value)
        
        receipt.updated_by = admin_user_id or user_id
        self.db.commit()
        
        # Log audit event
        self.audit_service.log_action(
            action="RECEIPT_UPDATED",
            user_id=admin_user_id or user_id or receipt.user_id,
            description=f"Updated receipt {receipt.receipt_number}",
            resource_type="receipt",
            resource_id=receipt.id,
            metadata={
                "receipt_number": receipt.receipt_number,
                "changes": update_data
            }
        )
        
        return receipt
    
    def delete_receipt(self, receipt_id: int, admin_user_id: int) -> bool:
        """Delete receipt (admin only)."""
        
        receipt = self.get_receipt_by_id(receipt_id)
        if not receipt:
            return False
        
        # Only allow deletion of draft receipts
        if receipt.status != ReceiptStatus.DRAFT:
            raise ValueError("Can only delete draft receipts")
        
        # Delete PDF file if exists
        if receipt.pdf_file_path and os.path.exists(receipt.pdf_file_path):
            os.remove(receipt.pdf_file_path)
        
        # Log before deletion
        self.audit_service.log_admin_action(
            admin_id=admin_user_id,
            action_type="RECEIPT_MANAGEMENT",
            action_name="Receipt Deletion",
            description=f"Deleted receipt {receipt.receipt_number}",
            target_resource_type="receipt",
            target_resource_id=receipt.id
        )
        
        self.db.delete(receipt)
        self.db.commit()
        
        return True
    
    def _generate_receipt_number(self) -> str:
        """Generate unique receipt number."""
        
        # Get current year and month
        now = datetime.now()
        year_month = now.strftime("%Y%m")
        
        # Get the last receipt number for this month
        last_receipt = self.db.query(PaymentReceipt).filter(
            PaymentReceipt.receipt_number.like(f"{year_month}%")
        ).order_by(PaymentReceipt.receipt_number.desc()).first()
        
        if last_receipt:
            # Extract sequence number and increment
            last_sequence = int(last_receipt.receipt_number[-4:])
            sequence = last_sequence + 1
        else:
            sequence = 1
        
        return f"{year_month}{sequence:04d}"
    
    def _generate_secure_download_token(
        self, 
        user_id: int, 
        receipt_id: int
    ) -> SecureDownloadToken:
        """Generate secure download token for receipt PDF."""
        
        # Generate token
        token_plain = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token_plain.encode()).hexdigest()
        
        # Create token record
        download_token = SecureDownloadToken(
            user_id=user_id,
            receipt_id=receipt_id,
            token_hash=token_hash,
            token_plain=token_plain,
            expires_at=datetime.utcnow() + timedelta(hours=24),  # 24 hour expiry
            max_downloads=5
        )
        
        self.db.add(download_token)
        self.db.commit()
        
        return download_token
    
    def _format_address(self, company_profile: CompanyProfile) -> str:
        """Format company address."""
        if not company_profile:
            return None
        
        address_parts = []
        if company_profile.address:
            address_parts.append(company_profile.address)
        if company_profile.city:
            address_parts.append(company_profile.city)
        if company_profile.state:
            address_parts.append(company_profile.state)
        if company_profile.postal_code:
            address_parts.append(company_profile.postal_code)
        
        return ", ".join(address_parts) if address_parts else None
    
    def _format_invoice_client_address(self, invoice: Invoice) -> str:
        """Format invoice client address."""
        address_parts = []
        if invoice.client_address_line1:
            address_parts.append(invoice.client_address_line1)
        if invoice.client_address_line2:
            address_parts.append(invoice.client_address_line2)
        if invoice.client_city:
            address_parts.append(invoice.client_city)
        if invoice.client_state:
            address_parts.append(invoice.client_state)
        if invoice.client_postal_code:
            address_parts.append(invoice.client_postal_code)
        
        return ", ".join(address_parts) if address_parts else None
    
    def _get_company_address(self) -> str:
        """Get company address from settings."""
        # This should be configurable in settings
        return "123 Business Street, Business City, State 12345, India"
    
    def _get_company_gstin(self) -> str:
        """Get company GSTIN from settings."""
        # This should be configurable in settings
        return "22AAAAA0000A1Z5"
    
    def _get_company_pan(self) -> str:
        """Get company PAN from settings."""
        # This should be configurable in settings
        return "AAAAA0000A"