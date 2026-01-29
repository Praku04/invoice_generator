"""Notification service for managing user notifications."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.models.notification import Notification, NotificationType, NotificationStatus
from app.models.user import User
from app.models.invoice import Invoice
from app.models.subscription import Subscription
from app.services.email_service import EmailService


class NotificationService:
    """Service class for notification operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService(db)
    
    def create_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        resource_type: str = None,
        resource_id: int = None,
        metadata: Dict[str, Any] = None,
        send_email: bool = True
    ) -> Notification:
        """Create a new notification."""
        
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=json.dumps(metadata) if metadata else None,
            status=NotificationStatus.PENDING
        )
        
        self.db.add(notification)
        self.db.flush()
        
        # Send email notification if requested
        if send_email:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                self._send_notification_email(user, notification)
        
        notification.status = NotificationStatus.SENT
        self.db.commit()
        
        return notification
    
    def notify_invoice_finalized(self, invoice: Invoice) -> Notification:
        """Send notification when invoice is finalized."""
        
        return self.create_notification(
            user_id=invoice.user_id,
            notification_type=NotificationType.INVOICE_FINALIZED,
            title="Invoice Finalized",
            message=f"Invoice {invoice.invoice_number} has been finalized and is ready to send.",
            resource_type="invoice",
            resource_id=invoice.id,
            metadata={
                "invoice_number": invoice.invoice_number,
                "client_name": invoice.client_name,
                "amount": str(invoice.grand_total),
                "currency": invoice.currency
            }
        )
    
    def notify_invoice_sent(self, invoice: Invoice) -> List[Notification]:
        """Send notification when invoice is sent."""
        
        notifications = []
        
        # Notify user
        user_notification = self.create_notification(
            user_id=invoice.user_id,
            notification_type=NotificationType.INVOICE_SENT,
            title="Invoice Sent",
            message=f"Invoice {invoice.invoice_number} has been sent to {invoice.client_name}.",
            resource_type="invoice",
            resource_id=invoice.id,
            metadata={
                "invoice_number": invoice.invoice_number,
                "client_name": invoice.client_name,
                "client_email": invoice.client_email,
                "amount": str(invoice.grand_total),
                "currency": invoice.currency
            }
        )
        notifications.append(user_notification)
        
        # Send email to user and client
        user = self.db.query(User).filter(User.id == invoice.user_id).first()
        if user:
            self.email_service.send_invoice_notification(
                user=user,
                invoice=invoice,
                notification_type="sent",
                client_email=invoice.client_email
            )
        
        return notifications
    
    def notify_invoice_paid(self, invoice: Invoice) -> Notification:
        """Send notification when invoice is paid."""
        
        user_notification = self.create_notification(
            user_id=invoice.user_id,
            notification_type=NotificationType.INVOICE_PAID,
            title="Invoice Paid",
            message=f"Invoice {invoice.invoice_number} has been marked as paid.",
            resource_type="invoice",
            resource_id=invoice.id,
            metadata={
                "invoice_number": invoice.invoice_number,
                "client_name": invoice.client_name,
                "amount": str(invoice.grand_total),
                "currency": invoice.currency
            }
        )
        
        # Send email notification
        user = self.db.query(User).filter(User.id == invoice.user_id).first()
        if user:
            self.email_service.send_invoice_notification(
                user=user,
                invoice=invoice,
                notification_type="paid"
            )
        
        return user_notification
    
    def notify_subscription_activated(self, subscription: Subscription) -> Notification:
        """Send notification when subscription is activated."""
        
        return self.create_notification(
            user_id=subscription.user_id,
            notification_type=NotificationType.SUBSCRIPTION_ACTIVATED,
            title="Subscription Activated",
            message=f"Your {subscription.plan.name} subscription has been activated.",
            resource_type="subscription",
            resource_id=subscription.id,
            metadata={
                "plan_name": subscription.plan.name,
                "plan_price": str(subscription.plan.price),
                "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None
            }
        )
    
    def notify_subscription_cancelled(self, subscription: Subscription) -> Notification:
        """Send notification when subscription is cancelled."""
        
        return self.create_notification(
            user_id=subscription.user_id,
            notification_type=NotificationType.SUBSCRIPTION_CANCELLED,
            title="Subscription Cancelled",
            message=f"Your {subscription.plan.name} subscription has been cancelled.",
            resource_type="subscription",
            resource_id=subscription.id,
            metadata={
                "plan_name": subscription.plan.name,
                "cancelled_at": subscription.cancelled_at.isoformat() if subscription.cancelled_at else None,
                "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None
            }
        )
    
    def notify_subscription_renewed(self, subscription: Subscription) -> Notification:
        """Send notification when subscription is renewed."""
        
        return self.create_notification(
            user_id=subscription.user_id,
            notification_type=NotificationType.SUBSCRIPTION_RENEWED,
            title="Subscription Renewed",
            message=f"Your {subscription.plan.name} subscription has been renewed.",
            resource_type="subscription",
            resource_id=subscription.id,
            metadata={
                "plan_name": subscription.plan.name,
                "plan_price": str(subscription.plan.price),
                "current_period_start": subscription.current_period_start.isoformat() if subscription.current_period_start else None,
                "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None
            }
        )
    
    def notify_password_reset_requested(self, user: User) -> Notification:
        """Send notification when password reset is requested."""
        
        return self.create_notification(
            user_id=user.id,
            notification_type=NotificationType.PASSWORD_RESET,
            title="Password Reset Requested",
            message="A password reset has been requested for your account.",
            resource_type="user",
            resource_id=user.id,
            metadata={
                "requested_at": datetime.utcnow().isoformat()
            },
            send_email=False  # Password reset has its own email
        )
    
    def notify_email_verification_sent(self, user: User) -> Notification:
        """Send notification when email verification is sent."""
        
        return self.create_notification(
            user_id=user.id,
            notification_type=NotificationType.EMAIL_VERIFICATION,
            title="Email Verification Sent",
            message="Please check your email to verify your account.",
            resource_type="user",
            resource_id=user.id,
            send_email=False  # Email verification has its own email
        )
    
    def notify_account_activity(
        self,
        user_id: int,
        activity_type: str,
        description: str,
        metadata: Dict[str, Any] = None
    ) -> Notification:
        """Send notification for account activity."""
        
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.ACCOUNT_ACTIVITY,
            title=f"Account Activity: {activity_type}",
            message=description,
            resource_type="user",
            resource_id=user_id,
            metadata=metadata
        )
    
    def get_user_notifications(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a user."""
        
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.read_at.is_(None))
        
        return query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    def mark_notification_as_read(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """Mark a notification as read."""
        
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification and not notification.read_at:
            notification.read_at = datetime.utcnow()
            notification.status = NotificationStatus.READ
            self.db.commit()
        
        return notification
    
    def mark_all_notifications_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user."""
        
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read_at.is_(None)
        ).update({
            "read_at": datetime.utcnow(),
            "status": NotificationStatus.READ
        })
        
        self.db.commit()
        return count
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read_at.is_(None)
        ).count()
    
    def _send_notification_email(self, user: User, notification: Notification):
        """Send email for notification (if applicable)."""
        
        # Only send emails for certain notification types
        email_types = [
            NotificationType.SUBSCRIPTION_ACTIVATED,
            NotificationType.SUBSCRIPTION_CANCELLED,
            NotificationType.SUBSCRIPTION_RENEWED,
            NotificationType.ADMIN_MESSAGE
        ]
        
        if notification.type in email_types:
            try:
                # Use appropriate email template based on notification type
                if notification.type == NotificationType.SUBSCRIPTION_ACTIVATED:
                    self.email_service.send_subscription_notification(
                        user=user,
                        subscription_type="activated",
                        subscription_data=json.loads(notification.metadata) if notification.metadata else {}
                    )
                elif notification.type == NotificationType.SUBSCRIPTION_CANCELLED:
                    self.email_service.send_subscription_notification(
                        user=user,
                        subscription_type="cancelled",
                        subscription_data=json.loads(notification.metadata) if notification.metadata else {}
                    )
                elif notification.type == NotificationType.SUBSCRIPTION_RENEWED:
                    self.email_service.send_subscription_notification(
                        user=user,
                        subscription_type="renewed",
                        subscription_data=json.loads(notification.metadata) if notification.metadata else {}
                    )
                
                notification.email_sent = True
                notification.email_sent_at = datetime.utcnow()
                
            except Exception as e:
                print(f"Failed to send notification email: {e}")
    
    def cleanup_old_notifications(self, days: int = 90) -> int:
        """Clean up old notifications."""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        count = self.db.query(Notification).filter(
            Notification.created_at < cutoff_date,
            Notification.status == NotificationStatus.READ
        ).delete()
        
        self.db.commit()
        return count