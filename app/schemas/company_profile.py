"""Company profile schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CompanyProfileBase(BaseModel):
    """Base company profile schema."""
    company_name: str = Field(..., min_length=2, max_length=255)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(default="India", max_length=100)
    gstin: Optional[str] = Field(None, max_length=15)
    pan: Optional[str] = Field(None, max_length=10)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)


class CompanyProfileCreate(CompanyProfileBase):
    """Schema for creating company profile."""
    pass


class CompanyProfileUpdate(BaseModel):
    """Schema for updating company profile."""
    company_name: Optional[str] = Field(None, min_length=2, max_length=255)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    gstin: Optional[str] = Field(None, max_length=15)
    pan: Optional[str] = Field(None, max_length=10)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)


class CompanyProfileResponse(CompanyProfileBase):
    """Schema for company profile response."""
    id: int
    user_id: int
    logo_file_id: Optional[int]
    stamp_file_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True