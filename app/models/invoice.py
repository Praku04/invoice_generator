"""Invoice model for invoice management."""

from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from decimal import Decimal as PyDecimal

from app.database import Base


class InvoiceStatus(str, enum.Enum):
    """Invoice status enumeration."""
    DRAFT = "draft"
    FINALIZED = "finalized"
    SENT = "sent"
    PAID = "paid"
    CANCELLED = "cancelled"


class Invoice(Base):
    """Invoice model for managing invoices."""
    
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Invoice identification
    invoice_number = Column(String(50), nullable=False)
    invoice_title = Column(String(100), default="Invoice")
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Dates
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    
    # Client information
    client_name = Column(String(255), nullable=False)
    client_email = Column(String(255), nullable=True)
    client_phone = Column(String(20), nullable=True)
    client_address_line1 = Column(String(255), nullable=True)
    client_address_line2 = Column(String(255), nullable=True)
    client_city = Column(String(100), nullable=True)
    client_state = Column(String(100), nullable=True)
    client_postal_code = Column(String(20), nullable=True)
    client_country = Column(String(100), default="India")
    client_gstin = Column(String(15), nullable=True)
    
    # Financial calculations
    subtotal = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    discount_amount = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    discount_percentage = Column(Numeric(5, 2), default=PyDecimal('0.00'))
    taxable_amount = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    cgst_amount = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    sgst_amount = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    igst_amount = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    total_tax = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    round_off = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    grand_total = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    
    # Currency
    currency = Column(String(3), default="INR")
    currency_symbol = Column(String(5), default="₹")
    
    # Additional information
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    footer_message = Column(String(200), nullable=True)
    
    # PDF and file management
    pdf_generated = Column(Boolean, default=False)
    pdf_file_path = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Template
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    secure_download_tokens = relationship("SecureDownloadToken", back_populates="invoice")
    payment_receipts = relationship("PaymentReceipt", back_populates="invoice")
    template = relationship("Template", back_populates="invoices")
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', status='{self.status}')>"