"""Add template_id to payment_receipts table

Revision ID: 005
Revises: 004
Create Date: 2026-01-29 19:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Check if template_id column already exists
    conn = op.get_bind()
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='payment_receipts' AND column_name='template_id'
    """))
    
    if not result.fetchone():
        # Add template_id column to payment_receipts table only if it doesn't exist
        op.add_column('payment_receipts', sa.Column('template_id', sa.Integer(), nullable=True))
        op.create_foreign_key('fk_payment_receipts_template_id', 'payment_receipts', 'templates', ['template_id'], ['id'])
    else:
        # Column exists, just ensure foreign key exists
        try:
            op.create_foreign_key('fk_payment_receipts_template_id', 'payment_receipts', 'templates', ['template_id'], ['id'])
        except:
            # Foreign key might already exist, ignore error
            pass


def downgrade():
    # Remove template_id column from payment_receipts table
    try:
        op.drop_constraint('fk_payment_receipts_template_id', 'payment_receipts', type_='foreignkey')
    except:
        pass
    
    try:
        op.drop_column('payment_receipts', 'template_id')
    except:
        pass