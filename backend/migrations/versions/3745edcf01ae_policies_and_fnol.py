"""policies and fnol

Revision ID: 3745edcf01ae
Revises: 7f2d2ec3e4e0
Create Date: 2026-11-17 17:00:07.805238

"""
from alembic import op
import sqlalchemy as sa


revision = '3745edcf01ae'
down_revision = '7f2d2ec3e4e0'
branch_labels = None
depends_on = None


def upgrade():
    # create_table also creates the two Postgres enum types the columns use.
    op.create_table('policy',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('policy_number', sa.String(length=255), nullable=False),
    sa.Column('insured_name', sa.String(length=255), nullable=False),
    sa.Column('line_of_business', sa.Enum('auto', 'property', 'general_liability', name='policy_line_of_business'), nullable=False),
    sa.Column('effective_date', sa.Date(), nullable=False),
    sa.Column('expiration_date', sa.Date(), nullable=False),
    sa.Column('status', sa.Enum('active', 'cancelled', name='policy_status'), server_default='active', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('expiration_date > effective_date', name=op.f('ck_policy_expiration_after_effective')),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], name=op.f('fk_policy_organization_id_organization')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_policy'))
    )
    with op.batch_alter_table('policy', schema=None) as batch_op:
        batch_op.create_index('uq_policy_organization_id_policy_number_lower', ['organization_id', sa.literal_column('lower(policy_number)')], unique=True)

    op.create_table('fnol',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('reported_policy_number', sa.String(length=255), nullable=False),
    sa.Column('policy_id', sa.Integer(), nullable=True),
    sa.Column('reporter_name', sa.String(length=255), nullable=False),
    sa.Column('reporter_email', sa.String(length=255), nullable=True),
    sa.Column('reporter_phone', sa.String(length=255), nullable=True),
    sa.Column('loss_date', sa.Date(), nullable=False),
    sa.Column('loss_description', sa.Text(), nullable=False),
    sa.Column('loss_state', sa.String(length=255), nullable=True),
    sa.Column('status', sa.Enum('submitted', 'converted', 'rejected', name='fnol_status'), server_default='submitted', nullable=False),
    sa.Column('rejection_reason', sa.Text(), nullable=True),
    sa.Column('submitted_by_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("(status = 'rejected') = (rejection_reason IS NOT NULL)", name=op.f('ck_fnol_rejection_reason_iff_rejected')),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], name=op.f('fk_fnol_organization_id_organization')),
    sa.ForeignKeyConstraint(['policy_id'], ['policy.id'], name=op.f('fk_fnol_policy_id_policy')),
    sa.ForeignKeyConstraint(['submitted_by_id'], ['user.id'], name=op.f('fk_fnol_submitted_by_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_fnol'))
    )
    with op.batch_alter_table('fnol', schema=None) as batch_op:
        batch_op.create_index('ix_fnol_organization_id_status', ['organization_id', 'status'], unique=False)


def downgrade():
    with op.batch_alter_table('fnol', schema=None) as batch_op:
        batch_op.drop_index('ix_fnol_organization_id_status')

    op.drop_table('fnol')
    sa.Enum(name='fnol_status').drop(op.get_bind())

    with op.batch_alter_table('policy', schema=None) as batch_op:
        batch_op.drop_index('uq_policy_organization_id_policy_number_lower')

    op.drop_table('policy')
    # Dropping the table leaves its enum types behind; without this, upgrading again would fail.
    sa.Enum(name='policy_status').drop(op.get_bind())
    sa.Enum(name='policy_line_of_business').drop(op.get_bind())
