"""Add payment receipts table

Revision ID: 003
Revises: 002
Create Date: 2026-01-28 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create payment_receipts table
    op.create_table('payment_receipts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('receipt_number', sa.String(length=50), nullable=False),
        sa.Column('receipt_type', sa.Enum('SUBSCRIPTION_PAYMENT', 'INVOICE_PAYMENT', 'REFUND', 'ADJUSTMENT', name='receipttype'), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'GENERATED', 'SENT', 'VIEWED', name='receiptstatus'), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('payment_id', sa.Integer(), nullable=True),
        sa.Column('subscription_id', sa.Integer(), nullable=True),
        sa.Column('invoice_id', sa.Integer(), nullable=True),
        sa.Column('receipt_date', sa.DateTime(), nullable=False),
        sa.Column('payment_date', sa.DateTime(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('currency_symbol', sa.String(length=5), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('transaction_id', sa.String(length=100), nullable=True),
        sa.Column('razorpay_payment_id', sa.String(length=100), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('customer_name', sa.String(length=255), nullable=False),
        sa.Column('customer_email', sa.String(length=255), nullable=False),
        sa.Column('customer_phone', sa.String(length=20), nullable=True),
        sa.Column('customer_address', sa.Text(), nullable=True),
        sa.Column('customer_gstin', sa.String(length=20), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('company_address', sa.Text(), nullable=True),
        sa.Column('company_gstin', sa.String(length=20), nullable=True),
        sa.Column('company_pan', sa.String(length=20), nullable=True),
        sa.Column('pdf_generated', sa.Boolean(), nullable=True),
        sa.Column('pdf_file_path', sa.String(length=500), nullable=True),
        sa.Column('pdf_generated_at', sa.DateTime(), nullable=True),
        sa.Column('email_sent', sa.Boolean(), nullable=True),
        sa.Column('email_sent_at', sa.DateTime(), nullable=True),
        sa.Column('email_sent_to', sa.String(length=255), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('admin_reviewed', sa.Boolean(), nullable=True),
        sa.Column('admin_reviewed_by', sa.Integer(), nullable=True),
        sa.Column('admin_reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['admin_reviewed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payment_receipts_id'), 'payment_receipts', ['id'], unique=False)
    op.create_index(op.f('ix_payment_receipts_receipt_number'), 'payment_receipts', ['receipt_number'], unique=True)

    # Add receipt_id column to secure_download_tokens table
    op.add_column('secure_download_tokens', sa.Column('receipt_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_secure_download_tokens_receipt_id', 'secure_download_tokens', 'payment_receipts', ['receipt_id'], ['id'])
    
    # Make invoice_id nullable in secure_download_tokens (since we can now have receipt downloads)
    op.alter_column('secure_download_tokens', 'invoice_id', nullable=True)


def downgrade():
    # Remove receipt_id column from secure_download_tokens
    op.drop_constraint('fk_secure_download_tokens_receipt_id', 'secure_download_tokens', type_='foreignkey')
    op.drop_column('secure_download_tokens', 'receipt_id')
    
    # Make invoice_id non-nullable again
    op.alter_column('secure_download_tokens', 'invoice_id', nullable=False)
    
    # Drop payment_receipts table
    op.drop_index(op.f('ix_payment_receipts_receipt_number'), table_name='payment_receipts')
    op.drop_index(op.f('ix_payment_receipts_id'), table_name='payment_receipts')
    op.drop_table('payment_receipts')