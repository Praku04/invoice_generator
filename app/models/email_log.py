"""Email log model for tracking sent emails."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class EmailType(str, enum.Enum):
    """Email type enumeration."""
    INVOICE_NOTIFICATION = "invoice_notification"
    SUBSCRIPTION_NOTIFICATION = "subscription_notification"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"
    WELCOME = "welcome"
    ADMIN_MESSAGE = "admin_message"
    PAYMENT_CONFIRMATION = "payment_confirmation"


class EmailStatus(str, enum.Enum):
    """Email status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    BOUNCED = "bounced"
    FAILED = "failed"
    OPENED = "opened"
    CLICKED = "clicked"


class EmailLog(Base):
    """Email log model for tracking sent emails."""
    
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Email details
    to_email = Column(String(255), nullable=False)
    from_email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body_html = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)
    
    # Email type and status
    email_type = Column(Enum(EmailType), nullable=False)
    status = Column(Enum(EmailStatus), default=EmailStatus.PENDING)
    
    # Related resource
    resource_type = Column(String(50), nullable=True)  # invoice, subscription, user
    resource_id = Column(Integer, nullable=True)
    
    # Delivery tracking
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    bounced_at = Column(DateTime, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # External provider tracking
    provider_message_id = Column(String(255), nullable=True)
    provider_response = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="email_logs")
    
    def __repr__(self):
        return f"<EmailLog(id={self.id}, to_email='{self.to_email}', type='{self.email_type}', status='{self.status}')>"