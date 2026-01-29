"""File asset schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FileAssetResponse(BaseModel):
    """Schema for file asset response."""
    id: int
    user_id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    file_extension: str
    file_type: str
    is_active: bool
    width: Optional[int]
    height: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True