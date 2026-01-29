"""User model for authentication and user management."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """User model for authentication and profile management."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    verification_token = Column(String(255), nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user")
    company_profile = relationship("CompanyProfile", back_populates="user", uselist=False)
    invoice_settings = relationship("InvoiceSettings", back_populates="user", uselist=False)
    invoices = relationship("Invoice", back_populates="user")
    file_assets = relationship("FileAsset", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    email_logs = relationship("EmailLog", back_populates="user")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")
    audit_logs = relationship("AuditLog", foreign_keys="AuditLog.user_id", back_populates="user")
    admin_actions = relationship("AdminAction", foreign_keys="AdminAction.admin_id", back_populates="admin")
    secure_download_tokens = relationship("SecureDownloadToken", back_populates="user")
    payment_receipts = relationship("PaymentReceipt", foreign_keys="PaymentReceipt.user_id", back_populates="user")
    template_preferences = relationship("UserTemplatePreference", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"