"""Subscription schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.subscription import SubscriptionStatus


class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription."""
    plan_id: int


class SubscriptionResponse(BaseModel):
    """Schema for subscription response."""
    id: int
    user_id: int
    plan_id: int
    status: SubscriptionStatus
    razorpay_subscription_id: Optional[str]
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    is_trial: bool
    created_at: datetime
    
    class Config:
        from_attributes = True