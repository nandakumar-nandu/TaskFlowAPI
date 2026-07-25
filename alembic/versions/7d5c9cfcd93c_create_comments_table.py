"""create comments table

Revision ID: 7d5c9cfcd93c
Revises: 5bfa399b5973
Create Date: 2026-07-25 11:54:10.598417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d5c9cfcd93c'
down_revision: Union[str, Sequence[str], None] = '5bfa399b5973'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 📌 Step 1: Create the comments table with foreign key constraints
    op.create_table(
        'comments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('task_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 📌 Step 2: Create index on task_id to optimize comments retrieval by parent task
    op.create_index('ix_comments_task_id', 'comments', ['task_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # 📌 Step 1: Drop index on task_id
    op.drop_index('ix_comments_task_id', table_name='comments')

    # 📌 Step 2: Drop the comments table
    op.drop_table('comments')
