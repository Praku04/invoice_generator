"""Payment schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.models.payment import PaymentStatus, PaymentMethod


class PaymentResponse(BaseModel):
    """Schema for payment response."""
    id: int
    subscription_id: int
    razorpay_payment_id: Optional[str]
    razorpay_order_id: Optional[str]
    amount: Decimal
    currency: str
    status: PaymentStatus
    method: Optional[PaymentMethod]
    description: Optional[str]
    payment_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True