"""Payment model for tracking subscription payments."""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from decimal import Decimal as PyDecimal

from app.database import Base


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration."""
    CARD = "card"
    UPI = "upi"
    NETBANKING = "netbanking"
    WALLET = "wallet"
    EMI = "emi"


class Payment(Base):
    """Payment model for tracking subscription payments."""
    
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    
    # Razorpay identifiers
    razorpay_payment_id = Column(String(100), nullable=True)
    razorpay_order_id = Column(String(100), nullable=True)
    razorpay_signature = Column(String(255), nullable=True)
    
    # Payment details
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="INR")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    method = Column(Enum(PaymentMethod), nullable=True)
    
    # Payment metadata
    description = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    failure_reason = Column(String(255), nullable=True)
    
    # Timestamps
    payment_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subscription = relationship("Subscription", back_populates="payments")
    receipt = relationship("PaymentReceipt", back_populates="payment", uselist=False)
    receipt = relationship("PaymentReceipt", back_populates="payment", uselist=False)
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status='{self.status}')>"