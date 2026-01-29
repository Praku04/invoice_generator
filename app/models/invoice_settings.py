"""Invoice settings model for customization preferences."""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class InvoiceSettings(Base):
    """Invoice settings model for user customization preferences."""
    
    __tablename__ = "invoice_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Invoice customization
    invoice_title = Column(String(100), default="Invoice")
    invoice_prefix = Column(String(20), default="INV")
    invoice_number_format = Column(String(50), default="{prefix}-{number:04d}")
    next_invoice_number = Column(Integer, default=1)
    
    # Currency and formatting
    currency = Column(String(3), default="INR")
    currency_symbol = Column(String(5), default="₹")
    decimal_places = Column(Integer, default=2)
    
    # Display preferences
    show_logo = Column(Boolean, default=True)
    show_stamp = Column(Boolean, default=True)
    show_gst_breakdown = Column(Boolean, default=True)
    show_hsn_code = Column(Boolean, default=False)
    
    # Default terms and notes
    default_notes = Column(String(500), nullable=True)
    default_terms = Column(String(500), nullable=True)
    footer_message = Column(String(200), nullable=True)
    
    # Payment terms
    default_due_days = Column(Integer, default=30)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="invoice_settings")
    
    def __repr__(self):
        return f"<InvoiceSettings(id={self.id}, user_id={self.user_id})>"