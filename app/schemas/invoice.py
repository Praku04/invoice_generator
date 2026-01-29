"""Invoice schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

from app.models.invoice import InvoiceStatus
from .invoice_item import InvoiceItemResponse, InvoiceItemCreate


class InvoiceBase(BaseModel):
    """Base invoice schema."""
    invoice_title: str = Field(default="Invoice", max_length=100)
    client_name: str = Field(..., min_length=2, max_length=255)
    client_email: Optional[str] = Field(None, max_length=255)
    client_phone: Optional[str] = Field(None, max_length=20)
    client_address_line1: Optional[str] = Field(None, max_length=255)
    client_address_line2: Optional[str] = Field(None, max_length=255)
    client_city: Optional[str] = Field(None, max_length=100)
    client_state: Optional[str] = Field(None, max_length=100)
    client_postal_code: Optional[str] = Field(None, max_length=20)
    client_country: str = Field(default="India", max_length=100)
    client_gstin: Optional[str] = Field(None, max_length=15)
    invoice_date: date
    due_date: Optional[date] = None
    notes: Optional[str] = None
    terms: Optional[str] = None
    footer_message: Optional[str] = Field(None, max_length=200)


class InvoiceCreate(InvoiceBase):
    """Schema for creating an invoice."""
    items: List[InvoiceItemCreate] = []
    discount_percentage: Optional[Decimal] = Field(default=Decimal('0.00'), ge=0, le=100)
    discount_amount: Optional[Decimal] = Field(default=Decimal('0.00'), ge=0)


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice."""
    invoice_title: Optional[str] = Field(None, max_length=100)
    client_name: Optional[str] = Field(None, min_length=2, max_length=255)
    client_email: Optional[str] = Field(None, max_length=255)
    client_phone: Optional[str] = Field(None, max_length=20)
    client_address_line1: Optional[str] = Field(None, max_length=255)
    client_address_line2: Optional[str] = Field(None, max_length=255)
    client_city: Optional[str] = Field(None, max_length=100)
    client_state: Optional[str] = Field(None, max_length=100)
    client_postal_code: Optional[str] = Field(None, max_length=20)
    client_country: Optional[str] = Field(None, max_length=100)
    client_gstin: Optional[str] = Field(None, max_length=15)
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None
    terms: Optional[str] = None
    footer_message: Optional[str] = Field(None, max_length=200)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    status: Optional[InvoiceStatus] = None


class InvoiceResponse(InvoiceBase):
    """Schema for invoice response."""
    id: int
    user_id: int
    invoice_number: str
    status: InvoiceStatus
    subtotal: Decimal
    discount_amount: Decimal
    discount_percentage: Decimal
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_tax: Decimal
    round_off: Decimal
    grand_total: Decimal
    currency: str
    currency_symbol: str
    pdf_generated: bool
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[InvoiceItemResponse] = []
    
    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    """Schema for invoice list response."""
    id: int
    invoice_number: str
    invoice_title: str
    client_name: str
    status: InvoiceStatus
    invoice_date: date
    due_date: Optional[date]
    grand_total: Decimal
    currency_symbol: str
    created_at: datetime
    
    class Config:
        from_attributes = True