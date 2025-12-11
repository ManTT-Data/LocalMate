"""Initial migration - core schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-12-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Note: profiles table is created via Supabase SQL 
    # because it needs to reference auth.users
    
    # Create itineraries table
    op.create_table(
        'itineraries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('total_days', sa.Integer(), nullable=False),
        sa.Column('total_budget', sa.Numeric(12, 2), nullable=True),
        sa.Column('currency', sa.String(), server_default='VND'),
        sa.Column('meta', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.CheckConstraint('total_days >= 1', name='itineraries_total_days_check'),
    )
    op.create_index('idx_itineraries_user_id', 'itineraries', ['user_id'])
    op.create_index('idx_itineraries_created_at', 'itineraries', ['created_at'])

    # Create itinerary_stops table
    op.create_table(
        'itinerary_stops',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('itinerary_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('day_index', sa.Integer(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('place_id', sa.String(), nullable=False),
        sa.Column('arrival_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stay_minutes', sa.Integer(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('snapshot', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['itinerary_id'], ['itineraries.id'], ondelete='CASCADE'),
        sa.CheckConstraint('day_index >= 1', name='stops_day_index_check'),
        sa.CheckConstraint('order_index >= 1', name='stops_order_index_check'),
    )
    op.create_index('idx_stops_itinerary_id', 'itinerary_stops', ['itinerary_id'])
    op.create_index('idx_stops_place_id', 'itinerary_stops', ['place_id'])
    op.create_index('idx_stops_day_order', 'itinerary_stops', ['itinerary_id', 'day_index', 'order_index'])


def downgrade() -> None:
    op.drop_table('itinerary_stops')
    op.drop_table('itineraries')
