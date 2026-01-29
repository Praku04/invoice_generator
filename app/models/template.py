"""Template model for managing invoice and receipt templates."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import os

from app.database import Base


class TemplateCategory(str, enum.Enum):
    """Template category enumeration."""
    INVOICE = "invoice"
    RECEIPT = "receipt"


class Template(Base):
    """Template model for invoice and receipt templates."""
    
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Template identification
    template_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(Enum(TemplateCategory), nullable=False)
    
    # Template description and metadata
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0.0")
    author = Column(String(100), nullable=True)
    
    # File paths
    html_file = Column(String(255), nullable=False)
    css_file = Column(String(255), nullable=False)
    preview_image = Column(String(255), nullable=True)
    
    # Template configuration
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    
    # Template features and capabilities
    features = Column(Text, nullable=True)  # JSON string
    supports_logo = Column(Boolean, default=True)
    supports_signature = Column(Boolean, default=True)
    supports_watermark = Column(Boolean, default=False)
    
    # PDF configuration
    page_size = Column(String(10), default="A4")
    orientation = Column(String(10), default="portrait")
    margins = Column(String(100), default="1cm")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_preferences = relationship("UserTemplatePreference", back_populates="template")
    invoices = relationship("Invoice", back_populates="template")
    receipts = relationship("PaymentReceipt", back_populates="template")
    
    @property
    def template_path(self) -> str:
        """Get the full path to template directory."""
        return os.path.join("app", "templates", "pdf", self.category.value + "s", self.template_id)
    
    @property
    def html_path(self) -> str:
        """Get the full path to HTML template file."""
        return os.path.join(self.template_path, self.html_file)
    
    @property
    def css_path(self) -> str:
        """Get the full path to CSS template file."""
        return os.path.join(self.template_path, self.css_file)
    
    @property
    def preview_path(self) -> str:
        """Get the full path to preview image."""
        if self.preview_image:
            return os.path.join(self.template_path, self.preview_image)
        return None
    
    @property
    def is_available(self) -> bool:
        """Check if template files exist and are available."""
        return (
            self.is_active and 
            os.path.exists(self.html_path) and 
            os.path.exists(self.css_path)
        )
    
    def get_features_list(self) -> list:
        """Get template features as a list."""
        if self.features:
            import json
            try:
                return json.loads(self.features)
            except:
                return []
        return []
    
    def __repr__(self):
        return f"<Template(id={self.id}, template_id='{self.template_id}', name='{self.name}', category='{self.category}')>"


class UserTemplatePreference(Base):
    """User template preferences for default templates."""
    
    __tablename__ = "user_template_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    template_id = Column(Integer, nullable=False)
    category = Column(Enum(TemplateCategory), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    template = relationship("Template", back_populates="user_preferences")
    
    def __repr__(self):
        return f"<UserTemplatePreference(user_id={self.user_id}, template_id={self.template_id}, category='{self.category}')>"