"""Payment receipt schemas for API requests and responses."""

from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator

from app.models.payment_receipt import ReceiptStatus, ReceiptType


class PaymentReceiptBase(BaseModel):
    """Base payment receipt schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    notes: Optional[str] = None
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: str = Field(..., min_length=1, max_length=255)
    customer_phone: Optional[str] = Field(None, max_length=20)
    customer_address: Optional[str] = None
    customer_gstin: Optional[str] = Field(None, max_length=20)


class PaymentReceiptCreate(PaymentReceiptBase):
    """Schema for creating payment receipts."""
    receipt_type: ReceiptType
    payment_id: Optional[int] = None
    subscription_id: Optional[int] = None
    invoice_id: Optional[int] = None
    amount: Decimal = Field(..., gt=0)
    tax_amount: Decimal = Field(default=Decimal('0.00'), ge=0)
    total_amount: Decimal = Field(..., gt=0)
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    
    @validator('total_amount')
    def validate_total_amount(cls, v, values):
        """Validate that total amount equals amount + tax_amount."""
        amount = values.get('amount', Decimal('0'))
        tax_amount = values.get('tax_amount', Decimal('0'))
        expected_total = amount + tax_amount
        
        if abs(v - expected_total) > Decimal('0.01'):  # Allow small rounding differences
            raise ValueError('Total amount must equal amount + tax_amount')
        
        return v


class PaymentReceiptUpdate(BaseModel):
    """Schema for updating payment receipts."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    notes: Optional[str] = None
    customer_name: Optional[str] = Field(None, min_length=1, max_length=255)
    customer_email: Optional[str] = Field(None, min_length=1, max_length=255)
    customer_phone: Optional[str] = Field(None, max_length=20)
    customer_address: Optional[str] = None
    customer_gstin: Optional[str] = Field(None, max_length=20)
    admin_notes: Optional[str] = None


class PaymentReceiptResponse(PaymentReceiptBase):
    """Schema for payment receipt responses."""
    id: int
    receipt_number: str
    receipt_type: ReceiptType
    status: ReceiptStatus
    user_id: int
    payment_id: Optional[int]
    subscription_id: Optional[int]
    invoice_id: Optional[int]
    
    # Financial details
    amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    currency_symbol: str
    
    # Payment details
    payment_method: Optional[str]
    transaction_id: Optional[str]
    razorpay_payment_id: Optional[str]
    
    # Dates
    receipt_date: datetime
    payment_date: Optional[datetime]
    
    # Company details
    company_name: Optional[str]
    company_address: Optional[str]
    company_gstin: Optional[str]
    company_pan: Optional[str]
    
    # PDF and email status
    pdf_generated: bool
    pdf_generated_at: Optional[datetime]
    email_sent: bool
    email_sent_at: Optional[datetime]
    email_sent_to: Optional[str]
    
    # Admin management
    admin_notes: Optional[str]
    admin_reviewed: bool
    admin_reviewed_by: Optional[int]
    admin_reviewed_at: Optional[datetime]
    
    # Audit fields
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed properties
    @property
    def formatted_receipt_number(self) -> str:
        return f"RCP-{self.receipt_number}"
    
    @property
    def is_pdf_available(self) -> bool:
        return self.pdf_generated
    
    @property
    def display_amount(self) -> str:
        return f"{self.currency_symbol}{self.total_amount:,.2f}"
    
    class Config:
        from_attributes = True


class PaymentReceiptListResponse(BaseModel):
    """Schema for paginated payment receipt list responses."""
    receipts: List[PaymentReceiptResponse]
    total_count: int
    has_more: bool


class PaymentReceiptStatsResponse(BaseModel):
    """Schema for payment receipt statistics."""
    total_receipts: int
    receipts_by_type: dict
    receipts_by_status: dict
    total_amount: Decimal
    recent_receipts: List[PaymentReceiptResponse]


class AdminReceiptReviewRequest(BaseModel):
    """Schema for admin receipt review."""
    notes: Optional[str] = None
    approved: bool = True


class ReceiptEmailRequest(BaseModel):
    """Schema for sending receipt via email."""
    to_email: Optional[str] = None
    include_pdf: bool = True
    custom_message: Optional[str] = None


class ReceiptDownloadResponse(BaseModel):
    """Schema for receipt download response."""
    download_url: str
    expires_at: datetime
    max_downloads: int
    current_downloads: int