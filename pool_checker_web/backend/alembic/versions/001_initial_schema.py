"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create pools table
    op.create_table(
        'pools',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('element_id', sa.String(length=100), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=True, default='CET'),
        sa.Column('scrape_start_time', sa.String(length=5), nullable=True, default='05:50'),
        sa.Column('scrape_end_time', sa.String(length=5), nullable=True, default='22:10'),
        sa.Column('scrape_interval_minutes', sa.Integer(), nullable=True, default=10),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pools_id'), 'pools', ['id'], unique=False)

    # Create visitor_records table
    op.create_table(
        'visitor_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pool_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('weekday', sa.String(length=10), nullable=False),
        sa.Column('visitor_count', sa.Integer(), nullable=False),
        sa.Column('week_number', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['pool_id'], ['pools.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_visitor_records_id'), 'visitor_records', ['id'], unique=False)
    op.create_index(op.f('ix_visitor_records_timestamp'), 'visitor_records', ['timestamp'], unique=False)
    op.create_index('ix_visitor_pool_timestamp', 'visitor_records', ['pool_id', 'timestamp'], unique=False)
    op.create_index('ix_visitor_pool_weekday', 'visitor_records', ['pool_id', 'weekday'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_visitor_pool_weekday', table_name='visitor_records')
    op.drop_index('ix_visitor_pool_timestamp', table_name='visitor_records')
    op.drop_index(op.f('ix_visitor_records_timestamp'), table_name='visitor_records')
    op.drop_index(op.f('ix_visitor_records_id'), table_name='visitor_records')
    op.drop_table('visitor_records')
    op.drop_index(op.f('ix_pools_id'), table_name='pools')
    op.drop_table('pools')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
