"""Company profile model for invoice customization."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from app.database import Base


class CompanyProfile(Base):
    """Company profile model for invoice customization."""
    
    __tablename__ = "company_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    company_name = Column(String(255), nullable=False)
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="India")
    gstin = Column(String(15), nullable=True)
    pan = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    logo_file_id = Column(Integer, ForeignKey("file_assets.id"), nullable=True)
    stamp_file_id = Column(Integer, ForeignKey("file_assets.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="company_profile")
    logo_file = relationship("FileAsset", foreign_keys=[logo_file_id])
    stamp_file = relationship("FileAsset", foreign_keys=[stamp_file_id])
    
    def __repr__(self):
        return f"<CompanyProfile(id={self.id}, company_name='{self.company_name}')>"