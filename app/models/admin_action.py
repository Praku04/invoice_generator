"""Admin action model for tracking admin-specific operations."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class AdminActionType(str, enum.Enum):
    """Admin action type enumeration."""
    USER_MANAGEMENT = "user_management"
    SUBSCRIPTION_MANAGEMENT = "subscription_management"
    INVOICE_MANAGEMENT = "invoice_management"
    PAYMENT_MANAGEMENT = "payment_management"
    SYSTEM_CONFIGURATION = "system_configuration"
    ANALYTICS_ACCESS = "analytics_access"
    BULK_OPERATION = "bulk_operation"
    DATA_EXPORT = "data_export"
    EMAIL_CAMPAIGN = "email_campaign"
    SUPPORT_TICKET = "support_ticket"


class AdminAction(Base):
    """Admin action model for tracking admin-specific operations."""
    
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Action details
    action_type = Column(Enum(AdminActionType), nullable=False)
    action_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    
    # Target details
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    target_resource_type = Column(String(50), nullable=True)  # user, invoice, subscription
    target_resource_id = Column(Integer, nullable=True)
    
    # Operation details
    operation_data = Column(Text, nullable=True)  # JSON string for operation parameters
    result_data = Column(Text, nullable=True)  # JSON string for operation results
    
    # Status
    status = Column(String(20), default="completed")  # completed, failed, in_progress
    error_message = Column(Text, nullable=True)
    
    # Request context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    admin = relationship("User", foreign_keys=[admin_id], back_populates="admin_actions")
    target_user = relationship("User", foreign_keys=[target_user_id])
    
    def __repr__(self):
        return f"<AdminAction(id={self.id}, admin_id={self.admin_id}, action_type='{self.action_type}', status='{self.status}')>"