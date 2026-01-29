"""Notification schemas for API requests and responses."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.notification import NotificationType, NotificationStatus


class NotificationBase(BaseModel):
    """Base notification schema."""
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    resource_type: Optional[str] = Field(None, max_length=50)
    resource_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    """Schema for creating notifications."""
    send_email: bool = True


class NotificationUpdate(BaseModel):
    """Schema for updating notifications."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class NotificationResponse(NotificationBase):
    """Schema for notification responses."""
    id: int
    user_id: int
    status: NotificationStatus
    email_sent: bool
    email_sent_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    @property
    def is_read(self) -> bool:
        """Check if notification is read."""
        return self.read_at is not None
    
    @property
    def is_unread(self) -> bool:
        """Check if notification is unread."""
        return self.read_at is None
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list responses."""
    notifications: List[NotificationResponse]
    total_count: int
    unread_count: int
    has_more: bool


class NotificationStatsResponse(BaseModel):
    """Schema for notification statistics."""
    total_notifications: int
    unread_count: int
    read_count: int
    notifications_by_type: Dict[str, int]
    recent_notifications: List[NotificationResponse]