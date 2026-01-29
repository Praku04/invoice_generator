"""Password reset token model for secure password recovery."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta

from app.database import Base


class PasswordResetToken(Base):
    """Password reset token model for secure password recovery."""
    
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Token details
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    token_plain = Column(String(255), nullable=False)  # Store plain token temporarily for email
    
    # Token status
    is_used = Column(Boolean, default=False)
    is_expired = Column(Boolean, default=False)
    
    # Expiry
    expires_at = Column(DateTime, nullable=False)
    
    # Usage tracking
    used_at = Column(DateTime, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="password_reset_tokens")
    
    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not used, not expired)."""
        return not self.is_used and not self.is_expired and datetime.utcnow() < self.expires_at
    
    def mark_as_used(self, ip_address: str = None, user_agent: str = None):
        """Mark token as used."""
        self.is_used = True
        self.used_at = datetime.utcnow()
        if ip_address:
            self.ip_address = ip_address
        if user_agent:
            self.user_agent = user_agent
    
    def mark_as_expired(self):
        """Mark token as expired."""
        self.is_expired = True
    
    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, is_used={self.is_used}, expires_at='{self.expires_at}')>"