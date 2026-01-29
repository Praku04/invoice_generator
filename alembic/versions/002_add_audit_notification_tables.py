"""Add audit, notification, email and secure download tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-28 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('admin_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.Enum('USER_SIGNUP', 'USER_LOGIN', 'USER_LOGOUT', 'USER_EMAIL_VERIFIED', 'USER_PASSWORD_CHANGED', 'USER_PASSWORD_RESET_REQUESTED', 'USER_PASSWORD_RESET_COMPLETED', 'USER_PROFILE_UPDATED', 'INVOICE_CREATED', 'INVOICE_UPDATED', 'INVOICE_FINALIZED', 'INVOICE_SENT', 'INVOICE_PAID', 'INVOICE_CANCELLED', 'INVOICE_DELETED', 'INVOICE_PDF_DOWNLOADED', 'SUBSCRIPTION_CREATED', 'SUBSCRIPTION_ACTIVATED', 'SUBSCRIPTION_CANCELLED', 'SUBSCRIPTION_RENEWED', 'SUBSCRIPTION_EXPIRED', 'PAYMENT_INITIATED', 'PAYMENT_COMPLETED', 'PAYMENT_FAILED', 'PAYMENT_REFUNDED', 'ADMIN_USER_VIEWED', 'ADMIN_USER_DEACTIVATED', 'ADMIN_USER_ACTIVATED', 'ADMIN_USER_PASSWORD_RESET', 'ADMIN_USER_FORCE_LOGOUT', 'ADMIN_SUBSCRIPTION_MODIFIED', 'ADMIN_INVOICE_VIEWED', 'ADMIN_REVENUE_VIEWED', 'ADMIN_ANALYTICS_VIEWED', name='auditaction'), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('request_method', sa.String(length=10), nullable=True),
        sa.Column('request_path', sa.String(length=500), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('success', sa.String(length=10), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)

    # Create admin_actions table
    op.create_table('admin_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.Enum('USER_MANAGEMENT', 'SUBSCRIPTION_MANAGEMENT', 'INVOICE_MANAGEMENT', 'PAYMENT_MANAGEMENT', 'SYSTEM_CONFIGURATION', 'ANALYTICS_ACCESS', 'BULK_OPERATION', 'DATA_EXPORT', 'EMAIL_CAMPAIGN', 'SUPPORT_TICKET', name='adminactiontype'), nullable=False),
        sa.Column('action_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('target_user_id', sa.Integer(), nullable=True),
        sa.Column('target_resource_type', sa.String(length=50), nullable=True),
        sa.Column('target_resource_id', sa.Integer(), nullable=True),
        sa.Column('operation_data', sa.Text(), nullable=True),
        sa.Column('result_data', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['target_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_actions_id'), 'admin_actions', ['id'], unique=False)

    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('INVOICE_FINALIZED', 'INVOICE_SENT', 'INVOICE_PAID', 'SUBSCRIPTION_ACTIVATED', 'SUBSCRIPTION_CANCELLED', 'SUBSCRIPTION_RENEWED', 'PASSWORD_RESET', 'EMAIL_VERIFICATION', 'ACCOUNT_ACTIVITY', 'ADMIN_MESSAGE', name='notificationtype'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SENT', 'DELIVERED', 'FAILED', 'READ', name='notificationstatus'), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('email_sent', sa.Boolean(), nullable=True),
        sa.Column('email_sent_at', sa.DateTime(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)

    # Create email_logs table
    op.create_table('email_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('to_email', sa.String(length=255), nullable=False),
        sa.Column('from_email', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('body_html', sa.Text(), nullable=True),
        sa.Column('body_text', sa.Text(), nullable=True),
        sa.Column('email_type', sa.Enum('INVOICE_NOTIFICATION', 'SUBSCRIPTION_NOTIFICATION', 'PASSWORD_RESET', 'EMAIL_VERIFICATION', 'WELCOME', 'ADMIN_MESSAGE', 'PAYMENT_CONFIRMATION', name='emailtype'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SENT', 'DELIVERED', 'BOUNCED', 'FAILED', 'OPENED', 'CLICKED', name='emailstatus'), nullable=True),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('opened_at', sa.DateTime(), nullable=True),
        sa.Column('clicked_at', sa.DateTime(), nullable=True),
        sa.Column('bounced_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('max_retries', sa.Integer(), nullable=True),
        sa.Column('provider_message_id', sa.String(length=255), nullable=True),
        sa.Column('provider_response', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_logs_id'), 'email_logs', ['id'], unique=False)

    # Create secure_download_tokens table
    op.create_table('secure_download_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('token_plain', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('max_downloads', sa.Integer(), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_used', sa.Boolean(), nullable=True),
        sa.Column('first_accessed_at', sa.DateTime(), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True),
        sa.Column('ip_addresses', sa.String(length=500), nullable=True),
        sa.Column('user_agents', sa.String(length=1000), nullable=True),
        sa.Column('sent_to_email', sa.String(length=255), nullable=True),
        sa.Column('email_log_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['email_log_id'], ['email_logs.id'], ),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_secure_download_tokens_id'), 'secure_download_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_secure_download_tokens_token_hash'), 'secure_download_tokens', ['token_hash'], unique=True)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_secure_download_tokens_token_hash'), table_name='secure_download_tokens')
    op.drop_index(op.f('ix_secure_download_tokens_id'), table_name='secure_download_tokens')
    op.drop_table('secure_download_tokens')
    
    op.drop_index(op.f('ix_email_logs_id'), table_name='email_logs')
    op.drop_table('email_logs')
    
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    
    op.drop_index(op.f('ix_admin_actions_id'), table_name='admin_actions')
    op.drop_table('admin_actions')
    
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')