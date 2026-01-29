"""Audit schemas for API requests and responses."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.audit_log import AuditAction
from app.models.admin_action import AdminActionType


class AuditLogResponse(BaseModel):
    """Schema for audit log responses."""
    id: int
    user_id: Optional[int]
    admin_id: Optional[int]
    action: AuditAction
    description: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_method: Optional[str]
    request_path: Optional[str]
    metadata: Optional[str]  # JSON string
    success: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminActionResponse(BaseModel):
    """Schema for admin action responses."""
    id: int
    admin_id: int
    action_type: AdminActionType
    action_name: str
    description: str
    target_user_id: Optional[int]
    target_resource_type: Optional[str]
    target_resource_id: Optional[int]
    operation_data: Optional[str]  # JSON string
    result_data: Optional[str]  # JSON string
    status: Optional[str]
    error_message: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SecurityEventResponse(BaseModel):
    """Schema for security event responses."""
    id: int
    user_id: Optional[int]
    action: AuditAction
    description: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    success: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list responses."""
    logs: List[AuditLogResponse]
    total_count: int
    has_more: bool


class AdminActionListResponse(BaseModel):
    """Schema for paginated admin action list responses."""
    actions: List[AdminActionResponse]
    total_count: int
    has_more: bool


class AuditStatsResponse(BaseModel):
    """Schema for audit statistics."""
    total_logs: int
    logs_by_action: Dict[str, int]
    logs_by_user: Dict[str, int]
    recent_security_events: List[SecurityEventResponse]
    failed_actions_count: int