"""Email service for sending notifications and managing email templates."""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
import os
import hashlib
import secrets

from app.models.email_log import EmailLog, EmailType, EmailStatus
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.models.secure_download_token import SecureDownloadToken
from app.models.user import User
from app.models.invoice import Invoice
from app.config import settings


class EmailService:
    """Service class for email operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email
        
        # Setup Jinja2 environment for email templates
        self.jinja_env = Environment(
            loader=FileSystemLoader('app/templates/email'),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str = None,
        email_type: EmailType = EmailType.ADMIN_MESSAGE,
        user_id: int = None,
        resource_type: str = None,
        resource_id: int = None,
        attachments: List[Dict[str, Any]] = None
    ) -> EmailLog:
        """Send an email and log the attempt."""
        
        # Create email log entry
        email_log = EmailLog(
            user_id=user_id,
            to_email=to_email,
            from_email=self.from_email,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            email_type=email_type,
            resource_type=resource_type,
            resource_id=resource_id,
            status=EmailStatus.PENDING
        )
        
        self.db.add(email_log)
        self.db.flush()
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to_email
            
            # Add text and HTML parts
            if body_text:
                text_part = MIMEText(body_text, "plain")
                message.attach(text_part)
            
            if body_html:
                html_part = MIMEText(body_html, "html")
                message.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self._add_attachment(message, attachment)
            
            # Send email
            if self.smtp_host and self.smtp_user and self.smtp_password:
                context = ssl.create_default_context()
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls(context=context)
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.from_email, to_email, message.as_string())
                
                # Update email log
                email_log.status = EmailStatus.SENT
                email_log.sent_at = datetime.utcnow()
            else:
                # Email not configured, mark as failed
                email_log.status = EmailStatus.FAILED
                email_log.error_message = "SMTP configuration not provided"
        
        except Exception as e:
            email_log.status = EmailStatus.FAILED
            email_log.error_message = str(e)
            email_log.retry_count += 1
        
        self.db.commit()
        return email_log
    
    def _add_attachment(self, message: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message."""
        try:
            with open(attachment['path'], "rb") as attachment_file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_file.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment["filename"]}'
            )
            message.attach(part)
        except Exception as e:
            print(f"Failed to attach file {attachment['path']}: {e}")
    
    def send_invoice_notification(
        self,
        user: User,
        invoice: Invoice,
        notification_type: str,
        client_email: str = None
    ) -> List[EmailLog]:
        """Send invoice notification to user and optionally to client."""
        
        email_logs = []
        
        # Generate secure download token
        download_token = self._generate_secure_download_token(user.id, invoice.id)
        download_url = f"{settings.app_base_url}/api/invoices/download/{download_token.token_plain}"
        
        # Email to user (invoice owner)
        user_email_log = self._send_invoice_email_to_user(
            user, invoice, notification_type, download_url
        )
        email_logs.append(user_email_log)
        
        # Email to client if email provided
        if client_email and invoice.client_email:
            client_email_log = self._send_invoice_email_to_client(
                invoice, notification_type, download_url
            )
            email_logs.append(client_email_log)
        
        # Create notification
        self._create_notification(
            user.id,
            notification_type,
            invoice.id,
            f"Invoice {invoice.invoice_number} has been {notification_type.lower()}"
        )
        
        return email_logs
    
    def _send_invoice_email_to_user(
        self,
        user: User,
        invoice: Invoice,
        notification_type: str,
        download_url: str
    ) -> EmailLog:
        """Send invoice notification email to user."""
        
        # Render email template
        template = self.jinja_env.get_template('invoice_notification_user.html')
        html_content = template.render(
            user=user,
            invoice=invoice,
            notification_type=notification_type,
            download_url=download_url,
            app_name=settings.app_name
        )
        
        # Plain text version
        text_template = self.jinja_env.get_template('invoice_notification_user.txt')
        text_content = text_template.render(
            user=user,
            invoice=invoice,
            notification_type=notification_type,
            download_url=download_url,
            app_name=settings.app_name
        )
        
        subject = f"Invoice {invoice.invoice_number} - {notification_type}"
        
        return self.send_email(
            to_email=user.email,
            subject=subject,
            body_html=html_content,
            body_text=text_content,
            email_type=EmailType.INVOICE_NOTIFICATION,
            user_id=user.id,
            resource_type="invoice",
            resource_id=invoice.id
        )
    
    def _send_invoice_email_to_client(
        self,
        invoice: Invoice,
        notification_type: str,
        download_url: str
    ) -> EmailLog:
        """Send invoice notification email to client."""
        
        # Render email template
        template = self.jinja_env.get_template('invoice_notification_client.html')
        html_content = template.render(
            invoice=invoice,
            notification_type=notification_type,
            download_url=download_url,
            app_name=settings.app_name
        )
        
        # Plain text version
        text_template = self.jinja_env.get_template('invoice_notification_client.txt')
        text_content = text_template.render(
            invoice=invoice,
            notification_type=notification_type,
            download_url=download_url,
            app_name=settings.app_name
        )
        
        subject = f"Invoice {invoice.invoice_number} from {invoice.user.full_name}"
        
        return self.send_email(
            to_email=invoice.client_email,
            subject=subject,
            body_html=html_content,
            body_text=text_content,
            email_type=EmailType.INVOICE_NOTIFICATION,
            user_id=invoice.user_id,
            resource_type="invoice",
            resource_id=invoice.id
        )
    
    def send_password_reset_email(self, user: User, reset_token: str) -> EmailLog:
        """Send password reset email."""
        
        reset_url = f"{settings.app_base_url}/reset-password?token={reset_token}"
        
        # Render email template
        template = self.jinja_env.get_template('password_reset.html')
        html_content = template.render(
            user=user,
            reset_url=reset_url,
            app_name=settings.app_name,
            expires_in_hours=1
        )
        
        # Plain text version
        text_template = self.jinja_env.get_template('password_reset.txt')
        text_content = text_template.render(
            user=user,
            reset_url=reset_url,
            app_name=settings.app_name,
            expires_in_hours=1
        )
        
        subject = f"Password Reset - {settings.app_name}"
        
        return self.send_email(
            to_email=user.email,
            subject=subject,
            body_html=html_content,
            body_text=text_content,
            email_type=EmailType.PASSWORD_RESET,
            user_id=user.id,
            resource_type="user",
            resource_id=user.id
        )
    
    def send_email_verification(self, user: User, verification_token: str) -> EmailLog:
        """Send email verification email."""
        
        verification_url = f"{settings.app_base_url}/verify-email?token={verification_token}"
        
        # Render email template
        template = self.jinja_env.get_template('email_verification.html')
        html_content = template.render(
            user=user,
            verification_url=verification_url,
            app_name=settings.app_name
        )
        
        # Plain text version
        text_template = self.jinja_env.get_template('email_verification.txt')
        text_content = text_template.render(
            user=user,
            verification_url=verification_url,
            app_name=settings.app_name
        )
        
        subject = f"Verify Your Email - {settings.app_name}"
        
        return self.send_email(
            to_email=user.email,
            subject=subject,
            body_html=html_content,
            body_text=text_content,
            email_type=EmailType.EMAIL_VERIFICATION,
            user_id=user.id,
            resource_type="user",
            resource_id=user.id
        )
    
    def send_welcome_email(self, user: User) -> EmailLog:
        """Send welcome email to new user."""
        
        # Render email template
        template = self.jinja_env.get_template('welcome.html')
        html_content = template.render(
            user=user,
            app_name=settings.app_name,
            dashboard_url=f"{settings.app_base_url}/dashboard"
        )
        
        # Plain text version
        text_template = self.jinja_env.get_template('welcome.txt')
        text_content = text_template.render(
            user=user,
            app_name=settings.app_name,
            dashboard_url=f"{settings.app_base_url}/dashboard"
        )
        
        subject = f"Welcome to {settings.app_name}!"
        
        return self.send_email(
            to_email=user.email,
            subject=subject,
            body_html=html_content,
            body_text=text_content,
            email_type=EmailType.WELCOME,
            user_id=user.id,
            resource_type="user",
            resource_id=user.id
        )
    
    def send_subscription_notification(
        self,
        user: User,
        subscription_type: str,
        subscription_data: Dict[str, Any] = None
    ) -> EmailLog:
        """Send subscription notification email."""
        
        # Render email template
        template = self.jinja_env.get_template('subscription_notification.html')
        html_content = template.render(
            user=user,
            subscription_type=subscription_type,
            subscription_data=subscription_data,
            app_name=settings.app_name,
            dashboard_url=f"{settings.app_base_url}/dashboard"
        )
        
        # Plain text version
        text_template = self.jinja_env.get_template('subscription_notification.txt')
        text_content = text_template.render(
            user=user,
            subscription_type=subscription_type,
            subscription_data=subscription_data,
            app_name=settings.app_name,
            dashboard_url=f"{settings.app_base_url}/dashboard"
        )
        
        subject = f"Subscription {subscription_type} - {settings.app_name}"
        
        return self.send_email(
            to_email=user.email,
            subject=subject,
            body_html=html_content,
            body_text=text_content,
            email_type=EmailType.SUBSCRIPTION_NOTIFICATION,
            user_id=user.id,
            resource_type="subscription",
            resource_id=subscription_data.get('subscription_id') if subscription_data else None
        )
    
    def _generate_secure_download_token(self, user_id: int, invoice_id: int) -> SecureDownloadToken:
        """Generate secure download token for invoice PDF."""
        
        # Generate token
        token_plain = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token_plain.encode()).hexdigest()
        
        # Create token record
        download_token = SecureDownloadToken(
            user_id=user_id,
            invoice_id=invoice_id,
            token_hash=token_hash,
            token_plain=token_plain,
            expires_at=datetime.utcnow() + timedelta(hours=24),  # 24 hour expiry
            max_downloads=5
        )
        
        self.db.add(download_token)
        self.db.commit()
        
        return download_token
    
    def _create_notification(
        self,
        user_id: int,
        notification_type: str,
        resource_id: int,
        message: str
    ):
        """Create a notification record."""
        
        # Map notification type
        type_mapping = {
            "finalized": NotificationType.INVOICE_FINALIZED,
            "sent": NotificationType.INVOICE_SENT,
            "paid": NotificationType.INVOICE_PAID,
            "activated": NotificationType.SUBSCRIPTION_ACTIVATED,
            "cancelled": NotificationType.SUBSCRIPTION_CANCELLED,
        }
        
        notification = Notification(
            user_id=user_id,
            type=type_mapping.get(notification_type.lower(), NotificationType.ACCOUNT_ACTIVITY),
            title=f"Invoice {notification_type}",
            message=message,
            resource_type="invoice",
            resource_id=resource_id,
            status=NotificationStatus.SENT
        )
        
        self.db.add(notification)
        self.db.commit()
    
    def retry_failed_emails(self, max_retries: int = 3) -> int:
        """Retry failed email deliveries."""
        
        failed_emails = self.db.query(EmailLog).filter(
            EmailLog.status == EmailStatus.FAILED,
            EmailLog.retry_count < max_retries
        ).all()
        
        retry_count = 0
        for email_log in failed_emails:
            try:
                # Retry sending
                new_log = self.send_email(
                    to_email=email_log.to_email,
                    subject=email_log.subject,
                    body_html=email_log.body_html,
                    body_text=email_log.body_text,
                    email_type=email_log.email_type,
                    user_id=email_log.user_id,
                    resource_type=email_log.resource_type,
                    resource_id=email_log.resource_id
                )
                
                if new_log.status == EmailStatus.SENT:
                    retry_count += 1
                    
            except Exception as e:
                print(f"Failed to retry email {email_log.id}: {e}")
        
        return retry_count
    
    def send_receipt_notification(
        self,
        receipt,
        to_email: str,
        download_url: str
    ) -> EmailLog:
        """Send payment receipt notification email."""
        
        # Render email template
        template = self.jinja_env.get_template('receipt_notification.html')
        html_content = template.render(
            receipt=receipt,
            download_url=download_url,
            app_name=settings.app_name
        )
        
        # Plain text version
        text_template = self.jinja_env.get_template('receipt_notification.txt')
        text_content = text_template.render(
            receipt=receipt,
            download_url=download_url,
            app_name=settings.app_name
        )
        
        subject = f"Payment Receipt {receipt.formatted_receipt_number} - {settings.app_name}"
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            body_html=html_content,
            body_text=text_content,
            email_type=EmailType.PAYMENT_CONFIRMATION,
            user_id=receipt.user_id,
            resource_type="receipt",
            resource_id=receipt.id
        )