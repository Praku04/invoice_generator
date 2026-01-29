"""Audit service for logging and querying user and admin actions."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import json

from app.models.audit_log import AuditLog, AuditAction
from app.models.admin_action import AdminAction, AdminActionType
from app.models.user import User


class AuditService:
    """Service for audit logging and querying."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # User action logging methods
    def log_user_signup(self, user_id: int, ip_address: str = None, user_agent: str = None):
        """Log user signup action."""
        return self._log_action(
            action=AuditAction.USER_SIGNUP,
            user_id=user_id,
            description=f"User signed up",
            resource_type="user",
            resource_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_user_login(self, user_id: int, ip_address: str = None, user_agent: str = None):
        """Log user login action."""
        return self._log_action(
            action=AuditAction.USER_LOGIN,
            user_id=user_id,
            description=f"User logged in",
            resource_type="user",
            resource_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_user_logout(self, user_id: int, ip_address: str = None, user_agent: str = None):
        """Log user logout action."""
        return self._log_action(
            action=AuditAction.USER_LOGOUT,
            user_id=user_id,
            description=f"User logged out",
            resource_type="user",
            resource_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_invoice_created(self, user_id: int, invoice_id: int, invoice_number: str, ip_address: str = None):
        """Log invoice creation action."""
        return self._log_action(
            action=AuditAction.INVOICE_CREATED,
            user_id=user_id,
            description=f"Invoice {invoice_number} created",
            resource_type="invoice",
            resource_id=invoice_id,
            ip_address=ip_address
        )
    
    def log_invoice_finalized(self, user_id: int, invoice_id: int, invoice_number: str, ip_address: str = None):
        """Log invoice finalization action."""
        return self._log_action(
            action=AuditAction.INVOICE_FINALIZED,
            user_id=user_id,
            description=f"Invoice {invoice_number} finalized",
            resource_type="invoice",
            resource_id=invoice_id,
            ip_address=ip_address
        )
    
    def log_invoice_sent(self, user_id: int, invoice_id: int, invoice_number: str, recipient_email: str, ip_address: str = None):
        """Log invoice sent action."""
        return self._log_action(
            action=AuditAction.INVOICE_SENT,
            user_id=user_id,
            description=f"Invoice {invoice_number} sent to {recipient_email}",
            resource_type="invoice",
            resource_id=invoice_id,
            ip_address=ip_address,
            extra_data=json.dumps({"recipient_email": recipient_email})
        )
    
    def log_payment_completed(self, user_id: int, payment_id: int, amount: float, currency: str = "INR"):
        """Log payment completion action."""
        return self._log_action(
            action=AuditAction.PAYMENT_COMPLETED,
            user_id=user_id,
            description=f"Payment completed: {currency} {amount}",
            resource_type="payment",
            resource_id=payment_id,
            extra_data=json.dumps({"amount": amount, "currency": currency})
        )
    
    def log_action(self, action: str, user_id: int = None, description: str = None, 
                   resource_type: str = None, resource_id: int = None, 
                   ip_address: str = None, user_agent: str = None, 
                   extra_data: Dict[str, Any] = None):
        """Generic action logging method."""
        return self._log_action(
            action=action,
            user_id=user_id,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=json.dumps(extra_data) if extra_data else None
        )
    
    # Admin action logging
    def log_admin_action(self, admin_id: int, action_type: AdminActionType, 
                        action_name: str, description: str,
                        target_user_id: int = None, target_resource_type: str = None,
                        target_resource_id: int = None, ip_address: str = None,
                        user_agent: str = None, operation_data: Dict[str, Any] = None):
        """Log admin action."""
        admin_action = AdminAction(
            admin_id=admin_id,
            action_type=action_type,
            action_name=action_name,
            description=description,
            target_user_id=target_user_id,
            target_resource_type=target_resource_type,
            target_resource_id=target_resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            operation_data=json.dumps(operation_data) if operation_data else None,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            status="completed"
        )
        
        self.db.add(admin_action)
        self.db.commit()
        self.db.refresh(admin_action)
        
        # Also log as regular audit log
        self._log_action(
            action=AuditAction.ADMIN_USER_VIEWED if "view" in action_name.lower() else AuditAction.ADMIN_USER_DEACTIVATED,
            admin_id=admin_id,
            description=f"Admin action: {description}",
            resource_type=target_resource_type,
            resource_id=target_resource_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return admin_action
    
    # Query methods
    def get_user_audit_logs(self, user_id: int, limit: int = 50, offset: int = 0) -> List[AuditLog]:
        """Get audit logs for a specific user."""
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()
    
    def get_admin_actions(self, admin_id: int = None, action_type: AdminActionType = None,
                         target_user_id: int = None, limit: int = 50, offset: int = 0) -> List[AdminAction]:
        """Get admin actions with optional filtering."""
        query = self.db.query(AdminAction)
        
        if admin_id:
            query = query.filter(AdminAction.admin_id == admin_id)
        if action_type:
            query = query.filter(AdminAction.action_type == action_type)
        if target_user_id:
            query = query.filter(AdminAction.target_user_id == target_user_id)
        
        return query.order_by(desc(AdminAction.created_at)).offset(offset).limit(limit).all()
    
    def get_security_events(self, user_id: int = None, hours_back: int = 24) -> List[AuditLog]:
        """Get security-related events."""
        security_actions = [
            AuditAction.USER_LOGIN,
            AuditAction.USER_LOGOUT,
            AuditAction.USER_PASSWORD_CHANGED,
            AuditAction.USER_PASSWORD_RESET_REQUESTED,
            AuditAction.USER_PASSWORD_RESET_COMPLETED
        ]
        
        since = datetime.utcnow() - timedelta(hours=hours_back)
        query = self.db.query(AuditLog).filter(
            and_(
                AuditLog.action.in_(security_actions),
                AuditLog.created_at >= since
            )
        )
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        return query.order_by(desc(AuditLog.created_at)).all()
    
    def get_resource_audit_logs(self, resource_type: str, resource_id: int, 
                               limit: int = 50, offset: int = 0) -> List[AuditLog]:
        """Get audit logs for a specific resource."""
        return self.db.query(AuditLog).filter(
            and_(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id
            )
        ).order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()
    
    def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        """Clean up old audit logs."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Delete old audit logs
        deleted_audit_logs = self.db.query(AuditLog).filter(
            AuditLog.created_at < cutoff_date
        ).delete()
        
        # Delete old admin actions
        deleted_admin_actions = self.db.query(AdminAction).filter(
            AdminAction.created_at < cutoff_date
        ).delete()
        
        self.db.commit()
        
        return deleted_audit_logs + deleted_admin_actions
    
    # Private helper methods
    def _log_action(self, action: AuditAction, user_id: int = None, admin_id: int = None,
                   description: str = None, resource_type: str = None, resource_id: int = None,
                   ip_address: str = None, user_agent: str = None, request_method: str = None,
                   request_path: str = None, extra_data: str = None, success: str = "success",
                   error_message: str = None) -> AuditLog:
        """Internal method to log an action."""
        audit_log = AuditLog(
            user_id=user_id,
            admin_id=admin_id,
            action=action,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path,
            extra_data=extra_data,
            success=success,
            error_message=error_message
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log