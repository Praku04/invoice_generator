# Payment Receipt System

This document describes the comprehensive payment receipt system implemented in the Invoice Generator SaaS application, providing automated receipt generation, PDF creation, email notifications, and admin CRM management.

## Overview

The Payment Receipt System provides:
- **Automatic Receipt Generation**: Create receipts from successful payments
- **Professional PDF Receipts**: Generate tax-compliant PDF receipts
- **Email Notifications**: Send receipts to customers with secure download links
- **Admin CRM Management**: Complete admin interface for receipt management
- **Account Matching**: Ensure receipts match user accounts and payments
- **Audit Trails**: Complete tracking of all receipt operations
- **Secure Downloads**: Time-bound secure tokens for PDF access

## Architecture

### Core Components

1. **PaymentReceiptService** (`app/services/payment_receipt_service.py`)
   - Creates receipts from payments and invoices
   - Generates PDF receipts
   - Manages email notifications
   - Handles admin operations

2. **PaymentReceipt Model** (`app/models/payment_receipt.py`)
   - Stores receipt data and metadata
   - Tracks PDF generation and email status
   - Manages admin review workflow

3. **PDF Generation** (`app/services/pdf_service.py`)
   - Professional receipt templates
   - Tax breakdown calculations
   - Watermarks and security features

4. **Email Integration** (`app/services/email_service.py`)
   - Receipt notification emails
   - Secure download links
   - Delivery tracking

### Database Schema

#### PaymentReceipt Table
```sql
CREATE TABLE payment_receipts (
    id SERIAL PRIMARY KEY,
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    receipt_type receipt_type_enum NOT NULL,
    status receipt_status_enum DEFAULT 'draft',
    
    -- Related entities
    user_id INTEGER REFERENCES users(id),
    payment_id INTEGER REFERENCES payments(id),
    subscription_id INTEGER REFERENCES subscriptions(id),
    invoice_id INTEGER REFERENCES invoices(id),
    
    -- Financial details
    amount DECIMAL(15,2) NOT NULL,
    tax_amount DECIMAL(15,2) DEFAULT 0.00,
    total_amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    
    -- Customer and company details
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    company_gstin VARCHAR(20),
    
    -- PDF and email tracking
    pdf_generated BOOLEAN DEFAULT FALSE,
    pdf_file_path VARCHAR(500),
    email_sent BOOLEAN DEFAULT FALSE,
    
    -- Admin management
    admin_reviewed BOOLEAN DEFAULT FALSE,
    admin_reviewed_by INTEGER REFERENCES users(id),
    admin_notes TEXT,
    
    -- Timestamps
    receipt_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

## Features

### Receipt Types

1. **Subscription Payment Receipts**
   - Generated automatically from successful subscription payments
   - Include GST calculations (18% tax)
   - Link to subscription and plan details
   - Activate premium features

2. **Invoice Payment Receipts**
   - Created when invoice payments are received
   - Support various payment methods
   - Include client and invoice details
   - Tax breakdown from invoice

3. **Refund Receipts** (Future)
   - Generated for refund transactions
   - Negative amounts
   - Reference original receipt

### Receipt Status Workflow

```
DRAFT → GENERATED → SENT → VIEWED
```

- **DRAFT**: Receipt created but not finalized
- **GENERATED**: PDF generated and ready
- **SENT**: Email sent to customer
- **VIEWED**: Customer accessed the receipt

### PDF Generation

#### Features
- Professional layout with company branding
- Tax breakdown tables
- Amount in words conversion
- Watermarks for authenticity
- GST compliance formatting

#### Template Structure
```html
<!-- Receipt Header -->
<div class="receipt-header">
    <div class="receipt-title">PAYMENT RECEIPT</div>
    <div class="receipt-number">RCP-202601001</div>
</div>

<!-- Company Information -->
<div class="company-section">
    <div class="company-name">Company Name</div>
    <div>GSTIN: 22AAAAA0000A1Z5</div>
</div>

<!-- Payment Details -->
<div class="payment-details">
    <table class="payment-table">
        <tr>
            <td>Payment Method:</td>
            <td>Credit Card</td>
        </tr>
        <tr>
            <td>Transaction ID:</td>
            <td>TXN123456789</td>
        </tr>
    </table>
</div>

<!-- Amount Section -->
<div class="amount-section">
    <div class="total-amount">₹99.00</div>
</div>
```

### Email Notifications

#### Receipt Email Template
- Professional HTML design
- Receipt details summary
- Secure download button
- Expiration notice
- Company branding

#### Features
- Automatic sending after receipt generation
- Secure download tokens (24-hour expiry)
- Delivery tracking
- Retry mechanism for failed emails

### Admin CRM Management

#### Admin Dashboard Features
1. **Receipt Overview**
   - All receipts across users
   - Filter by type, status, date
   - Search by receipt number or customer

2. **Receipt Review Workflow**
   - Mark receipts as reviewed
   - Add admin notes
   - Approve/reject receipts

3. **Statistics and Reports**
   - Total receipts and amounts
   - Receipts by type and status
   - Revenue tracking
   - Recent activity

4. **Bulk Operations**
   - Bulk review and approval
   - Export receipt data
   - Cleanup old receipts

### Security Features

#### Secure Download Tokens
- Time-bound access (24 hours)
- Download count limits (5 downloads)
- IP address tracking
- User agent logging
- Automatic expiration

#### Access Control
- User can only access their own receipts
- Admin can access all receipts
- Secure token validation
- Audit logging for all access

## API Endpoints

### User Endpoints

```http
GET /api/receipts/
# Get user's payment receipts
# Query params: skip, limit, receipt_type, status

GET /api/receipts/{receipt_id}
# Get specific receipt details

POST /api/receipts/
# Create receipt from invoice payment

PUT /api/receipts/{receipt_id}
# Update receipt (draft only)

POST /api/receipts/{receipt_id}/generate-pdf
# Generate PDF for receipt

POST /api/receipts/{receipt_id}/send-email
# Send receipt via email

GET /api/receipts/{receipt_id}/download-url
# Get secure download URL

GET /api/receipts/download/{token}
# Download PDF using secure token
```

### Admin Endpoints

```http
GET /api/receipts/admin/all
# Get all receipts (admin only)
# Query params: skip, limit, receipt_type, status, user_id, date_from, date_to

GET /api/receipts/admin/{receipt_id}
# Get receipt details (admin access)

PUT /api/receipts/admin/{receipt_id}/review
# Review and approve receipt

DELETE /api/receipts/admin/{receipt_id}
# Delete receipt (draft only)

GET /api/receipts/admin/stats
# Get receipt statistics
```

## Usage Examples

### Creating Receipt from Subscription Payment

```python
from app.services.payment_receipt_service import PaymentReceiptService

receipt_service = PaymentReceiptService(db)

# Create receipt from successful payment
receipt = receipt_service.create_receipt_from_payment(
    payment_id=payment.id,
    created_by_user_id=user.id,
    admin_notes="Auto-generated from subscription payment"
)

# Generate PDF
pdf_path = receipt_service.generate_receipt_pdf(receipt.id, user.id)

# Send email notification
success = receipt_service.send_receipt_email(
    receipt_id=receipt.id,
    to_email=user.email,
    user_id=user.id
)
```

### Creating Receipt from Invoice Payment

```python
# Create receipt from invoice payment
payment_details = {
    'method': 'Bank Transfer',
    'transaction_id': 'TXN123456789',
    'payment_date': datetime.utcnow()
}

receipt = receipt_service.create_receipt_from_invoice_payment(
    invoice_id=invoice.id,
    payment_details=payment_details,
    created_by_user_id=user.id
)
```

### Admin Receipt Management

```python
# Get all receipts for admin
receipts = receipt_service.get_all_receipts_for_admin(
    limit=50,
    receipt_type=ReceiptType.SUBSCRIPTION_PAYMENT,
    status=ReceiptStatus.GENERATED
)

# Review receipt
reviewed_receipt = receipt_service.admin_review_receipt(
    receipt_id=receipt.id,
    admin_user_id=admin.id,
    notes="Receipt verified and approved",
    approved=True
)
```

### Integration with Payment Processing

```python
# In subscription service after successful payment
def handle_successful_payment(self, payment_id: int) -> bool:
    receipt_service = PaymentReceiptService(self.db)
    
    # Create receipt
    receipt = receipt_service.create_receipt_from_payment(payment_id)
    
    # Generate PDF
    receipt_service.generate_receipt_pdf(receipt.id)
    
    # Send email
    receipt_service.send_receipt_email(receipt.id)
    
    return True
```

## Configuration

### Environment Variables

```bash
# Company Details (for receipts)
COMPANY_NAME=Invoice Generator SaaS
COMPANY_ADDRESS=123 Business Street, Business City, State 12345, India
COMPANY_GSTIN=22AAAAA0000A1Z5
COMPANY_PAN=AAAAA0000A

# PDF Configuration
PDF_TIMEOUT=30
PDF_DPI=300

# File Storage
UPLOAD_DIR=uploads
RECEIPTS_DIR=uploads/receipts
```

### Receipt Number Format

```
Format: YYYYMM####
Example: 202601001 (January 2026, sequence 001)
```

## Database Migration

Run the migration to create the payment receipts table:

```bash
alembic upgrade head
```

This creates:
- `payment_receipts` table
- Updates `secure_download_tokens` for receipt support
- Adds necessary indexes and constraints

## Demo Script

Run the comprehensive demo:

```bash
python demo_payment_receipts.py
```

The demo demonstrates:
- Subscription payment receipt creation
- Invoice payment receipt creation
- PDF generation and email sending
- Admin CRM management
- Account matching and reconciliation

## Integration Points

### With Subscription System
- Automatic receipt creation on successful payments
- Subscription activation confirmation
- Plan details in receipt

### With Invoice System
- Receipt creation for invoice payments
- Client information integration
- Tax calculation consistency

### With Audit System
- All receipt operations logged
- Admin actions tracked
- Security events monitored

### With Email System
- Professional email templates
- Secure download links
- Delivery status tracking

## Compliance Features

### Tax Compliance
- GST breakdown and calculations
- Tax registration numbers
- Compliant receipt format
- Amount in words

### Financial Compliance
- Sequential receipt numbering
- Immutable receipt records
- Complete audit trails
- Account reconciliation

### Data Protection
- Secure token-based downloads
- Access control and permissions
- Data retention policies
- Privacy-compliant email handling

## Performance Considerations

### PDF Generation
- Asynchronous processing for large volumes
- Template caching
- Optimized CSS and layouts
- File compression

### Database Optimization
- Indexes on frequently queried fields
- Partitioning for large datasets
- Archive old receipts
- Query optimization

### File Storage
- Organized directory structure
- Cleanup of expired tokens
- CDN integration for downloads
- Backup and recovery

## Monitoring and Analytics

### Key Metrics
- Receipt generation rate
- PDF download success rate
- Email delivery rate
- Admin review time
- Customer engagement

### Alerts
- Failed PDF generation
- Email delivery failures
- Expired download tokens
- Unusual access patterns

## Future Enhancements

### Planned Features
1. **Bulk Receipt Operations**
   - Batch PDF generation
   - Bulk email sending
   - Mass admin review

2. **Advanced Templates**
   - Custom receipt templates
   - Multi-language support
   - Brand customization

3. **Integration Enhancements**
   - Accounting software integration
   - Payment gateway webhooks
   - Mobile app support

4. **Analytics Dashboard**
   - Revenue analytics
   - Customer insights
   - Receipt performance metrics

## Troubleshooting

### Common Issues

1. **PDF Generation Fails**
   - Check WeasyPrint installation
   - Verify template syntax
   - Check file permissions

2. **Email Not Sending**
   - Verify SMTP configuration
   - Check email templates
   - Review delivery logs

3. **Download Token Expired**
   - Generate new token
   - Check expiration settings
   - Verify token validation

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support

For questions or issues with the payment receipt system:
1. Check the demo script for usage examples
2. Review the API documentation
3. Examine the service implementations
4. Check database migrations and models
5. Review audit logs for troubleshooting