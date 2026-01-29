"""Razorpay webhook event model for tracking webhook events."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func

from app.database import Base


class RazorpayEvent(Base):
    """Razorpay webhook event model for tracking and processing webhooks."""
    
    __tablename__ = "razorpay_events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event identification
    event_id = Column(String(100), unique=True, nullable=False)
    event_type = Column(String(100), nullable=False)
    
    # Event data
    payload = Column(Text, nullable=False)  # JSON payload
    signature = Column(String(255), nullable=False)
    
    # Processing status
    processed = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)
    processing_attempts = Column(Integer, default=0)
    
    # Timestamps
    event_created_at = Column(DateTime, nullable=True)  # Razorpay event timestamp
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<RazorpayEvent(id={self.id}, type='{self.event_type}', processed={self.processed})>"