"""Invoice item model for line items in invoices."""

from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from decimal import Decimal as PyDecimal

from app.database import Base


class InvoiceItem(Base):
    """Invoice item model for line items."""
    
    __tablename__ = "invoice_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    # Item details
    item_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    hsn_code = Column(String(20), nullable=True)
    
    # Quantities and rates
    quantity = Column(Numeric(10, 3), nullable=False, default=PyDecimal('1.000'))
    unit = Column(String(20), default="Nos")
    rate = Column(Numeric(15, 2), nullable=False, default=PyDecimal('0.00'))
    
    # Discounts
    discount_amount = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    discount_percentage = Column(Numeric(5, 2), default=PyDecimal('0.00'))
    
    # Tax information
    gst_rate = Column(Numeric(5, 2), default=PyDecimal('0.00'))
    cgst_rate = Column(Numeric(5, 2), default=PyDecimal('0.00'))
    sgst_rate = Column(Numeric(5, 2), default=PyDecimal('0.00'))
    igst_rate = Column(Numeric(5, 2), default=PyDecimal('0.00'))
    
    # Calculated amounts
    line_total = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    taxable_amount = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    cgst_amount = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    sgst_amount = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    igst_amount = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    total_amount = Column(Numeric(15, 2), default=PyDecimal('0.00'))
    
    # Ordering
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    
    def __repr__(self):
        return f"<InvoiceItem(id={self.id}, name='{self.item_name}', amount={self.total_amount})>"