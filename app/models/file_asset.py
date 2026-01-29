"""File asset model for managing uploaded files."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class FileAsset(Base):
    """File asset model for managing uploaded files like logos and stamps."""
    
    __tablename__ = "file_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_extension = Column(String(10), nullable=False)
    
    # File metadata
    file_type = Column(String(50), nullable=False)  # logo, stamp, document
    is_active = Column(Boolean, default=True)
    
    # Image specific (if applicable)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="file_assets")
    
    def __repr__(self):
        return f"<FileAsset(id={self.id}, filename='{self.filename}', type='{self.file_type}')>"