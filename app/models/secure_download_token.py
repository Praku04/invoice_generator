"""Secure download token model for time-bound invoice PDF downloads."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta

from app.database import Base


class SecureDownloadToken(Base):
    """Secure download token model for time-bound invoice PDF downloads."""
    
    __tablename__ = "secure_download_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    receipt_id = Column(Integer, ForeignKey("payment_receipts.id"), nullable=True)
    
    # Token details
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    token_plain = Column(String(255), nullable=False)  # Store plain token temporarily
    
    # Token configuration
    expires_at = Column(DateTime, nullable=False)
    max_downloads = Column(Integer, default=5)
    download_count = Column(Integer, default=0)
    
    # Token status
    is_active = Column(Boolean, default=True)
    is_used = Column(Boolean, default=False)
    
    # Access tracking
    first_accessed_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, nullable=True)
    ip_addresses = Column(String(500), nullable=True)  # Comma-separated list
    user_agents = Column(String(1000), nullable=True)  # JSON array
    
    # Email context
    sent_to_email = Column(String(255), nullable=True)
    email_log_id = Column(Integer, ForeignKey("email_logs.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="secure_download_tokens")
    invoice = relationship("Invoice", back_populates="secure_download_tokens")
    receipt = relationship("PaymentReceipt", back_populates="secure_download_tokens")
    email_log = relationship("EmailLog")
    
    @property
    def is_valid(self) -> bool:
        """Check if token is valid for download."""
        return (
            self.is_active and 
            not self.is_used and 
            datetime.utcnow() < self.expires_at and 
            self.download_count < self.max_downloads
        )
    
    def record_download(self, ip_address: str = None, user_agent: str = None):
        """Record a download attempt."""
        self.download_count += 1
        self.last_accessed_at = datetime.utcnow()
        
        if not self.first_accessed_at:
            self.first_accessed_at = datetime.utcnow()
        
        # Track IP addresses
        if ip_address:
            if self.ip_addresses:
                ips = set(self.ip_addresses.split(','))
                ips.add(ip_address)
                self.ip_addresses = ','.join(ips)
            else:
                self.ip_addresses = ip_address
        
        # Check if max downloads reached
        if self.download_count >= self.max_downloads:
            self.is_used = True
    
    def deactivate(self):
        """Deactivate the token."""
        self.is_active = False
        self.is_used = True
    
    def __repr__(self):
        return f"<SecureDownloadToken(id={self.id}, invoice_id={self.invoice_id}, download_count={self.download_count}, expires_at='{self.expires_at}')>"