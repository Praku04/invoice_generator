"""Add template_id to payment_receipts table

Revision ID: 005
Revises: 004
Create Date: 2026-01-29 19:05:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Add template_id column to payment_receipts table
    op.add_column('payment_receipts', sa.Column('template_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_payment_receipts_template_id', 'payment_receipts', 'templates', ['template_id'], ['id'])


def downgrade():
    # Remove template_id column from payment_receipts table
    op.drop_constraint('fk_payment_receipts_template_id', 'payment_receipts', type_='foreignkey')
    op.drop_column('payment_receipts', 'template_id')