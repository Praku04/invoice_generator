# Audit & Notification System

This document describes the comprehensive audit logging and notification system implemented in the Invoice Generator SaaS application.

## Overview

The system provides:
- **Comprehensive Audit Logging**: Track all user and admin actions
- **Real-time Notifications**: Notify users of important events
- **Email Integration**: Send notifications via email with templates
- **Secure Downloads**: Time-bound secure tokens for invoice PDFs
- **Admin Monitoring**: Detailed admin action tracking
- **Compliance Ready**: Full audit trails for regulatory compliance

## Architecture

### Core Services

1. **AuditService** (`app/services/audit_service.py`)
   - Logs all user and admin actions
   - Provides querying capabilities
   - Handles cleanup of old logs

2. **NotificationService** (`app/services/notification_service.py`)
   - Creates and manages user notifications
   - Integrates with email service
   - Handles notification lifecycle

3. **EmailService** (`app/services/email_service.py`)
   - Sends emails using SMTP
   - Manages email templates
   - Generates secure download tokens
   - Tracks email delivery status

### Database Models

1. **AuditLog** - Records all system actions
2. **AdminAction** - Tracks admin-specific operations
3. **Notification** - User notifications
4. **EmailLog** - Email delivery tracking
5. **SecureDownloadToken** - Time-bound PDF access tokens

## Features

### Audit Logging

#### User Actions Tracked
- User signup, login, logout
- Password changes and resets
- Email verification
- Profile updates
- Invoice creation, updates, finalization
- Payment processing
- Subscription changes

#### Admin Actions Tracked
- User management operations
- System configuration changes
- Data exports and analytics access
- Bulk operations
- Support ticket handling

#### Audit Log Fields
- Action type and description
- User/Admin ID
- Resource type and ID (invoice, user, etc.)
- IP address and user agent
- Request method and path
- Metadata (JSON)
- Success/failure status
- Timestamp

### Notification System

#### Notification Types
- Invoice finalized/sent/paid
- Subscription activated/cancelled/renewed
- Password reset requests
- Email verification
- Account activity alerts
- Admin messages

#### Features
- Real-time in-app notifications
- Email notifications with templates
- Read/unread status tracking
- Notification metadata
- Bulk operations (mark all as read)

### Email System

#### Email Types
- Invoice notifications (user & client)
- Password reset
- Email verification
- Welcome emails
- Subscription notifications
- Admin messages

#### Features
- HTML and plain text templates
- Secure download tokens for PDFs
- Delivery status tracking
- Retry mechanism for failed emails
- Template customization

### Secure Download Tokens

#### Features
- Time-bound access (24 hours default)
- Download count limits (5 downloads default)
- IP address tracking
- User agent logging
- Automatic expiration
- Email context tracking

## API Endpoints

### Notifications API (`/api/notifications`)

```
GET    /                    # Get user notifications
GET    /unread-count        # Get unread count
GET    /{id}               # Get specific notification
PUT    /{id}/read          # Mark as read
PUT    /mark-all-read      # Mark all as read
POST   /test               # Create test notification
```

### Audit API (`/api/audit`) - Admin Only

```
GET    /logs                           # Get audit logs
GET    /admin-actions                  # Get admin actions
GET    /security-events                # Get security events
GET    /user/{id}/logs                 # Get user audit logs
GET    /resource/{type}/{id}/logs      # Get resource audit logs
DELETE /cleanup                        # Cleanup old logs
```

## Configuration

### Environment Variables

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@invoicegen.com

# Application
APP_BASE_URL=http://localhost:8000
```

### Email Templates

Templates are located in `app/templates/email/`:
- `invoice_notification_user.html/txt`
- `invoice_notification_client.html/txt`
- `password_reset.html/txt`
- `email_verification.html/txt`
- `welcome.html/txt`
- `subscription_notification.html/txt`

## Usage Examples

### Basic Audit Logging

```python
from app.services.audit_service import AuditService

audit_service = AuditService(db)

# Log user action
audit_service.log_user_login(
    user_id=user.id,
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0..."
)

# Log invoice action
audit_service.log_invoice_created(
    user_id=user.id,
    invoice_id=invoice.id,
    invoice_number="INV-2026-001"
)
```

### Creating Notifications

```python
from app.services.notification_service import NotificationService

notification_service = NotificationService(db)

# Create notification
notification = notification_service.create_notification(
    user_id=user.id,
    notification_type=NotificationType.INVOICE_FINALIZED,
    title="Invoice Finalized",
    message="Your invoice has been finalized and is ready to send.",
    resource_type="invoice",
    resource_id=invoice.id,
    send_email=True
)
```

### Sending Emails

```python
from app.services.email_service import EmailService

email_service = EmailService(db)

# Send invoice notification
email_logs = email_service.send_invoice_notification(
    user=user,
    invoice=invoice,
    notification_type="sent",
    client_email=invoice.client_email
)
```

### Integration in Services

```python
class InvoiceService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
        self.notification_service = NotificationService(db)
    
    def finalize_invoice(self, invoice_id: int, user_id: int):
        # Business logic
        invoice.status = InvoiceStatus.FINALIZED
        self.db.commit()
        
        # Audit logging
        self.audit_service.log_invoice_finalized(
            user_id=user_id,
            invoice_id=invoice.id,
            invoice_number=invoice.invoice_number
        )
        
        # Notification
        self.notification_service.notify_invoice_finalized(invoice)
```

## Database Migration

Run the migration to create the new tables:

```bash
alembic upgrade head
```

This will create:
- `audit_logs`
- `admin_actions`
- `notifications`
- `email_logs`
- `secure_download_tokens`

## Demo Script

Run the demo script to see the system in action:

```bash
python demo_audit_notification.py
```

The demo shows:
- Creating audit logs for various actions
- Sending notifications to users
- Email service capabilities
- Integration between all services

## Security Considerations

1. **Audit Log Integrity**: Audit logs are append-only and should not be modified
2. **Secure Tokens**: Download tokens are hashed and time-limited
3. **IP Tracking**: All actions include IP address for security monitoring
4. **Admin Actions**: All admin operations are logged for accountability
5. **Email Security**: SMTP credentials should be stored securely

## Performance Considerations

1. **Log Cleanup**: Implement regular cleanup of old audit logs
2. **Indexing**: Database indexes on frequently queried fields
3. **Async Processing**: Consider async processing for email sending
4. **Pagination**: All list endpoints support pagination
5. **Caching**: Cache notification counts for better performance

## Compliance Features

1. **Complete Audit Trail**: Every action is logged with context
2. **Data Retention**: Configurable retention periods
3. **User Activity Tracking**: Detailed user behavior logging
4. **Admin Accountability**: All admin actions are tracked
5. **Export Capabilities**: Audit logs can be exported for compliance

## Monitoring and Alerts

The system provides data for:
- Failed login attempts
- Suspicious activity patterns
- Email delivery failures
- System errors and exceptions
- Performance metrics

## Future Enhancements

1. **Real-time Notifications**: WebSocket support for live notifications
2. **Advanced Analytics**: Dashboard for audit log analysis
3. **Webhook Integration**: External system notifications
4. **Mobile Push Notifications**: Mobile app integration
5. **Advanced Email Features**: Email tracking, A/B testing

## Troubleshooting

### Common Issues

1. **Email Not Sending**: Check SMTP configuration
2. **Notifications Not Created**: Verify service integration
3. **Audit Logs Missing**: Check service initialization
4. **Download Tokens Expired**: Verify token generation logic

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support

For questions or issues with the audit and notification system:
1. Check the demo script for usage examples
2. Review the API documentation
3. Examine the service implementations
4. Check database migrations and models