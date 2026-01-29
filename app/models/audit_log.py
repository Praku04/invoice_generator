"""Audit log model for tracking user and admin actions."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class AuditAction(str, enum.Enum):
    """Audit action enumeration."""
    # User actions
    USER_SIGNUP = "user_signup"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_EMAIL_VERIFIED = "user_email_verified"
    USER_PASSWORD_CHANGED = "user_password_changed"
    USER_PASSWORD_RESET_REQUESTED = "user_password_reset_requested"
    USER_PASSWORD_RESET_COMPLETED = "user_password_reset_completed"
    USER_PROFILE_UPDATED = "user_profile_updated"
    
    # Invoice actions
    INVOICE_CREATED = "invoice_created"
    INVOICE_UPDATED = "invoice_updated"
    INVOICE_FINALIZED = "invoice_finalized"
    INVOICE_SENT = "invoice_sent"
    INVOICE_PAID = "invoice_paid"
    INVOICE_CANCELLED = "invoice_cancelled"
    INVOICE_DELETED = "invoice_deleted"
    INVOICE_PDF_DOWNLOADED = "invoice_pdf_downloaded"
    
    # Subscription actions
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_ACTIVATED = "subscription_activated"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    
    # Payment actions
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_REFUNDED = "payment_refunded"
    
    # Admin actions
    ADMIN_USER_VIEWED = "admin_user_viewed"
    ADMIN_USER_DEACTIVATED = "admin_user_deactivated"
    ADMIN_USER_ACTIVATED = "admin_user_activated"
    ADMIN_USER_PASSWORD_RESET = "admin_user_password_reset"
    ADMIN_USER_FORCE_LOGOUT = "admin_user_force_logout"
    ADMIN_SUBSCRIPTION_MODIFIED = "admin_subscription_modified"
    ADMIN_INVOICE_VIEWED = "admin_invoice_viewed"
    ADMIN_REVENUE_VIEWED = "admin_revenue_viewed"
    ADMIN_ANALYTICS_VIEWED = "admin_analytics_viewed"


class AuditLog(Base):
    """Audit log model for tracking user and admin actions."""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Actor (who performed the action)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Action details
    action = Column(Enum(AuditAction), nullable=False)
    description = Column(String(500), nullable=True)
    
    # Resource affected
    resource_type = Column(String(50), nullable=True)  # user, invoice, subscription, payment
    resource_id = Column(Integer, nullable=True)
    
    # Request details
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    request_path = Column(String(500), nullable=True)
    
    # Additional data
    extra_data = Column(Text, nullable=True)  # JSON string for additional data
    
    # Success/failure
    success = Column(String(10), default="success")  # success, failure, error
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="audit_logs")
    admin = relationship("User", foreign_keys=[admin_id])
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id}, resource_type='{self.resource_type}')>"