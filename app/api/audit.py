"""Audit API endpoints for admin users."""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_admin_user
from app.models.user import User
from app.models.audit_log import AuditLog, AuditAction
from app.models.admin_action import AdminAction, AdminActionType
from app.services.audit_service import AuditService
from app.schemas.audit import (
    AuditLogResponse,
    AdminActionResponse,
    AuditLogListResponse,
    AdminActionListResponse,
    SecurityEventResponse
)

router = APIRouter()


@router.get("/logs", response_model=AuditLogListResponse)
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    action: Optional[AuditAction] = Query(None),
    resource_type: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get audit logs with filtering options (admin only)."""
    
    audit_service = AuditService(db)
    
    if user_id:
        # Get logs for specific user
        logs = audit_service.get_user_audit_logs(
            user_id=user_id,
            limit=limit,
            offset=skip,
            action_filter=[action] if action else None,
            date_from=date_from,
            date_to=date_to
        )
    else:
        # Get all logs with filters
        query = db.query(AuditLog)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if date_from:
            query = query.filter(AuditLog.created_at >= date_from)
        
        if date_to:
            query = query.filter(AuditLog.created_at <= date_to)
        
        logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return AuditLogListResponse(
        logs=[AuditLogResponse.from_orm(log) for log in logs],
        total_count=len(logs),
        has_more=len(logs) == limit
    )


@router.get("/admin-actions", response_model=AdminActionListResponse)
def get_admin_actions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin_id: Optional[int] = Query(None),
    action_type: Optional[AdminActionType] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin actions with filtering options (admin only)."""
    
    audit_service = AuditService(db)
    
    actions = audit_service.get_admin_actions(
        admin_id=admin_id,
        action_type=action_type,
        limit=limit,
        offset=skip,
        date_from=date_from,
        date_to=date_to
    )
    
    return AdminActionListResponse(
        actions=[AdminActionResponse.from_orm(action) for action in actions],
        total_count=len(actions),
        has_more=len(actions) == limit
    )


@router.get("/security-events", response_model=List[SecurityEventResponse])
def get_security_events(
    user_id: Optional[int] = Query(None),
    ip_address: Optional[str] = Query(None),
    hours_back: int = Query(24, ge=1, le=168),  # Max 1 week
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get security-related events (admin only)."""
    
    audit_service = AuditService(db)
    
    events = audit_service.get_security_events(
        user_id=user_id,
        ip_address=ip_address,
        limit=limit,
        hours_back=hours_back
    )
    
    return [SecurityEventResponse.from_orm(event) for event in events]


@router.get("/user/{user_id}/logs", response_model=AuditLogListResponse)
def get_user_audit_logs(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action: Optional[AuditAction] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get audit logs for a specific user (admin only)."""
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    audit_service = AuditService(db)
    
    logs = audit_service.get_user_audit_logs(
        user_id=user_id,
        limit=limit,
        offset=skip,
        action_filter=[action] if action else None,
        date_from=date_from,
        date_to=date_to
    )
    
    return AuditLogListResponse(
        logs=[AuditLogResponse.from_orm(log) for log in logs],
        total_count=len(logs),
        has_more=len(logs) == limit
    )


@router.get("/resource/{resource_type}/{resource_id}/logs", response_model=AuditLogListResponse)
def get_resource_audit_logs(
    resource_type: str,
    resource_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get audit logs for a specific resource (admin only)."""
    
    audit_service = AuditService(db)
    
    logs = audit_service.get_resource_audit_logs(
        resource_type=resource_type,
        resource_id=resource_id,
        limit=limit,
        offset=skip
    )
    
    return AuditLogListResponse(
        logs=[AuditLogResponse.from_orm(log) for log in logs],
        total_count=len(logs),
        has_more=len(logs) == limit
    )


@router.delete("/cleanup")
def cleanup_old_logs(
    days: int = Query(365, ge=30, le=1095),  # Min 30 days, max 3 years
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Clean up old audit logs (admin only)."""
    
    audit_service = AuditService(db)
    
    # Log the cleanup action
    audit_service.log_admin_action(
        admin_id=current_admin.id,
        action_type=AdminActionType.SYSTEM_CONFIGURATION,
        action_name="Audit Log Cleanup",
        description=f"Cleaned up audit logs older than {days} days",
        operation_data={"days": days}
    )
    
    deleted_count = audit_service.cleanup_old_logs(days=days)
    
    return {
        "message": f"Cleaned up {deleted_count} old audit log entries",
        "deleted_count": deleted_count,
        "cutoff_days": days
    }