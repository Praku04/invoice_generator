"""Notification model for user notifications."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class NotificationType(str, enum.Enum):
    """Notification type enumeration."""
    INVOICE_FINALIZED = "invoice_finalized"
    INVOICE_SENT = "invoice_sent"
    INVOICE_PAID = "invoice_paid"
    SUBSCRIPTION_ACTIVATED = "subscription_activated"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"
    ACCOUNT_ACTIVITY = "account_activity"
    ADMIN_MESSAGE = "admin_message"


class NotificationStatus(str, enum.Enum):
    """Notification status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class Notification(Base):
    """Notification model for user notifications."""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    
    # Notification content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Related resource
    resource_type = Column(String(50), nullable=True)  # invoice, subscription, payment
    resource_id = Column(Integer, nullable=True)
    
    # Email details
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    
    # Read status
    read_at = Column(DateTime, nullable=True)
    
    # Additional data
    extra_data = Column(Text, nullable=True)  # JSON string for additional data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.type}', status='{self.status}')>"