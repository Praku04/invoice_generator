"""Add template system tables

Revision ID: 004
Revises: 003
Create Date: 2026-01-28 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create templates table
    op.create_table('templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.Enum('INVOICE', 'RECEIPT', name='templatecategory'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True),
        sa.Column('author', sa.String(length=100), nullable=True),
        sa.Column('html_file', sa.String(length=255), nullable=False),
        sa.Column('css_file', sa.String(length=255), nullable=False),
        sa.Column('preview_image', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_premium', sa.Boolean(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('features', sa.Text(), nullable=True),
        sa.Column('supports_logo', sa.Boolean(), nullable=True),
        sa.Column('supports_signature', sa.Boolean(), nullable=True),
        sa.Column('supports_watermark', sa.Boolean(), nullable=True),
        sa.Column('page_size', sa.String(length=10), nullable=True),
        sa.Column('orientation', sa.String(length=10), nullable=True),
        sa.Column('margins', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_templates_id'), 'templates', ['id'], unique=False)
    op.create_index(op.f('ix_templates_template_id'), 'templates', ['template_id'], unique=True)

    # Create user_template_preferences table
    op.create_table('user_template_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.Enum('INVOICE', 'RECEIPT', name='templatecategory'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_template_preferences_id'), 'user_template_preferences', ['id'], unique=False)
    op.create_index(op.f('ix_user_template_preferences_user_id'), 'user_template_preferences', ['user_id'], unique=False)

    # Add template_id columns to invoices and payment_receipts tables
    op.add_column('invoices', sa.Column('template_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_invoices_template_id', 'invoices', 'templates', ['template_id'], ['id'])
    
    op.add_column('payment_receipts', sa.Column('template_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_payment_receipts_template_id', 'payment_receipts', 'templates', ['template_id'], ['id'])


def downgrade():
    # Remove foreign keys and columns
    op.drop_constraint('fk_payment_receipts_template_id', 'payment_receipts', type_='foreignkey')
    op.drop_column('payment_receipts', 'template_id')
    
    op.drop_constraint('fk_invoices_template_id', 'invoices', type_='foreignkey')
    op.drop_column('invoices', 'template_id')
    
    # Drop user_template_preferences table
    op.drop_index(op.f('ix_user_template_preferences_user_id'), table_name='user_template_preferences')
    op.drop_index(op.f('ix_user_template_preferences_id'), table_name='user_template_preferences')
    op.drop_table('user_template_preferences')
    
    # Drop templates table
    op.drop_index(op.f('ix_templates_template_id'), table_name='templates')
    op.drop_index(op.f('ix_templates_id'), table_name='templates')
    op.drop_table('templates')