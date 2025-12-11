"""Add place_embeddings table

Revision ID: 002_embeddings
Revises: 001_initial
Create Date: 2024-12-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_embeddings'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension (if not already enabled)
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create place_embeddings table
    op.create_table(
        'place_embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('place_id', sa.String(), nullable=False, unique=True),
        sa.Column('text_embedding', sa.LargeBinary(), nullable=True),  # Will store vector
        sa.Column('image_embedding', sa.LargeBinary(), nullable=True),  # Will store vector
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Add vector columns using raw SQL (pgvector specific)
    op.execute('ALTER TABLE place_embeddings DROP COLUMN IF EXISTS text_embedding')
    op.execute('ALTER TABLE place_embeddings ADD COLUMN text_embedding vector(768)')
    op.execute('ALTER TABLE place_embeddings DROP COLUMN IF EXISTS image_embedding')
    op.execute('ALTER TABLE place_embeddings ADD COLUMN image_embedding vector(512)')
    
    # Create indexes
    op.create_index('idx_place_embeddings_place_id', 'place_embeddings', ['place_id'])
    op.execute('CREATE INDEX IF NOT EXISTS idx_place_text_embedding ON place_embeddings USING hnsw (text_embedding vector_cosine_ops)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_place_image_embedding ON place_embeddings USING hnsw (image_embedding vector_cosine_ops)')


def downgrade() -> None:
    op.drop_table('place_embeddings')
