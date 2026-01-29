"""Plan schemas for subscription plans."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PlanResponse(BaseModel):
    """Schema for plan response."""
    id: int
    name: str
    description: Optional[str]
    price: int  # Price in paise
    currency: str
    interval: str
    invoice_limit: Optional[int]
    features: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True