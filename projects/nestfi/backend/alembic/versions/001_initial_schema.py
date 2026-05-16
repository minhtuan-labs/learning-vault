"""Initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-05-16

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='member'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Families table
    op.create_table(
        'families',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000)),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Family members table
    op.create_table(
        'family_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer()),
        sa.Column('role', sa.String(50), nullable=False, server_default='member'),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('joined_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['family_id'], ['families.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_family_members_family_id', 'family_members', ['family_id'])
    op.create_index('ix_family_members_user_id', 'family_members', ['user_id'])

    # Invitations table
    op.create_table(
        'invitations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.UUID(), nullable=False, unique=True),
        sa.Column('invited_by_user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['family_id'], ['families.id']),
        sa.ForeignKeyConstraint(['invited_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_invitations_family_id', 'invitations', ['family_id'])
    op.create_index('ix_invitations_token', 'invitations', ['token'])

    # Categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000)),
        sa.Column('color', sa.String(7), nullable=False, server_default='#808080'),
        sa.Column('icon', sa.String(50)),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['family_id'], ['families.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_categories_family_id', 'categories', ['family_id'])
    op.create_index('ix_categories_type', 'categories', ['type'])
    op.create_index('ix_categories_is_active', 'categories', ['is_active'])

    # Transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('description', sa.String(1000)),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('deleted_by', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.ForeignKeyConstraint(['family_id'], ['families.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['deleted_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_transactions_family_id', 'transactions', ['family_id'])
    op.create_index('ix_transactions_category_id', 'transactions', ['category_id'])
    op.create_index('ix_transactions_deleted_at', 'transactions', ['deleted_at'])
    op.create_index('ix_transactions_transaction_date', 'transactions', ['transaction_date'])

    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('old_values', sa.JSON()),
        sa.Column('new_values', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])

def downgrade() -> None:
    op.drop_index('ix_audit_logs_entity_id')
    op.drop_index('ix_audit_logs_entity_type')
    op.drop_index('ix_audit_logs_user_id')
    op.drop_table('audit_logs')

    op.drop_index('ix_transactions_transaction_date')
    op.drop_index('ix_transactions_deleted_at')
    op.drop_index('ix_transactions_category_id')
    op.drop_index('ix_transactions_family_id')
    op.drop_table('transactions')

    op.drop_index('ix_categories_is_active')
    op.drop_index('ix_categories_type')
    op.drop_index('ix_categories_family_id')
    op.drop_table('categories')

    op.drop_index('ix_invitations_token')
    op.drop_index('ix_invitations_family_id')
    op.drop_table('invitations')

    op.drop_index('ix_family_members_user_id')
    op.drop_index('ix_family_members_family_id')
    op.drop_table('family_members')

    op.drop_table('families')

    op.drop_index('ix_users_email')
    op.drop_table('users')
