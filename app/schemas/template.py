"""Template schemas for API requests and responses."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.models.template import TemplateCategory


class TemplateBase(BaseModel):
    """Base template schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: TemplateCategory
    is_premium: bool = False
    sort_order: int = 0
    features: Optional[List[str]] = []
    supports_logo: bool = True
    supports_signature: bool = True
    supports_watermark: bool = False
    page_size: str = "A4"
    orientation: str = "portrait"
    margins: str = "1cm"


class TemplateCreateRequest(TemplateBase):
    """Schema for creating templates."""
    template_id: str = Field(..., min_length=1, max_length=50, regex=r'^[a-z0-9_-]+$')
    version: str = "1.0.0"
    author: Optional[str] = None
    
    @validator('template_id')
    def validate_template_id(cls, v):
        """Validate template_id format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('template_id must contain only lowercase letters, numbers, hyphens, and underscores')
        return v


class TemplateUpdateRequest(BaseModel):
    """Schema for updating templates."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None
    sort_order: Optional[int] = None
    features: Optional[List[str]] = None
    supports_logo: Optional[bool] = None
    supports_signature: Optional[bool] = None
    supports_watermark: Optional[bool] = None
    page_size: Optional[str] = None
    orientation: Optional[str] = None
    margins: Optional[str] = None


class TemplateResponse(TemplateBase):
    """Schema for template responses."""
    id: int
    template_id: str
    version: str
    author: Optional[str]
    html_file: str
    css_file: str
    preview_image: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed properties
    @property
    def is_available(self) -> bool:
        return self.is_active
    
    @property
    def preview_url(self) -> Optional[str]:
        if self.preview_image:
            return f"/static/templates/{self.category.value}s/{self.template_id}/{self.preview_image}"
        return None
    
    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """Schema for paginated template list responses."""
    templates: List[TemplateResponse]
    total_count: int
    has_more: bool


class TemplateGalleryItem(BaseModel):
    """Schema for template gallery items."""
    id: int
    template_id: str
    name: str
    description: Optional[str]
    is_premium: bool
    is_default: bool
    features: List[str]
    preview_url: Optional[str]
    supports_logo: bool
    supports_signature: bool
    supports_watermark: bool


class TemplateGalleryResponse(BaseModel):
    """Schema for template gallery responses."""
    category: TemplateCategory
    templates: List[TemplateGalleryItem]
    current_default_id: Optional[int]


class TemplatePreferenceRequest(BaseModel):
    """Schema for setting template preferences."""
    template_id: int
    category: TemplateCategory


class TemplatePreviewRequest(BaseModel):
    """Schema for template preview requests."""
    use_sample_data: bool = True
    custom_data: Optional[Dict[str, Any]] = None


class TemplateStatsResponse(BaseModel):
    """Schema for template statistics."""
    total_templates: int
    templates_by_category: Dict[str, int]
    premium_templates: int
    active_templates: int
    most_popular_templates: List[Dict[str, Any]]


class UserTemplatePreferenceResponse(BaseModel):
    """Schema for user template preference responses."""
    id: int
    user_id: int
    template_id: int
    category: TemplateCategory
    template: TemplateResponse
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True