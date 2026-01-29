"""Invoice settings schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InvoiceSettingsBase(BaseModel):
    """Base invoice settings schema."""
    invoice_title: str = Field(default="Invoice", max_length=100)
    invoice_prefix: str = Field(default="INV", max_length=20)
    invoice_number_format: str = Field(default="{prefix}-{number:04d}", max_length=50)
    currency: str = Field(default="INR", max_length=3)
    currency_symbol: str = Field(default="₹", max_length=5)
    decimal_places: int = Field(default=2, ge=0, le=4)
    show_logo: bool = Field(default=True)
    show_stamp: bool = Field(default=True)
    show_gst_breakdown: bool = Field(default=True)
    show_hsn_code: bool = Field(default=False)
    default_notes: Optional[str] = Field(None, max_length=500)
    default_terms: Optional[str] = Field(None, max_length=500)
    footer_message: Optional[str] = Field(None, max_length=200)
    default_due_days: int = Field(default=30, ge=0, le=365)


class InvoiceSettingsCreate(InvoiceSettingsBase):
    """Schema for creating invoice settings."""
    pass


class InvoiceSettingsUpdate(BaseModel):
    """Schema for updating invoice settings."""
    invoice_title: Optional[str] = Field(None, max_length=100)
    invoice_prefix: Optional[str] = Field(None, max_length=20)
    invoice_number_format: Optional[str] = Field(None, max_length=50)
    currency: Optional[str] = Field(None, max_length=3)
    currency_symbol: Optional[str] = Field(None, max_length=5)
    decimal_places: Optional[int] = Field(None, ge=0, le=4)
    show_logo: Optional[bool] = None
    show_stamp: Optional[bool] = None
    show_gst_breakdown: Optional[bool] = None
    show_hsn_code: Optional[bool] = None
    default_notes: Optional[str] = Field(None, max_length=500)
    default_terms: Optional[str] = Field(None, max_length=500)
    footer_message: Optional[str] = Field(None, max_length=200)
    default_due_days: Optional[int] = Field(None, ge=0, le=365)


class InvoiceSettingsResponse(InvoiceSettingsBase):
    """Schema for invoice settings response."""
    id: int
    user_id: int
    next_invoice_number: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True