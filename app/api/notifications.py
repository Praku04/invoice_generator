"""Notifications API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.notification import Notification, NotificationType
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationResponse,
    NotificationCreate,
    NotificationUpdate,
    NotificationListResponse
)

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications with pagination."""
    
    notification_service = NotificationService(db)
    
    notifications = notification_service.get_user_notifications(
        user_id=current_user.id,
        limit=limit,
        offset=skip,
        unread_only=unread_only
    )
    
    unread_count = notification_service.get_unread_count(current_user.id)
    
    return NotificationListResponse(
        notifications=[NotificationResponse.from_orm(n) for n in notifications],
        total_count=len(notifications),
        unread_count=unread_count,
        has_more=len(notifications) == limit
    )


@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications."""
    
    notification_service = NotificationService(db)
    count = notification_service.get_unread_count(current_user.id)
    
    return {"unread_count": count}


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read."""
    
    notification_service = NotificationService(db)
    
    notification = notification_service.mark_notification_as_read(
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return NotificationResponse.from_orm(notification)


@router.put("/mark-all-read")
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for the current user."""
    
    notification_service = NotificationService(db)
    count = notification_service.mark_all_notifications_as_read(current_user.id)
    
    return {"marked_as_read": count}


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific notification."""
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return NotificationResponse.from_orm(notification)


@router.post("/test", response_model=NotificationResponse)
def create_test_notification(
    notification_data: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a test notification (for development/testing)."""
    
    notification_service = NotificationService(db)
    
    notification = notification_service.create_notification(
        user_id=current_user.id,
        notification_type=notification_data.type,
        title=notification_data.title,
        message=notification_data.message,
        resource_type=notification_data.resource_type,
        resource_id=notification_data.resource_id,
        metadata=notification_data.metadata,
        send_email=notification_data.send_email
    )
    
    return NotificationResponse.from_orm(notification)