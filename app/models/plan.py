"""Subscription plan model."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Plan(Base):
    """Subscription plan model."""
    
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # Price in paise
    currency = Column(String(3), default="INR")
    interval = Column(String(20), default="monthly")  # monthly, yearly
    invoice_limit = Column(Integer, nullable=True)  # NULL for unlimited
    features = Column(Text, nullable=True)  # JSON string of features
    is_active = Column(Boolean, default=True)
    razorpay_plan_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")
    
    def __repr__(self):
        return f"<Plan(id={self.id}, name='{self.name}', price={self.price})>"