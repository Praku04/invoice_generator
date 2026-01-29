"""Invoice item schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class InvoiceItemBase(BaseModel):
    """Base invoice item schema."""
    item_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    hsn_code: Optional[str] = Field(None, max_length=20)
    quantity: Decimal = Field(..., gt=0)
    unit: str = Field(default="Nos", max_length=20)
    rate: Decimal = Field(..., ge=0)
    discount_amount: Optional[Decimal] = Field(default=Decimal('0.00'), ge=0)
    discount_percentage: Optional[Decimal] = Field(default=Decimal('0.00'), ge=0, le=100)
    gst_rate: Decimal = Field(default=Decimal('0.00'), ge=0, le=100)


class InvoiceItemCreate(InvoiceItemBase):
    """Schema for creating an invoice item."""
    pass


class InvoiceItemUpdate(BaseModel):
    """Schema for updating an invoice item."""
    item_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    hsn_code: Optional[str] = Field(None, max_length=20)
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=20)
    rate: Optional[Decimal] = Field(None, ge=0)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    gst_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    sort_order: Optional[int] = None


class InvoiceItemResponse(InvoiceItemBase):
    """Schema for invoice item response."""
    id: int
    invoice_id: int
    cgst_rate: Decimal
    sgst_rate: Decimal
    igst_rate: Decimal
    line_total: Decimal
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_amount: Decimal
    sort_order: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True