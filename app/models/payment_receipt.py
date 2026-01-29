"""Payment receipt model for storing receipt data and metadata."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database import Base


class ReceiptType(str, enum.Enum):
    """Enum for receipt types."""
    SUBSCRIPTION_PAYMENT = "SUBSCRIPTION_PAYMENT"
    INVOICE_PAYMENT = "INVOICE_PAYMENT"
    REFUND = "REFUND"
    ADJUSTMENT = "ADJUSTMENT"


class ReceiptStatus(str, enum.Enum):
    """Enum for receipt status."""
    DRAFT = "DRAFT"
    GENERATED = "GENERATED"
    SENT = "SENT"
    VIEWED = "VIEWED"


class PaymentReceipt(Base):
    """Payment receipt model."""
    
    __tablename__ = "payment_receipts"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Receipt identification
    receipt_number = Column(String(50), nullable=False, unique=True, index=True)
    receipt_type = Column(Enum(ReceiptType), nullable=False)
    status = Column(Enum(ReceiptStatus), default=ReceiptStatus.DRAFT)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    
    # Dates
    receipt_date = Column(DateTime, nullable=False, default=func.now())
    payment_date = Column(DateTime, nullable=True)
    
    # Financial details
    amount = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), default=0.00)
    total_amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="INR")
    currency_symbol = Column(String(5), default="₹")
    
    # Payment details
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    razorpay_payment_id = Column(String(100), nullable=True)
    
    # Receipt content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Customer details
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(20), nullable=True)
    customer_address = Column(Text, nullable=True)
    customer_gstin = Column(String(20), nullable=True)
    
    # Company details
    company_name = Column(String(255), nullable=True)
    company_address = Column(Text, nullable=True)
    company_gstin = Column(String(20), nullable=True)
    company_pan = Column(String(20), nullable=True)
    
    # PDF generation
    pdf_generated = Column(Boolean, default=False)
    pdf_file_path = Column(String(500), nullable=True)
    pdf_generated_at = Column(DateTime, nullable=True)
    
    # Email tracking
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    email_sent_to = Column(String(255), nullable=True)
    
    # Admin management
    admin_notes = Column(Text, nullable=True)
    admin_reviewed = Column(Boolean, default=False)
    admin_reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    admin_reviewed_at = Column(DateTime, nullable=True)
    
    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="payment_receipts")
    payment = relationship("Payment", back_populates="payment_receipts")
    subscription = relationship("Subscription", back_populates="payment_receipts")
    invoice = relationship("Invoice", back_populates="payment_receipts")
    
    # Admin relationships
    admin_reviewer = relationship("User", foreign_keys=[admin_reviewed_by])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    # Secure download tokens
    secure_download_tokens = relationship("SecureDownloadToken", back_populates="receipt")
    
    def __repr__(self):
        return f"<PaymentReceipt(id={self.id}, receipt_number='{self.receipt_number}', type='{self.receipt_type}')>"
    
    @property
    def formatted_receipt_number(self) -> str:
        """Get formatted receipt number."""
        return f"RCP-{self.receipt_number}"
    
    @property
    def is_pdf_available(self) -> bool:
        """Check if PDF is available."""
        return self.pdf_generated and self.pdf_file_path is not None
    
    @property
    def display_amount(self) -> str:
        """Get formatted display amount."""
        return f"{self.currency_symbol}{self.total_amount:,.2f}"